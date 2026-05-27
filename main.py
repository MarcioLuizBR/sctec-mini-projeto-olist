import os

from funcoes import (
    sanitizar_produtos,
    analisar_pedidos,
    validar_hipotese_entrega_cancelada,
)


# -------------------------------------------------------------------
# Funções de exibição dos relatórios
# -------------------------------------------------------------------
# O arquivo main.py será responsável por executar o projeto.
# As regras de limpeza e análise ficam no funcoes.py.
#
# Essa separação deixa o projeto mais organizado:
# - funcoes.py: concentra a lógica do processamento;
# - main.py: chama as funções e mostra os resultados no terminal.


def exibir_relatorio_produtos(resultado_produtos):
    """
    Exibe no terminal o relatório do processamento da base de produtos.

    O parâmetro resultado_produtos é um dicionário retornado pela função
    sanitizar_produtos(), localizada no arquivo funcoes.py.

    Esse dicionário contém informações como:
    - total de produtos processados;
    - quantidade de categorias corrigidas;
    - quantidade de dimensões físicas corrigidas;
    - medianas utilizadas no preenchimento dos valores nulos.
    """
    print("=" * 60)
    print("RELATÓRIO DE SANITIZAÇÃO - PRODUTOS")
    print("=" * 60)

    print(f"Total de produtos processados: {resultado_produtos['total_produtos_processados']}")
    print(f"Categorias vazias corrigidas: {resultado_produtos['categorias_corrigidas']}")
    print(f"Dimensões físicas corrigidas: {resultado_produtos['dimensoes_corrigidas']}")

    print("\nMedianas utilizadas para preencher dimensões vazias:")

    # O método .items() permite percorrer chave e valor de um dicionário.
    # Neste caso:
    # - coluna representa o nome da coluna;
    # - mediana representa o valor usado para preencher os campos vazios.
    for coluna, mediana in resultado_produtos["medianas_utilizadas"].items():
        print(f"- {coluna}: {mediana}")

    print()


def exibir_relatorio_pedidos(resultado_pedidos):
    """
    Exibe no terminal o relatório do processamento da base de pedidos.

    O parâmetro resultado_pedidos é um dicionário retornado pela função
    analisar_pedidos(), localizada no arquivo funcoes.py.

    Esse relatório ajuda a validar a regra de negócio solicitada no enunciado:
    verificar se os pedidos sem data de entrega estão obrigatoriamente cancelados.
    """
    print("=" * 60)
    print("RELATÓRIO DE ANÁLISE - PEDIDOS")
    print("=" * 60)

    print(f"Total de pedidos processados: {resultado_pedidos['total_pedidos_processados']}")
    print(f"Total de pedidos cancelados: {resultado_pedidos['total_cancelados']}")
    print(f"Pedidos sem data de entrega: {resultado_pedidos['total_sem_data_entrega']}")
    print(f"Cancelados sem data de entrega: {resultado_pedidos['cancelados_sem_data_entrega']}")
    print(f"Cancelados com data de entrega: {resultado_pedidos['cancelados_com_data_entrega']}")

    print("\nPedidos sem data de entrega por status:")

    # A função sorted() foi usada apenas para organizar visualmente a saída
    # no terminal em ordem alfabética pelo status.
    #
    # Isso não altera os dados originais, apenas melhora a leitura do relatório.
    for status, quantidade in sorted(resultado_pedidos["sem_data_entrega_por_status"].items()):
        print(f"- {status}: {quantidade}")

    print("\nDatas de aprovação:")

    # Aqui exibimos o resultado da conversão de datas feita com datetime.
    # As datas podem cair em três situações:
    # - convertidas com sucesso;
    # - vazias;
    # - inválidas.
    print(f"- Convertidas com sucesso: {resultado_pedidos['datas_aprovacao_convertidas']}")
    print(f"- Vazias: {resultado_pedidos['datas_aprovacao_vazias']}")
    print(f"- Inválidas: {resultado_pedidos['datas_aprovacao_invalidas']}")

    print()


def exibir_validacao_hipotese(resultado_pedidos):
    """
    Exibe a conclusão da hipótese de negócio.

    Hipótese analisada:
    Todos os pedidos sem data de entrega ao cliente estão com status 'canceled'?

    A função validar_hipotese_entrega_cancelada() retorna:
    - True, se a hipótese for confirmada;
    - False, se a hipótese for rejeitada.
    """
    print("=" * 60)
    print("VALIDAÇÃO DA HIPÓTESE DE NEGÓCIO")
    print("=" * 60)

    hipotese_confirmada = validar_hipotese_entrega_cancelada(resultado_pedidos)

    if hipotese_confirmada:
        print(
            "Hipótese confirmada: todos os pedidos sem data de entrega "
            "possuem status 'canceled'."
        )
    else:
        print(
            "Hipótese rejeitada: existem pedidos sem data de entrega "
            "com status diferente de 'canceled'."
        )

    print()


# -------------------------------------------------------------------
# Função principal do projeto
# -------------------------------------------------------------------
def main():
    """
    Função principal do projeto.

    Esta função organiza a execução do pipeline completo:

    1. Define os caminhos dos arquivos de entrada;
    2. Cria a pasta de saída, caso ela ainda não exista;
    3. Executa a sanitização da base de produtos;
    4. Executa a análise da base de pedidos;
    5. Exibe os relatórios finais no terminal.

    A função main() é o ponto de partida do programa.
    """

    # os.path.join() foi usado para montar caminhos de arquivos de forma
    # mais segura entre diferentes sistemas operacionais.
    #
    # No Windows, os caminhos usam barra invertida: data\arquivo.csv
    # Em Linux/Mac, usam barra normal: data/arquivo.csv
    #
    # Com os.path.join(), o Python adapta o caminho automaticamente.
    caminho_produtos = os.path.join("data", "olist_products_dataset.csv")
    caminho_pedidos = os.path.join("data", "olist_orders_dataset.csv")

    # A pasta output será usada para salvar arquivos gerados pelo script.
    # Neste projeto, ela receberá a base de produtos sanitizada.
    pasta_saida = "output"

    # os.makedirs() cria a pasta caso ela ainda não exista.
    #
    # O parâmetro exist_ok=True evita erro se a pasta já existir.
    # Isso permite executar o programa várias vezes sem problemas.
    os.makedirs(pasta_saida, exist_ok=True)

    caminho_produtos_sanitizados = os.path.join(
        pasta_saida,
        "olist_products_dataset_sanitizado.csv"
    )

    # -------------------------------------------------------------------
    # Etapa 1: Sanitização da base de produtos
    # -------------------------------------------------------------------
    # A função sanitizar_produtos() lê o CSV original de produtos,
    # corrige categorias vazias, limpa textos com Regex,
    # trata dimensões físicas ausentes e gera um novo CSV sanitizado.
    resultado_produtos = sanitizar_produtos(
        caminho_entrada=caminho_produtos,
        caminho_saida=caminho_produtos_sanitizados,
    )

    # -------------------------------------------------------------------
    # Etapa 2: Análise da base de pedidos
    # -------------------------------------------------------------------
    # A função analisar_pedidos() lê o CSV de pedidos e calcula os indicadores
    # necessários para validar a hipótese de negócio sobre pedidos cancelados.
    resultado_pedidos = analisar_pedidos(caminho_pedidos)

    # -------------------------------------------------------------------
    # Etapa 3: Exibição dos relatórios no terminal
    # -------------------------------------------------------------------
    # As próximas funções não alteram os dados.
    # Elas apenas organizam a apresentação dos resultados para o usuário.
    exibir_relatorio_produtos(resultado_produtos)
    exibir_relatorio_pedidos(resultado_pedidos)
    exibir_validacao_hipotese(resultado_pedidos)

    print("=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)
    print(f"Arquivo de produtos sanitizado salvo em: {caminho_produtos_sanitizados}")


# -------------------------------------------------------------------
# Ponto de entrada do programa
# -------------------------------------------------------------------
# A condição abaixo garante que a função main() só será executada
# quando este arquivo for rodado diretamente.
#
# Exemplo:
# python main.py
#
# Se este arquivo for importado por outro arquivo Python,
# a função main() não será executada automaticamente.
if __name__ == "__main__":
    main()