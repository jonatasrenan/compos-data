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

    # remove acentos
    import unidecode
    texto3 = unidecode.unidecode(texto2) # remoção de acentos

    # Remove caracteres não imprimíveis
    # método muito lento
    from string import printable
    # printable = printable + "çÇãÃẽẼĩĨõÕũŨäÄëËïÏöÖüÜâÂêÊîÎôÔûÛáÁéÉíÍóÓúÚàÀèÈìÌòÒùÙ"
    texto4 = "".join(char for char in texto3 if char in printable)

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
    texto5 = delta(texto4, repl)

    # Divide as frases
    texto6 = texto5.split("\n\n")
    # Remove espaco+quebras na mesma frase
    texto7 = [linha.replace(" \n", "") for linha in texto6]
    # Remove quebras na mesma frase
    texto7 = [linha.replace("\n", "") for linha in texto7]
    # strip linhas
    texto8 = [linha.strip() for linha in texto7]

    # remove uma linha que contém somente um número
    texto9 = [linha for linha in texto8 if not linha.isdigit()]
    # remove frases específicas
    # texto10 = [
    #     linha for linha in texto9
    #     if linha not in [
    #
    #
    #     ] and linha.strip()
    # ]
    texto10 = texto9
    texto11 = "<quebra/>".join(texto10)

    def remove(expr, st):
        import re
        rg = re.compile(expr)
        return rg.sub('', st)

    texto12 = texto11
    lista_expr = [
        'Associacao.*?Nacional.*?em.*?Comunicacao',
        '((?=[^\Wa]*X)(?=[^\Wb]*V)(?=[^\Wb]*I)\w+.*?|)Encontro.*?[0-9]{4}',
        'www.compos.org.br/anais_encontros.php',
        'www.compos.org.br',
        '/anais_encontros.php'
    ]
    for expr in lista_expr:
        texto12 = remove(expr, texto12)

    texto13 = texto12.split("<quebra/>")

    texto14 = [l for l in texto13 if l]

    return texto14


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

    # ANX 	Nome do autor X do artigo
    # AIX 	Instituição do autor 1 do artigo
    # ANX 	Nome do autor X do artigo
    trabalho = obter_autores(trabalho, texto)

    # RAX 	Nome do autor X da referência
    # RNX 	Nacionalidade do autor X da referência
    # RMX 	Indicação se o autor X da referência é membro do GT


    # OBR 	Título da obra referenciada
    # ATC 	Indicação de autocitação (autor do artigo é o mesmo autor referenciado)

    # from src.utils import apos
    # referencias = apos("Referências", texto)
    # referencias = "\n".join(referencias)

    # from src.utils import ate
    # finaliza = ['\n', "Filmografia", "Reportagens"]
    # referencias = ate("\n", texto)

    trabalho = obter_referencias(trabalho, texto)

    # PC1-PC8
    trabalho = obter_palavras_chave(trabalho, texto)

    return trabalho

def limpeza_referencias(texto):
    import re
    ref1 = " ".join(texto)
    regex = re.compile("\n")
    ref2 = regex.sub("", ref1)
    regex = re.compile(".*Referencias")
    ref3 = regex.sub("", ref2)
    regex = re.compile(".*bibliograficas", )
    ref3 = regex.sub("", ref3)
    regex = re.compile("Filmografia.*")
    ref4 = regex.sub("", ref3)
    regex = re.compile("Reportagens.*")
    ref5 = regex.sub("", ref4)
    return ref5

def obter_referencias(trabalho, texto):
    texto = limpeza_referencias(texto)

    import re
    regex = re.compile('\(.*?\)')  # remover parênteses
    texto = regex.sub("", texto)
    regex = [
        "(",
            "[A-Z\- ]{2,}",     # primeiro nome em alta
            ",\ *",               # obrigatóriamente tem uma ',' e ' '
            "[A-Z \-a-z]*"       # segunda palavra não é em alta
            "[.;,]",
            "(",                #uma ou mais iniciais.
                " [A-Z]\.",
                "|",
            ")*",
            "|",                #ou
            "[A-Z\- ]* et al"  # primeiro nome em alta + " et al"
        ")"
    ]

    # Muito bom! > "([A-Z\- ]{2,}[,.]\ *[A-Z \-a-z]*[.;,]( [A-Z]\.|)*|[A-Z\- ]* et al)"

    # tratar quando tiver um " e "
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
