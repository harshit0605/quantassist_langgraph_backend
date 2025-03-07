from datetime import datetime, timezone
from typing import Any, Dict, List, Literal, cast

from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.prompts import ChatPromptTemplate

from nodes.get_ticker_node import get_ticker_node
from nodes.historical_data_node import historical_data_node
from stock_market_agent.models.personas.financial_agent import AdaptiveWeightingSystem

from stock_market_agent.nodes.meta_analysis_agent import MetaAnalysisLLM
from stock_market_agent.workflows.create_persona_agents import create_persona_agents
from stock_market_agent.config.state import ChartBuilderState
from stock_market_agent.config.chart_agent_config import ChartAgentConfig
from stock_market_agent.nodes.charting_nodes.human_node import human_node
from stock_market_agent.tools.charting_tools.chart_builder_tool import TOOLS

from stock_market_agent.utils.utils import load_chat_model


def route_model_output(state: ChartBuilderState) -> Literal["__end__", "tools"]:
    """Determine the next node based on the model's output.

    This function checks if the model's last message contains tool calls.

    Args:
        state (State): The current state of the conversation.

    Returns:
        str: The name of the next node to call ("__end__" or "tools").
    """
    last_message = state.messages[-1]
    if not isinstance(last_message, AIMessage):
        raise ValueError(
            f"Expected AIMessage in output edges, but got {type(last_message).__name__}"
        )
    # If there is no tool call, then we finish
    if not last_message.tool_calls:
        return "__end__"
    # Otherwise we execute the requested actions
    return "tools"

async def call_model(
    state: ChartBuilderState, config: RunnableConfig
) -> Dict[str, List[AIMessage]]:
    """Call the LLM powering our "agent".

    This function prepares the prompt, initializes the model, and processes the response.

    Args:
        state (State): The current state of the conversation.
        config (RunnableConfig): Configuration for the model run.

    Returns:
        dict: A dictionary containing the model's response message.
    """
    configuration = ChartAgentConfig.from_runnable_config(config)

    # Create a prompt template. Customize this to change the agent's behavior.
    prompt = ChatPromptTemplate.from_messages(
        [("system", configuration.system_prompt), ("placeholder", "{messages}")]
    )

    # Initialize the model with tool binding. Change the model or add more tools here.
    model = load_chat_model(configuration.model).bind_tools(TOOLS)

    # Prepare the input for the model, including the current system time
    message_value = await prompt.ainvoke(
        {
            "messages": state.messages,
            "system_time": datetime.now(tz=timezone.utc).isoformat(),
        },
        config,
    )

    # Get the model's response
    response = cast(AIMessage, await model.ainvoke(message_value, config))

    # Handle the case when it's the last step and the model still wants to use a tool
    if state.is_last_step and response.tool_calls:
        return {
            "messages": [
                AIMessage(
                    id=response.id,
                    content="Sorry, I could not find an answer to your question in the specified number of steps.",
                )
            ]
        }

    # Return the model's response as a list to be added to existing messages
    return {"messages": [response]}



def create_analysis_graph():
    llm : BaseChatModel = ChatOpenAI(model="gpt-4o")

    meta_analysis_agent = MetaAnalysisLLM(llm)
    # workflow = StateGraph(ChartBuilderState)
    workflow = StateGraph(ChartBuilderState, input=MessagesState, config_schema=ChartAgentConfig)

    #------------------------------ADD NODES-------------------------------
    # Add nodes
    workflow.add_node("human", human_node)
    workflow.add_node("agent", agent)
    workflow.add_node(call_model)
    workflow.add_node("call_tool", ToolNode(TOOLS))

    # Add edges
    workflow.set_entry_point("human")
    workflow.add_edge("human", "agent")
    workflow.add_edge("agent", "human")
    workflow.add_edge("agent", "call_tool")
    workflow.add_edge("call_tool", "agent")

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
    

    return graph.compile()