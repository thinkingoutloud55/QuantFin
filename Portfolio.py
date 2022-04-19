# -*- coding: utf-8 -*-
from numpy import ones
from pandas import DataFrame, DatetimeIndex, concat, qcut

from QuantFin.HandleError import InputError
from QuantFin.Regression import OLS
from QuantFin.ReqData import KenFrench


class Deciles:

    def method_qcut(self,
                    df: DataFrame,
                    on: str,
                    label: str = 'port',
                    jdate: str = 'jdate',
                    entity: str = 'permno',
                    duplicates: str = 'raise',
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
            .transform(lambda x: qcut(x, decile, labels=False, duplicates=duplicates)) + 1
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
            edges = [x/100*rankmax for x in
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
                       ranking=True,
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


class Performance:

    def __init__(self, df: DataFrame, freq: str = 'M', model: str = 'FF3',
                 datename: str = 'date'):
        """
        Parameters
        ----------
        df: DataFrame
            A DataFrame of portfolios returns with columns of portfolio 
            names and an index of datetime.

        freq: str
            The frequency of returns. Optional frequencies are monthly(M),
            daily(D) and yearly(Y). Default is 'M'.

        model: str
            Indicates the benchmark asset pricing models for estimating the 
            alpha. It will regress portfolios returns on factors. Optional 
            models are None (for not estimating alpha), Fama-French-3 factor (FF3), 
            Fama-French-5 factor (FF5), and FF3 + MOM (FF4). Default is FF3.

        datename: str
            Indicates the name of datetime index. Default is 'date'

        """
        if type(df.index) is not DatetimeIndex:
            if model != None:
                raise InputError(
                    "The Input dataset's index should be DatetimeIndex if model is indicated. Otherwise, please set model to None")
        self.df = df
        self.model = model
        self.freq = freq
        self.datename = datename

    def _get_factor_data(self):
        _f = KenFrench(self.model, self.freq).get_data()
        _f.index = _f.index.rename(self.datename)
        try:
            _f = _f[_f.columns.drop('RF')]
        except:
            pass
        return _f

    def stats(self, ys, x, param, percentage, decimal, **args):
        _tp = ys.apply(lambda y: OLS(y, x, **args).stats(param))
        _m = _tp.iloc[0, :]
        if percentage:
            _m = _m*100
        _m = _m.apply(lambda x: format(x, '.2f'))
        _t = _tp.iloc[1, :].apply(
            lambda x: '\n('+format(x, f'.{decimal}f')+')')
        _pv = _tp.iloc[2, :]
        _pv = _pv.mask(_pv <= .01, 3)
        _pv = _pv.mask(_pv <= .05, 2)
        _pv = _pv.mask(_pv <= .10, 1)
        _pv = _pv.mask((_pv > .10) & (_pv < 1), 0)
        _pv = _pv.apply(lambda x: int(x)*'*')
        _tp = _m + _pv + _t
        return _tp

    def summary(self, percentage: bool = True, decimal: int = 2, **args) -> DataFrame:
        """
        It reports the summary statistics of portfolios performance, including 
        mean returns and t-values, standard factor models'alpha and relative
        t-values. 

        Parameters
        ----------
        percentage: bool
        It indicates if returns in the summary table is in percentage, 
        including alphas. Default is True

        decimal: int
        It indicates the decimals in this summary table would be kept.
        Default is 2.

        args:
        All arguments related to the statsmodel.api.OLS.fit are applied
        here. e.g., cov_type='HAC', cov_kwds={'maxlags':6} for 
        Newey-West adjust t-statistics.

        Returns
        -------
        summary: DataFrame
        """
        _l = self.df.columns  # get all portfolio-label names
        _t = self.stats(self.df, ones(len(self.df)), 'const', 
                        percentage, decimal, **args)
        _t = _t.rename('Mean').to_frame()
        if self.model:
            _f = self._get_factor_data()
            self.df = concat([self.df, _f], axis=1, join='inner')
            _ta = self.stats(
                self.df[_l], 
                self.df[_f.columns], 'const', percentage, decimal, **args)
            _ta = _ta.rename(f'Alpha({self.model})')
            _t = concat([_t, _ta], axis=1)
            _t.index = _t.index.rename('Portfolio')
        return _t