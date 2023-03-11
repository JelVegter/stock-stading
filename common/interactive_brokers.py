from typing import Union
from common.rest_api import RestAPI
from common.models import (
    StockContract,
    StockHistory,
    StockHistoryRecord,
    Account,
    Position,
)
import json
import pandas as pd
from dataclasses import dataclass, asdict
from common.sql_queries import get_portfolio_returns
from common.calculations import calculcate_returns_percentage


@dataclass
class Portfolio:
    accounts: list[Account]
    id: str = "1"

    @property
    def positions(self) -> list[Position]:
        return [position for account in self.accounts for position in account.positions]

    @property
    def total_invested(self) -> list[Position]:
        return 1
        # return sum(position.mktValue for position in self.positions)

    @property
    def positions_and_weights(self):
        if self.total_invested == 0:
            raise ZeroDivisionError("Total invested amount cannot be zero.")

        return {
            position.ticker: (position.mktValue / self.total_invested)
            for position in self.positions
        }

    @property
    def positions_as_df(self) -> pd.DataFrame:
        records = [
            {**asdict(position), "portfolioId": self.id}
            for account in self.accounts
            for position in account.positions
        ]
        df = pd.DataFrame(records)
        # move
        first_cols = [
            "portfolioId",
            "acctId",
            "conid",
            "ticker",
            "name",
            "position",
            "mktPrice",
            "mktValue",
        ]
        ordered_cols = first_cols + [col for col in df.columns if col not in first_cols]
        df.reset_index(drop=True, inplace=True)
        return df[ordered_cols]

    def get_historical_returns(self) -> pd.DataFrame:
        symbols = list(self.positions_as_df["ticker"].unique())
        df = get_portfolio_returns(symbols)
        df = pd.pivot_table(
            df, values="price_close", index=["Date"], columns=["symbol"]
        ).reset_index()
        df.index.names = ["index"]
        df = calculcate_returns_percentage(df)
        return df


class InteractiveBrokersApi(RestAPI):
    def __init__(self):
        self.base_url = "https://localhost:5001/v1/api/"
        self.endpoints = {
            "user": "one/user",
            "tickle": "tickle",
            "validate": "portal/sso/validate",
            "accounts": "portfolio/accounts",
            "positions": "portfolio/{account}/positions/{pageId}",
            "trades": "iserver/account/trades",
            "market-data": "iserver/marketdata/snapshot",
            "stock-contracts": "trsrv/stocks",
            "market-data-history": "iserver/marketdata/history",
        }

    def fetch_stock_contracts(
        self, symbols: Union[str, list[str]]
    ) -> list[StockContract]:
        symbols = [symbols] if isinstance(symbols, str) else symbols
        stock_contracts = []
        for symbol in symbols:
            response = self.fetch_response_json(
                endpoint="stock-contracts", params={"symbols": symbol}
            )
            stock_contracts.extend(
                [
                    StockContract(
                        symbol=symbol,
                        name=stock["name"],
                        chineseName=stock["chineseName"],
                        assetClass=stock["assetClass"],
                        conid=contract["conid"],
                        exchange=contract["exchange"],
                        isUS=contract["isUS"],
                    )
                    for stock in response[symbol]
                    for contract in stock["contracts"]
                ]
            )
        return stock_contracts

    def fetch_stock_price_history(
        self, conids: Union[list[int], int], period: str = "1y", bar: str = "1m"
    ) -> list[StockHistory]:
        conids = [conids] if isinstance(conids, int) else conids
        responses = []
        for conid in conids:
            record = self.fetch_response_json(
                endpoint="market-data-history",
                params={"conid": conid, "period": period, "bar": bar},
            )
            record["conid"] = conid
            responses.append(record)
        return [StockHistory(**stock) for stock in responses]

    def fetch_accounts(self) -> list[Account]:
        # response = self.fetch_response_json(endpoint="accounts")
        # return
        with open("data/accounts.json") as f:
            response = json.load(f)
            return [Account(**account) for account in response]

    def fetch_account_positions(self, accounts: list[Account]) -> list[Account]:
        for account in accounts:
            # TODO requires paging
            # response = self.fetch_response_json(
            #     endpoint="positions", params={"account": account.id}
            # )
            with open("data/positions.json") as f:
                response = json.load(f)

            for position in response:
                if position["acctId"] == account.accountId:
                    account.positions.append(Position(**position))

        return accounts

    def fetch_portfolio(self) -> Portfolio:
        accounts = self.fetch_accounts()
        accounts_with_positions = self.fetch_account_positions(accounts)
        return Portfolio(accounts=accounts_with_positions)


ib_api = InteractiveBrokersApi()
