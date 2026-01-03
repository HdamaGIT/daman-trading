# system_live/execution/risk.py

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .trade_types import ProposedTrade, Signal, Direction
from ..config import SystemConfig


@dataclass
class RiskManager:
    """
    Simple risk manager:
    - risks a fixed % of allocated capital per trade
    - uses signal.entry_price & signal.stop_price to size the position
    """

    config: SystemConfig

    def allocate_capital(self) -> float:
        """Capital allocated to this strategy instance."""
        return self.config.strategy.capital * self.config.strategy.capital_allocation

    def calculate_position_size(
        self,
        entry_price: float,
        stop_price: float,
        instrument_symbol: str,
    ) -> (float, float):
        """
        Returns (size, risk_amount).
        For spread betting:
            risk_amount = capital * risk_per_trade
            stop_distance_points = abs(entry - stop)
            size (£/point) = risk_amount / stop_distance_points
        """
        allocated_capital = self.allocate_capital()
        risk_per_trade = self.config.strategy.risk_per_trade
        risk_amount = allocated_capital * risk_per_trade

        inst_cfg = self.config.get_instrument_config(instrument_symbol)
        point_value = inst_cfg.point_value if inst_cfg else 1.0

        stop_distance_points = abs(entry_price - stop_price)
        if stop_distance_points <= 0:
            return 0.0, 0.0

        effective_stop_distance = stop_distance_points * point_value
        size = risk_amount / effective_stop_distance

        return size, risk_amount

    def build_proposed_trade(
        self,
        signal: Signal,
    ) -> Optional[ProposedTrade]:
        if signal.kind != "entry":
            raise ValueError("build_proposed_trade should be called only for ENTRY signals")

        if signal.stop_price is None or signal.target_price is None:
            # In v1, require stop & target to be set by strategy
            return None

        size, risk_amount = self.calculate_position_size(
            entry_price=signal.price,
            stop_price=signal.stop_price,
            instrument_symbol=signal.instrument,
        )
        if size <= 0:
            return None

        direction = signal.direction
        if direction is None:
            return None

        trade = ProposedTrade(
            strategy_name=signal.strategy_name,
            instrument=signal.instrument,
            direction=direction,
            entry_price=signal.price,
            stop_price=signal.stop_price,
            target_price=signal.target_price,
            size=size,
            risk_amount=risk_amount,
            open_time=signal.timestamp,
            signal_id=signal.id,
        )
        return trade
