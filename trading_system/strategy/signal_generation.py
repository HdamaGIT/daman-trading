import pandas as pd
from typing import Dict, Any, Optional
import logging


def generate_signals_for_ticker(
    df: pd.DataFrame,
    signal_params: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Generate trading signals for a single asset.
    """

    # Default parameters
    default_params = dict(
        min_hold_period=5,
        volume_lookback_period=10,
        trailing_stop_pct=0.05,
        take_profit_pct=0.10,
        buy_rsi_threshold=60,
        sell_rsi_threshold=40,
    )
    if signal_params:
        default_params.update(signal_params)

    p = default_params

    required_cols = ['Close', 'Volume']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        logging.error(f"Data missing required columns: {missing_cols}")
        return pd.DataFrame()

    # Compute rolling volume MA
    df['volume_ma'] = df['Volume'].rolling(window=p['volume_lookback_period']).mean()

    warmup_window = max(50, 26, p['volume_lookback_period'])
    if len(df) <= warmup_window:
        logging.warning("Not enough data to generate signals after warmup trimming.")
        return pd.DataFrame()

    df = df.iloc[warmup_window:].copy()

    if df.empty:
        logging.warning("DataFrame is empty after trimming.")
        return pd.DataFrame()

    indicator_cols = [
        'fast_ema', 'slow_ema', 'RSI',
        'macd', 'macdsignal', 'volume_ma'
    ]

    missing_cols = [col for col in indicator_cols if col not in df.columns]
    if missing_cols:
        logging.error(f"Missing required columns for signal generation: {missing_cols}")
        return pd.DataFrame()

    df = df.dropna(subset=indicator_cols)

    if df.empty:
        logging.warning("DataFrame is empty after dropping NaNs in indicators.")
        return pd.DataFrame()

    logging.info("Calculating Buy Signals...")

    df['buy_signal'] = (
        (df['fast_ema'] > df['slow_ema'])
        & (df['RSI'] > p['buy_rsi_threshold'])
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
        | (df['RSI'] < p['sell_rsi_threshold'])
        | (df['macd'] < df['macdsignal'])
        | (df['Close'] < df['highest_since_buy'] * (1 - p['trailing_stop_pct']))
        | (df['Close'] > df['entry_price'] * (1 + p['take_profit_pct']))
    )

    df['signal'] = 0
    df['position'] = 0

    holding_position = False
    hold_counter = 0

    for i in range(len(df)):
        if holding_position:
            hold_counter += 1

        if df['buy_signal'].iloc[i] and not holding_position:
            df.at[df.index[i], 'signal'] = 1
            holding_position = True
            hold_counter = 0

        elif (
            df['sell_signal'].iloc[i]
            and holding_position
            and hold_counter >= p['min_hold_period']
        ):
            df.at[df.index[i], 'signal'] = -1
            holding_position = False

        if df['signal'].iloc[i] == 1:
            df.at[df.index[i], 'position'] = 1
        elif df['signal'].iloc[i] == -1:
            df.at[df.index[i], 'position'] = 0
        elif i > 0:
            df.at[df.index[i], 'position'] = df.at[df.index[i - 1], 'position']

    return df



def all_signals(
    data_with_indicators: Dict[str, pd.DataFrame],
    signal_params: Optional[Dict[str, Any]] = None
) -> Dict[str, pd.DataFrame]:
    """
    Generate momentum signals for each asset.

    Parameters
    ----------
    data_with_indicators : dict
        Dictionary of DataFrames keyed by ticker.
    signal_params : dict, optional
        Parameters to pass to signal generation.

    Returns
    -------
    dict
        Dictionary of DataFrames with signals for each asset.
    """

    final_dict = {}

    for asset, df in data_with_indicators.items():
        try:
            if df.empty:
                logging.warning(f"No data for {asset}, skipping.")
                continue

            # If DataFrame has multi-index columns, extract the relevant asset slice
            if isinstance(df.columns, pd.MultiIndex):
                # Extract columns matching either (col, asset) or (col, "")
                asset_cols = [
                    col for col in df.columns
                    if col[1] == asset or col[1] == ""
                ]

                df_asset = df.loc[:, asset_cols].copy()

                # Flatten MultiIndex columns
                df_asset.columns = [col[0] for col in df_asset.columns]

            else:
                df_asset = df.copy()

            # Now df_asset has flat columns:
            # ['Open', 'High', 'fast_ema', 'RSI', ...]

            if df_asset.empty:
                logging.warning(f"Data slice for {asset} is empty.")
                continue

            df_with_signals = generate_signals_for_ticker(df_asset, signal_params)

            if df_with_signals.empty:
                logging.warning(f"No usable data for {asset} after signal generation. Skipping.")
                continue

            final_dict[asset] = df_with_signals
            logging.info(f"Signals generated for {asset}.")

        except Exception as e:
            logging.error(f"Error generating signals for {asset}: {e}")

    if not final_dict:
        logging.error("No signals generated for any assets.")
    else:
        logging.info(f"Signals generated for {len(final_dict)} assets.")

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
