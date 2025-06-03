from dataclasses import dataclass, field
from typing import List, Optional, Dict
from datetime import datetime

@dataclass
class Equipamento:
    """Modelo para equipamentos sem nota fiscal"""
    tipo: str = ""
    descricao: str = ""
    valor: str = ""
    
    def is_valid(self) -> bool:
        """Verifica se pelo menos o tipo foi preenchido"""
        return bool(self.tipo.strip())
    
    def to_dict(self) -> Dict:
        """Converte para dicionário"""
        return {
            'tipo': self.tipo,
            'descricao': self.descricao,
            'valor': self.valor
        }

@dataclass
class Endereco:
    """Modelo para endereço"""
    cep: str = ""
    logradouro: str = ""
    numero: str = ""
    complemento: str = ""
    bairro: str = ""
    cidade: str = ""
    estado: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'cep': self.cep,
            'logradouro': self.logradouro,
            'numero': self.numero,
            'complemento': self.complemento,
            'bairro': self.bairro,
            'cidade': self.cidade,
            'estado': self.estado
        }

@dataclass
class DadosPessoais:
    """Modelo para dados pessoais do responsável"""
    nome_completo: str = ""
    cpf: str = ""
    email: str = ""
    telefone: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'nome_completo': self.nome_completo,
            'cpf': self.cpf,
            'email': self.email,
            'telefone': self.telefone
        }

@dataclass
class DadosEmpresa:
    """Modelo para dados da empresa"""
    cnpj: str = ""
    razao_social: str = ""
    
    def to_dict(self) -> Dict:
        return {
            'cnpj': self.cnpj,
            'razao_social': self.razao_social
        }

@dataclass
class FormularioSeguro:
    """Modelo principal do formulário de seguro"""
    dados_pessoais: DadosPessoais = field(default_factory=DadosPessoais)
    dados_empresa: DadosEmpresa = field(default_factory=DadosEmpresa)
    endereco: Endereco = field(default_factory=Endereco)
    equipamentos: List[Equipamento] = field(default_factory=list)
    plano_selecionado: str = ""
    timestamp_utc: Optional[str] = None
    data_inclusao: Optional[str] = None
    dias_restantes: Optional[int] = None
    premio_pro_rata: Optional[float] = None
    
    def __post_init__(self):
        """Inicializa com pelo menos um equipamento vazio"""
        if not self.equipamentos:
            self.equipamentos = [Equipamento()]
    
    def adicionar_equipamento(self):
        """Adiciona novo equipamento vazio"""
        self.equipamentos.append(Equipamento())
    
    def remover_equipamento(self, index: int):
        """Remove equipamento por índice (mantém pelo menos 1)"""
        if len(self.equipamentos) > 1 and 0 <= index < len(self.equipamentos):
            self.equipamentos.pop(index)
    
    def get_equipamentos_validos(self) -> List[Equipamento]:
        """Retorna apenas equipamentos com tipo preenchido"""
        return [eq for eq in self.equipamentos if eq.is_valid()]
    
    def to_dict(self) -> Dict:
        """Converte formulário completo para dicionário"""
        return {
            **self.dados_pessoais.to_dict(),
            **self.dados_empresa.to_dict(),
            **self.endereco.to_dict(),
            'equipamentos': [eq.to_dict() for eq in self.equipamentos],
            'plano_selecionado': self.plano_selecionado,
            'timestamp_utc': self.timestamp_utc,
            'data_inclusao': self.data_inclusao,
            'dias_restantes': self.dias_restantes,
            'premio_pro_rata': self.premio_pro_rata
        }
    
    @classmethod
    def from_session_state(cls, session_state: Dict) -> 'FormularioSeguro':
        """Cria instância a partir do session_state do Streamlit"""
        formulario = cls()
        
        # Dados pessoais
        formulario.dados_pessoais.nome_completo = session_state.get('nome_completo', '')
        formulario.dados_pessoais.cpf = session_state.get('cpf', '')
        formulario.dados_pessoais.email = session_state.get('email', '')
        formulario.dados_pessoais.telefone = session_state.get('telefone', '')
        
        # Dados empresa
        formulario.dados_empresa.cnpj = session_state.get('cnpj', '')
        formulario.dados_empresa.razao_social = session_state.get('razao_social', '')
        
        # Endereço
        formulario.endereco.cep = session_state.get('cep', '')
        formulario.endereco.logradouro = session_state.get('logradouro', '')
        formulario.endereco.numero = session_state.get('numero', '')
        formulario.endereco.complemento = session_state.get('complemento', '')
        formulario.endereco.bairro = session_state.get('bairro', '')
        formulario.endereco.cidade = session_state.get('cidade', '')
        formulario.endereco.estado = session_state.get('estado', '')
        
        # Equipamentos
        equipamentos_data = session_state.get('equipamentos', [])
        if equipamentos_data:
            formulario.equipamentos = [
                Equipamento(
                    tipo=eq.get('tipo', ''),
                    descricao=eq.get('descricao', ''),
                    valor=eq.get('valor', '')
                ) for eq in equipamentos_data
            ]
        
        # Plano
        formulario.plano_selecionado = session_state.get('plano_radio', '')
        
        return formulario 