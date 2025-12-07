import numpy as np
import pandas as pd

from system.system_development.engine.indicators import add_core_indicators
from .config import StrategyParams


def prepare_dataframe(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """
    Add indicators, classify trend regime, and generate entry signals.

    Logic (v1):

    1. TREND:
       - Uptrend   if ADX > threshold and Close > EMA_Slow
       - Downtrend if ADX > threshold and Close < EMA_Slow
       - Else: no trend (0) → no trades

    2. ENTRY:
       - Long  when:
         * Trend == 1 (uptrend)
         * RSI crosses below oversold (fresh pullback)
         * Price is near or below EMA_Fast (we're buying a dip toward the mean)

       - Short when:
         * Trend == -1 (downtrend)
         * RSI crosses above overbought
         * Price is near or above EMA_Fast

    We purposely don't also require an EMA cross on the same bar — that made
    signals extremely rare. This version should generate a reasonable number
    of trades while keeping the intent of "trend + pullback".
    """
    df = add_core_indicators(
        df,
        ema_fast=params.ema_fast,
        ema_slow=params.ema_slow,
        rsi_period=params.rsi_period,
        atr_period=params.atr_period,
        adx_period=params.adx_period,
    )

    df = df.copy()

    # ----- Trend regime classification -----
    uptrend = (df["ADX"] > params.adx_trend_threshold) & (
        df["Close"] > df["EMA_Slow"]
    )
    downtrend = (df["ADX"] > params.adx_trend_threshold) & (
        df["Close"] < df["EMA_Slow"]
    )

    df["Trend"] = np.where(uptrend, 1, np.where(downtrend, -1, 0))

    # ----- Entry signals -----
    df["Signal"] = 0

    # RSI crosses BELOW oversold (fresh pullback), in an uptrend,
    # and price is at/under the fast EMA (we're near the mean)
    rsi_cross_down = (df["RSI"] < params.rsi_oversold) & (
        df["RSI"].shift(1) >= params.rsi_oversold
    )
    long_condition = (
        (df["Trend"] == 1)
        & rsi_cross_down
        & (df["Close"] <= df["EMA_Fast"])
    )

    # RSI crosses ABOVE overbought, in a downtrend,
    # and price is at/above the fast EMA
    rsi_cross_up = (df["RSI"] > params.rsi_overbought) & (
        df["RSI"].shift(1) <= params.rsi_overbought
    )
    short_condition = (
        (df["Trend"] == -1)
        & rsi_cross_up
        & (df["Close"] >= df["EMA_Fast"])
    )

    df.loc[long_condition, "Signal"] = 1
    df.loc[short_condition, "Signal"] = -1

    return df
