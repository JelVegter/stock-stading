import yfinance as yf
import pandas as pd
import datetime as dt
from common.sql_queries import get_portfolio_returns, get_factor_portfolio_returns
from common.calculations import calculcate_returns_percentage
from common.database import sqlite3_conn


def convert_absolute_returns_to_perc_returns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.pct_change()[1:].dropna(axis="columns")
    return df


def convert_perc_returns_to_cumulative_perc_returns(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        df[col] = (((df[col] / 100 + 1).cumprod()) - 1) * 100
    return df


def get_sp500_symbols() -> list[str]:
    symbols = sqlite3_conn.sql_query_to_df("SELECT DISTINCT(symbol) FROM SP500")
    return list(symbols["symbol"].unique())


def fetch_stock_returns(
    symbols: list[str],
    interval: str = "1d",
    return_format: str = "absolute",  # absolute, percentage, cumulative_percentage
) -> pd.DataFrame:
    symbols = [symbols] if isinstance(symbols, str) else symbols
    symbols = [s.upper() for s in symbols]
    df: pd.DataFrame = yf.download(
        symbols, interval=interval, start="2018-01-01", end=dt.date.today()
    )["Close"]

    if isinstance(df, pd.Series):
        df = pd.DataFrame(df)
        df.columns = symbols

    if interval == "1mo":
        df.index = df.index.strftime("%Y-%m")

    if return_format == "absolute":
        return df
    elif return_format == "percentage":
        return convert_absolute_returns_to_perc_returns(df)
    elif return_format == "cumulative_percentage":
        df = convert_absolute_returns_to_perc_returns(df)
        return convert_perc_returns_to_cumulative_perc_returns(df)
    else:
        raise ValueError("Invalid return_format")


def get_sp500_stockhistory_data():
    symbols = get_sp500_symbols()
    symbols_str = "','".join(symbols)
    return sqlite3_conn.sql_query_to_df(
        f"""    SELECT strftime('%Y-%m',date) as date,
                id, symbol, price_open, price_close
                FROM stockhistory
                WHERE symbol IN ('{symbols_str}')
                """
    )


def get_sp500_performance():
    df = fetch_stock_returns(symbols=["VOO"])
    df = convert_absolute_returns_to_perc_returns(df)
    df = convert_perc_returns_to_cumulative_perc_returns(df)
    return df
