import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np


def analyse_backtest(data, cash, version, printlog):
    """
    Analyzes the results of a backtest for a trading strategy and compares it to a "buy & hold" comparison. Calculates various performance metrics, such as the final portfolio value, percentage profit/loss, Sharpe ratio, and maximum drawdown. If the `printlog` parameter is set to `True`, the function will print out all of these metrics.

    Parameters:
    data (pandas DataFrame): Dataframe containing the backtest results.
    cash (float): Initial cash balance at the start of the backtest.
    version (str): Algorithm version being tested.
    printlog (bool): Whether to print the performance metrics or not.

    Returns:
    None
    """

    # Calculate the final value of the portfolio
    final_value = data['portfolio_values'].iat[-1]
    # Calculate net profit/loss by subtracting the starting cash from the final portfolio value
    net = data['portfolio_values'].iat[-1] - cash
    # Calculate percentage profit/loss by dividing the net profit/loss by the starting cash
    perc_profit = net / cash
    # Format the percentage profit/loss as a percentage with 2 decimal places
    perc_profit_f = "{:.2%}".format(perc_profit)
    # Calculate the final value of the "buy & hold" comparison asset
    compare_hold_val = data['compare_hold_values'].iat[-1]
    # Calculate percentage profit/loss for the "buy & hold" comparison by subtracting the starting cash from the final value of the comparison asset
    perc_profit_asset = (compare_hold_val - cash) / cash
    # Format the percentage profit/loss for the "buy & hold" comparison as a percentage with 2 decimal places
    perc_profit_asset_f = "{:.2%}".format(perc_profit_asset)
    # Calculate the alpha (difference in returns) between the strategy and the "buy & hold" comparison
    alpha = final_value - compare_hold_val

    # Calculate the maximum drawdown for the strategy by finding the minimum drawdown value in the "portfolio_drawdown" column of the dataframe
    data['portfolio_return'] = data['portfolio_values'] - data['portfolio_values'].shift(1)
    data['portfolio_cumulative'] = data['portfolio_return'].cumsum().round(2)
    data['portfolio_high'] = data['portfolio_cumulative'].cummax()
    data['portfolio_drawdown'] = data['portfolio_cumulative'] - data['portfolio_high']
    strategy_max_drawdown = data['portfolio_drawdown'].min()
    # Calculate the maximum drawdown for the "buy & hold" comparison in a similar way
    data['asset_return'] = data['compare_hold_values'] - data['compare_hold_values'].shift(1)
    data['asset_cumulative'] = data['asset_return'].cumsum().round(2)
    data['asset_high'] = data['asset_cumulative'].cummax()
    data['asset_drawdown'] = data['asset_cumulative'] - data['asset_high']
    asset_max_drawdown = data['asset_drawdown'].min()
    # Average Drawdown %
    # Max Drawdown Duration
    # Average Drawdown Duration
    # Calculate the number of trades by counting the number of rows in the dataframe where the "trade_flg" column is equal to 1
    number_trades = data[data['trade_values'] == 1]['holding_values'].count()
    # Calculate the total fees paid by summing the values in the "fee_cash" column where the "trade_flg" column is equal to 1
    fee_paid = data[data['trade_values'] == 1]['fee_cash_values'].sum()
    # Find the maximum trade duration by taking the maximum value in the "hold_period" column
    max_trade_duration = max(data['holding_values'])
    # Calculate the average trade duration by dividing the sum of the "hold_period" column by the number of rows in the dataframe where the "trade_flg" column is equal to 1
    avg_trade_duration = data[data['trade_values'] == 1]['holding_values'].sum() / data[data['trade_values'] == 1]['holding_values'].count()

    # Calculate the Sharpe ratio for the strategy by taking the annualized mean return divided by the annualized standard deviation of returns
    data['PeriodReturn_portfolio'] = data['portfolio_values'].pct_change(1)
    SR_Portfolio = ((365 * 24) ** 0.5) * data['PeriodReturn_portfolio'].mean() / data['PeriodReturn_portfolio'].std()
    # Calculate the Sharpe ratio for the "buy & hold" comparison in a similar way
    data['PeriodReturn_hold'] = data['compare_hold_values'].pct_change(1)
    SR_hold = ((365*24)**0.5) * data['PeriodReturn_hold'].mean() / data['PeriodReturn_hold'].std()

    if printlog == True:
        print('---------------------------------------------------')
        print('Backtest assessment. Algorithm version: ' + version)
        print('---------------------------------------------------')
        print("Number months in backtest: " + str(len(data) / 30))
        print('Number Trades: ' + str(number_trades))
        print('Average trades per month: ' + str(number_trades / (len(data) / 30)))
        print('Start Portfolio Value: £{: .2f}'.format(cash))
        print('End Portfolio Value: £{: .2f}'.format(final_value))
        if net > 0:
            print('Profit: £{: .2f}'.format(net))
        else:
            print('Loss: £{: .2f}'.format(net))
        print('% : ' + str(perc_profit_f))
        print('Buy & Hold asset: £{: .2f}'.format(compare_hold_val))
        print('% : ' + str(perc_profit_asset_f))
        print('Alpha: £{: .2f}'.format(alpha))
        print('---------------------------------------------------')
        print('Strategy Max Drawdown: £{: .2f}'.format(strategy_max_drawdown))
        print('Asset Max Drawdown: £{: .2f}'.format(asset_max_drawdown))
        print('---------------------------------------------------')
        print('Fee Paid : £{: .2f}'.format(fee_paid))
        print('Max Hold Duration: ' + str(max_trade_duration))
        print('Avg Hold Duration: {: .2f}'.format(avg_trade_duration))
        print('---------------------------------------------------')
        print('Sharpe Ratio (Strategy): {:.2f}'.format(SR_Portfolio))
        print('Sharpe Ratio (Hold): {:.2f}'.format(SR_hold))
        print('---------------------------------------------------')
        print('Process: Backtest Analyse Complete.')
    return data, final_value, compare_hold_val, strategy_max_drawdown, asset_max_drawdown


def plot_backtest(data):

    data['flg_trade_buy'] = np.where((data['position_values'] == 'long') & (data['trade_values'] == 1), data['portfolio_values'], np.nan)
    data['flg_trade_sell'] = np.where((data['position_values'] == 'cash') & (data['trade_values'] == 1), data['portfolio_values'], np.nan)
    data['flg_trade_short'] = np.where((data['position_values'] == 'short') & (data['trade_values'] == 1), data['portfolio_values'], np.nan)
    fig, axs = plt.subplots(2)
    fig.suptitle('Total Value & Drawdown')

    # Top plot
    # 'ask_Close', 'short_ema', 'long_ema'
    # ax=0
    # sns.lineplot(ax=axs[ax], data=data, x='date', y='ask_Close', label='long_ema')
    # sns.lineplot(ax=axs[ax], data=data, x='date', y='short_ema', label='long_ema')
    # sns.lineplot(ax=axs[ax], data=data, x='date', y='long_ema', label='long_ema')

    # Middle plot
    # Portfolio value, compare hold value, flag buy/sell
    ax = 0
    sns.lineplot(ax=axs[ax], data=data, x=data.index, y='portfolio_values', label='Portfolio Value')
    sns.lineplot(ax=axs[ax], data=data, x=data.index, y='compare_hold_values', label='Buy & Hold Value')
    sns.scatterplot(ax=axs[ax], data=data, x=data.index, y='flg_trade_buy', color='g', s=100, marker="^")
    sns.scatterplot(ax=axs[ax], data=data, x=data.index, y='flg_trade_sell', color='r', s=100, marker="v")
    sns.scatterplot(ax=axs[ax], data=data, x=data.index, y='flg_trade_short', color='r', s=100, marker="v")
    axs[ax].xaxis.set_major_locator(ticker.MultipleLocator(100))

    # Bottom plot
    # Portfolio drawdown, compare hold drawdown
    ax = 1
    sns.lineplot(ax=axs[ax], data=data, x=data.index, y='portfolio_drawdown', label='Portfolio Drawdown')
    sns.lineplot(ax=axs[ax], data=data, x=data.index, y='asset_drawdown', label='Buy & Hold Drawdown')
    axs[ax].xaxis.set_major_locator(ticker.MultipleLocator(100))

    plt.show()

