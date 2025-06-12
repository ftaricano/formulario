#!/bin/bash

echo "🚀 Iniciando aplicação no ambiente virtual..."
echo ""

# Ativar ambiente virtual
source venv_formulario/bin/activate

# Verificar se as dependências estão instaladas
echo "📦 Verificando dependências..."
python -c "
try:
    import streamlit
    import requests
    import sendgrid
    import holidays
    import jinja2
    from src.utils.formatters import DateUtils
    print('✅ Todas as dependências estão OK!')
except ImportError as e:
    print(f'❌ Erro na importação: {e}')
    exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "🌐 Iniciando servidor Streamlit..."
    echo "📱 A aplicação estará disponível em: http://localhost:8501"
    echo ""
    streamlit run app.py
else
    echo "❌ Erro ao verificar dependências. Execute: pip install -r requirements.txt"
fi 