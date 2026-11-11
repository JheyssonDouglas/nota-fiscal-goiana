# Nota Fiscal Goiana — Análise Histórica

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)]()

Projeto de análise histórica dos sorteios da **Nota Fiscal Goiana**, desenvolvido em Python e Streamlit. O objetivo é transformar os resultados publicados em uma base histórica organizada e em visualizações simples, permitindo explorar ganhadores, municípios, valores distribuídos e recorrência de premiações.

> **Status:** o dashboard analítico está em desenvolvimento. A rotina de coleta automática e atualização incremental dos novos sorteios ainda será implementada.

---

## Objetivos

- Consolidar os resultados dos sorteios em uma única base histórica.
- Facilitar a consulta dos ganhadores e dos bilhetes premiados.
- Identificar os municípios com maior quantidade de premiações.
- Comparar os resultados com e sem Goiânia no ranking municipal.
- Identificar nomes que aparecem em mais de um sorteio.
- Analisar a distribuição dos valores dos prêmios.
- Preparar uma rotina para buscar novos resultados e atualizar a base sem duplicar registros.

## Funcionalidades do dashboard

### Resumo
- Quantidade de premiações registradas.
- Quantidade estimada de pessoas premiadas por nome.
- Municípios contemplados.
- Total distribuído em prêmios.
- Comparação da quantidade de premiações e do valor distribuído por sorteio.
- Distribuição dos prêmios menores e maiores em visualizações separadas.

### Municípios
- Ranking de municípios por quantidade de premiações.
- Opção para retirar Goiânia do ranking.
- Quantidade de pessoas premiadas por município, agrupadas por nome.
- Total de dinheiro distribuído por município.

### Ganhadores
- Ranking de nomes com maior quantidade de premiações.
- Total acumulado recebido e maior prêmio identificado.
- Relação dos números de todos os sorteios em que o nome apareceu.
- Consulta individual de um ganhador.

### Sorteios
- Quantidade de premiações por sorteio.
- Municípios contemplados.
- Total distribuído e maior prêmio de cada sorteio.

### Consulta de registros
- Visualização dos registros com filtros.
- Exportação dos dados filtrados para CSV.

## Tecnologias

- **Python** — linguagem principal.
- **Pandas** — leitura, tratamento e análise dos dados.
- **Streamlit** — aplicação web e interface interativa.
- **Plotly** — gráficos interativos.
- **Requests e BeautifulSoup** — planejados para localizar e baixar os resultados publicados.
- **pdfplumber** — planejado para extração de tabelas dos PDFs.
- **Pytest** — testes automatizados.

## Estrutura do projeto

```text
nota-fiscal-goiana/
│
├── app.py
├── dashboard/
│   ├── __init__.py
│   └── app.py
│
├── src/
│   ├── __init__.py
│   └── data.py
│
├── data/
│   ├── resultados_nota_fiscal_goiana.csv
│   └── raw/
│
├── scripts_atualizar_sorteios.py
├── tests/
│   └── test_data.py
│
├── requirements.txt
├── .gitignore
└── README.md
```

> A estrutura acima representa a organização prevista para o projeto. Arquivos de dados brutos e a base histórica local não devem ser versionados no Git quando contiverem dados pessoais.

## Como executar localmente

### 1. Pré-requisitos

- Python 3.10 ou superior.
- Git (opcional, para clonar e versionar o repositório).

Verifique a versão do Python:

```bash
python --version
```

### 2. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/nota-fiscal-goiana.git
cd nota-fiscal-goiana
```

Substitua `SEU-USUARIO` pelo seu usuário do GitHub.

### 3. Crie e ative um ambiente virtual

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Linux ou macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Instale as dependências

```bash
pip install -r requirements.txt
```

### 5. Disponibilize a base de dados

O dashboard espera encontrar o arquivo:

```text
data/resultados_nota_fiscal_goiana.csv
```

O CSV deve conter as colunas:

| Coluna | Descrição |
|---|---|
| `indice` | Identificador sequencial interno do registro |
| `sorteio` | Número do sorteio |
| `data_sorteio` | Data do sorteio |
| `posicao` | Posição do ganhador naquele sorteio |
| `bilhete` | Número do bilhete premiado |
| `nome` | Nome publicado do ganhador |
| `municipio` | Município do ganhador |
| `valor` | Valor do prêmio |

**Atenção:** a base histórica não é incluída neste repositório por padrão. Obtenha o arquivo por uma fonte apropriada e salve-o no caminho indicado. O projeto não deve publicar dados pessoais sem avaliar a finalidade, a necessidade e a base legal para essa divulgação.

### 6. Execute o Streamlit

Na raiz do projeto:

```bash
streamlit run app.py
```

O Streamlit abrirá o dashboard no navegador. Se isso não acontecer automaticamente, acesse o endereço local apresentado no terminal.

## Atualização dos sorteios

A atualização incremental é uma etapa planejada.

O comportamento desejado é executar um único script após a publicação de um novo resultado. Esse script deverá:

1. Consultar a página oficial da Nota Fiscal Goiana.
2. Identificar os sorteios ainda não presentes na base.
3. Localizar e baixar os PDFs correspondentes.
4. Extrair e padronizar os registros.
5. Validar os campos e a quantidade de ganhadores.
6. Evitar duplicidades usando uma chave de negócio, inicialmente composta por `sorteio`, `posicao` e `bilhete`.
7. Criar um backup da base antes da atualização.
8. Acrescentar os novos registros somente após a validação.
9. Registrar o resultado da execução.

O arquivo `scripts_atualizar_sorteios.py`, nesta versão, é apenas um esqueleto de verificação: **ele ainda não realiza a coleta nem altera o CSV**.

Alguns resultados podem apresentar mais de um número de sorteio na mesma linha da página oficial, e os PDFs podem ter layouts diferentes. A extração deverá tratar esses casos explicitamente antes de ser considerada confiável.

## Qualidade e limitações dos dados

- `indice` é um identificador interno sequencial; não identifica uma pessoa.
- `posicao` representa a posição do ganhador dentro de um sorteio.
- A identificação de ganhadores recorrentes é feita por nome normalizado.
- Sem CPF ou outro identificador individual, pessoas homônimas podem ser agrupadas incorretamente e variações de grafia podem separar registros da mesma pessoa.
- Os sorteios 85 e 86 estão pendentes de obtenção dos arquivos oficiais.
- O registro informado do sorteio 110 foi incluído manualmente na base histórica.
- Resultados especiais ou com estrutura diferente devem ser validados individualmente.
- Indicadores dependem da cobertura e da qualidade da base histórica disponível.

## Testes

Com o ambiente virtual ativado, execute:

```bash
pytest
```

## Privacidade e uso dos dados

O projeto utiliza resultados de sorteios disponibilizados publicamente pela Nota Fiscal Goiana.

## Contribuições

Sugestões, identificação de problemas e melhorias são bem-vindas. Abra uma *Issue* descrevendo o problema ou a proposta antes de enviar alterações maiores.