from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from src.models.formulario import FormularioSeguro
from src.validators.form_validators import FormValidator, FileValidator
from src.managers.state_manager import FormularioStateManager, ErrorStateManager
from src.services.api_service import ApiService
from src.utils.formatters import ValueFormatter, StringUtils
from config import PLANOS_SEGURO, DATA_FINAL_VIGENCIA

class FormularioController:
    """Controlador principal do formulário - gerencia toda a lógica de negócio"""
    
    def __init__(self):
        self.state_manager = FormularioStateManager()
        self.error_manager = ErrorStateManager()
    
    def inicializar_aplicacao(self) -> bool:
        """Inicializa aplicação e processa erros pendentes"""
        # Processar erros pendentes primeiro
        tinha_erros = self.error_manager.processar_erros_pendentes()
        return tinha_erros
    
    def buscar_dados_cnpj(self, cnpj: str) -> Tuple[bool, Optional[str]]:
        """Realiza busca de dados por CNPJ"""
        if not cnpj.strip():
            return False, "CNPJ não informado"
        
        if not FormValidator.validar_cnpj(cnpj):
            return False, "CNPJ deve estar no formato 00.000.000/0000-00"
        
        razao_social = ApiService.buscar_cnpj(cnpj)
        if razao_social:
            # Salvar no state manager
            self.state_manager.session_manager.definir_valor('razao_social', razao_social)
            return True, razao_social
        
        return False, "CNPJ não encontrado na base de dados"
    
    def buscar_dados_cep(self, cep: str) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Realiza busca de dados por CEP"""
        if not cep.strip():
            return False, None, "CEP não informado"
        
        if not FormValidator.validar_cep(cep):
            return False, None, "CEP deve estar no formato 00000-000"
        
        endereco = ApiService.buscar_cep(cep)
        if endereco:
            # Salvar endereço no state manager
            for campo, valor in endereco.items():
                self.state_manager.session_manager.definir_valor(campo, valor)
            return True, endereco, None
        
        return False, None, "CEP não encontrado"
    
    def calcular_premio_pro_rata(self, plano_nome: str) -> Tuple[int, float]:
        """Calcula prêmio pro rata para o plano selecionado"""
        if plano_nome not in PLANOS_SEGURO:
            return 0, 0.0
        
        preco_anual = PLANOS_SEGURO[plano_nome]
        data_inclusao = datetime.now() + timedelta(days=1)
        dias_restantes = (DATA_FINAL_VIGENCIA - data_inclusao.replace(tzinfo=None)).days + 1
        premio_pro_rata = round((preco_anual / 365) * dias_restantes, 2)
        
        return dias_restantes, premio_pro_rata
    
    def obter_plano_formatado(self, plano_selecionado: str) -> str:
        """Extrai nome do plano da string formatada"""
        if not plano_selecionado:
            return ""
        return plano_selecionado.split('\n')[0].replace(' -', '')
    
    def validar_e_processar_formulario(self, arquivos_uploaded=None) -> Tuple[bool, List[str], Optional[FormularioSeguro]]:
        """Valida formulário completo e retorna resultado"""
        # Criar modelo do formulário
        formulario = self.state_manager.criar_formulario_atual()
        dados = formulario.to_dict()
        
        # Validar dados do formulário
        erros = FormValidator.validar_formulario_completo(dados)
        
        # Validar arquivos se existirem
        arquivos_validos = []
        if arquivos_uploaded:
            arquivos_ok, erros_arquivos, arquivos_validos = FileValidator.validar_arquivos(arquivos_uploaded)
            if not arquivos_ok:
                erros.extend(erros_arquivos)
        
        # Se há erros, salvar estado e definir erros
        if erros:
            self.error_manager.definir_erros(erros)
            return False, erros, None
        
        # Sucesso - adicionar dados calculados
        plano_nome = self.obter_plano_formatado(dados.get('plano_selecionado', ''))
        if plano_nome:
            dias_restantes, premio_pro_rata = self.calcular_premio_pro_rata(plano_nome)
            
            # Atualizar dados do formulário
            formulario.dias_restantes = dias_restantes
            formulario.premio_pro_rata = premio_pro_rata
            formulario.timestamp_utc = datetime.now().isoformat()
            formulario.data_inclusao = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return True, [], formulario
    
    def processar_envio_formulario(self, arquivos_uploaded=None) -> Tuple[bool, Optional[FormularioSeguro], List[str]]:
        """Processa envio completo do formulário"""
        # Verificar se já foi enviado
        if self.state_manager.formulario_foi_enviado():
            return False, None, ["Formulário já foi enviado anteriormente"]
        
        # Validar e processar
        sucesso, erros, formulario = self.validar_e_processar_formulario(arquivos_uploaded)
        
        if sucesso and formulario:
            # Marcar como enviado
            self.state_manager.marcar_como_enviado()
            return True, formulario, []
        
        return False, None, erros
    
    def resetar_formulario_completo(self):
        """Reseta formulário completo para novo preenchimento"""
        self.state_manager.resetar_formulario()
        self.error_manager.limpar_erros()
    
    def obter_dados_para_exibicao(self) -> Dict:
        """Obtém dados atuais formatados para exibição"""
        formulario = self.state_manager.criar_formulario_atual()
        dados = formulario.to_dict()
        
        # Aplicar formatações para exibição
        dados_formatados = {
            'nome_primeiro': StringUtils.obter_primeiro_nome(dados.get('nome_completo', '')),
            'equipamentos_validos': self.state_manager.obter_equipamentos_validos(),
            'formulario_enviado': self.state_manager.formulario_foi_enviado()
        }
        
        return {**dados, **dados_formatados}

class EquipamentosController:
    """Controlador específico para gerenciamento de equipamentos"""
    
    def __init__(self, state_manager: FormularioStateManager):
        self.state_manager = state_manager
    
    def adicionar_equipamento(self) -> bool:
        """Adiciona novo equipamento e retorna sucesso"""
        try:
            self.state_manager.adicionar_equipamento()
            return True
        except Exception:
            return False
    
    def remover_equipamento(self, index: int) -> bool:
        """Remove equipamento por índice"""
        return self.state_manager.remover_equipamento(index)
    
    def obter_equipamentos_atuais(self) -> List[Dict]:
        """Obtém lista atual de equipamentos do session_state"""
        import streamlit as st
        return st.session_state.get('equipamentos', [])
    
    def obter_resumo_equipamentos(self) -> List[Dict]:
        """Obtém resumo dos equipamentos preenchidos"""
        equipamentos = self.obter_equipamentos_atuais()
        return [eq for eq in equipamentos if eq.get('tipo', '').strip()]
    
    def validar_equipamentos(self) -> Tuple[bool, List[str]]:
        """Valida se há pelo menos um equipamento válido"""
        equipamentos_validos = self.state_manager.obter_equipamentos_validos()
        
        if not equipamentos_validos:
            return False, ["Pelo menos um equipamento deve ser cadastrado com o tipo preenchido"]
        
        return True, []

class PlanoController:
    """Controlador para gerenciamento de planos"""
    
    @staticmethod
    def obter_opcoes_formatadas() -> List[str]:
        """Retorna opções de planos formatadas para seleção"""
        opcoes = []
        for plano, preco in PLANOS_SEGURO.items():
            opcoes.append(f"{plano} -\n{ValueFormatter.formatar_valor_real(preco)}/ano")
        return opcoes
    
    @staticmethod
    def extrair_nome_plano(plano_selecionado: str) -> str:
        """Extrai nome limpo do plano da opção selecionada"""
        if not plano_selecionado:
            return ""
        return plano_selecionado.split('\n')[0].replace(' -', '')
    
    @staticmethod
    def obter_preco_plano(plano_nome: str) -> float:
        """Obtém preço anual do plano"""
        return PLANOS_SEGURO.get(plano_nome, 0.0) 