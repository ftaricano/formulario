# 🛡️ Sistema de Adesão de Seguro Incêndio - ORLA RIO

Sistema web completo e moderno para adesão de seguros com interface elegante, validações automáticas e cálculo de prêmio pró-rata em tempo real.

## 🚀 **Início Rápido**

### **Opção 1: Script Automático (Recomendado)**
```bash
./start_app.sh
```

### **Opção 2: Manual**
```bash
# Ativar ambiente virtual
source venv_formulario/bin/activate

# Executar aplicação
streamlit run app.py

# Desativar ambiente (quando terminar)
deactivate
```

### **📦 Dependências do Projeto**
- **streamlit** (1.45.1) - Framework web para a aplicação
- **requests** (2.32.4) - Para requisições HTTP (APIs de CNPJ/CEP)
- **sendgrid** (6.12.4) - Para envio de emails
- **holidays** (0.74) - Para cálculo de feriados brasileiros
- **jinja2** (3.1.6) - Para templates de email

---

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
- **Tabela de coberturas** exibida primeiro para comparação
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

## 🔧 **Gerenciamento do Ambiente**

### **Comandos Úteis**

#### Verificar dependências instaladas
```bash
source venv_formulario/bin/activate
pip list
```

#### Instalar nova dependência
```bash
source venv_formulario/bin/activate
pip install nova_biblioteca
pip freeze > requirements.txt  # Atualizar arquivo de dependências
```

#### Recriar ambiente (se necessário)
```bash
rm -rf venv_formulario
python -m venv venv_formulario
source venv_formulario/bin/activate
pip install -r requirements.txt
```

### **🛠️ Solução de Problemas**

Se encontrar problemas:

1. **Reativar ambiente**:
   ```bash
   source venv_formulario/bin/activate
   ```

2. **Reinstalar dependências**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Verificar se está no ambiente correto**:
   ```bash
   which python  # Deve mostrar o caminho do venv_formulario
   ```

4. **Recriar ambiente** (última opção):
   ```bash
   rm -rf venv_formulario
   python -m venv venv_formulario
   source venv_formulario/bin/activate
   pip install -r requirements.txt
   ```

### **✅ Vantagens do Ambiente Virtual**

- **Isolamento**: Dependências separadas do sistema
- **Controle de versão**: Versões específicas das bibliotecas
- **Reprodutibilidade**: Mesmo ambiente em qualquer máquina
- **Limpeza**: Apenas bibliotecas necessárias
- **Segurança**: Evita conflitos com outros projetos

## 🏗️ Arquitetura Técnica

### 📁 **Estrutura do Projeto**
```
formulario/
├── app.py                              # Aplicação principal Streamlit
├── config.py                           # Configurações e constantes
├── styles.css                          # Estilos CSS personalizados
├── requirements.txt                    # Dependências Python
├── start_app.sh                        # Script de inicialização
├── venv_formulario/                    # Ambiente virtual isolado
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

### **🎯 Classes CSS Principais**
```css
/* Cards e seções */
.main-card { /* Seções principais */ }
.value-section { /* Seções de valor com gradiente */ }
.equipment-row { /* Linhas de equipamentos */ }

/* Botões */
.primary-button { /* Botão principal preto */ }
.secondary-button { /* Botões secundários */ }
.add-button { /* Botão adicionar equipamento */ }

/* Elementos de formulário */
.form-section { /* Seções do formulário */ }
.field-group { /* Grupos de campos */ }
.radio-horizontal { /* Radio buttons horizontais */ }
```

## 📱 **Otimizações Mobile**

### **🎯 Interface Responsiva**
- **Typography fluida** com `clamp()` para diferentes telas
- **Espaçamentos adaptativos** que se ajustam ao viewport
- **Radio buttons** sempre horizontais com scroll lateral
- **Upload de arquivos** otimizado para mobile
- **Tabelas responsivas** com scroll horizontal

### **⚡ Performance**
- **CSS otimizado** com variáveis e reutilização
- **Componentes modulares** para carregamento eficiente
- **Validações assíncronas** que não bloqueiam a interface
- **Estados de loading** para feedback visual

## 🌐 **APIs e Integrações**

### **🔍 Busca Automática**
- **CNPJ**: Integração com Receita Federal
- **CEP**: Busca de endereços via ViaCEP
- **Validações**: CPF, CNPJ, Email em tempo real

### **📧 Sistema de Email**
- **SendGrid**: Envio de emails profissionais
- **Templates HTML**: Emails formatados e responsivos
- **Anexos**: Suporte a múltiplos arquivos

## 🔐 **Segurança e Validações**

### **✅ Validações Implementadas**
- **CPF**: Validação completa com dígitos verificadores
- **CNPJ**: Validação completa com dígitos verificadores
- **Email**: Validação RFC compliant
- **Telefone**: Formatação e validação brasileira
- **CEP**: Formato e existência
- **Arquivos**: Tipos permitidos e tamanhos máximos

### **🛡️ Medidas de Segurança**
- **Sanitização** de inputs
- **Validação server-side** de todos os dados
- **Controle de upload** com limites de tamanho
- **Filtragem** de tipos de arquivo permitidos

---

## 📞 **Suporte**

Para dúvidas ou problemas técnicos, entre em contato com a equipe de desenvolvimento.

**Versão**: 2.0  
**Última atualização**: Janeiro 2025