from dataclasses import dataclass
from typing import List


# Default symbols for testing (you can edit these)
INDEX_SYMBOLS: List[str] = ["^GSPC", "^NDX", "^FTSE"]  # S&P 500, Nasdaq 100, FTSE 100
FX_SYMBOLS: List[str] = ["GBPUSD=X", "EURUSD=X", "USDJPY=X"]


@dataclass
class StrategyParams:
    ema_fast: int = 20
    ema_slow: int = 50
    rsi_period: int = 5
    atr_period: int = 14
    adx_period: int = 20
    adx_trend_threshold: float = 20.0
    adx_exit_threshold: float = 18.0
    rsi_oversold: float = 30.0
    rsi_overbought: float = 70.0
    stop_atr_mult: float = 1.0
    tp_atr_mult: float = 1.5
    initial_capital: float = 10_000.0
    risk_per_trade: float = 0.01  # 1%


DEFAULT_PARAMS = StrategyParams()
