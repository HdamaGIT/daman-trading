import logging
import yfinance as yf
import pandas as pd
from typing import List, Dict

def data(tickers: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """
    Main function to fetch price data for given tickers within a date range.

    Parameters:
    - tickers (List[str]): List of ticker symbols.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
    - data_price (Dict[str, pd.DataFrame]): Dictionary of DataFrames containing price data for each ticker.
    """
    data_price = price_data(tickers, start_date, end_date)
    return data_price

def price_data(tickers: List[str], start_date: str, end_date: str) -> Dict[str, pd.DataFrame]:
    """
    Fetches price data for multiple tickers sequentially.

    Parameters:
    - tickers (List[str]): List of ticker symbols.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
    - crypto_data_dict (Dict[str, pd.DataFrame]): Dictionary mapping ticker symbols to their price data DataFrames.
    """
    crypto_data_dict = {}
    for ticker in tickers:
        df = fetch_price(ticker, start_date, end_date)
        if df is not None:
            crypto_data_dict[ticker] = df
            logging.info(f"Data fetched successfully for {ticker}.")
        else:
            logging.error(f"Error fetching data for {ticker}. Skipping this ticker.")

    return crypto_data_dict

def fetch_price(pair: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetches the historical daily price and volume data for a cryptocurrency pair.

    Parameters:
    - pair (str): The cryptocurrency pair symbol, e.g., 'BTC-GBP'.
    - start (str): The start date for the query in 'YYYY-MM-DD' format.
    - end (str): The end date for the query in 'YYYY-MM-DD' format.

    Returns:
    - df (pd.DataFrame): Contains the Open, High, Low, Close prices, and Volume.
    """
    try:
        df = yf.download(pair, start=start, end=end)

        if df.empty:
            logging.error(f"No data fetched for {pair}. Data may not be available for this ticker.")
            return None

        # Select relevant columns
        df = df[['Open', 'High', 'Low', 'Close', 'Volume']].copy()

        # Handle missing data
        df.fillna(method='ffill', inplace=True)
        df.dropna(inplace=True)

        return df
    except Exception as e:
        logging.error(f"Error fetching data for {pair}: {e}")
        return None
