from .backtest import backtest
from .evaluate import evaluate
from typing import Dict, Any


def backtesting(strategy_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Conducts backtesting and evaluation of the strategy output.

    Parameters:
    - strategy_output (Dict[str, Any]): The output from the strategy including signals and price data.

    Returns:
    - evaluate_output (Dict[str, Any]): Evaluation summary and backtest details.
    """
    # Backtest the strategy output to simulate trading and generate performance data
    backtest_output = backtest(strategy_output)

    # Evaluate the backtest results to calculate performance metrics
    evaluate_output = evaluate(backtest_output)

    return evaluate_output
