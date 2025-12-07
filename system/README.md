Regime-Aware Trend–Pullback Swing Trading System
This folder defines the logic, rules, and components of the swing trading system used in this project.
The system is designed for indices and FX, traded via spread betting, using semi-automated execution and a 4-hour timeframe.

1. Strategy Overview
This is a Regime-Aware Trend + Pullback swing trading strategy.
The system:
Identifies whether the market is Trending or Choppy
Enters trades only during strong trends
Uses mean-reverting pullbacks to achieve favourable entries
Applies ATR-based position sizing and exits
Generates low-frequency swing signals, suitable for manual execution in ~10–30 minutes per day
The strategy targets stable, repeatable behaviour in indices and FX markets.

2. Market Regime Classification
A regime is classified as TRENDING when:
ADX(20) > 20 (directional strength)
Price is above/below EMA50 (uptrend/downtrend structure)
(Optional) ATR% above its rolling median (sufficient volatility)
If any conditions fail → Regime = CHOP, and no trades are taken.

3. Trade Entry Rules
Uptrend (Long Setup)
Enter long when:
Regime = TRENDING (Uptrend)
Price pulls back to the EMA20
RSI(5) < 30 during pullback
Candle closes back above EMA20
ADX remains > 20
Signal = LONG ENTRY
Downtrend (Short Setup)
Enter short when:
Regime = TRENDING (Downtrend)
Price pulls back up to EMA20
RSI(5) > 70
Candle closes back below EMA20
ADX remains > 20
Signal = SHORT ENTRY

4. 4.Exit Rules
Stop-Loss
ATR(14) × 1.0 from entry
Placed beyond swing high/low
Take-Profit
Configurable; default behaviour:
1.5 × ATR target
OR
Exit on candle crossing the EMA20 against the position
OR
Exit at opposite Bollinger Band
Emergency Exit (Trend Failure)
Exit early if:
ADX < 18, or
Price closes across EMA50 in opposing direction
5. Position Sizing (Spread Betting Compatible)
position_size (£/point) =
    (risk_per_trade £) / (ATR_stop_distance × point_value)
Typical risk: 0.5–1.0% of equity per trade
ATR scaling automatically adapts to volatility
6. Timeframe & Assets
Primary Timeframe
4-hour (H4) — balanced responsiveness + low noise
Recommended Instruments
Indices:
NAS100, SPX500, FTSE100
FX Pairs:
GBP/USD, EUR/USD, USD/JPY
Trade 3–5 instruments to avoid overtrading.

7. Daily Workflow
Review regime state for each instrument
Identify pullback setups
Monitor for signal confirmation on candle close
Place trades manually if signal triggers
Update log/tracker
Manage exits and stops according to rules
Total time: 10–30 minutes per day
8. Purpose of This Folder
This directory contains:
Core strategy logic (regime filters, signals, exits)
Indicator implementations
Simulation/backtest modules
Configuration files
Utility functions for signal generation
It forms the basis for both backtesting and live semi-automated execution of the strategy.