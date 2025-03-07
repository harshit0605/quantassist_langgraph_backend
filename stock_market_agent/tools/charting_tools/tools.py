"""This module provides example tools for web scraping and search functionality.

It includes a basic Tavily search function (as an example)

These tools are intended as free examples to get started. For production use,
consider implementing more robust and specialized tools tailored to your needs.
"""

from typing import Any, Callable, List, Optional, cast

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from typing_extensions import Annotated

from stock_market_agent.config.chart_agent_config import ChartAgentConfig


async def search(
    query: str, *, config: Annotated[RunnableConfig, InjectedToolArg]
) -> Optional[list[dict[str, Any]]]:
    """Search for general web results.

    This function performs a search using the Tavily search engine, which is designed
    to provide comprehensive, accurate, and trusted results. It's particularly useful
    for answering questions about current events.
    """
    configuration = ChartAgentConfig.from_runnable_config(config)
    wrapped = TavilySearchResults(max_results=configuration.max_search_results)
    result = await wrapped.ainvoke({"query": query})
    return cast(list[dict[str, Any]], result)

def analyst(analyst_input: AnalystInput):
    """Adds a and b.

    Args:
        a: first int
        b: second int
    """
    stock = yf.Ticker(analyst_input.stock_symbol)
    history = stock.history(period="1y")
    
    # Create a graph
    plt.figure(figsize=(10, 6))
    plt.plot(history.index, history['Close'])
    plt.title(f"{analyst_input.stock_symbol} Stock Price - Last Year")
    plt.xlabel("Date")
    plt.ylabel("Price")
    
    # Save the graph to a base64 encoded string
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    plt.close()
    
    return AIMessage(content=f"Here's the graph for {analyst_input.stock_symbol}. \
        [Graph](data:image/png;base64,{image_base64})")

tools = [add, multiply, divide]

TOOLS: List[Callable[..., Any]] = [search]