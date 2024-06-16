def apply_strategy(signals_dict):
    """
    Modifies signals_dict in place by adding an entry for the best asset to hold at each time point,
    taking into account the strength of buy and sell signals.
    """
    asset_scores = [{'BTC': 0, 'ETH': 0, 'GBP': 0} for _ in
                    range(len(signals_dict[next(iter(signals_dict))]['final_signal']))]

    # Example adjustment: Scoring now takes into account the strength of the signal
    def adjust_scores_based_on_signal(asset_scores, ticker, signals, time_index):
        asset = ticker.split('-')[0]
        buy_strength = signals['total_signals'][time_index] if signals['total_signals'][time_index] > 0 else 0
        sell_strength = signals['total_signals'][time_index] if signals['total_signals'][time_index] < 0 else 0

        # Adjust scores based on signal strength
        asset_scores[time_index][asset] += buy_strength  # Positive score for buy signals
        asset_scores[time_index]['GBP'] += abs(sell_strength)  # Increase GBP score for sell signals

    for ticker, data in signals_dict.items():
        if ticker == 'combined_position':  # Skip combined_position to avoid overwriting
            continue
        for time_index in range(len(data['final_signal'])):
            adjust_scores_based_on_signal(asset_scores, ticker, data, time_index)

    # Determine the best asset to hold based on scores
    best_assets_to_hold = [max(scores, key=scores.get) for scores in asset_scores]

    # Update the signals_dict with the best asset to hold decisions
    signals_dict['combined_position'] = {'final_signal': best_assets_to_hold}

    return signals_dict

