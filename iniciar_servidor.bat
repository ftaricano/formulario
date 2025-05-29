@echo off
chcp 65001 >nul
title Servidor Formulário CPZ

echo.
echo ================================================================
echo 🚀 INICIANDO SERVIDOR FORMULÁRIO CPZ
echo ================================================================
echo ⏰ Horário: %date% %time%
echo 📂 Diretório: %cd%
echo ================================================================
echo 🌐 ENDEREÇOS DE ACESSO:
echo ================================================================
echo 📍 Local (Principal):   http://localhost:8501
echo 📍 Local (Alternativo): http://127.0.0.1:8501
echo 🌐 Rede Local:          http://[SEU_IP]:8501
echo ================================================================
echo 📱 ACESSO MOBILE:
echo    WiFi (mesma rede): Descubra seu IP e use http://[IP]:8501
echo ================================================================
echo 🔧 COMANDOS ÚTEIS:
echo    • Ctrl+C para parar o servidor
echo    • Consulte ACESSO_URLS.md para mais detalhes
echo ================================================================
echo 🔄 Iniciando servidor Streamlit...
echo ================================================================
echo.

REM Verifica se o arquivo app.py existe
if not exist "app.py" (
    echo ❌ Erro: arquivo app.py não encontrado!
    echo 💡 Execute este script no diretório do projeto.
    pause
    exit /b 1
)

REM Inicia o servidor Streamlit
python -m streamlit run app.py --server.port 8501 --server.address 0.0.0.0 --browser.gatherUsageStats false

echo.
echo ================================================================
echo 🛑 SERVIDOR PARADO
echo ================================================================
echo ✅ Servidor encerrado com sucesso!
echo ================================================================
pause 