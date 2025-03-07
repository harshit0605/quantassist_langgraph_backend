from typing import Any, Callable, List, Optional, cast

from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_core.messages import AIMessage
from langchain_core.runnables import RunnableConfig
from langchain_core.tools import InjectedToolArg
from typing_extensions import Annotated

from stock_market_agent.config.chart_agent_config import ChartAgentConfig, ChartType

import base64
import io
from matplotlib import pyplot as plt
from pydantic import BaseModel, Field

class AnalystInput(BaseModel):
    stock_symbol: str = Field(..., description="The stock symbol to analyze")
    chart_type: str = Field(..., description="The type of chart requested ")
    ticker_data: Any = Field(..., description="The historical stock ticker data")



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
    """Generates a stock chart based on the input chart type.

    Args:
        analyst_input: An instance of AnalystInput containing stock symbol, chart type, and ticker data.
    """
    history = analyst_input.ticker_data
    chart_type = analyst_input.chart_type
    
    # Create a graph based on the chart type
    plt.figure(figsize=(10, 6))
    
    if chart_type == ChartType.LINE:
        plt.plot(history.index, history['Close'])
    elif chart_type == ChartType.BAR:
        plt.bar(history.index, history['Close'])
    elif chart_type == ChartType.CANDLESTICK:
        # Example using mplfinance for candlestick charts
        import mplfinance as mpf
        mpf.plot(history, type='candle', style='charles', volume=True)
    else:
        raise ValueError(f"Unsupported chart type: {chart_type}")
    
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

# # Define the tools
# tools = [ToolInvocation(name="analyst", func=analyst, args_schema=AnalystInput)]
# tool_executor = ToolExecutor(tools)

# TOOLS: List[Callable[..., Any]] = [search]
TOOLS: List[Callable[..., Any]] = [analyst]



# Example usage
if __name__ == "__main__":
    api_key = "IKPRCH1Z25YCA2SP"
    # tool = StockPriceTool(api_key)
    # print(tool._run("RELIANCE.BSE"))  # Example ticker for Reliance Industries on BSE