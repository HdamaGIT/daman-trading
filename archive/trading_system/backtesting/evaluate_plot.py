import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import pandas as pd
import numpy as np


import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np

def plot_prices_positions_and_portfolio(dic):
    btc_gbp_df = pd.DataFrame(dic['BTC-GBP'])
    eth_gbp_df = pd.DataFrame(dic['ETH-GBP'])
    positions_df = pd.DataFrame(dic['combined_position'])
    portfolio_values_df = pd.DataFrame(dic['backtest_details']['portfolio_value'], columns=['Portfolio Value'])

    # Calculate Drawdown
    portfolio_values = portfolio_values_df['Portfolio Value']
    peak = portfolio_values.expanding(min_periods=1).max()
    drawdown = (portfolio_values - peak) / peak * 100  # Convert to percentage

    # Create figure with two subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14), sharex=True)

    # Plot 1: Asset Prices and Positions
    color_btc = 'tab:blue'
    color_eth = 'tab:orange'
    ax1.plot(btc_gbp_df.index, btc_gbp_df['Close'], label='BTC-GBP Price', color=color_btc)
    ax1.set_ylabel('BTC-GBP Price', color=color_btc)
    ax1.tick_params(axis='y', labelcolor=color_btc)

    ax1_b = ax1.twinx()
    ax1_b.plot(eth_gbp_df.index, eth_gbp_df['Close'], label='ETH-GBP Price', color=color_eth)
    ax1_b.set_ylabel('ETH-GBP Price', color=color_eth)
    ax1_b.tick_params(axis='y', labelcolor=color_eth)

    # Highlight periods where BTC or ETH is held
    for i in range(1, len(positions_df)):
        if positions_df['final_signal'][i] == 'BTC':
            ax1.axvspan(btc_gbp_df.index[i-1], btc_gbp_df.index[i], color='green', alpha=0.2, label='Holding BTC' if i == 1 else "")
        elif positions_df['final_signal'][i] == 'ETH':
            ax1.axvspan(eth_gbp_df.index[i-1], eth_gbp_df.index[i], color='red', alpha=0.2, label='Holding ETH' if i == 1 else "")

    # Plot 2: Portfolio Value and Drawdown
    ax2.plot(portfolio_values_df.index, portfolio_values, label='Portfolio Value', color='blue')
    ax2.set_ylabel('Portfolio Value', color='purple')
    ax2.tick_params(axis='y', labelcolor='purple')

    # Secondary Y-axis for Drawdown
    ax2_b = ax2.twinx()
    ax2_b.plot(portfolio_values_df.index, drawdown, label='Drawdown (%)', color='red')
    ax2_b.set_ylabel('Drawdown (%)', color='orange')
    ax2_b.tick_params(axis='y', labelcolor='orange')

    # Highlight periods where BTC or ETH is held in Portfolio Value plot as well
    for i in range(1, len(positions_df)):
        if positions_df['final_signal'][i] == 'BTC':
            ax2.axvspan(portfolio_values_df.index[i-1], portfolio_values_df.index[i], color='green', alpha=0.1)
        elif positions_df['final_signal'][i] == 'ETH':
            ax2.axvspan(portfolio_values_df.index[i-1], portfolio_values_df.index[i], color='red', alpha=0.1)

    # Formatting and Layout Adjustments
    plt.xlabel('Date')
    plt.xticks(rotation=45)
    ax1.xaxis.set_major_locator(mdates.MonthLocator())
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
    fig.autofmt_xdate()  # Auto formats the date labels
    ax1.legend(loc='upper left')
    ax1_b.legend(loc='upper right')
    ax2.legend(loc='upper left')
    ax2_b.legend(loc='upper right', bbox_to_anchor=(1, 0.9))  # Adjust legend position for visibility
    plt.title('Asset Prices, Positions, Portfolio Value, and Drawdown Over Time', loc='left', pad=20)
    plt.tight_layout()
    plt.show()


# def plot_prices_positions_and_portfolio(dic):
#     btc_gbp_df = pd.DataFrame(dic['BTC-GBP'])
#     eth_gbp_df = pd.DataFrame(dic['ETH-GBP'])
#     positions_df = pd.DataFrame(dic['combined_position'])
#     portfolio_values_df = pd.DataFrame(dic['backtest_details']['portfolio_value'], columns=['Portfolio Value'])
#
#     # Calculate Drawdown
#     portfolio_values = portfolio_values_df['Portfolio Value']
#     peak = portfolio_values.expanding(min_periods=1).max()
#     drawdown = (portfolio_values - peak) / peak * 100  # Convert to percentage
#
#     # Create figure with two subplots
#     fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 14), sharex=True)
#
#     # Plot 1: Asset Prices and Positions
#     color_btc = 'tab:blue'
#     color_eth = 'tab:orange'
#     ax1.plot(btc_gbp_df.index, btc_gbp_df['Close'], label='BTC-GBP Price', color=color_btc)
#     ax1.set_ylabel('BTC-GBP Price', color=color_btc)
#     ax1.tick_params(axis='y', labelcolor=color_btc)
#
#     ax1_b = ax1.twinx()
#     ax1_b.plot(eth_gbp_df.index, eth_gbp_df['Close'], label='ETH-GBP Price', color=color_eth)
#     ax1_b.set_ylabel('ETH-GBP Price', color=color_eth)
#     ax1_b.tick_params(axis='y', labelcolor=color_eth)
#
#     for i, pos in enumerate(positions_df['final_signal']):
#         if pos == 'BTC':
#             ax1.axvline(x=btc_gbp_df.index[i], color='green', linestyle='--', alpha=0.1)
#         elif pos == 'ETH':
#             ax1.axvline(x=eth_gbp_df.index[i], color='red', linestyle='--', alpha=0.1)
#
#     # Plot 2: Portfolio Value and Drawdown
#     ax2.plot(portfolio_values_df.index, portfolio_values, label='Portfolio Value', color='blue')
#     ax2.set_ylabel('Portfolio Value', color='purple')
#     ax2.tick_params(axis='y', labelcolor='purple')
#
#     # Secondary Y-axis for Drawdown
#     ax2_b = ax2.twinx()
#     ax2_b.plot(portfolio_values_df.index, drawdown, label='Drawdown (%)', color='red')
#     ax2_b.set_ylabel('Drawdown (%)', color='orange')
#     ax2_b.tick_params(axis='y', labelcolor='orange')
#
#     for i, pos in enumerate(positions_df['final_signal']):
#         if pos == 'BTC':
#             ax2.axvline(x=portfolio_values_df.index[i], color='green', linestyle='--', alpha=0.1)
#         elif pos == 'ETH':
#             ax2.axvline(x=portfolio_values_df.index[i], color='red', linestyle='--', alpha=0.1)
#
#     # Formatting and Layout Adjustments
#     plt.xlabel('Date')
#     plt.xticks(rotation=45)
#     ax1.xaxis.set_major_locator(mdates.MonthLocator())
#     ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
#     fig.autofmt_xdate()  # Auto formats the date labels
#     ax1.legend(loc='upper left')
#     ax1_b.legend(loc='upper right')
#     ax2.legend(loc='upper left')
#     ax2_b.legend(loc='upper right', bbox_to_anchor=(1, 0.9))  # Adjust legend position for visibility
#     plt.title('Asset Prices, Positions, Portfolio Value, and Drawdown Over Time', loc='left', pad=20)
#     plt.tight_layout()
#     plt.show()
