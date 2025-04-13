# S&P 100 Index Fund Optimizer

An optimizer that tracks the S&P 100 index using fewer than 100 stocks. It uses both AMPL and PCA methods for optimization and compares performance across different time periods (1-4 quarters).

## Project Goals

1. Build a fund that tracks the S&P 100 index
2. Use fewer than 100 stocks while maintaining tracking performance
3. Optimize across different time periods (1-4 quarters)
4. Implement and compare 2 optimization methods:
   - AMPL optimization
   - PCA optimization
5. Provide reproducible results with detailed analysis


## 

1. Run portfolio analysis:
```bash
python src/portfolio_analysis.py
```

2. Run optimization:
```bash
# AMPL method
python src/ampl_runner.py

# PCA method
python src/pca_approach.py
```

```

## Dependencies

- Python 3.8 or higher
- AMPL 2021.1.0 or higher



