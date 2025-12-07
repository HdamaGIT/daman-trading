import numpy as np
import pandas as pd


def ema(series: pd.Series, period: int) -> pd.Series:
    return series.ewm(span=period, adjust=False).mean()


def rsi(series: pd.Series, period: int = 14) -> pd.Series:
    """
    Wilder-style RSI.
    """
    delta = series.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)

    avg_gain = gain.ewm(alpha=1 / period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, adjust=False).mean()

    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi_series = 100 - (100 / (1 + rs))
    return rsi_series


def true_range(high: pd.Series, low: pd.Series, close: pd.Series) -> pd.Series:
    prev_close = close.shift(1)
    tr1 = high - low
    tr2 = (high - prev_close).abs()
    tr3 = (low - prev_close).abs()
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
    return tr


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    tr = true_range(high, low, close)
    atr_series = tr.ewm(alpha=1 / period, adjust=False).mean()
    return atr_series


def adx(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    period: int = 14,
) -> pd.Series:
    """
    Welles Wilder ADX implementation.
    """
    up_move = high.diff()
    down_move = -low.diff()

    plus_dm = np.where(
        (up_move > down_move) & (up_move > 0),
        up_move,
        0.0,
    )
    minus_dm = np.where(
        (down_move > up_move) & (down_move > 0),
        down_move,
        0.0,
    )

    plus_dm = pd.Series(plus_dm, index=high.index)
    minus_dm = pd.Series(minus_dm, index=high.index)

    tr = true_range(high, low, close)

    atr_tr = tr.ewm(alpha=1 / period, adjust=False).mean()
    plus_di = 100 * (plus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr_tr)
    minus_di = 100 * (minus_dm.ewm(alpha=1 / period, adjust=False).mean() / atr_tr)

    dx = (100 * (plus_di - minus_di).abs() / (plus_di + minus_di).abs()).replace(
        [np.inf, -np.inf], np.nan
    )
    adx_series = dx.ewm(alpha=1 / period, adjust=False).mean()
    return adx_series


def add_core_indicators(
    df: pd.DataFrame,
    ema_fast: int = 20,
    ema_slow: int = 50,
    rsi_period: int = 5,
    atr_period: int = 14,
    adx_period: int = 20,
) -> pd.DataFrame:
    """
    Add EMA20, EMA50, RSI, ATR, ADX to a price DataFrame.
    """
    df = df.copy()
    df["EMA_Fast"] = ema(df["Close"], ema_fast)
    df["EMA_Slow"] = ema(df["Close"], ema_slow)
    df["RSI"] = rsi(df["Close"], rsi_period)
    df["ATR"] = atr(df["High"], df["Low"], df["Close"], atr_period)
    df["ADX"] = adx(df["High"], df["Low"], df["Close"], adx_period)
    return df
