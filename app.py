import streamlit as st
import requests
from datetime import datetime, timezone, timedelta
import re
import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Tuple
import os
from functools import lru_cache
import base64
import time
import socket

# Importações do SendGrid
try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

# Importar configurações
from config import (
    PLANOS_SEGURO, DATA_FINAL_VIGENCIA, EMAIL_CONFIG, API_URLS, 
    TIMEOUT_CONFIG, REGEX_PATTERNS, APP_CONFIG, MENSAGENS, CAMPOS_OBRIGATORIOS
)

# ==================== FUNÇÃO PARA MOSTRAR URLs ====================

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        # Conecta a um endereço externo para descobrir o IP local
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def mostrar_urls_acesso():
    """Mostra as URLs de acesso no console quando o servidor iniciar"""
    local_ip = get_local_ip()
    porta = 8501  # Porta padrão do Streamlit
    
    print("\n" + "="*60)
    print("🌐 SERVIDOR STREAMLIT INICIADO COM SUCESSO!")
    print("="*60)
    print(f"📍 URL Local:     http://localhost:{porta}")
    print(f"📍 URL Local Alt: http://127.0.0.1:{porta}")
    print(f"🌐 URL da Rede:   http://{local_ip}:{porta}")
    print("="*60)
    print("📱 Para acessar pelo celular:")
    print(f"   Use: http://{local_ip}:{porta}")
    print("   (Certifique-se de estar na mesma rede WiFi)")
    print("="*60)
    print("🔧 Comandos úteis:")
    print("   Ctrl+C para parar o servidor")
    print("   Consulte ACESSO_URLS.md para mais informações")
    print("="*60 + "\n")

# Mostrar URLs quando o app iniciar
if __name__ == "__main__" or "streamlit" in str(os.environ.get("_", "")):
    mostrar_urls_acesso()

# Configuração da página
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"]
)

# ==================== CONFIGURAÇÕES ====================

# CSS customizado para estética moderna e agradável
def load_css():
    """Carrega CSS do arquivo externo"""
    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Arquivo styles.css não encontrado. Usando estilos padrão.")

# Carregar CSS
load_css()

# JavaScript otimizado e limpo para mobile
st.markdown("""
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
""", unsafe_allow_html=True)

st.markdown("""
<script>
document.addEventListener('DOMContentLoaded', function() {
    const isMobile = window.innerWidth <= 768;
    
    if (isMobile) {
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(input => {
            input.style.fontSize = '16px';
            input.addEventListener('focus', function() {
                this.style.outline = '2px solid #182c4b';
            });
        });
        
        const buttons = document.querySelectorAll('button');
        buttons.forEach(button => {
            button.style.minHeight = '44px';
        });
        
        document.body.style.overflowX = 'hidden';
        document.documentElement.style.overflowX = 'hidden';
    }
    
    const errorElements = document.querySelectorAll('.error-message');
    if (errorElements.length > 0) {
        errorElements[0].scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
    
    window.addEventListener('resize', function() {
        document.body.style.overflowX = 'hidden';
        document.documentElement.style.overflowX = 'hidden';
    });
});
</script>
""", unsafe_allow_html=True)

def carregar_logo(width=None):
    """Carrega e exibe o logo da empresa de forma responsiva"""
    try:
        # Logo responsivo baseado no tamanho da tela
        logo_width = width if width is not None else 80  # Reduzido padrão
        
        # Usar HTML responsivo para controle total do posicionamento
        st.markdown(f"""
        <div class="logo-container" style="
            display: flex; 
            justify-content: center; 
            align-items: center; 
            width: 100%; 
            margin: 0 auto;
            padding: 0;
            max-width: 100%;
            overflow: hidden;
        ">
            <img src="data:image/png;base64,{get_logo_base64()}" 
                 style="
                     max-width: {logo_width}px;
                     width: auto;
                     height: auto;
                     display: block; 
                     margin: 0 auto;
                     border-radius: 8px;
                     box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                 " 
                 alt="Logo CPZ">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(MENSAGENS["logo_nao_encontrado"])

def get_logo_base64():
    """Converte o logo para base64 para embedding direto no HTML"""
    try:
        with open(APP_CONFIG["logo_path"], "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def validar_cnpj(cnpj: str) -> bool:
    """Valida se o CNPJ tem 14 dígitos e formato correto"""
    if not cnpj:
        return False
    
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return bool(re.match(REGEX_PATTERNS["cnpj"], cnpj_limpo))

def validar_cpf(cpf: str) -> bool:
    """Valida se o CPF tem 11 dígitos e formato correto"""
    if not cpf:
        return False
    
    cpf_limpo = re.sub(r'\D', '', cpf)
    return bool(re.match(REGEX_PATTERNS["cpf"], cpf_limpo))

def validar_cep(cep: str) -> bool:
    """Valida se o CEP tem 8 dígitos e formato correto"""
    if not cep:
        return False
    
    cep_limpo = re.sub(r'\D', '', cep)
    return bool(re.match(REGEX_PATTERNS["cep"], cep_limpo))

def validar_email(email: str) -> bool:
    """Valida email com regex mais robusta"""
    if not email:
        return False
    
    return bool(re.match(REGEX_PATTERNS["email"], email.strip()))

def validar_telefone(telefone: str) -> bool:
    """Valida se o telefone tem 10 ou 11 dígitos e formato correto"""
    if not telefone:
        return False
    
    telefone_limpo = re.sub(r'\D', '', telefone)
    return bool(re.match(REGEX_PATTERNS["telefone"], telefone_limpo))

def limpar_string(texto: str) -> str:
    """Remove espaços extras e caracteres desnecessários"""
    if not texto:
        return ""
    return texto.strip()

def formatar_cnpj(cnpj: str) -> str:
    """Formata CNPJ para exibição"""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj

def formatar_cpf(cpf: str) -> str:
    """Formata CPF para exibição"""
    cpf_limpo = re.sub(r'\D', '', cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

def formatar_cep(cep: str) -> str:
    """Formata CEP para exibição"""
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep

def formatar_telefone(telefone: str) -> str:
    """Formata telefone para exibição"""
    telefone_limpo = re.sub(r'\D', '', telefone)
    if len(telefone_limpo) == 11:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    elif len(telefone_limpo) == 10:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    return telefone

def formatar_valor_real(valor: float) -> str:
    """Formatar valor monetário em reais"""
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

# ==================== SENDGRID EMAIL SENDER ====================

class SendGridEmailSender:
    def __init__(self, api_key=None):
        """
        Inicializa o cliente SendGrid
        
        Args:
            api_key (str): API Key do SendGrid. Se None, busca em variável de ambiente
        """
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("API Key do SendGrid não encontrada!")
        
        self.sg = SendGridAPIClient(api_key=self.api_key)
    
    def enviar_email_formulario(self, dados_formulario, email_destino="informe@cpzseg.com.br"):
        """
        Envia email com dados do formulário
        
        Args:
            dados_formulario (dict): Dados do formulário preenchido
            email_destino (str): Email de destino
        """
        try:
            # Email remetente - tentar carregar do secrets.toml primeiro
            remetente_email = "noreply@cpzseg.com.br"  # padrão
            remetente_nome = "Grupo CPZ - Formulários"
            
            try:
                if hasattr(st, 'secrets') and 'sendgrid' in st.secrets:
                    remetente_email = st.secrets["sendgrid"].get("from_email", remetente_email)
                    remetente_nome = st.secrets["sendgrid"].get("from_name", remetente_nome)
            except:
                pass  # usar padrão se não conseguir carregar
            
            from_email = Email(remetente_email, remetente_nome)
            
            # Email destinatário
            to_email = To(email_destino)
            
            # Assunto
            subject = f"Nova Solicitação - Seguro Incêndio Conteúdos - {dados_formulario.get('nome_completo', 'N/A')}"
            
            # Conteúdo HTML do email
            html_content = self._gerar_html_email(dados_formulario)
            content = Content("text/html", html_content)
            
            # Criar email
            mail = Mail(from_email, to_email, subject, content)
            
            # Enviar
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                return True, "Email enviado com sucesso!"
            else:
                return False, f"Erro ao enviar email. Status: {response.status_code}"
                
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def _gerar_html_email(self, dados):
        """Gera HTML formatado para o email"""
        # Extrair nome do plano corretamente
        plano_nome = dados.get('plano_selecionado', '').split('\n')[0] if dados.get('plano_selecionado') else 'Não selecionado'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #182c4b; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #182c4b; padding-bottom: 5px; }}
                .info-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
                .label {{ font-weight: bold; color: #4a5568; }}
                .value {{ color: #2d3748; }}
                .highlight {{ background: #c6f6d5; padding: 15px; border-radius: 8px; border-left: 4px solid #48bb78; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #718096; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🛡️ Seguro Incêndio Conteúdos - Cessionários ORLA RIO</h1>
                    <p>Nova Solicitação Recebida</p>
                    <p>Formulário preenchido em {datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y às %H:%M')}</p>
                </div>
                
                <div class="content">
                    <div class="section">
                        <div class="section-title">👤 Dados Pessoais</div>
                        <div class="info-row">
                            <span class="label">Nome Completo:</span>
                            <span class="value">{dados.get('nome_completo', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">CPF:</span>
                            <span class="value">{formatar_cpf(dados.get('cpf', ''))}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">E-mail:</span>
                            <span class="value">{dados.get('email', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Telefone:</span>
                            <span class="value">{formatar_telefone(dados.get('telefone', ''))}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">CNPJ:</span>
                            <span class="value">{formatar_cnpj(dados.get('cnpj', ''))}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Razão Social:</span>
                            <span class="value">{dados.get('razao_social', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">📍 Identificação do Quiosque</div>
                        <div class="info-row">
                            <span class="label">CEP:</span>
                            <span class="value">{formatar_cep(dados.get('cep', ''))}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Logradouro:</span>
                            <span class="value">{dados.get('logradouro', 'N/A')}, {dados.get('numero', 'N/A')}</span>
                        </div>
                        {f'<div class="info-row"><span class="label">Complemento:</span><span class="value">{dados.get("complemento", "")}</span></div>' if dados.get('complemento') else ''}
                        <div class="info-row">
                            <span class="label">Bairro:</span>
                            <span class="value">{dados.get('bairro', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Cidade/Estado:</span>
                            <span class="value">{dados.get('cidade', 'N/A')} - {dados.get('estado', 'N/A')}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">🛡️ Plano de Seguro</div>
                        <div class="info-row">
                            <span class="label">Plano Selecionado:</span>
                            <span class="value">{plano_nome}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Data de Inclusão:</span>
                            <span class="value">{datetime.strptime(dados.get('data_inclusao', ''), '%Y-%m-%d').strftime('%d/%m/%Y') if dados.get('data_inclusao') else 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Vigência até:</span>
                            <span class="value">31/12/2025</span>
                        </div>
                    </div>
                    
                    <div class="highlight">
                        <h3 style="margin: 0 0 10px 0; color: #22543d;">💰 Cálculo Pró-rata</h3>
                        <div class="info-row">
                            <span class="label">Dias Restantes:</span>
                            <span class="value">{dados.get('dias_restantes', 'N/A')} dias</span>
                        </div>
                        <div class="info-row">
                            <span class="label"><strong>Prêmio Pró-rata:</strong></span>
                            <span class="value"><strong>{formatar_valor_real(dados.get('premio_pro_rata', 0))}</strong></span>
                        </div>
                    </div>
                    
                    <div class="footer">
                        <p>Este email foi gerado automaticamente pelo sistema de adesão de seguros - Grupo CPZ</p>
                        <p>Data/Hora UTC: {dados.get('timestamp_utc', 'N/A')}</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html
    
    def enviar_email_confirmacao_cliente(self, dados_formulario):
        """
        Envia email de confirmação para o cliente
        
        Args:
            dados_formulario (dict): Dados do formulário preenchido
        """
        try:
            # Email remetente - tentar carregar do secrets.toml primeiro
            remetente_email = "seu_email_verificado@gmail.com"  # padrão
            remetente_nome = "Grupo CPZ - Formulários"
            
            try:
                if hasattr(st, 'secrets') and 'sendgrid' in st.secrets:
                    remetente_email = st.secrets["sendgrid"].get("from_email", remetente_email)
                    remetente_nome = st.secrets["sendgrid"].get("from_name", remetente_nome)
            except:
                pass  # usar padrão se não conseguir carregar
            
            from_email = Email(remetente_email, remetente_nome)
            
            # Email destinatário (cliente)
            to_email = To(dados_formulario.get('email', ''))
            
            # Assunto personalizado para o cliente
            subject = f"✅ Confirmação de Adesão - Seguro Incêndio Conteúdos - {dados_formulario.get('nome_completo', 'N/A')}"
            
            # Conteúdo HTML do email para o cliente
            html_content = self._gerar_html_email_cliente(dados_formulario)
            content = Content("text/html", html_content)
            
            # Criar email
            mail = Mail(from_email, to_email, subject, content)
            
            # Enviar
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                return True, "Email de confirmação enviado para o cliente!"
            else:
                return False, f"Erro ao enviar email para cliente. Status: {response.status_code}"
                
        except Exception as e:
            return False, f"Erro ao enviar email para cliente: {str(e)}"
    
    def _gerar_html_email_cliente(self, dados):
        """Gera HTML formatado para o email de confirmação do cliente"""
        # Extrair nome do plano corretamente
        plano_nome = dados.get('plano_selecionado', '').split('\n')[0] if dados.get('plano_selecionado') else 'Não selecionado'
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: #182c4b; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #182c4b; padding-bottom: 5px; }}
                .info-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
                .label {{ font-weight: bold; color: #4a5568; }}
                .value {{ color: #2d3748; }}
                .highlight {{ background: #c6f6d5; padding: 15px; border-radius: 8px; border-left: 4px solid #48bb78; margin: 20px 0; }}
                .success-box {{ background: #d4edda; border: 1px solid #c3e6cb; color: #155724; padding: 20px; border-radius: 8px; margin: 20px 0; text-align: center; }}
                .footer {{ text-align: center; margin-top: 20px; color: #718096; font-size: 12px; }}
                .next-steps {{ background: #e3f2fd; border-left: 4px solid #2196f3; padding: 15px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>✅ Confirmação de Adesão</h1>
                    <h2>Seguro Incêndio Conteúdos - Cessionários ORLA RIO</h2>
                    <p>Olá, {dados.get('nome_completo', 'N/A')}!</p>
                </div>
                
                <div class="content">
                    <div class="success-box">
                        <h3 style="margin: 0 0 10px 0;">🎉 Sua solicitação foi recebida com sucesso!</h3>
                        <p style="margin: 0;">Recebemos sua adesão ao seguro e nossa equipe entrará em contato em breve.</p>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">📋 Resumo da sua Adesão</div>
                        <div class="info-row">
                            <span class="label">Nome:</span>
                            <span class="value">{dados.get('nome_completo', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">CPF:</span>
                            <span class="value">{formatar_cpf(dados.get('cpf', ''))}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Email:</span>
                            <span class="value">{dados.get('email', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Empresa:</span>
                            <span class="value">{dados.get('razao_social', 'N/A')}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">CNPJ:</span>
                            <span class="value">{formatar_cnpj(dados.get('cnpj', ''))}</span>
                        </div>
                    </div>
                    
                    <div class="section">
                        <div class="section-title">🛡️ Plano Selecionado</div>
                        <div class="info-row">
                            <span class="label">Plano:</span>
                            <span class="value">{plano_nome}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Data de Inclusão:</span>
                            <span class="value">{datetime.strptime(dados.get('data_inclusao', ''), '%Y-%m-%d').strftime('%d/%m/%Y') if dados.get('data_inclusao') else 'N/A'}</span>
                        </div>
                        <div class="info-row">
                            <span class="label">Vigência até:</span>
                            <span class="value">31/12/2025</span>
                        </div>
                    </div>
                    
                    <div class="highlight">
                        <h3 style="margin: 0 0 10px 0; color: #22543d;">💰 Valor do Prêmio</h3>
                        <div class="info-row">
                            <span class="label">Dias de Cobertura:</span>
                            <span class="value">{dados.get('dias_restantes', 'N/A')} dias</span>
                        </div>
                        <div class="info-row">
                            <span class="label"><strong>Prêmio Pró-rata:</strong></span>
                            <span class="value"><strong>{formatar_valor_real(dados.get('premio_pro_rata', 0))}</strong></span>
                        </div>
                    </div>
                    
                    <div class="next-steps">
                        <h3 style="margin: 0 0 10px 0; color: #1976d2;">📞 Próximos Passos</h3>
                        <p style="margin: 0;">
                            • Nossa equipe entrará em contato em até 24 horas<br>
                            • Você receberá as instruções para pagamento<br>
                            • Após confirmação do pagamento, sua apólice será emitida<br>
                            • Dúvidas? Entre em contato: <strong>informe@cpzseg.com.br</strong>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p><strong>Grupo CPZ Seguros</strong></p>
                        <p>Este email foi gerado automaticamente em {datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y às %H:%M')}</p>
                        <p>Email: informe@cpzseg.com.br | Telefone: (21) XXXX-XXXX</p>
                    </div>
                </div>
            </div>
        </body>
        </html>
        """
        return html

def configurar_sendgrid_streamlit():
    """
    Função para configurar SendGrid no Streamlit - MODO PRODUÇÃO
    """
    # EM PRODUÇÃO: Não mostrar configurações na sidebar
    # Tentar carregar configurações do secrets.toml primeiro
    api_key_from_secrets = None
    email_destino_from_secrets = "informe@cpzseg.com.br"
    email_mode = "SendGrid"  # Forçar SendGrid em produção
    
    try:
        if hasattr(st, 'secrets') and 'sendgrid' in st.secrets:
            api_key_from_secrets = st.secrets["sendgrid"].get("api_key", "")
            email_destino_from_secrets = st.secrets["sendgrid"].get("email_destino", "informe@cpzseg.com.br")
            
            if api_key_from_secrets and api_key_from_secrets != "SG.sua_api_key_aqui":
                # Configuração encontrada no secrets.toml
                try:
                    sender = SendGridEmailSender(api_key_from_secrets)
                    return sender, True, email_mode
                except Exception as e:
                    st.warning(f"⚠️ Problema na configuração do SendGrid: {str(e)}")
                    st.info("🧪 Usando modo de teste temporário")
                    return None, False, "Teste (sem envio)"
    except Exception as e:
        st.warning(f"⚠️ Erro ao carregar configurações: {str(e)}")
        st.info("🧪 Usando modo de teste temporário")
        return None, False, "Teste (sem envio)"
    
    # Tentar variáveis de ambiente como fallback
    api_key_env = os.getenv('SENDGRID_API_KEY')
    if api_key_env:
        try:
            sender = SendGridEmailSender(api_key_env)
            return sender, True, email_mode
        except Exception as e:
            st.warning(f"⚠️ Erro na configuração do SendGrid via env: {str(e)}")
            st.info("🧪 Usando modo de teste temporário")
            return None, False, "Teste (sem envio)"
    
    # Se chegou aqui, não há configuração válida - usar modo de teste
    st.info("🧪 **Modo de teste ativo** - Configure o SendGrid para envio real de emails")
    st.info("📋 Para configurar, adicione no arquivo `.streamlit/secrets.toml`:")
    st.code("""
[sendgrid]
api_key = "SG.sua_api_key_real_aqui"
email_destino = "informe@cpzseg.com.br"
from_email = "noreply@cpzseg.com.br"
from_name = "Grupo CPZ - Formulários"
    """)
    
    return None, False, "Teste (sem envio)"

@lru_cache(maxsize=100)
def buscar_cnpj(cnpj: str) -> Optional[str]:
    """Busca razão social via Receita WS com cache e retry"""
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    
    if not validar_cnpj(cnpj_limpo):
        st.error(MENSAGENS["cnpj_invalido"])
        return None
    
    url = f"{API_URLS['receita_ws']}{cnpj_limpo}"
    
    for tentativa in range(TIMEOUT_CONFIG["max_retries"]):
        try:
            response = requests.get(url, timeout=TIMEOUT_CONFIG["api_timeout"])
            response.raise_for_status()
            
            data = response.json()
            
            if data.get('status') == 'OK':
                return data.get('nome', '')
            else:
                st.error(f"❌ Erro na consulta CNPJ: {data.get('message', 'CNPJ inválido')}")
                return None
                
        except requests.exceptions.Timeout:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(MENSAGENS["timeout_cnpj"])
            continue
        except requests.exceptions.RequestException as e:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(f"❌ Erro na consulta do CNPJ: {str(e)}")
            continue
        except Exception as e:
            st.error(f"❌ Erro inesperado na consulta do CNPJ: {str(e)}")
            return None
    
    return None

@lru_cache(maxsize=100)
def buscar_cpf(cpf: str, data_nascimento: str = None) -> Optional[str]:
    """Busca nome via API de CPF com cache e retry"""
    cpf_limpo = re.sub(r'\D', '', cpf)
    
    if not validar_cpf(cpf_limpo):
        st.error(MENSAGENS["cpf_invalido"])
        return None
    
    # Usando uma API alternativa mais simples para demonstração
    # Em produção, você pode usar APIs como Serpro ou outras APIs oficiais
    try:
        # Simulação de consulta CPF - em produção use uma API real
        # Por questões de privacidade, vamos apenas validar o formato
        # e retornar uma mensagem de validação
        
        # Validação básica do CPF usando algoritmo de dígitos verificadores
        def validar_cpf_completo(cpf_str):
            cpf_nums = [int(d) for d in cpf_str if d.isdigit()]
            if len(cpf_nums) != 11:
                return False
            
            # Verifica se todos os dígitos são iguais
            if len(set(cpf_nums)) == 1:
                return False
            
            # Calcula primeiro dígito verificador
            soma = sum(cpf_nums[i] * (10 - i) for i in range(9))
            resto = soma % 11
            digito1 = 0 if resto < 2 else 11 - resto
            
            # Calcula segundo dígito verificador
            soma = sum(cpf_nums[i] * (11 - i) for i in range(10))
            resto = soma % 11
            digito2 = 0 if resto < 2 else 11 - resto
            
            return cpf_nums[9] == digito1 and cpf_nums[10] == digito2
        
        if validar_cpf_completo(cpf_limpo):
            return "CPF válido"
        else:
            st.error("❌ CPF inválido (dígitos verificadores incorretos)")
            return None
            
    except Exception as e:
        st.error(f"❌ Erro na validação do CPF: {str(e)}")
        return None

@lru_cache(maxsize=100)
def buscar_cep(cep: str) -> Optional[Dict]:
    """Busca endereço via ViaCEP com cache e retry"""
    cep_limpo = re.sub(r'\D', '', cep)
    
    if not validar_cep(cep_limpo):
        st.error(MENSAGENS["cep_invalido"])
        return None
    
    url = f"{API_URLS['via_cep']}{cep_limpo}/json/"
    
    for tentativa in range(TIMEOUT_CONFIG["max_retries"]):
        try:
            response = requests.get(url, timeout=TIMEOUT_CONFIG["api_timeout"])
            response.raise_for_status()
            
            data = response.json()
            
            if 'erro' not in data:
                return {
                    'logradouro': data.get('logradouro', ''),
                    'bairro': data.get('bairro', ''),
                    'cidade': data.get('localidade', ''),
                    'estado': data.get('uf', '')
                }
            else:
                st.error(MENSAGENS["cep_nao_encontrado"])
                return None
                
        except requests.exceptions.Timeout:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(MENSAGENS["timeout_cep"])
            continue
        except requests.exceptions.RequestException as e:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(f"❌ Erro na consulta do CEP: {str(e)}")
            continue
        except Exception as e:
            st.error(f"❌ Erro inesperado na consulta do CEP: {str(e)}")
            return None
    
    return None

def calcular_pro_rata(plano: str, data_inclusao: datetime) -> Tuple[int, float]:
    """Calcula o prêmio pró-rata"""
    # Remove timezone da data de inclusão para comparação
    data_inclusao_naive = data_inclusao.replace(tzinfo=None)
    
    # Calcula dias restantes até 31/12/2025
    dias_restantes = (DATA_FINAL_VIGENCIA - data_inclusao_naive).days + 1
    
    # Calcula prêmio pró-rata
    preco_anual = PLANOS_SEGURO[plano]
    premio_pro_rata = round((preco_anual / 365) * dias_restantes, 2)
    
    return dias_restantes, premio_pro_rata

def enviar_email_confirmacao(dados: Dict, email_sender=None, email_mode="Teste (sem envio)") -> bool:
    """Envia email apenas para a empresa com todas as informações"""
    try:
        # Modo de teste
        if email_mode == "Teste (sem envio)":
            st.info("🧪 **Modo de teste ativado** - Emails não serão enviados, mas dados foram processados com sucesso!")
            st.success("✅ Formulário processado com sucesso!")
            
            # Mostrar preview do email que seria enviado
            with st.expander("📧 Preview do email que seria enviado", expanded=False):
                plano_nome = dados.get('plano_selecionado', '').split('\n')[0] if dados.get('plano_selecionado') else 'Não selecionado'
                
                st.markdown("### 📨 Email para a Empresa")
                st.markdown("**Para:** informe@cpzseg.com.br")
                st.markdown("**Assunto:** 🛡️ Nova Solicitação - Seguro Incêndio Conteúdos - " + dados['nome_completo'])
                st.markdown("**Tipo:** Notificação de nova adesão (dados completos)")
                
                st.markdown("---")
                
                st.markdown("**📋 Resumo dos dados:**")
                st.markdown(f"""
                - **Nome:** {dados['nome_completo']}
                - **CPF:** {formatar_cpf(dados['cpf'])}
                - **Email:** {dados['email']}
                - **Telefone:** {formatar_telefone(dados['telefone'])}
                - **CNPJ:** {formatar_cnpj(dados['cnpj'])}
                - **Razão Social:** {dados['razao_social']}
                - **Endereço:** {dados['logradouro']}, {dados['numero']} - {dados['bairro']} - {dados['cidade']}/{dados['estado']}
                - **CEP:** {formatar_cep(dados['cep'])}
                - **Plano:** {plano_nome}
                - **Prêmio:** {formatar_valor_real(dados['premio_pro_rata'])}
                """)
            
            return True
        
        # Modo SendGrid
        elif email_mode == "SendGrid" and email_sender:
            try:
                # Enviar apenas para empresa
                email_destino = st.session_state.get('sendgrid_email_destino', 'informe@cpzseg.com.br')
                sucesso_empresa, msg_empresa = email_sender.enviar_email_formulario(dados, email_destino)
                
                if sucesso_empresa:
                    st.success(f"✅ Mensagem transmitida para: {email_destino}")
                    return True
                else:
                    st.error(f"❌ Erro ao transmitir mensagem: {msg_empresa}")
                    return False
                    
            except Exception as e:
                st.error(f"❌ Erro no SendGrid: {str(e)}")
                return False
        
        # Modo SMTP Tradicional
        elif email_mode == "SMTP Tradicional":
            # Verificar se está em modo de teste
            if EMAIL_CONFIG.get("modo_teste", True):
                st.info("🧪 **Modo de teste SMTP ativado** - Email não será enviado, mas dados foram processados com sucesso!")
                st.success("✅ Formulário processado com sucesso!")
                return True
            
            # Validação básica para modo produção
            if not all([EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"], EMAIL_CONFIG["email_remetente"], EMAIL_CONFIG["senha_email"], EMAIL_CONFIG["email_empresa"]]):
                st.warning("⚠️ Configurações de email incompletas. Configure as variáveis de ambiente:")
                st.code("""
                EMAIL_REMETENTE=seu_email@empresa.com
                EMAIL_SENHA=sua_senha_de_app
                EMAIL_EMPRESA=email_destino@empresa.com
                MODO_TESTE=false
                """)
                return False
            
            # Extrair nome do plano corretamente
            plano_nome = dados.get('plano_selecionado', '').split('\n')[0] if dados.get('plano_selecionado') else 'Não selecionado'
            
            # Enviar apenas para a empresa
            destinatario = EMAIL_CONFIG["email_empresa"]
            
            # Corpo do email em HTML
            corpo_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #182c4b; color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .section {{ margin-bottom: 25px; }}
                    .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #182c4b; padding-bottom: 5px; }}
                    .info-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; }}
                    .label {{ font-weight: bold; color: #4a5568; }}
                    .value {{ color: #2d3748; }}
                    .highlight {{ background: #c6f6d5; padding: 15px; border-radius: 8px; border-left: 4px solid #48bb78; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 20px; color: #718096; font-size: 12px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🛡️ Seguro Incêndio Conteúdos - Cessionários ORLA RIO</h1>
                        <p>Nova Solicitação Recebida</p>
                        <p>Formulário preenchido em {datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y às %H:%M')}</p>
                    </div>
                    
                    <div class="content">
                        <div class="section">
                            <div class="section-title">👤 Dados Pessoais</div>
                            <div class="info-row">
                                <span class="label">Nome Completo:</span>
                                <span class="value">{dados['nome_completo']}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">CPF:</span>
                                <span class="value">{formatar_cpf(dados['cpf'])}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">E-mail:</span>
                                <span class="value">{dados['email']}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Telefone:</span>
                                <span class="value">{formatar_telefone(dados['telefone'])}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">CNPJ:</span>
                                <span class="value">{formatar_cnpj(dados['cnpj'])}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Razão Social:</span>
                                <span class="value">{dados['razao_social']}</span>
                            </div>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">📍 Identificação do Quiosque</div>
                            <div class="info-row">
                                <span class="label">CEP:</span>
                                <span class="value">{formatar_cep(dados['cep'])}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Logradouro:</span>
                                <span class="value">{dados['logradouro']}, {dados['numero']}</span>
                            </div>
                            {f'<div class="info-row"><span class="label">Complemento:</span><span class="value">{dados["complemento"]}</span></div>' if dados.get('complemento') else ''}
                            <div class="info-row">
                                <span class="label">Bairro:</span>
                                <span class="value">{dados['bairro']}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Cidade/Estado:</span>
                                <span class="value">{dados['cidade']} - {dados['estado']}</span>
                            </div>
                        </div>
                        
                        <div class="section">
                            <div class="section-title">🛡️ Plano de Seguro</div>
                            <div class="info-row">
                                <span class="label">Plano Selecionado:</span>
                                <span class="value">{plano_nome}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Data de Inclusão:</span>
                                <span class="value">{datetime.strptime(dados['data_inclusao'], '%Y-%m-%d').strftime('%d/%m/%Y')}</span>
                            </div>
                            <div class="info-row">
                                <span class="label">Vigência até:</span>
                                <span class="value">31/12/2025</span>
                            </div>
                        </div>
                        
                        <div class="highlight">
                            <h3 style="margin: 0 0 10px 0; color: #22543d;">💰 Cálculo Pró-rata</h3>
                            <div class="info-row">
                                <span class="label">Dias Restantes:</span>
                                <span class="value">{dados['dias_restantes']} dias</span>
                            </div>
                            <div class="info-row">
                                <span class="label"><strong>Prêmio Pró-rata:</strong></span>
                                <span class="value"><strong>{formatar_valor_real(dados['premio_pro_rata'])}</strong></span>
                            </div>
                        </div>
                        
                        <div class="footer">
                            <p>Este email foi gerado automaticamente pelo sistema de adesão de seguros - Grupo CPZ</p>
                            <p>Data/Hora UTC: {dados['timestamp_utc']}</p>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Conectar ao servidor SMTP
            server = smtplib.SMTP(EMAIL_CONFIG["smtp_server"], EMAIL_CONFIG["smtp_port"])
            server.starttls()
            server.login(EMAIL_CONFIG["email_remetente"], EMAIL_CONFIG["senha_email"])
            
            try:
                # Criar mensagem
                msg = MIMEMultipart()
                msg['From'] = EMAIL_CONFIG["email_remetente"]
                msg['To'] = destinatario
                msg['Subject'] = f"🛡️ Nova Adesão de Seguro - {dados['nome_completo']}"
                
                # Anexar corpo HTML
                msg.attach(MIMEText(corpo_html, 'html'))
                
                # Enviar email
                text = msg.as_string()
                server.sendmail(EMAIL_CONFIG["email_remetente"], destinatario, text)
                
                st.success(f"✅ Mensagem transmitida para: {destinatario}")
                return True
                
            except Exception as e:
                st.error(f"❌ Erro ao transmitir mensagem: {str(e)}")
                return False
            finally:
                server.quit()
        
        else:
            st.error("❌ Configuração de email inválida")
            return False
            
    except smtplib.SMTPAuthenticationError as e:
        st.error(f"❌ Erro de autenticação SMTP: {str(e)}")
        st.error("Verifique as credenciais de email nas configurações.")
        return False
    except smtplib.SMTPConnectError as e:
        st.error(f"❌ Erro de conexão SMTP: {str(e)}")
        st.error("Verifique o servidor SMTP e a porta nas configurações.")
        return False
    except smtplib.SMTPException as e:
        st.error(f"❌ Erro SMTP: {str(e)}")
        return False
    except Exception as e:
        st.error(f"❌ Erro inesperado ao transmitir mensagem: {str(e)}")
        st.error(f"Tipo do erro: {type(e).__name__}")
        return False

def validar_formulario(dados: Dict) -> list:
    """Valida todos os campos do formulário e retorna lista de erros"""
    erros = []
    
    # Validações obrigatórias usando configuração
    for campo, nome in CAMPOS_OBRIGATORIOS.items():
        valor = dados.get(campo, '').strip()
        if not valor:
            erros.append(f"{nome} é obrigatório")
    
    # Validações específicas
    email = dados.get('email', '').strip()
    if email and not validar_email(email):
        erros.append("E-mail inválido")
    
    telefone = dados.get('telefone', '').strip()
    if telefone and not validar_telefone(telefone):
        erros.append("Telefone deve ter 10 ou 11 dígitos")
    
    cpf = dados.get('cpf', '').strip()
    if cpf and not validar_cpf(cpf):
        erros.append("CPF deve estar no formato 000.000.000-00")
    
    cnpj = dados.get('cnpj', '').strip()
    if cnpj and not validar_cnpj(cnpj):
        erros.append("CNPJ deve estar no formato 00.000.000/0000-00")
    
    cep = dados.get('cep', '').strip()
    if cep and not validar_cep(cep):
        erros.append("CEP deve estar no formato 00000-000")
    
    # Validação do nome (mínimo 2 palavras)
    nome = dados.get('nome_completo', '').strip()
    if nome and len(nome.split()) < 2:
        erros.append("Nome completo deve ter pelo menos nome e sobrenome")
    
    return erros

def preparar_dados_formulario(session_state: Dict) -> Dict:
    """Prepara e limpa os dados do formulário"""
    return {
        'nome_completo': limpar_string(session_state.get('nome_completo', '')),
        'cpf': limpar_string(session_state.get('cpf', '')),
        'email': limpar_string(session_state.get('email', '')),
        'telefone': limpar_string(session_state.get('telefone', '')),
        'cnpj': limpar_string(session_state.get('cnpj', '')),
        'razao_social': limpar_string(session_state.get('razao_social', '')),
        'cep': limpar_string(session_state.get('cep', '')),
        'logradouro': limpar_string(session_state.get('logradouro', '')),
        'numero': limpar_string(session_state.get('numero', '')),
        'complemento': limpar_string(session_state.get('complemento', '')),
        'bairro': limpar_string(session_state.get('bairro', '')),
        'cidade': limpar_string(session_state.get('cidade', '')),
        'estado': limpar_string(session_state.get('estado', '')),
        'plano_selecionado': session_state.get('plano_radio', '')
    }

def get_field_value(field_name: str) -> str:
    """Obtém o valor de um campo priorizando dados atuais ou preservados, com fallback para DOM"""
    # Prioriza dados atuais do session_state (valores digitados)
    current_value = st.session_state.get(field_name, '')
    if current_value:
        return current_value
    
    # Se não há valor atual, usa dados preservados
    preserved_value = st.session_state.form_data.get(field_name, '')
    if preserved_value:
        return preserved_value
    
    # Adicionar JavaScript para tentar ler valores do DOM como último recurso
    st.markdown(f"""
    <script>
    // Tentar recuperar valor do campo {field_name} do DOM
    setTimeout(function() {{
        const inputs = document.querySelectorAll('input[type="text"]');
        inputs.forEach(function(input, index) {{
            const label = input.closest('div').querySelector('label');
            const labelText = label ? label.textContent.trim().toLowerCase() : '';
            
            // Mapear nomes de campos para labels
            const fieldMap = {{
                'nome_completo': 'nome completo',
                'cpf': 'cpf',
                'email': 'e-mail',
                'telefone': 'telefone',
                'cnpj': 'cnpj',
                'razao_social': 'razão social',
                'cep': 'cep',
                'logradouro': 'logradouro',
                'numero': 'número',
                'complemento': 'complemento',
                'bairro': 'bairro',
                'cidade': 'cidade',
                'estado': 'estado'
            }};
            
            const targetField = fieldMap['{field_name}'];
            if (targetField && labelText.includes(targetField)) {{
                if (input.value && input.value.trim() !== '') {{
                    // Armazenar valor encontrado
                    sessionStorage.setItem('fallback_{field_name}', input.value);
                    
                    // Forçar eventos de sincronização
                    const inputEvent = new Event('input', {{ bubbles: true, cancelable: true }});
                    const changeEvent = new Event('change', {{ bubbles: true, cancelable: true }});
                    
                    input.dispatchEvent(inputEvent);
                    input.dispatchEvent(changeEvent);
                }}
            }}
        }});
    }}, 100);
    </script>
    """, unsafe_allow_html=True)
    
    return ''

def render_header():
    """Renderiza o header responsivo da aplicação"""
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
    """, unsafe_allow_html=True)
    
    # Logo responsivo
    try:
        carregar_logo(width=100)  # Menor para melhor responsividade
    except Exception:
        st.markdown("**🛡️ Formulário de Adesão**")
    
    # Títulos responsivos
    st.markdown("""
        <div class="header-titles">
            <h1 class="header-main-title">Formulário de Adesão</h1>
            <h2 class="header-subtitle">Seguro Incêndio Conteúdos - Cessionários</h2>
            <p class="header-company"><strong>ORLA RIO</strong></p>
        </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_coberturas_table():
    """Renderiza tabela de coberturas de forma responsiva"""
    st.markdown("### 📋 Detalhamento das Coberturas")
    
    # Versão desktop (tabela)
    st.markdown("""
    <div class="coverage-table-desktop">
        <div style="overflow-x: auto; margin: 1.5rem 0;">
            <table class="coverage-table">
                <thead>
                    <tr>
                        <th>Coberturas</th>
                        <th>Opção 1<br><span class="price-label">R$ 250.000</span></th>
                        <th>Opção 2<br><span class="price-label">R$ 400.000</span></th>
                        <th>Opção 3<br><span class="price-label">R$ 700.000</span></th>
                        <th>Franquia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td class="coverage-name">Incêndio, Raio e Explosão</td>
                        <td>R$ 250.000</td>
                        <td>R$ 400.000</td>
                        <td>R$ 700.000</td>
                        <td class="franchise">R$ 30.000 (**)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Alagamento</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td class="franchise">R$ 15.000 (*)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Danos Elétricos</td>
                        <td>R$ 20.000</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td class="franchise">R$ 3.000 (*)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Pequenas Obras</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td class="franchise">R$ 5.000 (*)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Perda/Pgto Aluguel (6m)</td>
                        <td>R$ 20.000</td>
                        <td>R$ 30.000</td>
                        <td>R$ 40.000</td>
                        <td class="no-franchise">Não Há</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Vidros</td>
                        <td>R$ 20.000</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td class="franchise">R$ 3.000 (*)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Tumultos</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td>R$ 200.000</td>
                        <td class="franchise">R$ 5.000 (*)</td>
                    </tr>
                    <tr>
                        <td class="coverage-name">Vendaval</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td>R$ 200.000</td>
                        <td class="franchise">R$ 10.000 (*)</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Versão mobile (cards)
    st.markdown("""
    <div class="coverage-cards-mobile">
        <div class="coverage-card">
            <h4>🔥 Incêndio, Raio e Explosão</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 250.000</span>
                <span>Opção 2: R$ 400.000</span>
                <span>Opção 3: R$ 700.000</span>
                <span class="franchise">Franquia: R$ 30.000 (*)</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>💧 Alagamento</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 50.000</span>
                <span>Opção 2: R$ 100.000</span>
                <span>Opção 3: R$ 150.000</span>
                <span class="franchise">Franquia: R$ 15.000 (*)</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>⚡ Danos Elétricos</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 20.000</span>
                <span>Opção 2: R$ 50.000</span>
                <span>Opção 3: R$ 100.000</span>
                <span class="franchise">Franquia: R$ 3.000 (*)</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>🔨 Pequenas Obras</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 50.000</span>
                <span>Opção 2: R$ 100.000</span>
                <span>Opção 3: R$ 150.000</span>
                <span class="franchise">Franquia: R$ 5.000</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>🏠 Perda/Pgto Aluguel (6m)</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 20.000</span>
                <span>Opção 2: R$ 30.000</span>
                <span>Opção 3: R$ 40.000</span>
                <span class="no-franchise">Franquia: Não Há</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>🪟 Vidros</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 20.000</span>
                <span>Opção 2: R$ 50.000</span>
                <span>Opção 3: R$ 100.000</span>
                <span class="franchise">Franquia: R$ 3.000</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>⚠️ Tumultos</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 100.000</span>
                <span>Opção 2: R$ 150.000</span>
                <span>Opção 3: R$ 200.000</span>
                <span class="franchise">Franquia: R$ 5.000</span>
            </div>
        </div>
        
        <div class="coverage-card">
            <h4>💨 Vendaval</h4>
            <div class="coverage-values">
                <span>Opção 1: R$ 100.000</span>
                <span>Opção 2: R$ 150.000</span>
                <span>Opção 3: R$ 200.000</span>
                <span class="franchise">Franquia: R$ 10.000</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_responsive_field(label, field_name, field_type="text", help_text="", placeholder="", search_button=False, col_ratio=None):
    """Renderiza campos de forma responsiva baseado no tamanho da tela"""
    
    if search_button:
        # Para campos com botão de busca
        if col_ratio is None:
            col_ratio = [3, 1]  # Desktop padrão
        
        # Container responsivo
        st.markdown('<div class="responsive-field-container">', unsafe_allow_html=True)
        
        # Usar CSS flexbox em vez de colunas do Streamlit para melhor controle
        st.markdown(f"""
        <div class="field-with-search">
            <div class="field-input">
        """, unsafe_allow_html=True)
        
        # Campo principal
        value = st.text_input(
            label,
            value=get_field_value(field_name),
            help=help_text,
            placeholder=placeholder,
            key=field_name
        )
        
        st.markdown('</div><div class="field-button">', unsafe_allow_html=True)
        
        # Botão de busca
        button_key = f"buscar_{field_name}"
        button_pressed = st.button(f"🔍 Buscar", key=button_key, use_container_width=True)
        
        st.markdown('</div></div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        return value, button_pressed
    else:
        # Campo simples
        return st.text_input(
            label,
            value=get_field_value(field_name),
            help=help_text,
            placeholder=placeholder,
            key=field_name
        )

def render_responsive_columns(fields_data, columns=2):
    """Renderiza campos em colunas responsivas que se empilham em mobile"""
    st.markdown('<div class="responsive-columns">', unsafe_allow_html=True)
    
    for i in range(0, len(fields_data), columns):
        chunk = fields_data[i:i+columns]
        
        # Criar div flexível em vez de usar st.columns
        st.markdown('<div class="responsive-row">', unsafe_allow_html=True)
        
        for field in chunk:
            st.markdown('<div class="responsive-col">', unsafe_allow_html=True)
            
            field['value'] = st.text_input(
                field['label'],
                value=get_field_value(field['key']),
                help=field.get('help', ''),
                placeholder=field.get('placeholder', ''),
                key=field['key']
            )
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    return {field['key']: field.get('value', '') for field in fields_data}

def main():
    """Função principal do aplicativo"""
    
    # Header limpo e responsivo
    render_header()
    
    # ==================== CONFIGURAÇÃO DE EMAIL ====================
    # Configurar SendGrid/Email antes do formulário
    email_sender, email_ready, email_mode = configurar_sendgrid_streamlit()
    
    # Inicializa session state para manter dados em caso de erro
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Verifica se há erros salvos para mostrar
    if st.session_state.get('show_errors', False) and st.session_state.get('form_errors', []):
        st.markdown('<div class="error-message">', unsafe_allow_html=True)
        st.markdown("❌ **Erros encontrados no formulário anterior:**")
        for erro in st.session_state.form_errors:
            st.markdown(f"• {erro}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("💡 **Seus dados foram preservados!** Corrija os campos destacados abaixo e envie novamente.")
        
        # Limpa os erros após mostrar
        del st.session_state.form_errors
        del st.session_state.show_errors
    
    # Criar opções formatadas para os planos (sempre)
    plano_opcoes_disponiveis = []
    for plano, preco in PLANOS_SEGURO.items():
        plano_opcoes_disponiveis.append(f"{plano}\n{formatar_valor_real(preco)}/ano")
    
    # Inicializa plano padrão apenas se não existir e não há widget ativo
    if 'plano_radio' not in st.session_state and plano_opcoes_disponiveis:
        st.session_state['plano_radio'] = plano_opcoes_disponiveis[0]
    
    # Formulário principal - SEM st.form() para evitar travamento
    # PRIMEIRA SEÇÃO: Identificação do Quiosque
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">📍 Identificação do Quiosque</div>', unsafe_allow_html=True)
    
    # Campo CNPJ com botão de busca usando função responsiva
    cnpj, buscar_cnpj_btn = render_responsive_field(
        label="CNPJ *",
        field_name="cnpj",
        help_text="Digite o CNPJ (14 dígitos)",
        placeholder="00.000.000/0000-00",
        search_button=True
    )
    
    # Campo para exibir razão social (somente leitura)
    razao_social = st.text_input(
        "Razão Social",
        value=get_field_value('razao_social'),
        help="Preenchido automaticamente após buscar CNPJ",
        key="razao_social"
    )
    
    # Campo CEP com botão de busca usando função responsiva
    cep, buscar_cep_btn = render_responsive_field(
        label="CEP *",
        field_name="cep",
        help_text="Digite o CEP no formato 00000-000 (busca automática opcional)",
        placeholder="00000-000",
        search_button=True
    )
    
    logradouro = st.text_input(
        "Logradouro *",
        value=get_field_value('logradouro'),
        help="Digite o endereço ou use a busca automática do CEP",
        key="logradouro"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        numero = st.text_input(
            "Número *",
            value=get_field_value('numero'),
            help="Número do endereço",
            key="numero"
        )
    with col2:
        complemento = st.text_input(
            "Complemento",
            value=get_field_value('complemento'),
            help="Apartamento, sala, etc. (opcional)",
            key="complemento"
        )
    
    col1, col2 = st.columns(2)
    with col1:
        bairro = st.text_input(
            "Bairro *",
            value=get_field_value('bairro'),
            help="Digite o bairro ou use a busca automática do CEP",
            key="bairro"
        )
    with col2:
        cidade = st.text_input(
            "Cidade *",
            value=get_field_value('cidade'),
            help="Digite a cidade ou use a busca automática do CEP",
            key="cidade"
        )
    
    estado = st.text_input(
        "Estado *",
        value=get_field_value('estado'),
        help="Digite o estado (UF) ou use a busca automática do CEP",
        key="estado"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # SEGUNDA SEÇÃO: Identificação do Responsável
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">👤 Identificação do Responsável</div>', unsafe_allow_html=True)
    
    cpf = st.text_input(
        "CPF *",
        value=get_field_value('cpf'),
        help="Digite o CPF no formato 000.000.000-00",
        placeholder="000.000.000-00",
        key="cpf"
    )
    
    nome_completo = st.text_input(
        "Nome Completo *",
        max_chars=120,
        value=get_field_value('nome_completo'),
        help="Digite seu nome completo (máximo 120 caracteres)",
        key="nome_completo"
    )
    
    email = st.text_input(
        "E-mail *",
        value=get_field_value('email'),
        help="Digite um e-mail válido",
        key="email"
    )
    
    telefone = st.text_input(
        "Telefone *",
        value=get_field_value('telefone'),
        help="Digite o telefone (10 ou 11 dígitos)",
        placeholder="(11) 99999-9999",
        key="telefone"
    )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Seção Seguro
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛡️ Plano de Seguro</div>', unsafe_allow_html=True)
    
    render_coberturas_table()
    
    # Processamento dos botões de busca (fora do form)
    if buscar_cnpj_btn and cnpj:
        if validar_cnpj(cnpj):
            razao_social_encontrada = buscar_cnpj(cnpj)
            if razao_social_encontrada:
                # Salva em uma chave separada para evitar conflito
                st.session_state.form_data['razao_social'] = razao_social_encontrada
                st.rerun()
        else:
            st.error("❌ CNPJ deve estar no formato 00.000.000/0000-00 para busca automática")
    
    if buscar_cep_btn and cep:
        if validar_cep(cep):
            endereco = buscar_cep(cep)
            if endereco:
                # Salva em chaves separadas para evitar conflito
                st.session_state.form_data.update(endereco)
                st.rerun()
        else:
            st.error("❌ CEP deve estar no formato 00000-000 para busca automática")

    # ==================== SELEÇÃO DE PLANO E CÁLCULO DINÂMICO (FORA DO FORMULÁRIO) ====================
    
    # Seção de seleção do plano FORA do formulário para atualização em tempo real
    st.markdown('<div class="form-section">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛡️ Seleção do Plano</div>', unsafe_allow_html=True)
    
    # Usar as opções que já criamos anteriormente
    plano_opcoes = plano_opcoes_disponiveis
    
    # Determinar índice padrão baseado no session state
    default_index = 0
    if st.session_state.form_data.get('plano'):
        try:
            default_index = list(PLANOS_SEGURO.keys()).index(st.session_state.form_data.get('plano'))
        except ValueError:
            default_index = 0
    
    plano_selecionado = st.radio(
        "Plano",
        options=plano_opcoes,
        index=default_index,
        key="plano_radio",
        label_visibility="collapsed",
        horizontal=True
    )
    
    # Cálculo dinâmico FORA do formulário - atualiza em tempo real
    if plano_selecionado:
        plano_nome = plano_selecionado.split('\n')[0]
        preco_anual = PLANOS_SEGURO[plano_nome]
        
        # Data de inclusão (hoje)
        tz_sao_paulo = timezone(timedelta(hours=-3))
        data_inclusao = datetime.now(tz_sao_paulo).replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Calcula pró-rata
        dias_restantes, premio_pro_rata = calcular_pro_rata(plano_nome, data_inclusao)
        
        # Exibe o cálculo detalhado
        st.markdown("---")
        
        # Container centralizado para o cálculo
        col_esq, col_calc, col_dir = st.columns([0.5, 2, 0.5])
        
        with col_calc:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📅 Período de Vigência:**")
                st.markdown(f"• **Data de Inclusão:** {data_inclusao.strftime('%d/%m/%Y')}")
                st.markdown(f"• **Final da Vigência:** {DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}")
                st.markdown(f"• **Dias Restantes:** {dias_restantes} dias")
                
            with col2:
                st.markdown("**💰 Memória de Cálculo:**")
                st.markdown(f"• **Prêmio Anual:** {formatar_valor_real(preco_anual)}")
                st.markdown(f"• **Valor Diário:** {formatar_valor_real(preco_anual/365)}")
                st.markdown(f"• **Cálculo:** {formatar_valor_real(preco_anual/365)} × {dias_restantes} dias")
        
        # Valor final destacado
        st.markdown("---")
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            border: 2px solid #48bb78;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 2px 8px rgba(72, 187, 120, 0.2);
        ">
            <h3 style="color: #22543d; margin: 0 0 0.5rem 0; font-size: 1.1rem;">
                🎯 Valor Final do Prêmio
            </h3>
            <div style="color: #22543d; font-size: 1.5rem; font-weight: bold; margin: 0;">
                {formatar_valor_real(premio_pro_rata)}
            </div>
            <div style="color: #2f855a; font-size: 0.8rem; margin-top: 0.5rem;">
                Válido de {data_inclusao.strftime('%d/%m/%Y')} até {DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ==================== BOTÃO DE ENVIO FINAL ====================
    
    # Botão de envio FORA do formulário - ÚLTIMA COISA
    st.markdown("---")
    enviar_formulario = st.button("🚀 Calcular e Enviar", use_container_width=True, type="primary", key="enviar_formulario_final")

    # Processamento do formulário quando enviado
    if enviar_formulario:
        # Pega os valores dos campos do formulário via session_state
        dados = preparar_dados_formulario(st.session_state)
        
        # Validações
        erros = validar_formulario(dados)
        
        if erros:
            # Salva dados no session state para preservar
            st.session_state.form_data.update(dados)
            
            # Mostra erros de forma mais amigável
            st.markdown('<div class="error-message">', unsafe_allow_html=True)
            st.markdown("❌ **Por favor, corrija os seguintes campos:**")
            for erro in erros:
                st.markdown(f"• {erro}")
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Adiciona uma mensagem explicativa
            st.info("💡 **Dica:** Corrija os campos acima e clique em 'Calcular e Enviar' novamente. Seus dados foram preservados!")
            
        else:
            # Se chegou aqui, não há erros - limpa dados preservados e processa o envio
            st.session_state.form_data = {}  # Limpa dados preservados
            
            # Extrai o nome do plano
            plano_nome = dados['plano_selecionado'].split('\n')[0]
            
            # Data de inclusão (hoje)
            tz_sao_paulo = timezone(timedelta(hours=-3))
            data_inclusao = datetime.now(tz_sao_paulo).replace(hour=0, minute=0, second=0, microsecond=0)
            
            # Calcula pró-rata
            dias_restantes, premio_pro_rata = calcular_pro_rata(plano_nome, data_inclusao)
            
            # Prepara dados para salvar
            dados['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
            dados['data_inclusao'] = data_inclusao.strftime('%Y-%m-%d')
            dados['dias_restantes'] = dias_restantes
            dados['premio_pro_rata'] = premio_pro_rata
            
            # Tenta enviar email
            try:
                email_sucesso = enviar_email_confirmacao(dados, email_sender, email_mode)
                
                if email_sucesso:
                    # Sucesso (pelo menos um funcionou)
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    mensagem_sucesso = f"✅ **Mensagem transmitida com sucesso!**<br>"
                    mensagem_sucesso += f"📧 **Seus dados foram enviados para nossa equipe.**<br>"
                    mensagem_sucesso += f"💰 **Prêmio pró-rata calculado:** {formatar_valor_real(premio_pro_rata)} para {dias_restantes} dias<br><br>"
                    mensagem_sucesso += f"🕐 **Em breve você receberá a confirmação do recebimento e informações sobre a cobertura.**<br>"
                    
                    if email_mode == "Teste (sem envio)":
                        mensagem_sucesso += "🧪 **Modo de teste ativo - dados processados localmente!**"
                    elif email_mode == "SendGrid":
                        mensagem_sucesso += "📨 **Nossa equipe entrará em contato em até 24 horas.**"
                    else:
                        mensagem_sucesso += "📨 **Nossa equipe entrará em contato em até 24 horas.**"
                    
                    st.markdown(mensagem_sucesso, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    # Opções pós-envio
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📝 Novo Formulário", key="new_form_button", use_container_width=True):
                            # Limpa todos os dados para novo formulário
                            keys_to_clear = ['form_data', 'cpf', 'nome_completo', 'email', 'telefone', 
                                           'cnpj', 'razao_social', 'cep', 'logradouro', 'numero', 'complemento', 
                                           'bairro', 'cidade', 'estado']
                            for key in keys_to_clear:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                    
                    with col2:
                        if st.button("📋 Ver Resumo", key="show_summary_button", use_container_width=True):
                            # Mostra resumo dos dados enviados
                            with st.expander("📋 Resumo dos dados enviados", expanded=True):
                                st.markdown(f"""
                                **👤 Cliente:** {dados['nome_completo']}  
                                **📧 Email:** {dados['email']}  
                                **🏢 Empresa:** {dados['razao_social']}  
                                **🛡️ Plano:** {plano_nome}  
                                **💰 Prêmio:** {formatar_valor_real(premio_pro_rata)}  
                                **📅 Vigência:** {data_inclusao.strftime('%d/%m/%Y')} até {DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}
                                """)
                    
                else:
                    # Falha no envio - preserva dados e permite nova tentativa
                    st.markdown('<div class="error-message">', unsafe_allow_html=True)
                    st.markdown("❌ **Erro ao transmitir mensagem. Verifique as configurações e tente novamente.**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    st.info("💡 **Seus dados foram preservados.** Corrija as configurações de email e clique em 'Calcular e Enviar' novamente.")
                    
            except Exception as e:
                st.error(f"❌ Erro crítico no processamento: {str(e)}")
                st.info("💡 **Seus dados foram preservados.** Corrija o problema e tente novamente.")

if __name__ == "__main__":
    main() 