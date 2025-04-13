import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
import os
from generate_data import get_sp100_symbols, get_stock_data, calculate_returns

# Set up logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

class DataProcessor:
    def __init__(self):
        # Initialize data processor
        self.raw_data = None
        self.processed_data = None
        
    def fetch_and_process_data(self):
        # Fetch and process data using generate_data functions
        try:
            # Get stock symbols and set date range
            symbols = get_sp100_symbols()
            end_date = datetime.now()
            start_date = end_date - timedelta(days=365)
            
            # Get stock data
            prices = get_stock_data(symbols, start_date, end_date)
            returns = calculate_returns(prices)
            
            # Store processed data
            self.processed_data = returns
            
            logging.info(f"Data processed successfully. Shape: {returns.shape}")
            return returns
            
        except Exception as e:
            logging.error(f"Error in fetch_and_process_data: {str(e)}")
            raise
            
    def calculate_statistics(self):
        # Calculate basic statistics for each stock
        try:
            if self.processed_data is None:
                raise ValueError("No data available. Call fetch_and_process_data first.")
                
            stats = self.processed_data.agg(['mean', 'std', 'min', 'max']).round(4)
            
            logging.info("Statistics calculated successfully")
            return stats
            
        except Exception as e:
            logging.error(f"Error calculating statistics: {str(e)}")
            raise
            
    def generate_summary(self):
        # Generate summary report
        try:
            if self.processed_data is None:
                raise ValueError("No data available. Call fetch_and_process_data first.")
                
            summary = {
                'total_stocks': len(self.processed_data.columns),
                'date_range': (
                    self.processed_data.index.min(),
                    self.processed_data.index.max()
                ),
                'total_days': len(self.processed_data),
                'missing_values': self.processed_data.isnull().sum().sum()
            }
            
            logging.info("Summary generated successfully")
            return summary
            
        except Exception as e:
            logging.error(f"Error generating summary: {str(e)}")
            raise
            
    def save_processed_data(self, output_path):
        # Save processed data to CSV
        try:
            if self.processed_data is None:
                raise ValueError("No data available. Call fetch_and_process_data first.")
                
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.processed_data.to_csv(output_path)
            logging.info(f"Processed data saved to {output_path}")
            
        except Exception as e:
            logging.error(f"Error saving processed data: {str(e)}")
            raise

def main():
    try:
        # Create data directory if it doesn't exist
        os.makedirs('data/processed', exist_ok=True)
        
        # Initialize data processor
        processor = DataProcessor()
        
        # Fetch and process data
        processor.fetch_and_process_data()
        
        # Calculate statistics and generate summary
        stats = processor.calculate_statistics()
        summary = processor.generate_summary()
        
        # Save processed data
        processor.save_processed_data('data/processed/returns.csv')
        
        # Log summary information
        logging.info(f"Total stocks: {summary['total_stocks']}")
        logging.info(f"Date range: {summary['date_range']}")
        logging.info(f"Total trading days: {summary['total_days']}")
        logging.info(f"Missing values: {summary['missing_values']}")
        
        logging.info("Data processing completed successfully")
        
    except Exception as e:
        logging.error(f"Error in main: {str(e)}")
        raise

if __name__ == "__main__":
    main() 