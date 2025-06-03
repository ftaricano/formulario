#!/usr/bin/env python3
"""
Health Check - Formulário CPZ
Verifica se todos os componentes estão funcionando
"""

import sys
import os

def check_environment():
    print("🔍 DIAGNÓSTICO DO AMBIENTE")
    print("=" * 50)
    
    # Python version
    print(f"Python: {sys.version}")
    print(f"Plataforma: {sys.platform}")
    
    # Check imports
    try:
        import streamlit as st
        print(f"✅ Streamlit: {st.__version__}")
    except ImportError as e:
        print(f"❌ Streamlit: {e}")
        return False
    
    try:
        import requests
        print(f"✅ Requests: {requests.__version__}")
    except ImportError as e:
        print(f"❌ Requests: {e}")
        return False
    
    try:
        import sendgrid
        print(f"✅ SendGrid: {sendgrid.__version__}")
    except ImportError as e:
        print(f"❌ SendGrid: {e}")
        return False
    
    # Check files
    files_to_check = [
        'app.py',
        'config.py', 
        'styles.css',
        'logo.png',
        'requirements.txt'
    ]
    
    print("\n📁 ARQUIVOS:")
    for file in files_to_check:
        if os.path.exists(file):
            size = os.path.getsize(file)
            print(f"✅ {file} ({size} bytes)")
        else:
            print(f"❌ {file} - AUSENTE")
            return False
    
    # Check config
    try:
        from config import PLANOS_SEGURO, APP_CONFIG
        print(f"\n⚙️ CONFIGURAÇÕES:")
        print(f"✅ Planos carregados: {len(PLANOS_SEGURO)}")
        print(f"✅ App config: {APP_CONFIG['page_title']}")
    except Exception as e:
        print(f"❌ Config: {e}")
        return False
    
    print("\n🎉 TODOS OS TESTES PASSARAM!")
    return True

if __name__ == "__main__":
    success = check_environment()
    sys.exit(0 if success else 1) 