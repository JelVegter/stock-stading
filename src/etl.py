from common.models import (
    StockHistory,
    StockHistoryRecord,
    StockContract,
    StockContractRecord,
)
from common.interactive_brokers import (
    InteractiveBrokersApi,
    ib_api,
)
from common.database import DBConnection
from typing import Union
import pandas as pd
from pandas import DataFrame, read_html, read_fwf, concat
from common.database import DB_CONN
from typing import Optional
from datetime import datetime, date, timedelta
import hashlib
from common.dt import format_datetime
import requests
from zipfile import ZipFile
from io import BytesIO
import logging
from yahoo_fin.stock_info import (
    get_data,
    tickers_sp500,
    tickers_nasdaq,
    tickers_other,
    tickers_dow,
    tickers_other,
    tickers_ftse100,
    tickers_ftse250,
    get_quote_table,
)


def get_hashed_id(*values) -> str:
    _str = ""
    for value in values:
        if not isinstance(value, str):
            value = str(value)
        _str = "".join([_str, value])
    _bytes = _str.encode("utf-8")
    return hashlib.md5(_bytes).hexdigest()


def convert_stock_contracts_to_records(
    stock_contracts: list[StockContract],
) -> list[StockContractRecord]:
    return [
        StockContractRecord(
            id=get_hashed_id(stock_contract.conid),
            symbol=stock_contract.symbol,
            name=stock_contract.name,
            chineseName=stock_contract.chineseName,
            assetClass=stock_contract.assetClass,
            conid=stock_contract.conid,
            exchange=stock_contract.exchange,
            isUS=stock_contract.isUS,
        )
        for stock_contract in stock_contracts
    ]


def convert_stock_history_to_records(
    stock_history: list[StockHistory],
) -> list[StockHistoryRecord]:
    records = []
    for stock in stock_history:
        for datapoint in stock.data:
            dt = format_datetime(datetime.fromtimestamp(datapoint["t"] / 1000))
            records.append(
                StockHistoryRecord(
                    id=get_hashed_id(stock.conid, dt),
                    conid=stock.conid,
                    serverId=stock.serverId,
                    symbol=stock.symbol,
                    text=stock.text,
                    priceFactor=stock.priceFactor,
                    chartAnnotations=stock.chartAnnotations,
                    startTime=stock.startTime,
                    high=stock.high,
                    low=stock.low,
                    timePeriod=stock.timePeriod,
                    barLength=stock.barLength,
                    mdAvailability=stock.mdAvailability,
                    mktDataDelay=stock.mktDataDelay,
                    outsideRth=stock.outsideRth,
                    volumeFactor=stock.volumeFactor,
                    priceDisplayRule=stock.priceDisplayRule,
                    priceDisplayValue=stock.priceDisplayValue,
                    negativeCapable=stock.negativeCapable,
                    messageVersion=stock.messageVersion,
                    points=stock.points,
                    travelTime=stock.travelTime,
                    price_open=datapoint["o"],
                    price_close=datapoint["c"],
                    price_high=datapoint["h"],
                    price_low=datapoint["l"],
                    volume=datapoint["v"],
                    datetime=dt,
                )
            )
    return records


def transform_stock_history_to_sql_df(
    df: DataFrame,
) -> DataFrame:
    df.reset_index(inplace=True)
    df["Date"] = df["index"].map(format_datetime)
    df["id"] = df.apply(lambda x: get_hashed_id(x["ticker"], x["Date"]), axis=1)
    df = df.rename(
        columns={
            "ticker": "symbol",
            "open": "price_open",
            "low": "price_low",
            "high": "price_high",
            "close": "price_close",
            "adjclose": "price_adjclose",
        }
    )
    cols = [
        "id",
        "Date",
        "symbol",
        "price_open",
        "price_low",
        "price_high",
        "price_close",
        "price_adjclose",
        "volume",
    ]
    return df[cols]


def transform_sp500_data_to_sql_df(
    df: DataFrame,
) -> DataFrame:
    col_mapping = {
        "SEC filings": "sec_filings",
        "GICS Sector": "gics_sector",
        "Headquarters Location": "headquarters_location",
        "GICS Sub-Industry": "gics_sub_industry",
        "Date first added": "date_first_added",
        "Date added": "date_added",
    }
    df = df.rename(columns=col_mapping)
    df["id"] = df.apply(lambda x: get_hashed_id(x["Security"], date.today()), axis=1)
    return df


def transform_ff_factors_to_sql_df(
    df: DataFrame,
) -> DataFrame:
    df.reset_index(inplace=True)
    df.rename(columns={"Mkt-RF": "mkt_rf"}, inplace=True)
    split_index = df.index[df["index"] == "Annua"][0]
    df = df.iloc[:split_index]
    df["date"] = df["index"].apply(
        lambda x: format_datetime(datetime.strptime(x, "%Y%m"))
    )
    df["id"] = df["date"].apply(lambda x: get_hashed_id(x))
    df = df.drop(columns="index")
    return df


class ETL:
    def __init__(self, db_conn: DBConnection, api: InteractiveBrokersApi):
        self.db_conn = db_conn
        self.api = api

    def stock_contract(self, symbols: Union[list[str], str]) -> DataFrame:
        table = "stock_contract"
        api_data = self.api.fetch_stock_contracts(symbols)
        records = convert_stock_contracts_to_records(api_data)
        df = DataFrame(records)
        df.columns = df.columns.str.lower()
        self.db_conn.df_to_sql_table(df, table=table)
        logging.info(f"Inserted {len(records)} stock contract records into {table}")
        self.db_conn.deduplicate_table(table)
        return df

    def stock_price_history(
        self,
        symbols: Union[list[str], str],
        years: int = 3,
        interval: str = "1mo",
    ) -> DataFrame:

        symbols = [symbols] if isinstance(symbols, str) else symbols
        table = "stock_history"
        today = date.today()
        df = DataFrame()
        failed_symbols = []
        for symbol in symbols:
            try:
                data = get_data(
                    symbol,
                    start_date=today - timedelta(days=365 * years),
                    end_date=today,
                    interval=interval,
                )
                df = concat([df, data])
            except Exception as e:
                failed_symbols.append((symbol, e))

        df = transform_stock_history_to_sql_df(df)
        df.columns = df.columns.str.lower()
        self.db_conn.df_to_sql_table(df, table=table)
        logging.info(f"Inserted {len(df)} stock price records into {table}")
        self.db_conn.deduplicate_table(table)
        return df

    def fetch_stock_symbols(self) -> DataFrame:
        table = "symbol"
        df = pd.DataFrame()
        ticker_sources = {
            "sp500": tickers_sp500(),
            "nasdaq": tickers_nasdaq(),
            "dow": tickers_dow(),
            "other": tickers_other(),
            # "ftse250": tickers_ftse250(),
        }
        for source, symbols in ticker_sources.items():
            row = pd.DataFrame({"symbol": symbols})
            row["source"] = source
            df = pd.concat([df, row])

        df.columns = df.columns.str.lower()
        self.db_conn.df_to_sql_table(df, table=table)
        df = self.db_conn.sql_table_to_df(table)
        return df

    def sp500(self) -> DataFrame:
        table = "sp500"
        html = read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = transform_sp500_data_to_sql_df(html[0])
        df.columns = df.columns.str.lower()
        self.db_conn.df_to_sql_table(df, table=table)
        logging.info(f"Inserted {len(df)} S&P500 records into {table}")
        df = self.db_conn.sql_table_to_df(table)
        # self.db_conn.deduplicate_table(table)
        return df

    def fama_french_factors(self) -> DataFrame:
        table = "ff_factors"
        url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_TXT.zip"
        response = requests.get(url)
        _zip = ZipFile(BytesIO(response.content))
        _bytes = _zip.read("F-F_Research_Data_5_Factors_2x3.txt")
        df = read_fwf(BytesIO(_bytes), skiprows=2, index_col=[0])
        df = transform_ff_factors_to_sql_df(df)
        df.columns = df.columns.str.lower()
        self.db_conn.df_to_sql_table(df, table=table)
        logging.info(f"Inserted {len(df)} FF factorse records into {table}")
        # self.db_conn.deduplicate_table(table)
        return df


def get_available_symbols() -> list[str]:
    db_conn: DBConnection = DB_CONN
    df = db_conn.sql_table_to_df(table="symbol")
    return list(df["symbol"].unique())


def get_sp500_symbols(db_conn: DBConnection) -> list[str]:
    df = db_conn.sql_table_to_df(table="sp500")
    return list(df["symbol"].unique())


def get_conids_for_symbols(
    db_conn: DBConnection, symbols: Optional[list[str]] = None
) -> list[str]:
    df = db_conn.sql_table_to_df(table="StockContract")
    df = df.loc[df["isUS"] == 1]
    if symbols:
        df = df.loc[df["symbol"].isin(symbols)]
    return list(df["conid"].unique())


def main():
    """Fetch data and write to sqlite3 database."""
    etl = ETL(DB_CONN, ib_api)

    # Fetch S&P 500 data
    etl.sp500()

    # Fetch Fama French factors data
    etl.fama_french_factors()

    # # Fetch stock contract data
    # symbols = get_sp500_symbols(DB_CONN)
    # etl.stock_contract(symbols)

    # Fetch stock price history data
    # symbols = ["ECNL"]
    # conids = get_conids_for_symbols(db_conn)
    # etl.stock_price_history(conids=conids, period="5y", bar="1m")
    # etl.stock_price_history(symbols=symbols, years=5, interval="1mo")

    etl.fetch_stock_symbols()


if __name__ == "__main__":
    main()
