import csv
import re
from datetime import datetime


# -------------------------------------------------------------------
# Constantes do projeto
# -------------------------------------------------------------------
# Esta lista concentra os nomes das colunas de dimensões físicas.
# Usar uma constante evita repetir esses nomes várias vezes no código
# e facilita futuras alterações, caso novas colunas sejam adicionadas.
COLUNAS_DIMENSOES = [
    "product_weight_g",
    "product_length_cm",
    "product_height_cm",
    "product_width_cm",
]


# -------------------------------------------------------------------
# Funções auxiliares gerais
# -------------------------------------------------------------------
def valor_vazio(valor):
    """
    Verifica se um valor está vazio ou nulo.

    Como os dados vêm de arquivos CSV, os valores chegam como strings.
    Por isso, antes de verificar se o campo está vazio, usamos strip()
    para remover espaços em branco no início e no fim.

    Exemplos considerados vazios:
    - None
    - ""
    - "   "
    """
    return valor is None or valor.strip() == ""


# -------------------------------------------------------------------
# Funções lambda
# -------------------------------------------------------------------
# Lambda é uma função anônima, geralmente usada para operações simples
# que podem ser escritas em uma única linha.
#
# Neste projeto, as funções lambda foram incluídas de forma didática,
# pois o enunciado menciona encapsulamento em funções def ou lambda.
# Elas serão usadas na análise dos pedidos.


normalizar_status = lambda status: "" if valor_vazio(status) else status.strip().lower()
# Esta lambda normaliza o status do pedido.
#
# Exemplo:
# Entrada: " Canceled "
# Saída:   "canceled"
#
# Ela remove espaços extras e transforma o texto em letras minúsculas.


eh_pedido_cancelado = lambda status: normalizar_status(status) == "canceled"
# Esta lambda verifica se um pedido está cancelado.
#
# Retorna:
# - True, se o status for "canceled";
# - False, caso contrário.


# -------------------------------------------------------------------
# Funções de tratamento de texto
# -------------------------------------------------------------------
def limpar_categoria(categoria):
    """
    Padroniza o nome da categoria do produto.

    Regras aplicadas:
    - valores vazios recebem 'sem categoria';
    - espaços no início e no fim são removidos com strip();
    - o texto é convertido para letras minúsculas com lower();
    - underline é substituído por espaço;
    - caracteres especiais são removidos com Regex;
    - espaços duplicados são reduzidos para um único espaço.

    Essa etapa é importante porque categorias escritas de formas diferentes
    podem prejudicar análises futuras e modelos de Machine Learning.
    """
    if valor_vazio(categoria):
        return "sem categoria"

    # Remove espaços laterais e padroniza para letras minúsculas.
    categoria = categoria.strip().lower()

    # Na base Olist, muitas categorias usam underline como separador.
    # Exemplo: "cama_mesa_banho".
    # Para melhorar a leitura, o underline será tratado como espaço.
    categoria = categoria.replace("_", " ")

    # Expressão Regular usada:
    # [^a-zA-Z0-9À-ÿ\s]
    #
    # Explicação:
    # ^ dentro dos colchetes significa negação.
    # Portanto, essa regex remove tudo que NÃO for:
    # - letra de A a Z;
    # - letra de a a z;
    # - número de 0 a 9;
    # - caractere acentuado;
    # - espaço em branco.
    categoria = re.sub(r"[^a-zA-Z0-9À-ÿ\s]", "", categoria)

    # Remove espaços duplicados no meio do texto.
    # Exemplo: "cama   mesa   banho" vira "cama mesa banho".
    categoria = re.sub(r"\s+", " ", categoria)

    return categoria.strip()


# -------------------------------------------------------------------
# Funções de tratamento numérico
# -------------------------------------------------------------------
def converter_para_numero(valor):
    """
    Converte um valor textual vindo do CSV para número float.

    Como arquivos CSV armazenam os dados em texto, mesmo valores numéricos
    chegam inicialmente como string.

    Se o valor estiver vazio ou não puder ser convertido, a função retorna None.
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

    A mediana representa o valor central de uma sequência ordenada.

    Neste projeto, ela foi escolhida para preencher valores nulos nas dimensões
    físicas dos produtos porque é menos sensível a valores extremos do que a média.

    Exemplo:
    Se uma base possui produtos de 100g, 200g, 300g e um produto de 30.000g,
    a média pode ficar distorcida pelo valor muito alto.

    A mediana, por outro lado, tende a representar melhor o comportamento central
    da maior parte dos produtos.
    """
    valores_ordenados = sorted(lista_valores)
    quantidade = len(valores_ordenados)

    # Caso a lista esteja vazia, retornamos 0 para evitar erro no cálculo.
    if quantidade == 0:
        return 0

    meio = quantidade // 2

    # Se a quantidade de valores for ímpar, a mediana é o valor central.
    if quantidade % 2 == 1:
        return valores_ordenados[meio]

    # Se a quantidade for par, a mediana é a média dos dois valores centrais.
    return (valores_ordenados[meio - 1] + valores_ordenados[meio]) / 2


def calcular_medianas_dimensoes(caminho_arquivo):
    """
    Lê o arquivo de produtos e calcula a mediana das colunas de dimensões físicas.

    Essa função faz uma primeira leitura da base de produtos para coletar
    os valores válidos de peso, comprimento, altura e largura.

    Depois, calcula a mediana de cada coluna.
    Essas medianas serão usadas posteriormente para preencher valores vazios.
    """
    valores_por_coluna = {
        coluna: []
        for coluna in COLUNAS_DIMENSOES
    }

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        # Percorre cada linha do arquivo CSV.
        for linha in leitor:
            # Para cada coluna de dimensão física, tentamos converter o valor.
            for coluna in COLUNAS_DIMENSOES:
                valor_convertido = converter_para_numero(linha[coluna])

                # Apenas valores válidos entram no cálculo da mediana.
                if valor_convertido is not None:
                    valores_por_coluna[coluna].append(valor_convertido)

    medianas = {}

    # Calcula a mediana de cada coluna de dimensão física.
    for coluna, valores in valores_por_coluna.items():
        medianas[coluna] = calcular_mediana(valores)

    return medianas


# -------------------------------------------------------------------
# Funções de sanitização da base de produtos
# -------------------------------------------------------------------
def sanitizar_produtos(caminho_entrada, caminho_saida):
    """
    Processa o arquivo de produtos e gera um novo CSV sanitizado.

    Tratamentos realizados:
    - categorias vazias são preenchidas com 'sem categoria';
    - categorias são padronizadas com strip(), lower() e Regex;
    - dimensões físicas vazias são preenchidas com a mediana da respectiva coluna.

    A função também retorna um dicionário com contadores para o relatório final.
    """
    # Antes de corrigir os valores vazios, calculamos as medianas das dimensões.
    # Essas medianas serão usadas como valores de preenchimento.
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

                # Verifica se a categoria original estava vazia.
                # Se estava, contabilizamos essa correção.
                if valor_vazio(linha["product_category_name"]):
                    categorias_corrigidas += 1

                # Aplica a limpeza textual na categoria.
                linha["product_category_name"] = limpar_categoria(
                    linha["product_category_name"]
                )

                # Percorre as colunas de dimensões físicas.
                for coluna in COLUNAS_DIMENSOES:
                    # Se a dimensão estiver vazia, preenchemos com a mediana
                    # calculada anteriormente para aquela coluna.
                    if valor_vazio(linha[coluna]):
                        linha[coluna] = str(medianas[coluna])
                        dimensoes_corrigidas += 1

                # Escreve a linha já tratada no novo arquivo CSV.
                escritor.writerow(linha)

    return {
        "total_produtos_processados": total_linhas,
        "categorias_corrigidas": categorias_corrigidas,
        "dimensoes_corrigidas": dimensoes_corrigidas,
        "medianas_utilizadas": medianas,
    }


# -------------------------------------------------------------------
# Funções de tratamento de datas
# -------------------------------------------------------------------
def formatar_data_brasileira(data_original):
    """
    Converte uma data do formato original da base Olist para o formato brasileiro.

    Exemplo:
    Entrada: 2017-05-16 15:05:35
    Saída:   16/05/2017

    Caso a data esteja vazia, retorna 'data não informada'.
    Caso a data esteja em formato inválido, retorna 'data inválida'.
    """
    if valor_vazio(data_original):
        return "data não informada"

    try:
        # datetime.strptime transforma uma string em um objeto de data.
        #
        # O formato "%Y-%m-%d %H:%M:%S" representa:
        # %Y = ano com 4 dígitos
        # %m = mês
        # %d = dia
        # %H = hora
        # %M = minuto
        # %S = segundo
        data_convertida = datetime.strptime(data_original, "%Y-%m-%d %H:%M:%S")

        # strftime transforma o objeto de data em uma string no formato desejado.
        # Aqui usamos o padrão brasileiro: dia/mês/ano.
        return data_convertida.strftime("%d/%m/%Y")

    except ValueError:
        return "data inválida"


# -------------------------------------------------------------------
# Funções de análise da base de pedidos
# -------------------------------------------------------------------
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
    - quantidade de datas de aprovação convertidas;
    - quantidade de datas de aprovação vazias;
    - quantidade de datas de aprovação inválidas.

    O resultado é retornado em um dicionário para ser exibido pelo main.py.
    """
    total_pedidos = 0
    total_cancelados = 0
    total_sem_data_entrega = 0
    cancelados_sem_data_entrega = 0
    cancelados_com_data_entrega = 0
    datas_aprovacao_convertidas = 0
    datas_aprovacao_vazias = 0
    datas_aprovacao_invalidas = 0

    # Este dicionário será usado para contar quantos pedidos sem data de entrega
    # existem em cada status.
    #
    # Exemplo esperado:
    # {
    #     "canceled": 619,
    #     "shipped": 1107,
    #     ...
    # }
    sem_data_entrega_por_status = {}

    with open(caminho_arquivo, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)

        for linha in leitor:
            total_pedidos += 1

            # O status do pedido será normalizado para evitar problemas causados
            # por letras maiúsculas, minúsculas ou espaços extras.
            #
            # Exemplo:
            # " Canceled " será tratado como "canceled".
            status = normalizar_status(linha["order_status"])

            data_entrega = linha["order_delivered_customer_date"]
            data_aprovacao = linha["order_approved_at"]

            # Aqui usamos uma função lambda para verificar se o pedido está cancelado.
            # Isso deixa a regra de negócio mais explícita e reaproveitável.
            pedido_cancelado = eh_pedido_cancelado(status)

            if pedido_cancelado:
                total_cancelados += 1

            # A regra de negócio principal analisa os pedidos em que a data
            # de entrega ao cliente está vazia.
            if valor_vazio(data_entrega):
                total_sem_data_entrega += 1

                # Se o status ainda não existe no dicionário, criamos a chave.
                if status not in sem_data_entrega_por_status:
                    sem_data_entrega_por_status[status] = 0

                # Incrementa a contagem de pedidos sem data de entrega
                # para o respectivo status.
                sem_data_entrega_por_status[status] += 1

                if pedido_cancelado:
                    cancelados_sem_data_entrega += 1
            else:
                if pedido_cancelado:
                    cancelados_com_data_entrega += 1

            # Converte a data de aprovação para o formato brasileiro
            # e classifica o resultado da conversão.
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

    Retorna:
    - True, se a hipótese for confirmada;
    - False, se existirem pedidos sem data de entrega com outros status.

    Na prática, a hipótese só será confirmada se a distribuição de pedidos
    sem data de entrega tiver apenas o status 'canceled'.
    """
    distribuicao = resultado_pedidos["sem_data_entrega_por_status"]

    for status in distribuicao:
        # Usamos novamente a lambda para verificar se o status corresponde
        # a um pedido cancelado.
        if not eh_pedido_cancelado(status):
            return False

    return True