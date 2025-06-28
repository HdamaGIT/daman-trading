from typing import Dict, Any, List
import pandas as pd

def apply_strategy(signals_dict: Dict[str, pd.DataFrame]) -> Dict[str, pd.DataFrame]:
    """
    Applies the strategy to determine best asset to hold at each time point.
    """
    # Assume all assets share the same index
    example_df = next(iter(signals_dict.values()))
    num_time_points = len(example_df)

    best_assets = []
    current_holding = 'GBP'

    for t in range(num_time_points):
        selected_asset = 'Hold'
        for ticker, df in signals_dict.items():
            asset = ticker.split('-')[0]
            signal = df.iloc[t]['signal']

            if signal > 0 and current_holding != asset:
                selected_asset = asset
                current_holding = asset
            elif signal < 0 and current_holding == asset:
                selected_asset = 'GBP'
                current_holding = 'GBP'

        best_assets.append(selected_asset)

    combined_df = pd.DataFrame({
        'final_signal': best_assets
    }, index=example_df.index)

    signals_dict['combined_position'] = combined_df

    return signals_dict