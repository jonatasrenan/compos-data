# -*- coding: utf-8 -*-
"""
    Extração das teses em formato texto

    jonatasrenan@dcc.ufmg.br
"""


def trabalho_texto(arquivo):
    """
    abre arquivo e faz uma limpeza inicial
        A limpeza consiste:
            - Caso não haja linha em branco entre 2 linhas elas serão concatenadas
    :param arquivo:
    :param arquivo:
    :return:
    """
    texto1 = list(open(arquivo))
    texto2 = [linha.strip(" ") for linha in texto1]
    texto3 = "".join(texto2)
    texto4 = texto3.replace("\t", " ")

    texto5 = texto4.replace("\n\n\n", "\n\n")
    texto5 = texto5.replace("\n \n", "\n\n")
    texto5 = texto5.replace("---", "--")
    texto5 = texto5.replace("___", "__")
    texto5 = texto5.replace("–––", "––")
    texto5 = texto5.replace("  ", " ")
    while texto4 != texto5:
        texto4 = texto5
        texto5 = texto5.replace("\n\n\n", "\n\n")
        texto5 = texto5.replace("\n \n", "\n\n")
        texto5 = texto5.replace("---", "--")
        texto5 = texto5.replace("___", "__")
        texto5 = texto5.replace("–––", "––")
        texto5 = texto5.replace("  ", " ")


    texto6 = texto5.split("\n\n")
    texto7 = [linha.replace("\n", "") for linha in texto6]
    texto8 = [linha.strip() for linha in texto7]
    texto9 = [linha for linha in texto8 if not linha.isdigit()]

    texto10 = [
        linha for linha in texto9
        if not linha == 'Associação Nacional dos Programas de Pós-Graduação em Comunicação'
    ]
    return texto10


def obter_campos(trabalho):
    import os
    arquivo = trabalho['trabalho_texto']
    if not os.path.isfile(arquivo):
        print("ERRO %s não encontrado" % trabalho['trabalho_texto'])
        return
    texto = trabalho_texto(arquivo)
    if len(texto) == 0:
        print("Arquivo vazio %s" % trabalho['trabalho_texto'])
        return

    # ATM 	Área temática do Projeto

    # GTR 	Nome do Grupo de Trabalho da Compós
    trabalho['GTR'] = trabalho['gt_nome']
    # ANO 	Ano de publicação
    trabalho['ANO'] = trabalho['compos_ano']
    # LOC 	Local da Compós
    trabalho['LOC'] = trabalho['compos_local']
    # ARQ 	Nome do arquivo
    trabalho['ARQ'] = trabalho['trabalho_arquivo']
    # ART 	Título do artigo
    trabalho['ART'] = trabalho['trabalho_titulo']

    # AN1 	Nome do autor 1 do artigo
    # AI1 	Instituição do autor 1 do artigo
    # AN2 	Nome do autor 2 do artigo
    # AI2 	Instituição do autor 2 do artigo
    # AN3 	Nome do autor 3 do artigo
    # AI3 	Instituição do autor 3 do artigo
    # AN4 	Nome do autor 4 do artigo
    # AI4 	Instituição do autor 4 do artigo
    # RA1 	Nome do autor 1 da referência
    # RN1 	Nacionalidade do autor 1 da referência
    # RM1 	Indicação se o autor 1 da referência é membro do GT
    # RA2 	Nome do autor 2 da referência
    # RN2 	Nacionalidade do autor 2 da referência
    # RM2 	Indicação se o autor 2 da referência é membro do GT
    # RA3 	Nome do autor 3 da referência
    # RN3 	Nacionalidade do autor 3 da referência
    # RM3 	Indicação se o autor 3 da referência é membro do GT
    # RA4 	Nome do autor 4 da referência
    # RN4 	Nacionalidade do autor 4 da referência
    # RM4 	Indicação se o autor 4 da referência é membro do GT
    # OBR 	Título da obra referenciada

    # ATC 	Indicação de autocitação (autor do artigo é o mesmo autor referenciado)

    # PC1-PC8
    trabalho = obter_palavras_chave(trabalho, texto)

    return trabalho


def obter_palavras_chave(trabalho, texto):
    """
    Obtem palavras chaves do texto do trabalho
    :param trabalho: dicionario contendo dados do trabalho
    :param texto: texto do arquivo do trabalho
    :return: 
    """
    import re
    from src.utils import filtra

    # filtra texto por linhas que contenham palavras
    filtro = ['palavras-chave', 'palavras chave', 'palavra chave']
    linhas = filtra(texto, filtro)

    # remove palavras das linhas
    from src.utils import limpa
    remover = [
        ".*" + re.escape('palavras-chave'),
        ".*" + re.escape('palavras chave'),
        ".*" + re.escape('palavra chave'),
        ':', '\n',
        re.escape('abstract')+".*"
    ]
    linhas = limpa(linhas, remover)

    # troca palavras por outras
    linhas = limpa(linhas, '  ', substituto=' ')
    linhas = limpa(linhas, ['[0-9]\.', '\.[0-9]'], substituto='.')

    # mantém só a primeira linha
    if len(linhas) == 0:
        return trabalho
    linha = linhas[0]

    # quebra linha em tokens
    import re
    pcs = [p for p in re.split('\.|,|;|–', linha)]
    pcs = [p.strip() for p in pcs]
    pcs = [p for p in pcs if p]

    # remove palavra se ela não contém nenhum caractere alfabético
    regex = re.compile('[^a-zA-Z]')
    pcs = [p for p in pcs if regex.sub('', p).strip != ""]

    # remove número no final da palavra chave
    # comentado pois confunde com a palavra-chave "Anos 50"
    # regex = re.compile('[0-9]$')
    # pcs = [regex.sub('', p) for p in pcs]

    # salva palavras chaves
    for pc in enumerate(pcs):
        trabalho["PC%d" % (pc[0]+1)] = pc[1]

    return trabalho