from typing import Any, Dict
from stock_market_agent.models.personas.financial_agent import FinancialAgent

class ConservativeInvestor(FinancialAgent):
    def analyze(self, data: Dict[str, Any]) -> Dict[str, Any]:
        # Implement conservative analysis logic
        dividend_yield = data.get("dividend_yield", 0)
        pe_ratio = data.get("pe_ratio", float('inf'))
        debt_equity_ratio = data.get("debt_equity_ratio", float('inf'))
        
        score = 0
        if dividend_yield > 0.03:  # 3% dividend yield threshold
            score += 1
        if pe_ratio < 15:  # Conservative P/E ratio
            score += 1
        if debt_equity_ratio < 0.5:  # Conservative debt-to-equity ratio
            score += 1
        
        decision = "buy" if score >= 2 else "hold"
        self.confidence = score / 3  # Normalize confidence
        
        return {"decision": decision, "confidence": self.confidence}