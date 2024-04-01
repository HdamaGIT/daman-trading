import pandas as pd
import numpy as np


def calculate_drawdowns(portfolio_values):
    """
    Calculates the maximum drawdown and average drawdown length from a series of portfolio values.

    Parameters:
    - portfolio_values (list): List of portfolio values.

    Returns:
    - max_drawdown (float): The maximum drawdown as a percentage.
    - average_drawdown_length (int): The average length of drawdowns in terms of the number of trading days.
    """
    # Convert to a pandas Series for convenience
    series = pd.Series(portfolio_values)
    # Calculate cumulative max
    cumulative_max = series.cummax()
    # Calculate drawdown
    drawdowns = (series - cumulative_max) / cumulative_max

    max_drawdown = drawdowns.min() * 100  # Convert to percentage

    # Calculate drawdown durations
    is_in_drawdown = drawdowns < 0
    drawdown_lengths = []
    drawdown_length = 0
    for in_drawdown in is_in_drawdown:
        if in_drawdown:
            drawdown_length += 1
        elif drawdown_length > 0:
            drawdown_lengths.append(drawdown_length)
            drawdown_length = 0
    # Handle ongoing drawdown at the end
    if drawdown_length > 0:
        drawdown_lengths.append(drawdown_length)

    average_drawdown_length = np.mean(drawdown_lengths) if drawdown_lengths else 0

    return round(max_drawdown, 2), round(average_drawdown_length, 2)


def evaluate(strategy_output, risk_free_rate=0.01, transaction_cost_percentage=0.02):
    """
    Appends evaluation metrics of the backtesting results to the strategy_output dictionary,
    with rounded and formatted values for clearer presentation.
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

    daily_returns = pd.Series(portfolio_values).pct_change().dropna()
    excess_daily_returns = daily_returns - (risk_free_rate / 252)
    sharpe_ratio = round(np.sqrt(252) * excess_daily_returns.mean() / excess_daily_returns.std(), 0)

    fees_paid = round(sum(trade['price'] * trade['qty'] * transaction_cost_percentage for trade in trades), 0)

    evaluation_summary = {
        'Number of Trading Days': num_trading_days,
        'Number of Trades': num_trades,
        'Average Trades Per Month': avg_trades_per_month,
        'Start Portfolio Value': f"£{start_portfolio:,.0f}",
        'End Portfolio Value': f"£{end_portfolio:,.0f}",
        'Profit/Loss': f"£{profit_loss:,.0f}",
        'Profit Percentage': f"{profit_percentage}%",
        'Sharpe Ratio': sharpe_ratio,
        'Fees Paid': f"£{fees_paid:,.0f}",
        'Average Hold Duration': "TBD",
        'Max Hold Duration': "TBD",
        'Max Drawdown': "TBD",
        'Average Drawdown Length': "TBD",
    }

    max_drawdown, average_drawdown_length = calculate_drawdowns(portfolio_values)
    evaluation_summary['Max Drawdown'] = f"{max_drawdown}%"
    evaluation_summary['Average Drawdown Length'] = f"{average_drawdown_length} days"

    # Merge hold strategy evaluation
    evaluation_summary.update(
        hold_strategy_evaluation(strategy_output, 'BTC-GBP', start_portfolio, transaction_cost_percentage))
    evaluation_summary.update(
        hold_strategy_evaluation(strategy_output, 'ETH-GBP', start_portfolio, transaction_cost_percentage))

    # Append evaluation summary to strategy_output
    strategy_output['evaluation_summary'] = evaluation_summary

    return strategy_output


def hold_strategy_evaluation(strategy_output, asset_pair, initial_investment, transaction_cost_percentage):
    """
    Formats the hold strategy evaluation with rounded values.
    """
    prices = strategy_output[asset_pair]['Close']
    buy_cost = initial_investment * transaction_cost_percentage
    final_investment = initial_investment - buy_cost
    final_quantity = final_investment / prices[0]
    final_value = final_quantity * prices[-1] - (final_quantity * prices[-1] * transaction_cost_percentage)
    profit_loss = round(final_value - initial_investment, 0)
    profit_percentage = round((profit_loss / initial_investment) * 100, 0)

    return {
        f'{asset_pair} Hold Final Value': f"£{final_value:,.0f}",
        f'{asset_pair} Hold Profit/Loss': f"£{profit_loss:,.0f}",
        f'{asset_pair} Hold Profit Percentage': f"{profit_percentage}%",
    }
