import pandas as pd
import talib
import logging
from typing import Dict, Any


def calculate_indicators_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    fast_ema_period = 10
    slow_ema_period = 50
    rsi_period = 14

    # Safely extract Close as ndarray
    close = df['Close'].values.squeeze()

    df['fast_ema'] = talib.EMA(close, timeperiod=fast_ema_period)
    df['slow_ema'] = talib.EMA(close, timeperiod=slow_ema_period)
    df['momentum_signal'] = df['fast_ema'] > df['slow_ema']

    df['RSI'] = talib.RSI(close, timeperiod=rsi_period)

    macd, macdsignal, _ = talib.MACD(
        close, fastperiod=12, slowperiod=26, signalperiod=9
    )
    df['macd'] = macd
    df['macdsignal'] = macdsignal

    df['vwap'] = (
        (df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum()
        / df['Volume'].cumsum()
    )

    return df


def calculate_indicators(
    data: Dict[str, pd.DataFrame]
) -> Dict[str, pd.DataFrame]:
    result = {}

    for ticker, df in data.items():
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        df = calculate_indicators_for_ticker(df)
        result[ticker] = df

    return result
