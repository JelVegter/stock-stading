import pandas as pd
import numpy as np
import datetime as dt
import yfinance as yf
import plotly.express as px
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import plotly.express as px
from src.analysis.stock_returns import (
    fetch_stock_returns,
)

# Define function to calculate returns, volatility
def portfolio_annualized_performance(
    weights: int, mean_returns: pd.Series, cov_matrix: pd.DataFrame
):
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
        daily_returns = meanM + np.inner(
            L, Z
        )  # Correlated daily returns for individual stocks
        portfolio_sims[:, m] = (
            np.cumprod(np.inner(weights, daily_returns.T) + 1) * initialPortfolio
        )
        print(portfolio_sims)
    # return std, returns


def portfolio_annualized_performance(
    weights: int, mean_returns: pd.Series, cov_matrix: pd.DataFrame
):
    # Given the avg returns, weights of equities calc. the portfolio return
    returns = np.sum(mean_returns * weights) * 252
    # Standard deviation of portfolio (using dot product against covariance, weights)
    # 252 trading days
    std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
    return std, returns


# # Define function to calculate returns, volatility
# def portfolio_annualized_performance(
#     weights: int, mean_returns: pd.Series, cov_matrix: pd.DataFrame
# ):
#     # Given the avg returns, weights of equities calc. the portfolio return
#     returns = np.sum(mean_returns * weights) * 252
#     # Standard deviation of portfolio (using dot product against covariance, weights)
#     # 252 trading days
#     std = np.sqrt(np.dot(weights.T, np.dot(cov_matrix, weights))) * np.sqrt(252)
#     return std, returns


def generate_random_portfolios(
    num_portfolios: int,
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    risk_free_rate: float,
) -> pd.DataFrame:
    # Initialize array of shape 3 x N to store our results,
    # where N is the number of portfolios we're going to simulate
    results = np.zeros((3, num_portfolios))
    # Array to store the weights of each equity
    weight_array = []
    for i in range(num_portfolios):
        # Randomly assign floats to our 4 equities
        weights = np.random.random(len(mean_returns))
        # Convert the randomized floats to percentages (summing to 100)
        weights /= np.sum(weights)
        # Add to our portfolio weight array
        weight_array.append(weights)
        # Pull the standard deviation, returns from our function above using
        # the weights, mean returns generated in this function
        portfolio_std_dev, portfolio_return = portfolio_annualized_performance(
            weights, mean_returns, cov_matrix
        )
        # Store output
        results[0, i] = portfolio_std_dev
        results[1, i] = portfolio_return
        # Sharpe ratio
        results[2, i] = (portfolio_return - risk_free_rate) / portfolio_std_dev
    weights = pd.DataFrame(weight_array)
    results = pd.DataFrame(results).T
    return pd.concat([weights, results], axis=1)


def simulate_portfolios(
    returns: pd.DataFrame,
    mean_returns: pd.Series,
    cov_matrix: pd.DataFrame,
    num_portfolios: int,
    risk_free_rate: float,
) -> pd.DataFrame:
    df = generate_random_portfolios(
        num_portfolios=num_portfolios,
        mean_returns=mean_returns,
        cov_matrix=cov_matrix,
        risk_free_rate=risk_free_rate,
    )
    cols = list(returns.columns)
    cols.extend(
        [
            "portfolio_std_dev",
            "portfolio_return",
            "sharpe_ratio",
        ]
    )
    df.columns = cols
    return df


def calculate_efficient_frontier(
    symbols: list[str], num_portfolios: int = 10_000, risk_free_rate: float = 0.018
) -> pd.DataFrame:

    df = fetch_stock_returns(symbols, return_format="percentage")
    # df = convert_absolute_returns_to_perc(df)
    mean_returns = df.mean()
    cov_matrix = df.cov()
    return simulate_portfolios(
        df, mean_returns, cov_matrix, num_portfolios, risk_free_rate
    )
