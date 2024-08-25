from typing import Dict, Any, List

def apply_strategy(signals_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Applies the strategy logic to determine the best asset to hold at each time point.

    Parameters:
    - signals_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.

    Returns:
    - signals_dict (Dict[str, Dict[str, Any]]): Updated dictionary with the best asset to hold at each time point.
    """
    asset_scores = [{'BTC': 0, 'ETH': 0, 'GBP': 0} for _ in range(len(signals_dict[next(iter(signals_dict))]['final_signal']))]

    def adjust_scores_based_on_signal(asset_scores: List[Dict[str, int]], ticker: str, signals: Dict[str, Any], time_index: int):
        asset = ticker.split('-')[0]
        buy_strength = signals['total_signals'][time_index] if signals['total_signals'][time_index] > 0 else 0
        sell_strength = signals['total_signals'][time_index] if signals['total_signals'][time_index] < 0 else 0
        asset_scores[time_index][asset] += buy_strength
        asset_scores[time_index]['GBP'] += abs(sell_strength)

    for ticker, data in signals_dict.items():
        if ticker == 'combined_position':
            continue
        for time_index in range(len(data['final_signal'])):
            adjust_scores_based_on_signal(asset_scores, ticker, data, time_index)

    best_assets_to_hold = [max(scores, key=scores.get) for scores in asset_scores]
    signals_dict['combined_position'] = {'final_signal': best_assets_to_hold}

    return signals_dict
