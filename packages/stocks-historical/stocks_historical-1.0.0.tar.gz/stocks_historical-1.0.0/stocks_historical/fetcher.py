import requests
import pandas as pd
from datetime import datetime
from .constants import API_BASE_URL

class Fetcher:
    def __init__(self, market: str, symbol: str, start: str, end: str = None):
        self.market = market
        self.symbol = symbol.upper()
        self.start = start
        self.end = end

    def fetch_data(self):
        try:
            url = f"{API_BASE_URL}/{self.market}/{self.symbol}"
            params = {"start": self.start, "end": self.end}
            response = requests.get(url, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching stocks data: {e}")

    @staticmethod
    def format_data(data):
        """
        Format JSON data into a Pandas DataFrame, handling missing values.

        Args:
            data: Raw JSON data returned by the Stocks Fetcher API.

        Returns:
            pd.DataFrame: A DataFrame with columns ['Date', 'Open', 'High', 'Low', 'Close'].
        """

        # Extract timestamps and quote data
        timestamps = data.get("timestamp", [])
        quote = data.get("indicators", {}).get("quote", [{}])[0]

        # Define keys to extract
        keys = ["open", "high", "low", "close"]

        # Ensure all keys exist in the quote data, and default to empty lists if missing
        formatted_data = {
            key: quote.get(key, []) for key in keys
        }

        # Normalize lengths: Fill missing values with 0.0
        max_length = len(timestamps)
        for key in keys:
            if len(formatted_data[key]) < max_length:
                formatted_data[key].extend([0.0] * (max_length - len(formatted_data[key])))

        # Create the DataFrame
        df = pd.DataFrame({
            "Date": [datetime.fromtimestamp(ts) for ts in timestamps],
            "Open": formatted_data["open"],
            "High": formatted_data["high"],
            "Low": formatted_data["low"],
            "Close": formatted_data["close"],
        })

        return df
