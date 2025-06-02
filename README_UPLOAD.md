# 📎 Funcionalidade de Upload de Arquivos

## 🎯 Visão Geral

A nova funcionalidade de upload permite aos usuários anexar documentos e imagens ao formulário de adesão do Seguro Incêndio, facilitando o envio de documentação complementar.

## 📋 Características Principais

### 🗂️ Tipos de Arquivo Aceitos
- **Imagens:** JPG, JPEG, PNG, GIF, WebP
- **Documentos:** PDF, DOC, DOCX, XLS, XLSX
- **Texto:** TXT

### 📏 Limites de Tamanho
- **Por arquivo:** Máximo 10MB
- **Total:** Máximo 25MB por formulário
- **Quantidade:** Sem limite de arquivos (respeitando o limite total)

### 🔧 Funcionalidades Técnicas

#### 1. **Validação Automática**
- ✅ Verificação de tipo de arquivo
- ✅ Controle de tamanho individual e total
- ✅ Exibição de erros descritivos
- ✅ Processamento seguro dos dados

#### 2. **Interface do Usuário**
- 🎨 Design responsivo e moderno
- 📱 Compatível com dispositivos móveis
- 🖱️ Suporte a drag & drop
- 🔢 Contador de arquivos e tamanho total
- 📊 Visualização em tempo real dos arquivos selecionados

#### 3. **Integração com Email**
- 📧 Anexos automáticos via SendGrid
- 📝 Listagem de arquivos no corpo do email
- 🔄 Fallback para modo de teste
- 📊 Informações de tamanho no email

## 🎮 Como Usar

### Para o Usuário Final:
1. **Acesse a seção "📎 Anexar Documentos"** no formulário
2. **Clique em "Browse files"** ou arraste arquivos para a área
3. **Selecione múltiplos arquivos** usando Ctrl+clique (Windows) ou Cmd+clique (Mac)
4. **Visualize os arquivos selecionados** com tamanhos individuais
5. **Preencha o resto do formulário** normalmente
6. **Envie o formulário** - os arquivos serão anexados automaticamente

### Indicadores Visuais:
- 🟢 **Verde:** Arquivos válidos selecionados
- 🔴 **Vermelho:** Erros de validação
- 📊 **Contador:** Mostra quantidade e tamanho total

## 🛠️ Implementação Técnica

### Arquivos Modificados:
- `app.py` - Lógica principal de upload e processamento
- `styles.css` - Estilos para a interface de upload

### Principais Funções:

#### `render_file_upload_section()`
- Renderiza a interface de upload
- Exibe informações sobre arquivos selecionados
- Mostra limitações e tipos aceitos

#### `validar_arquivos()`
- Valida tipos de arquivo permitidos
- Verifica limites de tamanho
- Processa arquivos para envio

#### `SendGridEmailSender.enviar_email_formulario()`
- Adiciona anexos ao email
- Converte arquivos para base64
- Trata erros de anexação

## 🔒 Segurança

- ✅ **Validação de tipos:** Apenas formatos seguros permitidos
- ✅ **Limite de tamanho:** Previne ataques de DoS
- ✅ **Sanitização:** Processamento seguro de nomes de arquivo
- ✅ **Tratamento de erros:** Falhas graciosamente sem quebrar o formulário

## 🌱 Melhorias Futuras

- 📊 **Pré-visualização:** Thumbnails para imagens
- 🗜️ **Compressão:** Redução automática de tamanho
- ☁️ **Cloud Storage:** Integração com serviços externos
- 📈 **Analytics:** Rastreamento de tipos de arquivo mais usados

## 💡 Dicas de Uso

1. **Para melhor performance:** Comprima imagens grandes antes do upload
2. **Documentos PDF:** Prefira PDF a DOC/DOCX para documentos finalizados
3. **Organização:** Use nomes descritivos para os arquivos
4. **Backup:** Mantenha cópias locais dos documentos importantes

---

*Esta funcionalidade foi implementada mantendo a compatibilidade total com o formulário existente e modo de teste.* 