import pandas as pd
from cobra.core import Reaction as R

from copy import deepcopy
import csv
import json
import settings
import numpy as np
from proteomics import BiGGProt
#import catalyic_rates

class CACHE(BiGGProt):
    def __init__(self, organism):        
        
        self.organism = organism        
        self.model = settings.get_model(organism)    

        self.flux = settings.read_data(settings.fluxes[self.organism])
        self.flux = self.flux * 1e3 / 60. # umol/gCDW/min
        
        self.abundance = settings.read_data(settings.abundances[self.organism])
        self.abundance = self.abundance * 1e3 # mg/gCDW
        
        self.conditions = self.flux.columns & self.abundance.columns
        
        self.bigg2ec = self.load_bigg_reaction_to_ec_df()
        
        self.reactions = self.reaction_information_df()
        self.genes = self.gene_information_df()
        
        self.searchin = self.searchables()

        self.kcat = self.model_kcat_df()
        self.specific_activity = self.specific_activity()
        
    @staticmethod
    def load_BRENDA_turnover_data():
        kcat = pd.DataFrame.from_csv(settings.DATA_DIR+"/turnover.csv")
        kcat = kcat[kcat>0]
        kcat = kcat[(pd.isnull(kcat['Commentary'])) |
                  ((kcat['Commentary'].str.find('mutant') == -1) &
                  (kcat['Commentary'].str.find('mutation') == -1))]
        # remove values with unmatched ligand
        kcat = kcat[pd.notnull(kcat['bigg.metabolite'])]
        kcat['bigg.metabolite'] = kcat['bigg.metabolite'].str.lower()
        
        return kcat
        
    @staticmethod    
    def load_bigg_reaction_to_ec_df():
        bigg2ec = []
    
        # a few manual fixes for missing EC numbers in the model
        bigg2ec.append(('FHL', '1.1.99.33'))
        bigg2ec.append(('GDMANE', '1.1.1.271'))
        
        with open(settings.DATA_DIR+'/bigg_models_reactions.txt', 'r') as fp:
            csv_reader = csv.reader(fp, delimiter='\t')
            csv_reader.next()
            for row in csv_reader:
                bigg_id = row[0]
                database_links = json.loads(row[3])
                if 'EC Number' in database_links:
                    for d in database_links['EC Number']:
                        bigg2ec.append((bigg_id, d['id']))
    
        df = pd.DataFrame(bigg2ec, columns=['reaction', 'ec_number'])
        
        # adding the real EC number for Pyruvate Dehydrogenase (PDH)
        # since BiGG only has the number for Dihydrolipoyllysine-residue
        # acetyltransferase which is a transient binding of the acyl
        # group to a modified lysine on the enzyme complex
        df['ec_number'][df.reaction=='PDH'] = '1.2.4.1'
        
        return df

    @staticmethod
    def _trim_reverse(reactions):
        l = map(lambda x: x.replace('_reverse', ''), reactions)
        return l
                
    def reaction_information_df(self):
        
        df = pd.DataFrame(columns=['reaction', 'id'])
        df['id'] = map(lambda x: x.id, self.model.reactions)

        df['reaction_name'] = map(lambda x: x.name, self.model.reactions)
        df['reaction_string'] = map(lambda x: R.build_reaction_string(x, 
                                          use_metabolite_names=True), 
                                          self.model.reactions)
        
        df['reaction_string'] = map(lambda x: x.replace('-->', '='),
                                      df['reaction_string'])
        
        df['reaction'] = self._trim_reverse(df.id)
        
        df = df.merge(self.bigg2ec, how='left')
        df.drop_duplicates(subset=['id'], inplace=True)
        df.set_index('id', inplace=True)
    
        return df
        
    def _map_reactions2metabolites(self):
        df = pd.DataFrame({g.id:g.metabolites for g in self.model.reactions})
        df = df.unstack().reset_index().dropna()
        df.columns = ['id', 'metabolite_id', 'stoich_coeff']
        df['metabolite_id'] = map(lambda x: str(x)[:-2], df['metabolite_id'])
        df['reaction'] = self._trim_reverse(df.id)
        df = df.merge(self.bigg2ec)        
        return df

    def gene_information_df(self):
        l = []
        for g in self.model.genes:
            gene2reac = {'gene_object':g, 'id':[r.id for r in g.reactions]}
            l.append(pd.DataFrame.from_dict(gene2reac))
        df = pd.concat(l)
        df['gene_name'] = map(lambda x: x.name, df['gene_object'])
        df['gene_id'] = map(lambda x: x.id, df['gene_object'])
        df.drop('gene_object', axis=1, inplace=True)
        df.set_index('id', inplace=True)
        df.replace('None', np.nan, inplace=True)
        return df
        
    def model_kcat_df(self):
        
        kcat_all = self.load_BRENDA_turnover_data()
        reac2metab = self._map_reactions2metabolites()
        kcat = kcat_all[kcat_all['Organism']==self.organism]
        kcat = kcat.rename(columns = {'Organism':'organism', 
                                      'bigg.metabolite':'metabolite_id',
                                      'Turnover_Number':'kcat'})

        df = reac2metab.merge(kcat, how='left')
        
        df = df[df['stoich_coeff']<0]
        df = df.groupby(['id']).median()
        df.drop(['LigandID', 'stoich_coeff'], axis=1, inplace=True)
        df.dropna(inplace=True)
        
        return df 

    def searchables(self):
        df = self.reactions.copy()
        df = df.merge(self.genes, how='left', left_index=True, right_index=True)
        df['organism'] = self.organism
        return df


    def specific_activity(self):
        E = self.reaction_to_enzyme_investemnt()
        out = self.flux.div(E)
        out.replace(np.inf, np.nan, inplace=True)
        return out

    def umol_mg_min_to_reactions_per_sec(self):
        return
        
    def get_kmax(self):
        return self.kapp.max(axis=1)    

        
if __name__ == '__main__':
#    organism = 'Saccharomyces cerevisiae'
    organism = 'Escherichia coli'    
    C = CACHE(organism)
    
    df = C.searchin
    #cache dataframes
#    settings.write_cache(B.kcat, organism+'_kcat')
#    settings.write_cache(B.reactions, organism+'_reaction')














#        

                
#    def _get_model_df(self):
#        df = self.reversible_model_df.merge(self.reaction2ec_df, how='left')
#        df = df.merge(self.irreversible_model_df, how='left')
#        df = df.merge(self.model_genes_df, how='left')
#        
#        return df
#        
#    def _merge_flux_data(self):
#        flux = settings.fluxes_df[self.organism].unstack().reset_index()
#        flux.columns = ['condition', 'reaction_id', 'flux [mmol/gCDW/h]']
#        self.kcatulator_df = self.model_df.merge(flux)
#
#    def _merge_abundance_data(self):
#        abundance = settings.abundances_df[self.organism].unstack().reset_index()
#        abundance.columns = ['condition', 'bnumber', 'abundance [g/gCDW]']
#        # use only proteins that are in more than 10 copies per cell
#        # this is assuming that there are 3 million proteins per cell so
#        # in units of gram per gCDW this means 10/1e6/2 since only half the 
#        # dry mass is proteins
##        abundance = abundance[abundance['abundance [g/gCDW]'] > 20./3e6]
#        self.kcatulator_df = self.kcatulator_df.merge(abundance, how='left')
#        
            



#
#    def _calculate_kapp(self, mode='simple'):
#        '''for each reaction, the mass of the associated enzyme is the sum of all:
#        expressed proteins known to catalyze this reaction, i.e., sum(m_i) for all
#        i in reaction.genes'''
#        
#        if mode == 'simple':
#            df = self.kcatulator_df.copy()
#            l = []
#            for i, g in df.groupby(['rev_reac_id', 'condition'], as_index=True):
#                total_mass = g['abundance [g/gCDW]'].sum() * 1e3 # mg/gCDW
#                flux = g['flux [mmol/gCDW/h]'] * 1e3 / 60 # umol/gCDW/min
#                kapp = flux / total_mass # umol/mg/min
#                l.append(kapp)
#            kapp = pd.DataFrame(pd.concat(l))
#            kapp.columns = ['kapp [umol/mg/min]']
#            kapp = kapp[kapp>=0]
#            self.kcatulator_df = self.kcatulator_df.merge(kapp, 
#                                                          right_index=True, 
#                                                          left_index=True)
#            
#    def _get_kmax(self):
#        kmax = self.kcatulator_df.groupby(by='rev_reac_id')['kapp [umol/mg/min]'].max()
#        kmax = pd.DataFrame(kmax)
#        kmax.columns = ['kmax [umol/mg/min]']
#        self.kcatulator_df = self.kcatulator_df.merge(kmax, left_on='rev_reac_id',
#                                                      right_index=True)
#        




#    df.to_csv("cache/reaction_information.csv", encoding='utf-8')
#    kapp = model_df.calculate_kapp_simple()
#    kcatulator = model_df.kcatulator_df
#    kapp = kcatulator.pivot_table(index='rev_reac_id', 
#                                  columns='condition', 
#                                  values='kapp [umol/mg/min]').dropna(how='all')
#
#    flux = kcatulator.pivot_table(index='rev_reac_id', 
#                                  columns='condition', 
#                                  values='kapp [umol/mg/min]').dropna(how='all')
#
#    abun = kcatulator.pivot_table(index='rev_reac_id', 
#                                  columns='condition', 
#                                  values='abundance [g/gCDW]').dropna(how='all')

#
#
#
#
#
#
#
#m = load_json_model()
#m_r = deepcopy(m)
#convert_to_irreversible(m_r)
#
#
#
#
#r2ec = pd.DataFrame.from_csv("bigg2ec.csv")
#df = pd.DataFrame(index=m.reactions, columns=['reaction_id'])
#df['reaction_id'] = map(lambda x: x.id, m.reactions)
#df['reaction_name'] = map(lambda x: x.name, m.reactions)
#df_reverse['reaction_string'] = map(lambda x: R.build_reaction_string(x, 
#                                        use_metabolite_names=False), 
#                                                       m_r.reactions)
#df_reverse['reaction_string_full'] = map(lambda x: R.build_reaction_string(x, 
#                                        use_metabolite_names=True), 
#                                                       m_r.reactions)

#

#
#

#df = df.merge(gene2reaction, on='reaction_id', how='left')
#
#df = df.merge(df_reverse, on='reaction_id')
#

#
#
#

