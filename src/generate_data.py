import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_sp100_symbols():
    # Use complete S&P 100 component stock list
    return ['AAPL', 'ABBV', 'ABT', 'ACN', 'ADBE', 'AIG', 'AMD', 'AMGN', 'AMT', 'AMZN', 
            'AVGO', 'AXP', 'BA', 'BAC', 'BK', 'BKNG', 'BLK', 'BMY', 'BRK.B', 'C', 
            'CAT', 'CHTR', 'CL', 'CMCSA', 'COF', 'COP', 'COST', 'CRM', 'CSCO', 'CVS', 
            'CVX', 'DE', 'DHR', 'DIS', 'DUK', 'EMR', 'FDX', 'GD', 'GE', 'GILD', 'GM', 
            'GOOG', 'GOOGL', 'GS', 'HD', 'HON', 'IBM', 'INTC', 'INTU', 'ISRG', 'JNJ', 
            'JPM', 'KO', 'LIN', 'LLY', 'LMT', 'LOW', 'MA', 'MCD', 'MDLZ', 'MDT', 'MET', 
            'META', 'MMM', 'MO', 'MRK', 'MS', 'MSFT', 'NEE', 'NFLX', 'NKE', 'NOW', 'NVDA', 
            'ORCL', 'PEP', 'PFE', 'PG', 'PLTR', 'PM', 'PYPL', 'QCOM', 'RTX', 'SBUX', 
            'SCHW', 'SO', 'SPG', 'T', 'TGT', 'TMO', 'TMUS', 'TSLA', 'TXN', 'UNH', 'UNP', 
            'UPS', 'USB', 'V', 'VZ', 'WFC', 'WMT', 'XOM']

def get_stock_data(symbols, start_date, end_date):
    data = pd.DataFrame()
    for symbol in symbols:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(start=start_date, end=end_date)
            if not hist.empty:
                data[symbol] = hist['Close']
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
    return data

def calculate_returns(prices):
    return prices.pct_change().dropna()

def generate_ampl_data(returns, benchmark_returns, output_file):
    with open(output_file, 'w') as f:
        # Write stock set
        f.write('set STOCKS := ' + ' '.join(returns.columns) + ';\n\n')
        
        # Write time set
        time_periods = list(range(1, len(returns) + 1))
        f.write('set T := ' + ' '.join(map(str, time_periods)) + ';\n\n')
        
        # Write parameter q (number of stocks to select)
        f.write('param q := 10;\n\n')
        
        # Write returns data
        f.write('param returns :=\n')
        for t, (idx, row) in enumerate(returns.iterrows(), 1):
            for symbol, ret in row.items():
                if not pd.isna(ret):
                    f.write(f'{symbol} {t} {ret:.6f}\n')
        f.write(';\n\n')
        
        # Write benchmark returns data
        f.write('param benchmark :=\n')
        for t, (idx, ret) in enumerate(benchmark_returns.items(), 1):
            if not pd.isna(ret):
                f.write(f'{t} {ret:.6f}\n')
        f.write(';\n')

def main():
    # Set time range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    # Get stock data
    symbols = get_sp100_symbols()
    prices = get_stock_data(symbols, start_date, end_date)
    
    # Calculate returns
    returns = calculate_returns(prices)
    
    # Get S&P 100 index data as benchmark
    try:
        sp100 = yf.Ticker("^OEX")  # S&P 100 index code
        sp100_hist = sp100.history(start=start_date, end=end_date)
        benchmark_returns = sp100_hist['Close'].pct_change().dropna()
    except Exception as e:
        print(f"Error fetching S&P 100 index data: {str(e)}")
        print("Using market-cap weighted average as fallback...")
        # If index data cannot be obtained, use market-cap weighted average as fallback
        market_caps = {}
        for symbol in symbols:
            try:
                stock = yf.Ticker(symbol)
                market_caps[symbol] = stock.info.get('marketCap', 0)
            except:
                market_caps[symbol] = 0
        
        total_market_cap = sum(market_caps.values())
        weights = {symbol: cap/total_market_cap for symbol, cap in market_caps.items() if total_market_cap > 0}
        benchmark_returns = returns.mul(weights).sum(axis=1)
    
    # Generate AMPL data file
    generate_ampl_data(returns, benchmark_returns, 'data/ampl/sp100_tracking.dat')
    
    print("Data generation completed!")

if __name__ == "__main__":
    main() 