# Stocks Historical Library 📊

A Python library to access historical stock data for NASDAQ and NYSE markets. This library simplifies fetching and formatting stock data using the [Stocks Historical API](https://github.com/mantey-github/stock-fetcher-api). It is designed for developers and data analysts who want to quickly retrieve and analyze stock data programmatically.

Library inspired by [Yahoo Historical](https://github.com/AndrewRPorter/yahoo-historical).

---

## Features
- Retrieve historical stock data for NASDAQ and NYSE.
- Supports specifying date ranges with start and optional end dates.
- Formats data into Pandas DataFrames for easy analysis.
- Fetch Open, High, Low, and Close data.

---

## Installation
Install the library via pip:
```bash
pip install stocks-historical
```

---

## Usage

#### **Import and Initialize**
You can use the `Nasdaq` or `Nyse` classes to fetch stock data:
```bash
from stocks_historical import Nasdaq, Nyse

# Fetch NASDAQ data
nasdaq_data = Nasdaq(symbol="AAPL", start="2023-01-03", end="2023-01-09")  # Start and end are dates (YYYY-MM-DD)
data = nasdaq_data.get_data()
print(data.head())

# Fetch NYSE data
nyse_data = Nyse(symbol="GE", start="2023-01-03")  # End is optional
data = nyse_data.get_data()
print(data.head())

```

**Output**:
The data is returned as a Pandas DataFrame with columns:

- `Date:` Timestamp of the record (in human-readable format).
- `Open:` Opening price of the stock.
- `High:` Highest price of the stock.
- `Low:` Lowest price of the stock.
- `Close:` Closing price of the stock.

**Example DataFrame:**
```bash
Fetched Data:
                 Date     Open     High     Low   Close
0 2023-01-03 01:00:00  130.280  130.900  124.17  125.07
1 2023-01-04 01:00:00  126.890  128.656  125.08  126.36
2 2023-01-05 01:00:00  127.130  127.770  124.76  125.02
3 2023-01-06 01:00:00  126.010  130.290  124.89  129.62
4 2023-01-09 01:00:00  130.465  133.410  129.89  130.15
```

---

## API Reference
This library is built on top of the Stocks Historical API. If you prefer to work directly with the API, refer to the API repository for documentation: [Stocks Historical API](https://github.com/mantey-github/stock-fetcher-api)


---

## Credits
The stock data used in this library is sourced from **Kaggle Datasets**:

1. [Top 100 NYSE Daily Stock Prices](https://www.kaggle.com/datasets/svaningelgem/nyse-100-daily-stock-prices) by Steven Van Ingelgem

2. [Top 100 NASDAQ daily stock prices](https://www.kaggle.com/datasets/svaningelgem/nasdaq-100-daily-stock-prices) by Steven Van Ingelgem

All credits goes to the Kaggle community for providing these datasets!

---

## Contributions
Contributions are welcome 🤗! If you'd like to improve this library, feel free to fork the repository and submit a pull request.