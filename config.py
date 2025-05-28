"""
Configurações do Sistema de Adesão de Seguro
"""
import os
from datetime import datetime

# Carregar variáveis de ambiente do arquivo .env (se existir)
try:
    from dotenv import load_dotenv
    load_dotenv()  # Carrega automaticamente o arquivo .env
except ImportError:
    pass  # python-dotenv não instalado, usar apenas variáveis de ambiente do sistema

# Tentar importar streamlit para usar secrets
try:
    import streamlit as st
    USE_STREAMLIT_SECRETS = True
except ImportError:
    USE_STREAMLIT_SECRETS = False

def get_config_value(key: str, default: str = "") -> str:
    """
    Busca configuração primeiro no st.secrets (Streamlit Cloud) 
    depois nas variáveis de ambiente
    """
    if USE_STREAMLIT_SECRETS:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            return os.getenv(key, default)
    return os.getenv(key, default)

# ==================== CONFIGURAÇÕES DOS PLANOS ====================

PLANOS_SEGURO = {
    "Opção 1": 2505.53,
    "Opção 2": 4008.85,
    "Opção 3": 7015.49  
}

# Data final de vigência fixa
DATA_FINAL_VIGENCIA = datetime(2025, 12, 8)

# ==================== CONFIGURAÇÕES DE EMAIL ====================

EMAIL_CONFIG = {
    "smtp_server": get_config_value("SMTP_SERVER", "smtp.office365.com"),
    "smtp_port": int(get_config_value("SMTP_PORT", "587")),
    "email_remetente": get_config_value("EMAIL_REMETENTE", ""),
    "senha_email": get_config_value("EMAIL_SENHA", ""),
    "email_empresa": get_config_value("EMAIL_EMPRESA", ""),
    "modo_teste": get_config_value("MODO_TESTE", "true").lower() == "true"
}

# ==================== CONFIGURAÇÕES DE API ====================

API_URLS = {
    "receita_ws": "https://www.receitaws.com.br/v1/cnpj/",
    "via_cep": "https://viacep.com.br/ws/",
    "cpf_ws": "https://api.cpfcnpj.com.br/"  # API para consulta de CPF
}

TIMEOUT_CONFIG = {
    "api_timeout": int(get_config_value("API_TIMEOUT", "5")),
    "max_retries": int(get_config_value("MAX_RETRIES", "3"))
}

# ==================== REGEX PATTERNS ====================

REGEX_PATTERNS = {
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "cnpj": r'^\d{14}$',
    "cep": r'^\d{8}$',
    "cpf": r'^\d{11}$',  # CPF deve ter 11 dígitos
    "telefone": r'^\d{10,11}$'  # Telefone deve ter 10 ou 11 dígitos
}

# ==================== CONFIGURAÇÕES DA APLICAÇÃO ====================

APP_CONFIG = {
    "page_title": "Adesão do Seguro Incêndio Orla Rio",
    "page_icon": "🛡️",
    "layout": "centered",
    "logo_path": "logo.png",
    "logo_width": 200
}

# ==================== MENSAGENS ====================

MENSAGENS = {
    "logo_nao_encontrado": "⚠️ Logo não encontrado. Coloque o arquivo 'logo.png' na raiz do projeto.",
    "cnpj_invalido": "❌ CNPJ inválido",
    "cpf_invalido": "❌ CPF inválido",
    "cep_invalido": "❌ CEP inválido",
    "telefone_invalido": "❌ Telefone inválido",
    "timeout_cnpj": "⏱️ Timeout na consulta do CNPJ. Tente novamente.",
    "timeout_cpf": "⏱️ Timeout na consulta do CPF. Tente novamente.",
    "timeout_cep": "⏱️ Timeout na consulta do CEP. Tente novamente.",
    "cep_nao_encontrado": "❌ CEP não encontrado.",
    "cpf_nao_encontrado": "❌ CPF não encontrado ou inválido.",
    "email_config_erro": "⚠️ Configurações de email não encontradas. Email não será enviado.",
    "sucesso_email": "📧 Emails de confirmação enviados com sucesso!",
    "erro_formulario": "❌ **Erro ao processar formulário. Verifique as configurações e tente novamente.**"
}

# ==================== VALIDAÇÕES ====================

CAMPOS_OBRIGATORIOS = {
    'nome_completo': 'Nome completo',
    'cpf': 'CPF',
    'email': 'E-mail',
    'telefone': 'Telefone',
    'cnpj': 'CNPJ',
    'cep': 'CEP',
    'logradouro': 'Logradouro',
    'numero': 'Número',
    'bairro': 'Bairro',
    'cidade': 'Cidade',
    'estado': 'Estado',
    'plano_selecionado': 'Plano de seguro'
} 