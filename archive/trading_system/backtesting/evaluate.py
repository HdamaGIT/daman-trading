import pandas as pd
import numpy as np
from typing import Dict, Any, List


def evaluate(strategy_output: Dict[str, Any], risk_free_rate: float = 0.01,
             transaction_cost_percentage: float = 0.0) -> Dict[str, Any]:
    """
    Evaluates the performance of the backtesting by calculating key metrics such as Sharpe ratio,
    profit/loss, drawdowns, win rate, profit factor, Sortino ratio, and volatility.

    Parameters:
    - strategy_output (Dict[str, Any]): The strategy output including backtest details.
    - risk_free_rate (float): The risk-free rate used for Sharpe ratio calculation.
    - transaction_cost_percentage (float): The decimal percentage (e.g., 0.012 for 1.2%) used to calculate transaction costs.

    Returns:
    - strategy_output (Dict[str, Any]): Updated with evaluation metrics.
    """
    details = strategy_output['backtest_details']
    portfolio_values = details['portfolio_value']
    trades = details['trades']
    start_portfolio = portfolio_values[0]
    end_portfolio = portfolio_values[-1]

    num_trading_days = len(portfolio_values)
    num_trades = len(trades)
    avg_trades_per_month = round(num_trades / (num_trading_days / 30), 0)
    profit_loss = round(end_portfolio - start_portfolio, 0)
    profit_percentage = round((profit_loss / start_portfolio) * 100, 0)

    # Daily Returns and Sharpe Ratio
    daily_returns = pd.Series(portfolio_values).pct_change().dropna()
    excess_daily_returns = daily_returns - (risk_free_rate / 252)
    sharpe_ratio = round(np.sqrt(252) * excess_daily_returns.mean() / excess_daily_returns.std(), 2)

    # Volatility (Standard Deviation of Daily Returns)
    volatility = round(daily_returns.std() * np.sqrt(252) * 100, 2)  # Annualized volatility as a percentage

    # Calculate the total fees paid during the backtest
    fees_paid = round(sum(trade['price'] * trade['qty'] * transaction_cost_percentage for trade in trades), 2)

    # Calculate Win Rate and Profit Factor
    winning_trades = [trade for trade in trades if (trade['action'] == 'sell' and trade['price'] > trade.get('buy_price', 0))]
    losing_trades = [trade for trade in trades if (trade['action'] == 'sell' and trade['price'] <= trade.get('buy_price', 0))]
    win_rate = round(len(winning_trades) / num_trades * 100, 2) if num_trades > 0 else 0

    total_profit = sum(trade['qty'] * (trade['price'] - trade.get('buy_price', 0)) for trade in winning_trades)
    total_loss = sum(trade['qty'] * (trade.get('buy_price', 0) - trade['price']) for trade in losing_trades)
    profit_factor = round(total_profit / total_loss, 2) if total_loss > 0 else float('inf')

    # Sortino Ratio (Using only negative returns for downside deviation)
    downside_returns = daily_returns[daily_returns < 0]
    downside_std = downside_returns.std()
    sortino_ratio = round(np.sqrt(252) * excess_daily_returns.mean() / downside_std, 2) if downside_std != 0 else float('inf')

    # Calculate Maximum Drawdown and Average Drawdown Length
    max_drawdown, average_drawdown_length = calculate_drawdowns(portfolio_values)

    # Compile the evaluation summary
    evaluation_summary = {
        'Number of Trading Days': num_trading_days,
        'Number of Trades': num_trades,
        'Average Trades Per Month': avg_trades_per_month,
        'Start Portfolio Value': f"£{start_portfolio:,.0f}",
        'End Portfolio Value': f"£{end_portfolio:,.0f}",
        'Profit/Loss': f"£{profit_loss:,.0f}",
        'Profit Percentage': f"{profit_percentage}%",
        'Sharpe Ratio': sharpe_ratio,
        'Sortino Ratio': sortino_ratio,
        'Volatility': f"{volatility}%",
        'Max Drawdown': f"{max_drawdown}%",
        'Average Drawdown Length': f"{average_drawdown_length} days",
        'Fees Paid': f"£{fees_paid:,.2f}",
        'Win Rate': f"{win_rate}%",
        'Profit Factor': profit_factor,
    }

    # Add evaluation of holding strategies (BTC and ETH hold strategies)
    evaluation_summary.update(hold_strategy_evaluation(strategy_output, 'BTC-GBP', start_portfolio, transaction_cost_percentage))
    evaluation_summary.update(hold_strategy_evaluation(strategy_output, 'ETH-GBP', start_portfolio, transaction_cost_percentage))

    # Update strategy output with the evaluation summary
    strategy_output['evaluation_summary'] = evaluation_summary

    return strategy_output


def calculate_drawdowns(portfolio_values: List[float]) -> (float, float):
    """
    Calculates the maximum drawdown and the average drawdown length from portfolio values.

    Parameters:
    - portfolio_values (List[float]): List of portfolio values over time.

    Returns:
    - max_drawdown (float): Maximum drawdown percentage.
    - average_drawdown_length (float): Average duration of drawdowns in days.
    """
    series = pd.Series(portfolio_values)
    cumulative_max = series.cummax()
    drawdowns = (series - cumulative_max) / cumulative_max

    max_drawdown = drawdowns.min() * 100

    is_in_drawdown = drawdowns < 0
    drawdown_lengths = is_in_drawdown.astype(int).groupby((is_in_drawdown != is_in_drawdown.shift()).cumsum()).sum()
    average_drawdown_length = drawdown_lengths.mean()

    return round(max_drawdown, 2), round(average_drawdown_length, 2)


def hold_strategy_evaluation(strategy_output: Dict[str, Any], asset_pair: str,
                             initial_investment: float, transaction_cost_percentage: float) -> Dict[str, str]:
    """
    Evaluates the hold strategy for a specific asset.

    Parameters:
    - strategy_output (Dict[str, Any]): The strategy output including price data.
    - asset_pair (str): The asset pair being evaluated.
    - initial_investment (float): The amount initially invested.
    - transaction_cost_percentage (float): The transaction cost as a percentage.

    Returns:
    - evaluation (Dict[str, str]): Evaluation results for the hold strategy.
    """
    prices = strategy_output[asset_pair]['Close']
    buy_cost = initial_investment * transaction_cost_percentage
    final_investment = initial_investment - buy_cost
    final_quantity = final_investment / prices[0]
    final_value = final_quantity * prices[-1] * (1 - transaction_cost_percentage)
    profit_loss = round(final_value - initial_investment, 0)
    profit_percentage = round((profit_loss / initial_investment) * 100, 0)

    return {
        f'{asset_pair} Hold Final Value': f"£{final_value:,.0f}",
        f'{asset_pair} Hold Profit/Loss': f"£{profit_loss:,.0f}",
        f'{asset_pair} Hold Profit Percentage': f"{profit_percentage}%",
    }
