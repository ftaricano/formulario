import streamlit as st
from typing import Tuple, List, Dict, Any
from src.models.formulario import Equipamento
from src.services.api_service import ApiService
from src.validators.form_validators import FormValidator

class FormSectionRenderer:
    """Classe para renderização de seções do formulário"""
    
    @staticmethod
    def render_field_with_search(label: str, field_name: str, 
                                help_text: str = "", placeholder: str = "") -> Tuple[str, bool]:
        """Renderiza campo de texto com busca automática silenciosa"""
        # Indicação visual sutil durante a busca
        search_status_key = f"{field_name}_searching"
        is_searching = st.session_state.get(search_status_key, False)
        
        # Aplicar classe CSS para feedback visual sutil quando buscando
        if is_searching:
            st.markdown("""
            <style>
            div[data-testid="stTextInput"] input[aria-label*="%s"] {
                border-left: 3px solid #28a745 !important;
                transition: border-left-color 0.3s ease;
            }
            </style>
            """ % field_name.upper(), unsafe_allow_html=True)
        
        # Campo de texto normal
        value = st.text_input(
            label,
            value=st.session_state.get(field_name, ''),
            help=help_text,
            placeholder=placeholder,
            key=field_name
        )
        
        # Verificar se o valor mudou e fazer busca automática
        search_triggered = False
        last_value_key = f"{field_name}_last_value"
        
        # Se o valor mudou desde a última verificação
        if value != st.session_state.get(last_value_key, ''):
            st.session_state[last_value_key] = value
            
            # Limpar indicador de busca anterior quando o valor muda
            if field_name == 'cnpj':
                # Remover flags de busca anterior para permitir nova busca
                keys_to_remove = [k for k in st.session_state.keys() if k.startswith('cnpj_searched_')]
                for key in keys_to_remove:
                    del st.session_state[key]
                # Limpar dados da busca anterior
                if 'razao_social_busca' in st.session_state:
                    del st.session_state['razao_social_busca']
            elif field_name == 'cep':
                # Remover flags de busca anterior para permitir nova busca
                keys_to_remove = [k for k in st.session_state.keys() if k.startswith('cep_searched_')]
                for key in keys_to_remove:
                    del st.session_state[key]
                # Limpar dados da busca anterior
                campos_busca = ['logradouro_busca', 'bairro_busca', 'cidade_busca', 'estado_busca']
                for campo in campos_busca:
                    if campo in st.session_state:
                        del st.session_state[campo]
            
            # Se o campo tem valor e é válido, fazer busca automática
            if value.strip():
                if field_name == 'cnpj' and FormValidator.validar_cnpj(value):
                    search_triggered = True
                    st.session_state[search_status_key] = True
                    ApiSearchHandler.handle_cnpj_search_auto(value)
                elif field_name == 'cep' and FormValidator.validar_cep(value):
                    search_triggered = True
                    st.session_state[search_status_key] = True
                    ApiSearchHandler.handle_cep_search_auto(value)
            else:
                # Limpar status de busca se campo ficar vazio
                if search_status_key in st.session_state:
                    del st.session_state[search_status_key]
        
        return value, search_triggered
    
    @staticmethod
    def render_section_header(title: str, description: str):
        """Renderiza cabeçalho de seção"""
        st.markdown(f"""
        <div class="form-section">
            <div class="section-title">{title}</div>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem; font-size: 0.95rem;">
                {description}
            </p>
        </div>
        """, unsafe_allow_html=True)

class EquipamentosSection:
    """Componente especializado para seção de equipamentos"""
    
    @staticmethod
    def render() -> List[Equipamento]:
        """Renderiza seção completa de equipamentos"""
        st.markdown("")
        FormSectionRenderer.render_section_header(
            "▪ Relação de Bens e Equipamentos sem Nota Fiscal a serem Incluídos",
            "Adicione bens e equipamentos sem nota fiscal, caso existam."
        )
        
        # Inicializar lista de equipamentos
        if 'equipamentos' not in st.session_state:
            st.session_state.equipamentos = [{"tipo": "", "descricao": "", "valor": ""}]
        
        # CSS para layout intercalado único
        st.markdown("""
        <style>
        /* Layout intercalado para todas as telas */
        .equipamento-mobile-item {
            border: 1px solid #e0e0e0 !important;
            border-radius: 8px !important;
            padding: 0 12px 12px 12px !important;
            margin-bottom: 10px !important;
            background: #fafafa !important;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
        }
        
        /* Remover espaçamento acima do cabeçalho do equipamento */
        .equipamento-mobile-item .stMarkdown:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .equipamento-mobile-item .stMarkdown:first-child p {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .equipamento-mobile-item > div:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .equipamento-mobile-item > * {
            margin-top: 0 !important;
        }
        
        .equipamento-mobile-item > *:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        /* CSS específico para remover espaçamento do Streamlit */
        .equipamento-mobile-item [data-testid="stMarkdown"] {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .equipamento-mobile-item [data-testid="stMarkdown"]:first-child {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .equipamento-mobile-item [data-testid="stMarkdown"] p {
            margin-top: 0 !important;
            padding-top: 0 !important;
        }
        
        .mobile-field-group {
            margin-bottom: 4px !important;
        }
        
        .mobile-field-label {
            font-weight: bold !important;
            font-size: 0.85rem !important;
            color: #333 !important;
            margin-bottom: 1px !important;
            display: block !important;
            background: transparent !important;
            padding: 0 !important;
            border-radius: 0 !important;
        }
        
        .mobile-remove-button {
            text-align: center !important;
            margin-top: 10px !important;
            padding-top: 8px !important;
            border-top: 1px solid #e0e0e0 !important;
        }
        
        /* Diminuir espaçamento dos inputs */
        .mobile-field-group .stTextInput > div {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        
        .mobile-field-group .stTextInput input {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
            padding: 0.4rem !important;
        }
        
        /* Remover espaçamento extra entre elementos */
        .mobile-field-group .stTextInput {
            margin-bottom: 0 !important;
            margin-top: 0 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Renderizar equipamentos - Layout intercalado único
        for i, equipamento in enumerate(st.session_state.equipamentos):
            st.markdown(f'<div class="equipamento-mobile-item">', unsafe_allow_html=True)
            
            # Cabeçalho do item
            st.markdown(f'<div style="margin:0; padding:12px 0 8px 0; font-weight:bold;">Equipamento {i+1}</div>', unsafe_allow_html=True)
            
            # Campo Tipo
            st.markdown('<div class="mobile-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="mobile-field-label">Tipo</div>', unsafe_allow_html=True)
            tipo = st.text_input(
                f"Tipo {i+1}",
                value=equipamento.get("tipo", ""),
                placeholder="Ex: Geladeira, Microondas, etc.",
                key=f"tipo_equip_{i}",
                label_visibility="collapsed"
            )
            st.session_state.equipamentos[i]["tipo"] = tipo
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Campo Descrição
            st.markdown('<div class="mobile-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="mobile-field-label">Descrição</div>', unsafe_allow_html=True)
            descricao = st.text_input(
                f"Descrição {i+1}",
                value=equipamento.get("descricao", ""),
                placeholder="Marca/Modelo",
                key=f"desc_equip_{i}",
                label_visibility="collapsed"
            )
            st.session_state.equipamentos[i]["descricao"] = descricao
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Campo Valor
            st.markdown('<div class="mobile-field-group">', unsafe_allow_html=True)
            st.markdown('<div class="mobile-field-label">Valor (R$)</div>', unsafe_allow_html=True)
            valor = st.text_input(
                f"Valor {i+1}",
                value=equipamento.get("valor", ""),
                placeholder="R$ 1.000,00",
                key=f"valor_equip_{i}",
                label_visibility="collapsed"
            )
            st.session_state.equipamentos[i]["valor"] = valor
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Botão remover
            if len(st.session_state.equipamentos) > 1:
                st.markdown('<div class="mobile-remove-button">', unsafe_allow_html=True)
                if st.button(f"🗑️ Remover Equipamento {i+1}", key=f"remove_equip_{i}", 
                           help=f"Remover item {i+1}", use_container_width=True):
                    EquipamentosSection._remover_equipamento(i)
                    st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
            
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Botões de controle
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            st.markdown("""
            <style>
            div[data-testid="stButton"] > button {
                white-space: nowrap !important;
                width: 100% !important;
                min-width: 220px !important;
                padding: 0.5rem 0.8rem !important;
                font-size: 0.9rem !important;
                overflow: hidden !important;
            }
            </style>
            """, unsafe_allow_html=True)
            if st.button("Adicionar Outro Equipamento", key="add_equipamento", use_container_width=True):
                EquipamentosSection._adicionar_equipamento()
                st.rerun()
        
        with col3:
            if len(st.session_state.equipamentos) > 1:
                if st.button("🧹 Limpar Todos", key="clear_equipamentos", 
                           use_container_width=True, type="secondary"):
                    st.session_state.equipamentos = [{"tipo": "", "descricao": "", "valor": ""}]
                    st.rerun()
        
        # Converter para objetos Equipamento
        return [
            Equipamento(
                tipo=eq.get('tipo', ''),
                descricao=eq.get('descricao', ''),
                valor=eq.get('valor', '')
            ) for eq in st.session_state.equipamentos
        ]
    
    @staticmethod
    def _adicionar_equipamento():
        """Adiciona novo equipamento vazio"""
        st.session_state.equipamentos.append({"tipo": "", "descricao": "", "valor": ""})
    
    @staticmethod
    def _remover_equipamento(index: int):
        """Remove equipamento por índice"""
        if len(st.session_state.equipamentos) > 1:
            st.session_state.equipamentos.pop(index)
    
    @staticmethod
    def _mostrar_resumo():
        """Mostra resumo dos equipamentos preenchidos"""
        equipamentos_preenchidos = [
            eq for eq in st.session_state.equipamentos 
            if eq.get('tipo', '').strip()
        ]
        
        if equipamentos_preenchidos:
            st.markdown("**▪ Resumo dos Itens Cadastrados:**")
            for i, eq in enumerate(equipamentos_preenchidos, 1):
                tipo = eq.get('tipo', 'N/A')
                descricao = eq.get('descricao', 'N/A')
                valor = eq.get('valor', 'N/A')
                valor_formatado = f"R$ {valor}" if valor and valor != 'N/A' else 'N/A'
                st.markdown(f"**{i}.** {tipo} - {descricao} - {valor_formatado}")

class ApiSearchHandler:
    """Handler para buscas automáticas via API"""
    
    @staticmethod
    def handle_cnpj_search(cnpj: str, button_pressed: bool):
        """Manipula busca de CNPJ (mantido para compatibilidade)"""
        if button_pressed and cnpj:
            if FormValidator.validar_cnpj(cnpj):
                with st.spinner("▪ Buscando dados do CNPJ..."):
                    razao_social = ApiService.buscar_cnpj(cnpj)
                    if razao_social:
                        # Usar uma chave diferente para evitar conflito
                        st.session_state['razao_social_busca'] = razao_social
                        st.success(f"✓ CNPJ encontrado: {razao_social}")
                        st.rerun()
                    else:
                        st.warning("⚠ CNPJ não encontrado na base de dados")
            else:
                st.error("✗ CNPJ deve estar no formato 00.000.000/0000-00")
    
    @staticmethod
    def handle_cep_search(cep: str, button_pressed: bool):
        """Manipula busca de CEP (mantido para compatibilidade)"""
        if button_pressed and cep:
            if FormValidator.validar_cep(cep):
                with st.spinner("▪ Buscando endereço..."):
                    endereco = ApiService.buscar_cep(cep)
                    
                    if endereco:
                        # Armazenar dados do endereço com chaves específicas
                        for campo, valor in endereco.items():
                            st.session_state[f'{campo}_busca'] = valor
                        
                        st.success("✓ Endereço encontrado e preenchido automaticamente")
                        st.rerun()
                    else:
                        st.warning("⚠ CEP não encontrado")
            else:
                st.error("✗ CEP deve estar no formato 00000-000")
    
    @staticmethod
    def handle_cnpj_search_auto(cnpj: str):
        """Manipula busca automática de CNPJ de forma imperceptível"""
        # Verificar se já foi buscado para evitar buscas repetidas
        search_key = f"cnpj_searched_{cnpj}"
        if st.session_state.get(search_key, False):
            return
            
        if cnpj and FormValidator.validar_cnpj(cnpj):
            # Busca totalmente silenciosa - sem spinners ou mensagens
            razao_social = ApiService.buscar_cnpj(cnpj)
            if razao_social:
                st.session_state['razao_social_busca'] = razao_social
                st.session_state[search_key] = True
            else:
                st.session_state[search_key] = True
            
            # Limpar status de busca
            if 'cnpj_searching' in st.session_state:
                del st.session_state['cnpj_searching']
            
            # Recarregar apenas se encontrou dados
            if razao_social:
                st.rerun()
    
    @staticmethod
    def handle_cep_search_auto(cep: str):
        """Manipula busca automática de CEP de forma imperceptível"""
        # Verificar se já foi buscado para evitar buscas repetidas
        search_key = f"cep_searched_{cep}"
        if st.session_state.get(search_key, False):
            return
            
        if cep and FormValidator.validar_cep(cep):
            # Busca totalmente silenciosa - sem spinners ou mensagens
            endereco = ApiService.buscar_cep(cep)
            
            if endereco:
                # Armazenar dados do endereço com chaves específicas
                for campo, valor in endereco.items():
                    st.session_state[f'{campo}_busca'] = valor
                
                st.session_state[search_key] = True
            else:
                st.session_state[search_key] = True
            
            # Limpar status de busca
            if 'cep_searching' in st.session_state:
                del st.session_state['cep_searching']
            
            # Recarregar apenas se encontrou dados
            if endereco:
                st.rerun() 