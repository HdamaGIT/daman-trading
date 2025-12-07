import numpy as np
import pandas as pd

from system_development.engine.indicators import add_core_indicators
from .config import StrategyParams


def prepare_dataframe(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """
    Add indicators and generate regime + entry signals.
    """
    df = add_core_indicators(
        df,
        ema_fast=params.ema_fast,
        ema_slow=params.ema_slow,
        rsi_period=params.rsi_period,
        atr_period=params.atr_period,
        adx_period=params.adx_period,
    )

    # Trend regime classification
    uptrend = (df["ADX"] > params.adx_trend_threshold) & (
        df["Close"] > df["EMA_Slow"]
    )
    downtrend = (df["ADX"] > params.adx_trend_threshold) & (
        df["Close"] < df["EMA_Slow"]
    )

    df["Trend"] = np.where(uptrend, 1, np.where(downtrend, -1, 0))

    # Entry signals
    df["Signal"] = 0

    # Long: pullback to EMA_Fast, RSI oversold, close crossing back above EMA_Fast
    long_condition = (
        (df["Trend"] == 1)
        & (df["RSI"] < params.rsi_oversold)
        & (df["Close"] > df["EMA_Fast"])
        & (df["Close"].shift(1) < df["EMA_Fast"].shift(1))
    )

    # Short: mirror
    short_condition = (
        (df["Trend"] == -1)
        & (df["RSI"] > params.rsi_overbought)
        & (df["Close"] < df["EMA_Fast"])
        & (df["Close"].shift(1) > df["EMA_Fast"].shift(1))
    )

    df.loc[long_condition, "Signal"] = 1
    df.loc[short_condition, "Signal"] = -1

    return df
