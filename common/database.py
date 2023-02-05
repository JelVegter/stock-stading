import sqlite3
from common.dt import format_datetime
from pandas import DataFrame, read_sql, read_sql_query
from typing import Optional
from datetime import datetime
from abc import ABC, abstractmethod


class DBConnection(ABC):
    @abstractmethod
    def __init__(self):
        ...

    @abstractmethod
    def _fetch_cursor(self):
        ...

    @abstractmethod
    def execute_query(self):
        ...

    @abstractmethod
    def fetch_tables_in_db(self):
        ...

    @abstractmethod
    def df_to_sql_table(self):
        ...

    @abstractmethod
    def sql_table_to_df(self) -> DataFrame:
        ...

    @abstractmethod
    def sql_query_to_df(self) -> DataFrame:
        ...

    @abstractmethod
    def deduplicate_table(self):
        ...


class SQLDBConnection(DBConnection):
    def __init__(self, db_file: str):
        self.db_file = db_file

    def _fetch_cursor(self):
        with sqlite3.connect(self.db_file) as db_conn:
            return db_conn.cursor()

    def execute_query(self, query):
        cursor = self._fetch_cursor()
        cursor.execute(query)
        return cursor.fetchall()

    def fetch_tables_in_db(self) -> list[str]:
        query = """ SELECT name
                    FROM sqlite_schema
                    WHERE type ='table'
                    AND name NOT LIKE 'sqlite_%';
                    """
        return self.execute_query(query)

    def df_to_sql_table(
        self,
        df: DataFrame,
        table: str,
        schema: Optional[str] = None,
        if_exists: str = "append",
    ):
        df["_ts"] = format_datetime(datetime.now())
        with sqlite3.connect(self.db_file) as db_conn:
            df.to_sql(
                name=table, schema=schema, con=db_conn, if_exists=if_exists, index=False
            )

    def sql_query_to_df(self, query: str) -> DataFrame:
        with sqlite3.connect(self.db_file) as db_conn:
            return read_sql_query(sql=query, con=db_conn)

    def sql_table_to_df(
        self, table: str, schema: Optional[str] = None, limit: Optional[int] = None
    ) -> DataFrame:
        table = ".".join([schema, table]) if schema else table
        limit = f"LIMIT {limit}" if limit else ""
        query = f"SELECT * FROM {table} {limit}"
        with sqlite3.connect(self.db_file) as db_conn:
            return read_sql(
                sql=query,
                con=db_conn,
            )

    def deduplicate_table(self, table: str, column: str = "id") -> None:
        query = f"""DELETE FROM {table}
                    WHERE rowid NOT IN (
                        SELECT MIN(rowid)
                        FROM {table}
                        GROUP BY {column}
                        HAVING COUNT(*) > 1
                    )"""
        self.execute_query(query)


sqlite3_conn = SQLDBConnection("db/sqlite3db")
