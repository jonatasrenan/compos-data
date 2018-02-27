"""
    Download dos trabalhos do site compos.org.br

    jonatasrenan@dcc.ufmg.br
"""

def download(trabalho):
    """
    Baixa o trabalho na subpasta trabalhos
    :param trabalho: dicionario contendo os dados do trabalho
    :return:
    """
    from requests.utils import requote_uri
    import os, urllib

    url = trabalho['trabalho_link']
    name = url.rsplit('/', 1)[-1]
    filename = os.path.join('./trabalhos', name)
    url = requote_uri(url)
    if not url:
        exit
    if not os.path.isfile(filename):
        try:
            urllib.request.urlretrieve(url, filename)
        except:
            print("Erro: %s\n" % url)
