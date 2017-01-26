# -*- coding: utf-8 -*-
"""
Created on Wed Jan 11 11:52:08 2017

@author: dan
"""

import settings
import pandas as pd

organism = 'Escherichia coli'    
entries = settings.read_data(organism+'_genome_info', sep='\t')
entries.drop_duplicates(subset=['bnumber'], inplace=True)

manual_replacememnts = {
'D0EX67':'b1107',
'D4HZR9':'b2755',
'P00452-2':'b2234',
'P02919-2':'b0149',
'Q2A0K9':'b2011',
'Q5H772':'b1302',
'Q5H776':'b1298',
'Q5H777':'b1297',
'Q6E0U3':'b3183',
'C9M2Y6':'b2755'}


entry2bnumber = entries.bnumber.copy()
for k,v in manual_replacememnts.iteritems():
    entry2bnumber[k] = v
    
p = settings.read_proteomics(organism, 'Schmidt etal 2016/copies_per_cell')
df = p.join(entry2bnumber, how='inner')
df.dropna(subset=['bnumber'], inplace=True)
df.set_index('bnumber', inplace=True)
settings.write_cache(df, organism+'_copies_cell')