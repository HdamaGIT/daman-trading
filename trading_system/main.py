#########################################################################################
#########################################################################################
#########################################################################################


from datetime import datetime
import datetime as dt

from functions.strategy_development_master import main_func
from functions.strategy_development_inputs import inputs

if __name__ == '__main__':
    start_time = datetime.now()
    print("start time: " + str(start_time))

    input_vars = inputs()

    version = input_vars['version']
    db = input_vars['db']
    filepath = input_vars['filepath']
    filename_historic = input_vars['filename_historic']
    filename_analysis = input_vars['filename_analysis']
    filename_mr = input_vars['filename_mr']
    filename_strategy = input_vars['filename_strategy']
    filename_backtest = input_vars['filename_backtest']
    filename_montecarlo = input_vars['filename_montecarlo']
    tickers = input_vars['tickers']
    interval = input_vars['interval']
    start = input_vars['start']
    end = input_vars['end']
    close = input_vars['close']
    vol = input_vars['vol']
    high = input_vars['high']
    low = input_vars['low']
    short = input_vars['short']
    long = input_vars['long']
    sl = input_vars['sl']
    tp = input_vars['tp']
    cash = input_vars['cash']
    fee = input_vars['fee']
    slippage = input_vars['slippage']
    startdate_backtest = input_vars['startdate_backtest']
    enddate_backtest = input_vars['enddate_backtest']
    startdate_forwards = input_vars['startdate_forwards']
    enddate_forwards = input_vars['enddate_forwards']
    days = input_vars['days']
    iterations = input_vars['iterations']

    # Choose modules to run
    finviz = False
    yahoo_extract = False
    data_prep = False
    meanreversion = False
    strategy = True
    run_backtest = False
    run_forwardstest = False
    montecarlo = False

    #########################################################################################
    #########################################################################################
    #########################################################################################

    main_func(version, start_time,
              db, filepath, filename_historic, filename_analysis, filename_mr, filename_strategy, filename_backtest, filename_montecarlo,
              tickers, start, end, interval,
              close, high, low, vol, short, long, sl, tp,
              cash, fee, slippage, days, iterations, startdate_backtest, enddate_backtest, startdate_forwards, enddate_forwards,
              finviz=finviz, yahoo_extract=yahoo_extract, data_prep=data_prep, meanreversion=meanreversion, strategy=strategy, run_backtest=run_backtest, run_forwardstest=run_forwardstest, montecarlo=montecarlo)
