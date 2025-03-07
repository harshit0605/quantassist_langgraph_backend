import numpy as np
from typing import Dict, List, Tuple
from stock_market_agent.models.indicators.base_indicator import BaseIndicator
from scipy import stats

class HistoricalAnalysisIndicator(BaseIndicator):
    def __init__(self):
        pass
    
    def calculate(self, parsed_data: Dict[str, List[float]]) -> Dict[str, float]:
        prices = parsed_data["price"]
        volumes = parsed_data["volume"]
        trend = self.calculate_trend(prices)
        volatility = self.calculate_volatility(prices)
        support, resistance = self.identify_support_resistance(prices)
        volume_trend = self.volume_trend(volumes)
        momentum = self.price_momentum(prices)
        average_price = self.calculate_average_price(prices)

        return {
            "Price Trend": trend,
            "Volatility": volatility,
            "Support Level": support,
            "Resistance Level": resistance,
            "Volume Trend": volume_trend,
            "Price Momentum": momentum,
            "Average Price": average_price
        }

    def calculate_trend(self, prices: List[float]) -> float:
        x = range(len(prices))
        slope, _, _, _, _ = stats.linregress(x, prices)
        return slope

    def calculate_volatility(self, prices: List[float]) -> float:
        return np.std(prices)

    def identify_support_resistance(self, prices: List[float]) -> Tuple[float, float]:
        support = min(prices)
        resistance = max(prices)
        return support, resistance

    def volume_trend(self, volumes: List[float]) -> str:
        avg_volume_first_half = np.mean(volumes[:len(volumes)//2])
        avg_volume_second_half = np.mean(volumes[len(volumes)//2:])
        if avg_volume_second_half > avg_volume_first_half * 1.1:
            return "increasing"
        elif avg_volume_second_half < avg_volume_first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

    def price_momentum(self, prices: List[float]) -> str:
        short_term_avg = np.mean(prices[-5:])
        long_term_avg = np.mean(prices)
        if short_term_avg > long_term_avg * 1.05:
            return "strong positive"
        elif short_term_avg > long_term_avg:
            return "positive"
        elif short_term_avg < long_term_avg * 0.95:
            return "strong negative"
        elif short_term_avg < long_term_avg:
            return "negative"
        else:
            return "neutral"

    def calculate_average_price(self, prices: List[float]) -> float:
        return np.mean(prices)