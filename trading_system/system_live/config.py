# system_live/config.py

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class InstrumentConfig:
    """Configuration for a single tradable instrument."""
    symbol: str              # e.g. "ES=F", "^GSPC", "EURUSD=X"
    point_value: float = 1.0 # monetary value of 1 point move, default 1


@dataclass
class StrategyRuntimeConfig:
    """Runtime config for a specific strategy instance."""
    strategy_name: str           # folder name under system_live/strategies
    timeframe: str               # e.g. "4h"
    capital: float               # total trading capital (e.g. 10_000.0)
    capital_allocation: float    # fraction of capital allocated to this strategy, e.g. 1.0
    risk_per_trade: float        # fraction of allocated capital to risk per trade, e.g. 0.01
    mode: str = "paper"          # "paper" or "live"


@dataclass
class SystemConfig:
    """
    Top-level config for the live trading_system.

    For v1, you can simply edit DEFAULT_CONFIG in this file, or
    later implement reading from a JSON/YAML config file.
    """
    db_path: str
    data_provider: str               # "yahoo" or "dummy"
    instruments: List[InstrumentConfig]
    strategy: StrategyRuntimeConfig

    def get_instrument_config(self, symbol: str) -> Optional[InstrumentConfig]:
        for inst in self.instruments:
            if inst.symbol == symbol:
                return inst
        return None


# --- Default config for a first run --- #

DEFAULT_CONFIG = SystemConfig(
    db_path="trading_live.db",
    data_provider="yahoo",   # change to "yahoo" when you want real data
    instruments=[
        InstrumentConfig(symbol="ES_FAKE", point_value=1.0),
    ],
    strategy=StrategyRuntimeConfig(
        strategy_name="example_strategy",
        timeframe="4h",
        capital=10_000.0,
        capital_allocation=1.0,
        risk_per_trade=0.02,
        mode="paper",
    ),
)
