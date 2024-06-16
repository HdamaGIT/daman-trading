#########################################################################################
#########################################################################################
#########################################################################################

"""
Historic Price Data Downloader

This class downloads historical price data for stocks from Yahoo Finance. It can be limited to a specific sector.
The user can specify the desired date range, the frequency of data (interval), and other optional constraints.
The downloaded data is saved in a pandas DataFrame and can be returned for further processing or analysis.
"""

import pandas as pd
import yfinance as yf
from pandas_datareader._utils import RemoteDataError


class HistoricPriceData:
    def __init__(self, ticker_df, start, end, interval, limit_sector=False, sector=None):
        self.ticker_df = ticker_df
        self.start = start
        self.end = end
        self.interval = interval
        self.limit_sector = limit_sector
        self.sector = sector

        self.data = pd.DataFrame()
        self.tickers = []

    def fetch_data(self):
        if self.limit_sector:
            self._filter_tickers_by_sector()
        self.tickers = self.ticker_df.ticker.tolist()
        self._download_data()

    def _filter_tickers_by_sector(self):
        self.ticker_df = self.ticker_df[self.ticker_df['sector'] == self.sector]

    def _download_data(self):
        for count, ticker in enumerate(self.tickers):
            try:
                df = yf.download(tickers=[ticker], interval=self.interval, start=self.start, end=self.end, progress=False)
                df['ticker'] = ticker
                df['dt'] = df.index.astype(str)

                self.data = pd.concat([self.data, df], ignore_index=True)
                if count % 1 == 0:
                    print(f"{count}: {ticker}")

            except KeyError:
                print(f'KeyError for {ticker}')
                continue

            except RemoteDataError:
                print(f'RemoteDataError for {ticker}')
                continue

        print('Process: Data extraction complete.')

    def get_data(self):
        return self.data


#########################################################################################
#########################################################################################
#########################################################################################
