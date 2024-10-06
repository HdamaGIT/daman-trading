import pandas as pd
import numpy as np
from typing import Dict, Any
import logging


def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trading signals based on momentum indicators including EMA crossovers, RSI, and MACD.

    Parameters:
    - df (pd.DataFrame): DataFrame with OHLCV data and calculated momentum indicators.

    Returns:
    - df (pd.DataFrame): DataFrame with generated trading signals.
    """
    # Entry Signal: Buy when fast EMA crosses above slow EMA, RSI > 50, and MACD > Signal Line
    df['buy_signal'] = (df['fast_ema'] > df['slow_ema']) & (df['RSI'] > 50) & (df['macd'] > df['macdsignal'])

    # Exit Signal: Sell when fast EMA crosses below slow EMA or RSI < 50 or MACD < Signal Line
    df['sell_signal'] = (df['fast_ema'] < df['slow_ema']) | (df['RSI'] < 50) | (df['macd'] < df['macdsignal'])

    # Initialize 'signal' and 'position' columns
    df['signal'] = 0
    df['position'] = 0

    # Iterate through rows to determine positions based on buy/sell signals
    for i in range(1, len(df)):
        if df['buy_signal'].iloc[i]:
            df['signal'].iloc[i] = 1  # Generate a buy signal
        elif df['sell_signal'].iloc[i]:
            df['signal'].iloc[i] = -1  # Generate a sell signal

        # Update position based on the generated signal
        if df['signal'].iloc[i] == 1:
            df['position'].iloc[i] = 1  # Enter a long position
        elif df['signal'].iloc[i] == -1:
            df['position'].iloc[i] = 0  # Exit the position
        else:
            # Maintain the previous position if no new signal is generated
            df['position'].iloc[i] = df['position'].iloc[i-1]

    return df


def all_signals(data_with_indicators: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Generate all momentum-based signals for each asset in the dataset.

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
            logging.info(f"Momentum signals generated for {asset}.")
        except Exception as e:
            logging.error(f"Error generating signals for {asset}: {e}")

    return final_dict