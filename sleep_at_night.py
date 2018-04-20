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

from trader_client import TraderClient


def main(sell_threshold=0.04):
    trader, sell_limit = TraderClient(), {}

    while True:
        for asset in trader.get_holdings():
            currency, price = asset['currency'], asset['price']

            sell_limit[currency] = max(
                    sell_limit.get(currency, -1),
                    price * (1 - sell_threshold))

            if price < sell_limit[currency]:
                trader.sell_all(currency)
                sell_limit.pop(currency)


if __name__ == '__main__':
    main()
