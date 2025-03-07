from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from stock_market_agent.models.custom_rules_engine import CustomRulesEngine
from stock_market_agent.models.indicators.technical_indicators import TechnicalIndicators
from stock_market_agent.models.indicators.fundamental_indicators import FundamentalIndicators

from stock_market_agent.models.evaluation_data import EvaluationData

def indicators_node(state):
    print("...................In analysis node..................")
    historical_data = state["historical_data"]

    # Extract financial data from collected_data
    financial_indicators_data = state["indicators_data"]
    sentiment_data = state["news_sentiment"]
    
    # Parse collected data (you'll need to implement proper parsing)
    # financial_indicators_data = {
    #     "P/E Ratio": "20.5",
    #     "Short-term MA": "105",
    #     "Long-term MA": "100",
    #     "Average Volume": "1000000",
    #     "Current Volume": "1200000",
    #     "RSI": "55",
    #     "Profit Margin": "12",
    #     # Add other indicators here
    # }

    #----------------------Technial analysis---------------

    technical_analysis = TechnicalIndicators(historical_data)
    technical_analysis_data = technical_analysis.calculate_indicators()

    # Add technical analysis results to financial data 
    financial_indicators_data.update(technical_analysis_data)
    
    #----------------------Fundamental analysis---------------

    fundamental_indicator = FundamentalIndicators(historical_data)
    fundamental_indicator_data = fundamental_indicator.calculate_indicators()

    # Add technical analysis results to financial data 
    financial_indicators_data.update(fundamental_indicator_data)

    #Add current stock price to the financial indicator dict
    financial_indicators_data.update({'stock_price' : state['stock_price']})

    # Create EvaluationData object
    evaluation_data = EvaluationData(financial_indicators_data, sentiment_data)

    # Apply custom rules
    rules_engine = CustomRulesEngine()
    rule_results = rules_engine.evaluate(evaluation_data)

    print("In analysis node rule result",rule_results)
    
    # llm = ChatOpenAI(model="gpt-4o")

    # analysis_prompt = f"""
    # Based on the following data, historical analysis and weighted rule-based recommendations, provide a final buy, hold, or sell recommendation:

    # Collected Data:
    # {collected_data}

    # Historical Analysis Results:
    # - Price Trend: {trend:.4f}
    # - Volatility: {volatility:.4f}
    # - Support Level: {support:.2f}
    # - Resistance Level: {resistance:.2f}
    # - Volume Trend: {volume_trend}
    # - Price Momentum: {momentum}

    # Weighted Rule-Based Recommendations:
    # {', '.join(rule_results)}

    # Please consider both the quantitative data and the weighted rule-based recommendations in your analysis.
    # Explain your reasoning, taking into account the confidence levels for each action (Buy, Sell, Hold).
    # Discuss any potential risks or opportunities you see, and how the weights of different rules affected the final recommendation.
    # """
    
    # analysis = llm.invoke([HumanMessage(content=analysis_prompt)])

    return {
        "indicators_data": financial_indicators_data,
        # "sentiment_data": sentiment_data,
        "rule_results": rule_results
    }

# if __name__ == "__main__":
#     print(analysis_node({}))