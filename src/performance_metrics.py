import pandas as pd
import numpy as np
import logging
import os

def calculate_correlation(portfolio_returns, benchmark_returns, window=63):
    # Calculate rolling correlation between portfolio and benchmark
    try:
        # Ensure index alignment
        common_index = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        
        # Calculate rolling correlation
        correlation = portfolio_returns.rolling(window=window).corr(benchmark_returns)
        
        return correlation
    except Exception as e:
        logging.error(f"Error in calculate_correlation: {str(e)}")
        raise

def calculate_tracking_error(portfolio_returns, benchmark_returns, window=63):
    # Calculate tracking error
    try:
        # Ensure index alignment
        common_index = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        
        # Calculate excess returns
        excess_returns = portfolio_returns - benchmark_returns
        
        # Calculate rolling tracking error
        tracking_error = excess_returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        
        return tracking_error
    except Exception as e:
        logging.error(f"Error in calculate_tracking_error: {str(e)}")
        raise

def calculate_information_ratio(portfolio_returns, benchmark_returns, window=63):
    # Calculate information ratio
    try:
        # Ensure index alignment
        common_index = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        
        # Calculate excess returns
        excess_returns = portfolio_returns - benchmark_returns
        
        # Calculate rolling information ratio
        mean_excess = excess_returns.rolling(window=window).mean() * 252  # Annualized
        tracking_error = excess_returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        
        information_ratio = mean_excess / tracking_error
        
        return information_ratio
    except Exception as e:
        logging.error(f"Error in calculate_information_ratio: {str(e)}")
        raise

def calculate_sharpe_ratio(returns, risk_free_rate=0.02, window=63):
    # Calculate Sharpe ratio
    try:
        # Calculate excess returns
        excess_returns = returns - risk_free_rate/252  # Convert to daily risk-free rate
        
        # Calculate rolling Sharpe ratio
        mean_excess = excess_returns.rolling(window=window).mean() * 252  # Annualized
        volatility = excess_returns.rolling(window=window).std() * np.sqrt(252)  # Annualized
        
        sharpe_ratio = mean_excess / volatility
        
        return sharpe_ratio
    except Exception as e:
        logging.error(f"Error in calculate_sharpe_ratio: {str(e)}")
        raise

def evaluate_performance(portfolio_returns, benchmark_returns):
    # Evaluate portfolio performance over different time periods
    try:
        # Ensure index alignment
        common_index = portfolio_returns.index.intersection(benchmark_returns.index)
        portfolio_returns = portfolio_returns.loc[common_index]
        benchmark_returns = benchmark_returns.loc[common_index]
        
        # Define time periods
        periods = {
            '3M': 63,  # ~3 months trading days
            '6M': 126,  # ~6 months trading days
            '9M': 189,  # ~9 months trading days
            '1Y': 252   # ~1 year trading days
        }
        
        # Calculate performance metrics for each period
        performance_metrics = {}
        
        for period_name, days in periods.items():
            # Get recent data
            recent_portfolio = portfolio_returns.iloc[-days:]
            recent_benchmark = benchmark_returns.iloc[-days:]
            
            # Calculate correlation
            correlation = recent_portfolio.corr(recent_benchmark)
            
            # Calculate tracking error
            excess_returns = recent_portfolio - recent_benchmark
            tracking_error = excess_returns.std() * np.sqrt(252)  # Annualized
            
            # Calculate information ratio
            mean_excess = excess_returns.mean() * 252  # Annualized
            information_ratio = mean_excess / tracking_error if tracking_error > 0 else 0
            
            # Calculate Sharpe ratio
            sharpe_ratio = calculate_sharpe_ratio(recent_portfolio).iloc[-1]
            
            # Store results
            performance_metrics[period_name] = {
                'correlation': correlation,
                'tracking_error': tracking_error,
                'information_ratio': information_ratio,
                'sharpe_ratio': sharpe_ratio
            }
        
        return performance_metrics
    except Exception as e:
        logging.error(f"Error in evaluate_performance: {str(e)}")
        raise

def save_performance_metrics(performance_metrics, method_name):
    # Save performance metrics to CSV file
    try:
        # Create results directory
        os.makedirs('results', exist_ok=True)
        
        # Convert to DataFrame
        metrics_df = pd.DataFrame(performance_metrics).T
        
        # Save to CSV
        metrics_df.to_csv(f'results/{method_name.lower()}_performance.csv')
        
        logging.info(f"Performance metrics saved to results/{method_name.lower()}_performance.csv")
    except Exception as e:
        logging.error(f"Error in save_performance_metrics: {str(e)}")
        raise

def load_performance_metrics(method_name):
    # Load performance metrics from CSV file
    try:
        df = pd.read_csv(f'results/{method_name.lower()}_performance.csv', index_col=0)
        return df.to_dict('index')
        
    except FileNotFoundError:
        logging.warning(f"Performance metrics file for {method_name} not found")
        return None
    except Exception as e:
        logging.error(f"Error in load_performance_metrics: {str(e)}")
        raise

def compare_methods(pca_performance, ampl_performance):
    # Compare performance metrics between PCA and AMPL methods
    try:
        comparison = {}
        periods = ['3M', '6M', '9M']
        
        for period in periods:
            comparison[period] = {
                'Correlation': {
                    'PCA': pca_performance[period]['correlation'],
                    'AMPL': ampl_performance[period]['correlation']
                },
                'Tracking Error': {
                    'PCA': pca_performance[period]['tracking_error'],
                    'AMPL': ampl_performance[period]['tracking_error']
                },
                'Information Ratio': {
                    'PCA': pca_performance[period]['information_ratio'],
                    'AMPL': ampl_performance[period]['information_ratio']
                },
                'Sharpe Ratio': {
                    'PCA': pca_performance[period]['sharpe_ratio'],
                    'AMPL': ampl_performance[period]['sharpe_ratio']
                }
            }
        
        # Save comparison results
        comparison_df = pd.DataFrame(comparison).T
        comparison_df.to_csv('results/method_comparison.csv')
        
        logging.info("Method comparison saved to results/method_comparison.csv")
        return comparison
        
    except Exception as e:
        logging.error(f"Error in compare_methods: {str(e)}")
        raise

def log_comparison_results(comparison):
    # Log comparison results
    try:
        logging.info("\nPerformance Comparison (PCA vs AMPL):")
        for period, metrics in comparison.items():
            logging.info(f"\n{period}:")
            logging.info("PCA:")
            logging.info(f"  Correlation: {metrics['PCA']['correlation']:.4f}")
            logging.info(f"  Tracking Error: {metrics['PCA']['tracking_error']:.4f}")
            logging.info(f"  Information Ratio: {metrics['PCA']['information_ratio']:.4f}")
            logging.info(f"  Sharpe Ratio: {metrics['PCA']['sharpe_ratio']:.4f}")
            logging.info("AMPL:")
            logging.info(f"  Correlation: {metrics['AMPL']['correlation']:.4f}")
            logging.info(f"  Tracking Error: {metrics['AMPL']['tracking_error']:.4f}")
            logging.info(f"  Information Ratio: {metrics['AMPL']['information_ratio']:.4f}")
            logging.info(f"  Sharpe Ratio: {metrics['AMPL']['sharpe_ratio']:.4f}")
            
    except Exception as e:
        logging.error(f"Error in log_comparison_results: {str(e)}")
        raise 