import pandas as pd
import yfinance as yf
from datetime import timedelta


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


def _max_chunk_days_for_interval(interval: str) -> int | None:
    """
    Return the maximum number of days Yahoo reliably supports in a single
    request for a given interval. None means 'no chunking needed'.
    """
    interval = interval.lower()

    # Daily / weekly / monthly can usually go back as far as you like
    if interval in ("1d", "5d", "1wk", "1mo", "3mo"):
        return None

    # Intraday intervals – Yahoo usually caps at ~730 days
    # We'll be conservative and use 700 days per chunk.
    return 700


def download_price_data(
    symbol: str,
    start: str = "2015-01-01",
    end: str | None = None,
    interval: str = "1d",
) -> pd.DataFrame:
    """
    Download OHLCV data for a symbol using yfinance, with automatic
    chunking for intraday intervals so that long lookback periods
    are still supported.

    Parameters
    ----------
    symbol : str
        Ticker symbol understood by yfinance (e.g. '^GSPC', 'GBPUSD=X').
    start : str
        Start date in 'YYYY-MM-DD' format.
    end : str | None
        End date. If None, uses today's date.
    interval : str
        Bar interval (e.g. '1d', '1h', '4h').

    Returns
    -------
    pd.DataFrame
        DataFrame indexed by datetime with columns:
        ['Open', 'High', 'Low', 'Close', 'Adj Close', 'Volume'].
    """
    start_dt = pd.to_datetime(start)
    end_dt = pd.to_datetime(end) if end is not None else pd.Timestamp.today()

    max_days = _max_chunk_days_for_interval(interval)

    if (max_days is None) or ((end_dt - start_dt).days <= max_days):
        # Single request is fine
        df = yf.download(
            symbol,
            start=start_dt,
            end=end_dt,
            interval=interval,
            auto_adjust=False,
            progress=False,
            group_by="column",
        )
    else:
        # Chunk the request into smaller date ranges
        frames: list[pd.DataFrame] = []
        chunk_start = start_dt
        delta = timedelta(days=max_days)

        while chunk_start < end_dt:
            chunk_end = min(chunk_start + delta, end_dt)

            df_chunk = yf.download(
                symbol,
                start=chunk_start,
                end=chunk_end,
                interval=interval,
                auto_adjust=False,
                progress=False,
                group_by="column",
            )

            if not df_chunk.empty:
                frames.append(df_chunk)

            # next chunk starts at the previous chunk_end
            chunk_start = chunk_end

        if not frames:
            raise ValueError(
                f"No data returned for {symbol} between {start_dt} and {end_dt} "
                f"with interval={interval}"
            )

        df = pd.concat(frames)
        # Remove any duplicate index rows that can occur at chunk boundaries
        df = df[~df.index.duplicated(keep="last")]

    if df.empty:
        raise ValueError(f"No data returned for {symbol} with interval={interval}")

    # Normalise and clean columns as before
    df = _normalise_columns(df)

    df.columns = [c.title() for c in df.columns]

    wanted = ["Open", "High", "Low", "Close", "Adj Close", "Volume"]
    existing = [c for c in wanted if c in df.columns]
    df = df[existing]

    df = df.dropna()
    return df