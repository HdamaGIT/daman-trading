from typing import Dict, Any, List

def backtest(strategy_output: Dict[str, Any], starting_cash: float = 5000, 
             slippage_percentage: float = 0.05, transaction_cost_percentage: float = 0.02) -> Dict[str, Any]:
    """
    Simulates trading based on the strategy's output, adjusting for slippage and transaction costs as percentages.
    Now ensures no unnecessary buy/sell of the same asset on the same day.

    Parameters:
    - strategy_output (Dict[str, Any]): Strategy output containing trading signals and price data.
    - starting_cash (float): Initial capital to start with.
    - slippage_percentage (float): Slippage percentage applied to trades.
    - transaction_cost_percentage (float): Transaction cost percentage applied to trades.

    Returns:
    - strategy_output (Dict[str, Any]): Updated with backtest details.
    """

    def get_trade_price(asset: str, time_point: int) -> float:
        if asset == 'GBP':
            return 1.0  # Placeholder for cash holding
        ticker_pair = f"{asset}-GBP"
        return strategy_output[ticker_pair]['Close'][time_point]

    cash = starting_cash
    positions = {'BTC': 0, 'ETH': 0}
    portfolio_value = []
    trades = []
    current_holding = 'GBP'

    for i, signal in enumerate(strategy_output['combined_position']['final_signal']):
        asset_to_trade = signal

        if asset_to_trade == current_holding or asset_to_trade == 'Hold':
            pass  # No trading action required
        else:
            # Sell current holdings
            if current_holding != 'GBP':
                sell_price = get_trade_price(current_holding, i) * (1 - slippage_percentage / 100)
                cash += positions[current_holding] * sell_price * (1 - transaction_cost_percentage / 100)
                trades.append({'asset': current_holding, 'action': 'sell', 'qty': positions[current_holding], 
                               'price': sell_price, 'time_point': i})
                positions[current_holding] = 0

            # Buy new asset
            if asset_to_trade != 'GBP':
                trade_price = get_trade_price(asset_to_trade, i)
                adjusted_trade_price = trade_price * (1 + slippage_percentage / 100)
                transaction_cost = cash * transaction_cost_percentage / 100
                quantity_to_buy = (cash - transaction_cost) / adjusted_trade_price
                positions[asset_to_trade] = quantity_to_buy
                trades.append({'asset': asset_to_trade, 'action': 'buy', 'qty': quantity_to_buy, 
                               'price': adjusted_trade_price, 'time_point': i})
                cash = 0
                current_holding = asset_to_trade

        # Calculate portfolio value at this time point
        total_value = cash + sum(qty * get_trade_price(asset, i) for asset, qty in positions.items())
        portfolio_value.append(total_value)

    strategy_output['backtest_details'] = {
        'portfolio_value': portfolio_value,
        'trades': trades,
        'final_positions': positions,
        'final_cash': cash
    }

    return strategy_output