from typing import List, Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from collections import Counter

from engine.data_loader import download_price_data
from engine.metrics import (
    Trade,
    BacktestResult,
    calculate_stats,
    print_stats,
)
from .config import StrategyParams, DEFAULT_PARAMS, INDEX_SYMBOLS, FX_SYMBOLS
from .rules import prepare_dataframe

LONG_ONLY_SYMBOLS = ["^GSPC", "^NDX", "^FTSE"] #["^GSPC", "^NDX", "^FTSE"]

def backtest_symbol(
    symbol: str,
    params: StrategyParams | None = None,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
    plot: bool = False,
    verbose: bool = True,
    show_benchmark: bool = False,
) -> BacktestResult:
    """
    Run the trend-pullback backtest for a single symbol.

    Supports two exit modes (see params.exit_mode) and,
    if show_benchmark=True, also computes a buy-and-hold equity curve
    for comparison and overlays it on the plot.
    """
    if params is None:
        params = DEFAULT_PARAMS

    # --- Load data and prepare indicators / signals ---
    raw = download_price_data(symbol, start=start, end=end, interval=interval)
    df = prepare_dataframe(raw, params)

    # Drop initial rows with NaNs in indicators
    df = df.dropna(subset=["EMA_Fast", "EMA_Slow", "RSI", "ATR", "ADX"]).copy()

    # Optional long-only mode for certain indices
    if symbol in LONG_ONLY_SYMBOLS:
        df.loc[df["Signal"] < 0, "Signal"] = 0

    # --- Buy & hold benchmark ---
    first_close = float(df["Close"].iloc[0])
    benchmark_curve = params.initial_capital * (df["Close"] / first_close)

    if verbose:
        print(f"\nSignal counts for {symbol}:")
        print(df["Signal"].value_counts(dropna=False))

    # ===== Backtest core =====

    # realised equity only
    equity = params.initial_capital
    equity_curve: list[float] = []
    dates: list[pd.Timestamp] = []

    trades: List[Trade] = []
    position = 0  # 0 flat, 1 long, -1 short
    entry_price = 0.0
    stop_price = 0.0
    tp_price: float | None = None
    size = 0.0
    entry_date: pd.Timestamp | None = None

    for idx, row in df.iterrows():
        dates.append(idx)

        close = float(row["Close"])
        high = float(row["High"])
        low = float(row["Low"])
        adx = float(row["ADX"])
        ema_slow = float(row["EMA_Slow"])
        atr_val = float(row["ATR"])

        if position == 0:
            # ---- FLAT: check for new entry ----
            signal = int(row["Signal"])
            if signal != 0:
                if atr_val <= 0:
                    # nothing we can do with a zero ATR
                    pass
                else:
                    stop_distance = params.stop_atr_mult * atr_val
                    risk_amount = equity * params.risk_per_trade
                    size = risk_amount / stop_distance

                    entry_price = close
                    if signal == 1:
                        stop_price = entry_price - stop_distance
                        if params.exit_mode == "fixed_rr":
                            tp_price = entry_price + params.tp_atr_mult * atr_val
                        else:
                            tp_price = None
                    else:
                        stop_price = entry_price + stop_distance
                        if params.exit_mode == "fixed_rr":
                            tp_price = entry_price - params.tp_atr_mult * atr_val
                        else:
                            tp_price = None

                    position = signal
                    entry_date = idx

        else:
            # ---- IN A TRADE: manage position ----
            exit_price = None
            exit_reason = None

            # Optionally trail the stop in trend_follow mode
            if params.exit_mode == "trend_follow" and params.trail_stops:
                if position == 1:
                    new_stop = close - params.stop_atr_mult * atr_val
                    stop_price = max(stop_price, new_stop)
                else:
                    new_stop = close + params.stop_atr_mult * atr_val
                    stop_price = min(stop_price, new_stop)

            if position == 1:
                # Long trade
                if low <= stop_price:
                    exit_price = stop_price
                    exit_reason = "stop"
                elif params.exit_mode == "fixed_rr" and tp_price is not None and high >= tp_price:
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
                elif params.exit_mode == "fixed_rr" and tp_price is not None and low <= tp_price:
                    exit_price = tp_price
                    exit_reason = "tp"
                elif (adx < params.adx_exit_threshold) or (close > ema_slow):
                    exit_price = close
                    exit_reason = "trend_exit"

            if exit_price is not None:
                pnl = (exit_price - entry_price) * size * position
                equity += pnl  # realised PnL only

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

                # reset position
                position = 0
                entry_price = stop_price = 0.0
                tp_price = None
                size = 0.0
                entry_date = None

        # ---- After handling trade logic: compute equity for this bar ----
        if position == 0:
            unrealised = 0.0
        else:
            unrealised = (close - entry_price) * size * position

        equity_mtm = equity + unrealised

        if params.equity_mode.lower() == "mtm":
            equity_curve.append(equity_mtm)
        else:  # "cash"
            equity_curve.append(equity)

    equity_series = pd.Series(equity_curve, index=dates)
    stats = calculate_stats(equity_series, trades)

    if verbose and trades:
        # Holding time in days for each trade
        holding_days = np.array(
            [
                (t.exit_date - t.entry_date).total_seconds() / 86400.0
                for t in trades
            ]
        )

        avg_all = float(holding_days.mean())
        print(f"\nExit breakdown for {symbol}:")
        print(f"  All trades       : {len(trades):4d} trades, "
              f"avg holding {avg_all:6.2f} days")

        reason_counts = Counter(t.exit_reason for t in trades)
        for reason, count in reason_counts.items():
            reason_durations = holding_days[
                [i for i, t in enumerate(trades) if t.exit_reason == reason]
            ]
            avg_reason = float(reason_durations.mean()) if len(reason_durations) else 0.0
            print(
                f"  {reason:<14s}: {count:4d} trades, "
                f"avg holding {avg_reason:6.2f} days"
            )

    if plot:
        plt.figure(figsize=(10, 4))
        plt.plot(equity_series, label="Strategy")
        if show_benchmark and benchmark_curve is not None:
            bh = benchmark_curve.reindex(equity_series.index).ffill()
            plt.plot(bh, linestyle="--", alpha=0.8, label="Buy & Hold")
        plt.title(f"Equity curve - {symbol}")
        plt.xlabel("Date")
        plt.ylabel("Equity")
        if show_benchmark:
            plt.legend()
        plt.tight_layout()
        plt.show()

    return BacktestResult(
        symbol=symbol,
        equity_curve=equity_series,
        trades=trades,
        stats=stats,
        benchmark_curve=benchmark_curve,
    )


def build_portfolio_result(
    results: Dict[str, BacktestResult],
    params: StrategyParams,
    portfolio_name: str = "PORTFOLIO_EQUAL_WEIGHT",
) -> BacktestResult:
    """
    Combine individual symbol equity curves into a single equal-weight portfolio.

    Method:
      - Align all equity curves on a common date index
      - Forward-fill missing values
      - Normalise each curve to 1.0 at its first value
      - Take the average across symbols → portfolio normalised curve
      - Scale by initial_capital to get portfolio equity
    """
    if not results:
        raise ValueError("No results provided to build_portfolio_result")

    # Build DataFrame of equity curves
    eq_df = pd.DataFrame(
        {sym: res.equity_curve for sym, res in results.items()}
    ).sort_index()

    # Forward-fill gaps
    eq_df = eq_df.ffill().dropna(how="all")

    # Normalise each column to 1 at the start
    eq_norm = eq_df / eq_df.iloc[0]

    # Equal-weight portfolio
    port_norm = eq_norm.mean(axis=1)

    initial_capital = params.initial_capital
    port_equity = port_norm * initial_capital

    # Combine all trades
    all_trades: List[Trade] = []
    for res in results.values():
        all_trades.extend(res.trades)

    stats = calculate_stats(port_equity, all_trades)

    return BacktestResult(
        symbol=portfolio_name,
        equity_curve=port_equity,
        trades=all_trades,
        stats=stats,
    )

def run_backtest_for_default_universe(
    params: StrategyParams | None = None,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
    plot: bool = False,
    portfolio: bool = True,
    show_benchmark: bool = False,
) -> Dict[str, BacktestResult]:
    """
    Run the strategy on the default set of indices + FX pairs.

    If portfolio=True, also builds an equal-weight portfolio equity curve.
    If show_benchmark=True:
      - individual symbol plots include buy-and-hold lines
      - the portfolio plot overlays buy-and-hold curves for each symbol
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
            verbose=True,
            show_benchmark=show_benchmark,
        )
        results[sym] = result

    # Portfolio view
    if portfolio and results:
        portfolio_result = build_portfolio_result(results, params)
        print_stats(portfolio_result.symbol, portfolio_result.stats)

        if plot:
            plt.figure(figsize=(10, 4))
            # main portfolio equity line
            plt.plot(
                portfolio_result.equity_curve,
                label="Strategy Portfolio",
                linewidth=2,
            )

            if show_benchmark:
                # overlay each symbol's buy-and-hold curve
                for sym, res in results.items():
                    if res.benchmark_curve is None:
                        continue
                    bh = res.benchmark_curve.reindex(portfolio_result.equity_curve.index).ffill()
                    plt.plot(
                        bh,
                        linestyle="--",
                        alpha=0.7,
                        label=f"{sym} B&H",
                    )

                plt.legend()

            plt.title(f"Equity curve - {portfolio_result.symbol}")
            plt.xlabel("Date")
            plt.ylabel("Equity")
            plt.tight_layout()
            plt.show()

    # Then print per-symbol stats
    for sym, res in results.items():
        print_stats(sym, res.stats)

    return results