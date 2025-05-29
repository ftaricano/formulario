# 🌐 URLs de Acesso - Formulário CPZ

## 📍 Endereços Locais

### Desenvolvimento Local
- **URL Principal:** http://localhost:8501
- **URL Alternativa:** http://127.0.0.1:8501

### Rede Local (Outros dispositivos na mesma rede)
- **URL da Rede:** http://[SEU_IP_LOCAL]:8501
  - Para descobrir seu IP: `ipconfig getifaddr en0` (Mac) ou `ipconfig` (Windows)

## 🚀 Como Iniciar o Servidor

### Opção 1: Scripts Automáticos (RECOMENDADO)

**macOS/Linux:**
```bash
# Script Python com informações detalhadas
python iniciar_servidor.py

# Ou tornar executável e rodar diretamente
./iniciar_servidor.py
```

**Windows:**
```cmd
# Duplo clique no arquivo ou execute no terminal
iniciar_servidor.bat
```

### Opção 2: Comando Manual
```bash
# Comando básico
streamlit run app.py

# Comando com porta específica
streamlit run app.py --server.port 8501

# Comando para permitir acesso externo
streamlit run app.py --server.address 0.0.0.0
```

## 📱 Acesso Mobile

Para acessar pelo celular na mesma rede WiFi:
1. Descubra o IP do seu computador
2. Use: http://[IP_DO_COMPUTADOR]:8501

## 🔧 Comandos Úteis

```bash
# Verificar se a porta está em uso
lsof -i :8501

# Parar processo na porta (se necessário)
kill -9 $(lsof -t -i:8501)

# Verificar IP local (Mac)
ipconfig getifaddr en0

# Verificar IP local (Windows)
ipconfig
```

## 📋 Status do Servidor

Quando usar os scripts automáticos, você verá:
```
🚀 INICIANDO SERVIDOR FORMULÁRIO CPZ
================================================================
⏰ Horário: [DATA/HORA]
📂 Diretório: [CAMINHO_DO_PROJETO]
================================================================
🌐 ENDEREÇOS DE ACESSO:
================================================================
📍 Local (Principal):  http://localhost:8501
📍 Local (Alternativo): http://127.0.0.1:8501
🌐 Rede Local:         http://[SEU_IP]:8501
================================================================
📱 ACESSO MOBILE:
   WiFi (mesmo rede): http://[SEU_IP]:8501
================================================================
```

## 🎯 Vantagens dos Scripts Automáticos

✅ **Mostram automaticamente todas as URLs de acesso**  
✅ **Verificam dependências antes de iniciar**  
✅ **Configuram o servidor para acesso externo**  
✅ **Exibem informações úteis no console**  
✅ **Facilitam o acesso mobile**  

## 🔍 Solução de Problemas

### Porta já em uso
```bash
# Verificar processos na porta 8501
lsof -i :8501

# Parar processo específico
kill -9 [PID]
```

### Dependências não instaladas
```bash
# Instalar dependências
pip install -r requirements.txt
```

### Acesso negado (Windows)
- Execute o terminal como Administrador
- Ou use: `python iniciar_servidor.py`

---
*Arquivo atualizado automaticamente - Projeto Formulário CPZ* 