from typing import Any, Dict, List
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
# from nodes.data_collection_node import data_collection_node
from stock_market_agent.nodes.get_ticker_node import get_ticker_node
from stock_market_agent.nodes.historical_data_node import historical_data_node
from stock_market_agent.nodes.meta_analysis_agent import MetaAnalysisLLM
from stock_market_agent.workflows.create_persona_agents import create_persona_agents
from stock_market_agent.config.state import AgentState2

from stock_market_agent.nodes.integrate_weighted_analysis import integrate_weighted_analyses
from stock_market_agent.nodes.collect_stock_price import collect_stock_price
from stock_market_agent.nodes.collect_news_sentiment import collect_news_sentiment
from stock_market_agent.nodes.collect_fundamental_indicators import collect_fundamental_indicators
from stock_market_agent.nodes.data_collection_node_v2 import data_collection_node
from stock_market_agent.nodes.collect_market_conditions import collect_market_conditions
from stock_market_agent.nodes.indicators_node import indicators_node

from langchain_core.language_models.chat_models import BaseChatModel
from langgraph.checkpoint.memory import MemorySaver
# Develop a system to track each agent's performance over time, which could be used to adjust their influence on the final decision.

def process_market_data(data: Dict[str, Any]) -> Dict[str, Any]:
    # Process and normalize market data
    # This function would handle data from various sources and format it for agent consumption
    return data

def make_decision(analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    buy_confidence = 0
    sell_confidence = 0
    hold_confidence = 0
    
    for analysis in analyses:
        if analysis["decision"] == "buy":
            buy_confidence += analysis["confidence"]
        elif analysis["decision"] == "sell":
            sell_confidence += analysis["confidence"]
        else:
            hold_confidence += analysis["confidence"]
    
    total_confidence = buy_confidence + sell_confidence + hold_confidence
    if total_confidence == 0:
        return {"decision": "hold", "confidence": 0}
    
    if buy_confidence > sell_confidence and buy_confidence > hold_confidence:
        return {"decision": "buy", "confidence": buy_confidence / total_confidence}
    elif sell_confidence > buy_confidence and sell_confidence > hold_confidence:
        return {"decision": "sell", "confidence": sell_confidence / total_confidence}
    else:
        return {"decision": "hold", "confidence": hold_confidence / total_confidence}

def create_workflow_graph():
    from stock_market_agent.models.personas.financial_agent import AdaptiveWeightingSystem
    llm : BaseChatModel = ChatOpenAI(model="gpt-4o")

    meta_analysis_agent = MetaAnalysisLLM(llm)
    graph = StateGraph(AgentState2)

    #------------------------------ADD NODES-------------------------------

    graph.add_node("get_ticker_node", get_ticker_node)

    data_collection_nodes = {
        "collect_stock_price_node" : collect_stock_price,
        "sentiment_analyzer_node" : collect_news_sentiment,
        "collect_fundamental_indicators_node" : collect_fundamental_indicators,
        "historical_data_node" : historical_data_node,
        "market_conditions_node" : collect_market_conditions, 
    }

    # Iterate over the dictionary and add each node to the graph
    for node_name, node_function in data_collection_nodes.items():
        graph.add_node(node_name, node_function)

    graph.add_node("collect_data", data_collection_node)
    graph.add_node("tech_fundamental_indicators_node", indicators_node)

    # Add agent persona nodes
    agents = create_persona_agents(llm)
    for agent in agents:
        graph.add_node(agent.name, agent.analyze)

    adaptive_weighting = AdaptiveWeightingSystem(agents) 
    graph.add_node("integration", lambda x: integrate_weighted_analyses(x, adaptive_weighting))
    graph.add_node("meta_analysis_node", meta_analysis_agent.analyze)
    
    #------------------------------ADD EDGES-------------------------------

    # Add edges from START node to all data collection nodes in parallel
    # Also add an edge from each data collection node to collect node
    # Exception being 
    graph.add_edge(START, "get_ticker_node")
    
    for node_name, node_function in data_collection_nodes.items():
        graph.add_edge("get_ticker_node", node_name)
        if node_name not in ['collect_stock_price_node','collect_fundamental_indicators_node']:
            graph.add_edge(node_name, "collect_data")
        else:
            graph.add_edge(node_name, "tech_fundamental_indicators_node")

    graph.add_edge("tech_fundamental_indicators_node", "collect_data")

    # Connect collect_data node to all agent persona nodes
    for agent in agents:
        graph.add_edge("collect_data", agent.name)
        graph.add_edge(agent.name, "integration")

    graph.add_edge("integration", "meta_analysis_node")
    graph.add_edge("meta_analysis_node", END)
    

    within_thread_memory = MemorySaver()
    return graph.compile(checkpointer=within_thread_memory,)