# system_live/strategies/__init__.py

"""
Strategy loading utilities.

Each strategy lives in a subpackage under this folder, e.g.:

system_live/strategies/my_strategy/
    __init__.py
    strategy.py

The strategy module must expose ONE of the following:
- build_strategy(instruments: list[str]) -> StrategyInstance
- or: a class called Strategy that can be instantiated with (instruments=...)

A StrategyInstance must implement:

- name: str
- timeframe: str
- get_required_lookback() -> int
- get_instruments() -> list[str]
- compute_indicators(df: pd.DataFrame) -> pd.DataFrame
- generate_signals(df: pd.DataFrame, open_trades_for_instrument: list[dict]) -> list[Signal]
"""

from __future__ import annotations

import importlib
from typing import Any, List


def load_strategy(strategy_name: str, instruments: List[str]) -> Any:
    """
    Dynamically load a strategy from system_live.strategies.<strategy_name>.strategy
    """
    module_path = f"system_live.strategies.{strategy_name}.strategy"
    module = importlib.import_module(module_path)

    if hasattr(module, "build_strategy"):
        return module.build_strategy(instruments=instruments)

    if hasattr(module, "Strategy"):
        return module.Strategy(instruments=instruments)

    raise RuntimeError(
        f"Strategy module {module_path} must define build_strategy() or Strategy class."
    )
