# system_live/discord_integration/notifier.py

from __future__ import annotations

from typing import List

from ..execution.trade_types import ProposedTrade, Signal


def notify_new_entry_signal(signal: Signal, trade: ProposedTrade) -> None:
    """
    Placeholder for Discord notification when a new ENTRY signal + proposed trade is created.
    For now we just print to stdout.
    """
    print(
        "[DISCORD PLACEHOLDER] ENTRY:"
        f" {signal.strategy_name} {signal.instrument} {signal.direction}"
        f" price={signal.price:.2f} size={trade.size:.4f} risk={trade.risk_amount:.2f}"
        f" stop={trade.stop_price:.2f} target={trade.target_price:.2f}"
    )


def notify_exit_signal(signal: Signal, affected_trade_ids: List[int]) -> None:
    """
    Placeholder for Discord notification when an EXIT signal is generated.
    """
    print(
        "[DISCORD PLACEHOLDER] EXIT:"
        f" {signal.strategy_name} {signal.instrument} {signal.direction}"
        f" price={signal.price:.2f} trades={affected_trade_ids}"
    )
