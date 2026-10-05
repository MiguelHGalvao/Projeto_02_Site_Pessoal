<div align="center">

# ◈ Plataforma de Análise Financeira

### Dashboard de investimentos, valuation e análise de carteira com Python

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-Análise_de_Dados-150458?style=for-the-badge&logo=pandas&logoColor=white)](https://pandas.pydata.org/)
[![Plotly](https://img.shields.io/badge/Plotly-Visualização-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)](https://plotly.com/python/)

*Uma aplicação interativa para análise fundamentalista, gestão de carteira e simulação de aportes.*

</div>

---

## Sobre o Projeto

A **Plataforma de Análise Financeira** é uma aplicação web desenvolvida em **Python + Streamlit** para consolidar informações de investimentos e auxiliar na análise de ativos do mercado financeiro.

O projeto combina **dados de mercado**, **indicadores fundamentalistas**, **modelos de valuation**, **visualizações interativas** e uma integração opcional com a **API do Google Gemini** para geração de relatórios analíticos.

A aplicação foi desenvolvida com foco em **estudo, experimentação e educação financeira**, não constituindo uma ferramenta de recomendação profissional de investimentos.

---

## Funcionalidades

### Dashboard da Carteira

Permite cadastrar e processar uma carteira de investimentos diretamente pela interface.

- Cadastro de ações, FIIs, BDRs e ETFs
- Quantidade e preço médio por ativo
- Patrimônio atual
- Total investido
- Lucro ou prejuízo
- Rentabilidade percentual
- Dividendos dos últimos 12 meses
- Estimativa de renda passiva anual
- Margem de segurança
- Classificação de cada ativo
- Exportação da carteira processada em CSV

A carteira também pode ser visualizada através de diferentes gráficos:

- Distribuição patrimonial por categoria
- Preço atual × preço teto Bazin
- Composição patrimonial por ativo através de Treemap

---

### Valuation Individual

Analisa um ativo individualmente utilizando diferentes modelos de precificação.

A plataforma apresenta:

| Indicador | Descrição |
|---|---|
| **Preço Atual** | Cotação atual do ativo |
| **Teto Bazin** | Estimativa baseada em dividend yield |
| **Teto Graham** | Modelo baseado em LPA e VPA |
| **Teto Gordon** | Modelo de crescimento de dividendos |
| **Teto Médio** | Combinação dos modelos disponíveis |
| **P/L** | Preço sobre lucro |
| **P/VP** | Preço sobre patrimônio |
| **Dividend Yield** | Rendimento de dividendos |
| **LPA** | Lucro por ação |
| **ROE** | Retorno sobre patrimônio |

Também é possível visualizar o histórico de preços dos últimos 12 meses juntamente com os preços teto calculados.

---

### Comparador de Ativos

Permite comparar diversos ativos simultaneamente.

Basta informar os tickers separados por vírgula para obter uma visão consolidada de:

- Preço atual
- Dividend Yield
- P/L
- P/VP
- ROE
- Preço teto Bazin
- Preço teto Graham
- Margem de segurança

O módulo também apresenta uma visualização gráfica comparando o **Dividend Yield** dos ativos selecionados.

---

### Simulador de Aportes

O simulador utiliza a **margem de segurança** calculada para os ativos da carteira e cria uma sugestão de distribuição para um novo aporte.

O processo:

1. Identifica os ativos abaixo do preço teto.
2. Ordena os ativos pela margem de segurança.
3. Calcula o peso proporcional de cada oportunidade.
4. Distribui o valor do novo aporte.
5. Estima a quantidade de ativos que poderia ser adquirida.

> **Importante:** o modelo é uma simulação simplificada. Não considera diversificação-alvo, correlação entre ativos, liquidez ou perfil individual de risco.

---

### Análise via IA Gemini

A aplicação possui uma integração opcional com o **Google Gemini**.

Após processar uma carteira, o usuário pode fornecer sua chave de API na sessão e solicitar um relatório estratégico contendo:

- Avaliação de risco e diversificação
- Possíveis oportunidades de alocação
- Ativos que exigem acompanhamento
- Sugestões para próximos aportes

O relatório pode ser exportado diretamente em formato Markdown.

A chave da API é utilizada apenas durante a sessão da aplicação e não é armazenada pelo sistema.

---

### Sistema de Temas

A interface possui um sistema de personalização visual integrado.

É possível selecionar:

- Modo claro
- Modo escuro
- Diferentes paletas de cores
- Cor de destaque personalizada
- Cor de destaque forte personalizada

A estilização combina **CSS próprio** com o sistema de componentes do Streamlit.

---

## Modelos de Valuation

### Método Bazin

O preço teto é calculado a partir dos dividendos distribuídos nos últimos 12 meses e de um Dividend Yield alvo:

```text
Preço Teto = Dividendos Anuais ÷ DY Alvo
```

Por exemplo, considerando um DY alvo de 6%:

```text
Preço Teto = Dividendos Anuais ÷ 0,06
```

---

### Método Graham

Para ações, a aplicação utiliza a fórmula tradicional baseada em Lucro por Ação (LPA) e Valor Patrimonial por Ação (VPA):

```text
Preço Justo = √(22,5 × LPA × VPA)
```

---

### Modelo de Gordon

O modelo de Gordon é utilizado para estimar um valor baseado no fluxo de dividendos e crescimento de longo prazo.

---

### Teto Médio

Quando existem múltiplos modelos válidos para determinado ativo, a aplicação pode utilizar uma média dos valores calculados como referência adicional.

> Os modelos são aproximações teóricas e possuem limitações. O resultado não representa necessariamente o valor intrínseco real de um ativo.

---

## Tecnologias Utilizadas

### Backend e aplicação

- **Python**
- **Streamlit**
- **Pandas**

### Dados e mercado

- **yfinance**
- **brapi.dev** como fonte alternativa

### Visualização

- **Plotly Express**
- **Plotly Graph Objects**

### Inteligência Artificial

- **Google Generative AI**
- **Gemini 1.5 Flash**

### Interface

- HTML
- CSS
- Streamlit Components
- Sistema próprio de temas

---

## Estrutura do Projeto

Uma estrutura recomendada para o projeto:

```text
.
├── app.py
├── data_utils.py
├── theme.py
├── style.css
├── logo.png
├── requirements.txt
└── README.md
```

### `app.py`

Arquivo principal da aplicação.

Responsável pela:

- Interface
- Navegação entre módulos
- Gestão da sessão
- Exibição dos indicadores
- Gráficos
- Integração com o Gemini

### `data_utils.py`

Concentra as funções relacionadas a:

- Busca de dados
- Histórico de preços
- Cálculos de valuation
- Margem de segurança
- Classificação de ativos

### `theme.py`

Responsável pelo sistema de aparência:

- Modos claro e escuro
- Paletas
- Cores de destaque
- CSS dinâmico

### `style.css`

Folha de estilos responsável pela personalização visual da aplicação.

### `logo.png`

Logotipo utilizado na interface da plataforma.

---

## Instalação

Clone o repositório:

```bash
git clone <URL_DO_REPOSITORIO>
cd <NOME_DO_REPOSITORIO>
```

Crie um ambiente virtual:

```bash
python -m venv .venv
```

Ative o ambiente virtual no Windows:

```bash
.venv\Scripts\activate
```

Instale as dependências:

```bash
pip install -r requirements.txt
```

---

## Executando a Aplicação

Execute:

```bash
streamlit run app.py
```

Após a inicialização, o Streamlit disponibilizará a aplicação localmente no navegador.

---

## Integração com Google Gemini

A integração com o Gemini é opcional.

Para utilizá-la:

1. Acesse o Google AI Studio.
2. Gere uma chave de API.
3. Abra a aplicação.
4. Acesse o painel lateral.
5. Informe a chave no campo **Chave API Google Gemini**.
6. Processe sua carteira.
7. Acesse **Análise via IA Gemini**.
8. Gere o relatório estratégico.

A biblioteca também pode ser instalada separadamente:

```bash
pip install google-generativeai
```

Caso a biblioteca não esteja instalada, os demais módulos da aplicação continuam disponíveis.

---

## Fluxo de Utilização

```text
                 ┌──────────────────────┐
                 │  Cadastro da Carteira│
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Busca de Dados       │
                 │ Yahoo Finance / Brapi│
                 └──────────┬───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Indicadores e        │
                 │ Valuation            │
                 └──────────┬───────────┘
                            │
              ┌─────────────┼─────────────┐
              ▼             ▼             ▼
        ┌──────────┐  ┌───────────┐  ┌───────────┐
        │Dashboard │  │Comparador │  │ Simulador │
        └──────────┘  └───────────┘  └───────────┘
                            │
                            ▼
                 ┌──────────────────────┐
                 │ Análise opcional      │
                 │ via Google Gemini     │
                 └──────────────────────┘
```

---

## Fontes de Dados

A aplicação utiliza principalmente dados obtidos através do **Yahoo Finance**, com possibilidade de utilização da **brapi.dev** como fonte alternativa.

A disponibilidade e precisão dos dados dependem dos provedores externos.

Por isso, os valores apresentados devem ser tratados como **informativos e sujeitos a alterações**.

---

## Limitações

Esta aplicação possui caráter experimental e educacional.

Entre suas principais limitações estão:

- Dependência de APIs e provedores externos
- Possíveis atrasos ou inconsistências nos dados
- Modelos de valuation simplificados
- Ausência de análise macroeconômica completa
- Ausência de avaliação qualitativa aprofundada das empresas
- Simulador de aportes sem otimização de carteira
- Análise de IA sujeita às limitações do modelo generativo
- Não consideração completa de liquidez, tributação e custos operacionais

---

## Aviso

> **Esta plataforma possui finalidade exclusivamente educacional.**
>
> Os cálculos, indicadores, classificações, simulações e relatórios apresentados não constituem recomendação, indicação ou aconselhamento financeiro.
>
> Decisões de investimento devem considerar outros fatores, incluindo fundamentos da empresa, riscos, cenário econômico, objetivos financeiros, horizonte de investimento e perfil de risco.

---

## Objetivos de Aprendizado

O projeto também funciona como um exercício prático de desenvolvimento de aplicações financeiras com Python.

Entre os principais conceitos explorados estão:

- Desenvolvimento de aplicações web com Streamlit
- Manipulação de dados com Pandas
- Consumo de dados financeiros
- Criação de funções para cálculos financeiros
- Visualização de dados com Plotly
- Gerenciamento de estado com `st.session_state`
- Criação de interfaces interativas
- Desenvolvimento de temas com CSS
- Integração de APIs
- Uso de inteligência artificial generativa
- Organização de aplicações Python em múltiplos módulos

---

## Próximos Passos

Possíveis evoluções para o projeto:

- [ ] Persistência de dados em banco de dados
- [ ] Autenticação de usuários
- [ ] Histórico de carteiras
- [ ] Controle de dividendos recebidos
- [ ] Inclusão de renda fixa
- [ ] Análise de FIIs mais detalhada
- [ ] Comparação por setores
- [ ] Indicadores históricos
- [ ] Backtesting das estratégias
- [ ] Dashboard de evolução patrimonial
- [ ] Integração com mais fontes de dados
- [ ] Melhorias no sistema de recomendação de aportes

---

## Licença

Este projeto é destinado a fins **educacionais e experimentais**.

Consulte o arquivo [`LICENSE`](LICENSE) para conhecer as condições de utilização, distribuição e modificação do projeto.

---

<div align="center">

**Python · Streamlit · Pandas · Plotly · Valuation · IA**

*Análise de dados aplicada ao mercado financeiro.*

</div>
