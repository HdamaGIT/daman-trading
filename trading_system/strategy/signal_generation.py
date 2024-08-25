import pandas as pd
from typing import Dict, Any

def generate_signals(df: pd.DataFrame) -> pd.DataFrame:
    """
    Generate trading signals based on various technical indicators.

    Parameters:
    - df (pd.DataFrame): DataFrame with calculated indicators.

    Returns:
    - df (pd.DataFrame): DataFrame with trading signals added.
    """
    df['signal_sma'] = 0
    df.loc[df['short_sma'] > df['long_sma'], 'signal_sma'] = 1
    df.loc[df['short_sma'] < df['long_sma'], 'signal_sma'] = -1

    df['signal_macd'] = 0
    df.loc[df['macd'] > df['macdsignal'], 'signal_macd'] = 1
    df.loc[df['macd'] < df['macdsignal'], 'signal_macd'] = -1

    df['signal_stochastic'] = 0
    df.loc[df['slowk'] > df['slowd'], 'signal_stochastic'] = 1
    df.loc[df['slowk'] < df['slowd'], 'signal_stochastic'] = -1

    df['signal_bollinger'] = 0
    df.loc[df['Close'] > df['upperband'], 'signal_bollinger'] = -1
    df.loc[df['Close'] < df['lowerband'], 'signal_bollinger'] = 1

    df['final_signal'] = 'Hold'
    df['total_signals'] = df[['signal_sma', 'signal_macd', 'signal_stochastic', 'signal_bollinger']].sum(axis=1)
    df.loc[df['total_signals'] >= 2, 'final_signal'] = 'Buy'
    df.loc[df['total_signals'] <= -2, 'final_signal'] = 'Sell'

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
        df = pd.DataFrame(indicator_data)
        df_with_signals = generate_signals(df)
        final_dict[asset] = df_with_signals.to_dict('list')

    return final_dict
