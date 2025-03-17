from pprint import pprint
import sys
import os
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..")))
# print(sys.path)

from stock_market_agent.tools.stock_price_tool import StockPriceTool
from stock_market_agent.tools.news_sentiment_tool import NewsSentimentTool
# from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage
from stock_market_agent.tools.portfolio_tool import PortfolioTool
from stock_market_agent.utils.get_api_key import get_api_key
from dotenv import load_dotenv
from stock_market_agent.config.state import AgentState2

def collect_stock_price(state: AgentState2):
    print("...................In collect_stock_price node..................")
    # Load environment variables from .env file
    load_dotenv()
    
    ticker = state["ticker"]
    
    alphavantage_api_key = get_api_key("ALPHA_VANTAGE_API_KEY")
    if not alphavantage_api_key:
        raise ValueError("No ALPHA_VANTAGE API key found. Please set the ALPHA_VANTAGE_API_KEY environment variable.")

    print(alphavantage_api_key)
    # print("Dry_run variable: ", state["dry_run"])
    # Use tools to collect data
    stock_price_tool = StockPriceTool(api_key=alphavantage_api_key)

    price_info = stock_price_tool.run(ticker["tickerId"], state)
    # Parse the JSON response from the sentiment tool

    collected_data = {
        "stock_price": price_info,
    }

    # TODO: Change this to accept {collected_data: {stock_price: price_info}}
    return collected_data 
    
    # return {
    #     # "messages": state["messages"] + [AIMessage(content=str(collected_data))],
    #     "collected_data": collected_data
    # }

if __name__ == "__main__":
    collected_data = collect_stock_price({"ticker" : "AAPL", "messages" : ['']})
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