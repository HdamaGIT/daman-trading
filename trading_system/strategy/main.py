from .indicators import calculate_indicators
from .signal_generation import all_signals
from .apply_strategy import apply_strategy
import logging
import pandas as pd
from typing import Dict, Any


def strategy(data: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Main strategy function.
    """
    try:
        logging.info("Calculating indicators...")
        data_with_indicators = calculate_indicators(data)
        logging.info("Complete: indicators...")

        logging.info("Generating signals...")
        signals_dict = all_signals(data_with_indicators)
        if signals_dict:
            logging.info(f"Signals generated for {len(signals_dict)} assets.")
        else:
            logging.error("No signals generated for any assets. Aborting strategy.")
            raise RuntimeError("Signal generation failed for all assets.")

        logging.info("Applying strategy...")
        strategy_apply = apply_strategy(signals_dict)
        logging.info("Complete: strategy...")

        logging.info("Strategy completed successfully.")
        return strategy_apply

    except Exception as e:
        logging.error(f"Error in strategy execution: {e}")
        raise
