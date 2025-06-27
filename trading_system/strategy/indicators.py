import pandas as pd
import talib
import logging
from typing import Dict, Any

def calculate_indicators_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for one ticker's data.
    """
    fast_ema_period = 10
    slow_ema_period = 50
    rsi_period = 14



    # Always extract 1D array
    close = df['Close']

    if isinstance(close, pd.DataFrame):
        close = close.squeeze()

    arr = close.values
    if arr.ndim > 1:
        arr = arr.squeeze()

    logging.info("EMA...")
    df['fast_ema'] = talib.EMA(arr, timeperiod=fast_ema_period)
    df['slow_ema'] = talib.EMA(arr, timeperiod=slow_ema_period)
    df['momentum_signal'] = df['fast_ema'] > df['slow_ema']

    logging.info("RSI...")
    df['RSI'] = talib.RSI(arr, timeperiod=rsi_period)

    logging.info("MACD...")
    macd, macdsignal, _ = talib.MACD(arr, fastperiod=12, slowperiod=26, signalperiod=9)
    df['macd'] = macd
    df['macdsignal'] = macdsignal

    logging.info("VWAP...")
    df['vwap'] = (
        (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum()
    ) / df['Volume'].cumsum()

    return df


def calculate_indicators(
    data: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    """
    Calculate indicators for all tickers in the dataset.

    Parameters
    ----------
    data : Dict[str, pd.DataFrame]
        Dictionary of raw price DataFrames keyed by ticker.

    Returns
    -------
    Dict[str, pd.DataFrame]
        Dictionary of DataFrames with calculated indicators.
    """
    result = {}

    for ticker, df in data.items():
        # Ensure 'date' is datetime index
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        df = calculate_indicators_for_ticker(df)
        result[ticker] = df

    return result
