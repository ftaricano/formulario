import re
from datetime import datetime, timezone, timedelta
import holidays

class DocumentFormatter:
    """Classe para formatação de documentos (CPF, CNPJ, CEP, etc.)"""
    
    @staticmethod
    def formatar_cnpj(cnpj: str) -> str:
        """Formata CNPJ no padrão XX.XXX.XXX/XXXX-XX"""
        cnpj_limpo = re.sub(r'\D', '', cnpj)
        if len(cnpj_limpo) == 14:
            return f"{cnpj_limpo[:2]}.{cnpj_limpo[2:5]}.{cnpj_limpo[5:8]}/{cnpj_limpo[8:12]}-{cnpj_limpo[12:]}"
        return cnpj
    
    @staticmethod
    def formatar_cpf(cpf: str) -> str:
        """Formata CPF no padrão XXX.XXX.XXX-XX"""
        cpf_limpo = re.sub(r'\D', '', cpf)
        if len(cpf_limpo) == 11:
            return f"{cpf_limpo[:3]}.{cpf_limpo[3:6]}.{cpf_limpo[6:9]}-{cpf_limpo[9:]}"
        return cpf
    
    @staticmethod
    def formatar_cep(cep: str) -> str:
        """Formata CEP no padrão XXXXX-XXX"""
        cep_limpo = re.sub(r'\D', '', cep)
        if len(cep_limpo) == 8:
            return f"{cep_limpo[:5]}-{cep_limpo[5:]}"
        return cep
    
    @staticmethod
    def formatar_telefone(telefone: str) -> str:
        """Formata telefone no padrão (XX) XXXXX-XXXX ou (XX) XXXX-XXXX"""
        telefone_limpo = re.sub(r'\D', '', telefone)
        if len(telefone_limpo) == 11:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:7]}-{telefone_limpo[7:]}"
        elif len(telefone_limpo) == 10:
            return f"({telefone_limpo[:2]}) {telefone_limpo[2:6]}-{telefone_limpo[6:]}"
        return telefone

class ValueFormatter:
    """Classe para formatação de valores e moedas"""
    
    @staticmethod
    def formatar_valor_real(valor: float) -> str:
        """Formata valor monetário para Real brasileiro"""
        try:
            return f"R$ {valor:,.2f}".replace(',', 'X').replace('.', ',').replace('X', '.')
        except (ValueError, TypeError):
            return "R$ 0,00"

class StringUtils:
    """Utilitários para manipulação de strings"""
    
    @staticmethod
    def limpar_string(texto: str) -> str:
        """Remove espaços extras e trata valores vazios"""
        if not texto:
            return ""
        return texto.strip()
    
    @staticmethod
    def obter_primeiro_nome(nome_completo: str) -> str:
        """Extrai primeiro nome de um nome completo"""
        if not nome_completo:
            return ""
        nomes = nome_completo.strip().split()
        return nomes[0] if nomes else ""

class DateUtils:
    """Utilitários para manipulação de datas"""
    
    @staticmethod
    def obter_timestamp_brasil() -> str:
        """Retorna timestamp atual no fuso horário do Brasil"""
        tz_brasil = timezone(timedelta(hours=-3))
        return datetime.now(tz_brasil).strftime('%d/%m/%Y às %H:%M')
    
    @staticmethod
    def _eh_feriado(data: datetime) -> bool:
        """Verifica se uma data é feriado usando a biblioteca holidays"""
        try:
            # Criar instância de feriados brasileiros do estado do RJ
            feriados_br = holidays.country_holidays('BR', subdiv='RJ', years=data.year)
            
            # Adicionar feriados municipais específicos do Rio de Janeiro
            # que podem não estar incluídos automaticamente
            feriados_municipais_rj = [
                (1, 20),   # São Sebastião (Padroeiro do Rio de Janeiro)
                (3, 1),    # Aniversário da Cidade do Rio de Janeiro
            ]
            
            # Verificar feriados da biblioteca
            if data.date() in feriados_br:
                return True
                
            # Verificar feriados municipais adicionais
            for mes, dia in feriados_municipais_rj:
                if data.month == mes and data.day == dia:
                    return True
                    
            return False
            
        except Exception:
            # Se houver erro, usar lógica de fallback apenas para feriados nacionais básicos
            return DateUtils._eh_feriado_fallback(data)
    
    @staticmethod
    def _eh_feriado_fallback(data: datetime) -> bool:
        """Fallback para verificação de feriados em caso de erro"""
        # Feriados fixos básicos (nacional)
        feriados_basicos = [
            (1, 1),    # Ano Novo
            (4, 21),   # Tiradentes
            (5, 1),    # Dia do Trabalhador
            (9, 7),    # Independência
            (10, 12),  # Nossa Senhora Aparecida
            (11, 2),   # Finados
            (11, 15),  # Proclamação da República
            (12, 25),  # Natal
        ]
        
        return (data.month, data.day) in feriados_basicos
    
    @staticmethod
    def obter_proximo_dia_util() -> datetime:
        """Retorna o próximo dia útil (considerando fins de semana e feriados)"""
        tz_sao_paulo = timezone(timedelta(hours=-3))
        hoje = datetime.now(tz_sao_paulo).replace(hour=0, minute=0, second=0, microsecond=0)
        
        data_candidata = hoje + timedelta(days=1)
        
        # Pular fins de semana e feriados
        max_tentativas = 30  # Proteção contra loop infinito
        tentativas = 0
        
        while tentativas < max_tentativas:
            # Verificar se é fim de semana (5=sábado, 6=domingo)
            if data_candidata.weekday() >= 5:
                data_candidata += timedelta(days=1)
                tentativas += 1
                continue
            
            # Verificar se é feriado
            if DateUtils._eh_feriado(data_candidata):
                data_candidata += timedelta(days=1)
                tentativas += 1
                continue
            
            # É um dia útil válido
            break
        
        return data_candidata
    
    @staticmethod
    def obter_proximo_dia_util_simples() -> datetime:
        """Alias para compatibilidade - retorna o próximo dia útil"""
        return DateUtils.obter_proximo_dia_util()
    
    @staticmethod
    def listar_feriados_ano(ano: int) -> dict:
        """Lista todos os feriados de um ano específico"""
        try:
            # Obter feriados brasileiros do RJ para o ano
            feriados_br = holidays.country_holidays('BR', subdiv='RJ', years=ano)
            
            # Converter para dicionário com nomes
            feriados_dict = {data: nome for data, nome in feriados_br.items()}
            
            # Adicionar feriados municipais específicos do Rio de Janeiro
            feriados_municipais_rj = {
                (1, 20): 'São Sebastião',
                (3, 1): 'Aniversário da Cidade do Rio de Janeiro',
            }
            
            # Adicionar feriados municipais se não estiverem já incluídos
            for (mes, dia), nome in feriados_municipais_rj.items():
                try:
                    data_feriado = datetime(ano, mes, dia).date()
                    if data_feriado not in feriados_dict:
                        feriados_dict[data_feriado] = nome
                except ValueError:
                    continue  # Ignora datas inválidas
            
            return feriados_dict
            
        except Exception:
            return {} 