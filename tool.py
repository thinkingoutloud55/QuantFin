# -*- coding: utf-8 -*-
from numpy import nan, log, exp
from pandas import DataFrame


class Volatility:

    def hist(self, df: DataFrame, window: int, minw: int) -> DataFrame:
        return df.rolling(window, min_periods=minw).std()

    def ewma(self, df: DataFrame, burnin: int, lambda_: float=0.94):
        df = df**2
        dfbi = df[:burnin]
        dfbi['i'] = reversed(range(burnin)) + 1
        dfbi['lamw'] = lambda_**(dfbi['i']-1)
        squared_sigma = (1 - lambda_)*(dfbi['lamw'].mul(dfbi.loc[:, :'i'], axis=0)) 
        sigma_0 = (1-lambda_)*

    def garch(self):
        pass

class CumulativeReturn:

    def geometric(self, df: DataFrame, pre: int, post: int) -> DataFrame:
        df = df.fillna(0) + 1
        window = abs(post - pre) + 1
        for i in range(1, window):
            cr = cr * df.shift(i)
        cr = cr.shift(-post)
        cr = cr - 1
        cr = cr.replace(0, nan)
        return cr

    def logsum(self, df: DataFrame, pre: int, post: int) -> DataFrame:
        df = df.fillna(0) + 1
        window = abs(post - pre) + 1
        cr = log(df)
        cr = cr.rolling(window=window, min_periods=window).sum()
        cr = (exp(cr)-1).shift(-post)
        cr = cr.replace(0, nan)
        cr = cr.stack().rename(f'CR[{pre},{post}]').to_frame()
        cr[abs(cr[f'CR[{pre},{post}]']) < 0.0000001] = nan
        cr = cr.loc[:, f'CR_{pre}_{post}'].unstack()
        return cr
