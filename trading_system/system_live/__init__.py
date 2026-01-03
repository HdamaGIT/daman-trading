# system_live/__init__.py
"""
Live trading / signal execution trading_system.

This package is designed to:
- Periodically pull market data.
- Compute indicators for a chosen strategy.
- Generate entry and exit signals.
- Apply risk management & position sizing.
- Persist everything to a trade log (SQLite DB).
- Notify Discord via a pluggable notifier (placeholder for now).
"""