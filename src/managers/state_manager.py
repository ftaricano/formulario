import streamlit as st
from typing import Dict, Any, Optional, List
from src.models.formulario import FormularioSeguro, Equipamento
from dataclasses import asdict

class SessionStateManager:
    """Gerenciador centralizado do estado da sessão"""
    
    # Chaves conhecidas do session_state
    FORM_KEYS = [
        'nome_completo', 'cpf', 'email', 'telefone',
        'cnpj', 'razao_social', 'cep', 'logradouro', 
        'numero', 'complemento', 'bairro', 'cidade', 'estado',
        'plano_radio', 'equipamentos', 'formulario_enviado'
    ]
    
    @staticmethod
    def inicializar_estado():
        """Inicializa estado padrão se necessário"""
        # Garantir que equipamentos sempre existe
        if 'equipamentos' not in st.session_state:
            st.session_state.equipamentos = [{"tipo": "", "descricao": "", "valor": ""}]
        
        # Garantir que formulário não foi enviado
        if 'formulario_enviado' not in st.session_state:
            st.session_state.formulario_enviado = False
            
        # Inicializar cache de dados preservados
        if 'form_data_cache' not in st.session_state:
            st.session_state.form_data_cache = {}
    
    @staticmethod
    def salvar_estado_atual() -> Dict[str, Any]:
        """Salva estado atual em cache para preservação"""
        estado_salvo = {}
        for key in SessionStateManager.FORM_KEYS:
            if key in st.session_state:
                estado_salvo[key] = st.session_state[key]
        
        st.session_state.form_data_cache = estado_salvo
        return estado_salvo
    
    @staticmethod
    def restaurar_estado_salvo():
        """Restaura estado salvo do cache"""
        if 'form_data_cache' in st.session_state:
            for key, value in st.session_state.form_data_cache.items():
                st.session_state[key] = value
    
    @staticmethod
    def limpar_estado_formulario():
        """Limpa apenas dados do formulário, mantendo estado da aplicação"""
        for key in SessionStateManager.FORM_KEYS:
            if key in st.session_state:
                del st.session_state[key]
        
        # Recriar equipamentos vazios
        st.session_state.equipamentos = [{"tipo": "", "descricao": "", "valor": ""}]
        st.session_state.formulario_enviado = False
        
        # Limpar cache
        if 'form_data_cache' in st.session_state:
            del st.session_state.form_data_cache
    
    @staticmethod
    def obter_valor(key: str, default: Any = "") -> Any:
        """Obtém valor do session_state com fallback"""
        # Primeiro, tentar session_state atual
        if key in st.session_state:
            return st.session_state[key]
        
        # Depois, tentar cache preservado
        if 'form_data_cache' in st.session_state:
            if key in st.session_state.form_data_cache:
                return st.session_state.form_data_cache[key]
        
        return default
    
    @staticmethod
    def definir_valor(key: str, value: Any):
        """Define valor no session_state"""
        st.session_state[key] = value
    
    @staticmethod
    def tem_erros_pendentes() -> bool:
        """Verifica se há erros de validação pendentes"""
        return st.session_state.get('show_errors', False)
    
    @staticmethod
    def definir_erros(erros: List[str]):
        """Define erros de validação para exibição"""
        st.session_state.form_errors = erros
        st.session_state.show_errors = True
        # Salvar estado atual antes de mostrar erros
        SessionStateManager.salvar_estado_atual()
    
    @staticmethod
    def limpar_erros():
        """Limpa erros de validação"""
        if 'form_errors' in st.session_state:
            del st.session_state.form_errors
        if 'show_errors' in st.session_state:
            del st.session_state.show_errors

class FormularioStateManager:
    """Gerenciador específico para estado do formulário"""
    
    def __init__(self):
        self.session_manager = SessionStateManager()
        self.session_manager.inicializar_estado()
    
    def criar_formulario_atual(self) -> FormularioSeguro:
        """Cria instância do formulário com dados atuais"""
        return FormularioSeguro.from_session_state(st.session_state)
    
    def salvar_formulario(self, formulario: FormularioSeguro):
        """Salva dados do formulário no session_state"""
        dados = formulario.to_dict()
        
        # Salvar dados estruturados
        for key, value in dados.items():
            if key in SessionStateManager.FORM_KEYS:
                st.session_state[key] = value
    
    def adicionar_equipamento(self):
        """Adiciona novo equipamento vazio"""
        if 'equipamentos' not in st.session_state:
            st.session_state.equipamentos = []
        
        st.session_state.equipamentos.append({"tipo": "", "descricao": "", "valor": ""})
    
    def remover_equipamento(self, index: int) -> bool:
        """Remove equipamento por índice. Retorna True se removido."""
        if 'equipamentos' not in st.session_state:
            return False
            
        if len(st.session_state.equipamentos) > 1 and 0 <= index < len(st.session_state.equipamentos):
            st.session_state.equipamentos.pop(index)
            return True
        
        return False
    
    def obter_equipamentos_validos(self) -> List[Equipamento]:
        """Retorna lista de equipamentos válidos"""
        equipamentos_data = st.session_state.get('equipamentos', [])
        equipamentos_validos = []
        
        for eq_data in equipamentos_data:
            if eq_data.get('tipo', '').strip():  # Só incluir se tipo foi preenchido
                equipamento = Equipamento(
                    tipo=eq_data.get('tipo', ''),
                    descricao=eq_data.get('descricao', ''),
                    valor=eq_data.get('valor', '')
                )
                equipamentos_validos.append(equipamento)
        
        return equipamentos_validos
    
    def formulario_foi_enviado(self) -> bool:
        """Verifica se formulário já foi enviado"""
        return st.session_state.get('formulario_enviado', False)
    
    def marcar_como_enviado(self):
        """Marca formulário como enviado"""
        st.session_state.formulario_enviado = True
    
    def resetar_formulario(self):
        """Reseta completamente o formulário"""
        SessionStateManager.limpar_estado_formulario()
        SessionStateManager.inicializar_estado()

class ErrorStateManager:
    """Gerenciador específico para erros de validação"""
    
    @staticmethod
    def tem_erros() -> bool:
        """Verifica se há erros para exibir"""
        return st.session_state.get('show_errors', False)
    
    @staticmethod
    def obter_erros() -> List[str]:
        """Obtém lista de erros atuais"""
        return st.session_state.get('form_errors', [])
    
    @staticmethod
    def definir_erros(erros: List[str]):
        """Define novos erros e preserva dados"""
        SessionStateManager.definir_erros(erros)
    
    @staticmethod
    def limpar_erros():
        """Limpa erros e cache"""
        SessionStateManager.limpar_erros()
    
    @staticmethod
    def processar_erros_pendentes() -> bool:
        """Processa e exibe erros pendentes. Retorna True se havia erros."""
        if ErrorStateManager.tem_erros():
            erros = ErrorStateManager.obter_erros()
            
            # Exibir erros
            st.error("**❌ Erros encontrados no formulário anterior:**")
            for erro in erros:
                st.markdown(f"• {erro}")
            
            st.info("▪ **Seus dados foram preservados!** Corrija os campos destacados abaixo.")
            
            # Restaurar dados preservados
            SessionStateManager.restaurar_estado_salvo()
            
            # Limpar erros após exibir
            ErrorStateManager.limpar_erros()
            
            return True
        
        return False