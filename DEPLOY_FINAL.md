# 🚀 Guia Final de Deploy - Formulário de Adesão Seguro

## 📋 **Checklist Pré-Deploy**

### ✅ **Arquivos Verificados e Prontos:**
- `app.py` - Aplicação principal (limpa, sem debug)
- `config.py` - Configurações do sistema
- `styles.css` - Estilos CSS
- `requirements.txt` - Dependências Python
- `logo.png` - Logo da empresa
- `.streamlit/config.toml` - Configurações Streamlit
- `.streamlit/secrets.toml.example` - Exemplo de configuração
- `.gitignore` - Arquivos ignorados pelo Git

### ✅ **Funcionalidades Testadas:**
- ✅ Formulário completo funcionando
- ✅ Validações de campos
- ✅ Busca automática CNPJ (ReceitaWS)
- ✅ Busca automática CEP (ViaCEP)
- ✅ Cálculo pró-rata automático
- ✅ Preservação de dados em caso de erro
- ✅ Interface responsiva
- ✅ Integração SendGrid pronta

---

## 🌐 **Opções de Deploy**

### **1. Streamlit Cloud (Recomendado - GRATUITO)**

#### **Passo 1: Preparar Repositório**
```bash
# Se ainda não tem Git configurado
git init
git add .
git commit -m "Deploy: Formulário de Adesão Seguro v1.0"

# Criar repositório no GitHub
# Fazer push do código
```

#### **Passo 2: Deploy no Streamlit Cloud**
1. Acesse: https://share.streamlit.io/
2. Conecte sua conta GitHub
3. Clique "New app"
4. Selecione o repositório
5. Main file path: `app.py`
6. Clique "Deploy!"

#### **Passo 3: Configurar Secrets**
No painel do Streamlit Cloud:
```toml
[sendgrid]
api_key = "SG.sua_api_key_sendgrid_real"
email_destino = "informe@cpzseg.com.br"
from_email = "seu_email_verificado@gmail.com"
from_name = "Grupo CPZ - Formulários"
```

### **2. Heroku (Alternativa)**

#### **Arquivos Necessários:**
```bash
# Criar Procfile
echo "web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0" > Procfile

# Deploy
heroku create nome-da-app
git push heroku main
```

### **3. VPS/Servidor Próprio**

#### **Instalação:**
```bash
# Instalar dependências
pip install -r requirements.txt

# Executar
streamlit run app.py --server.port=8501 --server.address=0.0.0.0
```

---

## 🔐 **Configuração de Email (SendGrid)**

### **Passo 1: Criar Conta SendGrid**
1. Acesse: https://sendgrid.com/
2. Crie conta gratuita (100 emails/dia)
3. Verifique seu email

### **Passo 2: Configurar API Key**
1. Vá em Settings > API Keys
2. Clique "Create API Key"
3. Nome: "Formulario-Seguro"
4. Permissions: "Full Access"
5. Copie a API Key (só aparece uma vez!)

### **Passo 3: Verificar Email Remetente**
1. Vá em Settings > Sender Authentication
2. Clique "Single Sender Verification"
3. Adicione seu email empresarial
4. Verifique no email recebido

### **Passo 4: Configurar Secrets**
```toml
[sendgrid]
api_key = "SG.sua_api_key_copiada_aqui"
email_destino = "informe@cpzseg.com.br"
from_email = "seu_email_verificado@gmail.com"
from_name = "Grupo CPZ - Formulários"
```

---

## 🧪 **Teste Final Antes do Deploy**

### **1. Teste Local**
```bash
streamlit run app.py
```

### **2. Checklist de Teste:**
- [ ] Formulário carrega corretamente
- [ ] Logo aparece centralizado
- [ ] Busca CNPJ funciona
- [ ] Busca CEP funciona
- [ ] Validações funcionam
- [ ] Dados são preservados em caso de erro
- [ ] Cálculo pró-rata está correto
- [ ] Email de teste funciona
- [ ] Interface responsiva (mobile/desktop)

### **3. Teste de Produção:**
- [ ] Configurar SendGrid real
- [ ] Testar envio de email real
- [ ] Verificar se emails chegam corretamente
- [ ] Testar em diferentes dispositivos

---

## 📱 **URLs e Acessos**

### **Após Deploy:**
- **URL da Aplicação:** `https://sua-app.streamlit.app/`
- **Painel Streamlit:** `https://share.streamlit.io/`
- **SendGrid Dashboard:** `https://app.sendgrid.com/`

### **Emails Configurados:**
- **Empresa:** `informe@cpzseg.com.br`
- **Remetente:** `seu_email_verificado@gmail.com`

---

## 🔧 **Manutenção e Monitoramento**

### **Logs e Monitoramento:**
- Streamlit Cloud: Logs automáticos no painel
- SendGrid: Activity Feed para emails
- Erros: Aparecem no painel do Streamlit

### **Atualizações:**
```bash
# Para atualizar a aplicação
git add .
git commit -m "Atualização: descrição"
git push origin main
# Deploy automático no Streamlit Cloud
```

### **Backup:**
- Código: Sempre no GitHub
- Configurações: Documentadas neste arquivo
- Dados: Emails salvos no SendGrid Activity

---

## 🎯 **Próximos Passos Após Deploy**

1. **Testar completamente** em produção
2. **Compartilhar URL** com equipe
3. **Monitorar emails** enviados
4. **Coletar feedback** dos usuários
5. **Implementar melhorias** conforme necessário

---

## 📞 **Suporte e Contatos**

### **Em caso de problemas:**
- **Streamlit:** https://docs.streamlit.io/
- **SendGrid:** https://docs.sendgrid.com/
- **GitHub:** Repositório do projeto

### **Configurações Importantes:**
- **Fuso Horário:** UTC-3 (São Paulo)
- **Vigência:** Até 31/12/2025
- **Planos:** 3 opções configuradas
- **APIs:** ReceitaWS (CNPJ) + ViaCEP (CEP)

---

## 🎉 **Aplicação Pronta para Produção!**

✅ **Código limpo e otimizado**  
✅ **Interface profissional**  
✅ **Funcionalidades completas**  
✅ **Integração de email configurada**  
✅ **Documentação completa**  
✅ **Pronto para deploy!**

**Boa sorte com o deploy! 🚀** 