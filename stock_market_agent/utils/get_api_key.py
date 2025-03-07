import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_api_key(service_name):
    """
    Fetches the API key for a given service from the .env file.

    Args:
        service_name (str): The name of the API key (environment variable) to fetch.

    Returns:
        str: The API key if found, raises KeyError if the key is missing.
    """
    try:
        # Get the API key from the environment variables
        api_key = os.getenv(service_name)
        
        # Raise an error if the API key is not found
        if api_key is None or api_key.strip() == "":
            raise KeyError(f"API key for {service_name} not found in environment variables.")
        
        return api_key
    
    except KeyError as e:
        # Log the error or handle it appropriately
        print(f"Error: {e}")
        return None
        # raise

    except Exception as e:
        # Catch any other exceptions and log
        print(f"Unexpected error while fetching API key: {e}")
        # raise
        return None

# Example usage
if __name__ == "__main__":
    try:
        alpha_vantage_key = get_api_key("ALPHA_VANTAGE_API_KEY")
        print(f"Alpha Vantage API Key: {alpha_vantage_key}")
    except KeyError as e:
        print(f"Could not fetch API key: {e}")
