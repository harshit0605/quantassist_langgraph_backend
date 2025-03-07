from typing import Dict, List, Tuple, Union

import numpy as np
from stock_market_agent.models.evaluation_data import EvaluationData


class WeightedRule:
    def __init__(self, rule_func, weight: float):
        self.rule_func = rule_func
        self.weight = weight

# New: Custom Rules Engine

class CustomRulesEngine:
    def __init__(self):
        self.rules = [
            WeightedRule(self.pe_ratio_rule, 0.2),
            WeightedRule(self.moving_average_rule, 0.3),
            WeightedRule(self.volume_spike_rule, 0.15),
            # WeightedRule(self.rsi_rule, 0.25),
            WeightedRule(self.profit_margin_rule, 0.1),
            WeightedRule(self.trend_rule, 0.15),
            WeightedRule(self.support_resistance_rule, 0.15),
            WeightedRule(self.sentiment_rule, 0.2),  # New sentiment rule
            WeightedRule(self.volatility_rule, 0.1),  # New volatility rule
            WeightedRule(self.current_price_rule, 0.1),
            WeightedRule(self.operating_cash_flow_rule, 0.1),  # New rule
            WeightedRule(self.free_cash_flow_rule, 0.1),  # New rule
            WeightedRule(self.cash_flow_from_investing_rule, 0.1),  # New rule
            WeightedRule(self.cash_flow_from_financing_rule, 0.1),  # New rule
            WeightedRule(self.net_change_in_cash_rule, 0.1),  # New rule
            # Add more weighted rules as needed
        ]
        self.validate_weights() # Validate and normalize rule weights
    
    def validate_weights(self):
        """Ensure weights are properly normalized."""
        total_weight = sum(rule.weight for rule in self.rules)
        if not np.isclose(total_weight, 1.0):
            # Normalize weights to sum to 1
            for rule in self.rules:
                rule.weight = rule.weight / total_weight
    
    def pe_ratio_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        pe_ratio = float(data.indicator_data['P/E Ratio'])
        if pe_ratio < 15:
            return "Buy", 1.0, f"Low P/E Ratio of {pe_ratio} indicates undervaluation."
        elif pe_ratio > 30:
            return "Sell", 1.0, f"High P/E Ratio of {pe_ratio} indicates overvaluation."
        return "Hold", 0.5, f"P/E Ratio of {pe_ratio} is within normal range."

    def moving_average_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        short_ma = float(data.indicator_data['Short-term MA'])
        long_ma = float(data.indicator_data['Long-term MA'])
        difference = (short_ma - long_ma) / long_ma
        if difference > 0.05:
            return "Buy", 1.0, f"Short-term MA ({short_ma}) is above Long-term MA ({long_ma})."
        elif difference < -0.05:
            return "Sell", 1.0, f"Short-term MA ({short_ma}) is below Long-term MA ({long_ma})."
        return "Hold", 0.5, "Moving Averages are neutral."

    def volume_spike_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        avg_volume = float(data.indicator_data['Average Volume'])
        current_volume = float(data.indicator_data['Current Volume'])
        if current_volume > (1.5 * avg_volume):
            return "Buy", 1.0, f"Significant volume increase (Current: {current_volume}, Average: {avg_volume})."
        elif current_volume < (0.5 * avg_volume):
            return "Sell", 0.8, f"Significant volume decrease (Current: {current_volume}, Average: {avg_volume})."
        return "Hold", 0.3, f"Normal trading volume (Current: {current_volume}, Average: {avg_volume})."

    def volatility_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        volatility = float(data.indicator_data['Volatility'])
        if volatility > 0.2:
            return "Sell", 0.8, f"High volatility of {volatility}."
        elif volatility < 0.1:
            return "Buy", 0.8, f"Low volatility of {volatility}."
        return "Hold", 0.5, f"Moderate volatility of {volatility}."

    def current_price_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        current_price = float(data.indicator_data['stock_price'])
        average_price = float(data.indicator_data['Average Price'])
        if current_price < average_price * 0.9:
            return "Buy", 0.7, f"Current price ({current_price}) is significantly lower than average price ({average_price})."
        elif current_price > average_price * 1.1:
            return "Sell", 0.7, f"Current price ({current_price}) is significantly higher than average price ({average_price})."
        return "Hold", 0.5, f"Current price ({current_price}) is close to average price ({average_price})."

    def profit_margin_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        profit_margin = float(data.indicator_data['Profit Margin'])
        if profit_margin > 20:
            return "Buy", 0.8, f"High profit margin of {profit_margin}%."
        elif profit_margin < 5:
            return "Sell", 0.8, f"Low profit margin of {profit_margin}%."
        return "Hold", 0.4, f"Moderate profit margin of {profit_margin}%."

    def trend_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        trend = float(data.indicator_data['Price Trend'])
        if trend > 0.1:
            return "Buy", 1.0, f"Positive price trend of {trend}."
        elif trend < -0.1:
            return "Sell", 1.0, f"Negative price trend of {trend}."
        return "Hold", 0.5, f"Neutral price trend of {trend}."

    def support_resistance_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        current_price = float(data.indicator_data['stock_price'])
        support = float(data.indicator_data['Support Level'])
        resistance = float(data.indicator_data['Resistance Level'])
        
        if current_price < support * 1.05:
            return "Buy", 0.8, f"Current price ({current_price}) is near support level ({support})."
        elif current_price > resistance * 0.95:
            return "Sell", 0.8, f"Current price ({current_price}) is near resistance level ({resistance})."
        return "Hold", 0.5, f"Current price ({current_price}) is between support ({support}) and resistance ({resistance})."
    
    def sentiment_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        sentiment_info = data.sentiment_data
        sentiment_label = sentiment_info.get("sentiment", "Neutral")
        average_score = sentiment_info.get("average_score", 0.0)

        if sentiment_label == "Positive":
            return "Buy", 1.0, f"Positive sentiment with an average score of {average_score}."
        elif sentiment_label == "Negative":
            return "Sell", 1.0, f"Negative sentiment with an average score of {average_score}."
        return "Hold", 0.5, f"Neutral sentiment with an average score of {average_score}."

    def operating_cash_flow_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        operating_cash_flow = float(data.indicator_data.get('Operating Cash Flow'))
        if operating_cash_flow > 0:
            return "Buy", 0.8, f"Positive operating cash flow of {operating_cash_flow}."
        elif operating_cash_flow < 0:
            return "Sell", 0.8, f"Negative operating cash flow of {operating_cash_flow}."
        return "Hold", 0.5, f"Neutral operating cash flow of {operating_cash_flow}."

    def free_cash_flow_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        free_cash_flow = float(data.indicator_data['Free Cash Flow'])
        if free_cash_flow > 0:
            return "Buy", 0.8, f"Positive free cash flow of {free_cash_flow}."
        elif free_cash_flow < 0:
            return "Sell", 0.8, f"Negative free cash flow of {free_cash_flow}."
        return "Hold", 0.5, f"Neutral free cash flow of {free_cash_flow}."

    def cash_flow_from_investing_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        cash_flow_from_investing = float(data.indicator_data['Cash Flow from Investing'])
        if cash_flow_from_investing < 0:
            return "Buy", 0.6, f"Negative cash flow from investing ({cash_flow_from_investing}), indicating investment in growth."
        elif cash_flow_from_investing > 0:
            return "Sell", 0.6, f"Positive cash flow from investing ({cash_flow_from_investing}), indicating divestment of assets."
        return "Hold", 0.5, f"Neutral cash flow from investing ({cash_flow_from_investing})."

    def cash_flow_from_financing_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        cash_flow_from_financing = float(data.indicator_data['Cash Flow from Financing'])
        if cash_flow_from_financing > 0:
            return "Buy", 0.6, f"Positive cash flow from financing ({cash_flow_from_financing}), indicating raising capital."
        elif cash_flow_from_financing < 0:
            return "Sell", 0.6, f"Negative cash flow from financing ({cash_flow_from_financing}), indicating paying off debt."
        return "Hold", 0.5, f"Neutral cash flow from financing ({cash_flow_from_financing})."

    def net_change_in_cash_rule(self, data: EvaluationData) -> Tuple[str, float, str]:
        net_change_in_cash = float(data.indicator_data['Net Change in Cash'])
        if net_change_in_cash > 0:
            return "Buy", 0.7, f"Positive net change in cash ({net_change_in_cash})."
        elif net_change_in_cash < 0:
            return "Sell", 0.7, f"Negative net change in cash ({net_change_in_cash})."
        return "Hold", 0.5, f"Neutral net change in cash ({net_change_in_cash})."
    
    def extract_metric(self, rule_func, data: EvaluationData) -> str:
        # Mapping of rule functions to their corresponding metric keys
        rule_to_metrics = {
            self.pe_ratio_rule: ["P/E Ratio"],
            self.moving_average_rule: ["Short-term MA", "Long-term MA"],
            self.volume_spike_rule: ["Current Volume", "Average Volume"],
            self.volatility_rule: ["Volatility"],
            self.current_price_rule: ["Current Price", "Average Price"],
            self.profit_margin_rule: ["Profit Margin"],
            self.trend_rule: ["Price Trend"],
            self.support_resistance_rule: ["Current Price", "Support Level", "Resistance Level"],
            self.sentiment_rule: ["sentiment"],
            self.operating_cash_flow_rule: ["Operating Cash Flow"],
            self.free_cash_flow_rule: ["Free Cash Flow"],
            self.cash_flow_from_investing_rule: ["Cash Flow from Investing"],
            self.cash_flow_from_financing_rule: ["Cash Flow from Financing"],
            self.net_change_in_cash_rule: ["Net Change in Cash"],
            # Add more mappings as needed
        }

        # Retrieve the metric keys for the given rule function
        metric_keys = rule_to_metrics.get(rule_func, [])

        # Construct the metric string
        metrics = []
        for key in metric_keys:
            if key in data.indicator_data:
                metrics.append(f"{key}: {data.indicator_data.get(key, 'N/A')}")
            elif key in data.sentiment_data:
                metrics.append(f"{key}: {data.sentiment_data.get(key, 'N/A')}")
        
        return ", ".join(metrics) if metrics else "Metric not available"

    def calculate_weighted_scores(self, data: EvaluationData) -> Tuple[Dict[str, Dict[str, Union[float, str]]], List[str]]:
        """Calculate weighted scores and detailed reasoning for each action."""
        results = {
           "Buy": {"score": 0, "reasoning": []},
           "Sell": {"score": 0, "reasoning": []},
           "Hold": {"score": 0, "reasoning": []}
        }

        for weighted_rule in self.rules:
            action, confidence, reasoning = weighted_rule.rule_func(data)
            
            # Apply exponential weighting to confidence
            confidence_exp = np.exp(confidence - 1)

            # Calculate detailed reasoning
            rule_reasoning = (
                f"Rule: {weighted_rule.rule_func.__name__}\n"
                f"Metric: {self.extract_metric(weighted_rule.rule_func, data)}\n"
                f"Condition: {reasoning}\n"
                f"Confidence: {confidence}\n"
            )

            # Update scores and reasoning
            results[action]["score"] += weighted_rule.weight * confidence_exp
            results[action]["reasoning"].append(rule_reasoning)
        # Normalize scores
        total_score = sum(results[action]["score"] for action in results)
        if total_score > 0:
            for action in results:
                results[action]["score"] /= total_score
        return results
    
    def evaluate(self, data: EvaluationData, threshold: float = 0.5) -> Dict[str, Dict[str, Union[float, str]]]:
        """
        Evaluate market data and return formatted results with scores, reasoning, and best action.
        
        Args:
            data: Market data to analyze
            threshold: Minimum score required for Buy/Sell decision (default: 0.5)
        
        Returns:
            Dictionary containing scores, reasoning, and best action recommendation
        """
        results = self.calculate_weighted_scores(data)

        # Determine best action
        best_action = max(results.items(), key=lambda x: x[1]["score"])
        action, details = best_action

        # Default to Hold if no strong signals
        if details["score"] < threshold:
            action = "Hold"
            hold_score = 1 - sum(results[k]["score"] for k in ["Buy", "Sell"])
            results["Hold"]["score"] = hold_score

        # Format the output
        formatted_results = {}
        for act, details in results.items():
            formatted_results[act] = {
                "score": round(details["score"], 2),
                "reasoning": "\n\n".join(details["reasoning"])
            }

        # Add best action recommendation
        formatted_results["recommendation"] = {
            "action": action,
            "confidence": round(results[action]["score"], 2),
            "threshold_used": threshold
        }
        return formatted_results
    