import os

from funcoes import (
    sanitizar_produtos,
    analisar_pedidos,
    validar_hipotese_entrega_cancelada,
)


def exibir_relatorio_produtos(resultado_produtos):
    """
    Exibe no terminal o relatório do processamento da base de produtos.
    """
    print("=" * 60)
    print("RELATÓRIO DE SANITIZAÇÃO - PRODUTOS")
    print("=" * 60)

    print(f"Total de produtos processados: {resultado_produtos['total_produtos_processados']}")
    print(f"Categorias vazias corrigidas: {resultado_produtos['categorias_corrigidas']}")
    print(f"Dimensões físicas corrigidas: {resultado_produtos['dimensoes_corrigidas']}")

    print("\nMedianas utilizadas para preencher dimensões vazias:")
    for coluna, mediana in resultado_produtos["medianas_utilizadas"].items():
        print(f"- {coluna}: {mediana}")

    print()


def exibir_relatorio_pedidos(resultado_pedidos):
    """
    Exibe no terminal o relatório do processamento da base de pedidos.
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
    for status, quantidade in sorted(resultado_pedidos["sem_data_entrega_por_status"].items()):
        print(f"- {status}: {quantidade}")

    print("\nDatas de aprovação:")
    print(f"- Convertidas com sucesso: {resultado_pedidos['datas_aprovacao_convertidas']}")
    print(f"- Vazias: {resultado_pedidos['datas_aprovacao_vazias']}")
    print(f"- Inválidas: {resultado_pedidos['datas_aprovacao_invalidas']}")

    print()


def exibir_validacao_hipotese(resultado_pedidos):
    """
    Exibe a conclusão da regra de negócio solicitada no enunciado.
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


def main():
    """
    Função principal do projeto.

    Executa o pipeline de:
    1. sanitização da base de produtos;
    2. análise da base de pedidos;
    3. geração dos relatórios no terminal.
    """
    caminho_produtos = os.path.join("data", "olist_products_dataset.csv")
    caminho_pedidos = os.path.join("data", "olist_orders_dataset.csv")

    pasta_saida = "output"
    os.makedirs(pasta_saida, exist_ok=True)

    caminho_produtos_sanitizados = os.path.join(
        pasta_saida,
        "olist_products_dataset_sanitizado.csv"
    )

    resultado_produtos = sanitizar_produtos(
        caminho_entrada=caminho_produtos,
        caminho_saida=caminho_produtos_sanitizados,
    )

    resultado_pedidos = analisar_pedidos(caminho_pedidos)

    exibir_relatorio_produtos(resultado_produtos)
    exibir_relatorio_pedidos(resultado_pedidos)
    exibir_validacao_hipotese(resultado_pedidos)

    print("=" * 60)
    print("PROCESSAMENTO FINALIZADO")
    print("=" * 60)
    print(f"Arquivo de produtos sanitizado salvo em: {caminho_produtos_sanitizados}")


if __name__ == "__main__":
    main()