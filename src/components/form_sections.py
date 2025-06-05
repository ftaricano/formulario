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
        """Renderiza campo de texto com botão de busca"""
        col1, col2 = st.columns([5, 1])
        
        with col1:
            value = st.text_input(
                label,
                value=st.session_state.get(field_name, ''),
                help=help_text,
                placeholder=placeholder,
                key=field_name
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            button_key = f"buscar_{field_name}"
            button_pressed = st.button("🔍", key=button_key, use_container_width=True)
        
        return value, button_pressed
    
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
            "▪ Relação de Bens e Equipamentos Sem Nota Fiscal (Opcional)",
            "Adicione bens e equipamentos sem nota fiscal, caso existam. Use os botões para adicionar ou remover itens."
        )
        
        # Inicializar lista de equipamentos
        if 'equipamentos' not in st.session_state:
            st.session_state.equipamentos = [{"tipo": "", "descricao": "", "valor": ""}]
        
        # Cabeçalhos da tabela
        col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
        with col1:
            st.markdown("**Tipo**")
        with col2:
            st.markdown("**Descrição**")
        with col3:
            st.markdown("**Valor (R$)**")
        
        # Renderizar equipamentos
        for i, equipamento in enumerate(st.session_state.equipamentos):
            col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
            
            with col1:
                tipo = st.text_input(
                    f"Tipo {i+1}",
                    value=equipamento.get("tipo", ""),
                    placeholder="Ex: Eletrônico, Móvel",
                    key=f"tipo_equip_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.equipamentos[i]["tipo"] = tipo
            
            with col2:
                descricao = st.text_input(
                    f"Descrição {i+1}",
                    value=equipamento.get("descricao", ""),
                    placeholder="Descrição detalhada",
                    key=f"desc_equip_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.equipamentos[i]["descricao"] = descricao
            
            with col3:
                valor = st.text_input(
                    f"Valor {i+1}",
                    value=equipamento.get("valor", ""),
                    placeholder="1.000,00",
                    key=f"valor_equip_{i}",
                    label_visibility="collapsed"
                )
                st.session_state.equipamentos[i]["valor"] = valor
            
            with col4:
                # Só mostrar botão de remover se houver mais de um item
                if len(st.session_state.equipamentos) > 1:
                    if st.button("🗑️", key=f"remove_equip_{i}", 
                               help=f"Remover item {i+1}", 
                               use_container_width=True):
                        EquipamentosSection._remover_equipamento(i)
                        st.rerun()
                else:
                    st.markdown("")  # Espaço vazio quando só há um item
        
        # Botões de controle
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col2:
            if st.button("➕ Adicionar Item", key="add_equipamento", use_container_width=True):
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
        """Manipula busca de CNPJ"""
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
        """Manipula busca de CEP"""
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