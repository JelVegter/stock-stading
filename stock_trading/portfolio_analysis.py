from plotly.graph_objs import Figure

from common.database import sqlite3_conn
from pandas import DataFrame, Series, to_numeric, read_html
import statsmodels.api as sm
from typing import Optional
import logging
import numpy as np
from dataclasses import dataclass
from typing import Optional


def get_available_symbols() -> list[str]:
    symbols = sqlite3_conn.sql_query_to_df("SELECT DISTINCT(symbol) FROM StockHistory")
    return list(symbols["symbol"].unique())


def get_sp500_symbols() -> list[str]:
    symbols = sqlite3_conn.sql_query_to_df("SELECT DISTINCT(symbol) FROM SP500")
    return list(symbols["symbol"].unique())


def calc_total_returns_percentage(df: DataFrame) -> DataFrame:
    df = (
        df.groupby(by=["date"])
        .mean(numeric_only=True)
        .reset_index()
        .sort_values(by="date")
    )
    df["returns_percentage"] = df["price_adjclose"].pct_change(1) * 100
    df["cumulative_returns_percentage"] = (
        ((df["returns_percentage"] / 100 + 1).cumprod()) - 1
    ) * 100
    df.at[0, "returns_percentage"] = 0
    df.at[0, "cumulative_returns_percentage"] = 0
    return df


def get_sp500_stockhistory_data():
    symbols = get_sp500_symbols()
    symbols_str = "','".join(symbols)
    return sqlite3_conn.sql_query_to_df(
        f"""    SELECT strftime('%Y-%m',date) as date,
                id, symbol, price_open, price_adjclose
                FROM stockhistory
                WHERE symbol IN ('{symbols_str}')
                """
    )


@dataclass
class PortfolioAnalysis:
    found_symbols: list[str]
    history: DataFrame
    analysis: Optional[DataFrame] = None
    graph: Optional[Figure] = None

    @property
    def mean_returns(self):
        return np.exp(np.mean(np.log(self.history["returns_percentage"])))

    @property
    def mean_returns_str(self):
        return f"Mean returns for portfolio: {round(self.mean_returns,2)}%"

    @property
    def found_symbols_str(self):
        return f"Stocks in portfolio: {', '.join(self.found_symbols)}"


def get_factor_portfolio_returns() -> DataFrame:
    return sqlite3_conn.sql_query_to_df(
        """ SELECT strftime('%Y-%m',date) as date,
            mkt_rf, smb, hml, cma, rf
            FROM FFFactors
            GROUP BY strftime('%Y-%m',date), mkt_rf, smb, hml, cma, rf"""
    )


def get_portfolio_returns(
    symbols: list[str],
) -> PortfolioAnalysis:

    symbols_str = symbols
    if isinstance(symbols, list):
        symbols_str = "','".join(symbols)

    df = sqlite3_conn.sql_query_to_df(
        f"""SELECT strftime('%Y-%m',date) as date,
            id, symbol, price_open, price_adjclose
            FROM stockhistory
        WHERE symbol IN ('{symbols_str}')"""
    )

    found_symbols = list(df["symbol"].unique())
    portfolio_performance = PortfolioAnalysis(found_symbols, df)

    if len(portfolio_performance.found_symbols) == 0:
        return get_portfolio_returns(get_sp500_symbols())

    return portfolio_performance


def process_df(df: DataFrame) -> DataFrame:
    df.columns = df.columns.str.lower()
    numeric_cols = [
        "mkt_rf",
        "smb",
        "hml",
        "cma",
        "rf",
        "price_open",
        "price_adjclose",
    ]
    df[numeric_cols] = df[numeric_cols].apply(to_numeric, errors="coerce")
    df = calc_total_returns_percentage(df)
    return df


def split_df_into_X_and_y(df: DataFrame) -> tuple[DataFrame, Series]:
    df_copy = df.copy()
    y = df_copy.pop("returns_percentage")
    X = df_copy.copy()
    X = X.drop(
        columns=[
            "date",
            "price_open",
            "price_adjclose",
            "cumulative_returns_percentage",
        ]
    )
    return X, y


def run_ols_regression(y, X) -> sm.regression.linear_model.RegressionResults:
    X = sm.add_constant(X, prepend=False)
    model = sm.OLS(y, X, missing="drop")
    res = model.fit()
    logging.debug(res.summary())
    return res


def get_sp500_performance():
    df = get_sp500_stockhistory_data()
    df = calc_total_returns_percentage(df)
    return df


def get_portfolio_performance(symbols: list[str]) -> PortfolioAnalysis:
    pf_analysis = main(symbols)
    pf_analysis.history = pf_analysis.history.sort_values("date", ascending=False)
    return pf_analysis


def combine_portfolio_performance_with_benchmark(
    df: DataFrame, benchmark: DataFrame
) -> DataFrame:
    df = df.merge(benchmark, how="left", on="date", suffixes=("", "_benchmark"))
    return df


def main(symbols: Optional[list[str]] = None):
    factor_pf_returns = get_factor_portfolio_returns()
    pf_analysis = get_portfolio_returns(symbols)
    pf_analysis.history = pf_analysis.history.merge(
        factor_pf_returns, how="inner", on="date"
    )

    pf_analysis.history = process_df(pf_analysis.history)
    X, y = split_df_into_X_and_y(pf_analysis.history)
    model = run_ols_regression(y, X)
    summary = model.summary().tables[1].as_html()
    pf_analysis.analysis = read_html(summary, header=0)[0].rename(
        columns={"Unnamed: 0": "var"}
    )
    return pf_analysis


if __name__ == "__main__":
    main(["AAPL", "MSFT"])
