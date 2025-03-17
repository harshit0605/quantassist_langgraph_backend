import json
import os
import yfinance as yf
from yfinance import Ticker
from datetime import datetime, timedelta
from typing import Literal
from pydantic import Field

import requests
from datetime import datetime, timedelta
from langchain.tools import BaseTool

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from stock_market_agent.config.state import AgentState2

# class HistoricalDataTool(BaseTool):
#     name = "Historical Data Tool"
#     description = "Get historical stock data for a given ticker symbol"
#     api_key = "YOUR_ALPHA_VANTAGE_API_KEY"  # Replace with your actual API key

#     def _run(self, ticker: str) -> str:
#         # Fetch historical data for the past 30 days
#         end_date = datetime.now()
#         start_date = end_date - timedelta(days=30)
#         start_date_str = start_date.strftime('%Y-%m-%d')
#         end_date_str = end_date.strftime('%Y-%m-%d')
        
#         # Use Alpha Vantage to get the historical data
#         url = f"https://www.alphavantage.co/query"
#         params = {
#             "function": "TIME_SERIES_DAILY",
#             "symbol": ticker,
#             "apikey": self.api_key,
#             "outputsize": "compact"
#         }
#         response = requests.get(url, params=params)
#         data = response.json()
        
#         # Check if the response contains the expected data
#         if "Time Series (Daily)" not in data:
#             return "Error fetching data from Alpha Vantage"
        
#         time_series = data["Time Series (Daily)"]
        
#         # Prepare the data in the desired format
#         historical_data = ["date,price,volume"]
#         for date in sorted(time_series.keys()):
#             if start_date_str <= date <= end_date_str:
#                 day_data = time_series[date]
#                 historical_data.append(f"{date},{day_data['4. close']},{day_data['5. volume']}")
        
#         return "\n".join(historical_data)


class HistoricalDataTool(BaseTool):
    name: Literal["Historical Data Tool"] = Field("Historical Data Tool")
    description: Literal["Get historical stock data for a given ticker symbol"] = Field("Get historical stock data for a given ticker symbol")

    def run(self, ticker: str, state: AgentState2 = None) -> str:
        return self._run(ticker, state)
    

    # def _run(self, ticker: str, state: AgentState2) -> str:

    #     dry_run = state.get("dry_run", False) if state else False  


    #     temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
    #     os.makedirs(temp_data_folder, exist_ok=True)
    #     output_file_path = os.path.join(temp_data_folder, "historical_data_output.txt")

    #     if dry_run and os.path.exists(output_file_path):
    #         with open(output_file_path, "r") as f:
    #             data = f.read()
    #         return data
        

    #     # Fetch historical data for the past 30 days
    #     end_date = datetime.now()
    #     start_date = end_date - timedelta(days=30)
        
    #     # Use yfinance to get the historical data
    #     stock_data = yf.download(ticker, start=start_date, end=end_date)
        
    #     # Prepare the data in the desired format
    #     data = ["date,price,volume"]
    #     for date, row in stock_data.iterrows():
    #         data.append(f"{date.strftime('%Y-%m-%d')},{row['Close']:.2f},{int(row['Volume'])}")
        
    #     with open(output_file_path, "w") as f:
    #             f.write("\n".join(data))
    #     return "\n".join(data)
    
    def _run(self, ticker: str, state: AgentState2 = None) -> str:
        dry_run = state.get("dry_run", False) if state else False  
        dry_run = True

        temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
        os.makedirs(temp_data_folder, exist_ok=True)
        output_file_path = os.path.join(temp_data_folder, "historical_data_output.txt")

        if dry_run and os.path.exists(output_file_path):
            with open(output_file_path, "r") as f:
                data = f.read()
            return data
        
        try:
            # Fetch historical data for the past 30 days
            end_date = datetime.now().date()  # Use only the date part
            start_date = end_date - timedelta(days=30)

            # Convert dates to strings
            start_date_str = start_date.strftime('%Y-%m-%d')
            end_date_str = end_date.strftime('%Y-%m-%d')
            
            # # Use yfinance download with proper parameters
            # stock_data = yf.download(
            #     ticker.upper().strip(),
            #     start=start_date,
            #     end=end_date,
            #     progress=False,
            #     interval='1d',
            #     ignore_tz=True  # Ignore timezone issues
            # )
            
            ticker_obj = Ticker(ticker.upper().strip())
            stock_data = ticker_obj.history(
                start=start_date_str,
                end=end_date_str,
                interval='1d'
            )
            
            if stock_data.empty:
                return f"No data found for ticker symbol: {ticker}"
            
            # Prepare the data in the desired format
            data = ["date,price,volume"]
            for date, row in stock_data.iterrows():
                data.append(f"{date.strftime('%Y-%m-%d')},{row['Close']:.2f},{int(row['Volume'])}")
            
            with open(output_file_path, "w") as f:
                f.write("\n".join(data))
            return "\n".join(data)
            
        except Exception as e:
            error_message = f"Error fetching data for {ticker}: {str(e)}"
            print(error_message)
            return error_message
       
        
# Example usage
if __name__ == "__main__":
    # api_key = "IKPRCH1Z25YCA2SP"
    # tool = HistoricalDataTool(api_key=api_key)
    tool = HistoricalDataTool()
    print(tool.run("AAPL"))  # Example ticker for Reliance Industries on BSE