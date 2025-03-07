from typing import List

from stock_market_agent.models.personas.aggressive_growth_seeker import AggressiveGrowthSeeker
from stock_market_agent.models.personas.conservative_investor import ConservativeInvestor
from stock_market_agent.models.personas.financial_agent import LLMFinancialAgent

def create_persona_agents(llm) -> List[LLMFinancialAgent]:
    return [
        LLMFinancialAgent(
            name="conservative_investor",
            traits={
                "risk_tolerance": "Low",
                "time_horizon": "Long-term",
                "priority": "Capital preservation"
            },
            strategy=[
                "Focus on blue-chip stocks and established companies",
                "Prefer companies with strong balance sheets and consistent dividends",
                "Utilize dollar-cost averaging for entering positions"
            ],
            focus=[
                "Dividend yield",
                "Price-to-earnings (P/E) ratio",
                "Debt-to-equity ratio",
                "Historical price stability"
            ],
            llm=llm,
            additional_data={
                "keys": ["historical_data", "risk_report", "indicators_data", "market_conditions", "rule_results"]
            }
        ),
        LLMFinancialAgent(
            name="aggressive_growth_seeker",
            traits={
                "risk_tolerance": "High",
                "time_horizon": "Short to medium-term",
                "priority": "High returns"
            },
            strategy=[
                "Invest in emerging markets and technologies",
                "Look for companies with high growth potential",
                "Use momentum trading techniques"
            ],
            focus=[
                "Revenue growth rate",
                "Market trend analysis",
                "Relative strength index (RSI)",
                "Earnings surprise history"
            ],
            llm=llm,
            additional_data={
                "keys": ["news_sentiment", "market_conditions", "indicators_data", "rule_results"]
            }
        ),
        # ... Create other agent types similarly ...
    ]

# def create_agents() -> List[FinancialAgent]:
#     return [
#         ConservativeInvestor(
#             name="Conservative Investor",
#             traits={"risk_tolerance": 0.2, "time_horizon": "long"},
#             strategy=["blue-chip stocks", "consistent dividends"],
#             focus=["dividend yield", "P/E ratio", "debt-to-equity ratio"]
#         ),
#         AggressiveGrowthSeeker(
#             name="Aggressive Growth Seeker",
#             traits={"risk_tolerance": 0.8, "time_horizon": "short"},
#             strategy=["emerging markets", "high growth potential"],
#             focus=["revenue growth rate", "RSI", "earnings surprise"]
#         ),
#         # ... Create instances of other agent classes ...
#     ]