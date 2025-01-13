import logging
from datetime import datetime
import pandas as pd
from trading_strategy.signal_generator import TradingSignalGenerator
from pybacktestchain.data_module import get_stocks_data

# Setup logging
logging.basicConfig(level=logging.INFO)

def main():
    #Asking the user to enter the indices to analyse
    index1 = input("Enter the first index: ")
    index2 = input("Enter the second index: ")
    
    #Asking the user to enter the date range for the analysis
    start_date_input = input("Enter the start date (YYYY-MM-DD): ")
    end_date_input = input("Enter the end date (YYYY-MM-DD): ")

    try:
        #Converting input date strings into pandas Timestamps for better processing afterwards
        start_date = pd.to_datetime(start_date_input).normalize()
        end_date = pd.to_datetime(end_date_input).normalize()
    except Exception as e:
        logging.error(f"Error in date conversion: {e}")
        return

    logging.info(f"Date range selected: {start_date.date()} to {end_date.date()}")

    try:
        #Asking user to enter the maximum amount he wants to invest
        max_investment = float(input("Maximum amount you want to invest: "))
    except ValueError:
        logging.error("Invalid input for maximum investment.")
        return

    logging.info(f"Fetching historical data for {index1} and {index2} between {start_date.date()} and {end_date.date()}.")
    
    try:
        #Getting historical data for the first and second indices within the provided date range
        data_first = get_stocks_data([index1], start_date, end_date)
        data_second = get_stocks_data([index2], start_date, end_date)

        #Checking if any data was fetched
        if data_first.empty:
            raise ValueError(f"No data fetched for {index1}. Please check the ticker and date range.")
        if data_second.empty:
            raise ValueError(f"No data fetched for {index2}. Please check the ticker and date range.")

        #Removing timezone info from 'Date' and dropping duplicates
        data_first['Date'] = pd.to_datetime(data_first['Date']).dt.tz_localize(None)
        data_second['Date'] = pd.to_datetime(data_second['Date']).dt.tz_localize(None)

        data_first = data_first.drop_duplicates(subset='Date', keep='last')
        data_second = data_second.drop_duplicates(subset='Date', keep='last')

        #Checking for the 'Close' column
        if 'Close' not in data_first.columns or 'Close' not in data_second.columns:
            raise ValueError("Close price column is missing in the fetched data.")

        #Renaming closing price columns for clarity
        data_first.rename(columns={'Close': f'{index1}_Close'}, inplace=True)
        data_second.rename(columns={'Close': f'{index2}_Close'}, inplace=True)

        #Merging data on the 'Date' column
        combined_data = pd.merge(data_first[['Date', f'{index1}_Close']], 
                                  data_second[['Date', f'{index2}_Close']], 
                                  on='Date', how='inner')

        #Ensuring that expected columns are present after the merge
        expected_columns = [f'{index1}_Close', f'{index2}_Close']
        missing_columns = [col for col in expected_columns if col not in combined_data.columns]
        if missing_columns:
            raise ValueError(f"Missing columns after merging: {', '.join(missing_columns)}")

        logging.info(f"Combined data preview:\n{combined_data.head()}")

    except Exception as e:
        logging.error(f"Error during data fetching or processing: {e}")
        return

    #Performing the regression analysis
    try:
        signal_generator = TradingSignalGenerator(
            index1=index1,
            index2=index2,
            start_date=start_date,
            end_date=end_date,
            portfolio_budget=max_investment
        )

        #Executing the regression and saving the beta and intercept
        slope, intercept = signal_generator.perform_regression()
        logging.info(f"Regression results: Slope: {slope}, Intercept: {intercept}")
    except Exception as e:
        logging.error(f"Error during regression: {e}")


#This block ensures that the main function is executed when the script is run directly
if __name__ == '__main__':
    main()
