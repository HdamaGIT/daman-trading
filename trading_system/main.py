import logging
from config import AppConfig
from utils.logging import configure_logging
from data.main import data
from strategy.main import strategy
from backtesting.main import backtesting
from typing import Optional, Any
import pandas as pd


def load_configuration() -> AppConfig:
    """Loads the application configuration."""
    try:
        config = AppConfig(system_mode='development')
        logging.info("Config loaded successfully.")
        return config
    except Exception as e:
        logging.error(f"Error loading configuration: {e}")
        raise


def load_data(config: AppConfig) -> Optional[pd.DataFrame]:
    """Loads data based on the provided configuration."""
    try:
        df_data = data(tickers=config.development.tickers,
                       start_date=config.development.start_date,
                       end_date=config.development.end_date)
        logging.info("Data loaded successfully.")
        return df_data
    except Exception as e:
        logging.error(f"Error loading data: {e}")
        return None


def generate_strategy_signals(df_data: pd.DataFrame) -> Optional[pd.DataFrame]:
    """Generates trading signals based on the strategy."""
    try:
        strategy_output = strategy(df_data)
        logging.info("Strategy signals generated successfully.")
        return strategy_output
    except Exception as e:
        logging.error(f"Error generating strategy signals: {e}")
        return None


def run_backtesting(strategy_output: pd.DataFrame) -> Optional[Any]:
    """Runs backtesting on the strategy output."""
    try:
        backtester = backtesting(strategy_output)
        logging.info("Backtesting completed successfully.")
        return backtester
    except Exception as e:
        logging.error(f"Error during backtesting: {e}")
        return None


def main():
    configure_logging()  # Configure logging at the start
    logging.info("Starting the trading system...")

    # Load configuration
    try:
        config = load_configuration()
    except Exception:
        logging.error("Terminating due to configuration load failure.")
        return

    # Load data
    df_data = load_data(config)
    if df_data is None:
        logging.error("Terminating due to data load failure.")
        return

    # Generate strategy signals
    strategy_output = generate_strategy_signals(df_data)
    if strategy_output is None:
        logging.error("Terminating due to strategy signal generation failure.")
        return

    # Conduct backtesting
    backtester = run_backtesting(strategy_output)
    if backtester is None:
        logging.error("Terminating due to backtesting failure.")
        return

    logging.info("Trading system completed successfully.")
    return backtester

if __name__ == "__main__":
    main()
