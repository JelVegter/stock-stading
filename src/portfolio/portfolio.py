from common.interactive_brokers import ib_api


def main():
    portfolio = ib_api.fetch_portfolio()

    print(portfolio.positions_as_df)

    _ = portfolio.get_historical_returns()
    print(_)


if __name__ == "__main__":
    main()
