from .indicators import calculate_indicators
from .signal_generation import all_signals
from .apply_strategy import apply_strategy
import logging
import pandas as pd
from typing import Dict, Any, Optional
import time

class StrategyError(Exception):
    pass

def strategy(
    data: Dict[str, pd.DataFrame],
    strategy_params: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Main strategy function.
    """
    try:
        if not data:
            logging.error("Input data dictionary is empty. Aborting strategy.")
            raise StrategyError("No input data provided for strategy.")

        t0 = time.time()
        logging.info("Calculating indicators...")
        data_with_indicators = calculate_indicators(data)
        logging.info(f"Complete: indicators in {time.time() - t0:.2f}s")

        t1 = time.time()
        logging.info("Generating signals...")
        signals_dict = all_signals(data_with_indicators, signal_params=strategy_params)
        logging.info(f"Signals generated for {len(signals_dict)} assets in {time.time() - t1:.2f}s")

        if not signals_dict:
            logging.error("No signals generated for any assets. Aborting strategy.")
            raise StrategyError("Signal generation failed for all assets.")

        t2 = time.time()
        logging.info("Applying strategy...")
        strategy_apply = apply_strategy(signals_dict)
        logging.info(f"Complete: strategy in {time.time() - t2:.2f}s")

        total_time = time.time() - t0
        logging.info(f"Strategy completed successfully in {total_time:.2f}s.")

        return {
            "strategy_output": strategy_apply,
            "signals": signals_dict,
            "indicator_data": data_with_indicators,
            "execution_time_sec": total_time
        }

    except Exception as e:
        logging.error(f"Error in strategy execution: {e}")
        raise StrategyError from e