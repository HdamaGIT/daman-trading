def backtest(strategy_output, starting_cash=5000, slippage_percentage=0.05, transaction_cost_percentage=0.02):
    """
    Simulates trading based on the strategy's output, adjusting for slippage and transaction costs as percentages.
    Now ensures no unnecessary buy/sell of the same asset on the same day.
    """

    def get_trade_price(asset, time_point):
        if asset == 'GBP':
            return 1.0  # Placeholder for cash holding
        ticker_pair = f"{asset}-GBP"
        return strategy_output[ticker_pair]['Close'][time_point]

    cash = starting_cash
    positions = {'BTC': 0, 'ETH': 0}  # Tracks quantity of each asset held
    portfolio_value = []
    trades = []

    current_holding = 'GBP'  # Initialize current holding to GBP

    for i, signal in enumerate(strategy_output['combined_position']['final_signal']):
        asset_to_trade = signal

        # Skip if the current holding is the same as the asset to trade
        if asset_to_trade == current_holding or asset_to_trade == 'Hold':
            pass  # No trading action required, continue holding
        else:
            # Sell current holdings
            if current_holding != 'GBP':  # If holding an asset, sell it
                sell_price = get_trade_price(current_holding, i) * (1 - slippage_percentage / 100)
                cash += positions[current_holding] * sell_price - (positions[current_holding] * sell_price * transaction_cost_percentage / 100)
                trades.append({'asset': current_holding, 'action': 'sell', 'qty': positions[current_holding], 'price': sell_price, 'time_point': i})
                positions[current_holding] = 0

            # Buy new asset if not holding cash
            if asset_to_trade != 'GBP':
                trade_price = get_trade_price(asset_to_trade, i)
                adjusted_trade_price = trade_price * (1 + slippage_percentage / 100)
                transaction_cost = cash * transaction_cost_percentage / 100
                quantity_to_buy = (cash - transaction_cost) / adjusted_trade_price
                positions[asset_to_trade] = quantity_to_buy
                trades.append({'asset': asset_to_trade, 'action': 'buy', 'qty': quantity_to_buy, 'price': adjusted_trade_price, 'time_point': i})
                cash = 0  # Allocate all cash to new asset
                current_holding = asset_to_trade  # Update current holding

        # Update portfolio value for this time point
        total_value = cash + sum(qty * get_trade_price(asset, i) for asset, qty in positions.items())
        portfolio_value.append(total_value)

    # Record detailed backtest results in strategy_output
    strategy_output['backtest_details'] = {
        'portfolio_value': portfolio_value,
        'trades': trades,
        'final_positions': positions,
        'final_cash': cash
    }

    return strategy_output
