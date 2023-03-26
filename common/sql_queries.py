import pandas as pd

from common.database import DB_CONN


def get_factor_portfolio_returns() -> pd.DataFrame:
    df = DB_CONN.sql_query_to_df(
        """ SELECT to_char(fff.date::date, 'YYYY-MM') as date
                , fff.mkt_rf
                , fff.smb
                , fff.hml
                , fff.cma
                , fff.rf
            FROM ff_factors fff
            GROUP BY to_char(fff.date::date, 'YYYY-MM')
                , fff.mkt_rf
                , fff.smb
                , fff.hml
                , fff.cma
                , fff.rf"""
    )
    df.set_index("date", inplace=True)
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

    return DB_CONN.sql_query_to_df(
        f"""to_char(fff.date::date, 'YYYY-MM') as date
            , id
            , symbol
            , price_open
            , price_close
            FROM "stock_history"
        WHERE symbol IN ('{symbols_str}')"""
    )
