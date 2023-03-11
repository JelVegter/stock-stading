import pandas as pd

from common.database import sqlite3_conn


def get_factor_portfolio_returns() -> pd.DataFrame:
    df = sqlite3_conn.sql_query_to_df(
        """ SELECT strftime('%Y-%m',date) as Date,
            mkt_rf, smb, hml, cma, rf
            FROM FFFactors
            GROUP BY strftime('%Y-%m',date), mkt_rf, smb, hml, cma, rf"""
    )
    df.set_index("Date", inplace=True)
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].astype(float)

    return df


def get_portfolio_returns(
    symbols: list[str],
) -> pd.DataFrame:

    symbols_str = symbols
    if isinstance(symbols, list):
        symbols_str = "','".join(symbols)

    return sqlite3_conn.sql_query_to_df(
        f"""SELECT strftime('%Y-%m',date) as Date,
            id, symbol, price_open, price_close
            FROM stockhistory
        WHERE symbol IN ('{symbols_str}')"""
    )
