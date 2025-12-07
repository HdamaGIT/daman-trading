from dataclasses import dataclass
from typing import List, Dict

import numpy as np
import pandas as pd


@dataclass
class Trade:
    symbol: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    direction: int  # 1 = long, -1 = short
    entry_price: float
    exit_price: float
    size: float
    pnl: float
    return_pct: float
    exit_reason: str


@dataclass
class BacktestResult:
    symbol: str
    equity_curve: pd.Series
    trades: List[Trade]
    stats: Dict[str, float]


def calculate_stats(equity_curve: pd.Series, trades: List[Trade]) -> dict:
    if equity_curve.empty:
        return {}

    start_equity = float(equity_curve.iloc[0])
    end_equity = float(equity_curve.iloc[-1])
    total_return = (end_equity / start_equity) - 1.0

    # Max drawdown
    running_max = equity_curve.cummax()
    drawdown = (equity_curve - running_max) / running_max
    max_dd = float(drawdown.min())

    # Trade-based stats
    pnls = np.array([t.pnl for t in trades]) if trades else np.array([])
    wins = pnls[pnls > 0]
    losses = pnls[pnls < 0]

    num_trades = len(pnls)
    win_rate = float(len(wins) / num_trades) if num_trades > 0 else 0.0
    avg_win = float(wins.mean()) if wins.size > 0 else 0.0
    avg_loss = float(losses.mean()) if losses.size > 0 else 0.0
    gross_profit = float(wins.sum()) if wins.size > 0 else 0.0
    gross_loss = float(losses.sum()) if losses.size > 0 else 0.0
    profit_factor = (
        gross_profit / abs(gross_loss) if gross_loss != 0 else float("inf")
    )

    stats = {
        "start_equity": start_equity,
        "end_equity": end_equity,
        "total_return_pct": total_return * 100,
        "max_drawdown_pct": max_dd * 100,
        "num_trades": num_trades,
        "win_rate_pct": win_rate * 100,
        "avg_win": avg_win,
        "avg_loss": avg_loss,
        "profit_factor": profit_factor,
    }
    return stats


def print_stats(symbol: str, stats: dict) -> None:
    print(f"\n=== Backtest statistics for {symbol} ===")
    for k, v in stats.items():
        if "pct" in k:
            print(f"{k:20s}: {v:8.2f}%")
        else:
            print(f"{k:20s}: {v:8.2f}")
