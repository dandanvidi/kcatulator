from cobra.io import load_json_model
from cobra.manipulation.modify import convert_to_irreversible
import pandas as pd
import os, sys
import inspect

SCRIPT_DIR = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
BASE_DIR = os.path.join(*os.path.split(SCRIPT_DIR)[0:-1])
DATA_DIR = os.path.join(BASE_DIR, 'data')
CACHE_DIR = os.path.join(BASE_DIR, 'cache')
RESULT_DIR = os.path.join(BASE_DIR, 'res')
PROTEOMICS_DIR = os.path.join(DATA_DIR, 'proteomics')

#%%
models = {'Escherichia coli': 'iJO1366',
          'Saccharomyces cerevisiae': 'iMM904'}
fluxes = {'Escherichia coli':'mmol_gCDW_h'}
abundances = {'Escherichia coli':'g_gCDW'}

genomes = {'Escherichia coli':'Escherichia coli_genome_info'}

#%%
def read_cache(fname):
    return pd.DataFrame.from_csv(os.path.join(CACHE_DIR, fname + '.csv'))

def write_cache(df, fname):
    df.to_csv(os.path.join(CACHE_DIR, fname + '.csv'), encoding='utf-8')
    
def read_data(fname, sep=',', encoding='utf-8'):
    df = pd.DataFrame.from_csv(os.path.join(DATA_DIR, fname + '.csv'), 
                               sep=sep, encoding=encoding)
    return df

def read_proteomics(organism, fname, sep=',', encoding='utf-8'):
    ORG_DIR = os.path.join(PROTEOMICS_DIR,organism)
    df = pd.DataFrame.from_csv(os.path.join(ORG_DIR, fname + '.csv'),
                               sep=',', encoding='utf-8')
    return df
    
def get_model(organism):
    fname = os.path.join(DATA_DIR, models[organism] + '.json')
    m = load_json_model(fname)
    convert_to_irreversible(m)
    return m
    
def tidy_split(df, column, sep='|', keep=False):
    """
    Split the values of a column and expand so the new DataFrame has one split
    value per row. Filters rows where the column is missing.

    Params
    ------
    df : pandas.DataFrame
        dataframe with the column to split and expand
    column : str
        the column to split and expand
    sep : str
        the string used to split the column's values
    keep : bool
        whether to retain the presplit value as it's own row

    Returns
    -------
    pandas.DataFrame
        Returns a dataframe with the same columns as `df`.
    """
    indexes = list()
    new_values = list()
    df = df.dropna(subset=[column])
    for i, presplit in enumerate(df[column].astype(str)):
        values = presplit.split(sep)
        if keep and len(values) > 1:
            indexes.append(i)
            new_values.append(presplit)
        for value in values:
            indexes.append(i)
            new_values.append(value)
    new_df = df.iloc[indexes, :].copy()
    new_df[column] = new_values
    return new_df
    
