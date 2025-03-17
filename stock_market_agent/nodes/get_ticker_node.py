import sys
import os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..")))
# print(sys.path)

def get_ticker_node(state):
    from stock_market_agent.tools.extract_stock_name import CompanyTickerTool
    from stock_market_agent.models.schemas import StockTicker
    
    print("...................In ticker node..................")
    # user_query = state["query"]
    dry_run = state.get("dry_run", False) if state else False
    print("dry run: ", dry_run)
    
    print(state["messages"][-1].content)

    # user_query = state["messages"][-1].content
    user_query = None
    for message in reversed(state["messages"]):
        if hasattr(message, 'type') and message.type == 'human':
            user_query = message.content
            break
    
    if not user_query:
        return {"error": "No user message found in the conversation."}
    
    response = CompanyTickerTool().run(user_query)

    if "error" in response:
        # Handle the case when the ticker is not found
        return {"error": "Ticker symbol could not be found for the given company name."}

    # Create a proper StockTicker object
    if hasattr(response, 'stock_names') and len(response.stock_names) > 0:
        stock = response.stock_names[0]
        ticker_dict = {
            "companyName": stock.companyName,
            "tickerId": stock.tickerId
        }
        return {'ticker': ticker_dict}
    else:
        return {"error": "No stock information found in the response."}

if __name__ == "__main__":
    print(get_ticker_node({"query" : "Get me the latest financial statements for Apple and Microsoft"}))