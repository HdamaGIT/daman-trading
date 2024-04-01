from datetime import time
import pandas as pd


#########################################################################################
#########################################################################################
#########################################################################################

MARKET_OPEN = time(10, 30)
MARKET_OPEN_PLUS_ONE = time(11, 30)

class TradeAllocation:
    """
    This class represents a trading strategy that issues long and short signals based on RSI.
    It has a maximum number of trades it can execute and a trading window in hours.
    """

    def __init__(self, data, close, max_trades, trade_window):
        self.data = data.copy()  # create a copy of the data to avoid modifying the original dataframe
        self.data['date'] = pd.to_datetime(self.data['date'], errors='coerce')  # convert 'date' column to datetime
        self.close = close
        self.max_trades = max_trades
        self.trade_window = pd.Timedelta(hours=trade_window)
        self.positions = []
        self.trade_count = 0

    def run(self):
        self.generate_signals()
        self.risk_management(2, 5)
        self.data = self.get_signals()

    def generate_signals(self):
        """
        Generate long and short signals based on RSI, limiting the number of trades per day.
        """
        # Initialize the signal column to 'neutral'
        self.data['signal'] = 'neutral'

        # Keep track of the current day
        current_day = None

        # Iterate over the DataFrame by index (i.e., row by row)
        for i in range(1, len(self.data) - 1):
            # Reset trade_count and update current_day if a new day has started
            if self.data['date'][i].day != current_day:
                self.trade_count = 0
                current_day = self.data['date'][i].day

            # Define market open time as the first bar of the day (this bar typically represents the first hour of trading)
            is_market_open = pd.to_datetime(self.data['date'][i]).time() == time(10, 30)
            is_next_hour = pd.to_datetime(self.data['date'][i + 1]).time() == time(11, 30)

            # If market is open, it's the next hour, and we haven't exceeded the max number of trades
            if is_market_open and is_next_hour and self.trade_count < self.max_trades:
                # Define your indicators and conditions for going long or short
                # For instance, using RSI and Volume as sample indicators:
                if self.data['rsi'][i] < 30:
                    self.data.loc[i, 'signal'] = 'long'
                    self.trade_count += 1
                elif self.data['rsi'][i] > 70:
                    self.data.loc[i, 'signal'] = 'short'
                    self.trade_count += 1

    def get_signals(self):
        """
        Get a DataFrame with only the rows where a trade signal was generated.
        """
        # Create a new DataFrame containing only rows where a signal was generated
        signals_df = self.data[self.data['signal'] != 'neutral'].copy()

        return signals_df

    def risk_management(self, stop_loss_level, take_profit_level):
        """
        Set stop loss and take profit levels.
        """
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
