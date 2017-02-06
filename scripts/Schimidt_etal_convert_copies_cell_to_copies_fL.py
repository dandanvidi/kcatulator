# -*- coding: utf-8 -*-
"""
Created on Sun Jan 29 11:29:34 2017

@author: dan
"""
import settings

info = settings.read_data('eco_[genome_info]')
conditions = settings.read_data('conditions_index')
volume = conditions['single_cell_volume_[fL]']
fg = info['mass_dalton'] * settings.dalton_2_fg 
fg.drop_duplicates(inplace=True)

copies_cell = settings.read_data('eco_[copies_per_cell]_[schmidt_etal_2016]')
copies_cell.drop_duplicates(inplace=True)
copies_fL = copies_cell.div(volume,axis=1)

fg = fg.loc[copies_fL.index]
fg_fL = copies_fL.mul(fg, axis=0)

fg_fL.dropna(how='all', inplace=True)
copies_fL = copies_fL.loc[fg_fL.index].dropna()

