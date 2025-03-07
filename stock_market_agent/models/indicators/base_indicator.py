from typing import Dict, List

class BaseIndicator:
    def calculate(self, parsed_data: Dict[str, List[float]]) -> Dict[str, float]:
        raise NotImplementedError("Subclasses should implement this method")

class IndicatorRegistry:
    def __init__(self):
        self._indicators : Dict[str, BaseIndicator] = {}

    def register(self, name: str, indicator: BaseIndicator):
        self._indicators[name] = indicator

    def get(self, name: str) -> BaseIndicator:
        return self._indicators.get(name)
    
    def getRegisteredIndicators(self) -> Dict[str, BaseIndicator]:
        return self._indicators
    