import pandas as pd
from typing import Dict, Any
import logging

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trading signals based on mean reversion and momentum strategies.

    Parameters:
    - df (pd.DataFrame): DataFrame with calculated indicators.

    Returns:
    - df (pd.DataFrame): DataFrame with trading signals added.
    """

    # Mean Reversion Strategy (using Bollinger Bands)
    df['signal_bollinger'] = 0
    df.loc[df['Close'] > df['upperband'], 'signal_bollinger'] = -1  # Sell signal
    df.loc[df['Close'] < df['lowerband'], 'signal_bollinger'] = 1   # Buy signal

    # Momentum Strategy (using Moving Average Crossover and RSI)
    df['signal_momentum'] = 0
    df.loc[(df['short_sma'] > df['long_sma']) & (df['RSI'] > 50), 'signal_momentum'] = 1  # Buy signal
    df.loc[(df['short_sma'] < df['long_sma']) & (df['RSI'] < 50), 'signal_momentum'] = -1  # Sell signal

    # Combine signals
    df['final_signal'] = 'Hold'
    # df['total_signals'] = df[['signal_bollinger', 'signal_momentum']].sum(axis=1)
    df['total_signals'] = df[['signal_bollinger']].sum(axis=1)
    df.loc[df['total_signals'] > 0, 'final_signal'] = 'Buy'
    df.loc[df['total_signals'] < 0, 'final_signal'] = 'Sell'

    return df


def all_signals(data_with_indicators: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Generate all signals for each asset in the dataset.

    Parameters:
    - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators for each ticker.

    Returns:
    - final_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.
    """
    final_dict = {}

    for asset, indicator_data in data_with_indicators.items():
        try:
            df = pd.DataFrame(indicator_data)
            if df.empty:
                logging.warning(f"No data available for {asset}, skipping.")
                continue

            df_with_signals = generate_signals(df)
            final_dict[asset] = df_with_signals.to_dict('list')
            logging.info(f"Signals generated for {asset}.")
        except Exception as e:
            logging.error(f"Error generating signals for {asset}: {e}")

    return final_dict
