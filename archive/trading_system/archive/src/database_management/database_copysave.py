import sqlite3
import pandas as pd


#########################################################################################
#########################################################################################
#########################################################################################


# This is a Python class called Database that represents a database and provides methods for interacting with it. The class takes three arguments in its constructor:
    # df: a Pandas DataFrame that contains data that can be written to or read from the database
    # db: a string representing the path to the database file
    # table_name: a string representing the name of the table in the database

# The class has three methods:
    # copy_table: creates a copy of the table stock_prices in the database and saves it with the name specified by self.table_name.
    # save_historic: writes the data from self.df to a temporary table in the database, then overwrites the existing self.table_name table with the data from the temporary table, and finally deletes the temporary table.
    # read_table: reads the data from the table specified by from_table and stores it in self.df.
    # Each of the methods establishes a connection to the database, performs the desired operation, and then closes the connection when finished.


#########################################################################################
#########################################################################################
#########################################################################################


class Database:
    """
    This class represents a database and provides methods for interacting with it.

    Attributes:
    df (pandas.DataFrame): a DataFrame that contains data that can be written to or read from the database
    db (str): a string representing the path to the database file
    table_name (str): a string representing the name of the table in the database

    Methods:
    copy_table: creates a copy of the table 'stock_prices' in the database and saves it with the name specified by 'self.table_name'.
    save_historic: writes the data from 'self.df' to a temporary table in the database, then overwrites the existing 'self.table_name' table with the data from the temporary table, and finally deletes the temporary table.
    read_table: reads the data from the table specified by 'from_table' and stores it in 'self.df'.
    """

    def __init__(self, df, db, table_name):
        self.df = df
        self.db = db
        self.table_name = table_name

    def copy_table(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Create a copy of the 'stock_prices' table
            cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name} AS SELECT * FROM stock_prices")

            # Commit the changes to the database
            conn.commit()

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

    def read_table(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Retrieve the data from the table
            cursor.execute(f"SELECT * FROM {self.table_name}")
            rows = cursor.fetchall()

            # Create the column names for the DataFrame
            column_names = [column[0] for column in cursor.description]

            # Create the DataFrame
            self.df = pd.DataFrame(rows, columns=column_names)

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

        return self.df

    def save_finviz_tickers(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            # Create the table
            cursor.execute('''CREATE TABLE IF NOT EXISTS temp (
                                                                ticker text,
                                                                company text,
                                                                sector text,
                                                                industry text,
                                                                country text,
                                                                market_cap float,
                                                                PE float,
                                                                price float,
                                                                change float,
                                                                volume float

                                                                )''')

            # Iterate through the rows of the DataFrame and insert the data into the table
            for index, row in self.df.iterrows():
                cursor.execute('''INSERT INTO temp VALUES (?,?,?,?,?,?,?,?,?,?)''', row)

            # Commit the changes to the database
            conn.commit()

            # Delete the existing 'stock_prices_copy' table
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

            # Create a new 'stock_prices_copy' table
            cursor.execute(f'''CREATE TABLE {self.table_name} AS SELECT * FROM temp''')

            # Commit the changes to the database
            conn.commit()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            print(f'changes successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

    def save_historic_yahoo(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            # Create the table
            cursor.execute('''CREATE TABLE IF NOT EXISTS temp (
                                                                date text, 
                                                                open float,
                                                                high float,
                                                                low float,
                                                                close float,
                                                                adj_close float,
                                                                volume float,
                                                                ticker text
                                                                )''')

            # Iterate through the rows of the DataFrame and insert the data into the table
            for index, row in self.df.iterrows():
                cursor.execute('''INSERT INTO temp VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', (row['dt'], row['Open'], row['High'], row['Low'], row['Close'], row['Adj Close'], row['Volume'], row['ticker']))

            # Commit the changes to the database
            conn.commit()

            # Delete the existing 'stock_prices_copy' table
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

            # Create a new 'stock_prices_copy' table
            cursor.execute(f'''CREATE TABLE {self.table_name} AS SELECT * FROM temp''')

            # Commit the changes to the database
            conn.commit()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            print(f'changes successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

    def save_backtest(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)

            cursor = conn.cursor()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            cursor.execute('''CREATE TABLE IF NOT EXISTS temp (
                                            price_values FLOAT,
                                            trade_values FLOAT,
                                            signal_values TEXT,
                                            position_values TEXT,
                                            portfolio_values FLOAT,
                                            compare_hold_values FLOAT,
                                            trade_prices FLOAT,
                                            short_prices FLOAT,
                                            cash_values FLOAT,
                                            holding_values FLOAT,
                                            short_values FLOAT,
                                            hold_period_values FLOAT,
                                            fee_values FLOAT,
                                            fee_cash_values FLOAT,
                                            slippage_values FLOAT,
                                            price_paid_values FLOAT,
                                            stop_loss_values FLOAT,
                                            take_profit_values FLOAT,
                                            portfolio_return FLOAT,
                                            portfolio_cumulative FLOAT,
                                            portfolio_high FLOAT,
                                            portfolio_drawdown FLOAT,
                                            asset_return FLOAT,
                                            asset_cumulative FLOAT,
                                            asset_high FLOAT,
                                            asset_drawdown FLOAT,
                                            PeriodReturn_portfolio FLOAT,
                                            PeriodReturn_hold FLOAT)''')

            # Iterate through the rows of the dataframe and insert the values into the table
            for index, row in self.df.iterrows():
                cursor.execute('''INSERT INTO temp VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''',
                    (row['price_values'], row['trade_values'], row['signal_values'], row['position_values'],
                     row['portfolio_values'], row['compare_hold_values'],
                     row['trade_prices'], row['short_prices'], row['cash_values'], row['holding_values'],
                     row['short_values'], row['hold_period_values'], row['fee_values'], row['fee_cash_values'],
                     row['slippage_values'], row['price_paid_values'], row['stop_loss_values'],
                     row['take_profit_values'],
                     row['portfolio_return'], row['portfolio_cumulative'],
                     row['portfolio_high'], row['portfolio_drawdown'], row['asset_return'], row['asset_cumulative'],
                     row['asset_high'], row['asset_drawdown'], row['PeriodReturn_portfolio'], row['PeriodReturn_hold']))
            # Commit the changes to the database
            conn.commit()

            # Delete the existing 'stock_prices_copy' table
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

            # Create a new 'stock_prices_copy' table
            cursor.execute(f'''CREATE TABLE {self.table_name} AS SELECT * FROM temp''')

            # Commit the changes to the database
            conn.commit()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            print(f'changes successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

    def save_historic_paper_ig(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            # Create the table
            cursor.execute('''CREATE TABLE IF NOT EXISTS temp (
                                                                date text, 
                                                                bid_Open float,
                                                                bid_High float,
                                                                bid_Low float,
                                                                bid_Close float,
                                                                ask_Open float,
                                                                ask_High float,
                                                                ask_Low float,
                                                                ask_Close float,
                                                                last_Volume float
                                                                )'''
                           )
            # Iterate through the rows of the DataFrame and insert the data into the table
            for index, row in self.df.iterrows():
                cursor.execute('''INSERT INTO temp VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                               (row['date'], row['bid_Open'], row['bid_High'], row['bid_Low'],
                                row['bid_Close'], row['ask_Open'], row['ask_High'], row['ask_Low'],
                                row['ask_Close'], row['last_Volume']))
            # Commit the changes to the database
            conn.commit()

            # Delete the existing 'stock_prices_copy' table
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

            # Create a new 'stock_prices_copy' table
            cursor.execute(f'''CREATE TABLE {self.table_name} AS SELECT * FROM temp''')

            # Commit the changes to the database
            conn.commit()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            print(f'Successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()

    def save_dataprep(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            # Create the table
            cursor.execute('''CREATE TABLE IF NOT EXISTS temp ( 
                                                                date text,
                                                                close float, 
                                                                vol float,
                                                                short_sma float,
                                                                long_sma float,
                                                                signal_sma float,
                                                                short_ema float,
                                                                long_ema float,
                                                                signal_ema float,
                                                                up_band float,
                                                                mind_band float,
                                                                low_band float,
                                                                rsi float,
                                                                macd float,
                                                                macdsignal float,
                                                                macdhist float,
                                                                roc float

                                                                )''')

            # Iterate through the rows of the DataFrame and insert the data into the table
            for index, row in self.df.iterrows():
                cursor.execute('''INSERT INTO temp VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)''', row)

            # Commit the changes to the database
            conn.commit()

            # Delete the existing 'stock_prices_copy' table
            cursor.execute(f"DROP TABLE IF EXISTS {self.table_name}")

            # Create a new 'stock_prices_copy' table
            cursor.execute(f'''CREATE TABLE {self.table_name} AS SELECT * FROM temp''')

            # Commit the changes to the database
            conn.commit()

            # Delete the existing temp table
            cursor.execute(f"DROP TABLE IF EXISTS temp")

            # Commit the changes to the database
            conn.commit()

            print(f'changes successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred: {e}')

        finally:
            # Close the connection
            conn.close()