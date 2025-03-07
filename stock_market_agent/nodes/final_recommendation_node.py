from langchain_core.messages import HumanMessage, AIMessage
from langchain_openai import ChatOpenAI
from models.custom_rules_engine import CustomRulesEngine
# from stock_market_agent.tools.historical_analysis_tool import HistoricalAnalysisTool

def final_recommendation_node(state):
    print("...................In final recommendation node..................")
    collected_data = state.get("collected_data", "No collected data available.")
    historical_analysis = state.get("historical_data", "No historical data available.")
    risk_report = state.get("risk_report", "No risk report available.")
    portfolio_report = state.get("portfolio_report", "No portfolio report available.")
    rule_results = state.get("rule_results", "No rule results available.")


    llm = ChatOpenAI(model="gpt-4o")
    final_prompt = f"""
    Based on the following information, provide a comprehensive investment recommendation:

    1. Current Financial Data:
    {collected_data}

    2. Historical Analysis:
    {historical_analysis}

    3. Risk Assessment:
    {risk_report}

    4. Portfolio Analysis:
    {portfolio_report}

    5. Rule-Based Recommendations:
    {rule_results}


    Please consider ALL of the above information to provide:
    1. A recommendation on whether to buy, hold, or sell the stock in question. Take into account the confidence levels for each action (Buy, Sell, Hold).
    2. How this decision fits into the overall portfolio strategy.
    3. Any potential risks or opportunities you see, and how the weights of different rules affected the final recommendation.
    4. Suggestions for portfolio rebalancing or diversification, if necessary.
    

    Explain your reasoning thoroughly, taking into account the individual stock analysis, 
    risk factors, and the current portfolio composition.
    """
    # final_analysis = llm.invoke([HumanMessage(content=final_prompt)])

    final_analysis = {"content": """
        Dummy Recommendation:
        1. Recommendation: Hold
        2. Portfolio Strategy: The decision aligns with the current strategy.
        3. Risks/Opportunities: No significant risks identified.
        4. Suggestions: No rebalancing needed at this time.
        """}
    return {
        "messages": state["messages"] + [AIMessage(content=final_analysis.content)],
        "final_recommendation": final_analysis.content
    }