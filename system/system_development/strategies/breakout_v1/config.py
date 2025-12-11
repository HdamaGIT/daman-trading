# system/system_development/strategies/breakout_v1/config.py

from dataclasses import dataclass
from typing import List

# Default symbols for this breakout strategy (can be overridden)
INDEX_SYMBOLS: List[str] = ["^GSPC", "^NDX", "^FTSE"]
FX_SYMBOLS: List[str] = []  # keep empty for now, this is index-focused


@dataclass
class StrategyParams:
    # Core indicator settings (re-use existing engine indicators)
    ema_fast: int = 20        # not strictly needed, but available
    ema_slow: int = 50        # used as trend filter
    rsi_period: int = 5       # unused here, but kept for compatibility
    atr_period: int = 14
    adx_period: int = 14

    # Breakout-specific settings
    donchian_lookback: int = 20     # bars for range high/low
    vol_lookback: int = 50          # bars for ATR moving average
    low_vol_mult: float = 0.8       # "low vol" if ATR < low_vol_mult * ATR_MA
    adx_trend_threshold: float = 20.0  # require some trend strength for entries

    # Risk & trade management
    stop_atr_mult: float = 1.0      # initial stop distance in ATRs
    tp_atr_mult: float = 2.5        # fixed RR target multiple
    initial_capital: float = 10_000.0
    risk_per_trade: float = 0.01    # 1% risk per trade by default
    exit_mode: str = "fixed_rr"     # "fixed_rr" or "trend_follow"
    trail_stops: bool = True

    # "cash" = realised PnL only, "mtm" = mark-to-market equity
    equity_mode: str = "mtm"

    # Long-only for indices by default
    long_only: bool = True


DEFAULT_PARAMS = StrategyParams()
