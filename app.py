"""
Formulário de Adesão - Seguro Incêndio Conteúdos
Versão Otimizada
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import os
import time

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
        div[data-testid="stHeader"],
        header[data-testid="stHeader"],
        .stApp > header,
        .main-header {
            visibility: hidden !important;
            height: 0 !important;
            min-height: 0 !important;
            max-height: 0 !important;
            display: none !important;
            padding: 0 !important;
            margin: 0 !important;
            border: none !important;
            background: transparent !important;
        }
        
        /* Remove qualquer fundo branco superior */
        body, html, #root, .stApp {
            margin-top: 0 !important;
            padding-top: 0 !important;
            border-top: none !important;
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
            "Informe os dados do estabelecimento que será segurado."
        )
        
        # CNPJ com busca automática silenciosa
        cnpj, cnpj_searched = FormSectionRenderer.render_field_with_search(
            label="▪ CNPJ *",
            field_name="cnpj",
            help_text="Digite o CNPJ (14 dígitos) - A razão social será preenchida automaticamente",
            placeholder="00.000.000/0000-00"
        )
        
        # Razão social (preenchida automaticamente)
        razao_social = st.text_input(
            "▪ Razão Social",
            value=st.session_state.get('razao_social_busca', ''),
            help="Preenchido automaticamente quando um CNPJ válido é digitado",
            key="razao_social"
        )
        
        # CEP com busca automática silenciosa
        cep, cep_searched = FormSectionRenderer.render_field_with_search(
            label="▪ CEP *",
            field_name="cep",
            help_text="Digite o CEP no formato 00000-000 - O endereço será preenchido automaticamente",
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
    
    def renderizar_identificacao_responsavel(self):
        """Renderiza seção de identificação do responsável"""
        FormSectionRenderer.render_section_header(
            "▪ Identificação do Responsável",
            "Dados da pessoa responsável pelo seguro."
        )
        
        cpf = st.text_input("▪ CPF *", placeholder="000.000.000-00", key="cpf")
        nome_completo = st.text_input("▪ Nome Completo *", key="nome_completo")
        email = st.text_input("▪ E-mail *", key="email")
        telefone = st.text_input("▪ Telefone *", placeholder="(11) 99999-9999", key="telefone")
    
    def renderizar_selecao_plano(self):
        """Renderiza seção de seleção de planos"""
        FormSectionRenderer.render_section_header(
            "▪ Seleção do Plano",
            "Escolha uma das opções de cobertura disponíveis."
        )
        
        # Criar opções formatadas
        plano_opcoes = []
        for plano, preco in PLANOS_SEGURO.items():
            valor_formatado = ValueFormatter.formatar_valor_real(preco).replace("R$ ", "")
            plano_opcoes.append(f"{plano} -\n{valor_formatado}/ano")
        
        plano_selecionado = st.radio(
            "Plano",
            options=plano_opcoes,
            key="plano_radio",
            label_visibility="collapsed",
            horizontal=True
        )
        
        # Adicionar tabela de coberturas após seleção
        if plano_selecionado:
            self._renderizar_tabela_coberturas()
        
        return plano_selecionado
    
    def _renderizar_tabela_coberturas(self):
        """Renderiza tabela compacta de coberturas otimizada para mobile"""
        st.markdown("---")
        st.markdown("**📋 Coberturas Incluídas nos Planos:**")
        
        # Tabela responsiva com CSS customizado
        st.markdown("""
        <style>
        .coverage-table {
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.75rem;
            background: white;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .coverage-table th {
            background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);
            color: white;
            padding: 6px 4px;
            text-align: center;
            font-weight: bold;
            font-size: 0.7rem;
        }
        .coverage-table td {
            padding: 4px 3px;
            text-align: center;
            border-bottom: 1px solid #eee;
            font-size: 0.7rem;
        }
        .coverage-table tr:nth-child(even) {
            background-color: #f8f9fa;
        }
        .coverage-table tr:hover {
            background-color: #e8f4f8;
        }
        .coverage-name {
            text-align: left !important;
            font-weight: 500;
            padding-left: 6px !important;
        }
        .franchise-col {
            color: #dc3545;
            font-weight: 500;
        }
        .no-franchise {
            background-color: #d4edda;
            color: #155724;
            font-weight: 500;
        }
        @media (max-width: 768px) {
            .coverage-table {
                font-size: 0.65rem;
            }
            .coverage-table th {
                font-size: 0.6rem;
                padding: 4px 2px;
            }
            .coverage-table td {
                padding: 3px 2px;
                font-size: 0.6rem;
            }
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Tabela HTML compacta
        st.markdown("""
        <table class="coverage-table">
            <thead>
                <tr>
                    <th style="width: 35%;">Coberturas</th>
                    <th style="width: 15%;">Opção 1</th>
                    <th style="width: 15%;">Opção 2</th>
                    <th style="width: 15%;">Opção 3</th>
                    <th style="width: 20%;">Franquia</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td class="coverage-name">Incêndio, Raio e Explosão</td>
                    <td>250.000</td>
                    <td>400.000</td>
                    <td>700.000</td>
                    <td class="franchise-col">30.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Alagamento</td>
                    <td>50.000</td>
                    <td>100.000</td>
                    <td>150.000</td>
                    <td class="franchise-col">15.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Danos Elétricos</td>
                    <td>20.000</td>
                    <td>50.000</td>
                    <td>100.000</td>
                    <td class="franchise-col">3.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Pequenas Obras</td>
                    <td>50.000</td>
                    <td>100.000</td>
                    <td>150.000</td>
                    <td class="franchise-col">5.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Perda/Pgto Aluguel (6m)</td>
                    <td>20.000</td>
                    <td>30.000</td>
                    <td>40.000</td>
                    <td class="no-franchise">Não Há</td>
                </tr>
                <tr>
                    <td class="coverage-name">Vidros</td>
                    <td>20.000</td>
                    <td>50.000</td>
                    <td>100.000</td>
                    <td class="franchise-col">3.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Tumultos</td>
                    <td>100.000</td>
                    <td>150.000</td>
                    <td>200.000</td>
                    <td class="franchise-col">5.000</td>
                </tr>
                <tr>
                    <td class="coverage-name">Vendaval</td>
                    <td>100.000</td>
                    <td>150.000</td>
                    <td>200.000</td>
                    <td class="franchise-col">10.000</td>
                </tr>
            </tbody>
        </table>
        """, unsafe_allow_html=True)
    
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
            
            # Quadro resumo da vigência centralizado com responsividade
            st.markdown(f"""
            <style>
                @media (max-width: 767px) {{
                    .vigencia-grid {{
                        display: grid !important;
                        grid-template-columns: 1fr !important;
                        gap: 12px !important;
                    }}
                    .vigencia-container {{
                        padding: 15px !important;
                        margin: 10px 5px !important;
                    }}
                    .vigencia-card {{
                        padding: 12px !important;
                    }}
                    .vigencia-card-label {{
                        font-size: 0.8em !important;
                    }}
                    .vigencia-card-value {{
                        font-size: 1em !important;
                    }}
                    .vigencia-card-value.destaque {{
                        font-size: 1.1em !important;
                    }}
                }}
            </style>
            <div style="display: flex; justify-content: center; margin: 15px 0;">
                <div class="vigencia-container" style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); border-radius: 12px; padding: 20px; max-width: 800px; width: 100%; color: white; border: 1px solid rgba(255, 255, 255, 0.1); box-shadow: 0 10px 30px rgba(26, 26, 26, 0.4); position: relative;">
                    <h3 style="margin: 0 0 15px 0; color: #ffffff; font-size: 1.1em; text-align: center; position: relative; z-index: 2;">📅 Período de Vigência</h3>
                    <div class="vigencia-grid" style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 15px; align-items: center; position: relative; z-index: 2;">
                        <div class="vigencia-card" style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div class="vigencia-card-label" style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Data de Inclusão</div>
                            <div class="vigencia-card-value" style="font-size: 1.1em; color: #000000; font-weight: bold;">{data_inclusao.strftime('%d/%m/%Y')}</div>
                        </div>
                        <div class="vigencia-card" style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div class="vigencia-card-label" style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Final da Vigência</div>
                            <div class="vigencia-card-value" style="font-size: 1.1em; color: #000000; font-weight: bold;">{DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y')}</div>
                        </div>
                        <div class="vigencia-card" style="background: #ffffff; padding: 15px; border-radius: 8px; text-align: center; position: relative; z-index: 3; border: 2px solid rgba(255, 255, 255, 0.4); box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3);">
                            <div class="vigencia-card-label" style="font-size: 0.9em; margin-bottom: 5px; color: #333333;">Dias Restantes</div>
                            <div class="vigencia-card-value destaque" style="font-size: 1.3em; color: #1a7a1a; font-weight: bold;">{dias_restantes} dias</div>
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

        # Botão de envio (só aparece se formulário ainda não foi enviado)
        # Checkbox para incluir outro quiosque
        st.markdown("---")
        incluir_outro_quiosque = st.checkbox(
            "✅ Deseja incluir outro quiosque para cobrança única?",
            key="incluir_outro_quiosque",
            help="Marque esta opção se você possui outro quiosque que deseja incluir na mesma apólice"
        )
        
        # Se checkbox marcado, mostrar aviso
        if incluir_outro_quiosque:
            st.info("📋 **Atenção:** Ao marcar esta opção e finalizar o formulário, será necessário preenchê-lo novamente com as informações do novo quiosque.")
        
        st.markdown("---")
        
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
                    # Verificar se deve incluir outro quiosque e criar grupo se necessário
                    incluir_outro = st.session_state.get('incluir_outro_quiosque', False)
                    
                    if incluir_outro and 'grupo_quiosques' not in st.session_state:
                        # Primeira vez com "incluir outro" - criar grupo
                        st.session_state.grupo_quiosques = {
                            'id': f"GRUPO_{int(time.time())}",
                            'contador': 1,
                            'responsavel_principal': dados.get('nome_completo', ''),
                            'email_principal': dados.get('email', '')
                        }
                    elif 'grupo_quiosques' in st.session_state:
                        # Já existe grupo - incrementar contador
                        st.session_state.grupo_quiosques['contador'] += 1
                    
                    # Preparar dados para envio do email
                    dados_email = self._preparar_dados_email(dados)
                    
                    # Coletar arquivos anexados
                    arquivos = []
                    
                    # Adicionar arquivos de upload
                    if st.session_state.get('arquivos_upload'):
                        arquivos.extend(st.session_state.arquivos_upload)
                    
                    # Tentar enviar email
                    try:
                        email_service = EmailService()
                        sucesso = email_service.enviar_formulario(dados_email, arquivos)
                        
                        if sucesso:
                            # Verificar se está em modo de grupo (incluir outro quiosque)
                            if incluir_outro or 'grupo_quiosques' in st.session_state:
                                # Verificar se é continuação do grupo ou finalização
                                if incluir_outro:
                                    # Continuação de grupo - não é o último quiosque
                                    primeiro_nome = StringUtils.obter_primeiro_nome(dados.get('nome_completo', ''))
                                    contador = st.session_state.grupo_quiosques['contador'] if 'grupo_quiosques' in st.session_state else 1
                                    proximo_numero = contador + 1
                                    
                                    # Resetar formulário mas manter dados do grupo
                                    self._resetar_formulario_grupo()
                                    
                                    # Marcar que acabou de enviar um quiosque do grupo
                                    st.session_state.quiosque_enviado_grupo = True
                                    st.session_state.ultimo_contador = contador
                                    st.session_state.proximo_numero = proximo_numero
                                    st.session_state.primeiro_nome_enviado = primeiro_nome
                                    
                                    # Scroll ao topo
                                    st.session_state.scroll_to_top = True
                                    
                                    # Rerun para mostrar tela de confirmação
                                    st.rerun()
                                else:
                                    # Finalização de grupo - último quiosque (incluir_outro = False mas grupo existe)
                                    st.session_state.formulario_enviado = True
                                    # Marcar que foi envio com grupo para mostrar botão de nova solicitação
                                    st.session_state.foi_envio_com_grupo = True
                                    
                                    primeiro_nome = StringUtils.obter_primeiro_nome(dados.get('nome_completo', ''))
                                    contador = st.session_state.grupo_quiosques['contador'] if 'grupo_quiosques' in st.session_state else 1
                                    
                                    st.success(f"### ✓ Grupo finalizado com sucesso, {primeiro_nome}!")
                                    st.success(f"**■ Total de {contador} quiosques enviados!**")
                                    st.info("▪ **Nossa equipe analisará suas solicitações e entrará em contato em breve.**")
                                    st.rerun()  # Recarregar para mostrar o botão de nova solicitação
                            else:
                                # Sucesso final - formulário normal (sem grupo)
                                primeiro_nome = StringUtils.obter_primeiro_nome(dados.get('nome_completo', ''))
                                
                                # Marcar que acabou de enviar formulário normal
                                st.session_state.formulario_enviado_normal = True
                                st.session_state.primeiro_nome_normal = primeiro_nome
                                
                                # Scroll ao topo
                                st.session_state.scroll_to_top = True
                                
                                # Rerun para mostrar tela de confirmação
                                st.rerun()
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
        
        # Adicionar arquivos de upload
        if st.session_state.get('arquivos_upload'):
            for arquivo in st.session_state.arquivos_upload:
                arquivos_info.append({
                    'name': arquivo.name,
                    'size_mb': round(arquivo.size / 1024 / 1024, 2)
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
            'arquivos_info': arquivos_info,
            'incluir_outro_quiosque': st.session_state.get('incluir_outro_quiosque', False),
            'grupo_info': self._obter_info_grupo()
        }
    
    def _resetar_formulario(self):
        """Reseta todos os campos do formulário no session_state"""
        # Lista de todas as chaves do session_state relacionadas ao formulário
        chaves_para_resetar = [
            # Identificação do Quiosque
            'cnpj', 'razao_social', 'razao_social_busca',
            'cep', 'logradouro', 'logradouro_busca', 'numero', 'complemento',
            'bairro', 'bairro_busca', 'cidade', 'cidade_busca', 'estado', 'estado_busca',
            
            # Identificação do Responsável
            'cpf', 'nome_completo', 'email', 'telefone',
            
            # Seleção do Plano
            'plano_radio',
            
            # Equipamentos
            'equipamentos', 'num_equipamentos',
            
            # Arquivos
            'arquivos_upload',
            
            # Opções adicionais
            'incluir_outro_quiosque',
            
            # Controle do formulário
            'formulario_enviado', 'show_errors', 'scroll_to_top',
            
            # Dados do grupo
            'grupo_quiosques'
        ]
        
        # Resetar todas as chaves
        for chave in chaves_para_resetar:
            if chave in st.session_state:
                del st.session_state[chave]
        
        # Limpar dados de busca automática
        campos_busca = [
            'razao_social_busca', 'logradouro_busca', 'bairro_busca', 
            'cidade_busca', 'estado_busca'
        ]
        
        for campo in campos_busca:
            if campo in st.session_state:
                del st.session_state[campo]
    
    def _resetar_formulario_grupo(self):
        """Reseta todos os campos do formulário no session_state para o grupo"""
        # Lista de todas as chaves do session_state relacionadas ao formulário
        chaves_para_resetar = [
            # Identificação do Quiosque
            'cnpj', 'razao_social', 'razao_social_busca',
            'cep', 'logradouro', 'logradouro_busca', 'numero', 'complemento',
            'bairro', 'bairro_busca', 'cidade', 'cidade_busca', 'estado', 'estado_busca',
            
            # Identificação do Responsável
            'cpf', 'nome_completo', 'email', 'telefone',
            
            # Seleção do Plano
            'plano_radio',
            
            # Equipamentos
            'equipamentos', 'num_equipamentos',
            
            # Arquivos
            'arquivos_upload',
            
            # Opções adicionais
            'incluir_outro_quiosque',
            
            # Controle do formulário
            'formulario_enviado', 'show_errors'
        ]
        
        # Resetar todas as chaves
        for chave in chaves_para_resetar:
            if chave in st.session_state:
                del st.session_state[chave]
        
        # Limpar dados de busca automática
        campos_busca = [
            'razao_social_busca', 'logradouro_busca', 'bairro_busca', 
            'cidade_busca', 'estado_busca'
        ]
        
        for campo in campos_busca:
            if campo in st.session_state:
                del st.session_state[campo]
    
    def _obter_info_grupo(self):
        """Obtém informações do grupo de quiosques se existir"""
        if 'grupo_quiosques' in st.session_state:
            grupo = st.session_state.grupo_quiosques
            return {
                'pertence_grupo': True,
                'grupo_id': grupo['id'],
                'numero_quiosque': grupo['contador'],
                'responsavel_principal': grupo['responsavel_principal'],
                'email_principal': grupo['email_principal']
            }
        else:
            return {
                'pertence_grupo': False,
                'grupo_id': None,
                'numero_quiosque': 1,
                'responsavel_principal': None,
                'email_principal': None
            }
    
    def executar(self):
        """Executa a aplicação principal"""
        self.inicializar()
        
        # Adicionar âncora invisível no topo absoluto
        st.markdown('<div id="topo-pagina" style="position: absolute; top: 0; left: 0; width: 1px; height: 1px;"></div>', unsafe_allow_html=True)
        
        # Verificar se deve fazer scroll ao topo (via localStorage ou session_state)
        st.markdown("""
        <script>
            // Verificar se deve fazer scroll baseado no localStorage
            if (localStorage.getItem('scroll_to_top_on_load') === 'true') {
                // Limpar flag
                localStorage.removeItem('scroll_to_top_on_load');
                
                // Função para forçar scroll ao topo de forma agressiva
                function forcarScrollTopoReload() {
                    // Método 1: Window scroll
                    window.scrollTo({top: 0, left: 0, behavior: 'instant'});
                    
                    // Método 2: Document scroll
                    document.documentElement.scrollTop = 0;
                    document.body.scrollTop = 0;
                    
                    // Método 3: Scroll para elemento âncora
                    const topoElement = document.getElementById('topo-pagina');
                    if (topoElement) {
                        topoElement.scrollIntoView({behavior: 'instant', block: 'start'});
                    }
                    
                    // Método 4: Hash navigation
                    window.location.hash = '#topo-pagina';
                    setTimeout(() => {
                        window.location.hash = '';
                        window.scrollTo(0, 0);
                    }, 50);
                    
                    // Método 5: Scroll manual de todos elementos scrolláveis
                    const scrollableElements = document.querySelectorAll('*');
                    scrollableElements.forEach(el => {
                        if (el.scrollTop > 0) {
                            el.scrollTop = 0;
                        }
                    });
                }
                
                // Executar imediatamente
                forcarScrollTopoReload();
                
                // Executar após DOM pronto
                document.addEventListener('DOMContentLoaded', forcarScrollTopoReload);
                
                // Múltiplas tentativas agressivas
                setTimeout(forcarScrollTopoReload, 10);
                setTimeout(forcarScrollTopoReload, 50);
                setTimeout(forcarScrollTopoReload, 100);
                setTimeout(forcarScrollTopoReload, 200);
                setTimeout(forcarScrollTopoReload, 300);
                setTimeout(forcarScrollTopoReload, 500);
                setTimeout(forcarScrollTopoReload, 800);
                setTimeout(forcarScrollTopoReload, 1000);
                setTimeout(forcarScrollTopoReload, 1500);
                
                // Observer para garantir scroll quando elementos mudarem
                const observer = new MutationObserver(function() {
                    setTimeout(forcarScrollTopoReload, 10);
                });
                observer.observe(document.body, {childList: true, subtree: true});
                
                // Desativar observer após 3 segundos
                setTimeout(() => observer.disconnect(), 3000);
            }
        </script>
        """, unsafe_allow_html=True)
        
        # Verificar se deve fazer scroll ao topo (session_state - fallback)
        if st.session_state.get('scroll_to_top', False):
            # Limpar flag
            st.session_state.scroll_to_top = False
            
            # Componente HTML para scroll via session_state
            components.html("""
            <script>
                function scrollTopoParent() {
                    // Scroll na janela pai
                    parent.window.scrollTo({top: 0, left: 0, behavior: 'instant'});
                    parent.document.documentElement.scrollTop = 0;
                    parent.document.body.scrollTop = 0;
                    
                    // Tentar scroll no elemento âncora
                    const topoEl = parent.document.getElementById('topo-pagina');
                    if (topoEl) {
                        topoEl.scrollIntoView({behavior: 'instant', block: 'start'});
                    }
                    
                    // Scroll em todos elementos scrolláveis do pai
                    const allElements = parent.document.querySelectorAll('*');
                    allElements.forEach(el => {
                        if (el.scrollTop > 0) {
                            el.scrollTop = 0;
                        }
                    });
                }
                
                // Executar imediatamente
                scrollTopoParent();
                
                // Múltiplas tentativas
                setTimeout(scrollTopoParent, 10);
                setTimeout(scrollTopoParent, 50);
                setTimeout(scrollTopoParent, 100);
                setTimeout(scrollTopoParent, 200);
                setTimeout(scrollTopoParent, 300);
                setTimeout(scrollTopoParent, 500);
                setTimeout(scrollTopoParent, 800);
                setTimeout(scrollTopoParent, 1000);
            </script>
            """, height=0)
        
        # Verificar se acabou de enviar um formulário normal (tela de confirmação)
        if st.session_state.get('formulario_enviado_normal', False):
            # Limpar flag
            st.session_state.formulario_enviado_normal = False
            
            # Obter dados salvos
            primeiro_nome = st.session_state.get('primeiro_nome_normal', '')
            
            # Tela de confirmação estilizada para formulário normal
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                        color: white; padding: 2rem; border-radius: 15px; 
                        margin: 20px 0; text-align: center; 
                        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);">
                <h1 style="margin: 0 0 1rem 0; font-size: 2rem;">✅ Formulário Encaminhado com Sucesso!</h1>
                <h2 style="margin: 0 0 1.5rem 0; font-size: 1.3rem;">Obrigado, {primeiro_nome}!</h2>
                <p style="margin: 0 0 1.5rem 0; font-size: 1.1rem; line-height: 1.6;">
                    Sua solicitação foi enviada e processada com sucesso.<br>
                    <strong>▪ Nossa equipe analisará sua solicitação e entrará em contato em breve.</strong>
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão para preencher outro formulário
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    "🔄 Preencher Outro Formulário",
                    use_container_width=True,
                    type="secondary",
                    key="novo_formulario"
                ):
                    # Limpar dados da confirmação
                    if 'primeiro_nome_normal' in st.session_state:
                        del st.session_state['primeiro_nome_normal']
                    
                    # Resetar formulário completamente
                    self._resetar_formulario()
                    
                    # Marcar scroll ao topo
                    st.session_state.scroll_to_top = True
                    
                    # Rerun para voltar ao formulário limpo
                    st.rerun()
            
            # Parar execução aqui - só continua após clicar no botão
            return
        
        # Verificar se acabou de enviar um quiosque do grupo (tela de confirmação)
        if st.session_state.get('quiosque_enviado_grupo', False):
            # Limpar flag
            st.session_state.quiosque_enviado_grupo = False
            
            # Obter dados salvos
            contador = st.session_state.get('ultimo_contador', 1)
            proximo_numero = st.session_state.get('proximo_numero', 2)
            primeiro_nome = st.session_state.get('primeiro_nome_enviado', '')
            
            # Tela de confirmação estilizada
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #28a745 0%, #20c997 100%); 
                        color: white; padding: 2rem; border-radius: 15px; 
                        margin: 20px 0; text-align: center; 
                        box-shadow: 0 10px 30px rgba(40, 167, 69, 0.3);">
                <h1 style="margin: 0 0 1rem 0; font-size: 2rem;">✅ Quiosque {contador} Enviado!</h1>
                <h2 style="margin: 0 0 1.5rem 0; font-size: 1.3rem;">Parabéns, {primeiro_nome}!</h2>
                <p style="margin: 0 0 1.5rem 0; font-size: 1.1rem; line-height: 1.6;">
                    Os dados do quiosque {contador} foram enviados e processados com sucesso.<br>
                    <strong>Próximo passo:</strong> Preencher os dados do Quiosque {proximo_numero} do mesmo grupo.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            # Botão nativo do Streamlit (muito mais confiável)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button(
                    f"➜ Continuar para o Quiosque {proximo_numero}",
                    use_container_width=True,
                    type="primary",
                    key="continuar_proximo_quiosque"
                ):
                    # Limpar dados da confirmação
                    for key in ['ultimo_contador', 'proximo_numero', 'primeiro_nome_enviado']:
                        if key in st.session_state:
                            del st.session_state[key]
                    
                    # Marcar scroll ao topo
                    st.session_state.scroll_to_top = True
                    
                    # Rerun para continuar com formulário limpo
                    st.rerun()
            
            # Parar execução aqui - só continua após clicar no botão
            return
        
        self.renderizar_cabecalho()
        
        # Verificar se faz parte de um grupo de quiosques
        if 'grupo_quiosques' in st.session_state:
            grupo = st.session_state.grupo_quiosques
            proximo_numero = grupo['contador'] + 1
            
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%); 
                        color: white; padding: 1rem; border-radius: 10px; 
                        margin: 10px 0; text-align: center; border: 2px solid #4a5568;">
                <h3 style="margin: 0; color: white;">Quiosque {proximo_numero}</h3>
            </div>
            """, unsafe_allow_html=True)
        
        # Verificar erros anteriores
        if st.session_state.get('show_errors', False):
            st.error("**Erros encontrados no formulário anterior**")
            st.info("▪ **Seus dados foram preservados!** Corrija os campos abaixo.")
        
        # Renderizar seções na nova ordem
        self.renderizar_identificacao_quiosque()
        self.renderizar_identificacao_responsavel()
        
        # Seleção de plano primeiro
        plano_selecionado = self.renderizar_selecao_plano()
        
        # Nota: CSS responsivo de equipamentos movido para src/components/form_sections.py
        # para melhor organização e layout intercalado em mobile
        
        # Agora renderizar equipamentos após seleção do plano
        equipamentos = EquipamentosSection.render()
        
        
        # Upload de arquivos após equipamentos
        FormSectionRenderer.render_section_header(
            "▪ Anexar Documentos (Opcional)",
            "Adicione fotos ou documentos dos equipamentos e da propriedade."
        )
        
        # Aviso simples sobre limites
        st.info("📋 **Limite de tamanho:** Máximo 10MB por arquivo | Máximo 25MB no total")
        
        # CSS personalizado para ocultar botão de browse e personalizar área de upload
        st.markdown("""
        <style>
        /* Personalizar área de upload */
        .stFileUploader [data-testid="stFileUploaderDropzone"] {
            position: relative !important;
            min-height: 120px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
            border: 2px dashed #cccccc !important;
            border-radius: 8px !important;
            background-color: #fafafa !important;
            margin-bottom: 15px !important;
        }
        
        .stFileUploader [data-testid="stFileUploaderDropzone"]:hover {
            border-color: #999999 !important;
            background-color: #f5f5f5 !important;
        }
        
        /* Esconder textos originais em inglês */
        .stFileUploader [data-testid="stFileUploaderDropzone"] > div,
        .stFileUploader [data-testid="stFileUploaderDropzone"] span,
        .stFileUploader [data-testid="stFileUploaderDropzone"] small,
        .stFileUploader [data-testid="stFileUploaderDropzone"] p {
            opacity: 0 !important;
            font-size: 0 !important;
        }
        
        /* Texto principal em português - centralizado */
        .stFileUploader [data-testid="stFileUploaderDropzone"]::before {
            content: "Clique aqui para anexar arquivos" !important;
            position: absolute !important;
            top: 50% !important;
            left: 50% !important;
            transform: translate(-50%, -50%) !important;
            font-size: 1.1rem !important;
            color: #666666 !important;
            font-weight: 600 !important;
            pointer-events: none !important;
            z-index: 10 !important;
        }
        
        /* OCULTAR COMPLETAMENTE o botão Browse files */
        .stFileUploader button[kind="secondary"] {
            display: none !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Upload de arquivos apenas com drag & drop
        arquivos_upload = st.file_uploader(
            "Área de upload",
            type=['jpg', 'jpeg', 'png', 'pdf', 'xlsx'],
            accept_multiple_files=True,
            key="arquivos_upload",
            help="Tipos aceitos: JPG, JPEG, PNG, PDF, XLSX • Máximo: 10MB por arquivo",
            label_visibility="collapsed"
        )
        
        # Usar apenas arquivos de upload
        arquivos = []
        if arquivos_upload:
            arquivos.extend(arquivos_upload)
        
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