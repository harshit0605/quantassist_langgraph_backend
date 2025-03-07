from langchain_core.messages import AIMessage
from typing import Dict, List

class PortfolioAnalysisAgent:
    def __init__(self, portfolio_data: str):
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

    def calculate_total_value(self) -> float:
        return sum(holding["value"] for holding in self.portfolio)

    def identify_largest_holdings(self, n: int = 3) -> List[Dict]:
        sorted_holdings = sorted(self.portfolio, key=lambda x: x["value"], reverse=True)
        return sorted_holdings[:n]

    def calculate_sector_allocations(self) -> Dict[str, float]:
        sector_allocations = {}
        for holding in self.portfolio:
            sector = holding["sector"]
            allocation = holding["allocation"]
            sector_allocations[sector] = sector_allocations.get(sector, 0) + allocation
        return sector_allocations

    def generate_portfolio_report(self) -> str:
        total_value = self.calculate_total_value()
        largest_holdings = self.identify_largest_holdings()
        sector_allocations = self.calculate_sector_allocations()

        report = f"Portfolio Analysis Report:\n"
        report += f"Total Portfolio Value: ${total_value:,.2f}\n\n"
        
        report += "Largest Holdings:\n"
        for holding in largest_holdings:
            report += f"- {holding['ticker']}: ${holding['value']:,.2f} ({holding['allocation']*100:.1f}%)\n"
        
        report += "\nSector Allocations:\n"
        for sector, allocation in sector_allocations.items():
            report += f"- {sector}: {allocation*100:.1f}%\n"

        return report
    

def portfolio_analysis_node(state):
    print("...................In portfolio node..................")
    portfolio_data = state["collected_data"]["portfolio_data"]
    
    portfolio_agent = PortfolioAnalysisAgent(portfolio_data)
    portfolio_report = portfolio_agent.generate_portfolio_report()

    return {
        "messages": state["messages"] + [AIMessage(content=portfolio_report)],
        "portfolio_report": portfolio_report
    }