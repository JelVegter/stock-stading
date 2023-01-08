# clientportal.gw/bin/run.sh clientportal.gw/root/conf.yaml
from common.ib import InteractiveBrokersApi


def main():
    api = InteractiveBrokersApi()
    status_code = api.fetch_status_code("user")
    assert status_code == 200
    symbol = "AAPL"

    # stock_contracts = api.fetch_stock_contracts(symbol)
    # pprint(stock_contracts)

    AAPL_con_id = 265598
    MSFT_con_id = 272093
    con_ids = [AAPL_con_id, MSFT_con_id]
    stock_histories = api.fetch_stock_price_history(conid=con_ids)
    print(stock_histories)


if __name__ == "__main__":
    main()
