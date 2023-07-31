from datetime import time
import pandas as pd


#########################################################################################
#########################################################################################
#########################################################################################


class TradeAllocation:
    """
    This code defines three functions: signal, allocation, and plot_allocation. The signal function adds two columns to the input dataframe data: trigger and trigger_shift. The trigger column is created by using np.where to set the value to "BUY" if the value in the signal_EMA column is 1, "SELL" if the value in the signal_EMA column is 2, and "999" otherwise. The trigger_shift column is created by shifting the trigger column one time period back.
    The allocation function adds three columns to the input dataframe data: trade, position, and position_shift. The trade column is created by using np.where to set the value to 1 if the current trigger value is "BUY" and the previous trigger value is not "BUY", to 2 if the current trigger value is "SELL" and the previous trigger value is not "SELL", and to 0 otherwise. The position column is created by using np.where to set the value to "long" if the trigger value is "BUY", "short" if the trigger value is "SELL", and np.nan otherwise. The position_shift column is created by shifting the position column one time period back.
    The plot_allocation function creates a line plot of the close column from the input dataframe data, with points marked for trades using the trade column. It does this by adding two columns to the input dataframe data: flg_trade_buy and flg_trade_sell. The flg_trade_buy column is created by using np.where to set the value to the corresponding value in the close column if the value in the trade column is 1, and to np.nan otherwise. The flg_trade_sell column is created in a similar manner, using the value in the close column if the value in the trade column is 2. The function then uses the sns.lineplot and sns.scatterplot functions from the seaborn library to create a line plot of the close column and scatter plots for the flg_trade_buy and flg_trade_sell columns, using different marker shapes and colors to distinguish between buy and sell trades. Finally, it uses the ticker.MultipleLocator function to set the x-axis tick marks to be spaced 100 units apart.
    """

    def __init__(self, data, close):
        self.data = data
        self.close = close
        self.positions = []

    def run(self):
        self.generate_signals()
        # self.risk_management(2, 5)

    def generate_signals(self):
        # Iterate over the DataFrame by index (i.e., row by row)
        for i in range(1, len(self.data) - 1):
            # Define market open time as the first bar of the day (this bar typically represents the first hour of trading)
            is_market_open = pd.to_datetime(self.data['date'][i]).time() == time(10, 30)
            is_next_hour = pd.to_datetime(self.data['date'][i + 1]).time() == time(11, 30)

            if is_market_open and is_next_hour:
                # Define your indicators and conditions for going long or short
                # For instance, using RSI and Volume as sample indicators:
                if self.data['rsi'][i] < 30:
                    self.data.loc[i, 'signal'] = 'long'

                elif self.data['rsi'][i] > 70:
                    self.data.loc[i, 'signal'] = 'short'

                else:
                    self.data.loc[i, 'signal'] = 'neutral'

    def risk_management(self, stop_loss_level, take_profit_level):
        # The risk_management method could look something like this:
        # You'll have to adapt this depending on how you're calculating stop loss and take profit
        for i in range(1, len(self.data)):
            if self.data.loc[i, 'signal'] == 'long':
                self.data.loc[i, 'StopLoss'] = self.data.loc[i, self.close] - stop_loss_level
                self.data.loc[i, 'TakeProfit'] = self.data.loc[i, self.close] + take_profit_level
            elif self.data.loc[i, 'signal'] == 'short':
                self.data.loc[i, 'StopLoss'] = self.data.loc[i, self.close] + stop_loss_level
                self.data.loc[i, 'TakeProfit'] = self.data.loc[i, self.close] - take_profit_level


#########################################################################################
#########################################################################################
#########################################################################################
