#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Monthly Returns Heatmap
# https://github.com/ranaroussi/monthly-returns-heatmap
#
# Copyright 2017 Ran Aroussi
#
# Licensed under the GNU Lesser General Public License, v3.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.gnu.org/licenses/lgpl-3.0.en.html
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

__version__ = "0.0.11"
__author__ = "Ran Aroussi"
__all__ = ['get', 'plot']

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pandas.core.base import PandasObject


def sum_returns(returns, groupby, compounded=True):
    def returns_prod(data):
        return (data + 1).prod() - 1
    if compounded:
        return returns.groupby(groupby).apply(returns_prod)
    return returns.groupby(groupby).sum()


def get(returns, eoy=False, is_prices=False, compounded=True):

    # get close / first column if given DataFrame
    if isinstance(returns, pd.DataFrame):
        returns.columns = map(str.lower, returns.columns)
        if len(returns.columns) > 1 and 'close' in returns.columns:
            returns = returns['close']
        else:
            returns = returns[returns.columns[0]]

    # convert price data to returns
    if is_prices:
        returns = returns.pct_change()

    original_returns = returns.copy()

    # build monthly dataframe
    # returns_index = returns.resample('MS').first().index
    # returns_values = sum_returns(returns,
    #     [returns.index.year, returns.index.month]).values
    # returns = pd.DataFrame(index=returns_index, data={
    #                        'Returns': returns_values})

    # simpler, works with pandas 0.23.1
    returns = pd.DataFrame(sum_returns(returns,
                                       returns.index.strftime('%Y-%m-01'),
                                       compounded))
    returns.columns = ['Returns']
    returns.index = pd.to_datetime(returns.index)

    # get returnsframe
    returns['Year'] = returns.index.strftime('%Y')
    returns['Month'] = returns.index.strftime('%b')

    # make pivot table
    returns = returns.pivot('Year', 'Month', 'Returns').fillna(0)

    # handle missing months
    for month in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                  'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
        if month not in returns.columns:
            returns.loc[:, month] = 0

    # order columns by month
    returns = returns[['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun',
                       'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']]

    if eoy:
        returns['eoy'] = sum_returns(original_returns,
                                     original_returns.index.year).values

    return returns


def plot(returns,
         title="Monthly Returns (%)\n",
         title_color="black",
         title_size=14,
         annot_size=10,
         figsize=None,
         cmap='RdYlGn',
         cbar=True,
         square=False,
         is_prices=False,
         compounded=True,
         eoy=False,
         ax=None,
         **kwargs
        ):

    returns = get(returns, eoy=eoy, is_prices=is_prices, compounded=compounded)
    returns *= 100

    if figsize is None and ax is None:
        size = list(plt.gcf().get_size_inches())
        figsize = (size[0], size[0] // 2)
        plt.close()

    if ax is None:
        fig, ax = plt.subplots(figsize=figsize)

    ax = sns.heatmap(returns, ax=ax, annot=True, center=0,
                     annot_kws={"size": annot_size},
                     fmt="0.2f", linewidths=0.5,
                     square=square, cbar=cbar, cmap=cmap, **kwargs)
    ax.set_title(title, fontsize=title_size,
                 color=title_color, fontweight="bold")

    if ax is None:
        fig.subplots_adjust(hspace=0)
        plt.yticks(rotation=0)
        plt.show()
        plt.close()

    return fig, ax




PandasObject.get_returns_heatmap = get
PandasObject.plot_returns_heatmap = plot
PandasObject.sum_returns = sum_returns
