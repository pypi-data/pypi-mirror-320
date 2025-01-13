import os
import logging
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pybacktestchain.data_module import DataModule, Information, get_stocks_data
from pybacktestchain.broker import Broker
from numba import njit

#Setting up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

#Created functions with Numba optimisation
@njit

#Function to process the trade signals for each trading day and to calculate the value of the porfolio.
def process_signals(trading_days, signals, prices, initial_cash, asset_quantity=1):
    #trading_days (list): trading days to process.
    #signals (dict): containing buy/sell signals by date.
    #prices (dict): prices by date.
    #initial_cash (float): initial amount of cash in the portfolio.
    #asset_quantity (int): quantity of assets to buy/sell.

    portfolio_values = []
    for t in trading_days:
        #Checking if there is a signal for the current trading day
        if t in signals:
            signal = signals[t]
            if signal == "Buy":
                #Decreasing cash by the price of the asset multiplied by the quantity for a buy order
                initial_cash -= prices[t] * asset_quantity
            elif signal == "Sell":
                #Increasing cash by the price of the asset multiplied by the quantity for a sell order

                initial_cash += prices[t] * asset_quantity
        portfolio_values.append(initial_cash)
    return portfolio_values

#Function to get the next available trading day if data is missing
def get_next_trading_day(current_date, trading_days):
    #Converting trading_days to a set for faster lookup and sorting them
    trading_days_sorted = sorted(trading_days)

    next_day = current_date + timedelta(days=1)
    
    #Looping until a valid trading day is found
    while next_day not in trading_days_sorted:
        next_day += timedelta(days=1)

    return next_day

class Backtest:
    def __init__(self, initial_date, final_date, universe, portfolio_budget, name_blockchain='backtest', verbose=True):
        #initial_date (datetime): starting date for backtest
        #final_date (datetime): end date for the backtest
        #universe (list): list of assets to include in the backtest
        #portfolio_budget (float): initial budget for the portfolio
        ##name_blockchain (str): name for the blockchain (default 'backtest')

        self.initial_date = initial_date
        self.final_date = final_date
        self.universe = universe
        self.initial_cash = portfolio_budget
        self.name_blockchain = name_blockchain
        self.verbose = verbose
        self.broker = Broker(cash=self.initial_cash, verbose=self.verbose)
        self.broker.initialize_blockchain(self.name_blockchain)
        self.portfolio_values = []
        self.dates = []

def run_backtest(self, signals):
    logging.info(f"Running backtest from {self.initial_date} to {self.final_date}.")
    
    #Retrieving price data
    df = get_stocks_data(self.universe, self.initial_date.strftime('%Y-%m-%d'), self.final_date.strftime('%Y-%m-%d'))
    
    if df.empty:
        logging.error("No data retrieved for the given universe and date range.")
        return
    
    df['Date'] = pd.to_datetime(df['Date'])
    #Creating a range of valid trading days within the specified period

    trading_days = pd.date_range(start=self.initial_date, end=self.final_date, freq='B')  # all valid trading days
    df = df[df['Date'].isin(trading_days)]  # filter valid trading days
    
    if df.empty:
        logging.error("No valid trading data available for the selected period.")
        return

    data_module = DataModule(df)
    info = Information(s=self.initial_cash, data_module=data_module)

    #optimising price fetching logic (only for available dates in df)
    prices = {t: info.get_prices(t) for t in trading_days if t in df['Date'].values}

    # Backtest logic
    for t in trading_days:
        if t not in df['Date'].values:
            logging.warning(f"Data for {t} is missing, finding next valid day.")
            t = get_next_trading_day(t, trading_days)
            logging.info(f"Using data for {t} instead of missing day.")
        
        if t in signals:
            signal = signals[t]
            try:
                portfolio_value = self.broker.get_portfolio_value(prices)
                if signal == "Buy":
                    logging.info(f"Executing a buy order for portfolio value: {portfolio_value} on {t}.")
                    self.broker.execute_portfolio(portfolio_value, prices[t], t)
                elif signal == "Sell":
                    logging.info(f"Executing a sell order for portfolio value: {-portfolio_value} on {t}.")
                    self.broker.execute_portfolio(-portfolio_value, prices[t], t)
            except Exception as e:
                logging.error(f"Error processing signal on {t}: {e}")
                continue

    def plot_portfolio_value(self, testing=False):
        if not self.portfolio_values:
            logging.error("No portfolio values to plot.")
            return

        plt.figure(figsize=(14, 7))
        plt.plot(self.dates, self.portfolio_values, label='Portfolio value', color='blue')

        plt.title('Portfolio value over time')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value ($)')

        plt.legend()
        plt.grid()
        plt.show()

        if not testing:
            plt.show() 