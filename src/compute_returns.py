import pandas as pd
import numpy as np
import os

def compute_log_returns(input_path: str, output_path: str):
    """
    Calculate the logarithmic yield from the price CSV and save it as a new file.
    
    - input_path: Original price file path
    - output_path: The path for saving the processed rate of return
    """
    # Read price data
    df = pd.read_csv(input_path)
    
    # datetime
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values(by=["symbol", "date"])

    # log return
    df["log_return"] = df.groupby("symbol")["close"].transform(lambda x: np.log(x / x.shift(1)))


    # Remove missing value
    df.dropna(subset=["log_return"], inplace=True)

    # 
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    # save
    df.to_csv(output_path, index=False)
    print(f"Log returns saved to {output_path}")

if __name__ == "__main__":
    compute_log_returns("data/raw/prices_full.csv", "data/processed/returns_full.csv")




