from typing import Any, Dict, List
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.language_models.chat_models import BaseChatModel

from stock_market_agent.models.schemas import FinalInvestmentDecision
from stock_market_agent.config.state import AgentState2

class MetaAnalysisLLM:
    def __init__(self, llm):
        self.llm: BaseChatModel = llm.with_structured_output(FinalInvestmentDecision)
        self.prompt = self.create_meta_analysis_prompt()
        self.chain = self.prompt | self.llm 

    def create_meta_analysis_prompt(self) -> PromptTemplate:
        template = """
        You are a expert financial meta-analyst. Your task is to analyze the conclusions and reasonings of multiple financial agents, each with their own expertise and perspective, and provide a final investment recommendation.

        Market Data:
        {market_data}

        Market Conditions:
        {market_conditions}

        Weighted Agent Analyses Summary:
        {combined_weighted_analysis}

        Based on the above information, please provide:
        1. A final investment decision (Buy, Sell, or Hold)
        2. A confidence level for this decision (0-1)
        3. A comprehensive reasoning for your decision, taking into account the various perspectives and any conflicts or agreements between the agents
        4. Any additional insights or considerations that might be valuable for the investment decision

        Your response should be structured as follows:
        Decision: [Your decision]
        Confidence: [Your confidence level]
        Reasoning: [Your comprehensive reasoning]
        Additional Insights: [Any extra valuable information]
        """
        return PromptTemplate(
            input_variables=["market_data", "market_conditions", "combined_weighted_analysis"],
            template=template
        )

    def analyze(self, 
                state: AgentState2, 
            ) -> Dict[str, Any]:
        
        print(f"...................In Meta analysis node..................")
        market_data = state.get("collected_data",None)
        market_conditions = state.get("market_conditions", None)
        combined_weighted_analysis = state.get("combined_weighted_analysis", None)

        if market_data is None or market_conditions is None or combined_weighted_analysis in [None, ""]:
            return {
                    "final_prediction": {}
                }
        
        market_data_str = "\n".join(f"- {k}: {v}" for k, v in market_data.items())
        market_conditions_str = "\n".join(f"- {k}: {v}" for k, v in market_conditions.items())
        
        # agent_analyses_str = ""
        # for analysis in agent_analyses:
        #     agent_analyses_str += f"\nAgent: {analysis['agent']}\n"
        #     agent_analyses_str += f"Decision: {analysis['analysis']['decision']}\n"
        #     agent_analyses_str += f"Confidence: {analysis['analysis']['confidence']:.2f}\n"
        #     agent_analyses_str += f"Reasoning: {analysis['analysis']['reasoning']}\n"
        #     # agent_analyses_str += f"Weight: {analysis['weight']:.2f}\n"

        input_data = {
            "market_data": market_data_str,
            "market_conditions": market_conditions_str,
            "combined_weighted_analysis": combined_weighted_analysis
        }
        
        
        class Response:
            def __init__(self, final_decision, confidence, reasoning, additional_insights):
                self.final_decision = final_decision
                self.confidence = confidence
                self.reasoning = reasoning
                self.additional_insights = additional_insights

        response = None
        test_mode = True
        if test_mode:
            # Return a dummy response for testing
            response = Response(
                final_decision="Hold",
                confidence=0.75,
                reasoning="This is a dummy reasoning for testing purposes.",
                additional_insights="These are additional insights for testing."
            )
        else:
            # Call the LLM as usual
            response = self.chain.invoke(input=input_data)
        # response = self.chain.invoke(input=input_data)

        return {
            "final_prediction": {
                "final_analysis": {
                    "decision": response.final_decision,
                    "confidence": response.confidence,
                    "reasoning": response.reasoning,
                },
                "additional_insights": response.additional_insights
            }
        }
    