# 🛡️ Sistema de Adesão de Seguro - Cessionários ORLA RIO

Sistema web completo para adesão de seguros com interface moderna, validações automáticas e cálculo de prêmio pró-rata em tempo real.

## ✨ Principais Funcionalidades

### 🎯 **Core Features**
- ✅ **Formulário completo** de adesão com validações robustas
- ✅ **Cálculo automático** do prêmio pró-rata baseado na data de inclusão
- ✅ **Busca automática** de dados via APIs (CNPJ/Receita Federal e CEP/ViaCEP)
- ✅ **Sistema de email profissional** com SendGrid (100 emails/dia grátis)
- ✅ **Interface responsiva** e moderna com design profissional
- ✅ **Sistema de validação** em tempo real com feedback visual

### 🔧 **Validações Implementadas**
- **CPF**: Formato e dígitos verificadores
- **CNPJ**: Formato e consulta à Receita Federal
- **CEP**: Formato e busca automática de endereço
- **Email**: Validação de formato RFC compliant
- **Telefone**: 10 ou 11 dígitos com formatação automática
- **Campos obrigatórios**: Validação completa antes do envio

### 🎨 **Experiência do Usuário (UX)**
- **Design moderno** com gradientes e animações suaves
- **Feedback visual** para todos os estados (sucesso, erro, carregamento)
- **Formulário inteligente** que preserva dados em caso de erro
- **Cálculo dinâmico** visível em tempo real
- **Botões de retry** para recuperação de erros
- **Interface compacta** otimizada para produtividade

## 📋 Estrutura do Formulário

### 👤 **Seção 1: Identificação do Responsável**
- **Nome Completo** (mínimo 2 palavras, máximo 120 caracteres)
- **CPF** (com validação de dígitos verificadores)
- **Email** (com validação RFC)
- **Telefone** (formatação automática)
- **CNPJ** (com busca automática da razão social)
- **Razão Social** (preenchimento automático)

### 📍 **Seção 2: Endereço do Quiosque**
- **CEP** (com busca automática de endereço)
- **Logradouro** (preenchimento automático via CEP)
- **Número** e **Complemento**
- **Bairro**, **Cidade** e **Estado** (automático via CEP)

### 🛡️ **Seção 3: Plano de Seguro**
- **Tabela detalhada** de coberturas por plano
- **Seleção visual** de planos com radio buttons estilizados
- **Cálculo automático** do prêmio pró-rata
- **Exibição em tempo real** do valor final

## 🎯 Planos e Coberturas Disponíveis

### 📊 **Tabela Completa de Coberturas**

| **Coberturas** | **Opção 1** | **Opção 2** | **Opção 3** | **Franquia** |
|----------------|-------------|-------------|-------------|--------------|
| **Incêndio, Raio e Explosão** | R$ 250.000 | R$ 400.000 | R$ 700.000 | R$ 30.000 |
| **Alagamento** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 15.000 |
| **Danos Elétricos** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
| **Pequenas Obras** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 5.000 |
| **Perda/Pgto Aluguel (6 meses)** | R$ 20.000 | R$ 30.000 | R$ 40.000 | Não Há |
| **Vidros** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
| **Tumultos** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 5.000 |
| **Vendaval** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 10.000 |

### 💰 **Prêmios Anuais**
- **Opção 1**: R$ 2.505,53/ano
- **Opção 2**: R$ 4.008,85/ano  
- **Opção 3**: R$ 7.015,49/ano

### 📅 **Cálculo Pró-rata**
- **Vigência**: Até 31/12/2025
- **Cálculo**: (Prêmio Anual ÷ 365) × Dias Restantes
- **Exibição**: Valor final destacado em tempo real

## 🔧 Configuração e Instalação

### 📦 **Dependências**
```bash
pip install -r requirements.txt
```

### 🚀 **Início Rápido**

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd formulario
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Execute o aplicativo**
```bash
streamlit run app.py
```

4. **Configure o email** (na barra lateral do app):
   - **Modo Teste**: Para desenvolvimento (não envia emails)
   - **SendGrid**: Para produção (recomendado)
   - **SMTP Tradicional**: Para configuração manual

### 📧 **Configuração de Email com SendGrid (Recomendado)**

#### **Por que SendGrid?**
- ✅ **100 emails/dia grátis** (suficiente para testes)
- ✅ **Alta entregabilidade** (emails não vão para spam)
- ✅ **Fácil configuração** (apenas API Key)
- ✅ **Monitoramento** de entregas e estatísticas
- ✅ **Profissional** para uso empresarial

#### **Configuração Rápida:**
1. **Criar conta**: https://sendgrid.com/ (gratuita)
2. **Obter API Key**: Settings > API Keys > Create API Key
3. **Configurar no app**: Sidebar > SendGrid > Cole a API Key
4. **Testar**: Envie um formulário

📖 **Guia completo**: Veja `CONFIGURACAO_SENDGRID.md` para instruções detalhadas

### ⚙️ **Configuração Alternativa (SMTP)**
Para usar email tradicional, configure as variáveis de ambiente:
```bash
# Arquivo .env (opcional)
EMAIL_REMETENTE=seu_email@empresa.com
EMAIL_SENHA=sua_senha_de_app
EMAIL_EMPRESA=email_destino@empresa.com
MODO_TESTE=false
```

### 🏃‍♂️ **Execução**

#### **Desenvolvimento Local**
```bash
streamlit run app.py
```

#### **Rede Local (Acesso via IP)**
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## 📧 Sistema de Email

### 📨 **3 Modos de Operação**
1. **🧪 Teste**: Preview do email sem envio real (desenvolvimento)
2. **📧 SendGrid**: Serviço profissional de email (recomendado)
3. **⚙️ SMTP**: Configuração manual via Gmail/Outlook

### 🎨 **Template de Email**
- Design responsivo com gradientes
- Seções organizadas (Dados Pessoais, Endereço, Seguro)
- Destaque para o valor final do prêmio
- Timestamp e informações de vigência
- Formatação profissional HTML

### 📊 **Vantagens do SendGrid**
- **Confiabilidade**: 99.9% de uptime
- **Entregabilidade**: Melhor taxa de entrega que SMTP tradicional
- **Monitoramento**: Dashboard com estatísticas detalhadas
- **Escalabilidade**: De 100 emails/dia até milhões
- **Segurança**: Autenticação de domínio e SPF/DKIM

## 🏗️ Arquitetura Técnica

### 📁 **Estrutura de Arquivos**
```
formulario/
├── app.py                      # Aplicação principal
├── config.py                   # Configurações e constantes
├── requirements.txt            # Dependências Python
├── logo.png                    # Logo da empresa
├── .gitignore                  # Arquivos ignorados pelo Git
├── .streamlit/
│   ├── config.toml            # Configurações do Streamlit
│   └── secrets.toml           # Secrets (não commitado)
├── README.md                   # Documentação principal
├── README_SENDGRID.md          # Guia rápido SendGrid
├── CONFIGURACAO_SENDGRID.md    # Guia completo SendGrid
├── exemplo_sendgrid.py         # Exemplo de implementação
└── DEPLOY_GUIDE.md            # Guia de deploy
```

### 🔄 **Fluxo de Dados**
1. **Entrada**: Usuário preenche formulário
2. **Validação**: Campos validados em tempo real
3. **APIs**: Busca automática CNPJ/CEP quando solicitado
4. **Cálculo**: Prêmio pró-rata calculado dinamicamente
5. **Envio**: Email formatado enviado para destinatários
6. **Feedback**: Confirmação visual para o usuário

### 🛡️ **Segurança e Validação**
- **Sanitização**: Limpeza de dados de entrada
- **Validação robusta**: CPF, CNPJ, CEP, email, telefone
- **Tratamento de erros**: Recuperação graceful de falhas
- **Cache inteligente**: APIs externas com cache LRU
- **Timeout**: Configurações de timeout para APIs

## 📱 Compatibilidade

### 🖥️ **Dispositivos Suportados**
- **Desktop**: Windows, macOS, Linux
- **Mobile**: iOS Safari, Android Chrome
- **Tablet**: iPad, Android tablets

### 🌐 **Navegadores Testados**
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## 🎨 Design System

### 🎨 **Paleta de Cores**
- **Primária**: Gradiente azul-roxo (#667eea → #764ba2)
- **Sucesso**: Verde (#48bb78)
- **Erro**: Vermelho (#f56565)
- **Neutros**: Cinzas (#f8f9fa, #e2e8f0)

### 📐 **Componentes**
- **Cards**: Bordas arredondadas com sombras suaves
- **Botões**: Gradientes com hover effects
- **Inputs**: Bordas destacadas com focus states
- **Radio buttons**: Estilização customizada tipo cards

## 🚀 Melhorias Implementadas

### ✅ **Sistema de Email Profissional**
- Integração completa com SendGrid
- 3 modos de operação (Teste, SendGrid, SMTP)
- Template HTML responsivo e profissional
- Configuração via interface web (sem código)
- Fallback graceful para diferentes modos

### ✅ **UX/UI Enhancements**
- Barra superior compacta com logo e títulos centralizados
- Formulário linear com botão de envio no final
- Cálculo pró-rata sempre visível dentro do formulário
- Sistema inteligente de preservação de dados
- Feedback visual aprimorado para todos os estados

### ✅ **Funcionalidades Técnicas**
- Validação completa de CPF com dígitos verificadores
- Sistema de retry para APIs externas
- Gerenciamento inteligente de session state
- Formatação automática de campos (CPF, CNPJ, CEP, telefone)
- Cache LRU para otimização de performance

### ✅ **Robustez e Confiabilidade**
- Tratamento de erros com possibilidade de nova tentativa
- Fallbacks para falhas de API
- Validação dupla (frontend + backend)
- Sistema de logs para debugging
- Configuração flexível (teste/produção)

## 📊 Métricas e Performance

- **Tempo de carregamento**: < 2 segundos
- **Validação em tempo real**: < 100ms
- **APIs externas**: Timeout de 10s com retry
- **Cache**: 100 entradas LRU para otimização
- **Responsividade**: Breakpoints otimizados
- **Email**: Entrega em < 5 segundos via SendGrid

## 📚 Documentação Adicional

- 📖 **`README_SENDGRID.md`**: Guia rápido para configurar SendGrid
- 📖 **`CONFIGURACAO_SENDGRID.md`**: Documentação completa do SendGrid
- 📖 **`exemplo_sendgrid.py`**: Exemplo de implementação
- 📖 **`DEPLOY_GUIDE.md`**: Guia para deploy em produção

---

## 🏢 Informações do Projeto

**Desenvolvido para**: Grupo CPZ Seguros  
**Produto**: Seguro Incêndio Conteúdos - Cessionários ORLA RIO  
**Tecnologia**: Streamlit + Python + SendGrid  
**Status**: ✅ Produção  

---

*Sistema desenvolvido com foco em usabilidade, performance e confiabilidade para otimizar o processo de adesão de seguros.* 🛡️ 

# 🛡️ Formulário CPZ - Seguro Incêndio

Formulário de adesão para Seguro Incêndio - Conteúdos Cessionários (ORLA RIO)

## 🚀 Deploy no Streamlit Cloud

### Arquivos Principais
- `app.py` - Aplicação principal
- `config.py` - Configurações
- `requirements.txt` - Dependências
- `styles.css` - Estilos
- `logo.png` - Logo principal

### Configuração Obrigatória
No Streamlit Cloud, configure em **App Settings > Secrets**:

```toml
[sendgrid]
api_key = "SG.sua_api_key_real_aqui"
```

### Dependências
- streamlit>=1.28.0
- requests>=2.31.0
- sendgrid>=6.10.0

## 🔧 Execução Local

```bash
pip install -r requirements.txt
streamlit run app.py
```

## 📧 Email (SendGrid)
1. Crie conta em: https://sendgrid.com
2. Obtenha API Key
3. Configure Single Sender Verification
4. Adicione API Key nos Secrets

## 📋 Funcionalidades
- ✅ Validação CNPJ/CPF automática
- ✅ Busca automática de endereço por CEP
- ✅ Cálculo automático de prêmio pro rata
- ✅ Upload de arquivos (max 25MB)
- ✅ Envio de email com anexos
- ✅ Design responsivo

---
**Grupo CPZ Seguros** - informe@cpzseg.com.br 