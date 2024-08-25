from typing import Dict, Any, List


def apply_strategy(signals_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Applies the strategy logic to determine the best asset to hold at each time point.

    Parameters:
    - signals_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.

    Returns:
    - signals_dict (Dict[str, Dict[str, Any]]): Updated dictionary with the best asset to hold at each time point.
    """
    # Initialize asset scores for each time point
    asset_scores = [{'BTC': 0, 'ETH': 0, 'GBP': 0} for _ in
                    range(len(signals_dict[next(iter(signals_dict))]['final_signal']))]

    def adjust_scores_based_on_signal(asset_scores: List[Dict[str, int]], ticker: str, signals: Dict[str, Any],
                                      time_index: int):
        asset = ticker.split('-')[0]
        signal_strength = signals['total_signals'][time_index]

        if signal_strength > 0:  # Buy signal
            asset_scores[time_index][asset] += signal_strength
        elif signal_strength < 0:  # Sell signal
            asset_scores[time_index]['GBP'] += abs(signal_strength)

    # Iterate over each ticker and adjust scores based on the signals
    for ticker, data in signals_dict.items():
        if ticker == 'combined_position':  # Skip any already combined data
            continue
        for time_index in range(len(data['final_signal'])):
            adjust_scores_based_on_signal(asset_scores, ticker, data, time_index)

    # Determine the best asset to hold at each time point based on the highest score
    best_assets_to_hold = [max(scores, key=scores.get) for scores in asset_scores]
    signals_dict['combined_position'] = {'final_signal': best_assets_to_hold}

    return signals_dict
