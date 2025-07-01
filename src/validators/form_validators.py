import re
from typing import List, Dict
from config import REGEX_PATTERNS, CAMPOS_OBRIGATORIOS

class FormValidator:
    """Classe responsável por todas as validações do formulário"""
    
    @staticmethod
    def validar_cnpj(cnpj: str) -> bool:
        """Valida formato do CNPJ"""
        if not cnpj:
            return False
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        return bool(re.match(REGEX_PATTERNS["cnpj"], cnpj_limpo))
    
    @staticmethod
    def validar_cpf(cpf: str) -> bool:
        """Valida formato do CPF"""
        if not cpf:
            return False
        cpf_limpo = re.sub(r'\D', '', cpf)
        return bool(re.match(REGEX_PATTERNS["cpf"], cpf_limpo))
    
    @staticmethod
    def validar_cep(cep: str) -> bool:
        """Valida formato do CEP"""
        if not cep:
            return False
        cep_limpo = re.sub(r'\D', '', cep)
        return bool(re.match(REGEX_PATTERNS["cep"], cep_limpo))
    
    @staticmethod
    def validar_email(email: str) -> bool:
        """Valida formato do email"""
        if not email:
            return False
        return bool(re.match(REGEX_PATTERNS["email"], email.strip()))
    
    @staticmethod
    def validar_telefone(telefone: str) -> bool:
        """Valida formato do telefone"""
        if not telefone:
            return False
        telefone_limpo = re.sub(r'\D', '', telefone)
        return bool(re.match(REGEX_PATTERNS["telefone"], telefone_limpo))
    
    @staticmethod
    def validar_nome_completo(nome: str) -> bool:
        """Valida se o nome tem pelo menos nome e sobrenome"""
        if not nome:
            return False
        return len(nome.strip().split()) >= 2
    
    @classmethod
    def validar_formulario_completo(cls, dados: Dict) -> List[str]:
        """Valida o formulário completo e retorna lista de erros"""
        erros = []
        
        # Validar campos obrigatórios
        for campo, nome in CAMPOS_OBRIGATORIOS.items():
            valor = dados.get(campo, '').strip()
            if not valor:
                erros.append(f"{nome} é obrigatório")
        
        # Validações específicas
        email = dados.get('email', '').strip()
        if email and not cls.validar_email(email):
            erros.append("E-mail inválido")
        
        telefone = dados.get('telefone', '').strip()
        if telefone and not cls.validar_telefone(telefone):
            erros.append("Telefone deve ter 10 ou 11 dígitos")
        
        cpf = dados.get('cpf', '').strip()
        if cpf and not cls.validar_cpf(cpf):
            erros.append("CPF deve conter exatamente 11 números")
        
        cnpj = dados.get('cnpj', '').strip()
        if cnpj and not cls.validar_cnpj(cnpj):
            erros.append("CNPJ deve conter exatamente 14 números")
        
        cep = dados.get('cep', '').strip()
        if cep and not cls.validar_cep(cep):
            erros.append("CEP deve conter exatamente 8 números")
        
        nome = dados.get('nome_completo', '').strip()
        if nome and not cls.validar_nome_completo(nome):
            erros.append("Nome completo deve ter pelo menos nome e sobrenome")
        
        # Validação de equipamentos - OPCIONAL: apenas validar se preenchidos incorretamente
        equipamentos = dados.get('equipamentos', [])
        for i, eq in enumerate(equipamentos):
            # Se algum campo foi preenchido, verificar se pelo menos o tipo está preenchido
            tipo = eq.get('tipo', '').strip()
            descricao = eq.get('descricao', '').strip()
            valor = eq.get('valor', '').strip()
            
            # Se algum campo foi preenchido mas não o tipo, exigir o tipo
            if (descricao or valor) and not tipo:
                erros.append(f"Equipamento {i+1}: se preenchido, o tipo é obrigatório")
        
        return erros

class FileValidator:
    """Classe para validação de arquivos"""
    
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB por arquivo
    MAX_TOTAL_SIZE = 25 * 1024 * 1024  # 25MB total
    TIPOS_PERMITIDOS = [
        'image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp',
        'application/pdf', 
        'application/msword', 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'text/plain'
    ]
    
    @classmethod
    def validar_arquivos(cls, arquivos_uploaded) -> tuple[bool, List[str], List[Dict]]:
        """Valida arquivos uploaded e retorna status, erros e arquivos processados"""
        if not arquivos_uploaded:
            return True, [], []
        
        erros = []
        arquivos_validos = []
        total_size = 0
        
        for arquivo in arquivos_uploaded:
            # Verificar tamanho individual
            if arquivo.size > cls.MAX_FILE_SIZE:
                erros.append(f"Arquivo '{arquivo.name}' excede 10MB")
                continue
                
            # Verificar tipo
            if arquivo.type not in cls.TIPOS_PERMITIDOS:
                erros.append(f"Tipo de arquivo não permitido: '{arquivo.name}' ({arquivo.type})")
                continue
                
            total_size += arquivo.size
            
            # Processar arquivo válido
            arquivo_dict = {
                'name': arquivo.name,
                'type': arquivo.type,
                'size': arquivo.size,
                'content': arquivo.read()
            }
            arquivos_validos.append(arquivo_dict)
        
        # Verificar tamanho total
        if total_size > cls.MAX_TOTAL_SIZE:
            erros.append(f"Tamanho total dos arquivos excede 25MB ({total_size/(1024*1024):.1f}MB)")
            return False, erros, []
        
        return len(erros) == 0, erros, arquivos_validos 