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
    client = TraderClient()
    prices = {}

    while True:
        holdings = client.get_holdings(avg_price_minutes_ago=1)
        [
            prices.pop(currency)
            for currency in
            set(prices) - {h['currency'] for h in holdings}
        ]

        for holding in holdings:
            currency = holding['currency']

            if currency not in prices:
                prices[currency] = (-1, -1)

            old_floor, old_avg_price = prices[currency]
            new_floor, new_avg_price = old_floor, holding['avg_price']
            prices[currency] = (old_floor, new_avg_price)

            if new_avg_price > old_avg_price or old_floor < 0:
                new_floor = new_avg_price - (new_avg_price * sell_threshold)

                if (new_avg_price - old_floor) > new_avg_price * sell_threshold:
                    new_floor = new_avg_price - (
                        new_avg_price * sell_threshold)

                prices[currency] = (new_floor, new_avg_price)

            if new_avg_price <= new_floor:
                client.sell_all(currency)


if __name__ == '__main__':
    main()
