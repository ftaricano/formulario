# 🛡️ Sistema de Adesão de Seguro Incêndio - ORLA RIO

Sistema web completo e moderno para adesão de seguros com interface elegante, validações automáticas e cálculo de prêmio pró-rata em tempo real.

## ✨ Visão Geral

**Formulário de Adesão de Seguro Incêndio Conteúdos - Cessionários** é uma aplicação web desenvolvida em Streamlit com design moderno, validações robustas e experiência de usuário otimizada.

### 🎯 **Principais Características**
- ✅ **Design moderno** com gradientes pretos elegantes
- ✅ **Interface responsiva** otimizada para todos os dispositivos
- ✅ **Validações em tempo real** com feedback visual
- ✅ **Busca automática** via APIs (CNPJ e CEP)
- ✅ **Cálculo dinâmico** do prêmio pró-rata
- ✅ **Arquitetura modular** com separação de responsabilidades
- ✅ **Sistema de templates** HTML para emails
- ✅ **Experiência de usuário** fluida e profissional

## 📋 Fluxo do Formulário

### **1. 🏢 Identificação do Quiosque**
- **CNPJ** com busca automática na Receita Federal
- **Razão Social** preenchida automaticamente
- **Endereço completo** com busca automática via CEP
- Campos: CEP, Logradouro, Número, Complemento, Bairro, Cidade, Estado

### **2. 👤 Identificação do Responsável**
- **CPF** com validação de dígitos verificadores
- **Nome Completo** (mínimo 2 palavras)
- **Email** com validação RFC
- **Telefone** com formatação automática

### **3. 🛡️ Seleção do Plano**
- **Radio buttons horizontais** com design moderno
- **Gradiente preto** quando selecionado
- **3 opções de cobertura** com valores claros
- **Cálculo automático** em tempo real

### **4. 📦 Bens e Equipamentos (sem Nota Fiscal)**
- **Sistema dinâmico** para adicionar itens
- **Campos**: Tipo, Descrição, Valor
- **Botão adicionar** para múltiplos itens
- **Resumo automático** dos itens cadastrados

### **5. 📎 Anexar Documentos (Opcional)**
- **Upload múltiplo** de arquivos
- **Tipos suportados**: JPG, JPEG, PNG, PDF, XLSX
- **Validação de tamanho** e tipo
- **Interface clean** sem elementos desnecessários

### **6. 💰 Cálculo e Valor Total**
- **Período de vigência** calculado automaticamente
- **Data de inclusão** considerando dias úteis e feriados
- **Valor destacado** com gradiente preto elegante
- **Proporcionalidade** baseada em dias restantes até 31/12/2024

### **7. 🚀 Envio da Solicitação**
- **Botão principal** com gradiente preto
- **Validação completa** antes do envio
- **Feedback visual** de sucesso/erro
- **Preservação de dados** em caso de erro

## 🎨 Design e Interface

### **🖤 Identidade Visual**
- **Gradiente preto principal**: `linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%)`
- **Botões consistentes** com mesmo gradiente em todo o formulário
- **Seções de valor** com destaque elegante
- **Typography**: Fonte Poppins em todo o sistema
- **Animações suaves** com efeitos glow

### **📱 Responsividade**
- **Layout adaptativo** para desktop, tablet e mobile
- **Seções compactas** com espaçamentos otimizados
- **Radio buttons sempre horizontais** com scroll se necessário
- **Tipografia responsiva** com clamp()
- **Padding e margin reduzidos** para melhor aproveitamento da tela

### **✨ Experiência do Usuário**
- **Seções organizadas** com títulos claros
- **Feedback visual** para todos os estados
- **Botões de busca** com ícones intuitivos
- **Animações suaves** para transições
- **Design clean** sem elementos desnecessários

## 🛡️ Planos e Coberturas

### 📊 **Tabela Completa de Coberturas**

| **Coberturas** | **Opção 1** | **Opção 2** | **Opção 3** | **Franquia** |
|----------------|-------------|-------------|-------------|--------------|
| **Incêndio, Raio e Explosão** | R$ 250.000 | R$ 400.000 | R$ 700.000 | R$ 30.000 |
| **Alagamento** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 15.000 |
| **Danos Elétricos** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
| **Pequenas Obras** | R$ 50.000 | R$ 100.000 | R$ 150.000 | R$ 5.000 |
| **Perda/Pgto Aluguel (6m)** | R$ 20.000 | R$ 30.000 | R$ 40.000 | Não Há |
| **Vidros** | R$ 20.000 | R$ 50.000 | R$ 100.000 | R$ 3.000 |
| **Tumultos** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 5.000 |
| **Vendaval** | R$ 100.000 | R$ 150.000 | R$ 200.000 | R$ 10.000 |

### 💰 **Prêmios Anuais**
- **Opção 1**: R$ 2.505,53/ano - R$ 208,79/mês
- **Opção 2**: R$ 4.008,85/ano - R$ 334,07/mês  
- **Opção 3**: R$ 7.015,49/ano - R$ 584,62/mês

### 📅 **Cálculo Pró-rata**
- **Vigência**: Até 31/12/2024
- **Fórmula**: (Prêmio Anual ÷ 365) × Dias Restantes
- **Considerações**: Próximo dia útil, feriados, fins de semana

## 🏗️ Arquitetura Técnica

### 📁 **Estrutura do Projeto**
```
formulario/
├── app.py                              # Aplicação principal Streamlit
├── config.py                           # Configurações e constantes
├── styles.css                          # Estilos CSS personalizados
├── requirements.txt                    # Dependências Python
├── logo.png                            # Logo da empresa
├── .gitignore                          # Arquivos ignorados pelo Git
├── README.md                           # Documentação (este arquivo)
│
├── src/                                # Código fonte modular
│   ├── components/                     # Componentes reutilizáveis
│   │   ├── form_sections.py           # Seções do formulário
│   │   └── enhanced_form_sections.py  # Versões aprimoradas
│   │
│   ├── controllers/                    # Controladores de negócio
│   │   └── form_controller.py         # Lógica do formulário
│   │
│   ├── managers/                       # Gerenciadores de estado
│   │   └── state_manager.py           # Gerenciamento de sessão
│   │
│   ├── models/                         # Modelos de dados
│   │   └── formulario.py              # Estruturas de dados
│   │
│   ├── utils/                          # Utilitários
│   │   └── formatters.py              # Formatadores e helpers
│   │
│   └── validators/                     # Validadores
│       └── form_validators.py         # Validações de formulário
│
└── templates/                          # Templates HTML
    ├── components/                     # Componentes de template
    │   ├── coverage_table.html         # Tabela de coberturas
    │   └── success_value.html          # Seção de valor
    │
    └── sections/                       # Seções de template
        └── calculation_section.html    # Seção de cálculo
```

### 🔧 **Arquitetura Modular**

#### **📦 Componentes (`src/components/`)**
- **`FormSectionRenderer`**: Renderização de seções do formulário
- **`EquipamentosSection`**: Gerenciamento de bens/equipamentos
- **`ApiSearchHandler`**: Integração com APIs externas
- **`EnhancedFormRenderer`**: Versões aprimoradas com validação

#### **🎮 Controladores (`src/controllers/`)**
- **`FormularioController`**: Lógica principal do formulário
- **`EquipamentosController`**: Gerenciamento de equipamentos
- **`PlanoController`**: Gerenciamento de planos de seguro

#### **🗃️ Modelos (`src/models/`)**
- **`FormularioSeguro`**: Modelo principal do formulário
- **`Equipamento`**: Modelo para bens/equipamentos
- **Dataclasses** com validação e serialização

#### **🛠️ Utilitários (`src/utils/`)**
- **`ValueFormatter`**: Formatação de valores monetários
- **`DateUtils`**: Manipulação de datas e feriados
- **`StringUtils`**: Manipulação de strings

#### **✅ Validadores (`src/validators/`)**
- **`FormValidator`**: Validação completa do formulário
- **`FileValidator`**: Validação de arquivos
- **Validações**: CPF, CNPJ, CEP, Email, Telefone

## 🎨 Sistema de Estilos

### **🖤 Gradientes e Cores**
```css
/* Gradiente principal (botões e seções de valor) */
--black-gradient: linear-gradient(135deg, #1a1a1a 0%, #2d2d2d 50%, #1a1a1a 100%);

/* Cores base */
--primary-color: #2d3748;
--text-white: #ffffff;
--background-card: rgba(248, 250, 252, 0.85);
```

### **📏 Espaçamentos Responsivos**
```css
/* Espaçamentos compactos */
--spacing-xs: clamp(0.25rem, 1vw, 0.5rem);    /* 4-8px */
--spacing-sm: clamp(0.5rem, 2vw, 0.75rem);    /* 8-12px */
--spacing-md: clamp(0.75rem, 2.5vw, 1rem);    /* 12-16px */
--spacing-lg: clamp(1rem, 3vw, 1.5rem);       /* 16-24px */
```

### **✨ Animações e Efeitos**
- **Glow effect**: Para botões e seções especiais
- **Hover transitions**: Elevação e mudança de sombra
- **Slide animations**: Para entrada de elementos
- **Cubic-bezier**: Para animações suaves e naturais

## 🔧 Configuração e Instalação

### 📋 **Pré-requisitos**
- Python 3.8 ou superior
- pip (gerenciador de pacotes Python)

### 🚀 **Instalação Rápida**

1. **Clone o repositório**
```bash
git clone <url-do-repositorio>
cd formulario
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Execute a aplicação**
```bash
streamlit run app.py
```

4. **Acesse no navegador**
```
http://localhost:8501
```

### 📦 **Dependências**
```python
streamlit>=1.28.0    # Framework web
requests>=2.31.0     # Requisições HTTP para APIs
python-dateutil      # Manipulação de datas
holidays             # Cálculo de feriados brasileiros
```

### 🌐 **Execução em Rede Local**
```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

## ⚙️ Configurações

### 📅 **Datas e Vigência**
```python
# config.py
DATA_FINAL_VIGENCIA = datetime(2024, 12, 31)  # Final da vigência
TIMEZONE = 'America/Sao_Paulo'                # Fuso horário brasileiro
```

### 💰 **Planos de Seguro**
```python
# config.py
PLANOS_SEGURO = {
    "Opção 1 (R$ 250.000)": 2505.53,
    "Opção 2 (R$ 400.000)": 4008.85,
    "Opção 3 (R$ 700.000)": 7015.49
}
```

### 🎨 **Configurações de Interface**
```python
# config.py
APP_CONFIG = {
    "page_title": "Formulário de Adesão - Seguro Incêndio",
    "page_icon": "🛡️",
    "layout": "wide",
    "initial_sidebar_state": "collapsed"
}
```

## 🔍 Validações Implementadas

### **📋 Validações de Campos**
- ✅ **CPF**: Formato e dígitos verificadores
- ✅ **CNPJ**: Formato e validação de dígitos
- ✅ **CEP**: Formato brasileiro (XXXXX-XXX)
- ✅ **Email**: Validação RFC compliant
- ✅ **Telefone**: 10 ou 11 dígitos com DDD
- ✅ **Nome**: Mínimo 2 palavras, máximo 120 caracteres

### **📁 Validações de Arquivo**
- ✅ **Tipos permitidos**: JPG, JPEG, PNG, PDF, XLSX
- ✅ **Tamanho individual**: Máximo 10MB por arquivo
- ✅ **Tamanho total**: Máximo 25MB
- ✅ **Sanitização**: Verificação de conteúdo

### **🔗 Integrações com APIs**
- ✅ **CNPJ**: Busca automática na Receita Federal
- ✅ **CEP**: Busca automática de endereço via ViaCEP
- ✅ **Cache**: Sistema LRU para otimização
- ✅ **Fallback**: Tratamento de erros graceful

## 🎯 Funcionalidades Avançadas

### **📊 Cálculo Dinâmico**
- **Prêmio pró-rata** baseado em dias restantes
- **Consideração de feriados** brasileiros
- **Próximo dia útil** para data de inclusão
- **Formatação monetária** brasileira (R$ X.XXX,XX)

### **🎨 Design Responsivo**
- **Mobile-first** approach
- **Breakpoints**: 768px (tablet) e 1024px (desktop)
- **Radio buttons horizontais** sempre visíveis
- **Seções compactas** para melhor UX

### **⚡ Performance**
- **Lazy loading** de componentes
- **Cache de APIs** com TTL
- **Componentes reutilizáveis**
- **CSS otimizado** com variáveis

### **🛡️ Segurança**
- **Sanitização** de inputs
- **Validação server-side**
- **Tratamento de exceções**
- **No sensitive data** em logs

## 🚀 Deploy e Produção

### **☁️ Streamlit Cloud (Recomendado)**
1. Fork do repositório no GitHub
2. Conectar no Streamlit Cloud
3. Deploy automático
4. URL pública disponível

### **🐳 Docker**
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

### **🖥️ Servidor Local**
```bash
# Instalação como serviço systemd
sudo systemctl enable formulario.service
sudo systemctl start formulario.service
```

## 📈 Melhorias Implementadas

### **🎨 Design Moderno (v2.0)**
- ✅ **Gradiente preto elegante** em todos os botões
- ✅ **Seções de valor** com destaque especial
- ✅ **Radio buttons** com design sofisticado
- ✅ **Espaçamentos otimizados** para melhor UX
- ✅ **Responsividade aprimorada** em todos os dispositivos
- ✅ **Animações suaves** com efeitos glow

### **📱 Interface Otimizada**
- ✅ **Ordem lógica** das seções (planos antes de bens)
- ✅ **Seções compactas** com menos espaçamento
- ✅ **Radio buttons sempre horizontais**
- ✅ **Botões uniformes** com gradiente consistente
- ✅ **Texto limpo** sem emojis nas seções finais

### **🔧 Arquitetura Modular**
- ✅ **Separação de responsabilidades**
- ✅ **Componentes reutilizáveis**
- ✅ **Templates HTML** para emails
- ✅ **Sistema de validação** robusto
- ✅ **Gerenciamento de estado** avançado

## 📞 Suporte

Para suporte técnico ou dúvidas sobre o sistema:
- **Email**: suporte@orla-rio.com
- **Horário**: Segunda a Sexta, 9h às 18h

## 📄 Licença

Este projeto é propriedade da **ORLA RIO** e destina-se ao uso interno para processos de adesão de seguros.

---

**🛡️ Sistema de Adesão de Seguro Incêndio - ORLA RIO**  
*Versão 2.0 - Interface Moderna com Gradientes Pretos*  
*Desenvolvido com ❤️ usando Streamlit e Python*

## 📧 Configuração de Email (SendGrid)

Para habilitar o envio de emails, você precisa configurar o SendGrid:

### 1. Obter API Key do SendGrid
1. Crie uma conta no [SendGrid](https://sendgrid.com/)
2. Gere uma API Key no painel administrativo
3. Configure a API Key no sistema

### 2. Configuração Local
Crie o arquivo `.streamlit/secrets.toml`:
```toml
SENDGRID_API_KEY = "SG.sua_api_key_aqui"
```

### 3. Configuração em Produção
- **Streamlit Cloud**: Adicione `SENDGRID_API_KEY` nas configurações de secrets
- **Heroku**: Configure como variável de ambiente
- **Docker**: Use variável de ambiente `SENDGRID_API_KEY`

### 4. Personalizar Emails
Edite o arquivo `src/services/email_service.py` para configurar:
- Email de origem (`from_email`)
- Email de destino (`to_email`)
- Assunto do email (`subject`)

## 🚀 Instalação e Execução 