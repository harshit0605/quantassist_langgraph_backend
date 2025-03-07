# Add the parent directory to the Python path
import sys, os, requests
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "..")))
# print(sys.path)

from langchain_openai import ChatOpenAI
from langchain.tools import BaseTool
from pydantic import Field, PrivateAttr
from typing import List, Literal
from stock_market_agent.models.schemas import StockName, CompanySelection, Stocks
from stock_market_agent.utils.get_api_key import get_api_key


class CompanyTickerTool(BaseTool):
    name: Literal["Stock name extraction tool"] = Field(default="Stock company name extraction tool")
    description: Literal["Extracts the name of the company"] = Field(default="Extracts the name of the company")

    _chat_api_key: str = PrivateAttr()
    _alphavantage_api_key: str = PrivateAttr()

    def __init__(self):
        super().__init__()
        self._chat_api_key = get_api_key("OPENAI_API_KEY")
        self._alphavantage_api_key = get_api_key("ALPHA_VANTAGE_API_KEY")

    def _run(self, query: str) -> List[str]:
        prompt = f"""Given the user's query: '{query}', 
        <instructions>
        1. identify the company names mentioned in the query
        2. For each company, get the stock ticker associated with that company. The ticker id will be used in alphavantage API to get further information about the stock"""

        try:
            model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=self._chat_api_key)
            structured_llm = model.with_structured_output(Stocks)
            response = structured_llm.invoke(prompt)
            return response
        except Exception as e:
            return f"Error extracting stock data: {str(e)} "
            # raise RuntimeError(f"Failed to extract stock info: {str(e)}")
                



    # def _run(self, query: str) -> List[str]:
    #     try:
    #         # Extract the stock name from the user's query
    #         company_names = self.extract_stock_names(query)
    #         print("company_names", company_names)
    #     except RuntimeError as e:
    #         return f"Error extracting stock name: {str(e)}"
    #     except Exception as e:
    #         return f"Unexpected error during stock name extraction: {str(e)}"

    #     all_best_tickers = []
    #     for company_name in company_names:

    #         try:
    #             # Get the ticker symbol for the company name
    #             ticker_best_matches = self.search_symbol(company_name)
    #         except RuntimeError as e:
    #             return f"error searching for ticker symbol: {str(e)}"
    #         except Exception as e:
    #             return f"Unexpected error during ticker symbol search: {str(e)}"
    
    #         try:
    #             # Select the best ticker from the matches
    #             best_ticker = self.select_best_ticker(query, ticker_best_matches)
    #             print("company_name", company_name)
    #             print("best_ticker", best_ticker)
    #             all_best_tickers.append(best_ticker)
    #         except RuntimeError as e:
    #             return f"error selecting best ticker: {str(e)}"
    #         except Exception as e:
    #             return f"Unexpected error during ticker selection: {str(e)}"

    #     return ", ".join(all_best_tickers)
    
    def extract_stock_names(self, query: str) -> List[str]:
        if not self._chat_api_key:
            raise ValueError("No OPENAI_API_KEY API key found. Please set the OPENAI_API_KEY environment variable.")
        
        try:
            model = ChatOpenAI(model="gpt-3.5-turbo-0125", temperature=0, api_key=self._chat_api_key)
            structured_llm = model.with_structured_output(StockName)
            response = structured_llm.invoke(query)
            return response.stock_names
        except Exception as e:
            raise RuntimeError(f"Failed to extract stock name: {str(e)}")
     
    def search_symbol(self, company_name):
        if not self._alphavantage_api_key:
            raise ValueError("No ALPHA_VANTAGE API key found. Please set the ALPHA_VANTAGE_API_KEY environment variable.")
        
        try:
            # Use Alpha Vantage's SYMBOL_SEARCH function
            base_url = "https://www.alphavantage.co/query"
            params = {
                "function": "SYMBOL_SEARCH",
                "keywords": company_name,
                "apikey": self._alphavantage_api_key
            }
            
            response = requests.get(base_url, params=params)
            data = response.json()
            
            if "bestMatches" in data and data["bestMatches"]:
                # Extract the first match's ticker symbol
                # print("Raw data", data)
                # print("Best matches", data["bestMatches"])
                return data["bestMatches"]
            else:
                raise RuntimeError("No matches found for the given company name.")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"HTTP request failed: {str(e)}")
        except ValueError as e:
            raise RuntimeError(f"Failed to parse JSON response: {str(e)}")

    def select_best_ticker(self, query: str, ticker_best_matches: list[dict]) -> str:
        if not self._chat_api_key:
            raise ValueError("No OPENAI_API_KEY API key found. Please set the OPENAI_API_KEY environment variable.")
        
        try:
            model = ChatOpenAI(model="gpt-4o", temperature=0, api_key=self._chat_api_key)
            structured_llm = model.with_structured_output(CompanySelection)

            # Prepare a prompt to ask the model which company is most likely being referred to
            prompt = f"Given the user's query: '{query}', which of the following companies is most likely being referred to?\n"
            for i, match in enumerate(ticker_best_matches):
                prompt += f"{i+1}. {match['2. name']} (Ticker: {match['1. symbol']})\n"
            
            prompt += """Please provide the number of the most likely company. Keep in mind the overall context of the query deducing the likely domain in which the company might exist. 
            """

            # Invoke the model with the prompt
            response = structured_llm.invoke(prompt)
            
            # Parse the response to get the selected company index
            selected_index = int(response.selected_index) - 1
            if 0 <= selected_index < len(ticker_best_matches):
                selected_ticker =  ticker_best_matches[selected_index]["1. symbol"]
                print("selected_ticker", selected_ticker)
                return selected_ticker
            else:
                raise RuntimeError("Selected index is out of range.")

        except (ValueError, IndexError):
            raise RuntimeError(f"Failed to select best ticker: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Model invocation failed: {str(e)}")
        
        # Fallback if parsing fails or no valid index is returned
        # return "Ticker not found"

if __name__ == "__main__":
    company_name_tool = CompanyTickerTool()
    # query = "Get the name of the stock mentioned in the query"
    query = "Get me the latest financial statements for Apple and Microsoft"
    print(company_name_tool.run(query))  # Example ticker for Reliance Industries on BSE

