from datetime import datetime

class DevelopmentConfig:
    def __init__(self, tickers=None, start_date=datetime(2024, 1, 1).date(), end_date=datetime.now().date()):
        self.tickers = tickers if tickers is not None else ['BTC-GBP', 'ETH-GBP', 'ETH-BTC']
        self.start_date = start_date
        self.end_date = end_date
