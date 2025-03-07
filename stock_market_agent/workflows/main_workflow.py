from langgraph.graph import StateGraph, START, END
from nodes.get_ticker_node import get_ticker_node
from nodes.data_collection_node import data_collection_node
from nodes.analysis_node import analysis_node
# from nodes.risk_assessment_node import risk_assessment_node
# from nodes.portfolio_analysis_node import portfolio_analysis_node
from nodes.final_recommendation_node import final_recommendation_node
from nodes.historical_data_node import historical_data_node
from tools.historical_data_tool import HistoricalDataTool
from config.state import AgentState

def create_workflow_graph():
    # Updated workflow to include historical data
    workflow = StateGraph(AgentState)
    workflow.add_node("get_ticker_node", get_ticker_node)
    workflow.add_node("data_collection_node", data_collection_node)
    workflow.add_node("historical_data_node", historical_data_node)
    workflow.add_node("analysis_node", analysis_node)
    # workflow.add_node("risk_assessment", risk_assessment_node)
    # workflow.add_node("portfolio_analysis", portfolio_analysis_node)
    workflow.add_node("final_recommendation_node", final_recommendation_node)
    
    workflow.add_edge(START, "get_ticker_node")
    workflow.add_edge("get_ticker_node", "data_collection_node")
    workflow.add_edge("data_collection_node", "historical_data_node")
    workflow.add_edge("historical_data_node", "analysis_node")
    # workflow.add_edge("analysis", "risk_assessment")
    # workflow.add_edge("risk_assessment", "portfolio_analysis")
    # workflow.add_edge("portfolio_analysis", "final_recommendation")
    workflow.add_edge("analysis_node", "final_recommendation_node")

    graph = workflow.compile()

    return graph

# def create_workflow():
#     workflow = SequentialGraph()
#     workflow.add_node("data_collection", DataCollectionAgent().process)
#     workflow.add_node("analysis", AnalysisAgent().process)
#     workflow.add_node("risk_assessment", RiskAssessmentAgent().process)
#     workflow.add_node("portfolio_analysis", PortfolioAnalysisAgent().process)
#     workflow.add_node("final_recommendation", FinalRecommendationAgent().process)

#     workflow.set_entry_point("data_collection")
#     workflow.add_edge("data_collection", "analysis")
#     workflow.add_edge("analysis", "risk_assessment")
#     workflow.add_edge("risk_assessment", "portfolio_analysis")
#     workflow.add_edge("portfolio_analysis", "final_recommendation")

#     return workflow