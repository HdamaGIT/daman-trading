from .indicators import calculate_indicators
from .signal_generation import all_signals
from .apply_strategy import apply_strategy
import logging
from typing import Dict, Any


def strategy(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main strategy function to calculate indicators, generate signals, and apply the strategy.

    Parameters:
    - data (Dict[str, Any]): Raw price data for each ticker.

    Returns:
    - strategy_apply (Dict[str, Any]): Final signals and strategy application results.
    """
    try:
        logging.info("Calculating indicators...")
        data_with_indicators = calculate_indicators(data)

        logging.info("Generating all signals...")
        final_dict = all_signals(data_with_indicators)

        logging.info("Applying strategy...")
        strategy_apply = apply_strategy(final_dict)

        logging.info("Strategy completed successfully.")
        return strategy_apply
    except Exception as e:
        logging.error(f"Error in strategy execution: {e}")
        raise
