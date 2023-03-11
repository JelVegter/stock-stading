from plotly.graph_objs import Figure

from common.sql_queries import get_portfolio_returns, get_factor_portfolio_returns
from common.calculations import calculcate_returns_percentage
from src.analysis.stock_returns import (
    get_sp500_symbols,
    fetch_stock_returns,
    convert_perc_returns_to_cumulative_perc_returns,
)
from pandas import DataFrame, Series, to_numeric, read_html
import statsmodels.api as sm
from typing import Optional
import logging
import numpy as np
from dataclasses import dataclass
import pandas as pd


@dataclass
class PortfolioAnalysis:
    cumulative_returns: DataFrame
    benchmark_portfolio: str = "VOO"
    interval: str = "1mo"
    graph: Optional[Figure] = None

    @property
    def grouped_cumulative_returns(self) -> pd.DataFrame:
        df = self.cumulative_returns.copy()
        df["Portfolio"] = df.mean(axis=1)
        return pd.DataFrame(df["Portfolio"])

    @property
    def mean_returns(self):
        return np.exp(np.mean(np.log(self.grouped_cumulative_returns["Portfolio"])))

    @property
    def mean_returns_str(self):
        return f"Mean returns for portfolio: {round(self.mean_returns,2)}%"

    @property
    def benchmark_cumulative_returns(self):
        return fetch_stock_returns(
            self.benchmark_portfolio,
            return_format="cumulative_percentage",
            interval=self.interval,
        )

    @property
    def benchmark_df(self):
        return pd.concat(
            [self.benchmark_cumulative_returns, self.grouped_cumulative_returns], axis=1
        )

    @property
    def FF_factor_cumulative_returns(self):
        df = get_factor_portfolio_returns()
        df = df / 10_000
        df = convert_perc_returns_to_cumulative_perc_returns(df)
        return df

    def run_portfolio_analysis(self) -> pd.DataFrame:
        df = self.grouped_cumulative_returns.copy()
        df = df.merge(self.FF_factor_cumulative_returns, on="Date")
        X, y = split_df_into_X_and_y(df)
        model = run_ols_regression(y, X)
        summary = model.summary().tables[1].as_html()
        self.analysis = read_html(summary, header=0)[0].rename(
            columns={"Unnamed: 0": "var"}
        )
        return self.analysis


def convert_portfolio_returns_to_portfolio_analysis(df: DataFrame) -> PortfolioAnalysis:
    return PortfolioAnalysis(df)


def process_df(df: DataFrame) -> DataFrame:
    df.columns = df.columns.str.lower()
    numeric_cols = [
        "mkt_rf",
        "smb",
        "hml",
        "cma",
        "rf",
        "price_open",
        "price_close",
    ]
    df[numeric_cols] = df[numeric_cols].apply(to_numeric, errors="coerce")
    # df = calc_cumulative_returns_percentage(df)
    return df


def split_df_into_X_and_y(df: DataFrame) -> tuple[DataFrame, Series]:
    print(df)
    df_copy = df.copy()
    y = df_copy.pop("Portfolio")
    X = df_copy.copy()
    return X, y


def run_ols_regression(y, X) -> sm.regression.linear_model.RegressionResults:
    X = sm.add_constant(X, prepend=False)
    model = sm.OLS(y, X, missing="drop")
    res = model.fit()
    logging.debug(res.summary())
    return res


def get_portfolio_performance(symbols: list[str]) -> PortfolioAnalysis:
    pf_analysis = main(symbols)
    pf_analysis.cumulative_returns = pf_analysis.cumulative_returns.sort_values(
        "Date", ascending=False
    )
    return pf_analysis


def combine_portfolio_performance_with_benchmark(
    df: DataFrame, benchmark: DataFrame
) -> DataFrame:
    df = df.merge(benchmark, how="left", on="Date", suffixes=("", "_benchmark"))
    return df


def main(symbols: Optional[list[str]] = None):
    factor_pf_returns = get_factor_portfolio_returns()
    portfolio_returns = fetch_stock_returns(symbols)

    pf_analysis = convert_portfolio_returns_to_portfolio_analysis(portfolio_returns)
    pf_analysis.cumulative_returns = pf_analysis.cumulative_returns.merge(
        factor_pf_returns, how="inner", on="Date"
    )

    pf_analysis.cumulative_returns = process_df(pf_analysis.cumulative_returns)

    X, y = split_df_into_X_and_y(pf_analysis.cumulative_returns)
    model = run_ols_regression(y, X)
    summary = model.summary().tables[1].as_html()
    pf_analysis.analysis = read_html(summary, header=0)[0].rename(
        columns={"Unnamed: 0": "var"}
    )
    return pf_analysis


if __name__ == "__main__":
    main(["AAPL", "MSFT"])
