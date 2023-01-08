from common.ib import (
    InteractiveBrokersApi,
    StockHistory,
    StockHistoryRecord,
    StockContract,
    StockContractRecord,
    ib_api,
)
from common.db import DBConnection
from typing import Union
from pandas import DataFrame, read_html, read_fwf
from common.sqlite import sqlite3_conn
from typing import Optional
from datetime import datetime, date
import hashlib
from common.dt import format_datetime
import requests
from zipfile import ZipFile
from io import BytesIO


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
    records = []
    for stock_contract in stock_contracts:
        records.append(
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
        )
    return records


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


def transform_sp500_data_to_sql_df(
    df: DataFrame,
) -> DataFrame:
    col_mapping = {
        "SEC filings": "sec_filings",
        "GICS Sector": "gics_sector",
        "GICS Sub-Industry": "gics_sub_industry",
        "Headquarters Location": "headquarters_location",
        "GICS Sub-Industry": "gics_sub_industry",
        "Date first added": "date_first_added",
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
        table = "StockContract"
        api_data = self.api.fetch_stock_contracts(symbols)
        records = convert_stock_contracts_to_records(api_data)
        df = DataFrame(records)
        self.db_conn.df_to_sql_table(df, table=table)
        self.db_conn.deduplicate_table(table)
        return df

    def stock_price_history(
        self,
        conids: Union[list[int], int],
    ) -> DataFrame:
        table = "StockHistory"
        chunk_size = 10
        for i in range(0, len(conids), chunk_size):
            api_data = self.api.fetch_stock_price_history(
                conids[i : i + chunk_size], period="5y", bar="1m"
            )
            records = convert_stock_history_to_records(api_data)
            df = DataFrame(records)
            self.db_conn.df_to_sql_table(df, table=table)
        self.db_conn.deduplicate_table(table)
        return df

    def sp500(self) -> DataFrame:
        table = "SP500"
        html = read_html("https://en.wikipedia.org/wiki/List_of_S%26P_500_companies")
        df = transform_sp500_data_to_sql_df(html[0])
        self.db_conn.df_to_sql_table(df, table=table)
        self.db_conn.deduplicate_table(table)
        return df

    def fama_french_factors(self) -> DataFrame:
        table = "FFFactors"
        url = "http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/ftp/F-F_Research_Data_5_Factors_2x3_TXT.zip"
        response = requests.get(url)
        zip = ZipFile(BytesIO(response.content))
        _bytes = zip.read("F-F_Research_Data_5_Factors_2x3.txt")
        df = read_fwf(BytesIO(_bytes), skiprows=2, index_col=[0])
        df = transform_ff_factors_to_sql_df(df)
        self.db_conn.df_to_sql_table(df, table=table)
        self.db_conn.deduplicate_table(table)
        return df


def get_sp500_symbols(db_conn: DBConnection) -> list[str]:
    df = db_conn.sql_table_to_df(table="SP500")
    return list(df.symbol.unique())


def get_conids_for_symbols(
    db_conn: DBConnection, symbols: Optional[list[str]] = None
) -> list[str]:
    df = db_conn.sql_table_to_df(table="StockContract")
    df = df.loc[df["isUS"] == 1]
    if symbols:
        df = df.loc[df["symbol"].isin(symbols)]
    return list(df.conid.unique())


def main():
    """Fetch stock contracts from ib-api and write to sqlite3 database."""
    etl = ETL(sqlite3_conn, ib_api)

    # # Fetch S&P 500 data
    # etl.sp500()

    # # Fetch Fama French factors data
    # etl.fama_french_factors()

    # symbols = get_sp500_symbols(sqlite3_conn)

    # # Fetch stock contract data
    # # symbols = ["AAPL", "MSFT"]
    # etl.stock_contract(symbols)

    conids = get_conids_for_symbols(sqlite3_conn)
    # Fetch stock price history data
    # conids = [265598, 272093]
    etl.stock_price_history(conids=conids)


if __name__ == "__main__":
    main()
