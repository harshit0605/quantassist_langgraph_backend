import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..")))
# print(sys.path)

def get_ticker_node(state):
    from stock_market_agent.tools.extract_stock_name import CompanyTickerTool
    from stock_market_agent.models.schemas import StockTicker
    
    print("...................In ticker node..................")
    # user_query = state["query"]
    print(state["messages"][-1])
    user_query = state["messages"][-1].content
    response = CompanyTickerTool().run(user_query)

    if "error" in response:
        # Handle the case when the ticker is not found
        return {"error": "Ticker symbol could not be found for the given company name."}

    # Create a proper StockTicker object
    if hasattr(response, 'stock_names') and len(response.stock_names) > 0:
        stock = response.stock_names[0]
        ticker = StockTicker(companyName=stock.companyName, tickerId=stock.tickerId)
        return {'ticker': ticker}
    else:
        return {"error": "No stock information found in the response."}

if __name__ == "__main__":
    print(get_ticker_node({"query" : "Get me the latest financial statements for Apple and Microsoft"}))