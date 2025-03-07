from stock_market_agent.tools.historical_data_tool import HistoricalDataTool
from stock_market_agent.tools.news_sentiment_tool import NewsSentimentTool
from langchain_community.tools import DuckDuckGoSearchRun
from langchain_core.messages import HumanMessage, AIMessage
import os

def historical_data_node(state):
    print("...................In historical data node..................")
    ticker = state["ticker"]
    
    stock_api_key = os.getenv("ALPHA_VANTAGE_API_KEY")
    if not stock_api_key:
        raise ValueError("No ALPHA_VANTAGE API key found. Please set the ALPHA_VANTAGE_API_KEY environment variable.")

    # Use tools to collect data
    historical_data_tool = HistoricalDataTool()
    historical_data = historical_data_tool.run(ticker.tickerId)
    
    return {
        "messages": state["messages"] + [AIMessage(content=historical_data)],
        "historical_data": historical_data
    }