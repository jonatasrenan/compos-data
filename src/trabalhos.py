# -*- coding: utf-8 -*-
"""
    Download dos trabalhos do site compos.org.br

    jonatasrenan@dcc.ufmg.br
"""

def download(trabalho):
    """
    Baixa o trabalho na subpasta downloads
    :param trabalho: dicionario contendo os dados do trabalho
    :return: trabalho atualizado
    """
    from requests.utils import requote_uri
    import os, urllib

    url = trabalho['trabalho_link']
    name = "%04d.%s" % (trabalho['#'], url.rsplit('.', 1)[-1])
    path = os.path.join('./downloads', name)
    url = requote_uri(url)
    trabalho['trabalho_arquivo'] = name
    if not url:
        trabalho['trabalho_arquivo'] = "HTTP Error: Falta URL"
        print('Falta URL: %s' % trabalho['#'])
    if not os.path.isfile(path):
        try:
            urllib.request.urlretrieve(url, path)
            print('Baixado (%s): %s' % (trabalho['#'], trabalho['trabalho_link']))
        except urllib.error.HTTPError as e:
            print("%s %s" % (e, trabalho['trabalho_link']))
            trabalho['trabalho_arquivo'] = e
    return trabalho


def doc2txt(trabalho):
    """
    Converte arquivo baixado para formato texto na subpasta textos
    :param trabalho:
    :return: trabalho atualizado
    """
    import os
    import subprocess

    name = trabalho['trabalho_arquivo']
    arq_entrada = os.path.join('./downloads', name)
    arq_saida = os.path.join('./textos/%s.%s' % (name.rsplit('.', 1)[-2], "txt"))

    if name.rsplit('.', 1)[-1].lower() == 'pdf':
        text = subprocess.Popen(["pdf2txt", "-t", "text", "-o", arq_saida, arq_entrada], stdout=subprocess.PIPE)
        output = text.communicate()[0]
        trabalho['trabalho_texto'] = arq_saida
        print('Convertido pdf2txt: %s para %s' % (arq_saida, arq_entrada))
        return trabalho
    else:
        print("Não é pdf %d %d %d" % (trabalho['trabalho_link'], trabalho['trabalho_arquivo'], trabalho['#']))
        trabalho['trabalho_text'] = "ERRO"
        return trabalho
