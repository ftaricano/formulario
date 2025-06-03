"""
Formulário de Adesão - Seguro Incêndio Conteúdos
Versão Otimizada
"""

import streamlit as st
import sys
import os

# Adicionar diretório src ao path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Importações dos módulos refatorados
from src.models.formulario import FormularioSeguro
from src.validators.form_validators import FormValidator
from src.components.form_sections import (
    FormSectionRenderer, EquipamentosSection, ApiSearchHandler
)
from src.utils.formatters import ValueFormatter, StringUtils, DateUtils
from src.services.email_service import EmailService

# Importações do sistema original
from config import APP_CONFIG, PLANOS_SEGURO, DATA_FINAL_VIGENCIA
from datetime import datetime, timedelta

# Configuração da página
st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"]
)

class FormularioApp:
    """Classe principal da aplicação do formulário"""
    
    def __init__(self):
        self.formulario = None
        
    def inicializar(self):
        """Inicializa a aplicação"""
        self._carregar_css()
        self._ocultar_cabecalho()
        
    def _carregar_css(self):
        """Carrega arquivo CSS personalizado"""
        try:
            with open("styles.css", "r", encoding="utf-8") as f:
                css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
        except FileNotFoundError:
            st.warning("⚠ Arquivo styles.css não encontrado.")
    
    def _ocultar_cabecalho(self):
        """Oculta elementos do cabeçalho padrão do Streamlit"""
        st.markdown("""
        <style>
        div[data-testid="stHeader"] {
            visibility: hidden !important;
            height: 0 !important;
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
    
    def renderizar_cabecalho(self):
        """Renderiza cabeçalho da aplicação"""
        # Navigation bar com logo
        st.markdown("""
        <div class="navbar-container">
            <div class="navbar-content">
                <div class="navbar-logo">
                    <img src="data:image/png;base64,{}" alt="Logo" class="navbar-logo-img">
                </div>
            </div>
        </div>
        """.format(self._get_logo_base64()), unsafe_allow_html=True)
        
        # Header estilizado principal
        st.markdown("""
        <div class="header-container">
            <div class="header-content">
                <div class="header-titles">
                    <h1 class="header-main-title">Formulário de Adesão</h1>
                    <h2 class="header-subtitle">Seguro Incêndio Conteúdos - Cessionários</h2>
                    <p class="header-company"><strong>ORLA RIO</strong></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    def _get_logo_base64(self):
        """Converte logo para base64"""
        import base64
        try:
            with open("logo.png", "rb") as f:
                return base64.b64encode(f.read()).decode()
        except FileNotFoundError:
            return ""
    
    def renderizar_identificacao_quiosque(self):
        """Renderiza seção de identificação do quiosque"""
        FormSectionRenderer.render_section_header(
            "▪ Identificação do Quiosque",
            "Informe os dados do estabelecimento que será segurado"
        )
        
        # CNPJ com busca
        cnpj, buscar_cnpj_btn = FormSectionRenderer.render_field_with_search(
            label="▪ CNPJ *",
            field_name="cnpj",
            help_text="Digite o CNPJ (14 dígitos)",
            placeholder="00.000.000/0000-00"
        )
        
        # Razão social (preenchida automaticamente)
        razao_social = st.text_input(
            "▪ Razão Social",
            value=st.session_state.get('razao_social_busca', ''),
            help="Preenchido automaticamente após buscar CNPJ",
            key="razao_social"
        )
        
        # CEP com busca
        cep, buscar_cep_btn = FormSectionRenderer.render_field_with_search(
            label="▪ CEP *",
            field_name="cep",
            help_text="Digite o CEP no formato 00000-000",
            placeholder="00000-000"
        )
        
        # Campos de endereço
        logradouro = st.text_input(
            "▪ Logradouro *", 
            value=st.session_state.get('logradouro_busca', ''),
            key="logradouro"
        )
        
        col1, col2 = st.columns(2)
        with col1:
            numero = st.text_input("▪ Número *", key="numero")
        with col2:
            complemento = st.text_input("▪ Complemento", key="complemento")
        
        col1, col2 = st.columns(2)
        with col1:
            bairro = st.text_input(
                "▪ Bairro *", 
                value=st.session_state.get('bairro_busca', ''),
                key="bairro"
            )
        with col2:
            cidade = st.text_input(
                "▪ Cidade *", 
                value=st.session_state.get('cidade_busca', ''),
                key="cidade"
            )
        
        estado = st.text_input(
            "▪ Estado *", 
            value=st.session_state.get('estado_busca', ''),
            key="estado"
        )
        
        # Handlers para buscas automáticas
        ApiSearchHandler.handle_cnpj_search(cnpj, buscar_cnpj_btn)
        ApiSearchHandler.handle_cep_search(cep, buscar_cep_btn)
    
    def renderizar_identificacao_responsavel(self):
        """Renderiza seção de identificação do responsável"""
        FormSectionRenderer.render_section_header(
            "▪ Identificação do Responsável",
            "Dados da pessoa responsável pelo seguro"
        )
        
        cpf = st.text_input("▪ CPF *", placeholder="000.000.000-00", key="cpf")
        nome_completo = st.text_input("▪ Nome Completo *", key="nome_completo")
        email = st.text_input("▪ E-mail *", key="email")
        telefone = st.text_input("▪ Telefone *", placeholder="(11) 99999-9999", key="telefone")
    
    def renderizar_selecao_plano(self):
        """Renderiza seção de seleção de planos"""
        FormSectionRenderer.render_section_header(
            "▪ Seleção do Plano",
            "Escolha uma das opções de cobertura disponíveis"
        )
        
        # Criar opções formatadas
        plano_opcoes = []
        for plano, preco in PLANOS_SEGURO.items():
            plano_opcoes.append(f"{plano} -\n{ValueFormatter.formatar_valor_real(preco)}/ano")
        
        plano_selecionado = st.radio(
            "Plano",
            options=plano_opcoes,
            key="plano_radio",
            label_visibility="collapsed",
            horizontal=True
        )
        
        return plano_selecionado
    
    def renderizar_calculo_vigencia(self, plano_selecionado: str):
        """Renderiza cálculo de vigência e valores"""
        if plano_selecionado:
            plano_nome = plano_selecionado.split('\n')[0].replace(' -', '')
            preco_anual = PLANOS_SEGURO[plano_nome]
            
            # Calcular pro rata usando próximo dia útil (considerando feriados)
            data_inclusao = DateUtils.obter_proximo_dia_util()
            dias_restantes = (DATA_FINAL_VIGENCIA - data_inclusao.replace(tzinfo=None)).days + 1
            premio_pro_rata = round((preco_anual / 365) * dias_restantes, 2)
            
            # Verificar se a data de inclusão é diferente de amanhã (indicando que pulou feriado/fim de semana)
            amanha = datetime.now() + timedelta(days=1)
            observacao = ""
            if data_inclusao.date() != amanha.date():
                observacao = "* Data ajustada para próximo dia útil"
            
            # Quadro resumo da vigência centralizado
            st.markdown(f"""
            <div style="display: flex; justify-content: center; margin: 15px 0;">
                <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); border-radius: 12px; padding: 20px; max-width: 800px; width: 100%; color: white; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 10px 30px rgba(26, 26, 26, 0.4); position: relative;">
                    <h3 style="margin: 0 0 15px 0; color: #ffffff; font-size: 1.1em; text-align: center; position: relative; z-index: 2;">📅 Período de Vigência</h3>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; align-items: center; position: relative; z-index: 2;">
                        <div style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Data de Inclusão</div>
                            <div style="font-size: 1.1em; color: #000000; font-weight: bold;">{data_inclusao.strftime('%d/%m/%Y')}</div>
                        </div>
                        <div style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Final da Vigência</div>
                            <div style="font-size: 1.1em; color: #000000; font-weight: bold;">{DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}</div>
                        </div>
                        <div style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Dias Restantes</div>
                            <div style="font-size: 1.3em; color: #1a7a1a; font-weight: bold;">{dias_restantes} dias</div>
                        </div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Adicionar observação separadamente se existir
            if observacao:
                st.markdown(f"""
                <div style="display: flex; justify-content: center; margin: -10px 0 15px 0;">
                    <p style="font-size: 0.85em; color: #FED7D7; text-align: center; max-width: 800px;">{observacao}</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Valor destacado
            st.markdown(f"""
            <div class="total-value-section-black">
                <h3>Valor Total: {ValueFormatter.formatar_valor_real(premio_pro_rata)}</h3>
                <p>Valor proporcional para o período selecionado</p>
            </div>
            """, unsafe_allow_html=True)
            
            return premio_pro_rata
        return 0
    
    def processar_envio(self):
        """Processa envio do formulário"""
        if st.session_state.get('formulario_enviado', False):
            st.success("✓ **Formulário já enviado com sucesso!**")
            return
        
        # Botão de envio
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            enviar = st.button(
                "▶ Calcular e Enviar Solicitação",
                use_container_width=True,
                type="primary",
                key="enviar_formulario"
            )
        
        if enviar:
            with st.spinner("▪ Processando sua solicitação..."):
                # Criar modelo do formulário
                formulario = FormularioSeguro.from_session_state(st.session_state)
                dados = formulario.to_dict()
                
                # Validar
                erros = FormValidator.validar_formulario_completo(dados)
                
                if erros:
                    st.error("**Por favor, corrija os seguintes campos:**")
                    for erro in erros:
                        st.markdown(f"• {erro}")
                else:
                    # Preparar dados para envio do email
                    dados_email = self._preparar_dados_email(dados)
                    
                    # Coletar arquivos anexados (considerando os removidos)
                    arquivos = []
                    
                    # Adicionar arquivos de upload válidos
                    if st.session_state.get('arquivos_upload'):
                        arquivos_validos = [
                            arquivo for arquivo in st.session_state.arquivos_upload 
                            if arquivo.name not in st.session_state.get('arquivos_excluidos', [])
                        ]
                        arquivos.extend(arquivos_validos)
                    
                    # Adicionar foto da câmera se ativa
                    if (st.session_state.get('foto_camera_ativa', True) and 
                        st.session_state.get('foto_camera')):
                        arquivos.append(st.session_state.foto_camera)
                    
                    # Tentar enviar email
                    try:
                        email_service = EmailService()
                        sucesso = email_service.enviar_formulario(dados_email, arquivos)
                        
                        if sucesso:
                            # Sucesso - marcar como enviado
                            st.session_state.formulario_enviado = True
                            
                            primeiro_nome = StringUtils.obter_primeiro_nome(dados.get('nome_completo', ''))
                            st.success(f"### ✓ Obrigado, {primeiro_nome}!")
                            st.success("**■ Sua solicitação foi enviada com sucesso!**")
                            st.info("▪ **Nossa equipe analisará sua solicitação e entrará em contato em breve.**")
                        else:
                            st.error("**■ Erro ao enviar solicitação**")
                            st.error("▪ Tente novamente ou entre em contato conosco.")
                            
                    except ValueError as e:
                        # Erro de configuração (API Key não encontrada)
                        st.error("**■ Erro de configuração do sistema**")
                        st.error(f"▪ {str(e)}")
                        st.info("▪ Entre em contato com o administrador.")
                    except Exception as e:
                        # Outros erros
                        st.error("**■ Erro inesperado ao enviar solicitação**")
                        st.error(f"▪ {str(e)}")
                        st.info("▪ Tente novamente ou entre em contato conosco.")
    
    def _preparar_dados_email(self, dados_formulario: dict) -> dict:
        """Prepara dados formatados para o template de email"""
        # Obter dados da sessão para campos que podem ter sido preenchidos automaticamente
        razao_social = st.session_state.get('razao_social_busca', '') or dados_formulario.get('razao_social', '')
        
        # Obter plano selecionado e calcular valores
        plano_selecionado = st.session_state.get('plano_radio', '')
        plano_nome = ''
        premio_formatado = ''
        dias_restantes = ''
        
        if plano_selecionado:
            from config import PLANOS_SEGURO, DATA_FINAL_VIGENCIA
            plano_nome = plano_selecionado.split('\n')[0].replace(' -', '')
            preco_anual = PLANOS_SEGURO.get(plano_nome, 0)
            
            data_inclusao = DateUtils.obter_proximo_dia_util()
            dias_restantes_calc = (DATA_FINAL_VIGENCIA - data_inclusao.replace(tzinfo=None)).days + 1
            premio_pro_rata = round((preco_anual / 365) * dias_restantes_calc, 2)
            
            premio_formatado = ValueFormatter.formatar_valor_real(premio_pro_rata)
            dias_restantes = str(dias_restantes_calc)
        
        # Preparar informações de arquivos
        arquivos_info = []
        
        # Adicionar arquivos de upload (excluindo os removidos)
        if st.session_state.get('arquivos_upload'):
            arquivos_validos = [
                arquivo for arquivo in st.session_state.arquivos_upload 
                if arquivo.name not in st.session_state.get('arquivos_excluidos', [])
            ]
            for arquivo in arquivos_validos:
                arquivos_info.append({
                    'name': arquivo.name,
                    'size_mb': round(arquivo.size / 1024 / 1024, 2)
                })
        
        # Adicionar foto da câmera se ativa
        if (st.session_state.get('foto_camera_ativa', True) and 
            st.session_state.get('foto_camera')):
            arquivos_info.append({
                'name': 'Foto capturada pela câmera',
                'size_mb': round(len(st.session_state.foto_camera.getvalue()) / 1024 / 1024, 2)
            })
        
        # Preparar equipamentos
        equipamentos = []
        if st.session_state.get('equipamentos'):
            for eq in st.session_state.equipamentos:
                if eq.get('tipo', '').strip():  # Só incluir equipamentos preenchidos
                    equipamentos.append({
                        'tipo': eq.get('tipo', ''),
                        'descricao': eq.get('descricao', ''),
                        'valor': eq.get('valor', '')
                    })
        
        return {
            'nome_completo': dados_formulario.get('nome_completo', ''),
            'cpf': dados_formulario.get('cpf', ''),
            'email': dados_formulario.get('email', ''),
            'telefone': dados_formulario.get('telefone', ''),
            'cnpj': dados_formulario.get('cnpj', ''),
            'razao_social': razao_social,
            'cep': dados_formulario.get('cep', ''),
            'logradouro': dados_formulario.get('logradouro', ''),
            'numero': dados_formulario.get('numero', ''),
            'bairro': dados_formulario.get('bairro', ''),
            'cidade': dados_formulario.get('cidade', ''),
            'estado': dados_formulario.get('estado', ''),
            'plano_nome': plano_nome,
            'premio_formatado': premio_formatado,
            'dias_restantes': dias_restantes,
            'equipamentos': equipamentos,
            'arquivos_info': arquivos_info
        }
    
    def executar(self):
        """Executa a aplicação principal"""
        self.inicializar()
        self.renderizar_cabecalho()
        
        # Verificar erros anteriores
        if st.session_state.get('show_errors', False):
            st.error("**Erros encontrados no formulário anterior**")
            st.info("▪ **Seus dados foram preservados!** Corrija os campos abaixo.")
        
        # Renderizar seções na nova ordem
        self.renderizar_identificacao_quiosque()
        self.renderizar_identificacao_responsavel()
        
        # Seleção de plano primeiro
        plano_selecionado = self.renderizar_selecao_plano()
        
        # Agora renderizar equipamentos após seleção do plano
        equipamentos = EquipamentosSection.render()
        
        # Upload de arquivos após equipamentos
        FormSectionRenderer.render_section_header(
            "▪ Anexar Documentos (Opcional)",
            "Adicione fotos ou documentos dos equipamentos e da propriedade. Use os botões para remover arquivos."
        )
        
        # Inicializar lista de arquivos excluídos se não existir
        if 'arquivos_excluidos' not in st.session_state:
            st.session_state.arquivos_excluidos = []
        
        # Tabs para organizar as opções
        tab1, tab2 = st.tabs(["📁 Selecionar Arquivos", "📷 Tirar Foto"])
        
        with tab1:
            st.markdown("**Selecione arquivos do seu dispositivo:**")
            arquivos_upload = st.file_uploader(
                "Selecione os arquivos",
            type=['jpg', 'jpeg', 'png', 'pdf', 'xlsx'],
            accept_multiple_files=True,
                key="arquivos_upload",
                label_visibility="collapsed"
        )
        
            # Filtrar arquivos não excluídos
            if arquivos_upload:
                arquivos_validos = [
                    arquivo for arquivo in arquivos_upload 
                    if arquivo.name not in st.session_state.arquivos_excluidos
                ]
                
                if arquivos_validos:
                    st.success(f"✓ {len(arquivos_validos)} arquivo(s) selecionado(s)")
                    
                    # Mostrar arquivos com botões de remoção
                    for i, arquivo in enumerate(arquivos_validos):
                        col1, col2 = st.columns([4, 1])
                        with col1:
                            st.markdown(f"📄 **{arquivo.name}** ({arquivo.size // 1024} KB)")
                        with col2:
                            if st.button("🗑️", key=f"remove_file_{i}_{arquivo.name}", 
                                       help=f"Remover {arquivo.name}",
                                       use_container_width=True):
                                st.session_state.arquivos_excluidos.append(arquivo.name)
                                st.rerun()
                else:
                    st.info("Todos os arquivos foram removidos.")
                
                # Botão para limpar todos os arquivos
                if arquivos_validos and len(arquivos_validos) > 1:
                    if st.button("🧹 Remover Todos os Arquivos", 
                               key="clear_all_files", 
                               type="secondary"):
                        for arquivo in arquivos_validos:
                            st.session_state.arquivos_excluidos.append(arquivo.name)
                        st.rerun()
        
        with tab2:
            st.markdown("**Tire uma foto diretamente:**")
            
            # Controle manual da foto da câmera
            if 'foto_camera_ativa' not in st.session_state:
                st.session_state.foto_camera_ativa = True
            
            if st.session_state.foto_camera_ativa:
                foto_camera = st.camera_input(
                    "Clique para tirar foto",
                    key="foto_camera",
                    label_visibility="collapsed"
                )
                
                if foto_camera:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.success("✓ Foto capturada com sucesso!")
                        # Mostrar preview da imagem em tamanho menor
                        st.image(foto_camera, caption="Foto capturada", width=300)
                    with col2:
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button("🗑️ Remover Foto", 
                                   key="remove_camera_photo",
                                   use_container_width=True):
                            st.session_state.foto_camera_ativa = False
                            if 'foto_camera' in st.session_state:
                                del st.session_state.foto_camera
                            st.rerun()
            else:
                st.info("📷 Foto removida.")
                if st.button("📷 Capturar Nova Foto", 
                           key="new_camera_photo",
                           use_container_width=True):
                    st.session_state.foto_camera_ativa = True
                    st.rerun()
        
        # Combinar todos os arquivos válidos
        arquivos = []
        
        # Adicionar arquivos de upload (excluindo os removidos)
        if arquivos_upload:
            arquivos_validos = [
                arquivo for arquivo in arquivos_upload 
                if arquivo.name not in st.session_state.arquivos_excluidos
            ]
            arquivos.extend(arquivos_validos)
        
        # Adicionar foto da câmera se ativa
        if st.session_state.get('foto_camera_ativa', True) and st.session_state.get('foto_camera'):
            arquivos.append(st.session_state.foto_camera)
        
        # Mostrar resumo se houver arquivos
        if arquivos:
            st.markdown("---")
            st.markdown("**📋 Resumo Final dos Anexos:**")
            total_size = 0
            for i, arquivo in enumerate(arquivos, 1):
                size_kb = arquivo.size // 1024 if hasattr(arquivo, 'size') else 0
                total_size += size_kb
                tipo = "📷 Foto" if arquivo == st.session_state.get('foto_camera') else "📄 Arquivo"
                nome = getattr(arquivo, 'name', f'Foto_{i}.jpg')
                st.markdown(f"**{i}.** {tipo}: {nome} ({size_kb} KB)")
            
            st.markdown(f"**Total:** {len(arquivos)} anexo(s) - {total_size} KB")
            
            if total_size > 25 * 1024:  # 25MB limit
                st.warning("⚠️ Tamanho total dos arquivos excede 25MB")
        else:
            st.info("📎 Nenhum arquivo anexado.")
        
        # Cálculo do valor por último
        premio_calculado = self.renderizar_calculo_vigencia(plano_selecionado)
        
        # Processamento final
        self.processar_envio()

def main():
    """Função principal"""
    app = FormularioApp()
    app.executar()

if __name__ == "__main__":
    main() 