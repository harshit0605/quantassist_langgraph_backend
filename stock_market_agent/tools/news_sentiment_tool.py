import json
import os
import requests
from langchain.tools import BaseTool
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from pydantic import Field, PrivateAttr
from typing import Literal

from stock_market_agent.config.state import AgentState2

class NewsSentimentTool(BaseTool):
    name: Literal["News Sentiment Tool"] = Field(default="News Sentiment Tool")
    description: Literal["This is an example"] = Field(default="Analyze recent news sentiment for a given company")
    api_key: str
    base_url: Literal["https://newsapi.org/v2/everything"] = Field(default="https://newsapi.org/v2/everything")
    _analyzer: SentimentIntensityAnalyzer = PrivateAttr()



    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        # self.api_key = api_key
        self._analyzer = SentimentIntensityAnalyzer()

    def run(self, company: str, state: AgentState2 = None) -> str:
        return self._run(company, state)

    def _run(self, company: str, state: AgentState2) -> str:
        dry_run = state.get("dry_run", False) if state else False
        dry_run = True
        params = {
            "q": company,
            "sortBy": "publishedAt",
            "apiKey": self.api_key,
            "language": "en"
        }

        temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
        os.makedirs(temp_data_folder, exist_ok=True)
        output_file_path = os.path.join(temp_data_folder, "news_sentiment_output.txt")

        if dry_run and os.path.exists(output_file_path):
            with open(output_file_path, "r") as f:
                data = json.loads(f.read())
        else:
            response = requests.get(self.base_url, params=params)
            data = response.json()

            # Write outputs to separate text files in the tempData folder
            with open(output_file_path, "w") as f:
                f.write(json.dumps(data, indent=4))

        # Debugging information
        # print("API Response:", data)
        print("API called for Sentiment Analysis:")

        if "articles" in data:
            sentiments = []
            for article in data["articles"]:
                title = article["title"]
                description = article["description"]
                content = article["content"]
                text = f"{title} {description} {content}"
                sentiment = self._analyzer.polarity_scores(text)
                sentiments.append(sentiment["compound"])

            if sentiments:
                average_sentiment = sum(sentiments) / len(sentiments)
                sentiment_label = "Positive" if average_sentiment > 0 else "Negative" if average_sentiment < 0 else "Neutral"
                result = {
                    "company": company,
                    "sentiment": sentiment_label,
                    "average_score": round(average_sentiment, 2)
                }
                return json.dumps(result)
            else:
                result = {
                    "company": company,
                    "error": "No sentiment data available."
                }
                return json.dumps(result)
        else:
            result = {
                "company": company,
                "error": f"Failed to fetch news. Error: {data.get('message', 'Unknown error')}"
            }
            return json.dumps(result)
    
# Example usage
if __name__ == "__main__":
    api_key = "33329b286a8d40c89a39748b2bb98dd5"
    tool = NewsSentimentTool(api_key=api_key)
    print(tool._run("Varun beverages"))
    