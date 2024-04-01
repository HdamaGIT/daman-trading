from .backtest import backtest
from .evaluate import evaluate


def backtesting(strategy_output):
    # Backtest the strategy output to simulate trading and generate performance data
    backtest_output = backtest(strategy_output)

    # Evaluate the backtest results to calculate performance metrics
    evaluate_output = evaluate(backtest_output)

    return evaluate_output
