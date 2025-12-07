from typing import List, Dict

import matplotlib.pyplot as plt
import pandas as pd  # <— make sure this is imported

from system.system_development.engine.data_loader import download_price_data
from system.system_development.engine.metrics import (
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
    verbose: bool = True,
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

    if verbose:
        print(f"\nSignal counts for {symbol}:")
        print(df["Signal"].value_counts(dropna=False))

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

    return BacktestResult(symbol=symbol, equity_curve=equity_series, trades=trades, stats=stats)

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
) -> Dict[str, BacktestResult]:
    """
    Convenience function to run the strategy on the default set of
    indices + FX pairs.

    If portfolio=True, also builds an equal-weight portfolio equity curve
    and prints its statistics first.
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
        )
        results[sym] = result

    # Portfolio view
    if portfolio and results:
        portfolio_result = build_portfolio_result(results, params)
        print_stats(portfolio_result.symbol, portfolio_result.stats)

        if plot:
            plt.figure(figsize=(10, 4))
            plt.plot(portfolio_result.equity_curve)
            plt.title(f"Equity curve - {portfolio_result.symbol}")
            plt.xlabel("Date")
            plt.ylabel("Equity")
            plt.tight_layout()
            plt.show()

    # Then print per-symbol stats
    for sym, res in results.items():
        print_stats(sym, res.stats)

    return results
