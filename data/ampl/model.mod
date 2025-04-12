param N;                     # total stock
param T;                     # Time point total
param q;                     # The number of stock to be selected
param benchmark{1..T};       # benchmark's log return time series
param R{1..T, 1..N};         # The log return of each stock at each point in time

var x{1..N} >= 0;            # The investment weight of each stock
var z{1..N} binary;          # The investment weight of each stock

# Each stock is either selected or invested at 0
s.t. selection_limit: sum{i in 1..N} z[i] = q;
s.t. linking{i in 1..N}: x[i] <= z[i];

# Total investment = 1(Complete Investor)
s.t. total_weight: sum{i in 1..N} x[i] = 1;

# Define the return of the portfolio at each point in time
var port_return{1..T};
s.t. portfolio_return{t in 1..T}:
    port_return[t] = sum{i in 1..N} R[t,i] * x[i];

# Objective function: Minimize tracking error
minimize tracking_error:
    sum{t in 1..T} (port_return[t] - benchmark[t])^2;
