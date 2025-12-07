import pandas as pd
import yfinance as yf


def _normalise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ensure OHLCV columns are simple string names, even if yfinance returns
    tuples or a MultiIndex.
    """
    cols = []

    # Handle both plain Index and MultiIndex / tuple style columns
    for c in df.columns:
        # If it's a tuple like ('Open',) or ('Open', 'AAPL'), take the first element
        if isinstance(c, tuple):
            c = c[0]
        cols.append(str(c))

    df = df.copy()
    df.columns = cols
    return df


def download_price_data(
    symbol: str,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download OHLCV data for a symbol using yfinance.

    Parameters
    ----------
    symbol : str
        Ticker symbol understood by yfinance (e.g. '^GSPC', 'GBPUSD=X').
    start : str
        Start date in 'YYYY-MM-DD' format.
    end : str | None
        End date. If None, yfinance uses today's date.
    interval : str
        Bar interval (e.g. '1d', '1h', '4h').

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by datetime with columns:
        ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'].
    """
    df = yf.download(
        symbol,
        start=start,
        end=end,
        interval=interval,
        auto_adjust=False,
        progress=False,
        # Just to be explicit; some versions default to group_by='column'
        group_by="column",
    )

    if df.empty:
        raise ValueError(f"No data returned for {symbol} with interval={interval}")

    df = _normalise_columns(df)

    # Title-case and select expected columns if they exist
    df.columns = [c.title() for c in df.columns]

    # Some symbols may not have all columns; filter by what's actually there
    wanted = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    existing = [c for c in wanted if c in df.columns]
    df = df[existing]

    df = df.dropna()
    return df
