from typing import Union, Optional
from dataclasses import dataclass, field
from common.rest_api import RestAPI


@dataclass
class StockContract:
    symbol: str
    name: str
    assetClass: str
    conid: int
    exchange: str
    isUS: bool
    chineseName: Optional[str] = None


@dataclass
class StockContractRecord:
    id: str
    symbol: str
    name: str
    assetClass: str
    conid: int
    exchange: str
    isUS: bool
    chineseName: Optional[str] = None


@dataclass
class StockHistory:
    conid: int
    symbol: str
    text: str
    data: list[dict[str, float]]
    serverId: Optional[str] = None
    priceFactor: Optional[int] = None
    chartAnnotations: Optional[str] = None
    startTime: Optional[str] = None
    high: Optional[str] = None
    low: Optional[str] = None
    timePeriod: Optional[str] = None
    barLength: Optional[int] = None
    mdAvailability: Optional[str] = None
    mktDataDelay: Optional[int] = None
    outsideRth: Optional[bool] = None
    volumeFactor: Optional[int] = None
    priceDisplayRule: Optional[int] = None
    priceDisplayValue: Optional[str] = None
    negativeCapable: Optional[bool] = None
    messageVersion: Optional[int] = None
    points: Optional[int] = None
    travelTime: Optional[int] = None


@dataclass
class StockHistoryRecord:
    id: int
    conid: int
    serverId: str
    symbol: str
    text: str
    price_open: float
    price_close: float
    price_high: float
    price_low: float
    volume: int
    datetime: str
    priceFactor: Optional[int] = None
    chartAnnotations: Optional[str] = None
    startTime: Optional[str] = None
    high: Optional[str] = None
    low: Optional[str] = None
    timePeriod: Optional[str] = None
    barLength: Optional[int] = None
    mdAvailability: Optional[str] = None
    mktDataDelay: Optional[int] = None
    outsideRth: Optional[bool] = None
    volumeFactor: Optional[int] = None
    priceDisplayRule: Optional[int] = None
    priceDisplayValue: Optional[str] = None
    negativeCapable: Optional[bool] = None
    messageVersion: Optional[int] = None
    points: Optional[int] = None
    travelTime: Optional[int] = None


class InteractiveBrokersApi(RestAPI):
    def __init__(self):
        self.base_url = "https://localhost:5001/v1/api/"
        self.endpoints = {
            "user": "one/user",
            "tickle": "tickle",
            "validate": "portal/sso/validate",
            "accounts": "portfolio/accounts",
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

    def fetch_ib_account(self):
        response = self.fetch_response_text(
            endpoint="accounts",
        )
        print(response)


ib_api = InteractiveBrokersApi()
