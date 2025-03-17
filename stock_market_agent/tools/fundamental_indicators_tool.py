import json
import os
import requests
from langchain.tools import BaseTool
from pydantic import Field
from typing import Literal
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from stock_market_agent.config.state import AgentState2

class FundamentalIndicatorsTool(BaseTool):
    name: Literal["Financial Indicators Tool"] = Field("Financial Indicators Tool")
    description: Literal["Get key financial indicators for a given ticker symbol"] = Field("Get key financial indicators for a given ticker symbol")
    api_key: str
    base_url: str = Field("https://www.alphavantage.co/query")

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
    
    def run(self, ticker: str, state: AgentState2 = None) -> str:
        return self._run(ticker, state)
    
    def _run(self, ticker: str, state: AgentState2=None) -> str:
            dry_run = state.get("dry_run", False) if state else False
            dry_run = True
            indicators = {}

            # Fetching different financial indicators
            functions = {
                "OVERVIEW": "Company Overview",
                "TIME_SERIES_DAILY": "Daily Time Series",
                "EARNINGS": "Earnings",
                "BALANCE_SHEET": "Balance Sheet",
                "INCOME_STATEMENT": "Income Statement",
                "CASH_FLOW": "Cash Flow"
            }

            temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
            os.makedirs(temp_data_folder, exist_ok=True)
            output_file_path = os.path.join(temp_data_folder, "financial_indicators_output.txt")

            if dry_run and os.path.exists(output_file_path):
                with open(output_file_path, "r") as f:
                    data = json.loads(f.read())
                return data

            for function, description in functions.items():
                params = {
                    "function": function,
                    "symbol": ticker,
                    "apikey": self.api_key
                }
                
                try:
                    response = requests.get(self.base_url, params=params)
                    response.raise_for_status()  # Raise exception for HTTP errors
                    data = response.json()
                    print(data)
                    
                    # Check for API error messages
                    if "Error Message" in data:
                        print(f"API Error for {description}: {data['Error Message']}")
                        continue
                    
                    if "Information" in data:
                        print(f"API Note for {description}: {data['Information']}")
                        continue
                        # This often indicates rate limiting
                    
                    # Print sample of data for debugging
                    print(f"API called for {description}. Sample data keys: {list(data.keys())[:5]}")
                    
                    if function == "OVERVIEW":
                        indicators.update({
                            "P/E Ratio": data.get("PERatio"),
                            "EPS": data.get("EPS"),
                            "Debt-to-Equity": data.get("DebtEquityRatio"),
                            "Current Ratio": data.get("CurrentRatio"),
                            "ROE": data.get("ReturnOnEquityTTM"),
                            "Profit Margin": data.get("ProfitMargin"),
                            "Dividend Yield": data.get("DividendYield"),
                            "Dividend Per Share": data.get("DividendPerShare"),
                        })
                    elif function == "TIME_SERIES_DAILY":
                        time_series = data.get("Time Series (Daily)", {})
                        if time_series:
                            latest_date = sorted(time_series.keys())[0]
                            latest_data = time_series[latest_date]
                            indicators.update({
                                "Short-term MA": latest_data.get("4. close"),  # Placeholder for actual calculation
                                "Long-term MA": latest_data.get("4. close"),  # Placeholder for actual calculation
                                "Average Volume": latest_data.get("5. volume"),  # Placeholder for actual calculation
                                "Current Volume": latest_data.get("5. volume")
                            })
                    elif function == "EARNINGS":
                        earnings = data.get("quarterlyEarnings", [])
                        if earnings:
                            print("earnings", earnings[0].get("reportedEPS"))
                            indicators["EPS"] = earnings[0].get("reportedEPS")
                    elif function == "BALANCE_SHEET":
                        balance_sheet = data.get("quarterlyReports", [])
                        if balance_sheet:
                            print("balance_sheet", balance_sheet[0].get("totalLiabilities"))
                            total_liabilities = balance_sheet[0].get("totalLiabilities")
                            total_shareholder_equity = balance_sheet[0].get("totalShareholderEquity")
                            if total_liabilities and total_shareholder_equity:
                                indicators["Debt-to-Equity"] = int(total_liabilities) / int(total_shareholder_equity)
                    elif function == "INCOME_STATEMENT":
                        income_statement = data.get("quarterlyReports", [])
                        if income_statement:
                            print("grossProfit", income_statement[0].get("grossProfit"))
                            gross_profit = income_statement[0].get("grossProfit")
                            total_revenue = income_statement[0].get("totalRevenue")
                            if gross_profit and total_revenue:
                                indicators["Profit Margin"] = int(gross_profit) / int(total_revenue)
                    elif function == "CASH_FLOW":
                        cash_flow = data.get("quarterlyReports", [])
                        if cash_flow:
                            operating_cashflow = int(cash_flow[0].get("operatingCashflow", 0))
                            capital_expenditures = int(cash_flow[0].get("capitalExpenditures", 0))
                            cashflow_from_investment = int(cash_flow[0].get("cashflowFromInvestment", 0))
                            cashflow_from_financing = int(cash_flow[0].get("cashflowFromFinancing", 0))

                            indicators.update({
                                "Operating Cash Flow": operating_cashflow,
                                "Free Cash Flow": operating_cashflow - capital_expenditures,
                                "Cash Flow from Investing": cashflow_from_investment,
                                "Cash Flow from Financing": cashflow_from_financing,
                                "Net Change in Cash": operating_cashflow + cashflow_from_investment + cashflow_from_financing
                            })
                except Exception as e:
                    print(f"Error fetching {description} data: {str(e)}")

            # If no data was retrieved, use sample data for testing
            # if not any(indicators.values()):
            #     print("No data retrieved from API. Using sample data for testing.")
            #     indicators = {
            #         "P/E Ratio": "25.5",
            #         "EPS": "5.72",
            #         "Debt-to-Equity": "1.2",
            #         "Current Ratio": "1.5",
            #         "ROE": "0.25",
            #         "Profit Margin": "0.15",
            #         "Short-term MA": "150.25",
            #         "Long-term MA": "145.75",
            #         "Average Volume": "35000000",
            #         "Current Volume": "40000000",
            #         "Volatility": "0.15",
            #         "Price Trend": "0.05",
            #         "Support Level": "145.00",
            #         "Resistance Level": "155.00",
            #         "Average Price": "148.50",
            #         "Operating Cash Flow": "25000000",
            #         "Free Cash Flow": "20000000",
            #         "Cash Flow from Investing": "-15000000",
            #         "Cash Flow from Financing": "-5000000",
            #         "Net Change in Cash": "5000000"
            #     }

            with open(output_file_path, "w") as f:
                f.write(json.dumps(indicators, indent=4))

            return indicators

    # def _run(self, ticker: str, state: AgentState2=None) -> str:
    #     dry_run = state.get("dry_run", False) if state else False
        
    #     indicators = {}

    #     # Fetching different financial indicators
    #     functions = {
    #         "OVERVIEW": "Company Overview",
    #         "TIME_SERIES_DAILY": "Daily Time Series",
    #         "EARNINGS": "Earnings",
    #         "BALANCE_SHEET": "Balance Sheet",
    #         "INCOME_STATEMENT": "Income Statement",
    #         "CASH_FLOW": "Cash Flow"
    #     }

    #     temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
    #     os.makedirs(temp_data_folder, exist_ok=True)
    #     output_file_path = os.path.join(temp_data_folder, "financial_indicators_output.txt")

    #     if dry_run and os.path.exists(output_file_path):
    #         with open(output_file_path, "r") as f:
    #             data = json.loads(f.read())
    #         return data

    #     for function, description in functions.items():
    #         params = {
    #             "function": function,
    #             "symbol": ticker,
    #             "apikey": self.api_key
    #         }
    #         response = requests.get(self.base_url, params=params)
    #         data = response.json()

    #         # Debugging information
    #         print(f"API called for {description}:")

    #         if function == "OVERVIEW":
    #             indicators.update({
    #                 "P/E Ratio": data.get("PERatio"),
    #                 "EPS": data.get("EPS"),
    #                 "Debt-to-Equity": data.get("DebtEquityRatio"),
    #                 "Current Ratio": data.get("CurrentRatio"),
    #                 "ROE": data.get("ReturnOnEquityTTM"),
    #                 "Profit Margin": data.get("ProfitMargin"),
    #                 "Dividend Yield": data.get("DividendYield"),
    #                 "Dividend Per Share": data.get("DividendPerShare"),
    #             })
    #         elif function == "TIME_SERIES_DAILY":
    #             time_series = data.get("Time Series (Daily)", {})
    #             if time_series:
    #                 latest_date = sorted(time_series.keys())[0]
    #                 latest_data = time_series[latest_date]
    #                 indicators.update({
    #                     "Short-term MA": latest_data.get("4. close"),  # Placeholder for actual calculation
    #                     "Long-term MA": latest_data.get("4. close"),  # Placeholder for actual calculation
    #                     "Average Volume": latest_data.get("5. volume"),  # Placeholder for actual calculation
    #                     "Current Volume": latest_data.get("5. volume")
    #                 })
    #         elif function == "EARNINGS":
    #             earnings = data.get("quarterlyEarnings", [])
    #             if earnings:
    #                 print("earnings", earnings[0].get("reportedEPS"))
    #                 indicators["EPS"] = earnings[0].get("reportedEPS")
    #         elif function == "BALANCE_SHEET":
    #             balance_sheet = data.get("quarterlyReports", [])
    #             if balance_sheet:
    #                 print("balance_sheet", balance_sheet[0].get("totalLiabilities"))
    #                 total_liabilities = balance_sheet[0].get("totalLiabilities")
    #                 total_shareholder_equity = balance_sheet[0].get("totalShareholderEquity")
    #                 if total_liabilities and total_shareholder_equity:
    #                     indicators["Debt-to-Equity"] = int(total_liabilities) / int(total_shareholder_equity)
    #         elif function == "INCOME_STATEMENT":
    #             income_statement = data.get("quarterlyReports", [])
    #             if income_statement:
    #                 print("grossProfit", income_statement[0].get("grossProfit"))
    #                 gross_profit = income_statement[0].get("grossProfit")
    #                 total_revenue = income_statement[0].get("totalRevenue")
    #                 if gross_profit and total_revenue:
    #                     indicators["Profit Margin"] = int(gross_profit) / int(total_revenue)
    #         elif function == "CASH_FLOW":
    #             cash_flow = data.get("quarterlyReports", [])
    #             if cash_flow:
    #                 operating_cashflow = int(cash_flow[0].get("operatingCashflow", 0))
    #                 capital_expenditures = int(cash_flow[0].get("capitalExpenditures", 0))
    #                 cashflow_from_investment = int(cash_flow[0].get("cashflowFromInvestment", 0))
    #                 cashflow_from_financing = int(cash_flow[0].get("cashflowFromFinancing", 0))

    #                 indicators.update({
    #                     "Operating Cash Flow": operating_cashflow,
    #                     "Free Cash Flow": operating_cashflow - capital_expenditures,
    #                     "Cash Flow from Investing": cashflow_from_investment,
    #                     "Cash Flow from Financing": cashflow_from_financing,
    #                     "Net Change in Cash": operating_cashflow + cashflow_from_investment + cashflow_from_financing
    #                 })

    #     with open(output_file_path, "w") as f:
    #             f.write(json.dumps(indicators, indent=4))

    #     return indicators
        
        # return f"""
        # Financial indicators for {ticker}:
        # P/E Ratio: {indicators.get("P/E Ratio")}
        # EPS: {indicators.get("EPS")}
        # Debt-to-Equity: {indicators.get("Debt-to-Equity")}
        # Current Ratio: {indicators.get("Current Ratio")}
        # ROE: {indicators.get("ROE")}
        # Short-term MA: {indicators.get("Short-term MA")}
        # Long-term MA: {indicators.get("Long-term MA")}
        # Average Volume: {indicators.get("Average Volume")}
        # Current Volume: {indicators.get("Current Volume")}
        # RSI: {indicators.get("RSI", "N/A")}  # Placeholder for actual calculation
        # Profit Margin: {indicators.get("Profit Margin")}
        # """

        
# Example usage
if __name__ == "__main__":
    api_key = "1KV9ZS0YZO8EQC43"
    tool = FundamentalIndicatorsTool(api_key=api_key)
    print(tool.run("AAPL"))  # Example ticker for Reliance Industries on BSE