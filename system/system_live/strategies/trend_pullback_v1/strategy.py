# system_live/strategies/example_strategy/strategy.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Any

import pandas as pd

from ...execution.trade_types import Signal, SignalKind, Direction


@dataclass
class ExampleMACrossStrategy:
    """
    Very simple moving-average cross strategy, for demonstration.

    Entry:
        - Go LONG when fast MA crosses above slow MA and no open long.
        - Go SHORT when fast MA crosses below slow MA and no open short.

    Exit:
        - Generate EXIT signal when the opposite cross occurs for an open trade.

    Stop/target:
        - Stop = entry_price -/+ N * ATR
        - Target = entry_price +|- R * (entry_price - stop_price)
    """

    instruments: List[str]
    name: str = "example_ma_cross"
    timeframe: str = "4h"
    fast_ma: int = 20
    slow_ma: int = 50
    atr_period: int = 14
    stop_atr_multiple: float = 2.0
    target_r_multiple: float = 3.0

    def get_required_lookback(self) -> int:
        return max(self.fast_ma, self.slow_ma, self.atr_period) + 10

    def get_instruments(self) -> List[str]:
        return self.instruments

    def compute_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        df = df.copy()

        df["fast_ma"] = df["close"].rolling(self.fast_ma).mean()
        df["slow_ma"] = df["close"].rolling(self.slow_ma).mean()

        # True range and ATR
        tr1 = df["high"] - df["low"]
        tr2 = (df["high"] - df["close"].shift()).abs()
        tr3 = (df["low"] - df["close"].shift()).abs()
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

        df["atr"] = tr.rolling(self.atr_period).mean()

        return df

    def generate_signals(
        self,
        df: pd.DataFrame,
        open_trades_for_instrument: List[Dict[str, Any]],
    ) -> List[Signal]:
        """
        Generate zero or more signals (entry/exit) for the most recent bar.

        open_trades_for_instrument is a list of dicts from the DB, each representing an open trade.
        """
        signals: List[Signal] = []

        if df.empty:
            return signals

        # focus on last two rows for cross detection
        if len(df) < 2:
            return signals

        last = df.iloc[-1]
        prev = df.iloc[-2]

        timestamp: datetime = df.index[-1].to_pydatetime()
        price: float = float(last["close"])
        fast_now = float(last["fast_ma"])
        slow_now = float(last["slow_ma"])
        fast_prev = float(prev["fast_ma"])
        slow_prev = float(prev["slow_ma"])
        atr_now = float(last["atr"]) if not pd.isna(last["atr"]) else None

        if atr_now is None or pd.isna(fast_now) or pd.isna(slow_now):
            # not enough data
            return signals

        # Determine whether we have open longs / shorts for this instrument
        has_open_long = any(t["direction"] == "long" for t in open_trades_for_instrument)
        has_open_short = any(t["direction"] == "short" for t in open_trades_for_instrument)

        # --- Entry signals --- #
        # Golden cross: fast crosses above slow
        crossed_up = fast_prev <= slow_prev and fast_now > slow_now
        crossed_down = fast_prev >= slow_prev and fast_now < slow_now

        if crossed_up and not has_open_long:
            stop = price - self.stop_atr_multiple * atr_now
            risk_per_unit = price - stop
            target = price + self.target_r_multiple * risk_per_unit

            signals.append(
                Signal(
                    strategy_name=self.name,
                    instrument="",  # filled by runner
                    timeframe=self.timeframe,
                    kind=SignalKind.ENTRY,
                    direction=Direction.LONG,
                    timestamp=timestamp,
                    price=price,
                    stop_price=stop,
                    target_price=target,
                    metadata={
                        "reason": "fast_ma_cross_above_slow_ma",
                        "fast_ma": fast_now,
                        "slow_ma": slow_now,
                        "atr": atr_now,
                    },
                )
            )

        if crossed_down and not has_open_short:
            stop = price + self.stop_atr_multiple * atr_now
            risk_per_unit = stop - price
            target = price - self.target_r_multiple * risk_per_unit

            signals.append(
                Signal(
                    strategy_name=self.name,
                    instrument="",  # filled by runner
                    timeframe=self.timeframe,
                    kind=SignalKind.ENTRY,
                    direction=Direction.SHORT,
                    timestamp=timestamp,
                    price=price,
                    stop_price=stop,
                    target_price=target,
                    metadata={
                        "reason": "fast_ma_cross_below_slow_ma",
                        "fast_ma": fast_now,
                        "slow_ma": slow_now,
                        "atr": atr_now,
                    },
                )
            )

        # --- Exit signals --- #
        # For simplicity: opposite cross => exit all existing positions in that direction
        if crossed_down and has_open_long:
            signals.append(
                Signal(
                    strategy_name=self.name,
                    instrument="",  # filled by runner
                    timeframe=self.timeframe,
                    kind=SignalKind.EXIT,
                    direction=Direction.LONG,
                    timestamp=timestamp,
                    price=price,
                    metadata={
                        "reason": "opposite_cross_exit_long",
                        "fast_ma": fast_now,
                        "slow_ma": slow_now,
                    },
                )
            )

        if crossed_up and has_open_short:
            signals.append(
                Signal(
                    strategy_name=self.name,
                    instrument="",  # filled by runner
                    timeframe=self.timeframe,
                    kind=SignalKind.EXIT,
                    direction=Direction.SHORT,
                    timestamp=timestamp,
                    price=price,
                    metadata={
                        "reason": "opposite_cross_exit_short",
                        "fast_ma": fast_now,
                        "slow_ma": slow_now,
                    },
                )
            )

        return signals


def build_strategy(instruments: List[str]) -> ExampleMACrossStrategy:
    return ExampleMACrossStrategy(instruments=instruments)
