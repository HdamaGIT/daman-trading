import numpy as np
import pandas as pd

from system.system_development.engine.indicators import add_core_indicators
from .config import StrategyParams


def prepare_dataframe(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """
    EMA-only trend regime + selectable entry modes.

    Trend:
      - Uptrend   if Close > EMA_Slow and EMA_Slow is rising
      - Downtrend if Close < EMA_Slow and EMA_Slow is falling
      - Else Trend = 0

    Entry modes
    -----------

    1) "deep_pullback"  (your current logic)
       Long:
         Trend == 1
         RSI <= rsi_oversold
         Close <= EMA_Fast

    2) "shallow_pullback"  (more trades)
       Long:
         Trend == 1
         RSI <= rsi_oversold + 5      (e.g. ≤ 40 instead of 35)
         Close <= EMA_Fast * 1.01     (within ~1% of fast EMA)

    3) "rebound_cross"  (buy the bounce after dip)
       Long:
         Trend == 1
         RSI <= rsi_oversold + 10     (e.g. ≤ 45)
         Close crosses back ABOVE EMA_Fast
           (today Close > EMA_Fast and yesterday Close <= EMA_Fast)

    Shorts are symmetric conditions for downtrend.
    """

    # --- Add indicators ---
    df = add_core_indicators(
        df,
        ema_fast=params.ema_fast,
        ema_slow=params.ema_slow,
        rsi_period=params.rsi_period,
        atr_period=params.atr_period,
        adx_period=params.adx_period,
    )

    df = df.copy()

    # --- Trend regime from EMA_Slow and its slope ---
    ema_slow = df["EMA_Slow"]
    ema_slow_slope = ema_slow - ema_slow.shift(1)

    uptrend = (df["Close"] > ema_slow) & (ema_slow_slope > 0)
    downtrend = (df["Close"] < ema_slow) & (ema_slow_slope < 0)

    df["Trend"] = np.where(uptrend, 1, np.where(downtrend, -1, 0))

    # --- Entry signals, by mode ---
    mode = getattr(params, "entry_mode", "deep_pullback")
    df["Signal"] = 0

    if mode == "deep_pullback":
        # Current strict logic
        long_condition = (
            (df["Trend"] == 1)
            & (df["RSI"] <= params.rsi_oversold)
            & (df["Close"] <= df["EMA_Fast"])
        )
        short_condition = (
            (df["Trend"] == -1)
            & (df["RSI"] >= params.rsi_overbought)
            & (df["Close"] >= df["EMA_Fast"])
        )

    elif mode == "shallow_pullback":
        # Allow shallower dips and a bit of slop around EMA_fast
        long_condition = (
            (df["Trend"] == 1)
            & (df["RSI"] <= params.rsi_oversold + 5.0)   # e.g. 40
            & (df["Close"] <= df["EMA_Fast"] * 1.01)
        )
        short_condition = (
            (df["Trend"] == -1)
            & (df["RSI"] >= params.rsi_overbought - 5.0)  # e.g. 60
            & (df["Close"] >= df["EMA_Fast"] * 0.99)
        )

    elif mode == "rebound_cross":
        # Buy the bounce back above EMA_fast after a dip
        # First define the "cross" of price vs EMA_fast
        close = df["Close"]
        ema_fast = df["EMA_Fast"]

        long_cross = (close > ema_fast) & (close.shift(1) <= ema_fast.shift(1))
        short_cross = (close < ema_fast) & (close.shift(1) >= ema_fast.shift(1))

        long_condition = (
            (df["Trend"] == 1)
            & long_cross
            & (df["RSI"] <= params.rsi_oversold + 10.0)   # a bit looser
        )
        short_condition = (
            (df["Trend"] == -1)
            & short_cross
            & (df["RSI"] >= params.rsi_overbought - 10.0)
        )

    else:
        raise ValueError(f"Unknown entry_mode: {mode}")

    df.loc[long_condition, "Signal"] = 1
    df.loc[short_condition, "Signal"] = -1

    return df