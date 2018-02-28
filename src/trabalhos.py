# -*- coding: utf-8 -*-
"""
    Download dos trabalhos do site compos.org.br

    jonatasrenan@dcc.ufmg.br
"""


def download(trabalho):
    """
    Baixa o trabalho na subpasta downloads
    :param trabalho: dicionario contendo os dados do trabalho
    :return: None
    """
    from requests.utils import requote_uri
    import os, urllib
    url = trabalho['trabalho_link']
    name = "%04d.%s" % (trabalho['#'], url.rsplit('.', 1)[-1])
    path = os.path.join('./downloads', name)
    url = requote_uri(url)
    if not url:
        exit
    if not os.path.isfile(path):
        try:
            urllib.request.urlretrieve(url, path)
        except urllib.error.HTTPError as e:
            return print("%s %s" % (e, trabalho['trabalho_link']))
        print('Baixado (%s): %s' % (trabalho['#'], trabalho['trabalho_link']))
