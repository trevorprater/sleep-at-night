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

Additionally, the script transitions the lights in my apartment from
red -> green based on the portfolio's performance.

"""
import os
import logging
import time
import math
from datetime import datetime
from multiprocessing import Pool

from qhue import Bridge
from qhue.qhue import QhueException

from trader_client import TraderClient


LOGGER = logging.getLogger()
TRADER = TraderClient()
MAX_DELTA = 0.08

class HueTradeLight(object):
    def __init__(
            self,
            portfolio_balance,
            bridge_ip=os.getenv('HUE_BRIDGE_IP'),
            down_color='red',
            up_color='green',
            light_ids=[],
            num_colors_in_range=100,
            performance_thresh=0.02):

        self.bridge = Bridge(bridge_ip, username=os.getenv('HUE_BRIDGE_USER'))
        self.light_ids = light_ids
        self._color_map = {
            'red': 0, 'yellow': 12750, 'green': 25500,
            'blue': 46920, 'violet': 56100, 'max': 65280
        }
        self.down_color = self._color_map[down_color]
        self.up_color = self._color_map[up_color]
        self.num_colors_in_range = num_colors_in_range

        # (color is scaled between -n% and +n%)
        self.performance_thresh = performance_thresh
        self.start_balance = portfolio_balance

    @property
    def color_range(self):
        return [int(self.down_color + (self.up_color - self.down_color) \
                * i/float(self.num_colors_in_range)) \
                for i in range(self.num_colors_in_range+1)]

    def set_color(self, curr_balance):
        hue = self.calculate_color(curr_balance)
        if not len(self.light_ids):
            self.light_ids = list(self.bridge.lights().keys())

        for _id in self.light_ids:
            try:
                self.bridge.lights[int(_id)].state(hue=hue)
            except QhueException as e:
                LOGGER.warning(e)

    def calculate_color(self, curr_balance):
        performance = (curr_balance/float(self.start_balance)) - 1
        LOGGER.warning("Current Performance: {}%".format(performance))

        if performance < 0.00:
            performance = max(performance, -1 * self.performance_thresh)
        elif performance > 0.00:
            performance = min(performance, self.performance_thresh)

        percentile = \
            (performance - -1 * self.performance_thresh) / \
            (self.performance_thresh - -1 * self.performance_thresh)

        return self.color_range[
                math.ceil(len(self.color_range) * percentile)]


def evaluate_asset(asset_and_sell_price):
    asset, sell_price = asset_and_sell_price
    currency, market_price = asset['Currency'], asset['AveragePrice']
    sell_price = max(sell_price, market_price * (1 - MAX_DELTA))
    delta = round((market_price / sell_price)*100.0-100.0, 2)
    LOGGER.warning("{}: sell_price: {:0.3e}, price: {:0.3e}, delta: {}%".format(
        currency, sell_price, market_price, delta))

    if market_price > sell_price:
        return currency, sell_price
    else:
        LOGGER.warning("SELLING: {}".format(currency))
        TRADER.sell_all(currency)
        return currency, -1


def main(num_workers=1):
    workers, sell_prices = Pool(num_workers), {}
    trade_light = None
    while True:
        LOGGER.warning(datetime.utcnow())
        asset_data = [(a, sell_prices.get(a['Currency'], -1))
                      for a in TRADER.get_holdings(avg_price_minutes_ago=1)]
        balance = round(sum(
            [a['Available'] * a['AveragePrice'] for a in [aa[0] for aa in asset_data]]), 4)
        LOGGER.warning("BTC VALUE: {}".format(balance))

        if trade_light is None:
            trade_light = HueTradeLight(balance)
        trade_light.set_color(balance)

        for result in workers.imap_unordered(evaluate_asset, asset_data):
            currency, sell_price = result
            if sell_price:
                sell_prices[currency] = sell_price
            else:
                sell_prices.pop(currency)

        LOGGER.warning('*'*58)


if __name__ == '__main__':
    main()
