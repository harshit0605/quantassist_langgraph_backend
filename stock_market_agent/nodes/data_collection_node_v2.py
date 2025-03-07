def data_collection_node(state):
    print("...................In data_collection_node node..................")
    stock_price = state.get("stock_price", None)
    news_sentiment = state.get("news_sentiment", None)
    indicators_data = state.get("indicators_data", None)
    rule_results = state.get("rule_results", None)
    
    if stock_price is None or news_sentiment is None or indicators_data is None or rule_results is None:
        return {"collected_data": {}}
    else:
        return {
            "collected_data" : {
                "stock_price" : stock_price,
                "news_sentiment" : news_sentiment,
                "indicators_data" : indicators_data,
            }
    }