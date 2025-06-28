import pandas as pd
from typing import Dict, Any
import logging


def generate_signals(df: pd.DataFrame, min_hold_period: int = 5) -> pd.DataFrame:
    volume_lookback_period = 10
    trailing_stop_pct = 0.05
    take_profit_pct = 0.10

    df['volume_ma'] = df['Volume'].rolling(window=volume_lookback_period).mean()

    # How many rows to skip for indicator warmup
    lookback_window = max(50, 26, volume_lookback_period)

    if len(df) <= lookback_window:
        logging.warning("Not enough data to generate signals after lookback trimming.")
        return df

    # Drop warmup rows
    df = df.iloc[lookback_window:].copy()

    if df.empty:
        logging.warning("DataFrame is empty after dropping NaNs. Skipping signal generation.")
        return df

    logging.info("Calculating Buy Signals...")
    df['buy_signal'] = (
        (df['fast_ema'] > df['slow_ema'])
        & (df['RSI'] > 60)
        & (df['macd'] > df['macdsignal'])
        & (df['Volume'] > df['volume_ma'])
    )

    df['highest_since_buy'] = df['Close'].cummax()

    if df['buy_signal'].any():
        df['entry_price'] = df['Close'].where(df['buy_signal']).ffill()
        df['entry_price'].fillna(df['Close'], inplace=True)
    else:
        df['entry_price'] = df['Close']

    for col in ['Close', 'highest_since_buy', 'entry_price']:
        df[col] = df[col].reindex(df.index)

    logging.info("Calculating Sell Signals...")
    df['sell_signal'] = (
        (df['fast_ema'] < df['slow_ema'])
        | (df['RSI'] < 40)
        | (df['macd'] < df['macdsignal'])
        | (df['Close'] < df['highest_since_buy'] * (1 - trailing_stop_pct))
        | (df['Close'] > df['entry_price'] * (1 + take_profit_pct))
    )

    df['signal'] = 0
    df['position'] = 0

    holding_position = False
    hold_counter = 0

    for i in range(len(df)):
        if holding_position:
            hold_counter += 1

        if df['buy_signal'].iloc[i] and not holding_position:
            df.at[i, 'signal'] = 1
            holding_position = True
            hold_counter = 0

        elif df['sell_signal'].iloc[i] and holding_position and hold_counter >= min_hold_period:
            df.at[i, 'signal'] = -1
            holding_position = False

        if df['signal'].iloc[i] == 1:
            df.at[i, 'position'] = 1
        elif df['signal'].iloc[i] == -1:
            df.at[i, 'position'] = 0
        elif i > 0:
            df.at[i, 'position'] = df.at[i - 1, 'position']

    return df


def all_signals(data_with_indicators: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    final_dict = {}

    for asset, df in data_with_indicators.items():
        try:
            if df.empty:
                logging.warning(f"No data for {asset}, skipping.")
                continue

            df_with_signals = generate_signals(df)
            final_dict[asset] = df_with_signals
            logging.info(f"Signals generated for {asset}.")
        except Exception as e:
            logging.error(f"Error generating signals for {asset}: {e}")

    return final_dict

# def generate_signals(df: pd.DataFrame, min_hold_period: int = 5) -> pd.DataFrame:
#     """
#     Generate trading signals based on momentum indicators.
#     """
#     # Parameters
#     volume_lookback_period = 10
#     trailing_stop_percentage = 0.05
#     take_profit_percentage = 0.10
#
#     df['volume_ma'] = df['Volume'].rolling(window=volume_lookback_period).mean()
#
#     df['buy_signal'] = (
#         (df['fast_ema'] > df['slow_ema']) &
#         (df['RSI'] > 60) &
#         (df['macd'] > df['macdsignal']) &
#         (df['Volume'] > df['volume_ma'])
#     )
#
#     df['highest_since_buy'] = df['Close'].cummax()
#
#     # Safe entry price
#     df['entry_price'] = df['Close'].where(df['buy_signal']).ffill()
#     df['entry_price'].fillna(df['Close'], inplace=True)
#
#     df['sell_signal'] = (
#         (df['fast_ema'] < df['slow_ema']) |
#         (df['RSI'] < 40) |
#         (df['macd'] < df['macdsignal']) |
#         (df['Close'] < df['highest_since_buy'] * (1 - trailing_stop_percentage)) |
#         (df['Close'] > df['entry_price'] * (1 + take_profit_percentage))
#     )
#
#     df['signal'] = 0
#     df['position'] = 0
#
#     holding_position = False
#     holding_period_counter = 0
#
#     for i in range(1, len(df)):
#         if holding_position:
#             holding_period_counter += 1
#
#         if df['buy_signal'].iloc[i] and not holding_position:
#             df.at[i, 'signal'] = 1
#             holding_position = True
#             holding_period_counter = 0
#
#         elif df['sell_signal'].iloc[i] and holding_position and holding_period_counter >= min_hold_period:
#             df.at[i, 'signal'] = -1
#             holding_position = False
#
#         if df['signal'].iloc[i] == 1:
#             df.at[i, 'position'] = 1
#         elif df['signal'].iloc[i] == -1:
#             df.at[i, 'position'] = 0
#         else:
#             df.at[i, 'position'] = df['position'].iloc[i-1]
#
#     return df
#
#
# def all_signals(data_with_indicators: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
#     """
#     Generate all momentum-based signals for each asset in the dataset.
#
#     Parameters:
#     - data_with_indicators (Dict[str, Dict[str, Any]]): Dictionary with indicators for each ticker.
#
#     Returns:
#     - final_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.
#     """
#     final_dict = {}
#
#     for asset, indicator_data in data_with_indicators.items():
#         try:
#             df = pd.DataFrame(indicator_data)
#             if df.empty:
#                 logging.warning(f"No data available for {asset}, skipping.")
#                 continue
#
#             df_with_signals = generate_signals(df)
#             final_dict[asset] = df_with_signals
#             logging.info(f"Momentum signals generated for {asset}.")
#         except Exception as e:
#             logging.error(f"Error generating signals for {asset}: {e}")
#
#     return final_dict
