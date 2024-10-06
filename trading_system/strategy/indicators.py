import pandas as pd
import talib
from typing import Dict, Any

def calculate_indicators_for_ticker(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate technical indicators for a given ticker's data, focusing on momentum indicators.

    Parameters:
    - df (pd.DataFrame): DataFrame containing OHLCV data.

    Returns:
    - df (pd.DataFrame): DataFrame with calculated indicators.
    """
    short_period = 20
    long_period = 200
    rsi_period = 14
    fast_ema_period = 10
    slow_ema_period = 50

    # Calculating EMAs for Momentum Cross Strategy
    df['fast_ema'] = talib.EMA(df['Close'], timeperiod=fast_ema_period)
    df['slow_ema'] = talib.EMA(df['Close'], timeperiod=slow_ema_period)
    df['momentum_signal'] = df['fast_ema'] > df['slow_ema']

    # RSI Indicator for Momentum Analysis
    df['RSI'] = talib.RSI(df['Close'], timeperiod=rsi_period)

    # MACD Indicator to Gauge Market Momentum
    df['macd'], df['macdsignal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

    # Volume-Weighted Average Price (VWAP) for Confirmation
    df['vwap'] = ((df['Volume'] * (df['High'] + df['Low'] + df['Close']) / 3).cumsum()) / df['Volume'].cumsum()

    return df


def calculate_indicators(data: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Calculate indicators for all tickers in the dataset, with a focus on momentum indicators.

    Parameters:
    - data (Dict[str, Dict[str, Any]]): Dictionary of raw price data per ticker.

    Returns:
    - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators calculated for each ticker.
    """
    for ticker, ticker_data in data.items():
        df = pd.DataFrame(ticker_data)

        # Ensure 'date' is properly set as index if it exists in data
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        # Calculate momentum indicators
        data[ticker] = calculate_indicators_for_ticker(df).reset_index().to_dict('list')

    return data
