from typing import Dict, List
from stock_market_agent.models.indicators.technical.bollinger_bands import BollingerBands
from stock_market_agent.models.indicators.technical.macd import MACD
from stock_market_agent.models.indicators.technical.rsi import RSI
from stock_market_agent.models.indicators.technical.historical_analysis_indicator import HistoricalAnalysisIndicator
from datetime import datetime
from stock_market_agent.models.indicators.base_indicator import IndicatorRegistry
   

class TechnicalIndicators:
    def __init__(self, data: str):
        self._parsed_data = self._parse_data(data)
        self.prices = self._parsed_data["price"]
        self.registry = IndicatorRegistry()
        self._register_indicators()
    
    def _register_indicators(self):
        self.registry.register("BollingerBands", BollingerBands())
        self.registry.register("MACD", MACD())
        self.registry.register("RSI", RSI())
        self.registry.register("HistoricalAnalysis", HistoricalAnalysisIndicator())

        # Register additional indicators here

    def calculate_indicators(self) -> Dict[str, float]:
        indicators_data = {}
        for name, indicator in self.registry.getRegisteredIndicators().items():
            indicators_data.update(indicator.calculate(self._parsed_data))
        return indicators_data

    def _parse_data(self, data: str) -> Dict[str, List[float]]:
        lines = data.strip().split("\n")[1:]  # Skip header
        parsed = {"date": [], "price": [], "volume": []}
        for line in lines:
            date, price, volume = line.split(",")
            parsed["date"].append(datetime.strptime(date, "%Y-%m-%d"))
            parsed["price"].append(float(price))
            parsed["volume"].append(int(volume))
        return parsed