import datetime as dt
from datetime import date


#########################################################################################
#########################################################################################
#########################################################################################


def inputs():
    """
    Defines a set of input variables that can be used as inputs in other parts of the project.

    Returns:
        dict: A dictionary containing the input variables.

    Variables:
        version (str): A string representing the version of the algorithm being used.
        db (str): A string representing the name of a database.
        filepath (str): A string representing the file path for saving CSV files.
        filename_historic (str): A string representing the name of a CSV file for storing historic data.
        filename_analysis (str): A string representing the name of a CSV file for storing analysis data.
        filename_backtest (str): A string representing the name of a CSV file for storing backtest data.
        filename_montecarlo (str): A string representing the name of a CSV file for storing Monte Carlo simulation data.
        tickers (list): A list of strings representing ticker symbols for financial instruments.
        start (date): A date representing the start date for a period of time.
        today (date): The current date.
        end (date): A date representing the end date for a period of time.
        epic (str): A string representing the epic of a financial instrument.
        resolution (str): A string representing the resolution (e.g., daily, hourly) of data.
        num_points (int): An integer representing the number of data points.
        close (str): A string representing the name of a column in data for the close price.
        vol (str): A string representing the name of a column in data for volume.
        high (str): A string representing the name of a column in data for the high price.
        low (str): A string representing the name of a column in data for the low price.
        short (int): An integer representing the period for a short-term moving average.
        long (int): An integer representing the period for a long-term moving average.
        sl (float): A float representing the stop loss level for a trade.
        tp (float): A float representing the take profit level for a trade.
        cash (int): An integer representing the starting cash balance for a backtest.
        fee (float): A float representing the fee for a trade.
        slippage
    """
    ################################################################################

    ### Algorithm
    version = '001'

    ################################################################################
    ################################################################################
    ################################################################################

    ### Database name
    db = 'outputs/mydatabase.db'
    # db = '/Volumes/My AFP Volume/database.db'

    ################################################################################
    ################################################################################
    ################################################################################

    ### Details for saving csv files
    filepath = 'outputs/'
    filename_historic = 'historic_' + version
    filename_analysis = 'analysis_' + version
    filename_mr = 'strategy_development_mr_pairs'
    filename_strategy = 'strategy_' + version
    filename_backtest = 'backtest_' + version
    filename_montecarlo = 'montecarlo_' + version

    ################################################################################
    ################################################################################
    ################################################################################

    ### Yahoo data parameters
    # tickers = ['GME'] # sp500
    tickers = ['^GSPC']  # sp500
    # tickers = ['^IXIC'] # NASDAQ

    interval = '1d' # 1m, 1h, or 1d
    start = date(2022, 1, 1)
    today = dt.datetime.now().date()
    end = today

    ################################################################################
    ################################################################################
    ################################################################################

    ### Indicator parameters
    # close = tickers[0] + '_adjclose' # yahoo
    close = 'close'
    # close = 'ask_Close' # TG Trading
    vol = 'last_Volume'
    high = 'ask_High'
    low = 'ask_Low'
    short = 50
    long = 200
    sl = 0.15
    tp = 2

    ################################################################################
    ################################################################################
    ################################################################################

    ### Backtest Parameters
    cash = 10000
    fee = 0
    slippage = 1.00
    startdate_backtest = '2012-06-01'
    enddate_backtest = '2020-06-01'
    startdate_forwards = '2020-01-01'
    enddate_forwards = '2022-01-01'

    ################################################################################
    ################################################################################
    ################################################################################

    ### Monte Carlo Parameters
    days = 1000
    iterations = 1000

    ################################################################################
    ################################################################################
    ################################################################################
    return {
        'version': version,
        'db': db,
        'filepath': filepath,
        'filename_historic': filename_historic,
        'filename_analysis': filename_analysis,
        'filename_mr': filename_mr,
        'filename_strategy': filename_strategy,
        'filename_backtest': filename_backtest,
        'filename_montecarlo': filename_montecarlo,
        'tickers': tickers,
        'interval': interval,
        'start': start,
        'end': end,
        'close': close,
        'vol': vol,
        'high': high,
        'low': low,
        'short': short,
        'long': long,
        'sl': sl,
        'tp': tp,
        'cash': cash,
        'fee': fee,
        'slippage': slippage,
        'startdate_backtest': startdate_backtest,
        'enddate_backtest': enddate_backtest,
        'startdate_forwards': startdate_forwards,
        'enddate_forwards': enddate_forwards,
        'days': days,
        'iterations': iterations,
    }

################################################################################
################################################################################
