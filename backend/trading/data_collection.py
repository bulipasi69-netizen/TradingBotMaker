# backend/trading/data_collection.py

import requests
import os
from pandas import json_normalize
from urllib.parse import urlencode
from typing import Optional, Dict, Any
from pathlib import Path
from dotenv import load_dotenv


# --- Token Metrics API Integration ---

BASE_DIR = Path(__file__).resolve().parent.parent  # Adjust as needed to point to the project root
load_dotenv(os.path.join(BASE_DIR, '.env'))
API_KEY = os.getenv("TOKEN_METRICS_API_KEY")

def tm_API(endpoint: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Obtain data from the Token Metrics Data API.
    """
    base_url = 'https://alpha.data-api.tokenmetrics.com/v1/'
    if payload:
        url = base_url + endpoint + '?' + urlencode(payload)
    else:
        url = base_url + endpoint
    headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'api_key': API_KEY}
    response = requests.get(url, headers=headers)
    # Debug: Print status code and response content
    print("URL Requested:", url)
    print("Status Code:", response.status_code)
    print("Response Text:", response.text)

    # Check if the response has content and a status code of 200
    if response.status_code != 200 or not response.text.strip():
        raise Exception(f"Error fetching data: Status code {response.status_code}, Response: {response.text}")

    try:
        return response.json()
    except Exception as e:
        raise Exception("Failed to decode JSON: " + str(e))

def get_tokens_index() -> None:
    """
    Retrieve token index and filter for Bitcoin, Ethereum, and Litecoin.
    """
    endpoint = 'tokens'
    response = tm_API(endpoint)
    coins = json_normalize(response['data'])
    coins = coins.sort_values(by='TOKEN_ID').reset_index(drop=True)
    filtered = coins[coins.NAME.isin(['Bitcoin', 'Ethereum', 'Litecoin'])]
    print(filtered)
    

# --- Coinbase Pro Testnet Market Data ---
def get_cpx_testnet_market_data(symbol: str, start_date: str, end_date: str, granularity: int = 86400):
    """
    Retrieve historical candle data from Coinbase Pro Testnet.
    symbol: e.g., 'BTC-USD'
    Dates: in format 'YYYY-MM-DD'
    granularity: in seconds (86400 for daily)
    """
    base_url = f"https://api-public.sandbox.pro.coinbase.com/products/{symbol}/candles"
    params = {
        'start': start_date + "T00:00:00Z",
        'end': end_date + "T00:00:00Z",
        'granularity': granularity
    }
    response = requests.get(base_url, params=params)
    return response.json()

if __name__ == "__main__":
    # For testing purposes:
    print("Token Metrics Tokens Index:")
    get_tokens_index()
    print("Coinbase Pro Testnet Market Data for BTC-USD:")
    candles = get_cpx_testnet_market_data('BTC-USD', '2023-01-01', '2023-01-10')
    print(candles)
