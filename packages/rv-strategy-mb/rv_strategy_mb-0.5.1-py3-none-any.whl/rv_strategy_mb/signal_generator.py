import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import logging
import statsmodels.api as sm
from pybacktestchain.data_module import get_stocks_data
from pybacktestchain.blockchain import Blockchain

# Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TradingSignalGenerator:
    def __init__(self, index1, index2, start_date, end_date, portfolio_budget):
        #index1 (str): The first stock index to analyse
        #index2 (str): The second stock index to analyse
        #start_date (datetime): start date for the analysis
        #end_date (datetime): end date for the analysis
        #portfolio_budget (float): budget for trade

        self.index1 = index1
        self.index2 = index2
        self.start_date = start_date
        self.end_date = end_date
        self.portfolio_budget = portfolio_budget
        self.data = pd.DataFrame()  # Initialize as empty
        self.blockchain = Blockchain(name="trading_signals")

    def get_data(self):
        logging.info(f"Fetching historical data for {self.index1} and {self.index2}.")
        try:
            #Getting the combined historical data for both indices

            combined_data = get_stocks_data([self.index1, self.index2], self.start_date, self.end_date)

            # Check necessary columns
            if not all(col in combined_data.columns for col in ['Date', 'Close']):
                raise ValueError("Close price column is missing from the fetched data.")

            combined_data['Date'] = pd.to_datetime(combined_data['Date'], errors='coerce')

            if combined_data.empty:
                raise ValueError(f"No data found for {self.index1} and {self.index2} for the entered date range.")

            #pivot the DataFrame to have stock indices as columns and 'Date' as index
            data = combined_data.pivot(index='Date', columns='ticker', values='Close')
            data.columns = [f"{ticker}_Close" for ticker in data.columns]

            return data

        except Exception as e:
            logging.error(f"Error fetching or processing data: {e}")
            return pd.DataFrame()

    #Function that performs OLS regression on the historical data to calculate beta and retrieve intercept
    def perform_regression(self):
        self.data = self.get_data()
        
        if self.data.empty:
            raise ValueError("No data available for regression.")

        #Closing prices for both indices
        col1 = f'{self.index1}_Close' 
        col2 = f'{self.index2}_Close'

        #Checking that both price columns exist
        if col1 not in self.data.columns or col2 not in self.data.columns:
            raise ValueError(f"Expected columns missing: {col1}, {col2}. Available columns: {self.data.columns.tolist()}")

        #Adding a constant for intercept
        X = sm.add_constant(self.data[col1])
        Y = self.data[col2]

        #Performing regression
        model = sm.OLS(Y, X).fit()

        #Keeping slope and intercept
        slope = model.params[col1]
        intercept = model.params['const']
        logging.info(f"Regression results: Slope: {slope}, Intercept: {intercept}, R-squared: {model.rsquared}")
        
        return slope, intercept

    #Function to generate trading signals based on z-score deviation from its historical mean
    def generate_signals(self, slope: float, intercept: float):
        signals = {}
        quantities = {}

        #calculating predicted values
        col1 = f'{self.index1}_Close'
        col2 = f'{self.index2}_Close'
        self.data['Predicted Value'] = intercept + slope * self.data[col1]

        #calculating residuals and Z-score
        self.data['Residual'] = self.data[col2] - self.data['Predicted Value']
        mean_residual = self.data['Residual'].mean()
        std_residual = self.data['Residual'].std()
        self.data['Z-score'] = (self.data['Residual'] - mean_residual) / std_residual

        total_budget = self.portfolio_budget

        #Generating signals
        for index, row in self.data.iterrows():
            current_z_score = row['Z-score']
            price1 = row[col1]
            price2 = row[col2]

            if current_z_score > 2:
                #Overvalued signal: sell index 1 buy index 2
                signals[index] = "Sell"
                quantity1 = total_budget // price1
                quantity2 = quantity1 * slope
                quantities[index] = (f"Sell {quantity1} shares of {self.index1}, "
                                     f"Buy {quantity2:.2f} shares of {self.index2}.")
            elif current_z_score < -2:
                #Undervalued signal: buy index 1 sell index 2
                signals[index] = "Buy"
                quantity2 = total_budget // price2
                quantity1 = quantity2 / slope
                quantities[index] = (f"Buy {quantity1:.2f} shares of {self.index1}, "
                                     f"Sell {quantity2:.2f} shares of {self.index2}.")
            else:
                signals[index] = "Hold"
                continue

        #Log trading activity and store in blockchain
        logging.info(f"Trading signals: {signals}")
        logging.info(f"Trading quantities: {quantities}")

        self.blockchain.add_block(
            name="Trading Signal",
            data={
                "signals": signals,
                "quantities": quantities,
                "slope": slope,
                "intercept": intercept,
            },
        )

        return signals, quantities

    #Plotting
    def plot_z_score(self):
        if self.data.empty:
            raise ValueError("No data available for plotting.")

        plt.figure(figsize=(14, 7))
        plt.plot(self.data.index, self.data['Z-score'], label='Z-score', color='blue')

        #Current Z-score
        current_z_score = self.data['Z-score'].iloc[-1]
        plt.axhline(current_z_score, color='red', linestyle='--', label='Current Z-score')

        #Z-score thresholds for buy/sell
        plt.axhline(y=2, color='green', linestyle='--', label='Buy Threshold (Z-score > 2)')
        plt.axhline(y=-2, color='red', linestyle='--', label='Sell Threshold (Z-score < -2)')

        plt.title(f'Historical Z-score of {self.index1} and {self.index2}')
        plt.xlabel('Date')
        plt.ylabel('Z-score')
        plt.legend()
        plt.grid()
        plt.show()
