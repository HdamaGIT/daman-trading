import yfinance as yf


def price_data(tickers, start_date, end_date):
    crypto_data_dict = {}
    for ticker in tickers:
        crypto_data_dict[ticker] = fetch_price(ticker, start_date, end_date)
    return crypto_data_dict


def fetch_price(pair, start, end):
    """
    Fetches the historical daily price and volume data for a cryptocurrency pair.

    Parameters:
    - pair (str): The cryptocurrency pair symbol, e.g., 'BTC-GBP'.
    - start (str): The start date for the query in 'YYYY-MM-DD' format.
    - end (str): The end date for the query in 'YYYY-MM-DD' format.

    Returns:
    - df (DataFrame): Contains the Open, High, Low, Close prices and Volume.
    """
    # Download the data from Yahoo Finance
    df = yf.download(pair, start=start, end=end)

    # Check if data was retrieved successfully
    if df.empty:
        raise ValueError(f"No data fetched for {pair} using yfinance.")

    # Select only relevant columns for price and volume
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Handle missing values if necessary (e.g., fillna or dropna)
    # df.dropna(inplace=True)  # Uncomment if you want to drop rows with missing values

    return df
