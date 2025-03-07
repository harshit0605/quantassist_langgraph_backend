from tools.portfolio_tool import PortfolioTool
from langchain_core.messages import AIMessage
from stock_market_agent.tools.historical_analysis_tool import HistoricalAnalysis
from typing import Dict, List, Tuple

class RiskAssessmentAgent:
    def __init__(self, historical_data: str, portfolio_data: str):
        self.historical_analysis = HistoricalAnalysis(historical_data)
        self.portfolio = self._parse_portfolio(portfolio_data)

    def _parse_portfolio(self, data: str) -> List[Dict]:
        portfolio = []
        for line in data.strip().split("\n"):
            ticker, shares, value, sector, allocation = line.split(",")
            portfolio.append({
                "ticker": ticker,
                "shares": int(shares),
                "value": float(value),
                "sector": sector,
                "allocation": float(allocation)
            })
        return portfolio

    def calculate_portfolio_beta(self) -> float:
        # In a real implementation, you'd calculate this using market data
        # Here, we're using a placeholder value
        return 1.2

    def calculate_sharpe_ratio(self) -> float:
        # Placeholder calculation
        portfolio_return = 0.1  # 10% annual return
        risk_free_rate = 0.03  # 3% risk-free rate
        portfolio_volatility = self.historical_analysis.calculate_volatility()
        return (portfolio_return - risk_free_rate) / portfolio_volatility


    def assess_diversification(self) -> str:
        sector_allocations = {}
        for holding in self.portfolio:
            sector = holding["sector"]
            allocation = holding["allocation"]
            sector_allocations[sector] = sector_allocations.get(sector, 0) + allocation

        max_allocation = max(sector_allocations.values())
        if max_allocation > 0.4:
            return "Poor - Heavy concentration in one sector"
        elif max_allocation > 0.3:
            return "Moderate - Some concentration risk"
        else:
            return "Good - Well diversified across sectors"


    def generate_risk_report(self) -> str:
        beta = self.calculate_portfolio_beta()
        sharpe_ratio = self.calculate_sharpe_ratio()
        diversification = self.assess_diversification()
        volatility = self.historical_analysis.calculate_volatility()

        return f"""
        Risk Assessment Report:
        - Portfolio Beta: {beta:.2f}
        - Sharpe Ratio: {sharpe_ratio:.2f}
        - Diversification: {diversification}
        - Historical Volatility: {volatility:.2f}
        """


def risk_assessment_node(state):
    print("...................In risk assessment node..................")
    historical_data = state["historical_data"]
    portfolio_data = state["collected_data"]["portfolio_data"]
    
    risk_agent = RiskAssessmentAgent(historical_data, portfolio_data)
    risk_report = risk_agent.generate_risk_report()

    return {
        "messages": state["messages"] + [AIMessage(content=risk_report)],
        "risk_report": risk_report
    }