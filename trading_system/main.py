from config import AppConfig
from .utils.logging import configure_logging
import logging
from data.main import data
from strategy.main import strategy
from backtesting.main import backtesting


def main():
    configure_logging()  # Configure logging at the start
    logging.info("Starting the trading system...")

    config = AppConfig(system_mode='development')
    logging.info("Config loaded successfully.")

    df_data = data(tickers=config.development.tickers, start_date=config.development.start_date, end_date=config.development.end_date)
    logging.info("Data loaded successfully.")

    # Generate strategy signals
    try:
        strategy_output = strategy(df_data)
        logging.info("Strategy signals generated.")
    except Exception as e:
        logging.error(f"Error generating strategy signals: {e}")
        return

    # Conduct backtesting
    try:
        backtester = backtesting(strategy_output)
        logging.info("Backtesting completed.")
    except Exception as e:
        logging.error(f"Error during backtesting: {e}")
        return

    return backtester
