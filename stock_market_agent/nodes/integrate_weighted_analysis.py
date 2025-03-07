import json
from typing import Dict, Any
from stock_market_agent.models.personas.financial_agent import AdaptiveWeightingSystem
from stock_market_agent.config.state import AgentState2


# def integrate_weighted_analyses(state: AgentState2, adaptiveWeightObj : AdaptiveWeightingSystem) -> Dict[str, Any]:
#     print("...................In integrate_weighted_analyses node..................")

#     market_conditions = state.get('market_conditions',None)
#     analyses = state.get("analyses",None)
#     if market_conditions is None or analyses in [None, []]:
#         return {"combined_weighted_analysis": ""}
    
    
#     decisions = {"Buy": 0, "Hold": 0, "Sell": 0}
#     total_confidence = 0
#     individual_analyses = []

#     # Update weights based on the market conditions
#     persona_weights = adaptiveWeightObj.update_weights(market_conditions)


#     for analysis in analyses:
#         agent_name = analysis['agent']
#         agent_analysis = analysis['analysis']
#         weight = persona_weights.get(agent_name, 1.0)
        
#         weighted_confidence = agent_analysis['confidence'] * weight
#         decisions[agent_analysis['decision']] += weighted_confidence
#         total_confidence += weighted_confidence

#         individual_analyses.append({
#             "agent": agent_name,
#             "decision": agent_analysis['decision'],
#             "confidence": agent_analysis['confidence'],
#             "weighted_confidence": weighted_confidence,
#             "reasoning": agent_analysis['reasoning']
#         })

#     # Sort individual analyses by weighted confidence
#     individual_analyses.sort(key=lambda x: x['weighted_confidence'], reverse=True)

#     # Normalize decision scores
#     for decision in decisions:
#         decisions[decision] /= total_confidence

#     final_decision = max(decisions, key=decisions.get)
#     final_confidence = decisions[final_decision]


#     # Compile reasoning summary
#     reasoning_summary = f"Decision based on Adaptive weighting of the differnet agent personas: {final_decision.upper()} with confidence {final_confidence}\n"
#     reasoning_summary += "Integrated Analysis Summary:\n"

#     for idx, analysis in enumerate(individual_analyses, 1):
#         reasoning_summary += f"{idx}. {analysis['agent']} ({analysis['decision'].upper()}, confidence: {analysis['weighted_confidence']:.2f}):\n"
#         reasoning_summary += f"   {analysis['reasoning']}\n\n"

#     return {
#         "combined_weighted_analysis": reasoning_summary
#     }

def integrate_weighted_analyses(state: AgentState2, adaptiveWeightObj: AdaptiveWeightingSystem) -> Dict[str, Any]:
    """
    Integrate multiple analyses with adaptive weighting to produce a final decision.

    Args:
        state: Current agent state containing market conditions and analyses
        adaptiveWeightObj: System for adjusting weights based on market conditions

    Returns:
        Dict containing combined analysis and metadata
    """
    print("...................In integrate_weighted_analyses node..................")

    market_conditions = state.get('market_conditions', None)
    analyses = state.get("analyses", None)

    # Input validation
    if not isinstance(analyses, list) or not analyses:
        return {"combined_weighted_analysis": "", "error": "No analyses provided"}
    
    # Validate market conditions
    if market_conditions is None:
        return {"combined_weighted_analysis": "", "error": "No market conditions provided"}
    
    # Update weights based on the market conditions
    persona_weights = adaptiveWeightObj.update_weights(market_conditions)
    
    decisions = {"Buy": 0, "Hold": 0, "Sell": 0}
    total_confidence = 0
    individual_analyses = []

    for analysis in analyses:
        # Validate analysis structure
        if not all(field in analysis for field in {'agent', 'analysis'}):
            continue

        agent_name = analysis['agent']
        agent_analysis = analysis['analysis']
        
        if not all(field in agent_analysis for field in {'decision', 'confidence', 'reasoning'}):
            continue

        # Ensure confidence is bounded
        confidence = max(0.0, min(1.0, agent_analysis['confidence']))
        
        # Retrieve the weight for the agent from persona_weights.
        weight = persona_weights.get(agent_name, 1.0)
        
        weighted_confidence = confidence * weight
        decisions[agent_analysis['decision']] += weighted_confidence
        total_confidence += weighted_confidence

        individual_analyses.append({
            "agent": agent_name,
            "decision": agent_analysis['decision'],
            "confidence": confidence,
            "weight": weight,
            "weighted_confidence": weighted_confidence,
            "reasoning": agent_analysis['reasoning']
        })
    # Handle zero confidence case
    if total_confidence <= 0:
        return {
            "combined_weighted_analysis": "Insufficient confidence in analyses",
            "error": "Total confidence is zero"
        }
    
    # Normalize decision scores
    for decision in decisions:
        decisions[decision] /= total_confidence

    # Sort analyses by weighted confidence
    individual_analyses.sort(key=lambda x: x['weighted_confidence'], reverse=True)

    # Determine final decision with confidence threshold
    CONFIDENCE_THRESHOLD = 0.4

    final_decision = max(decisions, key=decisions.get)
    final_confidence = decisions[final_decision]
    if final_confidence < CONFIDENCE_THRESHOLD:
        final_decision = "Hold"
        final_confidence = 1.0 - sum(v for k, v in decisions.items() if k != "Hold")

    # Compile reasoning summary
    reasoning_summary = (
        f"Decision based on Adaptive weighting of the different agent personas: "
        f"{final_decision.upper()} with confidence {final_confidence:.2f}\n"
        "Integrated Analysis Summary:\n"
    )

    # Create a structured dictionary for JSON conversion
    analysis_data = {
        "final_recommendation": {
            "decision": final_decision.upper(),
            "confidence": round(final_confidence, 2)
        },
        "decision_breakdown": {
            k: round(v, 2) for k, v in decisions.items()
        },
        "market_analysis": {
            "total_confidence": round(total_confidence, 2),
            "agent_weights": {
                k: round(v, 2) for k, v in persona_weights.items()
            }
        },
        "detailed_analyses": [
            {
                "agent": analysis['agent'],
                "decision": analysis['decision'].upper(),
                "confidence": round(analysis['confidence'], 2),
                "weight": round(analysis['weight'], 2),
                "weighted_confidence": round(analysis['weighted_confidence'], 2),
                "reasoning": analysis['reasoning'].strip()
            }
            for analysis in individual_analyses
        ]
    }

    # Convert to JSON string with proper formatting
    combined_weighted_analysis = json.dumps(analysis_data, indent=2)
    
    return {
        "combined_weighted_analysis": combined_weighted_analysis
    }