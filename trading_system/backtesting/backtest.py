from typing import Dict, Any


def backtest(strategy_output: Dict[str, Any], starting_cash: float = 1000,
             slippage_percentage: float = 0.005, transaction_cost_percentage: float = 0.00) -> Dict[str, Any]:
    """
    Simulates trading based on the strategy's output, adjusting for slippage and transaction costs as decimals.
    Now ensures no unnecessary buy/sell of the same asset on the same day.

    Parameters:
    - strategy_output (Dict[str, Any]): Strategy output containing trading signals and price data.
    - starting_cash (float): Initial capital to start with.
    - slippage_percentage (float): Slippage applied to trades as a decimal (e.g., 0.005 for 0.5%).
    - transaction_cost_percentage (float): Transaction cost applied to trades as a decimal (e.g., 0.012 for 1.2%).

    Returns:
    - strategy_output (Dict[str, Any]): Updated with backtest details.
    """

    def get_trade_price(asset: str, time_point: int) -> float:
        if asset == 'GBP':
            return 1.0  # Placeholder for cash holding
        ticker_pair = f"{asset}-GBP"
        return strategy_output[ticker_pair]['Close'][time_point]

    # Initial setup
    cash = starting_cash
    positions = {'BTC': 0, 'ETH': 0}
    portfolio_value = []
    trades = []
    current_holding = 'GBP'

    # Loop through the strategy signals to simulate trading
    for i, signal in enumerate(strategy_output['combined_position']['final_signal']):
        asset_to_trade = signal

        # If the signal is 'Hold' or matches current holding, do nothing
        if asset_to_trade == 'Hold' or asset_to_trade == current_holding:
            pass  # No trading action required
        else:
            # If there's an asset to sell (i.e., current holding is not cash), execute a sell
            if current_holding != 'GBP':
                sell_price = get_trade_price(current_holding, i) * (1 - slippage_percentage)
                proceeds = positions[current_holding] * sell_price
                cash += proceeds
                trades.append({
                    'asset': current_holding,
                    'action': 'sell',
                    'qty': positions[current_holding],
                    'price': sell_price,
                    'time_point': i
                })
                positions[current_holding] = 0
                current_holding = 'GBP'  # No asset holding after selling

            # If the signal is to buy a new asset
            if asset_to_trade != 'GBP':
                trade_price = get_trade_price(asset_to_trade, i)
                adjusted_trade_price = trade_price * (1 + slippage_percentage)
                transaction_cost = cash * transaction_cost_percentage
                # Buy new asset if there is enough cash after transaction costs
                quantity_to_buy = (cash - transaction_cost) / adjusted_trade_price
                if quantity_to_buy > 0:
                    positions[asset_to_trade] = quantity_to_buy
                    trades.append({
                        'asset': asset_to_trade,
                        'action': 'buy',
                        'qty': quantity_to_buy,
                        'price': adjusted_trade_price,
                        'transaction_cost': transaction_cost,
                        'time_point': i
                    })
                    cash = 0  # All cash has been invested
                    current_holding = asset_to_trade

        # Calculate portfolio value at this time point
        total_value = cash + sum(qty * get_trade_price(asset, i) for asset, qty in positions.items())
        portfolio_value.append(total_value)

    # Store backtesting details in strategy output
    strategy_output['backtest_details'] = {
        'portfolio_value': portfolio_value,
        'trades': trades,
        'final_positions': positions,
        'final_cash': cash
    }

    return strategy_output