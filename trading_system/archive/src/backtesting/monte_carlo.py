import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import norm

from functions.strategy_development_indicators import TAIndicators
from functions.strategy_development_trading_strategy import TradeAllocation
from functions.strategy_development_backtest import Backtest
from functions import strategy_development_backtest_analyse


#########################################################################################
#########################################################################################
#########################################################################################


# This code appears to be implementing a Monte Carlo simulation to model the daily returns of a particular asset and predict future prices based on those returns. The daily_returns() function takes in a time series of asset prices (data), the number of days to simulate returns for (days), the number of iterations to run the simulation for (iterations), and a boolean flag (plot) indicating whether or not to plot the results of the simulation.
# The probs_find() function calculates the probability of the predicted asset prices being above or below a certain value or return threshold.
# The monte_carlo_analysis() function then prints out a report of the results of the Monte Carlo simulation, including the expected value and return of the simulated asset prices, the expected value and return of a "buy and hold" strategy, and various other metrics such as maximum drawdown and alpha.


#########################################################################################
#########################################################################################
#########################################################################################

# v1.0
class MonteCarlo:
    def __init__(self, data, days, iterations, plot, close, cash, fee, slippage, startdate_backtest, enddate_backtest, sl, tp, high, low, vol, short, long, version):
        self.data = data
        self.days = days
        self.iterations = iterations
        self.plot = plot
        self.close = close
        self.cash = cash
        self.fee = fee
        self.slippage = slippage
        self.startdate_backtest = startdate_backtest
        self.enddate_backtest = enddate_backtest
        self.sl = sl
        self.tp = tp
        self.high = high
        self.low = low
        self.vol = vol
        self.short = short
        self.long = long
        self.version = version

    def run(self):
        # Generate prices of asset using monte carlo simulation
        df = self.price_list()
        # monte_carlo.simulate_mc(data, days, iterations)

        # Apply functions to generated prices. Indicators, signals, trading strategy, allocation, backtest, backtest analyse
        final_values = []
        compare_hold_values = []
        strategy_max_drawdown_values = []
        asset_max_drawdown_values = []

        for column in df:
            # print progress to log
            prog = round(((column + 1) / self.iterations) * 100, 2)
            print("Progress: " + str(prog) + "%")

            ta_indicators = TAIndicators(data=df, close=column, high=self.high, low=self.low, vol=self.vol, short=self.short,long=self.long)
            results = ta_indicators.run()
            df_mc = pd.DataFrame.from_dict(results)

            trade_alloc = TradeAllocation(data=df_mc, close=column)
            trade_alloc.signal()

            backtest = Backtest(trade_alloc.data, 'close', self.cash, self.fee, self.slippage, self.startdate_backtest, self.enddate_backtest, self.sl, self.tp)
            results = backtest.run()
            df_bt = pd.DataFrame.from_dict(results)
            data, final_value, compare_hold_val, strategy_max_drawdown, asset_max_drawdown = strategy_development_backtest_analyse.analyse_backtest(df_bt, self.cash, self.version, printlog=False)

            final_values.append(final_value)
            compare_hold_values.append(compare_hold_val)
            strategy_max_drawdown_values.append(strategy_max_drawdown)
            asset_max_drawdown_values.append(asset_max_drawdown)

        return {
                'final_values': final_values,
                'compare_hold_values': compare_hold_values,
                'strategy_max_drawdown_values': strategy_max_drawdown_values,
                'asset_max_drawdown_values': asset_max_drawdown_values
        }

    def log_returns(self):
        return np.log(1 + self.data.pct_change())

    def mean_and_var(self):
        log_returns = self.log_returns()
        u = log_returns.mean()
        var = log_returns.var()
        return u, var

    def drift(self):
        u, var = self.mean_and_var()
        return u - (0.5 * var)

    def stdev(self):
        return self.log_returns().std()

    def daily_returns(self):
        drift = self.drift()
        stdev = self.stdev()
        Z = norm.ppf(np.random.rand(self.days, self.iterations))
        return np.exp(drift + stdev * Z)

    def price_list(self):
        daily_returns = self.daily_returns()
        price_list = np.zeros_like(daily_returns)
        price_list[0] = self.data.iloc[-1]
        for t in range(1, self.days):
            price_list[t] = price_list[t - 1] * daily_returns[t]
        return pd.DataFrame(price_list)

    def plot_simulation(self):
        price_list = self.price_list()
        if self.plot:
            x = pd.DataFrame(price_list).iloc[-1]
            fig, ax = plt.subplots(1, 3, figsize=(14, 4))
            fig.suptitle('Monte Carlo Simulated Asset Price')
            sns.lineplot(ax=ax[0], data=price_list, legend=False)
            plt.legend([], [], frameon=False)
            plt.xlabel("Stock Price")
            sns.histplot(x, kde=True, stat="density", bins=30, ax=ax[1])
            ax[1].axvline(price_list[0][0], color='black', linestyle='--', label="starting price")
            plt.xlabel("Stock Price")
            sns.histplot(x, kde=True, stat="density", bins=30, cumulative=True, ax=ax[2])
            ax[2].axvline(price_list[0][0], color='black', linestyle='--', label="starting price")
            plt.xlabel("Stock Price")
        return pd.DataFrame(price_list)

    def probs_find(self, predicted, cash, higherthan, on):
        if on == 'return':
            over = predicted[((predicted - cash) / cash >= higherthan)].count()
            less = predicted[((predicted - cash) / cash < higherthan)].count()
        elif on == 'value':
            over = predicted[(predicted >= higherthan)].count()
            less = predicted[(predicted < higherthan)].count()
        else:
            print("'on' must be either value or return")

        perc = (over / (over + less)) * 100
        return perc

    def monte_carlo_analysis(self, final_values, compare_hold_values, strategy_max_drawdown_values, asset_max_drawdown_values,cash, days, iterations, version, plot):
        df = pd.DataFrame(final_values)
        df_compare = pd.DataFrame(compare_hold_values)
        df_drawdown = pd.DataFrame(strategy_max_drawdown_values)
        df_hold_drawdown = pd.DataFrame(asset_max_drawdown_values)

        # Printing monte carlo report
        print('---------------------------------------------------')
        print('Montecarlo Simulation assessment. Algorithm version: ' + version)
        print('---------------------------------------------------')
        print(f"Days: {days}")
        print(f"Scenarios: {iterations}")
        print('---------------------------------------------------')
        print(f"Starting Cash: £{cash}")
        print(f"Expected Value: £{round(df.values.mean(), 2)}")
        print(f"Return: {round(100 * (df.values.mean() - cash) / cash, 2)}%")
        print(f"Expected Value Buy & Hold: £{round(df_compare.values.mean(), 2)}")
        print(f"Return Buy & Hold: {round(100 * (df_compare.values.mean() - cash) / cash, 2)}%")
        print(f"Alpha: £{round(df.values.mean() - df_compare.values.mean(), 2)}")
        print('---------------------------------------------------')
        print(f"Average Strategy Max Drawdown: £{int(df_drawdown.mean())}")
        print(f"Average Hold Max Drawdown: £{int(df_hold_drawdown.mean())}")
        print('---------------------------------------------------')
        print(f"Probability of Breakeven: {int(self.probs_find(df, cash, 0, on='return'))}%")
        print(f"Probability of Required Return: {int(self.probs_find(df, cash, 0.3, on='return'))}%")
        print('---------------------------------------------------')
        print('Process: Montecarlo Simulation Analyse Complete.')

        # Plot Option
        if plot == True:
            x = df
            fig, ax = plt.subplots(1, 2, figsize=(14, 4))
            fig.suptitle('Monte Carlo Simulated Backtest')

            axs = 0
            sns.histplot(x, kde=True, stat="density", bins=50, ax=ax[axs])
            ax[axs].axvline(cash, linewidth=1, color='black', linestyle='--', label="starting cash")
            ax[axs].axvline(cash * 1.3, linewidth=1, color='red', linestyle='--', label="target return")
            ax[axs].axvline(df.values.mean(), linewidth=1, color='green', label="expected return")
            plt.xlabel("Final Equity")

            axs = 1
            sns.histplot(x, kde=True, stat="density", bins=50, cumulative=True, ax=ax[axs])
            ax[axs].axvline(cash, color='black', linestyle='--', label="starting cash")
            ax[axs].axhline(float(1 - (self.probs_find(df, cash, 0, on='return') / 100)), linewidth=1, color='black',
                            linestyle='--')
            ax[axs].axvline(cash * 1.3, linewidth=1, color='red', linestyle='--', label="target return")
            ax[axs].axhline(float(1 - (self.probs_find(df, cash, 0.3, on='return') / 100)), linewidth=1, color='red',
                            linestyle='--')
            ax[axs].axvline(df.values.mean(), color='green', linewidth=1, label="expected return")
            ax[axs].axhline(0.5, linewidth=1, color='green')
            plt.xlabel("Final Equity")
            plt.show()


#########################################################################################
#########################################################################################
#########################################################################################

# v0.1
# Generate prices of target asset
# def daily_returns(data, days, iterations, plot):
#     # with ThreadPoolExecutor() as executor:
#     log_returns = np.log(1 + data.pct_change())
#
#     u = log_returns.mean()
#     var = log_returns.var()
#     drift = u - (0.5*var)
#
#     stdev = log_returns.std()
#     Z = norm.ppf(np.random.rand(days, iterations))
#     daily_returns = np.exp(drift + stdev * Z)
#
#     # Create empty matrix
#     price_list = np.zeros_like(daily_returns)
#     # Put the last actual price in the first row of matrix.
#     price_list[0] = data.iloc[-1]
#     # Calculate the price of each day
#     for t in range(1, days):
#         price_list[t] = price_list[t - 1] * daily_returns[t]
#
#     if plot == True:
#         x = pd.DataFrame(price_list).iloc[-1]
#
#         fig, ax = plt.subplots(1, 3, figsize=(14, 4))
#         fig.suptitle('Monte Carlo Simulated Asset Price')
#         sns.lineplot(ax=ax[0], data=price_list, legend=False)
#         plt.legend([], [], frameon=False)
#         plt.xlabel("Stock Price")
#
#         sns.histplot(x, kde=True, stat="density", bins=30, ax=ax[1])
#         ax[1].axvline(price_list[0][0], color='black', linestyle='--', label="starting price")
#         plt.xlabel("Stock Price")
#
#         sns.histplot(x, kde=True, stat="density", bins=30, cumulative=True, ax=ax[2])
#         ax[2].axvline(price_list[0][0], color='black', linestyle='--', label="starting price")
#         plt.xlabel("Stock Price")
#
#     return pd.DataFrame(price_list)


# Find probability function
# def probs_find(predicted, cash, higherthan, on):
#     if on == 'return':
#         over = predicted[((predicted-cash)/cash >= higherthan)].count()
#         less = predicted[((predicted-cash)/cash < higherthan)].count()
#     elif on == 'value':
#         over = predicted[(predicted >= higherthan)].count()
#         less = predicted[(predicted < higherthan)].count()
#     else:
#         print("'on' must be either value or return")
#
#     perc = (over / (over + less)) * 100
#     return perc


# def monte_carlo_analysis(final_values, compare_hold_values, strategy_max_drawdown_values, asset_max_drawdown_values, cash, days, iterations, version, plot):
#     df = pd.DataFrame(final_values)
#     df_compare = pd.DataFrame(compare_hold_values)
#     df_drawdown = pd.DataFrame(strategy_max_drawdown_values)
#     df_hold_drawdown = pd.DataFrame(asset_max_drawdown_values)
#
#     # Printing monte carlo report
#     print('---------------------------------------------------')
#     print('Montecarlo Simulation assessment. Algorithm version: ' + version)
#     print('---------------------------------------------------')
#     print(f"Days: {days}")
#     print(f"Scenarios: {iterations}")
#     print('---------------------------------------------------')
#     print(f"Starting Cash: £{cash}")
#     print(f"Expected Value: £{round(df.values.mean(), 2)}")
#     print(f"Return: {round(100 * (df.values.mean() - cash) / cash, 2)}%")
#     print(f"Expected Value Buy & Hold: £{round(df_compare.values.mean(), 2)}")
#     print(f"Return Buy & Hold: {round(100 * (df_compare.values.mean() - cash) / cash, 2)}%")
#     print(f"Alpha: £{round(df.values.mean() - df_compare.values.mean(), 2)}")
#     print('---------------------------------------------------')
#     print(f"Average Strategy Max Drawdown: £{int(df_drawdown.mean())}")
#     print(f"Average Hold Max Drawdown: £{int(df_hold_drawdown.mean())}")
#     print('---------------------------------------------------')
#     print(f"Probability of Breakeven: {int(probs_find(df, cash, 0, on='return'))}%")
#     print(f"Probability of Required Return: {int(probs_find(df, cash, 0.3, on='return'))}%")
#     print('---------------------------------------------------')
#     print('Process: Montecarlo Simulation Analyse Complete.')
#
#     # Plot Option
#     if plot == True:
#         x = df
#         fig, ax = plt.subplots(1, 2, figsize=(14, 4))
#         fig.suptitle('Monte Carlo Simulated Backtest')
#
#         axs = 0
#         sns.histplot(x, kde=True, stat="density", bins=50, ax=ax[axs])
#         ax[axs].axvline(cash, linewidth=1, color='black', linestyle='--', label="starting cash")
#         ax[axs].axvline(cash*1.3, linewidth=1, color='red', linestyle='--', label="target return")
#         ax[axs].axvline(df.values.mean(), linewidth=1, color='green',label="expected return")
#         plt.xlabel("Final Equity")
#
#         axs = 1
#         sns.histplot(x, kde=True, stat="density", bins=50, cumulative=True, ax=ax[axs])
#         ax[axs].axvline(cash, color='black', linestyle='--', label="starting cash")
#         ax[axs].axhline(float(1 - (probs_find(df, cash, 0, on='return') / 100)), linewidth=1, color='black', linestyle='--')
#         ax[axs].axvline(cash * 1.3, linewidth=1, color='red', linestyle='--', label="target return")
#         ax[axs].axhline(float(1 - (probs_find(df, cash, 0.3, on='return')/100)), linewidth=1, color='red', linestyle='--')
#         ax[axs].axvline(df.values.mean(), color='green', linewidth=1, label="expected return")
#         ax[axs].axhline(0.5, linewidth=1, color='green')
#         plt.xlabel("Final Equity")
#         plt.show()


#########################################################################################
#########################################################################################
#########################################################################################
