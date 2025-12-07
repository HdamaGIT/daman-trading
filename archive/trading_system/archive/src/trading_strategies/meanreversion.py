#########################################################################################
#########################################################################################
#########################################################################################

import pandas as pd
from statsmodels.tsa.stattools import adfuller, coint

from statsmodels.sandbox.stats.multicomp import multipletests
from statsmodels.tsa.stattools import coint, adfuller
import pandas as pd
import numpy as np

class MeanReversion:
    def __init__(self, finviz, historic):
        self.database = finviz
        self.sectors = finviz['sector'].unique()
        self.historic = historic

    def get_sector_tickers(self, sector):
        return self.database[self.database['sector'] == sector]['ticker'].tolist()

    def test_stationarity(self, time_series):
        result = adfuller(time_series)
        return result[1]  # Return p-value

    def test_cointegration(self, ticker_1, ticker_2):
        score, p_value, _ = coint(ticker_1, ticker_2)
        return p_value

    def get_historic_data(self, ticker):
        return self.historic[self.historic['ticker'] == ticker]

    def find_mean_reverting_pairs(self, sector):
        tickers = self.get_sector_tickers(sector)
        n = len(tickers)
        pairs = []
        p_values = []

        for i in range(n):
            for j in range(i + 1, n):
                ticker_1 = self.get_historic_data(tickers[i])
                ticker_2 = self.get_historic_data(tickers[j])

                if not ticker_1.empty and not ticker_2.empty:
                    # Align the time series on common dates
                    merged_data = pd.merge(ticker_1[['date', 'adj_close']], ticker_2[['date', 'adj_close']], on='date',
                                           suffixes=('_1', '_2'))
                    if len(merged_data) > 0:
                        p_value = self.test_cointegration(merged_data['adj_close_1'], merged_data['adj_close_2'])
                        pairs.append((tickers[i], tickers[j]))
                        p_values.append(p_value)

        # Apply Bonferroni correction
        reject, corrected_p_values, _, _ = multipletests(p_values, method='bonferroni')
        significant_pairs = [pair for pair, rej in zip(pairs, reject) if rej]
        return significant_pairs

    def find_all_mean_reverting_pairs(self):
        all_pairs = []
        for sector in self.sectors:
            sector_pairs = self.find_mean_reverting_pairs(sector)
            all_pairs.extend(sector_pairs)
        return all_pairs

    def analyze_pairs(self, pairs, lookback=100):
        analyzed_pairs = []
        for pair in pairs:
            ticker_1 = self.get_historic_data(pair[0])
            ticker_2 = self.get_historic_data(pair[1])

            if not ticker_1.empty and not ticker_2.empty:
                merged_data = pd.merge(ticker_1[['date', 'adj_close']], ticker_2[['date', 'adj_close']], on='date',
                                       suffixes=('_1', '_2'))
                if len(merged_data) > 0:
                    # Calculate the spread
                    spread = merged_data['adj_close_1'] - merged_data['adj_close_2']
                    # Calculate moving average and standard deviation
                    spread_mavg = spread.rolling(window=lookback).mean()
                    spread_std = spread.rolling(window=lookback).std()
                    # Calculate z-score
                    z_score = (spread - spread_mavg) / spread_std
                    # Store the values in a DataFrame
                    analyzed_pair = {
                        'ticker_1': pair[0],
                        'ticker_2': pair[1],
                        'spread': spread,
                        'spread_mavg': spread_mavg,
                        'spread_std': spread_std,
                        'z_score': z_score
                    }
                    analyzed_pairs.append(analyzed_pair)
        return pd.DataFrame(analyzed_pairs)



#########################################################################################
#########################################################################################
#########################################################################################


# class MeanReversion:
#     def __init__(self, finviz, historic):
#         self.database = finviz
#         self.sectors = finviz['sector'].unique()
#         self.historic = historic
#
#     def get_sector_tickers(self, sector):
#         return self.database[self.database['sector'] == sector]['ticker'].tolist()
#
#     def test_stationarity(self, time_series):
#         result = adfuller(time_series)
#         return result[1]  # Return p-value
#
#     def test_cointegration(self, ticker_1, ticker_2):
#         score, p_value, _ = coint(ticker_1, ticker_2)
#         return p_value
#
#     def get_historic_data(self, ticker):
#         return self.historic[self.historic['ticker'] == ticker]
#
#     def find_mean_reverting_pairs(self, sector, p_value_threshold=0.05):
#         tickers = self.get_sector_tickers(sector)
#         n = len(tickers)
#         pairs = []
#
#         for i in range(n):
#             for j in range(i + 1, n):
#                 ticker_1 = self.get_historic_data(tickers[i])
#                 ticker_2 = self.get_historic_data(tickers[j])
#
#                 if not ticker_1.empty and not ticker_2.empty:
#                     # Align the time series on common dates
#                     merged_data = pd.merge(ticker_1[['date', 'adj_close']], ticker_2[['date', 'adj_close']], on='date',
#                                            suffixes=('_1', '_2'))
#                     if len(merged_data) > 0:
#                         print(f"Processing tickers: {tickers[i]}, {tickers[j]}")
#                         print(f"Shapes: ticker_1 - {ticker_1.shape}, ticker_2 - {ticker_2.shape}")
#                         p_value = self.test_cointegration(merged_data['adj_close_1'], merged_data['adj_close_2'])
#
#                         if p_value < p_value_threshold:
#                             pairs.append((tickers[i], tickers[j], p_value))
#
#         return pairs
#
#     def find_all_mean_reverting_pairs(self, p_value_threshold=0.05):
#         all_pairs = []
#
#         for sector in self.sectors:
#             sector_pairs = self.find_mean_reverting_pairs(sector, p_value_threshold)
#             all_pairs.extend(sector_pairs)
#
#         return all_pairs
#
#     def analyze_pairs(self, pairs, lookback=100):
#         analyzed_pairs = []
#
#         for pair in pairs:
#             ticker_1 = self.get_historic_data(pair[0])
#             ticker_2 = self.get_historic_data(pair[1])
#
#             if not ticker_1.empty and not ticker_2.empty:
#                 merged_data = pd.merge(ticker_1[['date', 'adj_close']], ticker_2[['date', 'adj_close']], on='date',
#                                        suffixes=('_1', '_2'))
#
#                 if len(merged_data) > 0:
#                     # Calculate the spread
#                     spread = merged_data['adj_close_1'] - merged_data['adj_close_2']
#
#                     # Calculate moving average and standard deviation
#                     spread_mavg = spread.rolling(window=lookback).mean()
#                     spread_std = spread.rolling(window=lookback).std()
#
#                     # Calculate z-score
#                     z_score = (spread - spread_mavg) / spread_std
#
#                     # Store the values in a DataFrame
#                     analyzed_pair = {
#                         'ticker_1': pair[0],
#                         'ticker_2': pair[1],
#                         'p_value': pair[2],
#                         'spread': spread,
#                         'spread_mavg': spread_mavg,
#                         'spread_std': spread_std,
#                         'z_score': z_score
#                     }
#                     analyzed_pairs.append(analyzed_pair)
#
#         return pd.DataFrame(analyzed_pairs)


#########################################################################################
#########################################################################################
#########################################################################################
