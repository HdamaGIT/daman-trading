#########################################################################################
#########################################################################################
#########################################################################################

import pandas as pd
from datetime import datetime, timedelta, date

from src.data_collect.finviz import Finviz
from src.data_collect.yahoo_historic_data import HistoricPriceData

from src.indicator_calculation.indicators import TAIndicators

# from src.trading_strategies.meanreversion import MeanReversion
from src.trading_strategies.strategy import TradeAllocation
#
# from src.backtesting.backtest import Backtest
# from src.backtesting.backtest_analyse import analyse_backtest, plot_backtest
# from src.backtesting.monte_carlo import MonteCarlo

from src.database_management.save_data import save_data
from src.database_management.database_copysave import Database


def master(input_vars, start_time,
            finviz, yahoo_extract, data_prep, meanreversion, strategy, run_backtest, run_forwardstest, montecarlo):

    """
    Main function for extracting, analyzing, and backtesting financial data.
    """

    #########################################################################################

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

    #########################################################################################

    if finviz:
        try:
            exchange = 'Any'
            index = 'S&P 500'
            sector = 'Basic Materials'

            fv = Finviz(exchange, sector, index)
            fv.run()

            save_data(fv.df, filepath, 'finviz_tickers', False)
            db = Database(fv.df, db, 'finviz_tickers')
            db.save_finviz_tickers()

        except Exception as e:
            # Handle exceptions and edge cases
            print(f"Error extracting data from FinViz {e}")
            return

    #########################################################################################

    if yahoo_extract:
        try:
            ### Choose which stock universe to use
            # Create a database object
            database = Database(None, db, 'finviz_tickers')
            # Read the 'stock_prices' table and create a DataFrame
            database.read_table()
            # yahoo_tickers = database.df

            # cryptocurrencies = ['BTC-USD']
            # yahoo_tickers = pd.DataFrame(cryptocurrencies, columns=['ticker'])

            target = tickers
            yahoo_tickers = pd.DataFrame(target, columns=['ticker'])

            df_hist = pd.DataFrame

            if interval == '1m':
                delta = timedelta(days=7)

                while start < end:
                    t_start = start
                    t_end = start + delta - timedelta(days=1)
                    if t_end > end:
                        t_end = end

                    print(f"data extract between: {t_start} and {t_end}")
                    yh = HistoricPriceData(yahoo_tickers, t_start, t_end, interval, limit_sector=False, sector='Technology')
                    yh.fetch_data()

                    if df_hist.empty:
                        df_hist = yh.data
                    else:
                        df_hist = pd.concat([df_hist, yh.data], ignore_index=True)

                    start += delta

                df_hist = df_hist.sort_values(by=['ticker', 'dt'])

                save_data(df_hist, filepath, filename_historic + '_' + interval, False)
                db = Database(df_hist, db, filename_historic + '_' + interval)
                db.save_historic_yahoo()

            elif interval == '1h':
                delta = timedelta(days=60)

                while start < end:
                    t_start = start
                    t_end = start + delta - timedelta(days=1)
                    if t_end > end:
                        t_end = end

                    print(f"data extract between: {t_start} and {t_end}")
                    yh = HistoricPriceData(yahoo_tickers, t_start, t_end, interval, limit_sector=False, sector='Technology')
                    yh.fetch_data()

                    if df_hist.empty:
                        df_hist = yh.data
                    else:
                        df_hist = pd.concat([df_hist, yh.data], ignore_index=True)

                    start += delta

                df_hist = df_hist.sort_values(by=['ticker', 'dt'])

                save_data(df_hist, filepath, filename_historic + '_' + interval, False)
                db = Database(df_hist, db, filename_historic + '_' + interval)
                db.save_historic_yahoo()

            elif interval == '1d':
                delta = timedelta(days=500)

                while start < end:
                    t_start = start
                    t_end = start + delta - timedelta(days=1)
                    if t_end > end:
                        t_end = end

                    print(f"data extract between: {t_start} and {t_end}")
                    yh = HistoricPriceData(yahoo_tickers, t_start, t_end, interval, limit_sector=False, sector='Technology')
                    yh.fetch_data()

                    if df_hist.empty:
                        df_hist = yh.data
                    else:
                        df_hist = pd.concat([df_hist, yh.data], ignore_index=True)

                    start += delta

                df_hist = df_hist.sort_values(by=['ticker', 'dt'])

                save_data(df_hist, filepath, filename_historic + '_' + interval, False)
                db = Database(df_hist, db, filename_historic + '_' + interval)
                db.save_historic_yahoo()

        except Exception as e:
            # Handle exceptions and edge cases
            print(f"Error extracting data from Yahoo Finance: {e}")
            return

    #########################################################################################

    # Indicators, Signals, Trading Strategy, Allocation
    if data_prep:
        try:
            # data = pd.read_csv(filepath + filename_historic + '.csv')
            # Create a database object
            database = Database(None, db, filename_historic + '_' + interval)
            # Read the 'stock_prices'
            #     if strategy:
            #     #     try:
            #         # data = pd.read_csv(filepath + filename_historic + '.csv')
            #         # Create a database object
            #         database = Database(None, db, filename_analysis + '_' + interval)
            #         # Read the 'stock_prices' table and create a DataFrame
            #         database.read_table()
            #
            #         trade_alloc = TradeAllocation(data=database.df, close=close)
            #         trade_alloc.run()
            #         print('Process: Strategy Complete')
            #
            #         save_data(trade_alloc.data, filepath, filename_strategy + '_' + interval, False)
            #
            #         time_elapsed = datetime.now() - start_time
            #         print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
            #
            #     # trade_alloc.plot_signals()
            #
            #         # except Exception as e:
            #         #     # Handle exceptions and edge cases
            #         #     print(f"Error preparing data for analysis: {e}")
            #         #
            #         #     returntable and create a DataFrame
            database.read_table()

            ta_indicators = TAIndicators(data=database.df, close=close, high=high, low=low, vol=vol, short=short, long=long)
            results = ta_indicators.run()
            df = pd.DataFrame.from_dict(results)
            print('Process: TA & Indicators  Complete.')

            save_data(df, filepath, filename_analysis + '_' + interval, False)
            db = Database(df, db, filename_analysis + '_' + interval)
            db.save_dataprep()

            time_elapsed = datetime.now() - start_time
            print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))

        except Exception as e:
            # Handle exceptions and edge cases
            print(f"Error preparing data for analysis: {e}")

            return

    # #########################################################################################
    #
    # if meanreversion:
    #     try:
    #
    #         database = Database(None, db, 'finviz_tickers')
    #         database.read_table()
    #         df_finviz = database.df
    #
    #         database = Database(None, db, 'historic_sp500_v1_1d')
    #         database.read_table()
    #         df_historic = database.df
    #
    #         mr = MeanReversion(df_finviz, df_historic)
    #         mr_pairs = mr.find_all_mean_reverting_pairs()
    #         analyzed_pairs = mr.analyze_pairs(mr_pairs)
    #
    #         # db = Database(analyzed_pairs, db, 'strategy_development_mr_pairs')
    #         # db.save_historic_yahoo()
    #         save_data(analyzed_pairs, filepath, filename_mr, False)
    #
    #     except Exception as e:
    #         # Handle exceptions and edge cases
    #         print(f"Error preparing data for analysis: {e}")
    #
    #     return
    #
    # #########################################################################################

    # #########################################################################################
    #
    # if run_backtest:
    #     try:
    #         data = pd.read_csv(filepath + filename_strategy + '.csv')
    #
    #         backtest = Backtest(data, close, cash, fee, slippage, startdate_backtest, enddate_backtest, sl, tp)
    #         results = backtest.run()
    #         df = pd.DataFrame.from_dict(results)
    #         print('Process: Backtest Complete.')
    #
    #         data, final_value, compare_hold_val, strategy_max_drawdown, asset_max_drawdown = analyse_backtest(df, cash, version, printlog=True)
    #
    #         save_data(data, filepath, filename_backtest, index=False)
    #         database = Database(data, db, filename_backtest)
    #         database.save_backtest()
    #
    #         time_elapsed = datetime.now() - start_time
    #         print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    #
    #         plot_backtest(data)
    #
    #     except Exception as e:
    #         # Handle exceptions and edge cases
    #         print(f"Error running backtest: {e}")
    #         return
    #
    # #########################################################################################
    #
    # if run_forwardstest:
    #     try:
    #         data = pd.read_csv(filepath + filename_analysis + '.csv')
    #         data = backtest.backtest(data, close, cash, fee, slippage, startdate_forwards, enddate_forwards)
    #         print('Process: Forwards Test Complete.')
    #         data, final_value, compare_hold_val, strategy_max_drawdown, asset_max_drawdown = analyse_backtest(data, cash, version, printlog=True)
    #         save_data(data, filepath, filename_backtest, index=False)
    #         time_elapsed = datetime.now() - start_time
    #         print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    #
    #         backtest.plot_backtest(data)
    #
    #     except Exception as e:
    #         # Handle exceptions and edge cases
    #         print(f"Error running forwards test: {e}")
    #         return
    #
    # #########################################################################################
    #
    # if montecarlo:
    #     # try:
    #     data = pd.read_csv(filepath + filename_analysis + '.csv')
    #
    #     mc = MonteCarlo(data[close], days, iterations, True, close, cash, fee, slippage, start, end, sl, tp, high, low, vol, short, long, version)
    #     mc_results = mc.run()
    #     df_mc = pd.DataFrame.from_dict(mc_results)
    #
    #     save_data(df_mc, filepath, filename_montecarlo, index=False)
    #     time_elapsed = datetime.now() - start_time
    #     print('Time elapsed (hh:mm:ss.ms) {}'.format(time_elapsed))
    #
    #     mc.plot_simulation()
    #     # Run summary of monte carlo analysis function
    #     mc.monte_carlo_analysis(df_mc.final_values, df_mc.compare_hold_values, df_mc.strategy_max_drawdown_values, df_mc.asset_max_drawdown_values, cash, days, iterations, version, plot=True)
    #
    #     # except Exception as e:
    #     #     # Handle exceptions and edge cases
    #     #     print(f"Error running monte carlo simulation: {e}")
    #     #     return
