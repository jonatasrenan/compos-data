# -*- coding: utf-8 -*-
"""
    Script principal

    jonatasrenan@dcc.ufmg.br
"""
from src.dados import obter_encontros, obter_gts, obter_trabalhos
from src.trabalhos import download
from src.utils import map, flat, criaCSV

print('# Obtém encontros')
encontros = obter_encontros()                               # Obtém encontros
print('# Obtém grupos de trabalhos')
gts = flat(map(obter_gts, encontros))                       # Obtém grupos de trabalhos
print('# Obtém trabalhos')
trabalhos = flat(map(obter_trabalhos, gts))                 # Obtém trabalhos
print('# Indexa %s itens encontrados (#)' % len(trabalhos))
trabalhos = map(lambda i: {'#': i[0], **i[1]}, enumerate(trabalhos))  # cria índice '#'
print('# Salva dados dos trabalhos em CSV')
criaCSV(trabalhos, './trabalhos.csv')                       # Salva dados dos trabalhos em CSV
print('# Baixa documentos dos trabalhos')
map(download, trabalhos)                                    # Baixa documentos dos trabalhos
