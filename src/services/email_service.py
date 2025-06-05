import os
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from jinja2 import Template
import streamlit as st

class EmailService:
    """Serviço para envio de emails usando SendGrid"""
    
    def __init__(self):
        # Configurar SendGrid API Key
        # Pode ser definida como variável de ambiente ou secrets do Streamlit
        self.api_key = (
            os.getenv('SENDGRID_API_KEY') or 
            st.secrets.get('SENDGRID_API_KEY') or
            st.secrets.get('sendgrid', {}).get('api_key')
        )
        
        if not self.api_key:
            raise ValueError("SENDGRID_API_KEY não encontrada. Configure como variável de ambiente ou secrets do Streamlit.")
        
        self.client = SendGridAPIClient(api_key=self.api_key)
        
        # Configurações padrão (com fallback para secrets e variáveis de ambiente)
        sendgrid_config = st.secrets.get('sendgrid', {})
        
        # Buscar configurações nas variáveis de ambiente primeiro, depois nos secrets
        self.from_email = (
            os.getenv('SENDGRID_FROM_EMAIL') or
            sendgrid_config.get('from_email', "noreply@cpzseg.com.br")
        )
        
        self.to_email = (
            os.getenv('SENDGRID_EMAIL_DESTINO') or
            sendgrid_config.get('email_destino', "informe@cpzseg.com.br")
        )
        
        self.from_name = (
            os.getenv('SENDGRID_FROM_NAME') or
            sendgrid_config.get('from_name', "Grupo CPZ - Formulários")
        )
        self.subject = "Nova Solicitação - Seguro Incêndio Conteúdos"
    
    def enviar_formulario(self, dados_formulario: Dict[str, Any], arquivos: List[Any] = None) -> bool:
        """
        Envia formulário por email usando template HTML
        
        Args:
            dados_formulario: Dados do formulário
            arquivos: Lista de arquivos anexados (opcional)
            
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Carregar e processar template
            html_content = self._processar_template(dados_formulario)
            
            # Criar email
            message = Mail(
                from_email=(self.from_email, self.from_name),
                to_emails=self.to_email,
                subject=self.subject,
                html_content=html_content
            )
            
            # Adicionar anexos se houver
            if arquivos:
                self._adicionar_anexos(message, arquivos)
            
            # Enviar email
            response = self.client.send(message)
            
            # Verificar sucesso (status 202 = aceito para entrega)
            return response.status_code == 202
            
        except Exception as e:
            st.error(f"Erro ao enviar email: {str(e)}")
            return False
    
    def _processar_template(self, dados: Dict[str, Any]) -> str:
        """Processa template HTML com os dados do formulário"""
        try:
            # Carregar template
            with open("templates/email_template.html", "r", encoding="utf-8") as f:
                template_content = f.read()
            
            template = Template(template_content)
            
            # Preparar dados para o template
            template_data = {
                'nome_completo': dados.get('nome_completo', ''),
                'cpf_formatado': self._formatar_cpf(dados.get('cpf', '')),
                'email': dados.get('email', ''),
                'telefone_formatado': self._formatar_telefone(dados.get('telefone', '')),
                'cnpj_formatado': self._formatar_cnpj(dados.get('cnpj', '')),
                'razao_social': dados.get('razao_social', ''),
                'cep_formatado': self._formatar_cep(dados.get('cep', '')),
                'logradouro': dados.get('logradouro', ''),
                'numero': dados.get('numero', ''),
                'bairro': dados.get('bairro', ''),
                'cidade': dados.get('cidade', ''),
                'estado': dados.get('estado', ''),
                'plano_nome': dados.get('plano_nome', ''),
                'premio_formatado': dados.get('premio_formatado', ''),
                'dias_restantes': dados.get('dias_restantes', ''),
                'equipamentos': dados.get('equipamentos', []),
                'equipamentos_html': len(dados.get('equipamentos', [])) > 0,
                'arquivos': dados.get('arquivos_info', []),
                'timestamp': datetime.now().strftime('%d/%m/%Y às %H:%M:%S'),
                'incluir_outro_quiosque': dados.get('incluir_outro_quiosque', False),
                'grupo_info': dados.get('grupo_info', {})
            }
            
            return template.render(**template_data)
            
        except Exception as e:
            st.error(f"Erro ao processar template: {str(e)}")
            return "<p>Erro ao gerar conteúdo do email</p>"
    
    def _adicionar_anexos(self, message: Mail, arquivos: List[Any]):
        """Adiciona arquivos como anexos ao email"""
        for arquivo in arquivos:
            try:
                # Ler conteúdo do arquivo
                file_content = arquivo.read()
                
                # Resetar ponteiro para futuras leituras
                if hasattr(arquivo, 'seek'):
                    arquivo.seek(0)
                
                # Codificar em base64
                encoded_content = base64.b64encode(file_content).decode()
                
                # Determinar tipo do arquivo
                file_name = getattr(arquivo, 'name', 'anexo')
                file_type = self._detectar_tipo_arquivo(file_name)
                
                # Criar anexo
                attachment = Attachment(
                    FileContent(encoded_content),
                    FileName(file_name),
                    FileType(file_type),
                    Disposition('attachment')
                )
                
                message.attachment = attachment
                
            except Exception as e:
                st.warning(f"Erro ao anexar arquivo {getattr(arquivo, 'name', 'desconhecido')}: {str(e)}")
    
    def _detectar_tipo_arquivo(self, nome_arquivo: str) -> str:
        """Detecta tipo MIME do arquivo baseado na extensão"""
        extensao = nome_arquivo.lower().split('.')[-1] if '.' in nome_arquivo else ''
        
        tipos = {
            'pdf': 'application/pdf',
            'jpg': 'image/jpeg',
            'jpeg': 'image/jpeg',
            'png': 'image/png',
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'xls': 'application/vnd.ms-excel'
        }
        
        return tipos.get(extensao, 'application/octet-stream')
    
    @staticmethod
    def _formatar_cpf(cpf: str) -> str:
        """Formata CPF com máscara"""
        if len(cpf) == 11:
            return f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
        return cpf
    
    @staticmethod
    def _formatar_cnpj(cnpj: str) -> str:
        """Formata CNPJ com máscara"""
        if len(cnpj) == 14:
            return f"{cnpj[:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:]}"
        return cnpj
    
    @staticmethod
    def _formatar_telefone(telefone: str) -> str:
        """Formata telefone com máscara"""
        if len(telefone) == 11:
            return f"({telefone[:2]}) {telefone[2:7]}-{telefone[7:]}"
        elif len(telefone) == 10:
            return f"({telefone[:2]}) {telefone[2:6]}-{telefone[6:]}"
        return telefone
    
    @staticmethod
    def _formatar_cep(cep: str) -> str:
        """Formata CEP com máscara"""
        if len(cep) == 8:
            return f"{cep[:5]}-{cep[5:]}"
        return cep 