"""
This is the state definition for the AI.
It defines the state of the agent and the state of the conversation.
"""

from typing_extensions import Dict, List, Union, Optional
from typing_extensions import TypedDict, Annotated
from operator import add

from langgraph.graph import MessagesState
from stock_market_agent.models.schemas import Stocks
from langgraph.managed import IsLastStep

from dataclasses import dataclass, field
from copilotkit import CopilotKitState
class AnalysisResult(TypedDict):
    decision: str
    confidence: float
    reasoning: str

class FinalPrediction(TypedDict):
    final_analysis: AnalysisResult
    additional_insights: str

class AgentAnalysis(TypedDict):
    agent: str
    analysis: AnalysisResult

class AgentState(MessagesState):
    """
    This is the state of the agent.
    It is a subclass of the MessagesState class from langgraph.
    """
    query: str
    ticker : Stocks
    collected_data: Optional[str]
    historical_data: Optional[str]
    risk_report: Optional[str]
    portfolio_report: Optional[str]
    recommendation: Optional[str]
    final_recommendation: Optional[str]
    rule_results : Optional[Dict[str, float]]
    error : Optional[str]

class AgentState2(CopilotKitState):
    """
    This is the state of the agent.
    It is a subclass of the MessagesState class from langgraph.
    """
    query: str
    ticker : Stocks
    stock_price: str
    news_sentiment: str
    indicators_data: str
    historical_data: str
    collected_data: Dict[str, Dict[str, str]]
    risk_report: str
    portfolio_report: str
    # analyses: Optional[Annotated[list[AgentAnalysis], add]]
    analyses: Annotated[list[AgentAnalysis], add]
    combined_weighted_analysis: str
    market_conditions : Dict[str, str]
    final_prediction : FinalPrediction
    rule_results : Dict[str, Dict[str, Union[float, str]]]
    error : str

@dataclass
class ChartBuilderState(MessagesState):
    current_stock: str
    is_last_step: IsLastStep = field(default=False)
