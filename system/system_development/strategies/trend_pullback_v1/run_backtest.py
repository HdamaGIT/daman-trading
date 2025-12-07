from typing import List, Dict

import matplotlib.pyplot as plt
import pandas as pd

from system_development.engine.data_loader import download_price_data
from system_development.engine.metrics import (
    Trade,
    BacktestResult,
    calculate_stats,
    print_stats,
)
from .config import StrategyParams, DEFAULT_PARAMS, INDEX_SYMBOLS, FX_SYMBOLS
from .rules import prepare_dataframe


def backtest_symbol(
    symbol: str,
    params: StrategyParams | None = None,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
    plot: bool = False,
) -> BacktestResult:
    """
    Run the trend-pullback backtest for a single symbol.
    """
    if params is None:
        params = DEFAULT_PARAMS

    raw = download_price_data(symbol, start=start, end=end, interval=interval)
    df = prepare_dataframe(raw, params)

    # Drop initial rows with NaNs in indicators
    df = df.dropna(subset=["EMA_Fast", "EMA_Slow", "RSI", "ATR", "ADX"]).copy()

    equity = params.initial_capital
    equity_curve = []
    dates = []

    trades: List[Trade] = []
    position = 0  # 0 flat, 1 long, -1 short
    entry_price = 0.0
    stop_price = 0.0
    tp_price = 0.0
    size = 0.0
    entry_date: pd.Timestamp | None = None

    for idx, row in df.iterrows():
        dates.append(idx)

        if position == 0:
            signal = int(row["Signal"])
            if signal != 0:
                # Open new position
                atr_val = float(row["ATR"])
                if atr_val <= 0:
                    equity_curve.append(equity)
                    continue

                stop_distance = params.stop_atr_mult * atr_val
                risk_amount = equity * params.risk_per_trade
                size = risk_amount / stop_distance

                entry_price = float(row["Close"])
                if signal == 1:
                    stop_price = entry_price - stop_distance
                    tp_price = entry_price + params.tp_atr_mult * atr_val
                else:
                    stop_price = entry_price + stop_distance
                    tp_price = entry_price - params.tp_atr_mult * atr_val

                position = signal
                entry_date = idx

                equity_curve.append(equity)
            else:
                equity_curve.append(equity)

        else:
            # Manage open position
            exit_price = None
            exit_reason = None

            high = float(row["High"])
            low = float(row["Low"])
            close = float(row["Close"])
            adx = float(row["ADX"])
            ema_slow = float(row["EMA_Slow"])

            if position == 1:
                # Long trade
                # Check stop first, then TP (conservative assumption)
                if low <= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop"
                elif high >= tp_price:
                    exit_price = tp_price
                    exit_reason = "tp"
                elif (adx < params.adx_exit_threshold) or (close < ema_slow):
                    exit_price = close
                    exit_reason = "trend_exit"
            else:
                # Short trade
                if high >= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop"
                elif low <= tp_price:
                    exit_price = tp_price
                    exit_reason = "tp"
                elif (adx < params.adx_exit_threshold) or (close > ema_slow):
                    exit_price = close
                    exit_reason = "trend_exit"

            if exit_price is not None:
                pnl = (exit_price - entry_price) * size * position
                equity += pnl

                trades.append(
                    Trade(
                        symbol=symbol,
                        entry_date=entry_date,
                        exit_date=idx,
                        direction=position,
                        entry_price=entry_price,
                        exit_price=exit_price,
                        size=size,
                        pnl=pnl,
                        return_pct=pnl / equity if equity != 0 else 0.0,
                        exit_reason=exit_reason,
                    )
                )

                position = 0
                entry_price = stop_price = tp_price = size = 0.0
                entry_date = None

                equity_curve.append(equity)
            else:
                equity_curve.append(equity)

    equity_series = pd.Series(equity_curve, index=dates)
    stats = calculate_stats(equity_series, trades)

    if plot:
        plt.figure(figsize=(10, 4))
        plt.plot(equity_series)
        plt.title(f"Equity curve - {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Equity")
        plt.tight_layout()
        plt.show()

    print_stats(symbol, stats)

    return BacktestResult(symbol=symbol, equity_curve=equity_series, trades=trades, stats=stats)


def run_backtest_for_default_universe(
    params: StrategyParams | None = None,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
    plot: bool = False,
) -> Dict[str, BacktestResult]:
    """
    Convenience function to run the strategy on the default set of
    indices + FX pairs.
    """
    if params is None:
        params = DEFAULT_PARAMS

    symbols = INDEX_SYMBOLS + FX_SYMBOLS
    results: Dict[str, BacktestResult] = {}

    for sym in symbols:
        print(f"\n=== Running backtest for {sym} ===")
        result = backtest_symbol(
            symbol=sym,
            params=params,
            start=start,
            end=end,
            interval=interval,
            plot=plot,
        )
        results[sym] = result

    return results


if __name__ == "__main__":
    # Example: run from daman-trading/system with
    #   python -m system_development.strategies.trend_pullback_v1.run_backtest
    run_backtest_for_default_universe(
        start="2015-01-01",
        end=None,
        interval="4H",
        plot=False,
    )
