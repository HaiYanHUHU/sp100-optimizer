

from yahooquery import Ticker
import pandas as pd
import os

# 
TICKERS = [
    "AAPL", "MSFT", "GOOG", "AMZN", "META", "NVDA", "TSLA", "PEP", "JNJ", "AVGO",
    "V", "MA", "UNH", "LLY", "HD", "MRK", "XOM", "ADBE", "ABBV", "KO", "COST",
    "BAC", "CSCO", "WMT", "CVX", "TMO", "MCD", "DHR", "ACN", "INTC", "QCOM", "TXN",
    "NEE", "LIN", "PM", "AMGN", "UNP", "MDT", "UPS", "IBM", "GS", "RTX", "ISRG", "NOW",
    "BLK", "AMAT", "LMT", "GE", "MS", "LOW", "CAT", "DE", "CB", "PLD", "C", "NFLX",
    "ADI", "SPGI", "SCHW", "ZTS", "BA", "T", "MO", "VRTX", "CI", "REGN", "GILD", "ADP",
    "EL", "SYK", "MMC", "PGR", "BDX", "CL", "SO", "PSX", "ETN", "FDX", "ICE", "AXP",
    "COF", "GM", "DUK", "AON", "ECL", "ORLY", "NSC", "USB", "ADI", "EW", "FIS", "APD",
    "SHW", "AIG", "BK", "ALL", "PXD", "BIIB", "TGT", "F", "HCA"
]

def fetch_stock_data(tickers, start_date, end_date):
   
    all_data = []

    for symbol in tickers:
        print(f"Getting {symbol}...")
        try:
            t = Ticker(symbol)
            hist = t.history(start=start_date, end=end_date)
            if not hist.empty:
                hist = hist.reset_index()
                hist["symbol"] = symbol
                all_data.append(hist)
        except Exception as e:
            print(f"Failed to fetch {symbol}: {e}")

    if all_data:
        return pd.concat(all_data, ignore_index=True)
    else:
        return pd.DataFrame()

def save_sp100_data(start_date, end_date, output_path="data/raw/prices_full.csv"):
   
    df = fetch_stock_data(TICKERS, start_date, end_date)
    if not df.empty:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        df.to_csv(output_path, index=False)
        print(f"Data save to {output_path}")
    else:
        print("No data was fetched.")


if __name__ == "__main__":
    save_sp100_data("2024-03-25", "2025-03-25")
