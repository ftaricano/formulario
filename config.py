"""
Configurações do Sistema de Adesão de Seguro
"""
import os
from datetime import datetime

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
    "smtp_server": "smtp.office365.com",
    "smtp_port": 587,
    "email_remetente": os.getenv("EMAIL_REMETENTE", ""),
    "senha_email": os.getenv("EMAIL_SENHA", ""),
    "email_empresa": "informe@cpzseg.com.br",
    "modo_teste": True
}

# ==================== CONFIGURAÇÕES DE API ====================

API_URLS = {
    "receita_ws": "https://www.receitaws.com.br/v1/cnpj/",
    "via_cep": "https://viacep.com.br/ws/"
}

TIMEOUT_CONFIG = {
    "api_timeout": 10,
    "max_retries": 2
}

# ==================== REGEX PATTERNS ====================

REGEX_PATTERNS = {
    "email": r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',
    "cnpj": r'^\d{14}$',
    "cep": r'^\d{8}$',
    "cpf": r'^\d{11}$',
    "telefone": r'^\d{10,11}$'
}

# ==================== CONFIGURAÇÕES DA APLICAÇÃO ====================

APP_CONFIG = {
    "page_title": "Adesão do Seguro Incêndio Orla Rio",
    "page_icon": "🛡️",
    "layout": "centered",
    "logo_path": "logo.png"
}

# ==================== MENSAGENS ====================

MENSAGENS = {
    "logo_nao_encontrado": "⚠️ Logo não encontrado.",
    "cnpj_invalido": "❌ CNPJ inválido",
    "cpf_invalido": "❌ CPF inválido",
    "cep_invalido": "❌ CEP inválido",
    "timeout_cnpj": "⏱️ Timeout na consulta do CNPJ. Tente novamente.",
    "timeout_cep": "⏱️ Timeout na consulta do CEP. Tente novamente.",
    "cep_nao_encontrado": "❌ CEP não encontrado."
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