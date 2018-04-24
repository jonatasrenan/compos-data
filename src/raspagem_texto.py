# -*- coding: utf-8 -*-
"""
    Extração das teses em formato texto

    jonatasrenan@dcc.ufmg.br
"""

# expressão regular para obter autor na referencia
re_autor = \
    '''(^\_{3,}\.|^([A-Z]{2,}|Mc)[A-Z\- \']*(, *(((\.|)( |)[A-Z]){1,}|[A-Z][A-Z \-a-z\']*|)''' + \
    '''(\([0-9]{2,4}[A-Za-z]{0,2}\)\.*|\.|\;|et al\.*)|.))'''

#    '''(^\_{3,}\.|^([A-Z]{2,}|Mc)[A-Z\- ]*(, *(((\.|)( |)[A-Z]){1,}|[A-Z][A-Z \-a-z]*|)''' + \
#   '''(\([0-9]{2,4}[A-Za-z]{0,2}\)\.*|\.|\;|et al\.*)|.))'''

# '''(^\_{3,}\.|^([A-Z]{2,}|Mc)[A-Z\- ]*(, *(((\.|)( |)[A-Z]){1,}|[A-Z][A-Z \-a-z]*|)(\.|\;|et al\.*)|\.))'''


def limpeza_inicial(nome_arquivo):
    """
    Abre arquivo e faz uma limpeza inicial:
        Remove acentos
        Remove caracteres não imprimíveis
        Remove expressões destinadas a cabeçalhos e rodapés, número de paǵina
        Sanitiza a linha
    :param nome_arquivo:
    :return:
    """

    import os
    if not nome_arquivo:
        return

    if not os.path.isfile(nome_arquivo):
        print("ERRO %s não encontrado" % nome_arquivo)
        return

    if len(nome_arquivo) == 0:
        print("Arquivo vazio %s" % nome_arquivo)
        return

    texto = list(open(nome_arquivo))

    def remove_acentos(linha):
        import unidecode
        return unidecode.unidecode(linha)

    def remove_nao_imprimiveis(linha):
        from string import printable
        return "".join(char for char in linha if char in printable)  # método muito lento

    subs = [  # subs[0] = expressão regular,  subs[1] = valor a ser substituído
        ("\n\n\n", "\n\n"),
        ("\n \n", "\n\n"),
        ("---", "--"),
        ("____", "___"),
        ("–––", "––"),
        ("  ", " "),
        (" ", " "),
        ("\t", " "),
        (" \n", " "),
        ('Associacao.*?Nacional.*?em.*?Comunicacao', ""),
        ('((?=[^\Wa]*X)(?=[^\Wb]*V)(?=[^\Wb]*I)\w+.*?|)Encontro.*?[0-9]{4}', ""),
        ('www.compos.org.br/anais_encontros.php', ""),
        ('www.compos.org.br', ""),
        ('/anais_encontros.php', "")
    ]

    # compila expressoes regulares
    import re
    subs = list(map(lambda sub: (re.compile(sub[0]), sub[1]), subs))

    # substitui enquanto ainda fazer diferença na linha
    def substituicoes(linha):

        # aplica 1 passo de substituicoes em l
        def passo(l):
            for sub in subs:
                l = sub[0].sub(sub[1], l)
            return l

        # executa funcao passo recursivamente em linha enquanto ainda houver efeito
        from src.utils import delta
        return delta(linha, passo)

    texto = map(remove_acentos, texto)
    texto = map(remove_nao_imprimiveis, texto)
    texto = map(substituicoes, texto)
    texto = map(lambda x: x.strip(), texto)
    texto = list(filter(lambda x: not x.isdigit(), texto))
    texto = list(filter(lambda x: x, texto))

    return texto


def obter_campos(trabalho):
    """
    Adiciona campos que são relacionados ao presente trabalho
    :param trabalho: Trabalho inicial
    :return: Lista de todas as referências do trabalho com os campos
    """
    # ATM 	Área temática do Projeto
    trabalho['ATM'] = ''

    # GTR 	Nome do Grupo de Trabalho da Compós
    trabalho['GTR'] = trabalho['gt_nome']
    # ANO 	Ano de publicação
    trabalho['ANO'] = trabalho['compos_ano']
    # LOC 	Local da Compós
    trabalho['LOC'] = trabalho['compos_local']
    # ARQ 	Nome do arquivo
    trabalho['ARQ'] = trabalho['trabalho_link']
    # ART 	Título do artigo
    trabalho['ART'] = trabalho['trabalho_titulo']

    # ANX 	Nome do autor X do artigo
    # AIX 	Instituição do autor 1 do artigo
    # ANX 	Nome do autor X do artigo
    trabalho = obter_autores(trabalho)

    if 'trabalho_texto' in trabalho and \
            trabalho['trabalho_texto'] and \
            '.pdf' in trabalho['trabalho_link']:
        texto = limpeza_inicial(trabalho['trabalho_texto'])

        # PCX   Palavras chave
        trabalho = obter_palavras_chave(trabalho, texto)

        # RAX 	Nome do autor X da referência
        # RNX 	Nacionalidade do autor X da referência
        # RMX 	Indicação se o autor X da referência é membro do GT
        # OBR 	Título da obra referenciada
        # ATC 	Indicação de autocitação (autor do artigo é o mesmo autor referenciado)
        trabalhos = obter_referencias(trabalho, texto)
    else:
        trabalhos = [trabalho]

    # Remoção de chaves intermediárias
    chaves_intermediarias = ['trabalho_link', 'trabalho_titulo', 'trabalho_autor', 'gt_id', 'gt_nome', 'compos_id',
                             'compos_nome', 'compos_cod', 'compos_ano', 'compos_local', 'trabalho_arquivo',
                             'trabalho_texto']
    trabalhos = [{k: v for k, v in trabalho.items() if k not in chaves_intermediarias} for trabalho in trabalhos]

    print('Fim #%s' % trabalho["#"])

    return trabalhos


def obter_referencias(trabalho, texto):
    """
    Obtém os campos que são relacionados as referências do trabalho
    :param trabalho:
    :param texto:
    :return: Referências do trabalho
    """

    def limpar(texto):
        """
        Limpa tese deixando somente as referências uma por linha
        :param texto: Texto da tese
        :return: Referências da bibliografia da tese, uma por linha
        """
        import re
        texto = '<linha />'.join(texto)
        texto = re.sub('.*Referencias', '', texto)
        texto = re.sub('.*Referencia', '', texto)
        texto = re.sub('.*bibliograficas', '', texto)
        texto = re.sub('.*Bibliografia', '', texto)
        texto = re.sub('Filmografia.*', '', texto)
        texto = re.sub('Reportagens.*', '', texto)
        texto = texto.split('<linha />')
        texto = list(filter(lambda x: x, texto))

        linhas_concatenadas = []
        for linha in texto:
            if re.search(re_autor, linha):  # é uma nova referencia
                linhas_concatenadas = linhas_concatenadas + [linha]
            else:  # é continuação da anterior
                if len(linhas_concatenadas) != 0:
                    try:
                        linhas_concatenadas[-1] = linhas_concatenadas[-1] + ' ' + linha
                        linhas_concatenadas[-1] = linhas_concatenadas[-1].replace('  ', ' ')
                    except Exception as e:
                        print(e)
                        print(linha)

        return linhas_concatenadas

    def raspar(linha):
        '''
        Separa autores do resto da linha da referência
        :param linha: Uma linha contendo uma referência bibliográfica completa
        :return: Lista de Autores e Resto da linha
        '''
        import re
        lista_autores = []
        while re.search(re_autor, linha):
            lista_autores = lista_autores + [re.search(re_autor, linha).group(0)]
            linha = re.sub('^' + re.escape(re.search(re_autor, linha).group(0)), "", linha)
            linha = re.sub('^ *\. *|^ *, *|^ *; *', '', linha)
            linha = linha.strip()
        return lista_autores, linha

    texto = limpar(texto)
    referencias = list(map(raspar, texto))

    import re
    ultimos_autores = ""
    trabalhos = []
    for autores, titulo in referencias:
        import copy
        trabalho_referencia = copy.deepcopy(trabalho)

        # quando os autores são descritos como ___. significa que são os mesmos autores da linha anterior.
        if autores[0] == "___.":
            autores = ultimos_autores
        else:
            ultimos_autores = autores

        # se ocorrer 'et al.' significa que existem mais autores não-declarados
        etal_nos_autores = bool(len(list(filter(lambda autor: re.search('.*et al.*', autor), autores))))
        etal_no_titulo = bool(re.search('.*et al', titulo))
        if etal_no_titulo or etal_nos_autores:
            titulo = re.sub('.*et al[. ;,]*', '', titulo)
            autores = list(map(lambda autor: re.sub(' *et al[. ;,]*', '', autor), autores))
            autores = autores + ['et al.']

        # OBR 	Título da obra referenciada
        # trabalho["OBR"] = re.search(".*?\.", titulo).group(0)
        trabalho_referencia['OBR'] = titulo

        # RAX 	Nome do autor X da referência
        for autor in enumerate(autores):
            trabalho_referencia['RA%d' % (autor[0] + 1)] = autor[1]

        # TODO: RNX 	Nacionalidade do autor X da referência
        # TODO: RMX 	Indicação se o autor X da referência é membro do GT
        # TODO: ATC 	Indicação de autocitação (autor do artigo é o mesmo autor referenciado)

        trabalhos = trabalhos + [trabalho_referencia]

    return trabalhos


def obter_autores(trabalho):
    """
    Obtem os autores do trabalho
    :param trabalho: dicionario contendo dados do trabalho
    :param texto: texto do arquivo do trabalho
    :return: trabalho com os autores incluídos
    """
    import re
    partes = re.split(',', trabalho['trabalho_autor'])
    autores = []
    for parte in partes:
        instituicao = ''
        if re.search('\(.*?\)', parte):  # se encontra texto entre parênteses é a instituição
            instituicao = re.search('\(.*?\)', parte).group(0).replace(')', '').replace('(', '')
        autor = parte.replace("(" + instituicao + ')', '').replace(',', '').strip()
        autores = autores + [(autor, instituicao)]

    for autor in enumerate(autores):
        id, (nome, instituicao) = autor
        trabalho['AN%d' % (id + 1)] = nome
        trabalho['AI%d' % (id + 1)] = instituicao

    return trabalho


def obter_palavras_chave(trabalho, texto):
    """
    Obtem palavras chaves do trabalho
    :param trabalho: dicionario contendo dados do trabalho
    :param texto: texto do arquivo do trabalho
    :return: trabalho com as palavras-chaves incluídas
    """
    import re

    def obtem_primeira_linha_contendo_padrao(padrao, texto):
        texto_enumerado = list(enumerate(texto))
        try:
            return list(filter(lambda i: re.search(padrao, i[1], flags=re.IGNORECASE), texto_enumerado))[0][0]
        except IndexError as e:
            return -1

    re_palavraschave = \
        '''(.*palavras\-chave|.*palavras chave|.*palavra chave|.*palavra\-chave|.*avras\-chave|.*PalavrasChave)'''

    primeira = obtem_primeira_linha_contendo_padrao(re_palavraschave, texto)

    if primeira == -1:  # não encontrou linha de
        print("Não encontrou palavras-chave para o #%s" % (trabalho["#"]))
        return trabalho

    # se o tamanho da linha for comprido o bastante para estar completa e
    # a linha abaixo não contiver abstract, próxima linha é continuação
    if len(texto[primeira]) > 75 and not re.search("Abstract", texto[primeira + 1], flags=re.IGNORECASE):
        linha = texto[primeira] + texto[primeira + 1]
    else:
        linha = texto[primeira]

    linha = re.sub(re_palavraschave, "", linha, flags=re.IGNORECASE)
    linha = re.sub(':', '', linha, flags=re.IGNORECASE)
    linha = re.sub('\n', ' ', linha, flags=re.IGNORECASE)
    linha = re.sub('[0-9]\. ', ' ', linha, flags=re.IGNORECASE)
    linha = re.sub('\.[0-9]', ' ', linha, flags=re.IGNORECASE)
    linha = re.sub(' {2,}', ' ', linha, flags=re.IGNORECASE)

    # quebra linha em tokens
    pcs = [p for p in re.split('\.|,|;|–', linha)]
    pcs = [p.strip() for p in pcs]
    pcs = [p for p in pcs if p]

    # Caso específico quando artigo não tem palavra chave e uma linha no meio do texto inicia com 'palavra chave'
    # Exemplo JORNALISMO : CENÁRIOS E TENDÊNCIAS de Ruth Reis (2123 http://www.compos.org.br/data/biblioteca_718.pdf)
    # contornado verificando se palavra chave contem mais de 6 sub-palavras
    for pc in pcs:
        if len(pc.split(' ')) > 6:
            return trabalho

    # remove palavra se ela não contém nenhum caractere alfabético
    regex = re.compile('[^a-zA-Z]')
    pcs = [p for p in pcs if regex.sub('', p).strip() != ""]

    # remove número no final da palavra chave
    # TODO: melhorar isso, pode confundir com números que estão na palavra-chave
    regex = re.compile(' [0-9]$')
    pcs = [regex.sub('', p) for p in pcs]
    regex = re.compile('^[0-9] ')
    pcs = [regex.sub('', p) for p in pcs]

    lista = []
    for i in reversed(pcs):
        if len(i) > 1:
            lista = lista + [i]
        if len(i) == 1 and len(lista) > 0:
            lista[len(lista) - 1] = '%s. %s' % (i, lista[len(lista) - 1])
    lista = reversed(lista)

    # salva palavras chaves
    for pc in enumerate(pcs):
        trabalho['PC%d' % (pc[0] + 1)] = pc[1]

    return trabalho
