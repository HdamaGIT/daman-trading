import pandas as pd
import talib

def calculate_indicators_for_ticker(df):
    # Existing SMA and EMA settings
    short_period = 20
    long_period = 200
    rsi_period = 14

    # Calculate SMAs
    df['short_sma'] = df['Close'].rolling(window=short_period).mean()
    df['long_sma'] = df['Close'].rolling(window=long_period).mean()

    # Calculate EMAs
    df['short_ema'] = talib.EMA(df['Close'].values, timeperiod=short_period)
    df['long_ema'] = talib.EMA(df['Close'].values, timeperiod=long_period)

    # Calculate RSI
    df['RSI'] = talib.RSI(df['Close'].values, timeperiod=rsi_period)

    # Bollinger Bands
    upperband, middleband, lowerband = talib.BBANDS(df['Close'].values, timeperiod=short_period, nbdevup=2, nbdevdn=2, matype=0)
    df['upperband'] = upperband
    df['middleband'] = middleband
    df['lowerband'] = lowerband

    # MACD
    macd, macdsignal, macdhist = talib.MACD(df['Close'].values, fastperiod=12, slowperiod=26, signalperiod=9)
    df['macd'] = macd
    df['macdsignal'] = macdsignal
    df['macdhist'] = macdhist

    # Stochastic Oscillator
    slowk, slowd = talib.STOCH(df['High'].values, df['Low'].values, df['Close'].values, fastk_period=5, slowk_period=3, slowk_matype=0, slowd_period=3, slowd_matype=0)
    df['slowk'] = slowk
    df['slowd'] = slowd

    return df


def calculate_indicators(data):
    # Process each ticker's data
    for ticker, ticker_data in data.items():
        df = pd.DataFrame(ticker_data)

        # Ensure 'date' column is in the correct format and set as index
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])
            df.set_index('date', inplace=True)

        # Calculate indicators for this ticker
        df = calculate_indicators_for_ticker(df)

        # Update the original dictionary with the modified DataFrame
        data[ticker] = df.reset_index().to_dict('list')

    return data
