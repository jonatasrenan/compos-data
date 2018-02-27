"""
    Extração dos dados do site compos.org.br

    jonatasrenan@dcc.ufmg.br
"""

from raspagem import raspar_encontro, raspar_gt, raspar_trabalho


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


def acessar(endereco, dados, seletor):
    """
    Acessa o "endereço" utilizando o método POST e enviando "dados";
    filtra resposta utilizando um determinado "seletor" CSS
    :param endereco: endereço a ser acessado
    :param dados: campos enviados na requisição post
    :param seletor: seletor aplicado na resposta da requisição
    :return: resultados da seleção
    """
    import requests
    import requests_cache
    import lxml.html
    from lxml.cssselect import CSSSelector

    requests_cache.install_cache('cache')
    resposta = requests.post(endereco, data=dados)
    conteudo = lxml.html.fromstring(resposta.content)
    return CSSSelector(seletor)(conteudo)


def obter_encontros():
    """
    Obtém todos os encontros do site
    :return: lista dos encontros
    """

    endereco = 'http://www.compos.org.br/anais_encontros.php'
    dados = {'xajax': 'carregaObjetoAnaisEncontro'}
    seletor = 'a'
    selecoes = acessar(endereco, dados, seletor)
    return map(raspar_encontro, selecoes)


def obter_gts(encontro):
    """
    Obtém todos os gts de um determinado encontro
    :param encontro: dicionário contendo dados do encontro
    :return: lista dos GTs
    """
    endereco = 'http://www.compos.org.br/anais_texto_por_gt.php?idEncontro=%s' % encontro['compos_cod']
    dados = {'xajax': 'carregaGt', 'xajaxargs[]': encontro['compos_id']}
    seletor = 'a'
    selecoes = acessar(endereco, dados, seletor)
    gts = map(raspar_gt, selecoes)
    [gt.update(encontro) for gt in gts]
    return gts



def obter_trabalhos(gt):
    """
    Obtém todos os trabalhos de um determinado GT
    :param gt: dicionario contendo dados do GT
    :return: lista dos trabalhos do GT
    """
    endereco = 'http://www.compos.org.br/anais_texto_por_gt.php?idEncontro=%s' % gt['compos_cod']
    dados = {'xajax': 'carregaObjetoAnais', 'xajaxargs[]': [gt['gt_id'], gt['compos_id']]}
    seletor = '.boxLine'
    selecoes = acessar(endereco, dados, seletor)
    trabalhos = map(raspar_trabalho, selecoes)
    [trabalho.update(gt) for trabalho in trabalhos]
    return trabalhos

flat = lambda l: [item for sublist in l for item in sublist]
encontros = obter_encontros()
gts = flat(map(obter_gts, encontros))
trabalhos = flat(map(obter_trabalhos, gts))

import csv
keys = trabalhos[0].keys()
with open('trabalhos.csv', 'w') as output_file:
    dict_writer = csv.DictWriter(output_file, keys)
    dict_writer.writeheader()
    dict_writer.writerows(trabalhos)
