from .indicators import calculate_indicators
from .signal_generation import all_signals
from .apply_strategy import apply_strategy


def strategy(data):
    data_with_indicators = calculate_indicators(data)

    final_dict = all_signals(data_with_indicators)

    strategy_apply = apply_strategy(final_dict)

    return strategy_apply
