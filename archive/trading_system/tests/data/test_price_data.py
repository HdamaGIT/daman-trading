import unittest
from archive.trading_system.data.price_data import price_data


class TestHistoricalDataExtraction(unittest.TestCase):

    def test_successful_data_retrieval(self):
        """Test that the function returns data for valid inputs."""
        data = price_data('BTC-USD', '2020-01-01', '2020-01-10')
        self.assertNotEqual(data.empty, True, "The data should not be empty for valid inputs.")

    def test_invalid_symbol(self):
        """Test the function's response to an invalid symbol."""
        with self.assertRaises(ValueError):
            price_data('INVALID-SYMBOL', '2020-01-01', '2020-01-10')

    def test_invalid_date_range(self):
        """Test the function's response to a start date later than the end date."""
        with self.assertRaises(ValueError):
            price_data('BTC-USD', '2020-01-10', '2020-01-01')

    def test_data_format(self):
        """Test that the returned data is in the expected format."""
        data = price_data('BTC-USD', '2020-01-01', '2020-01-10')
        expected_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        self.assertListEqual(list(data.columns), expected_columns, "The data columns do not match the expected format.")
