# system_live/execution/trade_types.py

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional


class SignalKind(str, Enum):
    ENTRY = "entry"
    EXIT = "exit"


class Direction(str, Enum):
    LONG = "long"
    SHORT = "short"


@dataclass
class Signal:
    """
    Strategy signal (entry or exit), before risk sizing and execution.
    """
    strategy_name: str
    instrument: str
    timeframe: str
    kind: SignalKind
    timestamp: datetime
    price: float
    direction: Optional[Direction] = None
    stop_price: Optional[float] = None
    target_price: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: Optional[int] = None
    linked_trade_id: Optional[int] = None


@dataclass
class ProposedTrade:
    """
    Trade proposal based on a signal + risk management.
    """
    strategy_name: str
    instrument: str
    direction: Direction
    entry_price: float
    stop_price: float
    target_price: float
    size: float
    risk_amount: float
    open_time: datetime
    signal_id: Optional[int] = None
    id: Optional[int] = None
