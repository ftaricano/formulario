import streamlit as st
from typing import Tuple, List, Dict, Any
from src.controllers.form_controller import FormularioController, EquipamentosController, PlanoController
from src.managers.state_manager import FormularioStateManager
from src.utils.formatters import ValueFormatter
from config import DATA_FINAL_VIGENCIA
from datetime import datetime, timedelta

class EnhancedFormRenderer:
    """Renderizador aprimorado de formulários com separação de responsabilidades"""
    
    def __init__(self, controller: FormularioController):
        self.controller = controller
        self.equipamentos_controller = EquipamentosController(controller.state_manager)
    
    def render_field_with_validation(self, label: str, field_name: str, 
                                   validation_type: str = "text", 
                                   help_text: str = "", placeholder: str = "",
                                   required: bool = False) -> str:
        """Renderiza campo com validação visual integrada"""
        # Obter valor atual (com fallback para dados preservados)
        current_value = self.controller.state_manager.session_manager.obter_valor(field_name, "")
        
        # Adicionar indicador de obrigatório
        display_label = f"{label} *" if required else label
        
        # Renderizar campo
        value = st.text_input(
            display_label,
            value=current_value,
            help=help_text,
            placeholder=placeholder,
            key=field_name
        )
        
        # Validação em tempo real (opcional - pode ser removida se causar muitos reruns)
        if value and validation_type != "text":
            self._mostrar_validacao_tempo_real(value, validation_type)
        
        return value
    
    def _mostrar_validacao_tempo_real(self, value: str, validation_type: str):
        """Mostra feedback de validação em tempo real"""
        from src.validators.form_validators import FormValidator
        
        if validation_type == "cpf" and not FormValidator.validar_cpf(value):
            st.caption("❌ Formato de CPF inválido")
        elif validation_type == "cnpj" and not FormValidator.validar_cnpj(value):
            st.caption("❌ Formato de CNPJ inválido")
        elif validation_type == "email" and not FormValidator.validar_email(value):
            st.caption("❌ Formato de email inválido")
        elif validation_type == "cep" and not FormValidator.validar_cep(value):
            st.caption("❌ Formato de CEP inválido")
    
    def render_api_search_field(self, label: str, field_name: str, 
                               search_type: str, help_text: str = "", 
                               placeholder: str = "") -> Tuple[str, bool]:
        """Renderiza campo com botão de busca via API"""
        col1, col2 = st.columns([5, 1])
        
        with col1:
            value = self.render_field_with_validation(
                label, field_name, search_type, help_text, placeholder, required=True
            )
        
        with col2:
            st.markdown("<br>", unsafe_allow_html=True)
            button_pressed = st.button("🔍", key=f"buscar_{field_name}", use_container_width=True)
        
        # Processar busca se botão foi clicado
        if button_pressed and value:
            self._processar_busca_api(value, search_type)
        
        return value, button_pressed
    
    def _processar_busca_api(self, value: str, search_type: str):
        """Processa busca via API com feedback adequado"""
        if search_type == "cnpj":
            with st.spinner("🔍 Buscando dados do CNPJ..."):
                sucesso, resultado = self.controller.buscar_dados_cnpj(value)
                if sucesso:
                    st.success(f"✅ CNPJ encontrado: {resultado}")
                    st.rerun()
                else:
                    st.error(f"❌ {resultado}")
                    
        elif search_type == "cep":
            with st.spinner("🔍 Buscando endereço..."):
                sucesso, endereco, erro = self.controller.buscar_dados_cep(value)
                if sucesso:
                    st.success("✅ Endereço encontrado e preenchido automaticamente")
                    st.rerun()
                else:
                    st.error(f"❌ {erro}")

class EnhancedEquipamentosSection:
    """Seção aprimorada de equipamentos com controlador integrado"""
    
    def __init__(self, equipamentos_controller: EquipamentosController):
        self.controller = equipamentos_controller
    
    def render(self) -> List[Dict]:
        """Renderiza seção completa de equipamentos"""
        st.markdown("")
        self._render_header()
        
        # Obter equipamentos atuais
        equipamentos = self.controller.obter_equipamentos_atuais()
        
        # Renderizar cabeçalhos
        self._render_table_headers()
        
        # Renderizar linhas de equipamentos
        for i, equipamento in enumerate(equipamentos):
            self._render_equipamento_row(i, equipamento)
        
        # Botões de ação
        self._render_action_buttons()
        
        # Resumo
        self._render_resumo()
        
        return equipamentos
    
    def _render_header(self):
        """Renderiza cabeçalho da seção"""
        st.markdown("""
                    <div class="section-title">▪ Relação de Bens e Equipamentos sem Nota Fiscal a serem Incluídos</div>
        <div class="section-description">
            Adicione todos os bens e equipamentos sem nota fiscal a serem incluídos no seguro. 
            Use o botão ➕ para adicionar mais itens.
        </div>
        """, unsafe_allow_html=True)
    
    def _render_table_headers(self):
        """Renderiza cabeçalhos da tabela"""

        col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
        with col1:
            st.markdown("**Tipo*** 📝")
        with col2:
            st.markdown("**Descrição*** 📄")
        with col3:
            st.markdown("**Valor (R$)*** 💰")
        with col4:
            st.markdown("**Ação** 🛠️")
    
    def _render_equipamento_row(self, index: int, equipamento: Dict):
        """Renderiza linha individual de equipamento"""
        col1, col2, col3, col4 = st.columns([3, 4, 2, 1])
        
        with col1:
            tipo = st.text_input(
                f"Tipo {index+1}",
                value=equipamento.get("tipo", ""),
                placeholder="Ex: Geladeira, Micro-ondas",
                key=f"tipo_equip_{index}",
                label_visibility="collapsed"
            )
            # Atualizar no session_state
            import streamlit as st
            st.session_state.equipamentos[index]["tipo"] = tipo
        
        with col2:
            descricao = st.text_input(
                f"Descrição {index+1}",
                value=equipamento.get("descricao", ""),
                placeholder="Descrição detalhada do bem",
                key=f"desc_equip_{index}",
                label_visibility="collapsed"
            )
            st.session_state.equipamentos[index]["descricao"] = descricao
        
        with col3:
            valor = st.text_input(
                f"Valor {index+1}",
                value=equipamento.get("valor", ""),
                placeholder="1.000,00",
                key=f"valor_equip_{index}",
                label_visibility="collapsed"
            )
            st.session_state.equipamentos[index]["valor"] = valor
        
        with col4:
            equipamentos = self.controller.obter_equipamentos_atuais()
            if len(equipamentos) > 1:
                if st.button("🗑️", key=f"remove_equip_{index}", 
                           help="Remover este item", use_container_width=True):
                    if self.controller.remover_equipamento(index):
                        st.rerun()
    
    def _render_action_buttons(self):
        """Renderiza botões de ação"""
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
            if st.button("Adicionar Outro Equipamento", key="add_equipamento", 
                        use_container_width=True, type="secondary"):
                if self.controller.adicionar_equipamento():
                    st.rerun()
    
    def _render_resumo(self):
        """Renderiza resumo dos equipamentos preenchidos"""
        resumo = self.controller.obter_resumo_equipamentos()
        
        if resumo:
            st.markdown("**▪ Resumo dos Itens Cadastrados:**")
            for i, eq in enumerate(resumo, 1):
                tipo = eq.get('tipo', 'N/A')
                descricao = eq.get('descricao', 'N/A')
                valor = eq.get('valor', 'N/A')
                valor_formatado = f"R$ {valor}" if valor and valor != 'N/A' else 'N/A'
                
                # Ícone baseado no tipo
                icone = "🔧" if "eletr" in tipo.lower() else "🏠" if "móvel" in tipo.lower() else "📦"
                
                st.markdown(f"{icone} **{i}.** {tipo} - {descricao} - {valor_formatado}")

class EnhancedPlanosSection:
    """Seção aprimorada de seleção de planos"""
    
    @staticmethod
    def render() -> str:
        """Renderiza seção de seleção de planos"""
        st.markdown("""
        <div class="section-title">▪ Seleção do Plano de Seguro</div>
        <div class="section-description">
            Escolha uma das opções de cobertura disponíveis. 
            O valor será calculado proporcionalmente até 31/12/2024.
        </div>
        """, unsafe_allow_html=True)
        
        # Renderizar tabela de coberturas primeiro
        EnhancedPlanosSection._render_coverage_table()
        
        # Seleção de plano
        opcoes = PlanoController.obter_opcoes_formatadas()
        
        plano_selecionado = st.radio(
            "**🛡️ Escolha seu plano:**",
            options=opcoes,
            key="plano_radio",
            horizontal=True,
            help="Selecione o plano que melhor atende às suas necessidades"
        )
        
        return plano_selecionado
    
    @staticmethod
    def _render_coverage_table():
        """Renderiza tabela de coberturas"""
        st.markdown("**📋 Coberturas Incluídas:**")
        st.markdown("""
        | 🛡️ **Coberturas** | **Opção 1** | **Opção 2** | **Opção 3** | **💰 Franquia** |
        |-------------------|-------------|-------------|-------------|-----------------|
        | 🔥 **Incêndio, Raio e Explosão** | R$ 250.000 | R$ 400.000 | R$ 700.000 | R$ 30.000 |
        | 🌊 **Alagamento** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 15.000 |
        | ⚡ **Danos Elétricos** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
        | 🔨 **Pequenas Obras** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 5.000 |
        | 🏠 **Perda/Pgto Aluguel (6m)** | R$ 20.000 | R$ 30.000 | R$ 40.000 | ✅ Não Há |
        | 🪟 **Vidros** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
        | 👥 **Tumultos** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 5.000 |
        | 💨 **Vendaval** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 10.000 |
        """)

class ValueDisplaySection:
    """Seção para exibição de valores calculados"""
    
    @staticmethod
    def render_calculation(plano_selecionado: str, controller: FormularioController) -> float:
        """Renderiza cálculo de valores"""
        if not plano_selecionado:
            return 0.0
        
        plano_nome = controller.obter_plano_formatado(plano_selecionado)
        dias_restantes, premio_pro_rata = controller.calcular_premio_pro_rata(plano_nome)
        
        # Seção de vigência
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.1) 100%);
                    border-radius: 16px; padding: 20px; margin: 20px 0;
                    border: 1px solid rgba(59, 130, 246, 0.2);">
        """, unsafe_allow_html=True)
        
        st.markdown("**📅 Período de Vigência:**")
        data_inclusao = datetime.now() + timedelta(days=1)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🗓️ Início", data_inclusao.strftime('%d/%m/%Y'))
        with col2:
            st.metric("🏁 Fim", DATA_FINAL_VIGENCIA.strftime('%d/%m/%Y'))
        with col3:
            st.metric("⏰ Dias", f"{dias_restantes} dias")
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Valor destacado
        st.markdown(f"""
        <div class="total-value-section-black">
            <h2>Valor Total: {ValueFormatter.formatar_valor_real(premio_pro_rata)}</h2>
            <p>Valor proporcional calculado automaticamente</p>
        </div>
        """, unsafe_allow_html=True)
        
        return premio_pro_rata 