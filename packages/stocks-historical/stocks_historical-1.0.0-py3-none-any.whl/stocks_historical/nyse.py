from .fetcher import Fetcher

class Nyse(Fetcher):
    def __init__(self, symbol: str, start: str, end: str = None):
        super().__init__(market="nyse", symbol=symbol, start=start, end=end)

    def get_data(self):
        data = self.fetch_data()
        return self.format_data(data)
