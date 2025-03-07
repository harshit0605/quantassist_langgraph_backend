import json
import os
import requests
from langchain_core.tools import BaseTool

class StockPriceTool(BaseTool):
    name: str = "Stock Price Tool"
    description: str = "Get the latest stock price for a given ticker symbol from the Indian stock market"
    api_key: str 
    base_url: str = "https://www.alphavantage.co/query"

    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def _run(self, ticker: str) -> str:
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": ticker,
            "apikey": self.api_key
        }

        temp_data_folder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'tempData'))
        os.makedirs(temp_data_folder, exist_ok=True)
        output_file_path = os.path.join(temp_data_folder, "stock_price_output.txt")

        if os.path.exists(output_file_path):
            with open(output_file_path, "r") as f:
                data = json.loads(f.read())
        else:
            response = requests.get(self.base_url, params=params)
            data = response.json()

            # Write outputs to separate text files in the tempData folder
            with open(output_file_path, "w") as f:
                f.write(json.dumps(data, indent=4))
                
        # response = requests.get(self.base_url, params=params)
        # data = response.json()

        if "Global Quote" in data:
            latest_price = data["Global Quote"]["05. price"]
            return f"{latest_price}"
        else:
            return f"Failed to fetch data for {ticker}. Error: {data.get('Note', 'Unknown error')}"

        # if "Global Quote" in data:
        #     latest_price = data["Global Quote"]["05. price"]
        #     content = f"The latest price for {ticker} is {latest_price}."
        #     artifact = data  # Including the full response as an artifact
        #     return content, artifact
        # else:
        #     error_message = f"Failed to fetch data for {ticker}. Error: {data.get('Note', 'Unknown error')}"
        #     return error_message, {}

# Example usage
if __name__ == "__main__":
    api_key = "IKPRCH1Z25YCA2SP"
    tool = StockPriceTool(api_key)
    print(tool.run("RELIANCE.BSE"))  # Example ticker for Reliance Industries on BSE