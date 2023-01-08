from dataclasses import dataclass
from typing import Union
from common.sqlite import SQLDBConnection, sqlite3_conn
import logging

StockContract = """
CREATE TABLE IF NOT EXISTS StockContract (
id VARCHAR(40) NOT NULL,
conid INT NOT NULL,
symbol VARCHAR(5) NOT NULL,
name VARCHAR(15) NOT NULL,
chineseName VARCHAR(15) NULL,
assetClass VARCHAR(15) NOT NULL,
exchange VARCHAR(15) NULL,
isUS INT NULL,
_ts VARCHAR(30) NOT NULL
);"""


StockHistory = """
CREATE TABLE IF NOT EXISTS StockHistory (
id VARCHAR(40) NOT NULL,
conid INT NOT NULL,
serverId VARCHAR(15) NULL,
symbol VARCHAR(15) NOT NULL,
text VARCHAR(15) NOT NULL,
priceFactor INT NULL,
chartAnnotations VARCHAR(100) NULL,
startTime VARCHAR(20) NOT NULL,
high VARCHAR(50) NOT NULL,
low VARCHAR(50) NOT NULL,
timePeriod VARCHAR(15) NOT NULL,
barLength INT NOT NULL,
mdAvailability VARCHAR(15) NULL,
mktDataDelay INT NULL,
outsideRth INT NULL,
volumeFactor INT NULL,
priceDisplayRule INT NULL,
priceDisplayValue VARCHAR(15) NULL,
negativeCapable INT NULL,
messageVersion INT NULL,
price_open DECIMAL(6,2) NOT NULL,
price_close DECIMAL(6,2) NOT NULL,
price_high DECIMAL(6,2) NOT NULL,
price_low DECIMAL(6,2) NOT NULL,
volume DECIMAL(6,2) NOT NULL,
datetime VARCHAR(20) NOT NULL,
points INT NOT NULL,
travelTime INT NOT NULL,
_ts VARCHAR(20) NOT NULL
);"""

SP500 = """
CREATE TABLE IF NOT EXISTS SP500 (
id VARCHAR(40) NOT NULL,
symbol VARCHAR(5) NOT NULL,
security VARCHAR(15) NOT NULL,
sec_filings VARCHAR(15) NULL,
gics_sector VARCHAR(30) NULL,
gics_sub_industry VARCHAR(30) NULL,
headquarters_location VARCHAR(30) NULL,
date_first_added VARCHAR(20) NULL,
cik VARCHAR(30) NULL,
founded VARCHAR(10) NULL,
_ts VARCHAR(20) NOT NULL
);"""

FFFactors = """
CREATE TABLE IF NOT EXISTS FFFactors (
id VARCHAR(40) NOT NULL,
date VARCHAR(20) NOT NULL,
mkt_rf DECIMAL(10,2) NOT NULL,
smb DECIMAL(10,2) NOT NULL,
hml DECIMAL(10,2) NOT NULL,
rmw DECIMAL(10,2) NOT NULL,
cma DECIMAL(10,2) NOT NULL,
rf DECIMAL(10,2) NOT NULL,
_ts VARCHAR(30) NOT NULL
);"""


@dataclass
class DatabaseTable:
    name: str
    create_query: str
    schema: str = ""


def create_database_tables(
    db_conn: SQLDBConnection, db_tables: Union[DatabaseTable, list[DatabaseTable]]
) -> None:
    db_tables = [db_tables] if isinstance(db_tables, DatabaseTable) else db_tables
    for table in db_tables:
        db_conn.execute_query(table.create_query)
        logging.debug(f"Created database table: {table.name}")


def main():
    table_definitions = {
        "StockContract": StockContract,
        "StockHistory": StockHistory,
        "SP500": SP500,
        "FFFactors": FFFactors,
    }
    db_tables = [DatabaseTable(k, v) for k, v in table_definitions.items()]
    create_database_tables(sqlite3_conn, db_tables)


if __name__ == "__main__":
    main()
