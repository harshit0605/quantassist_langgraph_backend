import numpy as np
from typing import Dict, List
from stock_market_agent.models.indicators.base_indicator import BaseIndicator

class RSI(BaseIndicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, parsed_data: Dict[str, List[float]]) -> Dict[str, float]:
        prices = parsed_data["price"]
        deltas = np.diff(prices)
        seed = deltas[:self.period+1]
        up = seed[seed >= 0].sum()/self.period
        down = -seed[seed < 0].sum()/self.period
        rs = up/down
        rsi = np.zeros_like(prices)
        rsi[:self.period] = 100. - 100./(1. + rs)

        for i in range(self.period, len(prices)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta

            up = (up*(self.period - 1) + upval)/self.period
            down = (down*(self.period - 1) + downval)/self.period

            rs = up/down
            rsi[i] = 100. - 100./(1. + rs)

        return {"RSI": rsi[-1]}