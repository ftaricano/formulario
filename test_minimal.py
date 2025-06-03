import streamlit as st

st.set_page_config(
    page_title="Teste CPZ",
    page_icon="🛡️",
    layout="centered"
)

st.title("🛡️ Teste - Formulário CPZ")
st.success("✅ Aplicação iniciada com sucesso!")

st.write("**Verificações:**")
st.write("- ✅ Streamlit funcionando")
st.write("- ✅ Configuração de página OK")

try:
    import requests
    st.write("- ✅ Requests importado")
except ImportError:
    st.write("- ❌ Erro no requests")

try:
    import sendgrid
    st.write("- ✅ SendGrid importado")
except ImportError:
    st.write("- ❌ Erro no sendgrid")

try:
    from config import PLANOS_SEGURO
    st.write(f"- ✅ Config importado ({len(PLANOS_SEGURO)} planos)")
except ImportError as e:
    st.write(f"- ❌ Erro no config: {e}")

st.markdown("---")
st.info("Se você vê esta mensagem, o ambiente está funcionando!") 