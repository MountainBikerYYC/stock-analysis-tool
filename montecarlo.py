import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from pandas_datareader import data as pdr
import yfinance as yf
yf.pdr_override() 

def createPortfolioSim(stocks, num_sim_portfolio):
    def get_data(stocks, start, end):
        stockData = pdr.get_data_yahoo(stocks, start, end)
        stockData = stockData['Close']
        returns = stockData.pct_change()
        meanReturns = returns.mean()
        covMatrix = returns.cov()
        return meanReturns, covMatrix

    endDate = dt.datetime.now()
    startDate = endDate - dt.timedelta(days=300)
    meanReturns, covMatrix = get_data(stocks, startDate, endDate)
    weights = np.random.random(len(meanReturns))
    weights /= np.sum(weights)

    # Monte Carlo Method
    mc_sims = num_sim_portfolio
    T = 100 #timeframe in days
    meanM = np.full(shape=(T, len(weights)), fill_value=meanReturns)
    meanM = meanM.T
    portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)
    initialPortfolio = 10000
    for m in range(0, mc_sims):
        Z = np.random.normal(size=(T, len(weights)))#uncorrelated RV's
        L = np.linalg.cholesky(covMatrix) #Cholesky decomposition to Lower Triangular Matrix
        dailyReturns = meanM + np.inner(L, Z) #Correlated daily returns for individual stocks
        portfolio_sims[:,m] = np.cumprod(np.inner(weights, dailyReturns.T)+1)*initialPortfolio

    return portfolio_sims

def singleStockSim(selectedTickerDf, num_simulations):
    daily_returns = np.diff(selectedTickerDf['Close']) / selectedTickerDf['Close'][:-1]
    mean_return = np.mean(daily_returns)
    std_deviation = np.std(daily_returns)

    # Number of simulations and days
    num_days = 100
    last_closing_price = selectedTickerDf['Close'][-1]

    # Monte Carlo simulation
    simulation_results = np.zeros((num_simulations, num_days))
    for i in range(num_simulations):
        simulated_prices = [last_closing_price]
        for j in range(1, num_days):
            random_return = np.random.normal(mean_return, std_deviation)
            simulated_price = simulated_prices[j - 1] * (1 + random_return)
            simulated_prices.append(simulated_price)
        simulation_results[i, :] = simulated_prices
    return simulation_results