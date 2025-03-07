import numpy as np
from typing import Dict, List, Tuple
from stock_market_agent.models.indicators.base_indicator import BaseIndicator
class BollingerBands(BaseIndicator):
    def __init__(self, period: int = 20, num_std_dev: float = 2.0):
        self.period = period
        self.num_std_dev = num_std_dev

    def calculate(self, parsed_data: Dict[str, List[float]]) -> Dict[str, float]:
        prices = parsed_data["price"]
        prices_array = np.array(prices)
        rolling_mean = np.convolve(prices_array, np.ones(self.period)/self.period, mode='valid')
        rolling_std = np.array([np.std(prices_array[i:i+self.period]) for i in range(len(prices_array) - self.period + 1)])
        
        upper_band = rolling_mean + (rolling_std * self.num_std_dev)
        lower_band = rolling_mean - (rolling_std * self.num_std_dev)
        
        return {
            "Bollinger Mean": rolling_mean[-1],
            "Bollinger Upper": upper_band[-1],
            "Bollinger Lower": lower_band[-1]
        }