from typing import Dict

class EvaluationData:
    def __init__(self, financial_data: Dict[str, str], sentiment_data: str):
        self.indicator_data = financial_data
        self.sentiment_data = sentiment_data