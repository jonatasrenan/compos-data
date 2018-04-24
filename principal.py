#!/bin/python3
# -*- coding: utf-8 -*-
"""
    Script principal

    jonatasrenan@dcc.ufmg.br
"""
from src.navegacao_web import obter_encontros, obter_gts, obter_trabalhos
from src.raspagem_texto import obter_campos
from src.trabalhos import download, doc2txt
from src.utils import flat, cria_csv, le_csv, pmap
import os


if not os.path.isfile('trabalhos.csv'):
    print('1 Navegação no site')
    print('- Navega encontros')
    encontros = obter_encontros()
    print('- Navega grupos de trabalhos')
    gts = flat(map(obter_gts, encontros))
    print('- Navega trabalhos')
    trabalhos = flat(map(obter_trabalhos, gts))
    print('- Indexa %s itens encontrados (#)' % len(trabalhos))
    trabalhos = list(map(lambda i: {'#': i[0], **i[1]}, enumerate(trabalhos)))
    print('- Salva dados dos trabalhos em CSV (trabalhos.csv)')
    cria_csv(trabalhos, 'trabalhos.csv')
else:
    print('1 Navegação no site prévia encontrada (para refazer, delete o arquivo trabalhos.csv)')
    trabalhos = le_csv('trabalhos.csv')

if not os.path.isfile('referencias.csv'):
    print('2 Raspagem dos PDFs')
    print('- Download de documentos dos trabalhos')
    trabalhos = pmap(download, trabalhos)
    print('- Converte documentos de PDF para texto')
    trabalhos = pmap(doc2txt, trabalhos)
    print('- Cria campos')
    referencias = flat(pmap(obter_campos, trabalhos))
    print('- Salva dados das referências em CSV (referencias.csv)')
    cria_csv(referencias, 'referencias.csv')
else:
    print('2 Raspagem prévia encontrada (para refazer, delete o arquivo referencias.csv)')
    referencias = le_csv('referencias.csv')

grupos = list(set([i['GTR'] for i in referencias]))
for grupo in grupos:
    ref_grupo = [i for i in referencias if i['GTR'] == grupo]
    cria_csv(ref_grupo, './grupos/%s.csv' % grupo.replace(' ', '_'))

print('4 Fim')

