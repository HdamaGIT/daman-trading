import numpy as np
import pandas as pd

from system.system_development.engine.indicators import add_core_indicators
from .config import StrategyParams


def prepare_dataframe(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """
    EMA-only trend regime + looser RSI pullback entries.

    Trend:
      - Uptrend   if Close > EMA_Slow and EMA_Slow is rising
      - Downtrend if Close < EMA_Slow and EMA_Slow is falling
      - Else Trend = 0

    Entry (LOOSENED):
      - Long when:
          * Trend == 1
          * RSI <= rsi_oversold (e.g. 35)
          * Close <= EMA_Fast (near/under fast EMA)

      - Short when:
          * Trend == -1
          * RSI >= rsi_overbought (e.g. 65)
          * Close >= EMA_Fast
    """

    # Add indicators
    df = add_core_indicators(
        df,
        ema_fast=params.ema_fast,
        ema_slow=params.ema_slow,
        rsi_period=params.rsi_period,
        atr_period=params.atr_period,
        adx_period=params.adx_period,
    )

    df = df.copy()

    # ----- Trend regime from EMA50 and its slope -----
    ema_slow = df["EMA_Slow"]
    ema_slow_slope = ema_slow - ema_slow.shift(1)

    uptrend = (df["Close"] > ema_slow) & (ema_slow_slope > 0)
    downtrend = (df["Close"] < ema_slow) & (ema_slow_slope < 0)

    df["Trend"] = np.where(uptrend, 1, np.where(downtrend, -1, 0))

    # ----- Entry signals -----
    df["Signal"] = 0

    # LONG: uptrend, RSI <= oversold threshold, price at/below fast EMA
    long_condition = (
        (df["Trend"] == 1)
        & (df["RSI"] <= params.rsi_oversold)
        & (df["Close"] <= df["EMA_Fast"])
    )

    # SHORT: downtrend, RSI >= overbought threshold, price at/above fast EMA
    short_condition = (
        (df["Trend"] == -1)
        & (df["RSI"] >= params.rsi_overbought)
        & (df["Close"] >= df["EMA_Fast"])
    )

    df.loc[long_condition, "Signal"] = 1
    df.loc[short_condition, "Signal"] = -1

    return df
