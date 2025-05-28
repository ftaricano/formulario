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

# Configuração da página
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"]
)

# ==================== CONFIGURAÇÕES ====================

# CSS customizado para estética moderna e agradável
st.markdown("""
<style>
    /* Importar fonte moderna do Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Configuração geral da página */
    .stApp {
        background: #ffffff;
        min-height: 100vh;
    }
    
    /* Container principal */
    .main {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
        max-width: 520px;
        margin: 0 auto;
        padding: 1rem 0.5rem;
    }
    
    /* Card principal do formulário */
    .main > div {
        background: #ffffff;
        border-radius: 20px;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
        padding: 1.5rem;
        border: 1px solid #e2e8f0;
    }
    
    /* Título principal */
    h1 {
        color: #1a202c !important;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        font-size: 2.5rem;
    }
    
    /* Botões principais */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        width: 100%;
        height: 3rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
    }
    
    .stButton > button:active {
        transform: translateY(0);
    }
    
    /* Botões de busca menores */
    .stButton > button[kind="secondary"] {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        padding: 0.5rem 1rem;
        font-size: 0.875rem;
        height: 2.5rem;
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.3);
    }
    
    /* Alinhamento dos botões de busca com os campos */
    .stFormSubmitButton {
        margin-top: 1.75rem;
    }
    
    .stFormSubmitButton > button {
        background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
        color: white !important;
        border: none;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-weight: 600;
        font-size: 0.875rem;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 2px 8px rgba(72, 187, 120, 0.3);
        width: 100%;
        height: 3.5rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .stFormSubmitButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(72, 187, 120, 0.4);
        background: linear-gradient(135deg, #38a169 0%, #2f855a 100%);
    }
    
    /* Botão principal do formulário */
    .stFormSubmitButton > button[type="submit"]:not([aria-label*="Buscar"]) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        height: 3rem;
        margin-top: 0;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stFormSubmitButton > button[type="submit"]:not([aria-label*="Buscar"]):hover {
        background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    /* Campos de input */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border: 2px solid #d1d5db;
        border-radius: 12px;
        padding: 0.75rem 1rem;
        font-size: 1rem;
        transition: all 0.3s ease;
        background: #ffffff !important;
        color: #1a202c !important;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.02);
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        outline: none;
        background: #ffffff !important;
    }
    
    /* Estados específicos dos campos para garantir fundo branco */
    .stTextInput > div > div > input:hover,
    .stTextInput > div > div > input:active,
    .stTextInput > div > div > input:valid,
    .stTextInput > div > div > input:invalid,
    .stSelectbox > div > div > select:hover,
    .stSelectbox > div > div > select:active,
    .stSelectbox > div > div > select:valid,
    .stSelectbox > div > div > select:invalid {
        background: #ffffff !important;
        color: #1a202c !important;
    }
    
    /* Autocomplete e preenchimento automático */
    .stTextInput > div > div > input:-webkit-autofill,
    .stTextInput > div > div > input:-webkit-autofill:hover,
    .stTextInput > div > div > input:-webkit-autofill:focus,
    .stTextInput > div > div > input:-webkit-autofill:active {
        -webkit-box-shadow: 0 0 0 30px #ffffff inset !important;
        -webkit-text-fill-color: #1a202c !important;
        background: #ffffff !important;
    }
    
    /* Labels dos campos */
    .stTextInput > label,
    .stSelectbox > label {
        color: #1a202c !important;
        font-weight: 600;
        font-size: 0.875rem;
        margin-bottom: 0.5rem;
    }
    
    /* Seções do formulário */
    .form-section {
        background: #f8f9fa;
        border: 1px solid #e2e8f0;
        border-left: 4px solid #1e3a8a;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1.5rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
    }
    
    .section-title {
        color: #1a202c !important;
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Mensagens de sucesso */
    .success-message {
        background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
        color: #22543d;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #9ae6b4;
        margin: 1.5rem 0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(72, 187, 120, 0.15);
    }
    
    /* Mensagens de erro */
    .error-message {
        background: linear-gradient(135deg, #fed7d7 0%, #feb2b2 100%);
        color: #742a2a;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #feb2b2;
        margin: 1.5rem 0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(245, 101, 101, 0.15);
    }
    
    /* Avisos */
    .stAlert {
        border-radius: 12px;
        border: none;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
    }
    
    /* Divisores */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.5rem 0;
    }
    
    /* Colunas */
    .row-widget.stHorizontal {
        gap: 1rem;
    }
    
    /* Campos desabilitados */
    .stTextInput > div > div > input:disabled {
        background: #e5e7eb;
        color: #1a202c;
        border-color: #d1d5db;
    }
    
    /* Placeholder text */
    .stTextInput > div > div > input::placeholder {
        color: #9ca3af;
        font-style: italic;
    }
    
    /* Selectbox styling */
    .stSelectbox > div > div {
        background: #ffffff !important;
        border-radius: 12px;
    }
    
    /* Garantir que o selectbox interno também seja branco */
    .stSelectbox > div > div > select,
    .stSelectbox > div > div > div {
        background: #ffffff !important;
        color: #1a202c !important;
    }
    
    /* Help text */
    .stTextInput > div > div > div,
    .stSelectbox > div > div > div {
        color: #6b7280;
        font-size: 0.75rem;
        margin-top: 0.25rem;
    }
    
    /* Logo container */
    .stImage {
        display: flex;
        justify-content: center;
        margin-bottom: 1rem;
    }
    
    /* Responsividade */
    @media (max-width: 768px) {
        .main {
            padding: 1rem 0.5rem;
            max-width: 100%;
        }
        
        .main > div {
            padding: 1.5rem;
            border-radius: 16px;
        }
        
        .form-section {
            padding: 1.5rem;
        }
        
        h1 {
            font-size: 2rem;
        }
        
        /* Barra superior responsiva */
        .header-bar {
            padding: 1rem !important;
        }
        
        .header-content {
            flex-direction: column !important;
            text-align: center !important;
            gap: 1rem !important;
        }
        
        .header-title {
            font-size: 1.2rem !important;
            text-align: center !important;
        }
        
        .header-subtitle {
            font-size: 0.8rem !important;
            text-align: center !important;
        }
        
        /* Logo na barra superior em mobile */
        .stImage {
            display: flex !important;
            justify-content: center !important;
        }
    }
    
    /* Animações suaves */
    * {
        transition: all 0.2s ease;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #667eea;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #5a67d8;
    }
    
    /* Garantir que todos os textos fiquem escuros */
    .stMarkdown, .stMarkdown p, .stMarkdown div {
        color: #1a202c !important;
    }
    
    /* Texto dos botões de formulário */
    .stFormSubmitButton > button {
        color: white !important;
    }
    
    /* Divisor mais sutil */
    hr {
        border: none;
        height: 1px;
        background: #e2e8f0;
        margin: 2rem 0;
    }
    
    /* Estilização dos Radio Buttons para Planos */
    .stRadio > div {
        display: flex;
        flex-direction: row;
        gap: 1rem;
        justify-content: space-between;
        flex-wrap: wrap;
    }
    
    .stRadio > div > label {
        background: #ffffff;
        border: 2px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        flex: 1;
        min-width: 150px;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
        position: relative;
        overflow: hidden;
        margin: 0;
    }
    
    .stRadio > div > label:hover {
        border-color: #667eea;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.15);
    }
    
    /* Estilo quando selecionado */
    .stRadio > div > label:has(input:checked) {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-color: #667eea;
        color: white;
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
    }
    
    .stRadio > div > label:has(input:checked) > div {
        color: white !important;
    }
    
    /* Esconder o radio button padrão */
    .stRadio input[type="radio"] {
        display: none;
    }
    
    /* Estilizar o texto dos radio buttons */
    .stRadio > div > label > div {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        color: #1a202c;
        font-weight: 600;
        white-space: pre-line;
        line-height: 1.4;
    }
    
    .stRadio > div > label:has(input:checked) > div {
        color: white !important;
    }
    
    /* Responsividade para radio buttons */
    @media (max-width: 768px) {
        .stRadio > div {
            flex-direction: column;
            gap: 0.75rem;
        }
        
        .stRadio > div > label {
            min-width: unset;
            padding: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def carregar_logo():
    """Carrega e exibe o logo da empresa"""
    try:
        st.image(APP_CONFIG["logo_path"], width=APP_CONFIG["logo_width"])
    except FileNotFoundError:
        st.warning(MENSAGENS["logo_nao_encontrado"])

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
    
    def enviar_email_formulario(self, dados_formulario, email_destino="seguros@grupocp.com.br"):
        """
        Envia email com dados do formulário
        
        Args:
            dados_formulario (dict): Dados do formulário preenchido
            email_destino (str): Email de destino
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
                .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #667eea; padding-bottom: 5px; }}
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
                        <div class="section-title">📍 Endereço do Quiosque</div>
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
                .header {{ background: linear-gradient(135deg, #48bb78, #38a169); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                .section {{ margin-bottom: 25px; }}
                .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #48bb78; padding-bottom: 5px; }}
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
    Função para configurar SendGrid no Streamlit
    """
    # Configuração na sidebar
    st.sidebar.header("⚙️ Configuração Email")
    
    # Opção para usar modo de teste ou SendGrid
    email_mode = st.sidebar.selectbox(
        "Modo de Email:",
        ["Teste (sem envio)", "SendGrid", "SMTP Tradicional"],
        help="Escolha como enviar os emails do formulário"
    )
    
    if email_mode == "SendGrid":
        if not SENDGRID_AVAILABLE:
            st.sidebar.error("❌ SendGrid não instalado! Execute: pip install sendgrid")
            return None, False, email_mode
        
        # Tentar carregar configurações do secrets.toml primeiro
        api_key_from_secrets = None
        email_destino_from_secrets = "seguros@grupocp.com.br"
        
        try:
            if hasattr(st, 'secrets') and 'sendgrid' in st.secrets:
                api_key_from_secrets = st.secrets["sendgrid"].get("api_key", "")
                email_destino_from_secrets = st.secrets["sendgrid"].get("email_destino", "seguros@grupocp.com.br")
                
                if api_key_from_secrets and api_key_from_secrets != "SG.sua_api_key_aqui":
                    st.sidebar.success("🔐 Configuração carregada do secrets.toml")
        except Exception:
            pass  # Ignora erros de secrets
        
        # Input para API Key (com valor padrão do secrets se disponível)
        api_key = st.sidebar.text_input(
            "SendGrid API Key:",
            value=api_key_from_secrets if api_key_from_secrets and api_key_from_secrets != "SG.sua_api_key_aqui" else "",
            type="password",
            help="Cole aqui sua API Key do SendGrid ou configure no secrets.toml",
            key="sendgrid_api_key"
        )
        
        # Input para email de destino (com valor padrão do secrets se disponível)
        email_destino = st.sidebar.text_input(
            "Email de Destino:",
            value=email_destino_from_secrets,
            help="Email que receberá as solicitações",
            key="sendgrid_email_destino"
        )
        
        if api_key:
            try:
                sender = SendGridEmailSender(api_key)
                st.sidebar.success("✅ SendGrid configurado!")
                
                # Mostrar informações de configuração
                if api_key_from_secrets and api_key == api_key_from_secrets:
                    st.sidebar.info("📋 Usando configuração do secrets.toml")
                else:
                    st.sidebar.info("📋 Usando configuração manual")
                
                return sender, True, email_mode
            except Exception as e:
                st.sidebar.error(f"❌ Erro na configuração: {str(e)}")
                return None, False, email_mode
        else:
            if api_key_from_secrets:
                st.sidebar.warning("⚠️ Configure a API Key no secrets.toml ou insira manualmente")
            else:
                st.sidebar.warning("⚠️ Insira a API Key do SendGrid")
            return None, False, email_mode
            
    elif email_mode == "SMTP Tradicional":
        st.sidebar.info("📧 Usando configuração SMTP tradicional")
        return None, True, email_mode
    else:
        st.sidebar.info("📧 Modo de teste ativo - emails não serão enviados")
        return None, True, email_mode

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
    """Envia email de confirmação com todas as informações"""
    try:
        # Modo de teste
        if email_mode == "Teste (sem envio)":
            st.info("🧪 **Modo de teste ativado** - Emails não serão enviados, mas dados foram processados com sucesso!")
            st.success("✅ Formulário processado com sucesso!")
            
            # Mostrar preview dos emails que seriam enviados
            with st.expander("📧 Preview dos emails que seriam enviados", expanded=False):
                plano_nome = dados.get('plano_selecionado', '').split('\n')[0] if dados.get('plano_selecionado') else 'Não selecionado'
                
                st.markdown("### 📨 Email 1 - Para a Empresa")
                st.markdown("**Para:** seguros@grupocp.com.br")
                st.markdown("**Assunto:** 🛡️ Nova Solicitação - Seguro Incêndio Conteúdos - " + dados['nome_completo'])
                st.markdown("**Tipo:** Notificação de nova adesão (dados completos)")
                
                st.markdown("---")
                
                st.markdown("### 📨 Email 2 - Para o Cliente")
                st.markdown(f"**Para:** {dados['email']}")
                st.markdown("**Assunto:** ✅ Confirmação de Adesão - Seguro Incêndio Conteúdos - " + dados['nome_completo'])
                st.markdown("**Tipo:** Confirmação de recebimento da solicitação")
                
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
                emails_enviados = 0
                mensagens = []
                
                # 1. Enviar para empresa
                email_destino = st.session_state.get('sendgrid_email_destino', 'seguros@grupocp.com.br')
                sucesso_empresa, msg_empresa = email_sender.enviar_email_formulario(dados, email_destino)
                
                if sucesso_empresa:
                    emails_enviados += 1
                    mensagens.append(f"✅ Email enviado para empresa: {email_destino}")
                else:
                    mensagens.append(f"❌ Erro ao enviar para empresa: {msg_empresa}")
                
                # 2. Enviar confirmação para cliente
                email_cliente = dados.get('email', '').strip()
                if email_cliente and validar_email(email_cliente):
                    sucesso_cliente, msg_cliente = email_sender.enviar_email_confirmacao_cliente(dados)
                    
                    if sucesso_cliente:
                        emails_enviados += 1
                        mensagens.append(f"✅ Email de confirmação enviado para cliente: {email_cliente}")
                    else:
                        mensagens.append(f"❌ Erro ao enviar para cliente: {msg_cliente}")
                else:
                    mensagens.append("⚠️ Email do cliente inválido - confirmação não enviada")
                
                # Exibir resultados
                for mensagem in mensagens:
                    if "✅" in mensagem:
                        st.success(mensagem)
                    elif "❌" in mensagem:
                        st.error(mensagem)
                    else:
                        st.warning(mensagem)
                
                # Retorna True se pelo menos um email foi enviado
                return emails_enviados > 0
                    
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
            
            # Lista de destinatários
            destinatarios = [EMAIL_CONFIG["email_empresa"], dados['email']]
            
            # Corpo do email em HTML
            corpo_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: 'Segoe UI', Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #667eea, #764ba2); color: white; padding: 20px; border-radius: 10px 10px 0 0; text-align: center; }}
                    .content {{ background: #f8f9fa; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .section {{ margin-bottom: 25px; }}
                    .section-title {{ color: #2d3748; font-size: 18px; font-weight: bold; margin-bottom: 10px; border-bottom: 2px solid #667eea; padding-bottom: 5px; }}
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
                            <div class="section-title">📍 Endereço do Quiosque</div>
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
            
            # Enviar para cada destinatário
            emails_enviados = 0
            for destinatario in destinatarios:
                try:
                    # Criar mensagem individual
                    msg = MIMEMultipart()
                    msg['From'] = EMAIL_CONFIG["email_remetente"]
                    msg['To'] = destinatario
                    
                    # Assunto personalizado baseado no destinatário
                    if destinatario == dados['email']:
                        msg['Subject'] = f"✅ Confirmação de Adesão de Seguro - {dados['nome_completo']}"
                    else:
                        msg['Subject'] = f"🛡️ Nova Adesão de Seguro - {dados['nome_completo']}"
                    
                    # Anexar corpo HTML
                    msg.attach(MIMEText(corpo_html, 'html'))
                    
                    # Enviar email
                    text = msg.as_string()
                    server.sendmail(EMAIL_CONFIG["email_remetente"], destinatario, text)
                    emails_enviados += 1
                    
                except Exception as e:
                    st.warning(f"⚠️ Erro ao enviar email para {destinatario}: {str(e)}")
            
            server.quit()
            
            # Retorna True se pelo menos um email foi enviado
            return emails_enviados > 0
        
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
        st.error(f"❌ Erro inesperado ao enviar email: {str(e)}")
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

def main():
    """Função principal do aplicativo"""
    
    # Barra superior compacta com logo e títulos
    st.markdown("""
    <div class="header-bar" style="
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        margin: -1rem -1rem 2rem -1rem;
        border-radius: 0 0 16px 16px;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        text-align: center;
    ">
    """, unsafe_allow_html=True)
    
    # Inserir logo real usando a função existente
    try:
        # Logo centralizado e menor
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            st.markdown('<div style="display: flex; justify-content: center; margin-bottom: 1rem;">', unsafe_allow_html=True)
            # Usar CSS para reduzir o tamanho do logo
            st.markdown("""
            <style>
            .stImage > img {
                width: 80px !important;
                height: auto !important;
                max-width: 80px !important;
            }
            </style>
            """, unsafe_allow_html=True)
            carregar_logo()
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Textos centralizados
        st.markdown("""
        <div style="text-align: center; color: white;">
            <h1 class="header-title" style="
                color: white; 
                font-weight: 700; 
                font-size: 1.4rem; 
                margin: 0 0 0.5rem 0;
                line-height: 1.2;
            ">Formulário de Adesão</h1>
            <p class="header-subtitle" style="
                color: rgba(255,255,255,0.9); 
                font-size: 1.9rem; 
                margin: 0;
                font-weight: 500;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            ">Seguro Incêndio Conteúdos - Cessionários <span style="color: #000080; font-weight: 600;">ORLA RIO</span></p>
        </div>
        """, unsafe_allow_html=True)
        
    except Exception as e:
        # Fallback se houver erro
        st.markdown("""
        <div style="text-align: center; color: white;">
            <h1 style="margin: 0 0 0.5rem 0; font-size: 1.4rem; font-weight: 700;">Formulário de Adesão</h1>
            <p style="margin: 0; font-size: 0.9rem; opacity: 0.9;">Seguro Incêndio Conteúdos - Cessionários <span style="color: #000080;">ORLA RIO</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    # Fechar a div da barra
    st.markdown("""
    </div>
    """, unsafe_allow_html=True)
    
    # ==================== CONFIGURAÇÃO DE EMAIL ====================
    # Configurar SendGrid/Email antes do formulário
    email_sender, email_ready, email_mode = configurar_sendgrid_streamlit()
    
    # Inicializa session state para manter dados em caso de erro
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    # Criar opções formatadas para os planos (sempre)
    plano_opcoes_disponiveis = []
    for plano, preco in PLANOS_SEGURO.items():
        plano_opcoes_disponiveis.append(f"{plano}\n{formatar_valor_real(preco)}/ano")
    
    # Inicializa plano padrão apenas se não existir e não há widget ativo
    if 'plano_radio' not in st.session_state and plano_opcoes_disponiveis:
        st.session_state['plano_radio'] = plano_opcoes_disponiveis[0]
    
    # Formulário principal
    with st.form("formulario_seguro"):
        
        # Seção Identificação
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">👤 Identificação do Responsável</div>', unsafe_allow_html=True)
        
        cpf = st.text_input(
            "CPF *",
            value=st.session_state.form_data.get('cpf', ''),
            help="Digite o CPF no formato 000.000.000-00",
            placeholder="000.000.000-00",
            key="cpf"
        )
        
        nome_completo = st.text_input(
            "Nome Completo *",
            max_chars=120,
            value=st.session_state.form_data.get('nome_completo', ''),
            help="Digite seu nome completo (máximo 120 caracteres)",
            key="nome_completo"
        )
        
        email = st.text_input(
            "E-mail *",
            value=st.session_state.form_data.get('email', ''),
            help="Digite um e-mail válido",
            key="email"
        )
        
        telefone = st.text_input(
            "Telefone *",
            value=st.session_state.form_data.get('telefone', ''),
            help="Digite o telefone (10 ou 11 dígitos)",
            placeholder="(11) 99999-9999",
            key="telefone"
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            cnpj = st.text_input(
                "CNPJ *",
                value=st.session_state.form_data.get('cnpj', ''),
                help="Digite o CNPJ (14 dígitos)",
                placeholder="00.000.000/0000-00",
                key="cnpj"
            )
        with col2:
            buscar_cnpj_btn = st.form_submit_button("🔍 Buscar CNPJ")
        
        # Campo para exibir razão social (somente leitura)
        razao_social = st.text_input(
            "Razão Social",
            value=st.session_state.form_data.get('razao_social', ''),
            help="Preenchido automaticamente após buscar CNPJ",
            key="razao_social"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Seção Endereço
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">📍 Endereço do Quiosque</div>', unsafe_allow_html=True)
        
        col1, col2 = st.columns([3, 1])
        with col1:
            cep = st.text_input(
                "CEP *",
                value=st.session_state.form_data.get('cep', ''),
                help="Digite o CEP no formato 00000-000 (busca automática opcional)",
                placeholder="00000-000",
                key="cep"
            )
        with col2:
            buscar_cep_btn = st.form_submit_button("🔍 Buscar CEP")
        
        logradouro = st.text_input(
            "Logradouro *",
            value=st.session_state.form_data.get('logradouro', ''),
            help="Digite o endereço ou use a busca automática do CEP",
            key="logradouro"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            numero = st.text_input(
                "Número *",
                value=st.session_state.form_data.get('numero', ''),
                help="Número do endereço",
                key="numero"
            )
        with col2:
            complemento = st.text_input(
                "Complemento",
                value=st.session_state.form_data.get('complemento', ''),
                help="Apartamento, sala, etc. (opcional)",
                key="complemento"
            )
        
        col1, col2 = st.columns(2)
        with col1:
            bairro = st.text_input(
                "Bairro *",
                value=st.session_state.form_data.get('bairro', ''),
                help="Digite o bairro ou use a busca automática do CEP",
                key="bairro"
            )
        with col2:
            cidade = st.text_input(
                "Cidade *",
                value=st.session_state.form_data.get('cidade', ''),
                help="Digite a cidade ou use a busca automática do CEP",
                key="cidade"
            )
        
        estado = st.text_input(
            "Estado *",
            value=st.session_state.form_data.get('estado', ''),
            help="Digite o estado (UF) ou use a busca automática do CEP",
            key="estado"
        )
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Seção Seguro
        st.markdown('<div class="form-section">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">🛡️ Plano de Seguro</div>', unsafe_allow_html=True)
        
        # Tabela de coberturas detalhadas
        st.markdown("### 📋 Detalhamento das Coberturas")
        st.markdown("""
        <div style="overflow-x: auto; margin: 1.5rem 0;">
            <table style="
                width: 100%; 
                min-width: 650px;
                border-collapse: collapse; 
                background: white; 
                border-radius: 8px; 
                overflow: hidden; 
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                table-layout: fixed;
            ">
                <thead>
                    <tr style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white;">
                        <th style="
                            padding: 12px 8px; 
                            text-align: left; 
                            font-weight: 600; 
                            width: 26%;
                            white-space: nowrap;
                            font-size: 0.9rem;
                        ">Coberturas</th>
                        <th style="
                            padding: 12px 8px; 
                            text-align: center; 
                            font-weight: 600; 
                            width: 18%;
                            white-space: nowrap;
                            font-size: 0.85rem;
                        ">Opção 1<br><span style='font-size: 0.8rem;'>R$ 250.000</span></th>
                        <th style="
                            padding: 12px 8px; 
                            text-align: center; 
                            font-weight: 600; 
                            width: 18%;
                            white-space: nowrap;
                            font-size: 0.85rem;
                        ">Opção 2<br><span style='font-size: 0.8rem;'>R$ 400.000</span></th>
                        <th style="
                            padding: 12px 8px; 
                            text-align: center; 
                            font-weight: 600; 
                            width: 18%;
                            white-space: nowrap;
                            font-size: 0.85rem;
                        ">Opção 3<br><span style='font-size: 0.8rem;'>R$ 700.000</span></th>
                        <th style="
                            padding: 12px 8px; 
                            text-align: center; 
                            font-weight: 600; 
                            width: 20%;
                            white-space: nowrap;
                            font-size: 0.85rem;
                        ">Franquia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr style="background: #f8f9fa;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Incêndio, Raio e Explosão</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 250.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 400.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 700.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(**) R$ 30.000</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Alagamento</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 50.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 150.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 15.000</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Danos Elétricos</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 20.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 50.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 3.000</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Pequenas Obras</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 50.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 150.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 5.000</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Perda/Pgto Aluguel (6 meses)</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 20.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 30.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 40.000</td>
                        <td style="padding: 8px; text-align: center; color: #16a34a; font-size: 0.8rem;">Não Há</td>
                    </tr>
                    <tr style="background: white;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Vidros</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 20.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 50.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 3.000</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Tumultos</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 150.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 200.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 5.000</td>
                    </tr>
                    <tr style="background: #f8f9fa;">
                        <td style="
                            padding: 8px; 
                            font-weight: 500; 
                            color: #2563eb;
                            font-size: 0.85rem;
                            white-space: nowrap;
                        ">Vendaval</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 100.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 150.000</td>
                        <td style="padding: 8px; text-align: center; font-size: 0.8rem;">R$ 200.000</td>
                        <td style="padding: 8px; text-align: center; color: #dc2626; font-size: 0.8rem;">(*) R$ 10.000</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)
        
        # Legenda das franquias
        st.markdown("""
        <div style="background: #f0f8ff; border-left: 4px solid #2563eb; padding: 1rem; margin: 1rem 0; border-radius: 0 8px 8px 0;">
            <p style="margin: 0; font-size: 0.875rem; color: #1e40af;">
                <strong>📝 Legenda das Franquias:</strong><br>
                (*) Franquia aplicável por sinistro<br>
                (**) Franquia aplicável por sinistro para Incêndio, Raio e Explosão<br>
                • Cobertura "Perda/Pgto Aluguel" não possui franquia
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Processamento dos botões de busca
        if buscar_cnpj_btn and cnpj:
            if validar_cnpj(cnpj):
                razao_social_encontrada = buscar_cnpj(cnpj)
                if razao_social_encontrada:
                    st.session_state.form_data['razao_social'] = razao_social_encontrada
                    st.rerun()
            else:
                st.error("❌ CNPJ deve estar no formato 00.000.000/0000-00 para busca automática")
        
        if buscar_cep_btn and cep:
            if validar_cep(cep):
                endereco = buscar_cep(cep)
                if endereco:
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
            border-radius: 12px;
            padding: 1.5rem;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 4px 12px rgba(72, 187, 120, 0.2);
        ">
            <h3 style="color: #22543d; margin: 0 0 0.5rem 0; font-size: 1.25rem;">
                🎯 Valor Final do Prêmio
            </h3>
            <div style="color: #22543d; font-size: 2rem; font-weight: bold; margin: 0;">
                {formatar_valor_real(premio_pro_rata)}
            </div>
            <div style="color: #2f855a; font-size: 0.875rem; margin-top: 0.5rem;">
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
            st.markdown('<div class="error-message">', unsafe_allow_html=True)
            st.markdown("❌ **Corrija os seguintes erros:**")
            for erro in erros:
                st.markdown(f"• {erro}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Salva dados no session state para preservar
            st.session_state.form_data = dados
            
            # Adiciona um botão para tentar novamente
            if st.button("🔄 Tentar Novamente", key="retry_button", use_container_width=True):
                # Limpa o estado de erro e permite nova tentativa
                if 'form_error' in st.session_state:
                    del st.session_state['form_error']
                st.rerun()
            
            # Marca que houve erro para evitar loop
            st.session_state['form_error'] = True
            st.stop()
        
        # Se chegou aqui, não há erros - limpa flag de erro se existir
        if 'form_error' in st.session_state:
            del st.session_state['form_error']
        
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
                mensagem_sucesso = f"✅ **Formulário enviado com sucesso!**<br>"
                mensagem_sucesso += f"💰 **Prêmio pró-rata:** {formatar_valor_real(premio_pro_rata)} para {dias_restantes} dias<br>"
                
                if email_mode == "Teste (sem envio)":
                    mensagem_sucesso += "🧪 **Modo de teste ativo - dados processados localmente!**"
                elif email_mode == "SendGrid":
                    mensagem_sucesso += "📧 **Email enviado via SendGrid!**"
                else:
                    mensagem_sucesso += "📧 **Emails de confirmação enviados!**"
                
                st.markdown(mensagem_sucesso, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Limpa session state dos campos do formulário, mas preserva plano padrão
                keys_to_clear = ['form_data', 'form_error', 'cpf', 'nome_completo', 'email', 'telefone', 
                               'cnpj', 'razao_social', 'cep', 'logradouro', 'numero', 'complemento', 
                               'bairro', 'cidade', 'estado']
                for key in keys_to_clear:
                    if key in st.session_state:
                        del st.session_state[key]
                
                # Nota: plano_radio não pode ser modificado após widget ser criado
                # O usuário pode selecionar manualmente o plano desejado para próximo formulário
                
                # Botão para novo formulário
                if st.button("📝 Preencher Novo Formulário", key="new_form_button", use_container_width=True):
                    st.rerun()
                
                st.stop()
                
            else:
                # Falha total - preserva dados
                st.markdown('<div class="error-message">', unsafe_allow_html=True)
                st.markdown("❌ **Erro ao processar formulário. Verifique as configurações e tente novamente.**")
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Salva dados no session state
                st.session_state.form_data = dados
                
                # Botão para tentar novamente
                if st.button("🔄 Tentar Novamente", key="retry_email_button", use_container_width=True):
                    st.rerun()
                
        except Exception as e:
            st.error(f"❌ Erro crítico no processamento: {str(e)}")
            st.error(f"Tipo do erro: {type(e).__name__}")
            
            # Salva dados no session state
            st.session_state.form_data = dados
            
            # Botão para tentar novamente
            if st.button("🔄 Tentar Novamente", key="retry_exception_button", use_container_width=True):
                st.rerun()

if __name__ == "__main__":
    main() 