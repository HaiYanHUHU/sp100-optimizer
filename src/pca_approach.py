import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import pytz
import logging
import os
from performance_metrics import calculate_correlation, evaluate_performance, save_performance_metrics, load_performance_metrics, compare_methods, log_comparison_results

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Set up plotting styles
plt.style.use('default')
sns.set_theme()

def load_data():
    """
    Load and preprocess data
    """
    try:
        df = pd.read_csv('data/raw/stock_data.csv')
        df['date'] = pd.to_datetime(df['date'])
        df = df.drop_duplicates(subset=['date', 'symbol'], keep='first')
        
        # Pivot the data
        df_pivot = df.pivot(index='date', columns='symbol', values='Close')
        
        logging.info(f"Data range: {df_pivot.index.min()} to {df_pivot.index.max()}")
        logging.info(f"Number of stocks: {len(df_pivot.columns)}")
        
        return df_pivot
        
    except Exception as e:
        logging.error(f"Error in load_data: {str(e)}")
        raise

def calculate_returns(prices):
    """
    Calculate daily returns
    """
    try:
        returns = prices.pct_change().dropna()
        return returns
    except Exception as e:
        logging.error(f"Error in calculate_returns: {str(e)}")
        raise

def apply_pca(returns, n_components=10):
    """
    Apply PCA to return data
    """
    try:
        # Standardize returns
        scaler = StandardScaler()
        scaled_returns = scaler.fit_transform(returns)
        
        # Apply PCA
        pca = PCA(n_components=n_components)
        pca_result = pca.fit_transform(scaled_returns)
        
        # Get component weights
        component_weights = pd.DataFrame(
            pca.components_.T,
            columns=[f'PC{i+1}' for i in range(n_components)],
            index=returns.columns
        )
        
        # Calculate explained variance ratio
        explained_variance = pca.explained_variance_ratio_
        
        return component_weights, explained_variance, pca_result
        
    except Exception as e:
        logging.error(f"Error in apply_pca: {str(e)}")
        raise

def construct_portfolio(component_weights, explained_variance, n_stocks=10):
    """
    Construct investment portfolio based on PCA components
    """
    try:
        # Calculate importance scores for each stock
        importance_scores = np.abs(component_weights).dot(explained_variance)
        
        # Select top n_stocks stocks
        selected_stocks = importance_scores.nlargest(n_stocks).index
        
        # Calculate weights based on importance scores
        weights = importance_scores[selected_stocks]
        weights = weights / weights.sum()
        
        return pd.Series(weights, index=selected_stocks)
        
    except Exception as e:
        logging.error(f"Error in construct_portfolio: {str(e)}")
        raise

def plot_results(weights, returns, benchmark_returns, explained_variance, title):
    """
    Plot investment portfolio weights and performance visualization
    """
    try:
        plt.figure(figsize=(15, 20))
        
        # Plot weights
        plt.subplot(4, 1, 1)
        weights.plot(kind='bar')
        plt.title(f'{title} Portfolio Weights')
        plt.xticks(rotation=45)
        
        # Plot cumulative returns
        plt.subplot(4, 1, 2)
        portfolio_returns = (returns * weights).sum(axis=1)
        cumulative_returns = (1 + portfolio_returns).cumprod()
        benchmark_cumulative = (1 + benchmark_returns).cumprod()
        cumulative_returns.plot(label='Portfolio')
        benchmark_cumulative.plot(label='Benchmark')
        plt.title('Cumulative Returns')
        plt.legend()
        
        # Plot rolling correlation
        plt.subplot(4, 1, 3)
        correlation = calculate_correlation(portfolio_returns, benchmark_returns)
        correlation.plot()
        plt.title('3-Month Rolling Correlation with Benchmark')
        plt.axhline(y=0.95, color='r', linestyle='--', label='0.95 Correlation Target')
        plt.legend()
        
        # Plot explained variance
        plt.subplot(4, 1, 4)
        plt.plot(np.cumsum(explained_variance))
        plt.title('Cumulative Explained Variance Ratio')
        plt.xlabel('Number of Components')
        plt.ylabel('Cumulative Explained Variance Ratio')
        
        plt.tight_layout()
        
        # Create results directory if it doesn't exist
        os.makedirs('results', exist_ok=True)
        plt.savefig(f'results/{title.lower()}_portfolio.png')
        plt.close()
        
        logging.info(f"Results plotted and saved to results/{title.lower()}_portfolio.png")
        
        # Evaluate and record performance
        performance = evaluate_performance(portfolio_returns, benchmark_returns)
        for period, metrics in performance.items():
            logging.info(f"{period} Performance:")
            logging.info(f"  Correlation: {metrics['correlation']:.4f}")
            logging.info(f"  Tracking Error: {metrics['tracking_error']:.4f}")
            logging.info(f"  Information Ratio: {metrics['information_ratio']:.4f}")
        
        return performance, portfolio_returns
        
    except Exception as e:
        logging.error(f"Error in plot_results: {str(e)}")
        raise

def main():
    try:
        # Create necessary directories
        os.makedirs('data', exist_ok=True)
        os.makedirs('results', exist_ok=True)
        
        # Load and process data
        prices = load_data()
        returns = calculate_returns(prices)
        
        # Load benchmark returns
        benchmark_returns = pd.read_csv('data/processed/benchmark_returns.csv')
        benchmark_returns['date'] = pd.to_datetime(benchmark_returns['date'])
        benchmark_returns = benchmark_returns.set_index('date')['benchmark_return']
        
        # Apply PCA
        n_components = 10
        component_weights, explained_variance, pca_result = apply_pca(returns, n_components)
        
        # Construct portfolio
        n_stocks = 10
        portfolio_weights = construct_portfolio(component_weights, explained_variance, n_stocks)
        
        # Plot results and get performance metrics
        pca_performance, portfolio_returns = plot_results(portfolio_weights, returns, benchmark_returns, explained_variance, 'PCA')
        
        # Save performance metrics
        save_performance_metrics(pca_performance, 'PCA')
        
        # Load AMPL performance metrics
        ampl_performance = load_performance_metrics('AMPL')
        
        # If AMPL performance metrics exist, perform comparison
        if ampl_performance:
            comparison = compare_methods(pca_performance, ampl_performance)
            log_comparison_results(comparison)
        else:
            logging.warning("AMPL performance metrics not found. Skipping comparison.")
        
        logging.info("PCA portfolio analysis completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 