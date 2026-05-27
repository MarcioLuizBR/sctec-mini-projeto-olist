import csv
import re
from datetime import datetime


# Colunas de dimensões físicas que precisam ser tratadas no arquivo de produtos.
COLUNAS_DIMENSOES = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]


def valor_vazio(valor):
    """
    Verifica se um valor está vazio ou nulo.

    Como os dados vêm de arquivos CSV, os valores chegam como strings.
    Por isso, é importante remover espaços antes de verificar se o campo está vazio.
    """
    return valor is None or valor.strip() == ""


def limpar_categoria(categoria):
    """
    Padroniza o nome da categoria do produto.

    Regras aplicadas:
    - valores vazios recebem 'sem categoria';
    - remove espaços no início e no fim;
    - converte para letras minúsculas;
    - troca underline por espaço;
    - remove caracteres especiais com regex;
    - remove espaços duplicados.
    """
    if valor_vazio(categoria):
        return "sem categoria"

    categoria = categoria.strip().lower()

    # Na base Olist, muitas categorias usam underline como separador.
    # Exemplo: cama_mesa_banho.
    # Para melhorar a padronização textual, o underline será tratado como espaço.
    categoria = categoria.replace("_", " ")

    # Remove caracteres que não sejam letras, números ou espaços.
    categoria = re.sub(r"[^a-zA-Z0-9À-ÿ\s]", "", categoria)

    # Remove espaços duplicados no meio da string.
    categoria = re.sub(r"\s+", " ", categoria)

    return categoria.strip()


def converter_para_numero(valor):
    """
    Converte um valor textual do CSV para número float.

    Caso o campo esteja vazio ou inválido, retorna None.
    """
    if valor_vazio(valor):
        return None

    try:
        return float(valor)
    except ValueError:
        return None


def calcular_mediana(lista_valores):
    """
    Calcula a mediana de uma lista numérica sem usar bibliotecas externas.

    A mediana foi escolhida para tratar valores nulos nas dimensões físicas
    porque é menos sensível a valores extremos do que a média.
    Por exemplo, um produto muito pesado poderia distorcer a média da coluna.
    """
    valores_ordenados = sorted(lista_valores)
    quantidade = len(valores_ordenados)

    if quantidade == 0:
        return 0

    meio = quantidade // 2

    if quantidade % 2 == 1:
        return valores_ordenados[meio]

    return (valores_ordenados[meio - 1] + valores_ordenados[meio]) / 2


def calcular_medianas_dimensoes(caminho_arquivo):
    """
    Lê o arquivo de produtos e calcula a mediana das colunas de dimensões físicas.

    Essas medianas serão usadas posteriormente para preencher campos vazios.
    """
    valores_por_coluna = {
        coluna: []
        for coluna in COLUNAS_DIMENSOES
    }

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            for coluna in COLUNAS_DIMENSOES:
                valor_convertido = converter_para_numero(linha[coluna])

                if valor_convertido is not None:
                    valores_por_coluna[coluna].append(valor_convertido)

    medianas = {}

    for coluna, valores in valores_por_coluna.items():
        medianas[coluna] = calcular_mediana(valores)

    return medianas


def sanitizar_produtos(caminho_entrada, caminho_saida):
    """
    Processa o arquivo de produtos e gera um novo CSV sanitizado.

    Tratamentos realizados:
    - categorias vazias são preenchidas com 'sem categoria';
    - categorias são padronizadas com lower, strip e regex;
    - dimensões físicas vazias são preenchidas com a mediana da respectiva coluna.
    """
    medianas = calcular_medianas_dimensoes(caminho_entrada)

    total_linhas = 0
    categorias_corrigidas = 0
    dimensoes_corrigidas = 0

    with open(caminho_entrada, mode="r", encoding="utf-8") as arquivo_entrada:
        leitor = csv.DictReader(arquivo_entrada)
        nomes_colunas = leitor.fieldnames

        with open(caminho_saida, mode="w", encoding="utf-8", newline="") as arquivo_saida:
            escritor = csv.DictWriter(arquivo_saida, fieldnames=nomes_colunas)
            escritor.writeheader()

            for linha in leitor:
                total_linhas += 1

                if valor_vazio(linha["product_category_name"]):
                    categorias_corrigidas += 1

                linha["product_category_name"] = limpar_categoria(
                    linha["product_category_name"]
                )

                for coluna in COLUNAS_DIMENSOES:
                    if valor_vazio(linha[coluna]):
                        linha[coluna] = str(medianas[coluna])
                        dimensoes_corrigidas += 1

                escritor.writerow(linha)

    return {
        "total_produtos_processados": total_linhas,
        "categorias_corrigidas": categorias_corrigidas,
        "dimensoes_corrigidas": dimensoes_corrigidas,
        "medianas_utilizadas": medianas,
    }


def formatar_data_brasileira(data_original):
    """
    Converte uma data do formato original da base Olist para o formato brasileiro.

    Exemplo:
    Entrada: 2017-05-16 15:05:35
    Saída:   16/05/2017
    """
    if valor_vazio(data_original):
        return "data não informada"

    try:
        data_convertida = datetime.strptime(data_original, "%Y-%m-%d %H:%M:%S")
        return data_convertida.strftime("%d/%m/%Y")
    except ValueError:
        return "data inválida"


def analisar_pedidos(caminho_arquivo):
    """
    Analisa o arquivo de pedidos para validar a hipótese de negócio.

    Hipótese:
    As datas de entrega ao cliente estão vazias obrigatoriamente porque
    o status do pedido é 'canceled'?

    A função conta:
    - total de pedidos;
    - total de pedidos cancelados;
    - total de pedidos sem data de entrega;
    - distribuição dos pedidos sem data de entrega por status;
    - quantidade de datas de aprovação convertidas.
    """
    total_pedidos = 0
    total_cancelados = 0
    total_sem_data_entrega = 0
    cancelados_sem_data_entrega = 0
    cancelados_com_data_entrega = 0
    datas_aprovacao_convertidas = 0
    datas_aprovacao_vazias = 0
    datas_aprovacao_invalidas = 0

    sem_data_entrega_por_status = {}

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            total_pedidos += 1

            status = linha["order_status"].strip().lower()
            data_entrega = linha["order_delivered_customer_date"]
            data_aprovacao = linha["order_approved_at"]

            if status == "canceled":
                total_cancelados += 1

            if valor_vazio(data_entrega):
                total_sem_data_entrega += 1

                if status not in sem_data_entrega_por_status:
                    sem_data_entrega_por_status[status] = 0

                sem_data_entrega_por_status[status] += 1

                if status == "canceled":
                    cancelados_sem_data_entrega += 1
            else:
                if status == "canceled":
                    cancelados_com_data_entrega += 1

            data_formatada = formatar_data_brasileira(data_aprovacao)

            if data_formatada == "data não informada":
                datas_aprovacao_vazias += 1
            elif data_formatada == "data inválida":
                datas_aprovacao_invalidas += 1
            else:
                datas_aprovacao_convertidas += 1

    return {
        "total_pedidos_processados": total_pedidos,
        "total_cancelados": total_cancelados,
        "total_sem_data_entrega": total_sem_data_entrega,
        "cancelados_sem_data_entrega": cancelados_sem_data_entrega,
        "cancelados_com_data_entrega": cancelados_com_data_entrega,
        "sem_data_entrega_por_status": sem_data_entrega_por_status,
        "datas_aprovacao_convertidas": datas_aprovacao_convertidas,
        "datas_aprovacao_vazias": datas_aprovacao_vazias,
        "datas_aprovacao_invalidas": datas_aprovacao_invalidas,
    }


def validar_hipotese_entrega_cancelada(resultado_pedidos):
    """
    Valida se todos os pedidos sem data de entrega possuem status canceled.

    Retorna True se a hipótese for confirmada.
    Retorna False se existirem pedidos sem data de entrega com outros status.
    """
    distribuicao = resultado_pedidos["sem_data_entrega_por_status"]

    for status in distribuicao:
        if status != "canceled":
            return False

    return True