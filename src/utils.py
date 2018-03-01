# -*- coding: utf-8 -*-
"""
    Funções genéricas

    jonatasrenan@dcc.ufmg.br
"""


def map(fn, l):
    """
    Redefinição da função map, paralela, aguarda threads no final e retorna resultado expandido em lista.
    :param fn: função
    :param l: lista
    :return: resultado do fn em l expandido em lista
    """
    import concurrent.futures
    threads = concurrent.futures.ThreadPoolExecutor(max_workers=20)
    result = threads.map(fn, l)
    threads.shutdown(wait=True)
    return list(result)


def flat(l):
    """
    Aplaina uma lista de lista
        ex: [[1,2,3],[4,5,6],[7,8,9]] = [1,2,3,4,5,6,7,8,9]
    :param l: lista de lista
    :return: lista
    """
    return [item for sublist in l for item in sublist]


def cria_csv(dics, nome_arquivo):
    """
    Cria CSV à partir de uma lista de dicionários
    :param dics: lista de dicionários
    :param nome_arquivo: nome do arquivo gerado
    :return: None
    """
    keys = dics[0].keys()
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
