import pandas as pd
import os

def generate_ampl_data(input_path, output_path, selected_symbols, q):
    df = pd.read_csv(input_path)
    df['date'] = pd.to_datetime(df['date'])

    # Keep only selected stocks
    df = df[df['symbol'].isin(selected_symbols)]

    # Sort by time and symbol
    df = df.sort_values(['date', 'symbol'])

    dates = sorted(df['date'].unique())
    symbols = sorted(df['symbol'].unique())

    T = len(dates)
    N = len(symbols)

    df_pivot = df.pivot(index='date', columns='symbol', values='log_return')
    df_pivot = df_pivot.fillna(0)

    benchmark = df_pivot.mean(axis=1).values

    # AMPL
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write(f"param N := {N};\n")
        f.write(f"param T := {T};\n")
        f.write(f"param q := {q};\n\n")

        f.write("param benchmark :=\n")
        for t, val in enumerate(benchmark, 1):
            f.write(f"{t} {val:.6f}\n")
        f.write(";\n\n")

        f.write("param R : " + ' '.join(str(i+1) for i in range(N)) + " :=\n")
        for t in range(T):
            row = df_pivot.iloc[t].values
            f.write(f"{t+1} " + ' '.join(f"{val:.6f}" for val in row) + "\n")
        f.write(";\n")

    print(f"AMPL data written to: {output_path}")
