import pandas as pd
import yfinance as yf
from pandas_datareader._utils import RemoteDataError
import sqlite3
import requests
import datetime as dt
from datetime import timedelta, date, datetime
from datetime import date

#delete existing tables
#make new tables that start as far back as possible
#run this process to get all data up to today

class Process_update_historic:
    def __init__(self, interval, delta, start, end, db, table_name):
        self.interval = interval
        self.delta = delta
        self.start = start
        self.overall_start = start
        self.end = end

        self.db = db
        self.table_name = table_name

        self.df = pd.DataFrame
        self.df_fv = pd.DataFrame
        self.data = pd.DataFrame
        self.tickers = []

    def run(self):
        self.discord_notification('*Initial start*', self.interval, self.overall_start, self.end)
        self.read_current()
        self.check_current()
        self.read_tickers()

        delta = timedelta(days=self.delta)
        while self.start <= self.end:
            self.t_end = self.start + delta - timedelta(days=1)
            if self.t_end > self.end:
                self.t_end = self.end

            self.discord_notification('start', self.interval, self.start, self.t_end)
            self.get_data()
            self.update_db()
            self.discord_notification('complete', self.interval, self.start, self.t_end)

            self.start += delta

        self.discord_notification('final complete', self.interval, self.overall_start, self.end)

    def read_current(self):
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
            print(f'An error occurred while reading data: {e}')

        finally:
            # Close the connection
            conn.close()

        return self.df

    def check_current(self):
        self.df['date'] = pd.to_datetime(self.df['date'])
        max_date = self.df['date'].max()
        # self.start = max_date + timedelta(days=1)
        self.start = pd.to_datetime(max_date.floor('d') + timedelta(days=1))

    def read_tickers(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)
            cursor = conn.cursor()

            # Retrieve the data from the table
            cursor.execute(f"SELECT * FROM finviz_tickers")
            rows = cursor.fetchall()

            # Create the column names for the DataFrame
            column_names = [column[0] for column in cursor.description]

            # Create the DataFrame
            self.df_fv = pd.DataFrame(rows, columns=column_names)
            self.tickers = self.df_fv.ticker.tolist()

        except sqlite3.Error as e:
            print(f'An error occurred while reading finviz data: {e}')

        finally:
            # Close the connection
            conn.close()

    def get_data(self):
        for count, ticker in enumerate(self.tickers):
            try:
                df = yf.download(tickers=[ticker], interval=self.interval, start=self.start, end=self.t_end,
                                 progress=False)
                df['ticker'] = ticker
                df['dt'] = df.index.astype(str)
                df.rename(columns={'dt': 'date', 'Open': 'open', 'High': 'high', 'Low': 'low', 'Close': 'close', 'Adj Close': 'adj_close', 'Volume': 'volume'}, inplace=True)


                if self.data.empty:
                    self.data = df
                else:
                    # self.data = self.data.join(df, how='outer')
                    self.data = pd.concat([self.data, df], ignore_index=True)
                if count % 1 == 0:
                    print(count)
                    print(ticker)

            except KeyError:
                print('key error {}'.format(ticker))
                continue

            except RemoteDataError:
                print('remote error {}'.format(ticker))
                continue

    def update_db(self):
        try:
            # Connect to the database
            conn = sqlite3.connect(self.db)

            # Use the 'to_sql' function to append the DataFrame to the existing table
            self.data.to_sql(self.table_name, conn, if_exists='append', index=False)
            conn.commit()

            print(f'changes successfully committed to {self.table_name}!')

        except sqlite3.Error as e:
            print(f'An error occurred while reading data: {e}')

        finally:
            conn.close()

    @staticmethod
    def discord_notification(status, interval, start, end):
        message = f'{status}: {interval} Historic price data download process between {start} and {end}'
        WEBHOOK_URL = 'https://discord.com/api/webhooks/1055563087014547486/WxnXCRSiUvQYJNO0Ne-afYU_u_lG3xMBvxrKbTdsvYKspuvVvikGg4eTAkVXMVPPyfdU'
        data = {'content': message}
        response = requests.post(WEBHOOK_URL, json=data)


if __name__ == '__main__':
    db = '/Volumes/My AFP Volume/database.db'

    intervals = ['1d', '1h']
    # intervals = ['1m']

    for interval in intervals:
        start = datetime(2000, 1, 1)
        # today = dt.datetime.now().date()
        today = dt.datetime.now()
        end = today
        # end = date(2023, 1, )

        if interval == '1d':
            delta = 500
            table_name = 'data_historic_sp500_daily'

        elif interval == '1h':
            table_name = 'data_historic_sp500_hourly'
            delta = 60

        elif interval == '1m':
            table_name = 'data_historic_sp500_minutely'
            delta = 3

        puh = Process_update_historic(interval, delta, start, end, db, table_name)
        puh.run()
