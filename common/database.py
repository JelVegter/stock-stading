import sqlite3
import psycopg2
from common.dt import format_datetime
from pandas import DataFrame, read_sql, read_sql_query
import pandas as pd
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod
from sqlalchemy import create_engine
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from pandas import DataFrame
from common.dt import format_datetime


class DBConnection(ABC):
    @abstractmethod
    def __init__(self):
        ...

    def execute_query(self, query: str):
        ...

    def fetch_tables_in_db(self) -> list[str]:
        ...

    def df_to_sql_table(self, df: DataFrame, table: str, if_exists: str = "append"):
        ...

    def sql_query_to_df(self, query: str) -> DataFrame:
        ...

    def sql_table_to_df(self, table: str, limit: int = None) -> DataFrame:
        ...

    def deduplicate_table(self, table: str, column: str = "id") -> None:
        ...


class PostgresDBConnection(DBConnection):
    def __init__(
        self, db_host: str, db_port: int, db_name: str, db_user: str, db_password: str
    ):
        self.db_host = db_host
        self.db_port = db_port
        self.db_name = db_name
        self.db_user = db_user
        self.engine = create_engine(
            f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
        )
        self.Session = sessionmaker(bind=self.engine)

    def execute_query(self, query: str):
        with self.Session() as session:
            result = session.execute(text(query))
            return result.fetchall()

    def fetch_tables_in_db(self) -> list[str]:
        query = """ SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public';
                 """
        return [row[0] for row in self.execute_query(query)]

    def df_to_sql_table(self, df: DataFrame, table: str, if_exists: str = "append"):
        df.to_sql(name=table, con=self.engine, if_exists=if_exists, index=False)

    def sql_query_to_df(self, query: str) -> DataFrame:
        with self.Session() as session:
            result = session.execute(text(query))
            data = result.fetchall()
            return DataFrame.from_records(data, columns=list(result.keys()))

    def sql_table_to_df(self, table: str, limit: int = None) -> DataFrame:
        limit = f"LIMIT {limit}" if limit else ""
        query = f'SELECT * FROM "{table}" {limit}'
        return self.sql_query_to_df(query)

    def deduplicate_table(self, table: str, column: str = "id") -> None:
        query = f"""DELETE FROM "{table}"
                    WHERE ctid NOT IN (
                        SELECT min(ctid)
                        FROM "{table}"
                        GROUP BY {column}
                        HAVING COUNT(*) > 1
                    )"""
        self.execute_query(query)


DB_CONN = PostgresDBConnection(
    db_host="stocktrading-db-dev-eu.cwixl1k0d3ug.eu-central-1.rds.amazonaws.com",
    db_port=5432,
    db_name="stocktrading",
    db_user="edu",
    db_password="password",
)
