from langchain.tools import BaseTool

class PortfolioTool(BaseTool):
    name:str = "Portfolio Tool"
    description:str = "Get current portfolio holdings and allocations"

    def _run(self) -> str:
        # In a real implementation, this would fetch data from a user's actual portfolio
        return """
        AAPL,100,15000,Technology,0.3
        GOOGL,50,60000,Technology,0.2
        JPM,200,30000,Finance,0.15
        JNJ,150,25000,Healthcare,0.15
        XOM,300,20000,Energy,0.1
        PG,100,15000,Consumer Goods,0.1
        """