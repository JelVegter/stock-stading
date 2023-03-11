from yahoo_fin.stock_info import (
    get_data,
    tickers_sp500,
    tickers_nasdaq,
    tickers_other,
    get_quote_table,
)

""" pull historical data for Netflix (NFLX) """
nflx = get_data("NFLX")

""" pull data for Apple (AAPL) """
"""case sensitivity does not matter"""
aapl = get_data("aapl", start_date="01/01/2017", end_date="01/31/2017")

""" get list of all stocks currently traded
    on NASDAQ exchange """
nasdaq_ticker_list = tickers_nasdaq()

""" get list of all stocks currently in the S&P 500 """
sp500_ticker_list = tickers_sp500()

""" get other tickers not in NASDAQ (based off nasdaq.com)"""
other_tickers = tickers_other()

""" get information on stock from quote page """
info = get_quote_table("amzn")

si.get_data(
    "amzn",
)
