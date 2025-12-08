# system_live/storage/db.py

from __future__ import annotations

import json
import sqlite3
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..execution.trade_types import Signal, ProposedTrade, Direction, SignalKind


class TradingDatabase:
    """
    Simple SQLite-based persistence for signals and trades.
    """

    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self.ensure_schema()

    def close(self):
        self._conn.close()

    # --- Schema --- #

    def ensure_schema(self):
        cur = self._conn.cursor()

        # Signals table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                strategy_name TEXT NOT NULL,
                instrument TEXT NOT NULL,
                timeframe TEXT NOT NULL,
                kind TEXT NOT NULL,
                direction TEXT,
                timestamp TEXT NOT NULL,
                price REAL NOT NULL,
                stop_price REAL,
                target_price REAL,
                metadata TEXT,
                linked_trade_id INTEGER
            )
            """
        )

        # Trades table
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                signal_id INTEGER,
                strategy_name TEXT NOT NULL,
                instrument TEXT NOT NULL,
                direction TEXT NOT NULL,
                entry_price REAL NOT NULL,
                stop_price REAL NOT NULL,
                target_price REAL NOT NULL,
                size REAL NOT NULL,
                risk_amount REAL NOT NULL,
                open_time TEXT NOT NULL,
                close_time TEXT,
                status TEXT NOT NULL,
                realised_pnl REAL
            )
            """
        )

        self._conn.commit()

    # --- Insert helpers --- #

    def insert_signal(self, signal: Signal) -> int:
        cur = self._conn.cursor()
        metadata_json = json.dumps(signal.metadata or {})

        cur.execute(
            """
            INSERT INTO signals (
                strategy_name, instrument, timeframe, kind, direction, timestamp,
                price, stop_price, target_price, metadata, linked_trade_id
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                signal.strategy_name,
                signal.instrument,
                signal.timeframe,
                signal.kind.value,
                signal.direction.value if signal.direction else None,
                signal.timestamp.isoformat(),
                signal.price,
                signal.stop_price,
                signal.target_price,
                metadata_json,
                signal.linked_trade_id,
            ),
        )
        self._conn.commit()
        signal_id = cur.lastrowid
        return signal_id

    def insert_trade(self, trade: ProposedTrade) -> int:
        cur = self._conn.cursor()

        cur.execute(
            """
            INSERT INTO trades (
                signal_id, strategy_name, instrument, direction,
                entry_price, stop_price, target_price, size, risk_amount,
                open_time, close_time, status, realised_pnl
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                trade.signal_id,
                trade.strategy_name,
                trade.instrument,
                trade.direction.value,
                trade.entry_price,
                trade.stop_price,
                trade.target_price,
                trade.size,
                trade.risk_amount,
                trade.open_time.isoformat(),
                None,
                "open",
                None,
            ),
        )
        self._conn.commit()
        trade_id = cur.lastrowid
        return trade_id

    def link_signal_to_trade(self, signal_id: int, trade_id: int):
        cur = self._conn.cursor()
        cur.execute(
            "UPDATE signals SET linked_trade_id = ? WHERE id = ?",
            (trade_id, signal_id),
        )
        self._conn.commit()

    # --- Query helpers --- #

    def get_open_trades(self, strategy_name: Optional[str] = None) -> List[Dict[str, Any]]:
        cur = self._conn.cursor()
        if strategy_name:
            cur.execute(
                """
                SELECT * FROM trades
                WHERE status = 'open' AND strategy_name = ?
                """,
                (strategy_name,),
            )
        else:
            cur.execute(
                "SELECT * FROM trades WHERE status = 'open'"
            )

        rows = cur.fetchall()
        return [dict(row) for row in rows]

    def close_trade(
        self,
        trade_id: int,
        close_time: datetime,
        realised_pnl: Optional[float] = None,
    ):
        cur = self._conn.cursor()
        cur.execute(
            """
            UPDATE trades
            SET status = 'closed',
                close_time = ?,
                realised_pnl = ?
            WHERE id = ?
            """,
            (close_time.isoformat(), realised_pnl, trade_id),
        )
        self._conn.commit()
