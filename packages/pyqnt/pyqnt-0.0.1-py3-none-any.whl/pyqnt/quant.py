from scipy.optimize import minimize
from scipy.signal import argrelextrema
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def annual_rets(weights, mean_returns):
    """
    Returns annual return of tickers.
    """
    return (weights.T @ mean_returns) * 252

def annual_vols(weights, covariance_matrix):
    """
    Returns annual volatility of tickers.
    """
    return np.sqrt(weights.T @ (covariance_matrix @ weights)) * np.sqrt(252)

def portfolio(data, risk_free_rate=0.2, method='gmv', budget=0):
    """
    Returns weights of the portfolio.
    
    Parameters
    ----------
    data : DataFrame
        Price history of multiple stocks.
    risk_free_rate : float
        Annual risk-free rate.
    method : str
        - 'msr' : maximum sharpe ratio
        - 'gmv' : global minimum variance (default)
    budget : int
        
    Returns
    -------
    DataFrame of optimized weights and name of tickers.
    """
    # data preparation
    returns = data.pct_change()
    covariance_matrix = returns.cov()
    mean_returns = returns.mean()
    num_assets = len(mean_returns)
    
    # maximum sharpe ratio method
    if method == 'msr':
        # optimization
        initial_guess = np.repeat(1/num_assets, num_assets)
        args = (mean_returns, covariance_matrix, risk_free_rate)
        constraints = ({'type': 'eq', 
                        'fun': lambda weights: np.sum(weights) - 1})
        bounds = ((0.0, 1.0),) * num_assets

        def negative_sharpe_ratio(weights, mean_returns, covariance_matrix, risk_free_rate):
            portfolio_return = annual_rets(weights, mean_returns)
            portfolio_variance = annual_vols(weights, covariance_matrix)
            return -(portfolio_return - risk_free_rate) / portfolio_variance

        result = minimize(negative_sharpe_ratio, 
                          initial_guess, 
                          args=args, 
                          method='SLSQP', 
                          bounds=bounds, 
                          constraints=constraints)
        
    # global minimum variance method
    else:
        # optimization
        initial_guess = np.repeat(1/num_assets, num_assets)
        args = (covariance_matrix)
        constraints = ({'type': 'eq', 
                        'fun': lambda x: np.sum(x) - 1})
        bounds = ((0.0, 1.0),) * num_assets

        result = minimize(annual_vols, 
                          initial_guess, 
                          args=args,
                          method='SLSQP', 
                          bounds=bounds, 
                          constraints=constraints)

    weights = np.round(result.x, 2)

    df = pd.DataFrame({'ticker': [c for c in data.columns],
                         'weight': weights})
    df = df[df['weight']>0]
    
    if budget != 0:
        df['amount'] = df['weight'] * budget
    return df