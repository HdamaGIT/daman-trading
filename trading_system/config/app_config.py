from .system_config import SystemConfig
from .development_config import DevelopmentConfig
from .utility_config import UtilityConfig

class AppConfig:
    def __init__(self, system_mode='development'):
        self.system = SystemConfig(mode=system_mode)
        self.development = DevelopmentConfig()
        self.utility = UtilityConfig()

    def summary(self):
        # Returns a summary of the current configuration settings
        return {
            'System Mode': self.system.mode,
            'Tickers': self.development.tickers,
            'Start Date': self.development.start_date,
            'End Date': self.development.end_date,
            'Database Path': self.utility.database_path,
            'File Path': self.utility.file_path,
        }
