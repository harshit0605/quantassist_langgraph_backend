from pprint import pprint
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..")))
# print(sys.path)

from stock_market_agent.tools.stock_price_tool import StockPriceTool
from stock_market_agent.tools.news_sentiment_tool import NewsSentimentTool
from stock_market_agent.tools.fundamental_indicators_tool import FundamentalIndicatorsTool
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage
from stock_market_agent.tools.portfolio_tool import PortfolioTool
from stock_market_agent.utils.get_api_key import get_api_key
from dotenv import load_dotenv


def collect_fundamental_indicators(state):
    print("...................In collect_fundamental_indicators node..................")
    # Load environment variables from .env file
    load_dotenv()
    
    ticker = state["ticker"]

    
    alphavantage_api_key = get_api_key("ALPHA_VANTAGE_API_KEY")
    if not alphavantage_api_key:
        raise ValueError("No ALPHA_VANTAGE API key found. Please set the ALPHA_VANTAGE_API_KEY environment variable.")

    print(alphavantage_api_key)

    
    fundamental_indicators_tool = FundamentalIndicatorsTool(api_key=alphavantage_api_key)
    fundamental_indicators = fundamental_indicators_tool.run(ticker["tickerId"], state)

    # portfolio_data = PortfolioTool().run()

    collected_data = {
        "indicators_data": fundamental_indicators,
        # "Recent News": recent_news,
        # "portfolio_data" : portfolio_data
    }

    return collected_data
    
    # return {
    #     "messages": state["messages"] + [AIMessage(content=str(collected_data))],
    #     "collected_data": collected_data
    # }

if __name__ == "__main__":
    collected_data = collect_fundamental_indicators({"ticker" : "AAPL", "messages" : ['']})
    with open("stock_market_agent/tempData/collected_data.json", "w") as outfile:
        json.dump(collected_data, outfile, indent=4)

# {
#     "stock_ticker": "AAPL",
#     "current_price": 150.25,
#     "52_week_high": 182.94,
#     "52_week_low": 124.17,
#     "pe_ratio": 24.5,
#     "dividend_yield": 0.0058,  # 0.58%
#     "revenue_growth_rate": 0.08,  # 8%
#     "debt_to_equity": 1.81,
#     "rsi_14": 65.20,
#     "earnings_surprise": 0.03,  # 3% positive surprise
#     "market_cap": "2.45T",
#     "sector": "Technology"
# }