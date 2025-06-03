import requests
import re
from functools import lru_cache
from typing import Optional, Dict
from config import API_URLS, TIMEOUT_CONFIG, MENSAGENS
import streamlit as st

class ApiService:
    """Serviço para integração com APIs externas"""
    
    @staticmethod
    @lru_cache(maxsize=100)
    def buscar_cnpj(cnpj: str) -> Optional[str]:
        """Busca razão social por CNPJ na Receita Federal"""
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        
        if len(cnpj_limpo) != 14:
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
                    st.error(f"✗ Erro na consulta CNPJ: {data.get('message', 'CNPJ inválido')}")
                    return None
                    
            except requests.exceptions.Timeout:
                if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                    st.error(MENSAGENS["timeout_cnpj"])
                continue
                
            except Exception as e:
                if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                    st.error(f"✗ Erro na consulta do CNPJ: {str(e)}")
                continue
        
        return None
    
    @staticmethod
    @lru_cache(maxsize=100)
    def buscar_cep(cep: str) -> Optional[Dict]:
        """Busca endereço por CEP no ViaCEP"""
        cep_limpo = re.sub(r'\D', '', cep)
        
        if len(cep_limpo) != 8:
            st.error(MENSAGENS["cep_invalido"])
            return None
        
        url = f"{API_URLS['via_cep']}{cep_limpo}/json/"
        
        for tentativa in range(TIMEOUT_CONFIG["max_retries"]):
            try:
                response = requests.get(url, timeout=TIMEOUT_CONFIG["api_timeout"])
                response.raise_for_status()
                data = response.json()
                
                if 'erro' not in data:
                    resultado = {
                        'logradouro': data.get('logradouro', ''),
                        'bairro': data.get('bairro', ''),
                        'cidade': data.get('localidade', ''),
                        'estado': data.get('uf', '')
                    }
                    return resultado
                else:
                    st.error(MENSAGENS["cep_nao_encontrado"])
                    return None
                    
            except requests.exceptions.Timeout:
                if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                    st.error(MENSAGENS["timeout_cep"])
                continue
                
            except Exception as e:
                if tentativa == TIMEOUT_CONFIG["max_retries"] - 1:
                    st.error(f"✗ Erro na consulta do CEP: {str(e)}")
                continue
        
        return None 