import logging
import yfinance as yf
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

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
    Fetches price data for multiple tickers concurrently.

    Parameters:
    - tickers (List[str]): List of ticker symbols.
    - start_date (str): Start date in 'YYYY-MM-DD' format.
    - end_date (str): End date in 'YYYY-MM-DD' format.

    Returns:
    - crypto_data_dict (Dict[str, pd.DataFrame]): Dictionary mapping ticker symbols to their price data DataFrames.
    """
    crypto_data_dict = {}
    with ThreadPoolExecutor(max_workers=min(10, len(tickers))) as executor:
        future_to_ticker = {executor.submit(fetch_price, ticker, start_date, end_date): ticker for ticker in tickers}
        for future in as_completed(future_to_ticker):
            ticker = future_to_ticker[future]
            try:
                crypto_data_dict[ticker] = future.result()
                logging.info(f"Data fetched successfully for {ticker}.")
            except Exception as e:
                logging.error(f"Error fetching data for {ticker}: {e}")

    return crypto_data_dict

def fetch_price(pair: str, start: str, end: str) -> pd.DataFrame:
    """
    Fetches historical daily price and volume data for a given ticker.

    Parameters:
    - pair (str): The ticker symbol.
    - start (str): The start date for the query in 'YYYY-MM-DD' format.
    - end (str): The end date for the query in 'YYYY-MM-DD' format.

    Returns:
    - df (pd.DataFrame): DataFrame containing the Open, High, Low, Close, and Volume data.
    """
    logging.info(f"Fetching data for {pair} from {start} to {end}.")

    # Download the data from Yahoo Finance
    df = yf.download(pair, start=start, end=end)

    # Check if data was retrieved successfully
    if df.empty:
        logging.warning(f"No data fetched for {pair}.")
        raise ValueError(f"No data fetched for {pair} using yfinance.")

    # Select only relevant columns for price and volume
    df = df[['Open', 'High', 'Low', 'Close', 'Volume']]

    # Handle missing values (e.g., filling NaNs or dropping them)
    df.fillna(method='ffill', inplace=True)  # Forward fill missing values
    df.dropna(inplace=True)  # Drop remaining rows with missing values if any

    logging.info(f"Data for {pair} fetched and processed successfully.")

    return df