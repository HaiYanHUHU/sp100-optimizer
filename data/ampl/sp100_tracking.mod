# S&P 100 Index Tracking Optimization Model

# Sets and Parameters
set STOCKS;      # Set of all stocks
set T;           # Set of time periods

param returns {STOCKS, T};      # Daily returns for each stock
param benchmark {T};            # S&P 100 index daily returns
param q;                        # Number of stocks to select

# Variables
var x {STOCKS} >= 0;           # Portfolio weights
var y {STOCKS} binary;         # Stock selection variables (1 if selected, 0 otherwise)
var dev_pos {T} >= 0;          # Positive deviation from benchmark
var dev_neg {T} >= 0;          # Negative deviation from benchmark

# Objective: Minimize total absolute deviation
minimize Tracking_Error:
    sum {t in T} (dev_pos[t] + dev_neg[t]);

# Constraints
subject to Weight_Sum:
    sum {i in STOCKS} x[i] = 1;

subject to Stock_Selection:
    sum {i in STOCKS} y[i] = q;

subject to Weight_Selection {i in STOCKS}:
    x[i] <= y[i];

# Deviation definition
subject to Deviation_Definition {t in T}:
    sum {i in STOCKS} x[i] * returns[i,t] - benchmark[t] = dev_pos[t] - dev_neg[t]; 