# -*- coding: utf-8 -*-
import pandas_datareader.data as web
from linearmodels import FamaMacBeth, PanelOLS
from linearmodels.panel import compare   
import statsmodels.formula.api as smf
from pandas.tseries.offsets import BMonthEnd
from pandas import qcut, DataFrame, Series, merge, concat, to_datetime, read_csv
from numpy import nan, log, exp
from datetime import datetime
from zipfile import ZipFile
from bs4 import BeautifulSoup as bs
import requests
import io
import os

class OLS:
    def ols_r_squared(self, x, formula):
        return smf.ols(formula, data=x).fit().rsquared_adj


class PanelRes:
    
    def __init__(self, df, entity, date, formula):
        '''
        
        Parameters
        ----------
        df : pd.DataFrame
            The panel data with columns of entity, date, regressand and 
            regressors. 
        entity : str
            The column name of entity, eg., 'permno', which is the 
            permanent number of a security in CRSP database.
        date : str
            The column name of date, eg., 'date'.
        formula : str
            The regression model, eg., 
            'dependent_variable(t+1) ~ 1 + independent_variable(t)'.

        Returns
        -------
        None.

        '''
        if df.index.names != [entity, date]:
            self.df = df.set_index([entity, date])
        else:
            self.df = df
        self.entity = entity
        self.date = date
        self.formula = formula
        
    def fmb_reg(self, cov_type='kernel'):
        '''
        
        Parameters
        ----------
        cov_type : str, optional
            The default is 'kernel'.
    
        Returns
        -------
        reg : panel.results.FamaMacBethResults
            The summary results of FamaMacBeth regression
    
        '''
        try:
            mod = FamaMacBeth.from_formula(self.formula, self.df)
            reg = mod.fit(cov_type=cov_type)
            return reg
        except Exception as e:
            print(e)
    
    def fe_reg(self, cov_type='clustered', cluster_entity=True, 
               time_effects=False, entity_effect=False, other_effects=None):
        '''

        Parameters
        ----------
        cov_type : str, optional
            The default is 'clustered'.
        cluster_entity : bool, optional
            The default is True.
        time_effects : bool, optional
            The default is True.
        entity_effect : bool, optional
            The default is False.
        Returns
        -------
        reg : panel.results.PanelOLSResults
            The summary results of PanelOLS regression

        '''
        try:
            formula = self.formula
            if time_effects:
                formula += '+ TimeEffects'
            if entity_effect:
                formula += '+ EntityEffects'
            mod = PanelOLS.from_formula(formula, self.df)
            reg = mod.fit(cov_type=cov_type, cluster_entity=cluster_entity, 
                          other_effects=other_effects)
            return reg
        except Exception as e:
            print(e)