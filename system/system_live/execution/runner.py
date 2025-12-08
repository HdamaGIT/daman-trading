# system_live/execution/runner.py

from __future__ import annotations

from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from ..config import SystemConfig
from ..data.data_provider import get_market_data_provider
from ..discord_integration import notifier
from ..storage.db import TradingDatabase
from ..strategies import load_strategy
from .risk import RiskManager
from .trade_types import Signal, SignalKind, Direction


def group_open_trades_by_instrument(open_trades: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = defaultdict(list)
    for t in open_trades:
        grouped[t["instrument"]].append(t)
    return grouped


def run_once(config: SystemConfig) -> None:
    """
    Run a single live cycle:
    - For each instrument:
        - Fetch data
        - Compute indicators
        - Generate signals
        - For entry signals: size trade, persist, notify
        - For exit signals: persist, notify (no auto-close yet)
    """

    db = TradingDatabase(config.db_path)
    risk_manager = RiskManager(config=config)
    provider = get_market_data_provider(config.data_provider)

    # Build strategy instance with list of symbols
    instruments = [i.symbol for i in config.instruments]
    strategy = load_strategy(config.strategy.strategy_name, instruments=instruments)
    lookback = strategy.get_required_lookback()

    now = datetime.utcnow()

    # Get open trades grouped by instrument
    open_trades = db.get_open_trades(strategy_name=strategy.name)
    open_trades_by_instrument = group_open_trades_by_instrument(open_trades)

    for inst_cfg in config.instruments:
        symbol = inst_cfg.symbol

        # Fetch OHLCV
        df = provider.get_ohlcv(
            symbol=symbol,
            timeframe=config.strategy.timeframe,
            lookback=lookback,
            now=now,
        )
        if df is None or df.empty:
            print(f"[WARN] No data returned for {symbol}")
            continue

        # Compute indicators
        df_ind = strategy.compute_indicators(df)

        # Generate signals for this instrument
        open_for_inst = open_trades_by_instrument.get(symbol, [])
        signals: List[Signal] = strategy.generate_signals(df_ind, open_for_inst)

        # Fill in instrument field and execute logic
        for sig in signals:
            sig.instrument = symbol

            # Persist signal
            sig_id = db.insert_signal(sig)
            sig.id = sig_id

            if sig.kind == SignalKind.ENTRY:
                trade = risk_manager.build_proposed_trade(sig)
                if trade is None:
                    print(f"[INFO] Skipping trade build for signal {sig_id}: no valid stop/target or size.")
                    continue

                trade.signal_id = sig_id
                trade_id = db.insert_trade(trade)
                trade.id = trade_id
                db.link_signal_to_trade(sig_id, trade_id)

                # Notify via placeholder
                notifier.notify_new_entry_signal(sig, trade)

            elif sig.kind == SignalKind.EXIT:
                # For now, just notify about exit proposals.
                affected_ids = [
                    t["id"]
                    for t in open_for_inst
                    if (sig.direction is None or t["direction"] == sig.direction.value)
                ]
                notifier.notify_exit_signal(sig, affected_ids)

    db.close()
