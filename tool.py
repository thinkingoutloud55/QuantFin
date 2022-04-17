# -*- coding: utf-8 -*-
from numpy import nan, log, exp
from pandas import DataFrame

class Volatility:
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
    
    def logSum(self, df: DataFrame, pre: int, post:int) -> DataFrame:
        df = df.fillna(0) + 1
        window = abs(post - pre) + 1
        cr = log(df)
        cr = cr.rolling(window=window, min_periods=window).sum()
        cr = (exp(cr)-1).shift(-post)
        cr = cr.replace(0, nan)
        cr = cr.stack().rename(f'CR[{pre},{post}]').to_frame()
        cr[abs(cr[f'CR[{pre},{post}]'])<0.0000001] = nan
        cr = cr.loc[:, f'CR_{pre}_{post}'].unstack()
        return cr