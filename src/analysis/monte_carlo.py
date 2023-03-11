import numpy as np
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
from pandas_datareader import data as pdr

# # import data
# def get_data(stocks, start, end):
#     stockData = pdr.get_data_yahoo(stocks, start, end)
#     stockData = stockData["Close"]
#     returns = stockData.pct_change()
#     meanReturns = returns.mean()
#     covMatrix = returns.cov()
#     return meanReturns, covMatrix


# stockList = ["CBA", "BHP", "TLS", "NAB", "WBC", "STO"]
# stocks = [stock + ".AX" for stock in stockList]
# endDate = dt.datetime.now()
# startDate = endDate - dt.timedelta(days=300)
# meanReturns, covMatrix = get_data(stocks, startDate, endDate)
# weights = np.random.random(len(meanReturns))
# weights /= np.sum(weights)


def monte_carlo(weights: int, mean_returns: pd.Series, cov_matrix: pd.DataFrame):
    # Monte Carlo Method
    mc_sims = 400  # number of simulations
    T = 100  # timeframe in days
    meanM = np.full(shape=(T, len(weights)), fill_value=mean_returns)
    meanM = meanM.T
    portfolio_sims = np.full(shape=(T, mc_sims), fill_value=0.0)
    initialPortfolio = 10000

    for m in range(mc_sims):
        Z = np.random.normal(size=(T, len(weights)))  # uncorrelated RV's
        L = np.linalg.cholesky(
            cov_matrix
        )  # Cholesky decomposition to Lower Triangular Matrix
        dailyReturns = meanM + np.inner(
            L, Z
        )  # Correlated daily returns for individual stocks
        portfolio_sims[:, m] = (
            np.cumprod(np.inner(weights, dailyReturns.T) + 1) * initialPortfolio
        )
