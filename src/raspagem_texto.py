# -*- coding: utf-8 -*-
"""
    Extração das teses em formato texto

    jonatasrenan@dcc.ufmg.br
"""


def limpeza(arquivo):
    """
    abre arquivo e faz uma limpeza inicial
        A limpeza consiste:
            - Caso não haja linha em branco entre 2 linhas elas serão concatenadas
    :param arquivo:
    :param arquivo:
    :return:
    """
    texto1 = list(open(arquivo))
    # Concatena
    texto2 = "".join([linha.strip(" ") for linha in texto1])

    # Remove caracteres não imprimíveis
    # método muito lento
    # from string import printable
    # printable = printable + "çÇãÃẽẼĩĨõÕũŨäÄëËïÏöÖüÜâÂêÊîÎôÔûÛáÁéÉíÍóÓúÚàÀèÈìÌòÒùÙ"
    # texto3 = "".join(char for char in texto2 if char in printable)
    texto3 = texto2

    def repl(texto):
        """
        Substitui várias substrings
        :param texto: texto inicial
        :return: texto modificado
        """
        #tratando caracteres invisíveis
        return texto.replace("\n\n\n", "\n\n") \
            .replace("\n \n", "\n\n") \
            .replace("---", "--") \
            .replace("___", "__") \
            .replace("–––", "––") \
            .replace("  ", " ") \
            .replace(" ", " ") \
            .replace("\t", " ")

    # repete repl(texto3) enquanto ouvir mudanca em texto3
    from src.utils import delta
    texto4 = delta(texto3, repl)
    # Divide as frases
    texto5 = texto4.split("\n\n")
    # Remove quebras na mesma frase
    texto6 = [linha.replace("\n", "") for linha in texto5]
    # strip linhas
    texto7 = [linha.strip() for linha in texto6]
    # remove uma linha que contém somente um número
    texto8 = [linha for linha in texto7 if not linha.isdigit()]
    # remove frases específicas
    texto9 = [
        linha for linha in texto8
        if not linha == 'Associação Nacional dos Programas de Pós-Graduação em Comunicação'
    ]
    return texto9


def obter_campos(trabalho):
    import os
    arquivo = trabalho['trabalho_texto']
    if not os.path.isfile(arquivo):
        print("ERRO %s não encontrado" % trabalho['trabalho_texto'])
        return
    texto = limpeza(arquivo)
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
    trabalho = obter_autores(trabalho, texto)

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


def obter_autores(trabalho, texto):
    """
    Obtem os autores do trabalho
    :param trabalho: dicionario contendo dados do trabalho
    :param texto: texto do arquivo do trabalho
    :return: trabalho com os autores incluídos
    """
    import re
    a = trabalho["trabalho_autor"]
    par = re.compile("\(.*?\)")
    instituicoes = re.findall(par, a)
    instituicoes = [i.replace(')', '').replace('(', '') for i in instituicoes]
    nomes = par.split(a)
    nomes = [nome.replace(',', '').strip() for nome in nomes if nome.strip() != ""]
    if len(nomes) != len(instituicoes):
        print('erro' % trabalho['#'])

    for n in enumerate(nomes):
        trabalho["AN%d" % (n[0]+1)] = n[1]
    for i in enumerate(instituicoes):
        trabalho["AI%d" % (i[0] + 1)] = i[1]

    return trabalho


def obter_palavras_chave(trabalho, texto):
    """
    Obtem palavras chaves do trabalho
    :param trabalho: dicionario contendo dados do trabalho
    :param texto: texto do arquivo do trabalho
    :return: trabalho com as palavras-chaves incluídas
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
    linhas = limpa(linhas, ['[0-9]\. ', '\.[0-9]'], substituto='.')

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
    pcs = [p for p in pcs if regex.sub('', p).strip() != ""]

    # remove número no final da palavra chave
    # TODO: melhorar isso, pode confundir com números que estão na palavra-chave
    regex = re.compile(' [0-9]$')
    pcs = [regex.sub('', p) for p in pcs]
    regex = re.compile('^[0-9] ')
    pcs = [regex.sub('', p) for p in pcs]

    #
    lista = []
    for i in reversed(pcs):
        if len(i) > 1:
            lista = lista + [i]
        if len(i) == 1:
            lista[len(lista)-1] = "%s. %s" % (i, lista[len(lista)-1])
    lista = reversed(lista)

    # salva palavras chaves
    for pc in enumerate(pcs):
        trabalho["PC%d" % (pc[0]+1)] = pc[1]

    return trabalho