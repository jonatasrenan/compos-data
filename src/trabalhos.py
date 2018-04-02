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
    name = "%04d.%s" % (int(trabalho['#']), url.rsplit('.', 1)[-1])
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
            print("%s %s %s" % (e, trabalho['trabalho_link'], trabalho['#']))
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
    try:
        arq_entrada = os.path.join('./downloads', name)
    except:
        # HTTP error et
        return trabalho
    arq_saida = os.path.join('./htmls/%s.%s' % (name.rsplit('.', 1)[-2], "html"))

    if not os.path.isfile(arq_saida):
        if name.rsplit('.', 1)[-1].lower() == 'pdf':
            import os
            cwd = os.getcwd()
            import shlex
            # docker_command = shlex.split('docker run --rm -v %s:/app bwits/pdf2txt -W0 -L1 -t text -o %s %s' % (cwd, arq_saida, arq_entrada))
            # docker_command = shlex.split('docker run --rm -v %s:/app bwits/pdf2txt -t html -o %s %s' % (cwd, arq_saida, arq_entrada))
            command = ["pdf2txt", "-W0", "-L1", "-t", "text", "-o", arq_saida, arq_entrada]
            # print(command)
            proc = subprocess.Popen(command, stdout=subprocess.PIPE)
            with open(arq_saida + '.out', 'w') as file:
                file.write(proc.communicate()[0])
                file.close()
            with open(arq_saida + '.err', 'w') as file:
                file.write(proc.communicate()[1])
                file.close()

            trabalho['trabalho_texto'] = arq_saida
            print('Convertido pdf2txt: %s para %s' % (arq_saida, arq_entrada))
        else:
            print("Não é pdf %s %s %s" % (trabalho['trabalho_link'], trabalho['trabalho_arquivo'], trabalho['#']))
            trabalho['trabalho_texto'] = "ERRO"
    else:
        trabalho['trabalho_texto'] = arq_saida

    return trabalho
