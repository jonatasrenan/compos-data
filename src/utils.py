# -*- coding: utf-8 -*-
"""
    Funções genéricas

    jonatasrenan@dcc.ufmg.br
"""


def tmap(func, args, workers=10):
    """
    Redefinição da função map, multithread, aguarda threads no final e retorna resultado expandido em lista.
    :param func: função
    :param args: lista
    :param workers: número de threads máximo
    :return: resultado do mapeamento de fn em l expandido em lista
    """
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(workers) as ex:
        res = ex.map(func, args)
        ex.shutdown(wait=True)

    return list(res)


def pmap(func, args, workers=8):
    """
    Redefinição da função map, multiprocessos, aguarda processos no final e retorna resultado expandido em lista.
    :param func: função
    :param args: lista
    :param workers: número de processos máximo
    :return: resultado do mapeamento de fn em l expandido em lista
    """
    import concurrent.futures
    with concurrent.futures.ProcessPoolExecutor(workers) as ex:
        res = ex.map(func, args)
        ex.shutdown(wait=True)
    return list(res)


def flat(l):
    """
    Aplaina uma lista de lista
        ex: [[1,2,3],[4,5,6],[7,8,9]] = [1,2,3,4,5,6,7,8,9]
    :param l: lista de lista
    :return: lista
    """
    return [item for sublist in l for item in sublist]


def delta(dado, func):
    """
    Aplica func no dado enquanto ainda houver alterações no dado
    :param dado: dado inicial
    :param func: funcao aplicada
    :return: dado modificado diversas vezes pela funcao
    """
    delta = func(dado)
    while delta != dado:
        dado = delta
        delta = func(dado)
    return dado


def filtra(texto_completo, substrings, ignore_case=True):
    """
    Retorna somente linhas no texto completo que contem ao menos uma substring
    :param texto_completo: texto referencia
    :param substrings: lista de substrings
    :param ignore_case: ignorar case
    :return: linhas que contém ao menos uma das substrings
    """
    ret = []
    for l in texto_completo:
        for s in substrings:
            if ignore_case:
                linha = l.lower()
                palavra = s.lower()
            else:
                linha = l
                palavra = s
            if palavra in linha:
                if linha not in ret:
                    ret = ret + [linha]
    return ret


def limpa(texto_completo, substrings, ignore_case=True, substituto=""):
    """
    Remove lista de substring de um determinada string
    :param texto_completo: string
    :param substrings: lista de substrings
    :param ignore_case: ignorar case
    :param substituto: substitui por outro texto
    :return: texto sem as substrings
    """
    import re

    if type(substrings) is not list:
        substrings = [substrings]

    ret = []
    for l in texto_completo:
        line = l
        for substring in substrings:
            if ignore_case:
                regex = re.compile(substring, re.IGNORECASE)
                line = regex.sub(substituto, line)
            else:
                regex = re.compile(substring)
                line = regex.sub(substituto, line)
        ret = ret + [line]
    return ret


def cria_csv(dics, nome_arquivo, keys=None):
    """
    Cria CSV à partir de uma lista de dicionários
    :param dics: lista de dicionários
    :param nome_arquivo: nome do arquivo gerado
    :return: None
    """
    if not keys:
        keys = sorted(set().union(*(d.keys() for d in dics)))

    import csv
    with open(nome_arquivo, 'w') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(dics)


def le_csv(nome_arquivo):
    """
    Lê CSV e cria lista de dicionários
    :param nome_arquivo: csv
    :return: lista de dicionarios
    """
    import csv
    return list(csv.DictReader(open(nome_arquivo)))