# Trailing Stop Loss Daemon
## AKA sleep-aid

This simple script implements a trailing stop loss algorithm.
<br/>

A trailing stop order sets the stop price at a fixed
amount below the market price with an attached "trailing" amount.
<br/>

As the market price rises, the stop price rises by the trail amount,
but if the stock price falls, the stop loss price doesn't change,
and a market order is submitted when the stop price is hit.

---

Due to the proprietary nature of the TraderClient package, it is not included in this project.

In order to use this algo, you will need to implement two methods in a TraderClient class, `get_holdings` and `sell_all`.