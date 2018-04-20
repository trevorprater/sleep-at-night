#!/usr/bin/python3
"""
sleep_at_night.py
Trevor Prater, 2018

This simple script implements a trailing stop loss algorithm.

A trailing stop order sets the stop price at a fixed
amount below the market price with an attached "trailing" amount.

As the market price rises, the stop price rises by the trail amount,
but if the stock price falls, the stop loss price doesn't change,
and a market order is submitted when the stop price is hit.
"""
from multiprocessing import Pool
from trader_client import TraderClient


TRADER = TraderClient()
MAX_DELTA = 0.05


def evaluate_asset(asset_and_sell_price):
    asset, sell_price = asset_and_sell_price
    currency, market_price = asset['currency'], asset['price']
    sell_price = max(sell_price, market_price * (1 - MAX_DELTA))

    if market_price > sell_price:
        return currency, sell_price
    else:
        TRADER.sell_all(currency)
        return currency, -1


def main(num_workers=8):
    workers, sell_prices = Pool(num_workers), {}
    while True:
        asset_data = [(a, sell_prices.get(a['currency'], -1))
                      for a in TRADER.get_holdings()]

        for result in workers.imap_unordered(evaluate_asset, asset_data):
            currency, sell_price = result
            if sell_price:
                sell_prices[currency] = sell_price
            else:
                sell_prices.pop(currency)


if __name__ == '__main__':
    main()
