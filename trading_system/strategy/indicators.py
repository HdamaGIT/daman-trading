import pandas as pd
import talib
from typing import Dict, Any

def calculate_indicators_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for a given ticker's data.

    Parameters:
    - df (pd.DataFrame): DataFrame containing OHLCV data.

    Returns:
    - df (pd.DataFrame): DataFrame with calculated indicators.
    """
    short_period = 20
    long_period = 200
    rsi_period = 14

    # Calculate SMAs, EMAs, RSI, Bollinger Bands, MACD, and Stochastic Oscillator
    df['short_sma'] = df['Close'].rolling(window=short_period).mean()
    df['long_sma'] = df['Close'].rolling(window=long_period).mean()
    df['short_ema'] = talib.EMA(df['Close'], timeperiod=short_period)
    df['long_ema'] = talib.EMA(df['Close'], timeperiod=long_period)
    df['RSI'] = talib.RSI(df['Close'], timeperiod=rsi_period)
    df['upperband'], df['middleband'], df['lowerband'] = talib.BBANDS(df['Close'], timeperiod=short_period, nbdevup=2, nbdevdn=2, matype=0)
    df['macd'], df['macdsignal'], df['macdhist'] = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)
    df['slowk'], df['slowd'] = talib.STOCH(df['High'], df['Low'], df['Close'], fastk_period=5, slowk_period=3, slowd_period=3)

    return df

def calculate_indicators(data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate indicators for all tickers in the dataset.

    Parameters:
    - data (Dict[str, Dict[str, Any]]): Dictionary of raw price data per ticker.

    Returns:
    - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators calculated for each ticker.
    """
    for ticker, ticker_data in data.items():
        df = pd.DataFrame(ticker_data)

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        data[ticker] = calculate_indicators_for_ticker(df).reset_index().to_dict('list')

    return data
