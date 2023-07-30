#########################################################################################
#########################################################################################
#########################################################################################

import pandas as pd
from finvizfinance.screener.overview import Overview
from finvizfinance.screener.valuation import Valuation


class Finviz:
    def __init__(self, exchange, sector, index):

        self.exchange = exchange
        self.sector = sector
        self.index = index
        self.tickers = []
        self.df = pd.DataFrame

        self.foverview = Overview()

        self.filters_dict = {f'Exchange': self.exchange
                # , 'Sector': 'Basic Materials'
                , 'Index': self.index
                }

        self.foverview.set_filter(filters_dict=self.filters_dict)

    def run(self):
        self.overview()
        # self.selection()

    def overview(self):
        self.df = pd.DataFrame(self.foverview.screener_view())


#########################################################################################


# def selection(self):
#     self.tickers = self.df[self.df['Sector'] == f'Basic Materials']['Ticker']
#     print(self.tickers)

# fvaluation = Valuation()
# fvaluation.set_filter(filters_dict=filters_dict)

# df = fvaluation.screener_view()
# print(df.head())

# from finvizfinance.news import News
# fnews = News()
# all_news = fnews.get_news()
# print(all_news['news'].head())
# # all_news['blogs'].head()
