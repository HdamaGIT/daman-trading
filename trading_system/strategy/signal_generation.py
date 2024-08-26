import pandas as pd
import numpy as np
from typing import Dict, Any
import logging


def calculate_z_score(series: pd.Series, window: int = 20) -> pd.Series:
    """
    Calculate the Z-Score for a given price series.

    Parameters:
    - series (pd.Series): The price series to calculate the Z-Score for.
    - window (int): The rolling window for the Z-Score calculation.

    Returns:
    - z_score (pd.Series): The calculated Z-Score.
    """
    mean = series.rolling(window=window).mean()
    std = series.rolling(window=window).std()
    z_score = (series - mean) / std
    return z_score


def generate_signals(df: pd.DataFrame, btc_eth_ratio: pd.Series) -> pd.DataFrame:
    """
    Generate trading signals focused on mean reversion with integrated risk management.

    Parameters:
    - df (pd.DataFrame): DataFrame with calculated indicators.
    - btc_eth_ratio (pd.Series): The BTC/ETH ratio series to calculate the Z-Score.

    Returns:
    - df (pd.DataFrame): DataFrame with trading signals, stop-loss, and take-profit levels added.
    """

    # Mean Reversion Strategy (using Bollinger Bands and Z-Score)
    df['z_score'] = calculate_z_score(btc_eth_ratio)
    df['signal_mean_reversion'] = 0

    # Define stop-loss and take-profit levels based on the Bollinger Bands and Z-Score
    stop_loss_percentage = 0.05  # Example: 2% stop-loss
    take_profit_percentage = 0.10  # Example: 3% take-profit

    # Calculate stop-loss and take-profit levels dynamically
    df['stop_loss'] = df['Close'] * (1 - stop_loss_percentage)
    df['take_profit'] = df['Close'] * (1 + take_profit_percentage)

    # Buy when price touches lower Bollinger Band or Z-Score indicates extreme negative deviation
    df.loc[(df['Close'] < df['lowerband']) | (df['z_score'] < -2), 'signal_mean_reversion'] = 1

    # Sell when price touches upper Bollinger Band or Z-Score indicates extreme positive deviation
    df.loc[(df['Close'] > df['upperband']) | (df['z_score'] > 2), 'signal_mean_reversion'] = -1

    # Calculate final signal with risk management
    df['final_signal'] = 'Hold'
    df['total_signals'] = df['signal_mean_reversion']

    df.loc[df['total_signals'] > 0, 'final_signal'] = 'Buy'
    df.loc[df['total_signals'] < 0, 'final_signal'] = 'Sell'

    # Integrate stop-loss and take-profit into the final signal
    df['final_signal'] = np.where(
        (df['final_signal'] == 'Buy') & (df['Close'] <= df['stop_loss']),
        'Stop Loss',
        df['final_signal']
    )
    df['final_signal'] = np.where(
        (df['final_signal'] == 'Sell') & (df['Close'] >= df['take_profit']),
        'Take Profit',
        df['final_signal']
    )

    return df


def calculate_btc_eth_ratio(data_with_indicators: Dict[str, Dict[str, Any]]) -> pd.Series:
    """
    Calculate the BTC/ETH ratio from the provided data.

    Parameters:
    - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators for each ticker.

    Returns:
    - btc_eth_ratio (pd.Series): The calculated BTC/ETH ratio series.
    """
    btc_close = pd.Series(data_with_indicators['BTC-GBP']['Close'])
    eth_close = pd.Series(data_with_indicators['ETH-GBP']['Close'])

    # Ensure that the lengths are the same by aligning the data by index (date).
    btc_close.index = pd.to_datetime(data_with_indicators['BTC-GBP']['Date'])
    eth_close.index = pd.to_datetime(data_with_indicators['ETH-GBP']['Date'])

    btc_eth_ratio = btc_close / eth_close
    return btc_eth_ratio

def all_signals(data_with_indicators: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Generate all signals for each asset in the dataset, considering the BTC/ETH ratio.

    Parameters:
    - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators for each ticker.

    Returns:
    - final_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.
    """
    final_dict = {}

    try:
        # Calculate the BTC/ETH ratio for use in the Z-Score calculation
        btc_eth_ratio = calculate_btc_eth_ratio(data_with_indicators)
    except KeyError as e:
        logging.error(f"Missing data for BTC or ETH: {e}")
        return final_dict

    for asset, indicator_data in data_with_indicators.items():
        try:
            df = pd.DataFrame(indicator_data)
            if df.empty:
                logging.warning(f"No data available for {asset}, skipping.")
                continue

            df_with_signals = generate_signals(df, btc_eth_ratio)
            final_dict[asset] = df_with_signals.to_dict('list')
            logging.info(f"Signals generated for {asset}.")
        except Exception as e:
            logging.error(f"Error generating signals for {asset}: {e}")

    return final_dict