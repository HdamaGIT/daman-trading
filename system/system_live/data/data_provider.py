# system_live/data/data_provider.py

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Protocol, Optional

import pandas as pd


class MarketDataProvider(Protocol):
    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        lookback: int,
        now: Optional[datetime] = None,
    ) -> pd.DataFrame:
        ...


@dataclass
class DummyProvider:
    """
    Dummy provider that generates synthetic OHLCV data.
    Useful for testing the system wiring without real data.
    """

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        lookback: int,
        now: Optional[datetime] = None,
    ) -> pd.DataFrame:
        import numpy as np

        if now is None:
            now = datetime.utcnow()

        # crude mapping of timeframe -> bar length
        tf_map = {
            "4h": timedelta(hours=4),
            "1h": timedelta(hours=1),
            "1d": timedelta(days=1),
        }
        delta = tf_map.get(timeframe, timedelta(hours=4))

        dates = [now - i * delta for i in range(lookback)][::-1]
        prices = np.cumsum(np.random.normal(0, 1, size=lookback)) + 100.0

        df = pd.DataFrame(
            {
                "open": prices + np.random.normal(0, 0.2, size=lookback),
                "high": prices + np.abs(np.random.normal(0.5, 0.3, size=lookback)),
                "low": prices - np.abs(np.random.normal(0.5, 0.3, size=lookback)),
                "close": prices,
                "volume": np.random.randint(1_000, 10_000, size=lookback),
            },
            index=pd.DatetimeIndex(dates, name="timestamp"),
        )
        return df


@dataclass
class YahooFinanceProvider:
    """
    Yahoo Finance provider, using yfinance.
    NOTE: yfinance must be installed in your environment.
    """

    def get_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        lookback: int,
        now: Optional[datetime] = None,
    ) -> pd.DataFrame:
        import yfinance as yf

        # Map timeframe to yfinance interval
        interval_map = {
            "1h": "60m",
            "4h": "4h",
            "1d": "1d",
        }
        interval = interval_map.get(timeframe, "4h")

        if now is None:
            now = datetime.utcnow()
        # Rough start date: lookback * timeframe length
        # we’ll just pull a bit more and trim
        period = "60d"  # safe default; you can refine

        data = yf.download(
            tickers=symbol,
            period=period,
            interval=interval,
            progress=False,
        )

        if data.empty:
            return data

        data = data.rename(
            columns={
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Adj Close": "adj_close",
                "Volume": "volume",
            }
        )

        if len(data) > lookback:
            data = data.iloc[-lookback:]

        data.index = data.index.tz_localize(None)
        data.index.name = "timestamp"
        return data


def get_market_data_provider(name: str) -> MarketDataProvider:
    if name == "yahoo":
        return YahooFinanceProvider()
    elif name == "dummy":
        return DummyProvider()
    else:
        raise ValueError(f"Unknown data provider: {name}")
