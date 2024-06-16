from trading_ig.rest import IGService, ApiExceededException
from trading_ig.config import config
from tenacity import Retrying, wait_exponential, retry_if_exception_type
import pandas as pd
from pytickersymbols import PyTickerSymbols


#########################################################################################
#########################################################################################
#########################################################################################

# v1.0
class IGConnection:
    def __init__(self, username, password, api_key, acc_type, acc_number):
        self.username = username
        self.password = password
        self.api_key = api_key
        self.acc_type = acc_type
        self.acc_number = acc_number

        self.retryer = Retrying(wait=wait_exponential(), retry=retry_if_exception_type(ApiExceededException))
        self.ig_service = IGService(
            self.username,
            self.password,
            self.api_key,
            self.acc_type,
            acc_number=self.acc_number,
            retryer=self.retryer,
            use_rate_limiter=True
        )
        self.ig_service.create_session(version='3')

    def get_session(self):
        return self.ig_service

    def close_session(self):
        self.ig_service.close_session()

    def display_top_level_nodes(self):
        response = self.ig_service.fetch_top_level_navigation_nodes()
        df = response['nodes']
        for record in df.to_dict('records'):
            print(f"{record['name']} [{record['id']}]")

    def display_all_epics(self):
        response = self.ig_service.fetch_top_level_navigation_nodes()
        df = response['nodes']
        for record in df.to_dict('records'):
            print(f"{record['name']} [{record['id']}]")
            # display_epics_for_node(record['id'], space='  ', ig_service=self.ig_service)

    def display_epics_for_node(self, node_id, space, ig_service):
        response = ig_service.fetch_market_navigation_node_children(node_id)
        df = response['nodes']
        for record in df.to_dict('records'):
            print(f"{space}{record['name']} [{record['id']}]")
            # if record['nodes'] is not None:
                # display_epics_for_node(record['id'], space + '  ', ig_service)

    def get_yahoo_tickers(self):
        stock_data = PyTickerSymbols()
        uk_stocks = stock_data.get_ftse_100_london_yahoo_tickers()
        sp100_yahoo = stock_data.get_sp_100_nyc_yahoo_tickers()
        df = pd.DataFrame(uk_stocks, columns=['symbol']).sort_values('symbol')
        df2 = df[df['symbol'].str.contains(".L")]
        print(df2)
        return df2

    def get_epic_from_ig(self, ticker):
        results = self.ig_service.search_markets(ticker)
        epic = results.iat[0, 0]
        return epic

    def historic_prices(self, epic, resolution, num_points):
        response = self.ig_service.fetch_historical_prices_by_epic_and_num_points(epic, resolution, num_points)
        data = response['prices']
        data.columns = ['_'.join(col) for col in data.columns.values]
        data.drop(['last_Open', 'last_High', 'last_Low', 'last_Close'], 1, inplace=True)
        data['date'] = data.index.date
        # df_ask = response['prices']['ask']
        # df_bid = response['prices']['bid']
        # df_vol = response['prices']['last']['Volume']
        return data


#########################################################################################
#########################################################################################
#########################################################################################

# v0.1
# ### connect to IG API
# def get_session():
#     retryer = Retrying(wait=wait_exponential(), retry=retry_if_exception_type(ApiExceededException))
#     ig_service = IGService(
#         config.username,
#         config.password,
#         config.api_key,
#         config.acc_type,
#         acc_number=config.acc_number,
#         retryer=retryer,
#         use_rate_limiter=True)
#     ig_service.create_session(version='3')
#     return ig_service
#
#
# def display_top_level_nodes():
#     ig_service = get_session()
#
#     response = ig_service.fetch_top_level_navigation_nodes()
#     df = response['nodes']
#     for record in df.to_dict('records'):
#         print(f"{record['name']} [{record['id']}]")


# def display_all_epics():
#     ig_service = get_session()
#     response = ig_service.fetch_top_level_navigation_nodes()
#     df = response['nodes']
#     for record in df.to_dict('records'):
#         print(f"{record['name']} [{record['id']}]")
#         display_epics_for_node(record['id'], space='  ', ig_service=ig_service)


# def display_epics_for_node(node_id=0, space='', ig_service=None):
#     if ig_service is None:
#         ig_service = get_session()
#
#     sub_nodes = ig_service.fetch_sub_nodes_by_node(node_id)
#
#     if sub_nodes['nodes'].shape[0] != 0:
#         rows = sub_nodes['nodes'].to_dict('records')
#         for record in rows:
#             print(f"{space}{record['name']} [{record['id']}]")
#             display_epics_for_node(record['id'], space=space + '  ', ig_service=ig_service)
#
#     if sub_nodes['markets'].shape[0] != 0:
#         cols = sub_nodes['markets'].to_dict('records')
#         for record in cols:
#             print(f"{space}{record['instrumentName']} ({record['expiry']}): {record['epic']}")


#########################################################################################
#########################################################################################
#########################################################################################


# def get_yahoo_tickers():
#     stock_data = PyTickerSymbols()
#     # uk_stocks = stock_data.get_stocks_by_index('FTSE 100')
#     uk_stocks = stock_data.get_ftse_100_london_yahoo_tickers()
#     sp100_yahoo = stock_data.get_sp_100_nyc_yahoo_tickers()
#     df = pd.DataFrame(uk_stocks, columns=['symbol']).sort_values('symbol')
#     df2 = df[df['symbol'].str.contains(".L")]
#     print(df2)
#     return df2
#
#
# def get_epic_from_ig(ticker):
#     # Retrieve EPIC from IG API
#     ig_service = get_session()
#     ticker = 'AAF.L'
#     results = ig_service.search_markets(ticker)
#     epic = results.iat[0, 0]
#     return epic
#
#
# def historic_prices(epic, resolution, num_points):
#     ig_service = get_session()
#     response = ig_service.fetch_historical_prices_by_epic_and_num_points(epic, resolution, num_points)
#     data = response['prices']
#
#     df_ask = response['prices']['ask']
#     df_bid = response['prices']['bid']
#     df_vol = response['prices']['last']['Volume']
#     data.columns = ['_'.join(col) for col in data.columns.values]
#     data.drop(['last_Open', 'last_High', 'last_Low', 'last_Close'], 1, inplace=True)
#     data['date'] = data.index.date
#     return data, df_ask, df_bid, df_vol
