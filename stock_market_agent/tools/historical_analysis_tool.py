from typing import Dict, List, Literal, Tuple
from datetime import datetime, timedelta
from pydantic import Field, PrivateAttr
from scipy import stats
import numpy as np
from langchain.tools import BaseTool


class HistoricalAnalysisTool(BaseTool):
    name: Literal["Historical Analysis Tool"] = Field("Historical Analysis Tool")
    description: Literal["Analyse the historical stock data and perform analysis"] = Field("Analyse the historical stock data and perform analysis")

    _parsed_data: Dict[str, List[float]] = PrivateAttr()
    
    def __init__(self):
        super().__init__()

    def _run(self, data : str):
        self._parsed_data = self._parse_data(data)
        
        trend = self.calculate_trend()
        volatility = self.calculate_volatility()
        support, resistance = self.identify_support_resistance()
        volume_trend = self.volume_trend()
        momentum = self.price_momentum()
        average_price = self.calculate_average_price()

        analysis_data = {
            "Price Trend": str(trend),
            "Volatility": str(volatility),
            "Support Level": str(support),
            "Resistance Level": str(resistance),
            "Volume Trend": volume_trend,
            "Price Momentum": momentum,
            "Current Price": str(self._parsed_data["price"][-1]),
            "Average Price": str(average_price)
        }

        return analysis_data

    def _parse_data(self, data: str) -> Dict[str, List[float]]:
        lines = data.strip().split("\n")[1:]  # Skip header
        parsed = {"date": [], "price": [], "volume": []}
        for line in lines:
            date, price, volume = line.split(",")
            parsed["date"].append(datetime.strptime(date, "%Y-%m-%d"))
            parsed["price"].append(float(price))
            parsed["volume"].append(int(volume))
        return parsed

    def calculate_trend(self) -> float:
        x = range(len(self._parsed_data["price"]))
        slope, _, _, _, _ = stats.linregress(x, self._parsed_data["price"])
        return slope

    def calculate_volatility(self) -> float:
        return np.std(self._parsed_data["price"])

    def identify_support_resistance(self) -> Tuple[float, float]:
        prices = self._parsed_data["price"]
        support = min(prices)
        resistance = max(prices)
        return support, resistance

    def volume_trend(self) -> str:
        avg_volume_first_half = np.mean(self._parsed_data["volume"][:15])
        avg_volume_second_half = np.mean(self._parsed_data["volume"][15:])
        if avg_volume_second_half > avg_volume_first_half * 1.1:
            return "increasing"
        elif avg_volume_second_half < avg_volume_first_half * 0.9:
            return "decreasing"
        else:
            return "stable"

    def price_momentum(self) -> str:
        short_term_avg = np.mean(self._parsed_data["price"][-5:])
        long_term_avg = np.mean(self._parsed_data["price"])
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
        
    def calculate_average_price(self) -> float:
        return np.mean(self._parsed_data["price"])