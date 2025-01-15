import numpy as np
from dataclasses import dataclass

#---------------------------------------------------------
# Classes
#---------------------------------------------------------

@dataclass
class PortfolioMetrics():
    # Portfolio initialized with portfolio values and risk free rate
    def __init__(self, portfolio_values, risk_free_rate=0.01):

        # Setting up the arguments
        self.portfolio_values = np.array(portfolio_values)
        self.risk_free_rate = risk_free_rate 
        self.returns = np.diff(self.portfolio_values) / self.portfolio_values[:-1] # daily returns of the portfolio over time
    
    def annualized_returns(self):
        total_return = self.portfolio_values[-1] / self.portfolio_values[0] - 1
        n_years = len(self.portfolio_values) / 252  # 252 trading days in a year
        return (1 + total_return) ** (1 / n_years) - 1
    
    def volatility(self):
        return np.std(self.returns) * np.sqrt(252) # annualized volatility
    
    def sharpe_ratio(self):
        excess_return = self.annualized_returns() - self.risk_free_rate
        return excess_return / self.volatility()
    
    # Measures the maximum fall in the value of the investment 
    def max_drawdown(self):
        cumulative_returns = np.maximum.accumulate(self.portfolio_values)
        drawdowns = (self.portfolio_values - cumulative_returns) / cumulative_returns
        return np.min(drawdowns)




