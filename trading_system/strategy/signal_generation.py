import pandas as pd
import numpy as np
from typing import Dict, Any
import logging


def generate_signals(df: pd.DataFrame, min_hold_period: int = 5) -> pd.DataFrame:
    """
    Generate trading signals based on momentum indicators including EMA crossovers, RSI, MACD, volume confirmation,
    trailing stop, take-profit logic, and minimum hold period.

    Parameters:
    - df (pd.DataFrame): DataFrame with OHLCV data and calculated momentum indicators.
    - min_hold_period (int): Minimum number of periods to hold a position before allowing another sell signal.

    Returns:
    - df (pd.DataFrame): DataFrame with generated trading signals.
    """
    # Parameters
    volume_lookback_period = 10  # Look-back period for volume moving average
    trailing_stop_percentage = 0.05  # Example: 5% trailing stop
    take_profit_percentage = 0.10  # Example: 10% take-profit level

    # Calculate Volume Moving Average (if not already present in the indicator calculation)
    df['volume_ma'] = df['Volume'].rolling(window=volume_lookback_period).mean()

    # Entry Signal: Buy when:
    # - Fast EMA > Slow EMA (indicating upward trend),
    # - RSI > 60 (indicating positive momentum),
    # - MACD > Signal Line (indicating upward momentum),
    # - Volume > Volume Moving Average (indicating strong market participation).
    df['buy_signal'] = (
        (df['fast_ema'] > df['slow_ema']) &
        (df['RSI'] > 60) &
        (df['macd'] > df['macdsignal']) &
        (df['Volume'] > df['volume_ma'])
    )

    # Track the highest price since the buy signal
    df['highest_since_buy'] = df['Close'].cummax()

    # Track the entry price (i.e., price when the buy signal was triggered)
    df['entry_price'] = df['Close'].where(df['buy_signal']).ffill()  # Forward fill to track entry price

    # New Exit Condition with Take-Profit and Trailing Stop
    df['sell_signal'] = (
        (df['fast_ema'] < df['slow_ema']) |  # Trend reversal
        (df['RSI'] < 40) |  # Lower RSI threshold to avoid overreaction
        (df['macd'] < df['macdsignal']) |  # MACD crosses below signal
        (df['Close'] < df['highest_since_buy'] * (1 - trailing_stop_percentage)) |  # Trailing stop-loss condition
        (df['Close'] > df['entry_price'] * (1 + take_profit_percentage))  # Take-profit condition
    )

    # Initialize 'signal' and 'position' columns
    df['signal'] = 0
    df['position'] = 0

    # Flag to track if we're currently holding a position
    holding_position = False
    holding_period_counter = 0  # Counter for the number of periods holding the position

    # Iterate through rows to determine positions based on buy/sell signals
    for i in range(1, len(df)):
        # If holding a position, increase the counter
        if holding_position:
            holding_period_counter += 1

        if df['buy_signal'].iloc[i] and not holding_position:
            # Only buy if we're not already holding a position
            df['signal'].iloc[i] = 1  # Generate a buy signal
            holding_position = True  # Update flag to indicate we are holding a position
            holding_period_counter = 0  # Reset holding period counter
            print(f"Buy signal triggered at {df.index[i]} with price {df['Close'].iloc[i]}")

        elif df['sell_signal'].iloc[i] and holding_position and holding_period_counter >= min_hold_period:
            # Only sell if we're currently holding a position and minimum hold period is satisfied
            df['signal'].iloc[i] = -1  # Generate a sell signal
            holding_position = False  # Update flag to indicate we are no longer holding a position
            print(f"Sell signal triggered at {df.index[i]} with price {df['Close'].iloc[i]}")

        # Update position based on the generated signal
        if df['signal'].iloc[i] == 1:
            df['position'].iloc[i] = 1  # Enter a long position
            print(f"Entered long position at {df.index[i]} with price {df['Close'].iloc[i]}")
        elif df['signal'].iloc[i] == -1:
            df['position'].iloc[i] = 0  # Exit the position
            print(f"Exited position at {df.index[i]} with price {df['Close'].iloc[i]}")
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