# -*- coding: utf-8 -*-
"""
Created on Sun Jan  8 10:58:32 2017

@author: dan
"""
import settings
import pandas as pd
import re
import numpy as np

class BiGGProt():
    
    def __init__(self, organism):

        self.organism = organism        
        self.model = settings.get_model(organism)    
        self.flux = settings.read_data(settings.fluxes[self.organism])
        self.gene_info = settings.read_data(settings.genomes[self.organism],
                                            sep='\t')
        self.gene_info.set_index('bigg_id', inplace=True)
        self.reac2enzyme = self.reaction_to_isozymes()
#        self.copies_gCDW = settings.read_proteomics(self.organism, 
#                                            settings.abundances[self.organism])

#        self.mg_gCDW = settings.read_proteomics(self.organism, 
#                                    settings.abundances[self.organism])

#        self.conditions = self.flux.columns & self.abundance.columns
#        self.use_shared_conditions()

    def use_shared_conditions(self):
        self.flux = self.flux[self.conditions]
        self.abundance = self.abundance[self.conditions]
        self.abundance = self.abundance.loc[map(str, self.model.genes)]
        self.abundance.replace(0, np.nan, inplace=True)
        
    def reaction_to_enzyme_investemnt(self):
        df = pd.DataFrame(columns=['id', 'bnumber'])
        df['id'] = [r.id for r in self.model.reactions]
        df['bnumber'] = ["|".join(map(str,r.genes)) for r in self.model.reactions]
        df = settings.tidy_split(df, 'bnumber')
        df = df.merge(self.abundance, left_on='bnumber', right_index=True, how='left')
        
        df = df.groupby('id').sum()
        return df
        
    def reaction_to_isozymes(self):
        r_to_isozymes = {}
        for r in self.model.reactions:
            isozymes = r.gene_reaction_rule.split("or")
            isozymes = ['&'.join(re.findall(r"\b(?:(?!and)\w)+\b", iso)) 
                        for iso in isozymes]
            r_to_isozymes[r.id] = filter(None, isozymes)
            r_to_isozymes[r.id] = "|".join(isozymes)
        df = pd.DataFrame.from_dict(r_to_isozymes.items())
        
        df.columns = ['id', 'isozyme']
        df = settings.tidy_split(df, 'isozyme')
        df.isozyme = df.isozyme.apply(lambda x: x.split("&"))
        df.index = range(len(df))
        
        # map isoenzyme to mass in daltons
        isomass = []
        for iso in df.isozyme:
            try:
                isomass.append(self.gene_info.loc[iso, 'mass_dalton'].sum())
            except KeyError:
                isomass.append(np.nan)
                
        df['mass_dalton'] = isomass
        
        return df

    def map_isozyme_abundance(self):
        rxn2isozyme = self.reaction_to_isozymes()
        df = pd.DataFrame(index=rxn2isozyme.index,
                          columns=self.conditions)
        df[self.conditions] = np.nan
        for row in rxn2isozyme.itertuples():
            iso = row.isozyme.split("&")
            if len(iso) == 0:
                continue
            try:
                abund = self.abundance.loc[iso].sum(skipna=False)
                df.loc[row.Index, self.conditions] = abund
            except KeyError:
                continue
        df['isozyme'] = rxn2isozyme.isozyme
        df['id'] = rxn2isozyme.id
        df = df[['id', 'isozyme']+list(self.conditions)]
        return df

    def mass_of_active_enzymes(self):
        rxn2isomass = self.map_isozyme_abundance()
        df = rxn2isomass.groupby('id').sum()
        df.drop('isozyme', axis=1, inplace=True)
        return df
    
if __name__ == '__main__':
    organism = 'Escherichia coli'    
    P = BiGGProt(organism)
#    settings.write_cache(P.reaction_to_enzyme_investemnt(), 'reaction2mass')