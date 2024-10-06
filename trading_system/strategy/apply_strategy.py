from typing import Dict, Any, List


def apply_strategy(signals_dict: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    """
    Applies the strategy logic to determine the best asset to hold at each time point.

    Parameters:
    - signals_dict (Dict[str, Dict[str, Any]]): Dictionary with generated signals for each ticker.

    Returns:
    - signals_dict (Dict[str, Dict[str, Any]]): Updated dictionary with the best asset to hold at each time point.
    """
    num_time_points = len(signals_dict[next(iter(signals_dict))]['signal'])
    best_assets_to_hold = []
    current_holding = 'GBP'  # Start with cash

    # Iterate over each time point
    for time_index in range(num_time_points):
        selected_asset = 'Hold'  # Default action if no change in holding
        for ticker, data in signals_dict.items():
            if ticker == 'combined_position':  # Skip any already combined data
                continue

            asset = ticker.split('-')[0]  # Extract asset name (e.g., 'BTC' from 'BTC-GBP')
            signal = data['signal'][time_index]

            # Buy signal takes precedence over hold or sell signals
            if signal > 0 and current_holding != asset:
                selected_asset = asset
                current_holding = asset
            # Sell signal if we're holding this asset
            elif signal < 0 and current_holding == asset:
                selected_asset = 'GBP'
                current_holding = 'GBP'

        best_assets_to_hold.append(selected_asset)

    # Add combined position to the signals dictionary
    signals_dict['combined_position'] = {'final_signal': best_assets_to_hold}

    return signals_dict
