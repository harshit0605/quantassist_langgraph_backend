from typing import Any, Dict, List
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from stock_market_agent.models.schemas import InvestmentDecision
from stock_market_agent.config.state import AgentState2

class Response:
            def __init__(self, decision, confidence, reasoning):
                self.decision = decision
                self.confidence = confidence
                self.reasoning = reasoning
                
class LLMFinancialAgent:
    def __init__(self, 
            name: str, 
            traits: Dict[str, Any], 
            strategy: List[str], 
            focus: List[str], 
            llm,
            additional_data: Dict[str, Any] = None):
        self.name : str = name
        self.traits: str = traits
        self.strategy: str = strategy
        self.focus: str = focus
        self.additional_data = additional_data or {}
        self.llm: BaseChatModel= llm.with_structured_output(InvestmentDecision)
        self.prompt: PromptTemplate = self._create_prompt()
        self.chain  = self.prompt | self.llm 

    def _create_prompt(self) -> PromptTemplate:
        template = """
        You are a {name}, an AI financial analyst with the following traits:
        {traits}

        Your investment strategy involves:
        {strategy}

        You focus on the following key areas when analyzing stocks:
        {focus}

        Rule-Based Recommendations:
        {custom_rule_result}

        Given the following market data:
        {market_data}

        Analyze the data and provide your investment recommendation. Your response should include:
        1. Your decision (Buy, Sell, or Hold)
        2. Your confidence level in this decision (0-1)
        3. A brief explanation of your reasoning

        Response Format:
        Decision: [Your decision]
        Confidence: [Your confidence level]
        Reasoning: [Your explanation]
        """

        return PromptTemplate(
            input_variables=["name", "traits", "strategy", "focus", "market_data", "custom_rule_result"],
            template=template
        )

    def analyze(self, agent_state: AgentState2) -> Dict[str, Any]:
        print(f"...................In {self.name} node..................")

        collected_data_from_prev_node = agent_state.get("collected_data", None)
        dry_run = agent_state.get("dry_run", False) if agent_state else False
        
        if collected_data_from_prev_node in [None, {}]:
            return {"analyses": []}

        traits_str = "\n".join(f"- {k}: {v}" for k, v in self.traits.items())
        strategy_str = "\n".join(f"- {s}" for s in self.strategy)
        focus_str = "\n".join(f"- {f}" for f in self.focus)
        custom_rule_result = agent_state.get("rule_results", "No data available")
        
        # Extract keys from additional_data to fetch corresponding values from agent_state
        keys_to_include = self.additional_data.get("keys", [])
        # print(f"In {self.name} ----------> Keys to include {keys_to_include}")

        market_data_str = "\n".join(
            f"- {key}: {agent_state.get(key, 'No data available.')}"
            for key in keys_to_include
        )

        input_data = {
            "name": self.name,
            "traits": traits_str,
            "strategy": strategy_str,
            "focus": focus_str,
            "custom_rule_result" : custom_rule_result,
            "market_data": market_data_str
        }

        # test_mode=True
        if dry_run:
            response = Response(
                decision="Hold",
                confidence=0.6,
                reasoning="Given the priority on capital preservation and a low risk tolerance, the current financial position is not urgent enough to trigger a buy or sell action. Despite positive cash flows and a positive price trend, high v olatility and a low profit margin introduce caution. The P/E ratio and moving averages suggest neutrality, aligned more closely with a 'Hold' strategy. Current price stability near the support level, consistent dividends, and historical stability support holding rather than making a hasty decision."
            )
                
        else:
            response = self.chain.invoke(input_data)


        return {
            "analyses":[
                {
                    "agent" : self.name,
                    "analysis" : {
                        "decision": response.decision,
                        "confidence": response.confidence,
                        "reasoning": response.reasoning
                    }                       
                }
            ]
        }
    
class AdaptiveWeightingSystem:
    def __init__(self, personas):
        self.personas = personas
        self.weights = {persona.name: 1/len(personas) for persona in personas}

    
    def update_weights(self, market_conditions: Dict[str, Any]):
        for persona in self.personas:
            self.weights[persona.name] = self._calculate_persona_relevance(persona, market_conditions)
        
        # Normalize weights
        total = sum(self.weights.values())
        self.weights = {k: v/total for k, v in self.weights.items()}
        return self.weights

    def _calculate_persona_relevance(self, persona, market_conditions):
       """
       Calculate the relevance weight of a persona based on market conditions.
       Higher weights indicate the persona's strategy is more relevant.
       
       Returns:
           float: Weight multiplier (typically between 0.5 and 2.0)
       """
       weight = 1.0
       
       # Volatility-based adjustments
       volatility = market_conditions.get('volatility', 'medium')
       risk_tolerance = persona.traits.get('risk_tolerance', 'Medium')
       
       volatility_weights = {
           ('high', 'Low'): 1.5,    # Conservative strategies preferred in high volatility
           ('high', 'Medium'): 1.2,
           ('high', 'High'): 0.8,   # Reduce aggressive strategies in high volatility
           ('low', 'Low'): 0.8,     # Reduce conservative strategies in low volatility
           ('low', 'Medium'): 1.0,
           ('low', 'High'): 1.3     # Favor aggressive strategies in low volatility
       }
       weight *= volatility_weights.get((volatility, risk_tolerance), 1.0)
        # Market trend adjustments
       trend = market_conditions.get('trend', 'neutral')
       if trend == 'bullish':
           if 'growth' in persona.focus:
               weight *= 1.3         # Growth strategies in bull markets
           if 'momentum' in persona.strategy:
               weight *= 1.2         # Momentum strategies in bull markets
       elif trend == 'bearish':
           if 'value' in persona.focus:
               weight *= 1.4         # Value strategies in bear markets
           if 'defensive' in persona.strategy:
               weight *= 1.3         # Defensive strategies in bear markets
        # Interest rate environment
       interest_rates = market_conditions.get('interest_rates', 'stable')
       if interest_rates == 'rising':
           if 'income' in persona.focus:
               weight *= 0.8         # Income strategies less favorable
           if 'growth' in persona.focus:
               weight *= 1.2         # Growth might outperform
       elif interest_rates == 'falling':
           if 'income' in persona.focus:
               weight *= 1.3         # Income strategies more attractive
           if 'bonds' in persona.focus:
               weight *= 1.2         # Bond strategies more attractive
        # Economic outlook adjustments
       outlook = market_conditions.get('economic_outlook', 'stable')
       if outlook == 'expanding':
           if 'cyclical' in persona.focus:
               weight *= 1.3         # Cyclical strategies in expansion
       elif outlook == 'contracting':
           if 'defensive' in persona.strategy:
               weight *= 1.4         # Defensive strategies in contraction
           if 'value' in persona.focus:
               weight *= 1.2         # Value strategies in contraction
        # Time horizon considerations
       time_horizon = persona.traits.get('time_horizon', 'Medium')
       if time_horizon == 'Long' and outlook == 'contracting':
           weight *= 1.2             # Long-term strategies more valuable in contractions
       elif time_horizon == 'Short' and volatility == 'high':
           weight *= 0.8             # Reduce short-term strategies in high volatility
        # Ensure weight stays within reasonable bounds (0.5 to 2.0)
       return max(0.5, min(2.0, weight))
    
    # def _calculate_persona_relevance(self, persona, market_conditions):
    #     # Implement logic to calculate relevance based on market conditions
    #     # This is a simplified example
    #     if market_conditions.get('volatility') == 'high' and persona.traits.get('risk_tolerance') == 'Low':
    #         return 1.5  # Increase weight for conservative investors in volatile markets
    #     elif market_conditions.get('trend') == 'bullish' and 'growth' in persona.focus:
    #         return 1.3  # Increase weight for growth-focused investors in bullish markets
    #     # ... add more conditions ...
    #     return 1.0  # Default weight
    
class FinancialAgent:
    # def __init__(self, name, risk_tolerance, time_horizon):
    #     self.name = name
    #     self.risk_tolerance = risk_tolerance
    #     self.time_horizon = time_horizon
    
    def __init__(self, name: str, traits: Dict[str, Any], strategy: List[str], focus: List[str]):
        self.name = name
        self.traits = traits
        self.strategy = strategy
        self.focus = focus
        self.confidence = 0.5
        self.success_rate = 0.5

    def adjust_risk(self, market_volatility):
        if market_volatility > self.volatility_threshold:
            self.risk_tolerance *= 0.9  # Reduce risk in volatile markets
        else:
            self.risk_tolerance *= 1.1  # Increase risk in stable markets
        self.risk_tolerance = max(0.1, min(1.0, self.risk_tolerance))  # Keep within bounds

    # If stability and the ability to analyze past decisions are more important (e.g., long-term investment strategies), the historical approach might be more suitable

    # def update_success_rate(self, decision, outcome):
    #     self.past_decisions.append((decision, outcome))
    #     if len(self.past_decisions) > 100:
    #         self.past_decisions.pop(0)
    #     self.success_rate = sum(1 for d, o in self.past_decisions if d == o) / len(self.past_decisions)

    # In scenarios where recent performance is more critical (e.g., high-frequency trading), the exponential moving average might be preferable due to its responsiveness.

    def update_success_rate(self, decision: str, outcome: str):
        # Update success rate based on decision outcome
        self.success_rate = 0.9 * self.success_rate + 0.1 * (decision == outcome)

    def analyze(self, data):
        # Basic analysis logic, to be overridden by specific agents
        return {"decision": "hold", "confidence": self.confidence}

class ValueInvestor(FinancialAgent):
    def analyze(self, data):
        # Conservative-specific analysis
        pass

class MomentumTrader(FinancialAgent):
    def analyze(self, data):
        # Conservative-specific analysis
        pass

class SectorSpecialist(FinancialAgent):
    def analyze(self, data):
        # Conservative-specific analysis
        pass

class GlobalMacroStrategist(FinancialAgent):
    def analyze(self, data):
        # Conservative-specific analysis
        pass
    