# SCTEC Mini-Projeto Olist - Sanitização de Dados com Python

## Descrição do Projeto

Este projeto foi desenvolvido como parte do Mini-Projeto Avaliativo do módulo de Machine Learning e Visão Computacional do programa SCTEC.

O desafio proposto simula uma situação real de Engenharia de Dados em uma empresa de e-commerce, utilizando arquivos CSV da base da Olist. O objetivo é construir um pipeline de sanitização de dados utilizando apenas bibliotecas nativas do Python, sem o uso da biblioteca Pandas.

O projeto realiza a leitura, limpeza, padronização e análise dos dados contidos nos arquivos:

- `olist_products_dataset.csv`
- `olist_orders_dataset.csv`

A proposta central é tratar inconsistências presentes nos dados antes que eles possam ser utilizados em relatórios automatizados, análises de negócio ou futuros modelos de Machine Learning.

## Objetivos

O pipeline desenvolvido tem como principais objetivos:

- Ler arquivos CSV utilizando o módulo nativo `csv`;
- Padronizar nomes de categorias de produtos;
- Tratar valores ausentes em categorias e dimensões físicas;
- Utilizar expressões regulares para limpeza textual;
- Analisar pedidos sem data de entrega;
- Validar uma hipótese de negócio envolvendo pedidos cancelados;
- Converter datas para o formato brasileiro utilizando `datetime`;
- Gerar um relatório final no terminal com os principais indicadores do processamento.

## Tecnologias Utilizadas

Este projeto utiliza apenas bibliotecas nativas do Python:

- `csv`
- `re`
- `datetime`
- `os`

Não foi utilizada a biblioteca Pandas, conforme solicitado no enunciado do projeto.

## Estrutura do Projeto

```text
sctec-mini-projeto-olist/
│
├── data/
│   ├── olist_orders_dataset.csv
│   └── olist_products_dataset.csv
│
├── output/
│   └── olist_products_dataset_sanitizado.csv
│
├── funcoes.py
├── main.py
├── README.md
├── pyproject.toml
├── .python-version
└── .gitignore
```

## Principais Funcionalidades

### 1. Sanitização da Base de Produtos

O script realiza o tratamento da base `olist_products_dataset.csv`.

As categorias de produtos passam pelos seguintes tratamentos:

- remoção de espaços no início e no fim da string;
- conversão para letras minúsculas;
- substituição de underline por espaço;
- remoção de caracteres especiais com Regex;
- preenchimento de categorias vazias com `"sem categoria"`.

Exemplo de tratamento:

```text
"cama_mesa_banho" -> "cama mesa banho"
```

### 2. Tratamento de Valores Nulos nas Dimensões Físicas

As colunas de dimensões físicas analisadas foram:

- `product_weight_g`
- `product_length_cm`
- `product_height_cm`
- `product_width_cm`

Para os valores vazios nessas colunas, foi utilizada a mediana da respectiva coluna.

A mediana foi escolhida por ser menos sensível a valores extremos do que a média. Em bases de produtos, é possível haver itens muito leves e itens muito pesados, o que poderia distorcer o valor médio.

Medianas utilizadas no processamento:

```text
product_weight_g: 700.0
product_length_cm: 25.0
product_height_cm: 13.0
product_width_cm: 20.0
```

### 3. Análise da Base de Pedidos

O script também analisa o arquivo `olist_orders_dataset.csv`, verificando os pedidos sem data de entrega ao cliente.

A hipótese de negócio analisada foi:

> As datas de entrega ao cliente estão vazias obrigatoriamente porque o pedido foi cancelado?

Após o processamento, a hipótese foi rejeitada, pois foram encontrados pedidos sem data de entrega com outros status além de `canceled`.

Distribuição de pedidos sem data de entrega por status:

```text
approved: 2
canceled: 619
created: 5
delivered: 8
invoiced: 314
processing: 301
shipped: 1107
unavailable: 609
```

Portanto, a ausência da data de entrega não está relacionada exclusivamente a pedidos cancelados.

### 4. Formatação de Datas

A coluna `order_approved_at` foi convertida do formato original:

```text
2017-10-02 11:07:15
```

Para o formato brasileiro simplificado:

```text
02/10/2017
```

A conversão foi realizada com o módulo nativo `datetime`.

## Como Executar o Projeto

### 1. Clonar o repositório

```bash
git clone https://github.com/MarcioLuizBR/sctec-mini-projeto-olist.git
```

### 2. Entrar na pasta do projeto

```bash
cd sctec-mini-projeto-olist
```

### 3. Criar o ambiente virtual

```bash
uv venv
```

### 4. Ativar o ambiente virtual no Windows PowerShell

```powershell
.venv\Scripts\activate
```

### 5. Executar o projeto

```bash
python main.py
```

## Resultado Esperado no Terminal

Ao executar o projeto, será exibido um relatório semelhante a este:

```text
============================================================
RELATÓRIO DE SANITIZAÇÃO - PRODUTOS
============================================================
Total de produtos processados: 32951
Categorias vazias corrigidas: 610
Dimensões físicas corrigidas: 8

Medianas utilizadas para preencher dimensões vazias:
- product_weight_g: 700.0
- product_length_cm: 25.0
- product_height_cm: 13.0
- product_width_cm: 20.0

============================================================
RELATÓRIO DE ANÁLISE - PEDIDOS
============================================================
Total de pedidos processados: 99441
Total de pedidos cancelados: 625
Pedidos sem data de entrega: 2965
Cancelados sem data de entrega: 619
Cancelados com data de entrega: 6

Pedidos sem data de entrega por status:
- approved: 2
- canceled: 619
- created: 5
- delivered: 8
- invoiced: 314
- processing: 301
- shipped: 1107
- unavailable: 609

Datas de aprovação:
- Convertidas com sucesso: 99281
- Vazias: 160
- Inválidas: 0

============================================================
VALIDAÇÃO DA HIPÓTESE DE NEGÓCIO
============================================================
Hipótese rejeitada: existem pedidos sem data de entrega com status diferente de 'canceled'.

============================================================
PROCESSAMENTO FINALIZADO
============================================================
Arquivo de produtos sanitizado salvo em: output\olist_products_dataset_sanitizado.csv
```

## Arquivo Gerado

Após a execução do script, será gerado o seguinte arquivo sanitizado:

```text
output/olist_products_dataset_sanitizado.csv
```

Esse arquivo contém a base de produtos após o tratamento das categorias e das dimensões físicas ausentes.

## Reflexão Teórica: Qualidade dos Dados e Machine Learning

A limpeza correta dos dados é uma etapa fundamental antes da construção de modelos de Machine Learning. Quando uma base contém valores ausentes, categorias mal padronizadas, datas inconsistentes ou registros incompletos, o modelo pode aprender padrões incorretos a partir desses dados. Isso compromete a qualidade das previsões e pode gerar decisões automatizadas pouco confiáveis.

Além disso, dados mal tratados podem contribuir para problemas como viés, overfitting ou underfitting. Um modelo pode se ajustar demais a ruídos e inconsistências da base, em vez de aprender padrões realmente úteis. Por isso, a etapa de ETL e sanitização é essencial para transformar dados brutos em informações mais consistentes, reduzindo o risco de erro em análises, dashboards e aplicações de Inteligência Artificial.

## Conclusão

O projeto demonstrou, de forma prática, como aplicar lógica de programação em Python para realizar um pipeline simples de sanitização de dados.

Foram utilizados conceitos fundamentais como:

- leitura de arquivos CSV;
- listas e dicionários;
- funções;
- estruturas condicionais;
- laços de repetição;
- expressões regulares;
- tratamento de valores ausentes;
- conversão de datas;
- geração de relatório manual.

Essa base de tratamento contribui para que os dados estejam mais consistentes antes de serem utilizados em análises ou modelos de Machine Learning.