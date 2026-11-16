# Nota Fiscal Goiana — Análise Histórica

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-Dashboard-FF4B4B)](https://streamlit.io/)
[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-yellow)]()

Projeto de análise histórica dos sorteios da **Nota Fiscal Goiana**, desenvolvido em Python e Streamlit. O objetivo é transformar os resultados publicados em uma base histórica organizada e em visualizações simples, permitindo explorar ganhadores, municípios, valores distribuídos e recorrência de premiações.

> **Status:** dashboard analítico disponível e rotina de atualização incremental por PDFs implementada. O download dos PDFs oficiais ainda é manual; a extração e a atualização do CSV são realizadas pelo script.

---

## Objetivos

- Consolidar os resultados dos sorteios em uma única base histórica.
- Facilitar a consulta dos ganhadores e dos bilhetes premiados.
- Identificar os municípios com maior quantidade de premiações.
- Comparar os resultados com e sem Goiânia no ranking municipal.
- Identificar nomes que aparecem em mais de um sorteio.
- Analisar a distribuição dos valores dos prêmios.
- Atualizar a base histórica a partir dos PDFs oficiais, evitando duplicidades e preservando um backup.

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
- **pdfplumber** — extração das tabelas dos PDFs oficiais.
- **argparse e pathlib** — interface de linha de comando e manipulação dos arquivos.
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

> A estrutura representa a organização do projeto. O CSV histórico é utilizado pelo dashboard e pelo atualizador. Os PDFs baixados ficam em `data/raw/`; a pasta `data/backups/` é criada automaticamente pelo atualizador.

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

A base histórica utilizada pelo projeto deve estar salva exatamente nesse caminho. Neste repositório, o CSV é disponibilizado para que seja possível executar o dashboard e reproduzir as análises. Os resultados têm origem nas publicações oficiais da Nota Fiscal Goiana. Consulte a seção [Fonte e uso dos dados](#fonte-e-uso-dos-dados) para conhecer a origem e as limitações da base.

### 6. Execute o Streamlit

Na raiz do projeto:

```bash
streamlit run app.py
```

O Streamlit abrirá o dashboard no navegador. Se isso não acontecer automaticamente, acesse o endereço local apresentado no terminal.

## Atualização dos sorteios

O projeto possui um script para extrair os dados de um ou mais PDFs oficiais e atualizar o CSV histórico. **Quando executado normalmente, o script atualiza o CSV automaticamente.** Não é necessário editar o arquivo Python para escolher os sorteios: basta informar os números no terminal.

### 1. Onde colocar os PDFs

Baixe os resultados no site oficial da Nota Fiscal Goiana e salve os arquivos na pasta `data/raw/`, usando este padrão de nome:

```text
data/raw/
├── Resultado_Sorteio_85.pdf
├── Resultado_Sorteio_86.pdf
└── Resultado_Sorteio_121.pdf
```

O número no nome do arquivo deve corresponder ao número do sorteio. O script não faz o download dos PDFs pela internet: essa etapa ainda é manual.

### 2. Atualizar um único sorteio

Na raiz do projeto, com o ambiente virtual ativado, execute:

```bash
python scripts_atualizar_sorteios.py --sorteios 121
```

### 3. Atualizar vários sorteios de uma vez

Informe os números separados por espaço:

```bash
python scripts_atualizar_sorteios.py --sorteios 85 86
```

Também é possível informar três ou mais números:

```bash
python scripts_atualizar_sorteios.py --sorteios 121 122 123
```

### 4. O CSV é atualizado automaticamente?

**Sim.** Por padrão, depois de extrair e validar todos os PDFs informados, o script:

1. Lê `data/resultados_nota_fiscal_goiana.csv`.
2. Extrai número do sorteio, data, posição, bilhete, nome, município e valor do prêmio.
3. Verifica se as posições formam uma sequência contínua e se não há chaves duplicadas nos PDFs.
4. Compara os registros com a base usando a chave `sorteio + posicao + bilhete`.
5. Ignora registros que já existem e adiciona somente os novos.
6. Cria uma cópia de segurança em `data/backups/`.
7. Grava o CSV atualizado no caminho original, que continua sendo o arquivo utilizado pelo dashboard.

Se houver erro na extração, ausência de arquivo, conflito entre os dados do PDF e os dados já existentes ou falha na validação, o script informa o problema e não grava a atualização. Quando vários sorteios são informados, todos os PDFs são processados e validados antes de qualquer alteração no CSV.

### 5. Simular sem alterar o CSV (dry-run)

Para conferir a extração e saber quantos registros seriam adicionados sem modificar nenhum arquivo, use `--dry-run`:

```bash
python scripts_atualizar_sorteios.py --sorteios 85 86 --dry-run
```

Nesse modo, o script mostra a quantidade extraída, os registros novos, os já existentes e o total previsto. **Nenhum CSV é atualizado e nenhum backup é criado.**

### 6. Arquivos e caminhos utilizados

| Arquivo/pasta | Finalidade |
|---|---|
| `scripts_atualizar_sorteios.py` | Script de atualização incremental |
| `data/resultados_nota_fiscal_goiana.csv` | Base histórica atualizada |
| `data/raw/` | PDFs oficiais baixados manualmente |
| `data/backups/` | Cópias de segurança criadas antes de cada gravação |

O script também aceita caminhos alternativos, se necessário:

```bash
python scripts_atualizar_sorteios.py --sorteios 85 --base caminho/para/base.csv --pdf-dir caminho/para/pdfs
```

**Importante:** o script espera PDFs com tabelas que possam ser extraídas pelo `pdfplumber` e com o padrão de colunas utilizado nos resultados já testados. Outros layouts devem ser validados antes de serem considerados compatíveis.

## Qualidade e limitações dos dados

- `indice` é um identificador interno sequencial; não identifica uma pessoa.
- `posicao` representa a posição do ganhador dentro de um sorteio.
- A identificação de ganhadores recorrentes é feita por nome normalizado.
- Sem CPF ou outro identificador individual, pessoas homônimas podem ser agrupadas incorretamente e variações de grafia podem separar registros da mesma pessoa.
- Os sorteios 85 e 86 foram recuperados e incorporados à base histórica a partir dos PDFs oficiais.
- O registro informado do sorteio 110 foi incluído manualmente na base histórica.
- Resultados especiais ou com estrutura diferente devem ser validados individualmente.
- Indicadores dependem da cobertura e da qualidade da base histórica disponível.

## Testes

Com o ambiente virtual ativado, execute:

```bash
pytest
```

## Fonte e uso dos dados

Os dados utilizados neste projeto foram obtidos a partir dos resultados oficiais dos sorteios da [Nota Fiscal Goiana](https://goias.gov.br/nfgoiana/), disponibilizados publicamente pelo Governo do Estado de Goiás. Os arquivos foram consolidados e padronizados em uma base histórica para permitir análises sobre sorteios, ganhadores, municípios e valores distribuídos.

A base CSV é disponibilizada neste repositório para permitir a execução do dashboard e a reprodução das análises. Os PDFs originais podem ser baixados diretamente da fonte oficial quando necessário para atualizar a base.

## Roadmap

- [x] Estrutura inicial do projeto.
- [x] Leitura e padronização da base CSV.
- [x] Dashboard inicial em Streamlit.
- [x] Ranking de municípios com opção de excluir Goiânia.
- [x] Ranking de ganhadores com relação dos sorteios em que aparecem.
- [x] Separação visual dos prêmios menores e maiores.
- [ ] Revisão e validação de inconsistências na base histórica.
- [ ] Automatizar a localização e o download dos novos PDFs oficiais.
- [x] Extração de PDFs dos layouts já validados (incluindo os sorteios 85 e 86).
- [x] Atualização incremental do CSV com backup e prevenção de duplicidades.
- [ ] Testes automatizados do processo de ingestão.
- [ ] Publicação do dashboard.

## Contribuições

Sugestões, identificação de problemas e melhorias são bem-vindas. Abra uma *Issue* descrevendo o problema ou a proposta antes de enviar alterações maiores.

