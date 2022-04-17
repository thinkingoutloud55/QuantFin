# -*- coding: utf-8 -*-
from pandas import qcut, DataFrame
from numpy import nan, log, exp

class PortfolioDecile:
    def method_qcut(self, 
                    df: DataFrame, 
                    on: str,
                    label: str = 'port',
                    jdate: str = 'jdate',
                    entity: str = 'permno',
                    duplicated: str = 'raise', 
                    decile: int = 10) -> DataFrame:
        """
        It assigns underlyings to deciles. Meanwhile, it raises or drops the 
        duplicated edges 
        
        Parameters
        ----------
        df : DataFrame
            A panel data in dataframe with an index of a range funct.
        on : str
            The column name that the sample would be cutted on.
        duplicated : str, optional
            'raise': raise the error of duplicated edges.
            'drop': drop the duplicated edges.
            The default is 'raise'
        label : str
            The name of the export deciles
        jdate: str
            The name of date index
        decile : int, optional
            The amount of equal-weighted deciles. The default is 10.

        Returns
        -------
        df : DataFrame
            A panel data with an index of a range funct.

        """
        _d = df.copy().dropna(axis=0, subset=[on])
        _d.loc[:, label] = df.groupby(jdate)[on]\
            .transform(lambda x: qcut(x, decile, labels=False)) + 1
        _d = _d[[entity, jdate, label]]
        df = df.merge(_d, on=[entity, jdate], how='left')
        return df

    def _assign_port_num_(self, x, decile, edges):
        if x < edges[0]:
            return 1
        elif x >= edges[-1]:
            return decile
        else:
            for i, edge in enumerate(edges):
                if i > 0:
                    if edges[i-1] <= x < edge:
                        return i+1

    def _assign_port_num(self, df, on, decile, label, ranking):
        try:
            if ranking:
                df.loc[:, label] = df.loc[:, on].rank()
            else:
                df.loc[:, label] = df.loc[:, on]
            rankmax = df.loc[:, label].max()
            edges = [x/100*rankmax for x in \
                     range(int(100/decile), 100, int(100/decile))]
            edges.sort()
            df.loc[:, label] = df.loc[:, label]\
                .apply(lambda x: self._assign_port_num_(x, decile, edges))
            return df
        except Exception as e:
            print(e)
        
    def method_ranking(self,
                       df: DataFrame,
                       on: str,
                       label: str = 'port',
                       jdate: str = 'jdate',
                       entity: str = 'permno',
                       decile: int = 10,
                       ranking = True,
                       ) -> DataFrame:
        """
        It assigns underlying to decile portfolios based on the ranking on 'on'.
        Then, it gets the maxmium ranking value and calculas the edges of decile
        on rankings. Lastly, it assigns the decile order to each entity on a 
        'jdate', termed as 'label'.

        Parameters
        ----------
        df: DataFrame
            It is a panel data. Column 
            names would be entity, date, jdate, maxn_date and maxn_ret. Noted
            that index would be a range index rather than multi-index of entity
            and jdate.
        on: str
            The column name that the sample would be cutted on.
        label: str
            The name of the export deciles. The default is 'port'.
        jdate: str
            The column name of join date. The default is 'jdate'.
        decile: int, optional
            The amount of deciles. The default is 10.

        Returns
        -------
        DataFrame
            It is a panel data in dataframe. Column names would be entity, 
            {jdate}, signals {on} and port {label}. Noted that index would be 
            a range index rather than multi-index of entity and jdate.

        """
        _d = df[[entity, jdate, on]].dropna()
        _d = _d.groupby(jdate).apply(
            lambda _f: self._assign_port_num(_f, on, decile, label, ranking))
        _d = _d[[entity, jdate, label]]
        df = df.merge(_d, on=[entity, jdate], how='left')
        return df
    

class CumuRet:
    def __init__(self, df, pre, post):
        self.df = df.fillna(0) + 1
        self.pre = pre
        self.post = post
    
    def geometric(self):
        cr = self.df
        window = abs(self.post-self.pre) + 1
        for i in range(1, window):
            cr = cr * self.df.shift(i)
        cr = cr.shift(-self.post)
        cr = cr - 1
        cr = cr.replace(0, nan)
        return cr
    
    def rolling_log_sum(self):
        window = abs(self.post-self.pre) + 1
        cr = log(self.df)
        cr = cr.rolling(window=window, min_periods=window).sum()
        cr = (exp(cr)-1).shift(-self.post)
        cr = cr.replace(0, nan)
        cr = cr.stack().rename(f'CR_{self.pre}_{self.post}').to_frame()
        cr[abs(cr[f'CR_{self.pre}_{self.post}'])<0.0000001] = nan
        cr = cr.loc[:, f'CR_{self.pre}_{self.post}'].unstack()
        return cr