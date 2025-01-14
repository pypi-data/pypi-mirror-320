import unittest
from stocks_historical import Nasdaq

class TestNasdaq(unittest.TestCase):
    def test_fetch_data(self):
        nasdaq = Nasdaq("AAPL", "2023-01-01", "2023-01-31")
        data = nasdaq.get_data()
        self.assertIn("Date", data)
        self.assertIn("Open", data)
        self.assertIn("High", data)
        self.assertIn("Low", data)
        self.assertIn("Close", data)

if __name__ == "__main__":
    unittest.main()