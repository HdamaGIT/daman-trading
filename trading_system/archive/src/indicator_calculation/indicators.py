import talib as ta
import numpy as np
import pandas as pd


#########################################################################################
#########################################################################################
#########################################################################################

"""
    This code is for a class called TAIndicators that is used to calculate some technical indicators for financial data. The calc_TA method calculates a number of technical indicators, including simple moving averages (SMA) and exponential moving averages (EMA). The indicators method creates new columns in the data with signals based on the values of these technical indicators.
    
    The technical indicators that are calculated include:
    Simple moving averages: These are a type of statistical measure that is used to smooth out data over a given time period. They are calculated by taking the sum of a set of data points and dividing it by the number of points in the set.
    Exponential moving averages: These are similar to simple moving averages, but they place more weight on more recent data points. This helps them respond more quickly to changes in the data.
    Bollinger bands: These are statistical measures that are used to indicate the volatility of a financial asset. They consist of a moving average and two "bands" that are placed a certain number of standard deviations above and below the moving average.
    Relative strength index (RSI): This is a momentum indicator that is used to measure the strength of a financial asset's price action. It is calculated using the ratio of the asset's average gains over a given time period to its average losses over the same time period.
    Moving average convergence divergence (MACD): This is a momentum indicator that is used to identify the strength and direction of a trend. It is calculated by subtracting the value of a long-term exponential moving average from a short-term exponential moving average.
    Stochastic oscillator: This is a momentum indicator that is used to identify potential overbought or oversold conditions in a financial asset. It is calculated using the asset's closing price and its high and low prices over a given time period.
    Price rate of change (RoC): This is a momentum indicator that is used to measure the percentage change in an asset's price over a given time period.
    Money flow index (MFI): This is a momentum indicator that is used to measure the flow of money into and out of a financial asset. It is calculated using the asset's price, volume, and high and low prices over a given time period.
    On balance volume (OBV): This is a volume indicator that is used to measure the flow of money into and out of a financial asset. It is calculated by adding the volume on up days and subtracting the volume on down days.
"""

#########################################################################################
#########################################################################################
#########################################################################################


class TAIndicators:
    def __init__(self, data, close, high, low, vol, short, long):
        """
        Initialize the TAIndicators class with the following parameters:
            - data: a data set containing the close, high, low, and volume data for a security
            - close: the name of the column in the data set containing the close price data
            - high: the name of the column in the data set containing the high price data
            - low: the name of the column in the data set containing the low price data
            - vol: the name of the column in the data set containing the volume data
            - short_SMA: the period for the short-term simple moving average indicator
            - long_SMA: the period for the long-term simple moving average indicator
        """

        self.data = data
        self.close = close
        self.high = high
        self.low = low
        self.vol = vol
        self.short = short
        self.long = long

        self.short_sma = np.nan
        self.long_sma = np.nan
        self.short_ema = np.nan
        self.long_ema = np.nan
        self.short_term_ema = np.nan
        self.long_term_ema = np.nan
        self.up_band = np.nan
        self.mind_band = np.nan
        self.low_band = np.nan
        self.rsi = np.nan
        self.macd = np.nan
        self.macdsignal = np.nan
        self.macdhist = np.nan
        self.slowk = np.nan
        self.slowd = np.nan
        self.roc = np.nan
        self.mfi = np.nan

        self.signal_sma = np.nan
        self.signal_ema = np.nan

    def run(self):
        self.calc_ta()
        self.indicators()

        return {
                'date': self.data['date'],
                'close': self.data[self.close],
                'vol': self.data['volume'],
                'short_sma': self.short_sma,
                'long_sma': self.long_sma,
                'signal_sma': self.signal_sma,
                'short_ema': self.short_ema,
                'long_ema': self.long_ema,
                'signal_ema': self.signal_ema,
                'up_band': self.up_band,
                'mind_band': self.mind_band,
                'low_band': self.low_band,
                'rsi': self.rsi,
                'macd': self.macd,
                'macdsignal': self.macdsignal,
                'macdhist': self.macdhist,
                'roc': self.roc
        }

    def calc_ta(self):
        """
        Calculate the following technical analysis indicators for the data set:
            - simple moving averages (SMAs) with periods short_SMA and long_SMA
            - exponential moving averages (EMAs) with periods short_SMA and long_SMA
        """
        # Simple Moving Average
        self.short_sma = ta.SMA(self.data[self.close], self.short)
        self.long_sma = ta.SMA(self.data[self.close], self.long)

        # Exponential Moving Average
        self.short_ema = ta.EMA(self.data[self.close], timeperiod=self.short)
        self.long_ema = ta.EMA(self.data[self.close], timeperiod=self.long)

        self.short_term_ema = self.data[self.close].ewm(span=self.short).mean()
        self.long_term_ema = self.data[self.close].ewm(span=self.long).mean()

        # Bollinger Bands
        self.up_band, self.mind_band, self.low_band = ta.BBANDS(self.data[self.close], timeperiod=self.short)

        ### MOMENTUM INDICATORS
        # Relative Strength Index (RSI)
        self.rsi = ta.RSI(self.data[self.close], 14)

        # Moving Average Convergence Divergence (MACD)
        self.macd, self.macdsignal, self.macdhist = ta.MACD(self.data[self.close], fastperiod=12, slowperiod=26, signalperiod=9)

        # # Stockastic
        # self.slowk, self.slowd = ta.STOCH(self.data[self.high], self.data[self.low],
        #                                                   self.data[self.close], fastk_period=5, slowk_period=3,
        #                                                   slowk_matype=0, slowd_period=3, slowd_matype=0)

        # Price Rate of Change (RoC)
        self.roc = ta.ROC(self.data[self.close], timeperiod=10)

        # # Money Flow Index (MFI)
        # self.mfi = ta.MFI(self.data[self.high], self.data[self.low], self.data[self.close],self.data[self.vol], timeperiod=14)
        #
        # ### VOLUME INDICATOR
        # # On Balance Volume (OBV)

    def indicators(self):
        """
        Calculate additional indicators based on the previously calculated SMAs and EMAs:
            - signals based on the short-term and long-term SMAs and EMAs crossing over
        """
        # Simple Moving Average
        self.signal_sma = np.where(self.short_sma > self.long_sma, 1, np.where(self.short_sma < self.long_sma, 2, 0))
        # self.data['signal_SMA'] = np.where(self.short_sma > self.long_sma, 1, np.where(self.short_sma < self.long_sma, 2, 0))

        # Exponential Moving Average
        self.signal_ema = np.where(self.short_ema > self.long_ema, 1, np.where(self.short_ema < self.long_ema, 2, 0))
        # self.data['signal_EMA'] = np.where(self.short_ema > self.long_ema, 1, np.where(self.short_ema < self.long_ema, 2, 0))

        # # Bollinger Bands
        # bb_buy = np.where((self.data[self.close] > self.data['low_band']) & (
        #                 self.data[self.close].shift(1) < self.data['low_band'].shift(1)), 1, 0)
        # bb_sell = np.where((self.data[self.close] < self.data['up_band']) & (
        #                 self.data[self.close].shift(1) > self.data['up_band'].shift(1)), 2, 0)
        # bb_check = pd.self.dataFrame({'bb_buy': bb_buy, 'bb_sell': bb_sell})
        # bb_position = np.where(bb_check['bb_buy'] == 1, bb_check['bb_buy'], bb_check['bb_sell'])
        # self.data['signal_BB'] = 0.0
        # self.data['signal_BB'] = pd.self.dataFrame(bb_position)
        # # self.data['up_band'] = self.data['up_band']
        # # self.data['low_band'] = self.data['low_band']
        #
        # ### MOMENTUM INDICATORS
        # # Relative Strength Index (RSI)
        # rsi_buy = np.where(self.data['rsi'] < 30, 1.0, 0.0)
        # rsi_sell = np.where(self.data['rsi'] > 70, 2.0, 0.0)
        # rsi_check = pd.self.dataFrame({'rsi_buy': rsi_buy, 'rsi_sell': rsi_sell})
        # rsi_position = np.where(rsi_check['rsi_buy'] == 1.0, rsi_check['rsi_buy'],
        #                         rsi_check['rsi_sell'])
        # self.data['signal_RSI'] = 0.0
        # self.data['signal_RSI'] = pd.self.dataFrame(rsi_position)
        # # self.data['rsi'] = self.data['rsi']
        #
        # # Moving Average Convergence Divergence (MACD)
        # macd_buy = np.where((self.data['macd'] > self.data['macdsignal']) & (
        #                 self.data['macd'].shift(1) < self.data['macdsignal'].shift(1)), 1, 0)
        # macd_sell = np.where((self.data['macd'] < self.data['macdsignal']) & (
        #                 self.data['macd'].shift(1) > self.data['macdsignal'].shift(1)), 2, 0)
        # macd_check = pd.self.dataFrame({'macd_buy': macd_buy, 'macd_sell': macd_sell})
        # macd_position = np.where(macd_check['macd_buy'] == 1.0, macd_check['macd_buy'],
        #                          macd_check['macd_sell'])
        # self.data['signal_MACD'] = 0.0
        # self.data['signal_MACD'] = pd.self.dataFrame(macd_position)
        #
        # # # Stockastic
        # # self.data['signal_stock'] = 0.0
        #
        # # Price Rate of Change (RoC)
        # self.data['signal_roc'] = 0.0

        # # Money Flow Index (MFI)
        # mfi_buy = np.where((self.data['mfi'] > 10) & (self.data['mfi'].shift(1) < 10), 1, 0)
        # mfi_sell = np.where((self.data['mfi'] < 90) & (self.data['mfi'].shift(1) > 90), 2, 0)
        # mfi_check = pd.self.dataFrame({'mfi_buy': mfi_buy, 'mfi_sell': mfi_sell})
        # mfi_position = np.where(mfi_check['mfi_buy'] == 1.0, mfi_check['mfi_buy'],
        #                         mfi_check['mfi_sell'])
        # self.data['signal_MFI'] = 0.0
        # self.data['signal_MFI'] = pd.self.dataFrame(mfi_position)

        ### VOLUME INDICATOR
        # On Balance Volume (OBV)


#########################################################################################
#########################################################################################
#########################################################################################

# v1.0
# def calc_TA(data, close, high, low, vol, short_SMA, long_SMA):
#         # Simple Moving Average
#         data['short_sma'] = ta.SMA(data[close], short_SMA)
#         data['long_sma'] = ta.SMA(data[close], long_SMA)
#
#         # Exponential Moving Average
#         data['short_ema'] = ta.EMA(data[close], timeperiod=short_SMA)
#         data['long_ema'] = ta.EMA(data[close], timeperiod=long_SMA)
#
#         data['short_term_ema'] = data[close].ewm(span=short_SMA).mean()
#         data['long_term_ema'] = data[close].ewm(span=long_SMA).mean()
#
#         # Bollinger Bands
#         data['up_band'], data['mind_band'], data['low_band'] = ta.BBANDS(data[close], timeperiod=short_SMA)
#
#         ### MOMENTUM INDICATORS
#         # Relative Strength Index (RSI)
#         data['rsi'] = ta.RSI(data[close], 14)
#
#         # Moving Average Convergence Divergence (MACD)
#         data['macd'], data['macdsignal'], data['macdhist'] = ta.MACD(data[close], fastperiod=12, slowperiod=26, signalperiod=9)
#
#         # Stockastic
#         data['slowk'], data['slowd'] = ta.STOCH(data[high], data[low], data[close], fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
#
#         # Price Rate of Change (RoC)
#         data['roc'] = ta.ROC(data[close], timeperiod=10)
#
#         # Money Flow Index (MFI)
#         data['mfi'] = ta.MFI(data[high], data[low], data[close], data[vol], timeperiod=14)
#
#         ### VOLUME INDICATOR
#         # On Balance Volume (OBV)
#         data['obv'] = ta.OBV(data[close], data[vol])
#
#         return data
