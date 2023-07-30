import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import seaborn as sns
import numpy as np


#########################################################################################
#########################################################################################
#########################################################################################


# The backtest function simulates a trading strategy using historical data. It takes in a data frame containing the data to be used for the backtest, a column name of the data frame that corresponds to the price of the security being traded, as well as various parameters such as the starting cash balance, fee, and slippage for each trade. It returns a dictionary with the results of the backtest.
# The function first filters the data to only include the dates between the start and end dates of the backtest period. It then initializes several variables, including a cash balance, a holding (the number of securities being held), and a short (the number of securities being sold short). It also initializes several arrays that will be used to store the results of the backtest.
# The function then iterates over the rows of the data frame and performs the following actions:
    # It checks if the position at the current row (indicated by the pos variable) is the same as the position at the previous row (indicated by the prevpos variable). If it is, it increments the days variable by 1. If it is not, it sets the hold_period variable to the value of days, resets days to 0, and sets the trade_flg variable to 1.
    # If trade_flg is 1, the function checks the value of pos to determine whether it is a "long" or "short" position. If it is a "long" position, it calculates the number of securities that can be bought with the available cash and slippage, and adds this number to the holding variable. If it is a "short" position, it calculates the number of securities that can be sold short and adds this number to the short variable.
    # It then calculates the portfolio value and appends this value, as well as the values of the other variables, to the relevant arrays.
    # The function then returns a dictionary containing the results of the backtest.



#########################################################################################
#########################################################################################
#########################################################################################

# v1.1
class Backtest:
    def __init__(self, data, close, cash, fee, slippage, startdate, enddate, sl, tp):
        """
        Initialize the backtest with the provided data and rules.

        Parameters:
            data (DataFrame): A pandas DataFrame containing the data to use for the backtest.
            price_column (str): The name of the column in the data containing the price of the security.
            cash (float): The starting cash balance for the backtest.
            fee (float): The fee to be paid for each trade, as a fraction of the trade value.
            slippage (float): The slippage to be applied to each trade, as a fraction of the trade price.
            startdate (date): The start date for the backtest period.
            enddate (date): The end date for the backtest period.
        """
        ### Limit data based on start and end date of backtest period
        # mask = (data['date'] >= startdate) & (data['date'] <= enddate)
        # self.data = data.loc[mask]
        self.data = data

        ### STOP LOSS AND PROFIT FACTOR
        # Initialize the stop_loss column with NaN values
        self.sl = sl
        self.tp = tp
        self.trade_exit = 0
        self.stop_loss = np.nan
        self.take_profit = np.nan

        ### ALLOCATION
        self.position = np.nan
        self.prevpos = np.nan

        ### FOR TRADES
        # Initiate Cash
        self.cash = int(cash)

        # Initiate Holding
        self.portfolio_value = self.cash
        self.compare_holding = cash / float(self.data[close].iloc[0])
        self.days = 0
        self.price = 0
        self.holding = 0
        self.short = 0
        self.short_price = 0
        self.hold_period = 0
        self.trade_flg = 0
        self.trade_price = 0
        self.fee_paid = 0
        self.fee_paid_cash = 0
        self.price_paid = 0
        self.slippage_cash = 0
        self.x = 0
        self.fee = fee
        self.slippage = slippage

        # Initiate Arrays to make into dataframe at end
        self.price_values = []
        self.trade_prices = []
        self.position_values = []
        self.portfolio_values = []
        self.cash_values = []
        self.holding_values = []
        self.short_values = []
        self.compare_hold_values = []
        self.hold_period_values = []
        self.trade_values = []
        self.signal_values = []
        self.short_prices = []
        self.fee_values = []
        self.fee_cash_values = []
        self.price_paid_values = []
        self.slippage_values = []
        self.stop_loss_values = []
        self.take_profit_values = []

    def run(self):
        """
        Run the backtest.
        """
        # Iterate rows in dataframe
        for row in self.data.itertuples():
            self.price = float(row[2])
            self.trade = row.signal
            self.trigger = row.trigger

            self.calc_stop_loss()
            self.calc_allocation()

            if self.trade != 0:
                self.apply_trade()

            self.update_values()

        # Return results as dictionary
        return {
            # 'x_values': self.x_values,
            'price_values': self.price_values,
            'trade_values': self.trade_values,
            'signal_values': self.signal_values,
            'position_values': self.position_values,
            'portfolio_values': self.portfolio_values,
            'compare_hold_values': self.compare_hold_values,
            'trade_prices': self.trade_prices,
            'short_prices': self.short_prices,
            'cash_values': self.cash_values,
            'holding_values': self.holding_values,
            'short_values': self.short_values,
            'hold_period_values': self.hold_period_values,
            'fee_values': self.fee_values,
            'fee_cash_values': self.fee_cash_values,
            'slippage_values': self.slippage_values,
            'price_paid_values': self.price_paid_values,
            'stop_loss_values': self.stop_loss_values,
            'take_profit_values': self.take_profit_values,
        }

    def calc_stop_loss(self):
        """
        Create a stop_loss column in the data set based on the trade and close columns.
        - If the trade is 1 (buy), set the stop_loss to the close price minus 20% of the close price.
        - If the trade is 2 (sell), set the stop_loss to the close price plus 20% of the close price.
        - If the trade is 0 (no trade) and the close price is less than the previous stop_loss value,
          set the stop_loss to the close price minus 20% of the close price.
        - If the trade is 0 (no trade) and the close price is greater than the previous stop_loss value,
          set the stop_loss to the close price plus 20% of the close price.
        - Otherwise, set the stop_loss to the previous stop_loss value.
        """

        # If the trade is 1 (buy)
        if self.trade == 1:
            # Set the stop_loss to the close price minus 20% of the close price
            self.stop_loss = self.price * (1 - self.sl)
            self.take_profit = self.price * (1 + self.tp)

        # If the trade is 2 (sell)
        elif self.trade == 2:
            # Set the stop_loss to the close price plus 20% of the close price
            self.stop_loss = self.price * (1 + self.sl)
            self.take_profit = self.price * (1 - self.tp)

        # If the trade is 0 (no trade)
        else:
            try:
                self.take_profit = self.take_profit
                # If the close price is less than the previous stop_loss value
                if self.price > self.stop_loss:
                    if self.price * (1 - self.sl) > self.stop_loss:
                        # Set the stop_loss to the close price minus 20% of the close price
                        self.stop_loss = self.price * (1 - self.sl)
                    else:
                        self.stop_loss = self.stop_loss
                # If the close price is greater than the previous stop_loss value
                elif self.price < self.stop_loss:
                    if self.price * (1 + self.sl) < self.stop_loss:
                        # Set the stop_loss to the close price plus 20% of the close price
                        self.stop_loss = self.price * (1 + self.sl)
                    else:
                        self.stop_loss = self.stop_loss
            except:
                self.stop_loss = np.nan
                self.take_profit = np.nan

    def calc_allocation(self):
        """
        Create trade and position columns in the data set based on the trigger column.
        - If the trigger is "BUY" and the previous trigger value is different, set trade to 1 (buy).
        - If the trigger is "SELL" and the previous trigger value is different, set trade to 2 (sell).
        - Otherwise, set trade to 0.
        - If the trigger is "BUY", set position to "long".
        - If the trigger is "SELL", set position to "short".
        - Otherwise, set position to NaN.
        """
        if self.trade > 0:
            self.trade_exit = False

        if self.trade_exit == False:
            if self.trigger == "BUY":
                if self.stop_loss < self.price < self.take_profit:
                    self.position = "long"
                else:
                    self.position = "cash"
                    self.trade_exit = True
                    self.trade = 3
            elif self.trigger == "SELL":
                if self.stop_loss > self.price > self.take_profit:
                    self.position = "short"
                else:
                    self.position = "cash"
                    self.trade_exit = True
                    self.trade = 3
        else:
            self.position = "cash"

    def apply_trade(self):
        self.hold_period = self.days
        self.trade_price = self.price
        self.days = 0
        self.trade_flg = 1

        if self.position == "long":
            if self.prevpos == "short":
                self.short_used_to_buy = self.short
                self.fee_paid = self.short_used_to_buy * self.fee
                self.fee_paid_cash = self.fee_paid * self.price
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_bought = (self.portfolio_value - self.fee_paid_cash) / self.trade_price
                self.holding += self.numb_bought
                self.short -= self.short_used_to_buy
            else:
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_bought = (self.cash - self.slippage_cash) / self.price
                self.holding += self.numb_bought
                self.cash -= self.price * self.numb_bought

        elif self.position == "short":
            self.short_price = self.price
            if self.prevpos == "long":
                self.long_used_to_short = self.holding
                self.fee_paid = self.long_used_to_short * self.fee
                self.fee_paid_cash = self.fee_paid * self.price
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_short = (self.portfolio_value + self.fee_paid_cash) / self.price
                self.short += self.numb_short
                self.holding -= self.long_used_to_short
            else:
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_short = self.cash / self.price
                self.short += self.numb_short
                self.cash -= self.price * self.numb_short

        elif self.position == 'cash':
            if self.prevpos == "long":
                self.numb_holding_sold = self.holding
                self.fee_paid = self.numb_holding_sold * self.fee
                self.fee_paid_cash = self.fee_paid * self.price
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_cash_bought = (self.portfolio_value - self.fee_paid_cash)
                self.cash += self.numb_cash_bought
                self.holding -= self.numb_holding_sold
            elif self.prevpos == "short":
                self.numb_short_sold = self.short
                self.fee_paid = self.numb_short_sold * self.fee
                self.fee_paid_cash = self.fee_paid * self.price
                self.price_paid = (self.price * self.slippage)
                self.slippage_paid = self.price_paid - self.price
                self.slippage_cash = self.slippage_paid * self.price
                self.numb_cash_bought = (self.portfolio_value - self.fee_paid_cash)
                self.cash += self.numb_cash_bought
                self.short -= self.numb_short_sold

    def update_values(self):
        """
        Update the values for the current period.
        """
        # buy and hold from day 1: Calculate value for each period based on volume from day 1
        self.compare_hold_val = self.compare_holding * float(self.price)
        self.portfolio_value = self.cash + (self.holding * float(self.price)) + (self.short * (float(self.short_price) + (float(self.short_price) - float(self.price))))

        self.price_values.append(self.price)
        self.portfolio_values.append(self.portfolio_value)
        self.cash_values.append(self.cash)
        self.holding_values.append(self.holding)
        self.short_values.append(self.short)
        self.compare_hold_values.append(self.compare_hold_val)
        self.hold_period_values.append(self.hold_period)
        self.trade_values.append(self.trade_flg)
        self.signal_values.append(self.trade)
        self.trade_prices.append(self.trade_price)
        self.short_prices.append(self.short_price)
        self.fee_values.append(self.fee_paid)
        self.fee_cash_values.append(self.fee_paid_cash)
        self.price_paid_values.append(self.price_paid)
        self.slippage_values.append(self.slippage_cash)
        self.position_values.append(self.position)
        self.stop_loss_values.append(self.stop_loss)
        self.take_profit_values.append(self.take_profit)

        self.trade_flg = 0
        self.prevpos = self.position


#########################################################################################
#########################################################################################
#########################################################################################
