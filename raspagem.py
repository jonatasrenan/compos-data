"""
    Limpeza dos dados do site compos.org.br

    jonatasrenan@dcc.ufmg.br
"""

import re

### Configuração do cache
import requests
import requests_cache
requests_cache.install_cache('cache')

### Seletor CSS
import lxml.html
from lxml.cssselect import CSSSelector


def raspar_encontro(seletor):
    nome = seletor.text
    cod = seletor.get('href')[-4:]
    ano = seletor.text.split()[1]
    local = ' '.join(seletor.text.split()[5:]).replace(' /', '/').replace('/ ', '/')
    id_response = requests.get('http://www.compos.org.br/anais_texto_por_gt.php?idEncontro=' + cod)
    id = re.search('xajax_carregaGt\(\'(.*)\'', id_response.text).group(1)
    return {'compos_id': id, 'compos_nome': nome, 'compos_cod': cod, 'compos_ano': ano, 'compose_local': local}


def raspar_gt(selector):
    nome = selector.text
    id = re.search('javascript:carregaObjetoAnais\((.*),', selector.get('href')).group(1)
    return {'gt_id': id, 'gt_nome': nome }


def raspar_trabalho(selector):
    link = CSSSelector('a')(selector)[0].get('href')
    titulo = CSSSelector('a')(selector)[0].text
    autor = [x for x in CSSSelector('p:nth-child(2)')(selector)[0].itertext()][1]
    return {'trabalho_link': link, 'trabalho_titulo': titulo, 'trabalho_autor': autor}

