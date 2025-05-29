#!/usr/bin/env python3
"""
Script de inicialização do servidor Streamlit
Mostra as URLs de acesso e inicia o servidor automaticamente
"""

import socket
import subprocess
import sys
import os
from datetime import datetime

def get_local_ip():
    """Obtém o IP local da máquina"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def mostrar_informacoes_servidor():
    """Mostra informações do servidor antes de iniciar"""
    local_ip = get_local_ip()
    porta = 8501
    timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    print("\n" + "="*70)
    print("🚀 INICIANDO SERVIDOR FORMULÁRIO CPZ")
    print("="*70)
    print(f"⏰ Horário: {timestamp}")
    print(f"📂 Diretório: {os.getcwd()}")
    print("="*70)
    print("🌐 ENDEREÇOS DE ACESSO:")
    print("="*70)
    print(f"📍 Local (Principal):  http://localhost:{porta}")
    print(f"📍 Local (Alternativo): http://127.0.0.1:{porta}")
    print(f"🌐 Rede Local:         http://{local_ip}:{porta}")
    print("="*70)
    print("📱 ACESSO MOBILE:")
    print(f"   WiFi (mesmo rede): http://{local_ip}:{porta}")
    print("="*70)
    print("🔧 COMANDOS ÚTEIS:")
    print("   • Ctrl+C para parar o servidor")
    print("   • Consulte ACESSO_URLS.md para mais detalhes")
    print("   • Use 'q' para sair do modo de visualização")
    print("="*70)
    print("🔄 Iniciando servidor Streamlit...")
    print("="*70 + "\n")

def verificar_dependencias():
    """Verifica se as dependências estão instaladas"""
    try:
        import streamlit
        import requests
        import sendgrid
        return True
    except ImportError as e:
        print(f"❌ Erro: Dependência não encontrada - {e}")
        print("💡 Execute: pip install -r requirements.txt")
        return False

def iniciar_servidor():
    """Inicia o servidor Streamlit"""
    if not verificar_dependencias():
        return False
    
    mostrar_informacoes_servidor()
    
    try:
        # Comando para iniciar o Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.address", "0.0.0.0",  # Permite acesso externo
            "--browser.gatherUsageStats", "false"  # Desabilita coleta de dados
        ]
        
        # Executa o comando
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n" + "="*70)
        print("🛑 SERVIDOR PARADO PELO USUÁRIO")
        print("="*70)
        print("✅ Servidor encerrado com sucesso!")
        print("="*70 + "\n")
    except Exception as e:
        print(f"\n❌ Erro ao iniciar servidor: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Verifica se está no diretório correto
    if not os.path.exists("app.py"):
        print("❌ Erro: arquivo app.py não encontrado!")
        print("💡 Execute este script no diretório do projeto.")
        sys.exit(1)
    
    # Inicia o servidor
    iniciar_servidor() 