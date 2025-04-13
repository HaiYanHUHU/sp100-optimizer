import os
import sys
import pandas as pd
import numpy as np
import amplpy
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import yfinance as yf
import logging
from performance_metrics import calculate_correlation, evaluate_performance, save_performance_metrics

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up plotting style
plt.style.use('default')
sns.set_theme()

def run_ampl_model():
    # Run the AMPL optimization model and return the results
    try:
        # Initialize AMPL environment
        ampl = amplpy.AMPL()
        
        # Set AMPL directory
        ampl.setOption("solver", "ipopt")
        
        # Read model and data files
        ampl.read("data/ampl/sp100_tracking.mod")
        ampl.readData("data/ampl/sp100_tracking.dat")
        
        # Solve the model
        ampl.solve()
        
        logging.info(f"AMPL solve status: {ampl.getValue('solve_result')}")
        
        return ampl
        
    except Exception as e:
        logging.error(f"Error in run_ampl_model: {str(e)}")
        raise

def get_results(ampl):
    # Get optimization results
    try:
        # Get portfolio weights
        x = ampl.getVariable("x")
        weights = {}
        for i in ampl.getSet("STOCKS"):
            weights[str(i)] = x[i].value()
        
        # Convert weights to pandas Series
        weights = pd.Series(weights)
        
        # Get time periods and stocks
        T = list(map(str, ampl.getSet("T")))
        stocks = list(map(str, ampl.getSet("STOCKS")))
        
        # Create DataFrame for returns
        returns_df = pd.DataFrame(0, index=T, columns=stocks)
        for i in stocks:
            for t in T:
                try:
                    returns_df.loc[t, i] = ampl.getParameter("returns")[i, int(t)]
                except:
                    continue
    
    # Calculate portfolio returns
        portfolio_returns = pd.Series(0, index=T)
        for t in T:
            portfolio_returns[t] = (returns_df.loc[t] * weights).sum()
    
    # Get benchmark returns
        benchmark_returns = pd.Series(0, index=T)
        for t in T:
            try:
                benchmark_returns[t] = ampl.getParameter("benchmark")[int(t)]
            except:
                continue
        
        return weights, portfolio_returns, benchmark_returns
        
    except Exception as e:
        logging.error(f"Error in get_results: {str(e)}")
        raise

def plot_results(weights, portfolio_returns, benchmark_returns):
    try:
        # Create figure
        plt.figure(figsize=(15, 15))
        
        # Plot weights
        plt.subplot(3, 1, 1)
        weights.plot(kind='bar')
        plt.title('AMPL Portfolio Weights')
        plt.xticks(rotation=45)
        
        # Plot cumulative returns
        plt.subplot(3, 1, 2)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        cumulative_returns.plot(label='Portfolio')
        benchmark_cumulative.plot(label='Benchmark')
        plt.title('Cumulative Returns')
        plt.legend()
        
        # Plot rolling correlation
        plt.subplot(3, 1, 3)
        correlation = calculate_correlation(portfolio_returns, benchmark_returns)
        correlation.plot()
        plt.title('3-Month Rolling Correlation with Benchmark')
        plt.axhline(y=0.95, color='r', linestyle='--', label='0.95 Correlation Target')
        plt.legend()
        
        plt.tight_layout()
        
        # Save results
        os.makedirs('results', exist_ok=True)
        plt.savefig('results/ampl_portfolio.png')
        plt.close()
        
        logging.info("Results plotted and saved to results/ampl_portfolio.png")
        
    except Exception as e:
        logging.error(f"Error in plot_results: {str(e)}")
        raise

def main():
    try:
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        
        # Run AMPL model
        ampl = run_ampl_model()
        
        # Get results
        weights, portfolio_returns, benchmark_returns = get_results(ampl)
    
    # Plot results
        plot_results(weights, portfolio_returns, benchmark_returns)
        
        # Evaluate and save performance
        performance_metrics = evaluate_performance(portfolio_returns, benchmark_returns)
        save_performance_metrics(performance_metrics, 'AMPL')
        
        # Log performance metrics
        for period, metrics in performance_metrics.items():
            logging.info(f"{period} Performance:")
            logging.info(f"  Correlation: {metrics['correlation']:.4f}")
            logging.info(f"  Tracking Error: {metrics['tracking_error']:.4f}")
            logging.info(f"  Information Ratio: {metrics['information_ratio']:.4f}")
            logging.info(f"  Sharpe Ratio: {metrics['sharpe_ratio']:.4f}")
        
        logging.info("AMPL portfolio analysis completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 