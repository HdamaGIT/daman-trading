import talib as ta
import numpy as np


def calculate_sma(data, short_period, long_period):
    close_prices = np.array(data['close'], dtype=float)
    short_sma = ta.SMA(close_prices, timeperiod=short_period)
    long_sma = ta.SMA(close_prices, timeperiod=long_period)
    return short_sma, long_sma


def calculate_ema(data, short_period, long_period):
    close_prices = np.array(data['close'], dtype=float)
    short_ema = ta.EMA(close_prices, timeperiod=short_period)
    long_ema = ta.EMA(close_prices, timeperiod=long_period)
    return short_ema, long_ema


def calculate_bollinger_bands(data, period):
    close_prices = np.array(data['close'], dtype=float)
    upper_band, middle_band, lower_band = ta.BBANDS(close_prices, timeperiod=period, nbdevup=2, nbdevdn=2, matype=0)
    return upper_band, middle_band, lower_band


def calculate_rsi(data, period=14):
    close_prices = np.array(data['close'], dtype=float)
    rsi = ta.RSI(close_prices, timeperiod=period)
    return rsi


def calculate_macd(data, fastperiod=12, slowperiod=26, signalperiod=9):
    close_prices = np.array(data['close'], dtype=float)
    macd, macdsignal, macdhist = ta.MACD(close_prices, fastperiod=fastperiod, slowperiod=slowperiod, signalperiod=signalperiod)
    return macd, macdsignal, macdhist


def calculate_roc(data, period=10):
    close_prices = np.array(data['close'], dtype=float)
    roc = ta.ROC(close_prices, timeperiod=period)
    return roc
