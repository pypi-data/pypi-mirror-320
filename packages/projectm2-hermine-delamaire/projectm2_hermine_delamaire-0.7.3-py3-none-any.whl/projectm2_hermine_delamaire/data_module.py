#%%
import yfinance as yf
import pandas as pd 
from sec_cik_mapper import StockMapper
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging 
from scipy.optimize import minimize
import numpy as np

# Setup logging
logging.basicConfig(level=logging.INFO)

#---------------------------------------------------------
# Constants
#---------------------------------------------------------

UNIVERSE_SEC = list(StockMapper().ticker_to_cik.keys())

#---------------------------------------------------------
# Functions
#---------------------------------------------------------

# function that retrieves historical data on prices for a given stock
def get_stock_data(ticker, start_date, end_date):
    """get_stock_data retrieves historical data on prices for a given stock

    Args:
        ticker (str): The stock ticker
        start_date (str): Start date in the format 'YYYY-MM-DD'
        end_date (str): End date in the format 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: A pandas dataframe with the historical data

    Example:
        df = get_stock_data('AAPL', '2000-01-01', '2020-12-31')
    """
    stock = yf.Ticker(ticker)
    data = stock.history(start=start_date, end=end_date, auto_adjust=False, actions=False)
    # as dataframe 
    df = pd.DataFrame(data)
    df['ticker'] = ticker
    df.reset_index(inplace=True)
    return df

def get_stocks_data(tickers, start_date, end_date):
    """get_stocks_data retrieves historical data on prices for a list of stocks

    Args:
        tickers (list): List of stock tickers
        start_date (str): Start date in the format 'YYYY-MM-DD'
        end_date (str): End date in the format 'YYYY-MM-DD'

    Returns:
        pd.DataFrame: A pandas dataframe with the historical data

    Example:
        df = get_stocks_data(['AAPL', 'MSFT'], '2000-01-01', '2020-12-31')
    """
    # get the data for each stock
    # try/except to avoid errors when a stock is not found
    dfs = []
    for ticker in tickers:
        try:
            df = get_stock_data(ticker, start_date, end_date)
            # append if not empty
            if not df.empty:
                dfs.append(df)
        except:
            logging.warning(f"Stock {ticker} not found")
    # concatenate all dataframes
    data = pd.concat(dfs)
    return data

# test 
# get_stocks_data(['AAPL', 'MSFT'], '2000-01-01', '2020-12-31')
#---------------------------------------------------------
# Classes 
#---------------------------------------------------------

# Class that represents the data used in the backtest. 
@dataclass
class DataModule:
    data: pd.DataFrame

# Interface for the information set 
@dataclass
class Information:
    s: timedelta = timedelta(days=360) # Time step (rolling window)
    data_module: DataModule = None # Data module
    time_column: str = 'Date'
    company_column: str = 'ticker'
    adj_close_column: str = 'Adj Close'

    def slice_data(self, t : datetime):
        # Get the data module 
        data = self.data_module.data
        # Get the time step 
        s = self.s

        # Convert both `t` and the data column to timezone-aware, if needed
        if t.tzinfo is not None:
            # If `t` is timezone-aware, make sure data is also timezone-aware
            data[self.time_column] = pd.to_datetime(data[self.time_column]).dt.tz_localize(t.tzinfo.zone, ambiguous='NaT', nonexistent='NaT')
        else:
            # If `t` is timezone-naive, ensure the data is timezone-naive as well
            data[self.time_column] = pd.to_datetime(data[self.time_column]).dt.tz_localize(None)
        
        # Get the data only between t-s and t
        data = data[(data[self.time_column] >= t - s) & (data[self.time_column] < t)]
        return data

    def get_prices(self, t : datetime):
        # gets the prices at which the portfolio will be rebalanced at time t 
        data = self.slice_data(t)
        
        # get the last price for each company
        prices = data.groupby(self.company_column)[self.adj_close_column].last()
        # to dict, ticker as key price as value 
        prices = prices.to_dict()
        return prices

    def compute_information(self, t : datetime):  
        pass

    def compute_portfolio(self, t : datetime,  information_set : dict):
        pass

       
        
@dataclass
class FirstTwoMoments(Information):
    def compute_portfolio(self, t:datetime, information_set):
        try:
            mu = information_set['expected_return']
            Sigma = information_set['covariance_matrix']
            gamma = 1 # risk aversion parameter
            n = len(mu)
            # objective function
            obj = lambda x: -x.dot(mu) + gamma/2 * x.dot(Sigma).dot(x)
            # constraints
            cons = ({'type': 'eq', 'fun': lambda x: np.sum(x) - 1})
            # bounds, allow short selling, +- inf 
            bounds = [(0.0, 1.0)] * n
            # initial guess, equal weights
            x0 = np.ones(n) / n
            # minimize
            res = minimize(obj, x0, constraints=cons, bounds=bounds)

            # prepare dictionary 
            portfolio = {k: None for k in information_set['companies']}

            # if converged update
            if res.success:
                for i, company in enumerate(information_set['companies']):
                    portfolio[company] = res.x[i]
            else:
                raise Exception("Optimization did not converge")

            return portfolio
        except Exception as e:
            # if something goes wrong return an equal weight portfolio but let the user know 
            logging.warning("Error computing portfolio, returning equal weight portfolio")
            logging.warning(e)
            return {k: 1/len(information_set['companies']) for k in information_set['companies']}

    def compute_information(self, t : datetime):
        # Get the data module 
        data = self.slice_data(t)
        # the information set will be a dictionary with the data
        information_set = {}

        # sort data by ticker and date
        data = data.sort_values(by=[self.company_column, self.time_column])

        # expected return per company
        data['return'] =  data.groupby(self.company_column)[self.adj_close_column].pct_change() #.mean()
        
        # expected return by company 
        information_set['expected_return'] = data.groupby(self.company_column)['return'].mean().to_numpy()

        # covariance matrix

        # 1. pivot the data
        data = data.pivot(index=self.time_column, columns=self.company_column, values=self.adj_close_column)
        # drop missing values
        data = data.dropna(axis=0)
        # 2. compute the covariance matrix
        covariance_matrix = data.cov()
        # convert to numpy matrix 
        covariance_matrix = covariance_matrix.to_numpy()
        # add to the information set
        information_set['covariance_matrix'] = covariance_matrix
        information_set['companies'] = data.columns.to_numpy()
        return information_set


@dataclass
class MomentumStrategy(Information):
    # Default look-back period in days
    look_back_period: int = 90   

    def compute_portfolio(self, t:datetime):
        logging.info(f"Computing portfolio for time {t} with look-back period {self.look_back_period} days.")

        # Define look-back period start
        look_back_start = t - timedelta(days=self.look_back_period)

        # Get the data module 
        data = self.data_module.data
        logging.debug(f"Data module contains {len(data)} rows.")

        # Convert dataframe into datetime format
        data[self.time_column] = pd.to_datetime(data[self.time_column])

        # Get the data between look_back_start and t 
        sliced_data = data[(data[self.time_column] >= look_back_start) & (data[self.time_column] < t)]
        logging.debug(f"Sliced data contains {len(sliced_data)} rows.")

        if sliced_data.empty:
            logging.warning(f"No data available for look-back period ending at time {t}")
            return {}
        
        # Past returns 
        sliced_data['return'] = sliced_data.groupby(self.company_column)[self.adj_close_column].pct_change()
        mean_returns = sliced_data.groupby(self.company_column)['return'].mean()

        # We don't want negative or null returns so we exclude them
            # negative returns are set to 0
        mean_returns = mean_returns.clip(lower = 0) 
        total_return = mean_returns.sum()

        if total_return == 0:
            logging.warning(f"For the period ending at time {t}, all returns are zero or negative")
            weights = {ticker: 1 / len(mean_returns) for ticker in mean_returns.index}
            print(f"Equal weights applied due to zero/negative returns: {weights}")
            return weights

        # Calculate weights and put them in a dictionnary
        weights = (mean_returns / total_return).to_dict()
        logging.info(f"Computed portfolio weights: {weights}")
        return weights
    
@dataclass
class MeanReversionStrategy(Information):
    # Default look-back period in days
    look_back_period: int = 90  

    def compute_portfolio(self, t: datetime):
        logging.info(f"[MeanReversionStrategy] Computing portfolio for time {t}.")
        
        # Define look-back period start
        look_back_start = t - timedelta(days=self.look_back_period)

        # Get the data module
        data = self.data_module.data

        # Convert dataframe into datetime format
        data[self.time_column] = pd.to_datetime(data[self.time_column])

        # Get the data between look_back_start and t
        sliced_data = data[(data[self.time_column] >= look_back_start) & (data[self.time_column] < t)]

        if sliced_data.empty:
            logging.warning(f"No data available for look-back period ending at time {t}. Returning empty portfolio.")
            return {}

        # Calculate rolling mean and current prices
        mean_prices = sliced_data.groupby(self.company_column)[self.adj_close_column].mean()
        current_prices = sliced_data.groupby(self.company_column)[self.adj_close_column].last()

        # Calculate z-scores for mean reversion
        z_scores = (mean_prices - current_prices) / mean_prices
        z_scores = z_scores.clip(lower=0)  # We only consider underpriced assets

        total_z_score = z_scores.sum()
        if total_z_score == 0:
            logging.warning(f"No assets show reversion potential at {t}. Returning equal weights.")
            return {ticker: 1 / len(mean_prices) for ticker in mean_prices.index}

        # Calculate portfolio weights
        weights = (z_scores / total_z_score).to_dict()
        logging.info(f"[MeanReversionStrategy] Computed portfolio weights: {weights}")
        return weights
 
@dataclass
class EqualWeightStrategy(Information):
    def compute_portfolio(self, t: datetime):
        logging.info(f"[EqualWeightStrategy] Computing portfolio for time {t}.")

        # Get the list of all the companies
        companies = self.data_module.data[self.company_column].unique()

        # Assign equal weights to all the companies
        weights = {ticker: 1 / len(companies) for ticker in companies}
        logging.info(f"[EqualWeightStrategy] Computed portfolio weights: {weights}")
        return weights

        







# %%
