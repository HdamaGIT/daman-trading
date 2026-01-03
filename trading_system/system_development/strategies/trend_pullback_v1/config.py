from dataclasses import dataclass
from typing import List


# Default symbols for testing (you can edit these)
INDEX_SYMBOLS: List[str] = ["^GSPC", "^NDX", "^FTSE"]  # S&P 500, Nasdaq 100, FTSE 100
# FX_SYMBOLS: List[str] = ["GBPUSD=X", "EURUSD=X", "USDJPY=X"]
FX_SYMBOLS: List[str] = ["EURUSD=X"]

@dataclass
class StrategyParams:
    ema_fast: int = 12
    ema_slow: int = 50
    rsi_period: int = 5
    atr_period: int = 14
    adx_period: int = 20
    adx_trend_threshold: float = 20.0
    adx_exit_threshold: float = 18.0
    rsi_oversold: float = 35.0
    rsi_overbought: float = 65.0
    stop_atr_mult: float = 1.0
    tp_atr_mult: float = 2.5
    initial_capital: float = 10_000.0
    risk_per_trade: float = 0.02  # 2%
    exit_mode: str = "fixed_rr"   # "fixed_rr" or "trend_follow"
    trail_stops: bool = True

    # "cash" = realised PnL only (your current behaviour)
    # "mtm"  = mark-to-market: realised + open PnL
    equity_mode: str = "mtm"

    # entry mode as you already had
    entry_mode: str = "deep_pullback"


DEFAULT_PARAMS = StrategyParams()
