import streamlit as st
import requests
from datetime import datetime, timezone, timedelta
import re
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, Optional, Tuple
import os
from functools import lru_cache
import base64

try:
    from sendgrid import SendGridAPIClient
    from sendgrid.helpers.mail import Mail, Email, To, Content
    SENDGRID_AVAILABLE = True
except ImportError:
    SENDGRID_AVAILABLE = False

from config import (
    PLANOS_SEGURO, DATA_FINAL_VIGENCIA, EMAIL_CONFIG, API_URLS, 
    TIMEOUT_CONFIG, REGEX_PATTERNS, APP_CONFIG, MENSAGENS, CAMPOS_OBRIGATORIOS
)

st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"]
)

def load_css():
    try:
        with open("styles.css", "r", encoding="utf-8") as f:
            css_content = f.read()
        st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning("⚠️ Arquivo styles.css não encontrado.")

load_css()

def ocultar_cabecalho_streamlit():
    st.markdown("""
    <style>
    div[data-testid="stHeader"] {
        visibility: hidden !important;
        height: 0 !important;
        display: none !important;
    }
    div[data-testid="stHeaderActionElements"] {
        display: none !important;
        visibility: hidden !important;
    }
    .stDeployButton,
    div[data-testid="stDecoration"],
    div[data-testid="stToolbar"],
    div[data-testid="stSidebarUserInfo"] {
        display: none !important;
        visibility: hidden !important;
    }
    </style>
    """, unsafe_allow_html=True)

ocultar_cabecalho_streamlit()

def carregar_logo(width=None):
    try:
        logo_width = width if width is not None else 80
        st.markdown(f"""
        <div style="display: flex; justify-content: center; margin: 0 auto;">
            <img src="data:image/png;base64,{get_logo_base64()}" 
                 style="max-width: {logo_width}px; border-radius: 8px;" 
                 alt="Logo CPZ">
        </div>
        """, unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(MENSAGENS["logo_nao_encontrado"])

def get_logo_base64():
    try:
        with open(APP_CONFIG["logo_path"], "rb") as f:
            return base64.b64encode(f.read()).decode()
    except FileNotFoundError:
        return ""

def validar_cnpj(cnpj: str) -> bool:
    if not cnpj:
        return False
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    return bool(re.match(REGEX_PATTERNS["cnpj"], cnpj_limpo))

def validar_cpf(cpf: str) -> bool:
    if not cpf:
        return False
    cpf_limpo = re.sub(r'\D', '', cpf)
    return bool(re.match(REGEX_PATTERNS["cpf"], cpf_limpo))

def validar_cep(cep: str) -> bool:
    if not cep:
        return False
    cep_limpo = re.sub(r'\D', '', cep)
    return bool(re.match(REGEX_PATTERNS["cep"], cep_limpo))

def validar_email(email: str) -> bool:
    if not email:
        return False
    return bool(re.match(REGEX_PATTERNS["email"], email.strip()))

def validar_telefone(telefone: str) -> bool:
    if not telefone:
        return False
    telefone_limpo = re.sub(r'\D', '', telefone)
    return bool(re.match(REGEX_PATTERNS["telefone"], telefone_limpo))

def limpar_string(texto: str) -> str:
    if not texto:
        return ""
    return texto.strip()

def formatar_cnpj(cnpj: str) -> str:
    cnpj_limpo = re.sub(r'\D', '', cnpj)
    if len(cnpj_limpo) == 14:
        return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
    return cnpj

def formatar_cpf(cpf: str) -> str:
    cpf_limpo = re.sub(r'\D', '', cpf)
    if len(cpf_limpo) == 11:
        return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
    return cpf

def formatar_cep(cep: str) -> str:
    cep_limpo = re.sub(r'\D', '', cep)
    if len(cep_limpo) == 8:
        return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
    return cep

def formatar_telefone(telefone: str) -> str:
    telefone_limpo = re.sub(r'\D', '', telefone)
    if len(telefone_limpo) == 11:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
    elif len(telefone_limpo) == 10:
        return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
    return telefone

def formatar_valor_real(valor: float) -> str:
    try:
        return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
    except (ValueError, TypeError):
        return "R$ 0,00"

class SendGridEmailSender:
    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv('SENDGRID_API_KEY')
        if not self.api_key:
            raise ValueError("API Key do SendGrid não encontrada!")
        self.sg = SendGridAPIClient(api_key=self.api_key)
    
    def enviar_email_formulario(self, dados_formulario, email_destino="informe@cpzseg.com.br"):
        try:
            from_email = Email("noreply@cpzseg.com.br", "Grupo CPZ - Formulários")
            to_email = To(email_destino)
            subject = f"Nova Solicitação - Seguro Incêndio - {dados_formulario.get('nome_completo', 'N/A')}"
            html_content = self._gerar_html_email(dados_formulario)
            content = Content("text/html", html_content)
            mail = Mail(from_email, to_email, subject, content)
            response = self.sg.client.mail.send.post(request_body=mail.get())
            
            if response.status_code == 202:
                return True, "Email enviado com sucesso!"
            else:
                return False, f"Erro ao enviar email. Status: {response.status_code}"
        except Exception as e:
            return False, f"Erro ao enviar email: {str(e)}"
    
    def _gerar_html_email(self, dados):
        plano_nome = dados.get('plano_selecionado', '').split('\n')[0].replace(' -', '') if dados.get('plano_selecionado') else 'Não selecionado'
        
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #182c4b;">🛡️ Nova Solicitação - Seguro Incêndio</h2>
                
                <h3>👤 Dados Pessoais</h3>
                <p><strong>Nome:</strong> {dados.get('nome_completo', 'N/A')}</p>
                <p><strong>CPF:</strong> {formatar_cpf(dados.get('cpf', ''))}</p>
                <p><strong>Email:</strong> {dados.get('email', 'N/A')}</p>
                <p><strong>Telefone:</strong> {formatar_telefone(dados.get('telefone', ''))}</p>
                <p><strong>CNPJ:</strong> {formatar_cnpj(dados.get('cnpj', ''))}</p>
                <p><strong>Razão Social:</strong> {dados.get('razao_social', 'N/A')}</p>
                
                <h3>📍 Endereço</h3>
                <p><strong>CEP:</strong> {formatar_cep(dados.get('cep', ''))}</p>
                <p><strong>Endereço:</strong> {dados.get('logradouro', 'N/A')}, {dados.get('numero', 'N/A')}</p>
                <p><strong>Bairro:</strong> {dados.get('bairro', 'N/A')}</p>
                <p><strong>Cidade/Estado:</strong> {dados.get('cidade', 'N/A')} - {dados.get('estado', 'N/A')}</p>
                
                <h3>🛡️ Plano</h3>
                <p><strong>Plano:</strong> {plano_nome}</p>
                <p><strong>Prêmio:</strong> {formatar_valor_real(dados.get('premio_pro_rata', 0))}</p>
                <p><strong>Dias:</strong> {dados.get('dias_restantes', 'N/A')} dias</p>
                
                <p style="margin-top: 20px; color: #666;">
                    Email gerado em {datetime.now(timezone(timedelta(hours=-3))).strftime('%d/%m/%Y às %H:%M')}
                </p>
            </div>
        </body>
        </html>
        """
        return html

def configurar_sendgrid_streamlit():
    api_key_from_secrets = None
    email_mode = "SendGrid"
    
    try:
        if hasattr(st, 'secrets') and 'sendgrid' in st.secrets:
            api_key_from_secrets = st.secrets["sendgrid"].get("api_key", "")
            if api_key_from_secrets and api_key_from_secrets != "SG.sua_api_key_aqui":
                try:
                    sender = SendGridEmailSender(api_key_from_secrets)
                    return sender, True, email_mode
                except Exception as e:
                    st.warning(f"⚠️ Problema na configuração do SendGrid: {str(e)}")
                    return None, False, "Teste (sem envio)"
    except Exception:
        pass
    
    api_key_env = os.getenv('SENDGRID_API_KEY')
    if api_key_env:
        try:
            sender = SendGridEmailSender(api_key_env)
            return sender, True, email_mode
        except Exception:
            pass
    
    st.info("🧪 **Modo de teste ativo** - Configure o SendGrid para envio real")
    return None, False, "Teste (sem envio)"

@lru_cache(maxsize=100)
def buscar_cnpj(cnpj: str) -> Optional[str]:
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
        except Exception as e:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(f"❌ Erro na consulta do CNPJ: {str(e)}")
            continue
    
        return None

@lru_cache(maxsize=100)
def buscar_cep(cep: str) -> Optional[Dict]:
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
        except Exception as e:
            if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                st.error(f"❌ Erro na consulta do CEP: {str(e)}")
            continue
    
    return None

def calcular_pro_rata(plano: str, data_inclusao: datetime) -> Tuple[int, float]:
    data_inclusao_naive = data_inclusao.replace(tzinfo=None)
    dias_restantes = (DATA_FINAL_VIGENCIA - data_inclusao_naive).days + 1
    preco_anual = PLANOS_SEGURO[plano]
    premio_pro_rata = round((preco_anual / 365) * dias_restantes, 2)
    return dias_restantes, premio_pro_rata

def enviar_email_confirmacao(dados: Dict, email_sender=None, email_mode="Teste (sem envio)") -> bool:
    try:
        if email_mode == "Teste (sem envio)":
            st.info("🧪 **Modo de teste ativado** - Email não será enviado")
            st.success("✅ Formulário processado com sucesso!")
            return True
        
        elif email_mode == "SendGrid" and email_sender:
            try:
                email_destino = "informe@cpzseg.com.br"
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
        
        else:
            st.error("❌ Configuração de email inválida")
            return False
            
    except Exception as e:
        st.error(f"❌ Erro inesperado: {str(e)}")
        return False

def validar_formulario(dados: Dict) -> list:
    erros = []
    
    for campo, nome in CAMPOS_OBRIGATORIOS.items():
        valor = dados.get(campo, '').strip()
        if not valor:
            erros.append(f"{nome} é obrigatório")
    
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
    
    nome = dados.get('nome_completo', '').strip()
    if nome and len(nome.split()) < 2:
        erros.append("Nome completo deve ter pelo menos nome e sobrenome")
    
    return erros

def preparar_dados_formulario(session_state: Dict) -> Dict:
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
    current_value = st.session_state.get(field_name, '')
    if current_value:
        return current_value
    
    preserved_value = st.session_state.form_data.get(field_name, '')
    if preserved_value:
        return preserved_value
    
    return ''

def render_header():
    st.markdown("""
    <div class="header-container">
        <div class="header-content">
    """, unsafe_allow_html=True)
    
    try:
        carregar_logo(width=100)
    except Exception:
        st.markdown("**🛡️ Formulário de Adesão**")
    
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
    st.markdown("### 📋 Detalhamento das Coberturas")
    
    st.markdown("""
    <div class="coverage-table-desktop">
        <div style="overflow-x: auto; margin: 1.5rem 0;">
            <table class="coverage-table">
                <thead>
                    <tr>
                        <th>Coberturas</th>
                        <th>Opção 1<br>R$ 250.000</th>
                        <th>Opção 2<br>R$ 400.000</th>
                        <th>Opção 3<br>R$ 700.000</th>
                        <th>Franquia</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td>Incêndio, Raio e Explosão</td>
                        <td>R$ 250.000</td>
                        <td>R$ 400.000</td>
                        <td>R$ 700.000</td>
                        <td class="franchise">R$ 30.000</td>
                    </tr>
                    <tr>
                        <td>Alagamento</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td class="franchise">R$ 15.000</td>
                    </tr>
                    <tr>
                        <td>Danos Elétricos</td>
                        <td>R$ 20.000</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td class="franchise">R$ 3.000</td>
                    </tr>
                    <tr>
                        <td>Pequenas Obras</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td class="franchise">R$ 5.000</td>
                    </tr>
                    <tr>
                        <td>Perda/Pgto Aluguel (6m)</td>
                        <td>R$ 20.000</td>
                        <td>R$ 30.000</td>
                        <td>R$ 40.000</td>
                        <td class="no-franchise">Não Há</td>
                    </tr>
                    <tr>
                        <td>Vidros</td>
                        <td>R$ 20.000</td>
                        <td>R$ 50.000</td>
                        <td>R$ 100.000</td>
                        <td class="franchise">R$ 3.000</td>
                    </tr>
                    <tr>
                        <td>Tumultos</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td>R$ 200.000</td>
                        <td class="franchise">R$ 5.000</td>
                    </tr>
                    <tr>
                        <td>Vendaval</td>
                        <td>R$ 100.000</td>
                        <td>R$ 150.000</td>
                        <td>R$ 200.000</td>
                        <td class="franchise">R$ 10.000</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_responsive_field(label, field_name, field_type="text", help_text="", placeholder="", search_button=False, col_ratio=None):
    if search_button:
        col1, col2 = st.columns([5, 1])
        
        with col1:
            value = st.text_input(
                label,
                value=get_field_value(field_name),
                help=help_text,
                placeholder=placeholder,
                key=field_name
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            button_key = f"buscar_{field_name}"
            button_pressed = st.button("🔍", key=button_key, use_container_width=True)
        
        return value, button_pressed
    else:
        return st.text_input(
            label,
            value=get_field_value(field_name),
            help=help_text,
            placeholder=placeholder,
            key=field_name
        )

def main():
    render_header()
    
    email_sender, email_ready, email_mode = configurar_sendgrid_streamlit()
    
    if 'form_data' not in st.session_state:
        st.session_state.form_data = {}
    
    if st.session_state.get('show_errors', False) and st.session_state.get('form_errors', []):
        st.markdown('<div class="error-message">', unsafe_allow_html=True)
        st.markdown("❌ **Erros encontrados no formulário anterior:**")
        for erro in st.session_state.form_errors:
            st.markdown(f"• {erro}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        st.info("💡 **Seus dados foram preservados!** Corrija os campos destacados abaixo.")
        
        del st.session_state.form_errors
        del st.session_state.show_errors
    
    plano_opcoes_disponiveis = []
    for plano, preco in PLANOS_SEGURO.items():
        plano_opcoes_disponiveis.append(f"{plano} -\n{formatar_valor_real(preco)}/ano")
    
    if 'plano_radio' not in st.session_state and plano_opcoes_disponiveis:
        st.session_state['plano_radio'] = plano_opcoes_disponiveis[0]
    
    st.markdown("")
    st.markdown('<div class="section-title">📍 Identificação do Quiosque</div>', unsafe_allow_html=True)
    
    cnpj, buscar_cnpj_btn = render_responsive_field(
        label="CNPJ *",
        field_name="cnpj",
        help_text="Digite o CNPJ (14 dígitos)",
        placeholder="00.000.000/0000-00",
        search_button=True
    )
    
    razao_social = st.text_input(
        "Razão Social",
        value=get_field_value('razao_social'),
        help="Preenchido automaticamente após buscar CNPJ",
        key="razao_social"
    )
    
    cep, buscar_cep_btn = render_responsive_field(
        label="CEP *",
        field_name="cep",
        help_text="Digite o CEP no formato 00000-000",
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
        numero = st.text_input("Número *", value=get_field_value('numero'), key="numero")
    with col2:
        complemento = st.text_input("Complemento", value=get_field_value('complemento'), key="complemento")
    
    col1, col2 = st.columns(2)
    with col1:
        bairro = st.text_input("Bairro *", value=get_field_value('bairro'), key="bairro")
    with col2:
        cidade = st.text_input("Cidade *", value=get_field_value('cidade'), key="cidade")
    
    estado = st.text_input("Estado *", value=get_field_value('estado'), key="estado")
    
    st.markdown("")
    st.markdown('<div class="section-title">👤 Identificação do Responsável</div>', unsafe_allow_html=True)
    
    cpf = st.text_input("CPF *", value=get_field_value('cpf'), placeholder="000.000.000-00", key="cpf")
    nome_completo = st.text_input("Nome Completo *", value=get_field_value('nome_completo'), key="nome_completo")
    email = st.text_input("E-mail *", value=get_field_value('email'), key="email")
    telefone = st.text_input("Telefone *", value=get_field_value('telefone'), placeholder="(11) 99999-9999", key="telefone")
    
    st.markdown("")
    st.markdown('<div class="section-title">🛡️ Plano de Seguro</div>', unsafe_allow_html=True)
    
    render_coberturas_table()
    
    if buscar_cnpj_btn and cnpj:
        if validar_cnpj(cnpj):
            razao_social_encontrada = buscar_cnpj(cnpj)
            if razao_social_encontrada:
                st.session_state.form_data['razao_social'] = razao_social_encontrada
                st.rerun()
        else:
            st.error("❌ CNPJ deve estar no formato 00.000.000/0000-00")
    
    if buscar_cep_btn and cep:
        if validar_cep(cep):
            endereco = buscar_cep(cep)
            if endereco:
                st.session_state.form_data.update(endereco)
                st.rerun()
        else:
            st.error("❌ CEP deve estar no formato 00000-000")

    st.markdown("")
    st.markdown('<div class="section-title">🛡️ Seleção do Plano</div>', unsafe_allow_html=True)
    
    plano_opcoes = plano_opcoes_disponiveis
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
    
    if plano_selecionado:
        plano_nome = plano_selecionado.split('\n')[0].replace(' -', '')
        preco_anual = PLANOS_SEGURO[plano_nome]
        
        tz_sao_paulo = timezone(timedelta(hours=-3))
        data_inclusao = datetime.now(tz_sao_paulo).replace(hour=0, minute=0, second=0, microsecond=0)
        
        dias_restantes, premio_pro_rata = calcular_pro_rata(plano_nome, data_inclusao)
        
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
        
        st.markdown(f"""
        <div style="
            background: linear-gradient(135deg, #c6f6d5 0%, #9ae6b4 100%);
            border: 2px solid #48bb78;
            border-radius: 8px;
            padding: 1rem;
            text-align: center;
            margin: 1rem 0;
        ">
            <h3 style="color: #22543d; margin: 0 0 0.5rem 0;">
                🎯 Valor Final do Prêmio
            </h3>
            <div style="color: #22543d; font-size: 1.5rem; font-weight: bold;">
                {formatar_valor_real(premio_pro_rata)}
            </div>
            <div style="color: #2f855a; font-size: 0.8rem; margin-top: 0.5rem;">
                Válido de {data_inclusao.strftime('%d/%m/%Y')} até {DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    enviar_formulario = st.button("🚀 Calcular e Enviar", use_container_width=True, type="primary", key="enviar_formulario_final")

    if enviar_formulario:
        dados = preparar_dados_formulario(st.session_state)
        erros = validar_formulario(dados)
        
        if erros:
            st.session_state.form_data.update(dados)
            st.markdown('<div class="error-message">', unsafe_allow_html=True)
            st.markdown("❌ **Por favor, corrija os seguintes campos:**")
            for erro in erros:
                st.markdown(f"• {erro}")
            st.markdown("</div>", unsafe_allow_html=True)
            st.info("💡 **Dica:** Corrija os campos acima e clique em 'Calcular e Enviar' novamente.")
        else:
            st.session_state.form_data = {}
            
            plano_nome = dados['plano_selecionado'].split('\n')[0].replace(' -', '')
            tz_sao_paulo = timezone(timedelta(hours=-3))
            data_inclusao = datetime.now(tz_sao_paulo).replace(hour=0, minute=0, second=0, microsecond=0)
            dias_restantes, premio_pro_rata = calcular_pro_rata(plano_nome, data_inclusao)
            
            dados['timestamp_utc'] = datetime.now(timezone.utc).isoformat()
            dados['data_inclusao'] = data_inclusao.strftime('%Y-%m-%d')
            dados['dias_restantes'] = dias_restantes
            dados['premio_pro_rata'] = premio_pro_rata
            
            try:
                email_sucesso = enviar_email_confirmacao(dados, email_sender, email_mode)
                
                if email_sucesso:
                    st.markdown('<div class="success-message">', unsafe_allow_html=True)
                    mensagem_sucesso = f"✅ **Mensagem transmitida com sucesso!**<br>"
                    mensagem_sucesso += f"📧 **Seus dados foram enviados para nossa equipe.**<br>"
                    mensagem_sucesso += f"💰 **Prêmio calculado:** {formatar_valor_real(premio_pro_rata)}<br>"
                    mensagem_sucesso += f"🕐 **Em breve você receberá retorno.**<br>"
                    
                    if email_mode == "Teste (sem envio)":
                        mensagem_sucesso += "🧪 **Modo de teste ativo!**"
                    else:
                        mensagem_sucesso += "📨 **Nossa equipe entrará em contato em até 24 horas.**"
                    
                    st.markdown(mensagem_sucesso, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("📝 Novo Formulário", key="new_form_button", use_container_width=True):
                            keys_to_clear = ['form_data', 'cpf', 'nome_completo', 'email', 'telefone', 
                                           'cnpj', 'razao_social', 'cep', 'logradouro', 'numero', 'complemento', 
                                           'bairro', 'cidade', 'estado']
                            for key in keys_to_clear:
                                if key in st.session_state:
                                    del st.session_state[key]
                            st.rerun()
                    
                    with col2:
                        if st.button("📋 Ver Resumo", key="show_summary_button", use_container_width=True):
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
                    st.markdown('<div class="error-message">', unsafe_allow_html=True)
                    st.markdown("❌ **Erro ao transmitir mensagem. Tente novamente.**")
                    st.markdown('</div>', unsafe_allow_html=True)
                    
            except Exception as e:
                st.error(f"❌ Erro crítico: {str(e)}")

if __name__ == "__main__":
    main() 