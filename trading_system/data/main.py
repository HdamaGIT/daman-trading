from .price_data import price_data


def data(tickers, start_date, end_date):

    data_price = price_data(tickers, start_date, end_date)

    return data_price
