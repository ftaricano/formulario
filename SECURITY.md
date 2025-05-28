# 🔒 Configuração de Segurança

## ⚠️ IMPORTANTE - DADOS SENSÍVEIS

**NUNCA** commite credenciais no repositório! Este projeto foi configurado para usar variáveis de ambiente.

## 🛡️ Configuração Segura

### 1. **Arquivo `.env` (Local)**
Crie um arquivo `.env` na raiz do projeto com suas credenciais reais:

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite com suas credenciais reais
EMAIL_REMETENTE=seu_email_real@empresa.com
EMAIL_SENHA=sua_senha_de_app_real
EMAIL_EMPRESA=email_destino_real@empresa.com
MODO_TESTE=false
```

### 2. **Senhas de App (Recomendado)**
Para maior segurança, use **senhas de app** ao invés da senha normal:

#### **Gmail:**
1. Ative a verificação em 2 etapas
2. Vá em: Conta Google → Segurança → Senhas de app
3. Gere uma senha específica para este app

#### **Outlook/Office365:**
1. Ative a verificação em 2 etapas
2. Vá em: Conta Microsoft → Segurança → Senhas de app
3. Gere uma senha específica para este app

### 3. **Streamlit Cloud (Produção)**
Para deploy no Streamlit Cloud, use o arquivo `secrets.toml`:

```toml
# .streamlit/secrets.toml
EMAIL_REMETENTE = "seu_email@empresa.com"
EMAIL_SENHA = "sua_senha_de_app"
EMAIL_EMPRESA = "email_destino@empresa.com"
MODO_TESTE = false
```

### 4. **Verificação de Segurança**
Antes de fazer commit, verifique:

```bash
# Verificar se .env está no .gitignore
git check-ignore .env

# Verificar se não há credenciais no código
grep -r "senha\|password\|@" --include="*.py" .
```

## 🚨 Se Você Já Commitou Credenciais

### **Ação Imediata:**
1. **Mude todas as senhas** imediatamente
2. **Remova o histórico** do Git:

```bash
# Remover arquivo do histórico
git filter-branch --force --index-filter \
'git rm --cached --ignore-unmatch config.py' \
--prune-empty --tag-name-filter cat -- --all

# Forçar push
git push origin --force --all
```

3. **Regenere senhas de app**
4. **Configure variáveis de ambiente**

## ✅ Boas Práticas

- ✅ Use sempre variáveis de ambiente
- ✅ Mantenha `.env` no `.gitignore`
- ✅ Use senhas de app específicas
- ✅ Ative modo teste por padrão
- ✅ Documente configurações sem expor dados
- ❌ NUNCA commite credenciais
- ❌ NUNCA use senhas principais
- ❌ NUNCA hardcode dados sensíveis

## 📞 Suporte

Em caso de dúvidas sobre segurança, consulte a equipe de TI antes de fazer deploy em produção. 