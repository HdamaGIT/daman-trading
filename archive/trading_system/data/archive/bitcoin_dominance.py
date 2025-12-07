import requests
from datetime import datetime


def fetch_historical_global_metrics(api_key, time_start, time_end, interval='daily', convert='USD'):
    """
    Fetches historical global cryptocurrency market metrics.

    Parameters:
    - api_key (str): CoinMarketCap API key.
    - time_start (str): Start timestamp (ISO 8601 format).
    - time_end (str): End timestamp (ISO 8601 format).
    - interval (str): Interval of time to return data points for.
    - convert (str): Currency symbol to convert market quotes into.

    Returns:
    - dict: Historical global metrics data.
    """
    url = 'https://pro-api.coinmarketcap.com/v1/global-metrics/quotes/historical'
    parameters = {
        'time_start': time_start,
        'time_end': time_end,
        'interval': interval,
        'convert': convert
    }
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': api_key,
    }

    response = requests.get(url, headers=headers, params=parameters)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch data: HTTP Status Code {response.status_code}")
        return None


# Example usage:
api_key = "9522382e-6f99-48cd-8f83-285dfef114d4"
time_start = '2021-01-01T00:00:00'
time_end = '2021-01-31T23:59:59'
interval = 'daily'

data = fetch_historical_global_metrics(api_key, time_start, time_end, interval)
if data:
    for quote in data["data"]["quotes"]:
        timestamp = quote["timestamp"]
        btc_dominance = quote.get("btc_dominance", "N/A")
        total_market_cap = quote["quote"]["USD"]["total_market_cap"]
        print(f"Timestamp: {timestamp}, BTC Dominance: {btc_dominance}, Total Market Cap: {total_market_cap}")

# Example usage


