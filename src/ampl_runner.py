from amplpy import AMPL
import pandas as pd

def run_ampl(model_path, data_path, output_path):
    # 
    ampl = AMPL()
    ampl.set_option("solver", "cbc")  

    # Load the model and data
    ampl.read(model_path)
    ampl.read_data(data_path)

    # 
    ampl.solve()

    # 
    x = ampl.get_variable("x")
    df = x.get_values().to_pandas()

    # 
    df.to_csv(output_path)
    print(f"AMPL is executed successfully and the result is saved to{output_path}")


def parse_weights(output_path, csv_path):
    # Reading CSV results
    df = pd.read_csv(output_path, index_col=0)
    df.columns = ['weight']
    df.index.name = 'symbol'

    # 
    df.to_csv(csv_path)
    print(f"Save the optimization results as CSV:{csv_path}")
