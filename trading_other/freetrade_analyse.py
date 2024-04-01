import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from pandas_datareader._utils import RemoteDataError
import yfinance as yf
from collections import OrderedDict

#########################################################################################
#########################################################################################
#########################################################################################


portfolio = {
    'AMC':
    {
        'holding_volume': 0.2648,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'IESU.L':
    {
        'holding_volume': 0.04,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'GOOG':
    {
        'holding_volume': 0.3808,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'LQGH.L':
    {
        'holding_volume': 7,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'VUTY.L':
    {
        'holding_volume': 2,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'VUTA.L':
    {
        'holding_volume': 2,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'BLND.L':
    {
        'holding_volume': 0.12,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'MPW':
    {
        'holding_volume': 5.4907,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'V':
    {
        'holding_volume': 0.4145,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'T':
    {
        'holding_volume': 6.497,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'MSFT':
    {
        'holding_volume': 0.6735,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'GHYG.L':
    {
        'holding_volume': 320,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'XOM':
    {
        'holding_volume': 2.2012,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'AMZN':
    {
        'holding_volume': 2.7564,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'SHEL.L':
    {
        'holding_volume': 0.09,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'SEDY.L':
    {
        'holding_volume': 0.22,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'CVX':
    {
        'holding_volume': 1.704,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'O':
    {
        'holding_volume': 4.931,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'AAPL':
    {
        'holding_volume': 2.5377,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'IDVY.L':
    {
        'holding_volume': 0.17,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'BGEU.L':
    {
        'holding_volume': 338,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'VHYL.L':
    {
        'holding_volume': 100,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'INRG.L':
    {
        'holding_volume': 0.52,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'GME':
    {
        'holding_volume': 96.2292,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    },

    'IUSA.L':
    {
        'holding_volume': 1.28,
        'type': 'Equities',
        'region': 'US',
        'category': 'Single'
    }
}

etf = ['IUSA.L'
            ,'INRG.L'
            ,'VHYL.L'
            ,'IESU.L'
            # ,'VWRL.L'
]

single = ['AAPL'
            ,'GME'
            ,'XOM'
            ,'V'
]

reit = ['O'
        ,'BLND.L'
]

bond = ['LQGH.L'
        ,'GHYG.L'
        ,'VUTA.L'
        ,'VUTY.L'
]

tickers = etf + single + reit + bond
new_portfolio = OrderedDict((k, portfolio[k]) for k in tickers if k in portfolio)


#########################################################################################
#########################################################################################
#########################################################################################


class Analysis:
    def __init__(self, start, end, tickers):
        self.start = start
        self.end = end
        self.tickers = tickers
        self.data = pd.DataFrame

    def run(self):
        # self.tickers = self.df.ticker.tolist()
        self.get_data()
        self.df = self.data.pivot_table(index='dt', columns='ticker', values='Close').dropna()

        # self.correlation()

    def correlation(self):
        corr_matrix = self.df.corr()
        print(corr_matrix)

        sns.color_palette("vlag")
        sns.heatmap(corr_matrix, annot=True)
        plt.show()

    def get_data(self):
        # tickers = get_yahoo_tickers()
        for count, ticker in enumerate(self.tickers):
            try:
                df = yf.download([ticker], start=self.start, end=self.end, progress=False)
                df['ticker'] = ticker
                df['dt'] = df.index.astype(str)

                if self.data.empty:
                    self.data = df[['dt','ticker','Close']]
                else:
                    # self.data = self.data.join(df, how='outer')
                    self.data = pd.concat([self.data, df[['dt','ticker','Close']]], ignore_index=True)
                if count % 1 == 0:
                    print(count)
                    print(ticker)

            except KeyError:
                print('key error {}'.format(ticker))
                continue

            except RemoteDataError:
                print('remote error {}'.format(ticker))
                continue

        print('Process: Data Extract Complete.')
        return self.data


class Rebalance:
    def __init__(self, tickers, historic):
        self.tickers = tickers
        self.hist = historic
        self.holdings_volume = np.nan
        self.holdings_value = np.nan
        self.holdings_volumes = []
        self.holdings_values = []

    def run(self):
        self.current_portfolio()

    def current_portfolio(self):
        for ticker in self.tickers.keys():
            self.prices = self.hist[-1:]
            self.holdings_volume = self.tickers[ticker]['holding_volume']
            self.holdings_value = self.tickers[ticker]['holding_volume'] * self.prices[ticker].values
            self.holdings_volumes.append(self.holdings_volume)
            self.holdings_values.append(self.holdings_value)

        self.portfolios = pd.DataFrame({'ticker': list(self.tickers.keys()), 'holdings_volumes': list(self.holdings_volumes), 'holding_values': list(self.holdings_values)})
        self.portfolios['perc'] = self.portfolios['holding_values'].apply(lambda x: x / self.portfolios['holding_values'].sum())


class Efficientfrontier:
    def __init__(self, full_portfolio, subset_tickers, historic, holding, scn, full=True):
        if full:
            self.tickers = full_portfolio
        else:
            self.tickers = subset_tickers
        self.scn = scn

        self.hist = historic
        self.holding = holding

        self.portfolios = pd.DataFrame
        self.df_weights = pd.DataFrame
        self.prices = pd.DataFrame
        self.weight_list = []
        self.portfolio_returns = []
        self.portfolio_volatilities = []

    def run(self):
        self.logreturns()
        self.returns()
        self.optimal_portfolio()
        self.curr_portfolio()
        self.plot()

    def logreturns(self):
        self.log_returns = np.log(self.hist/self.hist.shift(1))

    def returns(self):
        i = 0
        for x in range(self.scn):
            i += 1
            print(f"sim: {i}  ({round((i / self.scn) * 100, 1)}%)")
            self.weights = np.random.random(len(self.tickers))
            self.weights /= np.sum(self.weights)
            self.weight_list.append(self.weights)

            self.portfolio_returns.append(np.sum(self.weights * self.log_returns.mean()) * 250)
            self.portfolio_volatilities.append(np.sqrt(np.dot(self.weights.T, np.dot(self.log_returns.cov() * 250, self.weights))))

        self.portfolio_returns = np.array(self.portfolio_returns)
        self.portfolio_volatilities = np.array(self.portfolio_volatilities)
        self.optimal_portfolios = pd.DataFrame({'Return': self.portfolio_returns, 'Volatility': self.portfolio_volatilities})
        self.df_weights = pd.DataFrame(self.weight_list)

    def optimal_portfolio(self):
        self.min_vol_port = self.optimal_portfolios.iloc[self.optimal_portfolios['Volatility'].idxmin()]
        rf = 0.01  # risk factor
        self.optimal_risky_port = self.optimal_portfolios.iloc[((self.optimal_portfolios['Return'] - rf) / self.optimal_portfolios['Volatility']).idxmax()]
        self.optimal_weights = self.df_weights.iloc[((self.optimal_portfolios['Return'] - rf) / self.optimal_portfolios['Volatility']).idxmax()]
        self.optimal_weights.index = self.tickers

    def curr_portfolio(self):
        self.actual_returns = sum([x * y for x, y in zip(self.holding, self.log_returns.mean())]) * 250
        self.actual_volatilities = np.sqrt(np.dot(self.holding.T, np.dot(self.log_returns.cov() * 250, self.holding)))

    def plot(self):
        self.optimal_portfolios.plot(x='Volatility', y='Return', kind='scatter', figsize=(15,10))
        plt.scatter(self.min_vol_port[1], self.min_vol_port[0], color='r', marker='*', s=500)
        plt.scatter(self.optimal_risky_port[1], self.optimal_risky_port[0], color='g', marker='*', s=500)
        plt.scatter(self.actual_volatilities, self.actual_returns, color='y', marker='*', s=500)

        plt.xlabel('Expected Volatility')
        plt.ylabel('Expected Return')
        plt.show()


#########################################################################################
#########################################################################################
#########################################################################################

# run for full or partial tickers
run = 'full'
if run == 'full':
    portfolio_dict = portfolio
elif run == 'partial':
    portfolio_dict = new_portfolio

an = Analysis('2020-01-01', '2023-07-01', portfolio_dict)
an.run()

rb = Rebalance(portfolio_dict, an.df)
rb.run()

# print("rb.portfolio :")
# print(f"{rb.portfolios}")

scn = 500
ef = Efficientfrontier(portfolio, portfolio_dict, an.df, rb.portfolios['perc'], scn, False)
ef.run()

print("min volatility portfolio")
print(ef.min_vol_port)

print("optimal volatility portfolio")
print(ef.optimal_risky_port)

print("optimal weights")
print(ef.optimal_weights)

print("current weights")
print(ef.holding)

ef.optimal_weights.to_csv('test.csv')
