# trading_system/system_development/strategies/breakout_v1/rules.py

from __future__ import annotations

import numpy as np
import pandas as pd

from engine.indicators import add_core_indicators
from .config import StrategyParams


def prepare_dataframe(df: pd.DataFrame, params: StrategyParams) -> pd.DataFrame:
    """
    Volatility breakout strategy:

    Idea:
      - Look for periods of relatively LOW ATR (volatility compression).
      - Define a Donchian-style range (recent high/low).
      - Enter on breakout of that range in the direction of the trend
        (using EMA_slow + optional ADX filter).

    Trend filter (on trading timeframe):
      - Uptrend   if Close > EMA_Slow
      - Downtrend if Close < EMA_Slow

    Entry:
      - Long breakout when:
          * Uptrend
          * ATR is "low" (current ATR < low_vol_mult * ATR_MA(vol_lookback))
          * Close breaks above prior donchian_high (shifted)
          * ADX >= adx_trend_threshold

      - Short breakout when:
          * NOT long_only
          * Downtrend
          * same low-vol condition
          * Close breaks below prior donchian_low
          * ADX >= adx_trend_threshold
    """

    # --- Add core indicators (EMA, ATR, ADX, etc.) ---
    df = add_core_indicators(
        df,
        ema_fast=params.ema_fast,
        ema_slow=params.ema_slow,
        rsi_period=params.rsi_period,
        atr_period=params.atr_period,
        adx_period=params.adx_period,
    )

    df = df.copy()

    # --- Trend filter from EMA_slow ---
    df["Trend"] = np.where(df["Close"] > df["EMA_Slow"], 1,
                           np.where(df["Close"] < df["EMA_Slow"], -1, 0))

    # --- Donchian range (use prior N bars, exclude current bar) ---
    lookback = params.donchian_lookback
    donchian_high = df["High"].rolling(lookback).max().shift(1)
    donchian_low = df["Low"].rolling(lookback).min().shift(1)

    df["Donchian_High"] = donchian_high
    df["Donchian_Low"] = donchian_low

    # --- Volatility compression filter (ATR vs ATR moving average) ---
    atr = df["ATR"]
    atr_ma = atr.rolling(params.vol_lookback).mean()
    low_vol = atr < (params.low_vol_mult * atr_ma)

    df["ATR_MA"] = atr_ma
    df["Low_Vol"] = low_vol

    # --- ADX trend strength filter ---
    adx = df["ADX"]
    strong_trend = adx >= params.adx_trend_threshold

    # --- Breakout conditions ---
    close = df["Close"]

    long_breakout = (
        (df["Trend"] == 1)
        & low_vol
        & strong_trend
        & (close > donchian_high)
    )

    if params.long_only:
        short_breakout = pd.Series(False, index=df.index)
    else:
        short_breakout = (
            (df["Trend"] == -1)
            & low_vol
            & strong_trend
            & (close < donchian_low)
        )

    # --- Signal column ---
    df["Signal"] = 0
    df.loc[long_breakout, "Signal"] = 1
    df.loc[short_breakout, "Signal"] = -1

    return df
