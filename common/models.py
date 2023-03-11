from dataclasses import dataclass, field, asdict
import pandas as pd


@dataclass
class StockContract:
    symbol: str
    name: str
    assetClass: str
    conid: int
    exchange: str
    isUS: bool
    chineseName: str = None


@dataclass
class StockContractRecord:
    id: str
    symbol: str
    name: str
    assetClass: str
    conid: int
    exchange: str
    isUS: bool
    chineseName: str = None


@dataclass
class StockHistory:
    conid: int
    symbol: str
    text: str
    data: list[dict[str, float]]
    serverId: str = None
    priceFactor: int = None
    chartAnnotations: str = None
    startTime: str = None
    high: str = None
    low: str = None
    timePeriod: str = None
    barLength: int = None
    mdAvailability: str = None
    mktDataDelay: int = None
    outsideRth: bool = None
    volumeFactor: int = None
    priceDisplayRule: int = None
    priceDisplayValue: str = None
    negativeCapable: bool = None
    messageVersion: int = None
    points: int = None
    travelTime: int = None


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
    priceFactor: int = None
    chartAnnotations: str = None
    startTime: str = None
    high: str = None
    low: str = None
    timePeriod: str = None
    barLength: int = None
    mdAvailability: str = None
    mktDataDelay: int = None
    outsideRth: bool = None
    volumeFactor: int = None
    priceDisplayRule: int = None
    priceDisplayValue: str = None
    negativeCapable: bool = None
    messageVersion: int = None
    points: int = None
    travelTime: int = None


@dataclass
class Position:
    # Base
    acctId: str
    conid: int
    contractDesc: str
    assetClass: str
    position: int
    mktPrice: int
    mktValue: int
    currency: str
    avgCost: int
    avgPrice: int
    realizedPnl: int
    unrealizedPnl: int
    exchs: str
    expiry: str
    putOrCall: str
    multiplier: int
    strike: int
    exerciseStyle: str
    undConid: int
    conExchMap: list
    baseMktValue: int
    baseMktPrice: int
    baseAvgCost: int
    baseAvgPrice: int
    baseRealizedPnl: int
    baseUnrealizedPnl: int
    name: str
    lastTradingDay: str
    group: str
    sector: str
    sectorGroup: str
    ticker: str
    undComp: str
    undSym: str
    fullName: str
    pageSize: int
    model: str


@dataclass
class Account:
    # Base
    id: str
    accountId: str
    accountVan: str
    accountTitle: str
    displayName: str
    accountAlias: str
    accountStatus: int
    currency: str
    type: str
    tradingType: str
    faclient: bool
    clearingStatus: str
    covestor: bool
    parent: dict
    desc: str

    # Added
    positions: list[Position] = field(default_factory=list)
