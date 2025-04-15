import os
import json
import time
import base64
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables; adjust path as needed.
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))

def gemini_auth_headers(request_path: str, payload: dict, api_key: str, api_secret: str) -> dict:
    """
    Create Gemini authentication headers.
    The payload is dumped to JSON (without extra whitespace), base64-encoded,
    and signed using HMAC-SHA384 with the API secret.
    """
    # Dump with no extra whitespace (compact representation)
    payload_json = json.dumps(payload, separators=(',', ':'))
    encoded_payload = base64.b64encode(payload_json.encode())
    signature = hmac.new(api_secret.encode(), encoded_payload, hashlib.sha384).hexdigest()
    headers = {
        'Content-Type': 'text/plain',
        'Cache-Control': 'no-cache',
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': encoded_payload.decode(),
        'X-GEMINI-SIGNATURE': signature
    }
    return headers

def get_gemini_account_info() -> list:
    """
    Retrieve account balances from Gemini Sandbox using GET /v1/balances.
    If the endpoint returns 404, return a dummy account info with a valid account name.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/balances"
    nonce = str(int(time.time() * 1000))
    payload = {
        "request": "/v1/balances",
        "nonce": nonce
    }
    headers = gemini_auth_headers("/v1/balances", payload, api_key, api_secret)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()  # Expecting a list of account objects.
    except requests.exceptions.HTTPError as e:
        if response.status_code == 404:
            print("Warning: /v1/balances returned 404. Returning dummy account info for testing.")
            # Return dummy info with a valid account name: "primary"
            return [{
                "currency": "USD",
                "available": "100000",
                "hold": "0",
                "balance": "100000",
                "account": "primary"
            }]
        else:
            raise e

def create_gemini_order(product: str, side: str, quantity: str, price: str) -> dict:
    """
    Create a limit order on Gemini Sandbox using the POST /v1/order/new endpoint.
    The order uses immediate-or-cancel behavior, meaning that if it cannot be filled immediately,
    any unfilled portion will be canceled rather than held.
    
    Parameters:
      - product: Trading pair (in Gemini's format, e.g., "btcusd" for BTC/USD).
      - side: "buy" or "sell".
      - quantity: The order quantity as a string (e.g., "0.001").
      - price: The limit price as a string (e.g., "20000").
    
    Returns a dictionary with the response from Gemini.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/order/new"
    nonce = str(int(time.time() * 1000))
    
    # Retrieve account info to get a valid account name; defaulting to "primary"
    account_info = get_gemini_account_info()
    valid_account = account_info[0].get("account", "primary")
    
    # Build the order payload and include the immediate-or-cancel behavior
    payload = {
        "request": "/v1/order/new",
        "nonce": nonce,
        "symbol": product.lower(),
        "amount": quantity,
        "price": price,
        "side": side.lower(),
        "type": "exchange limit",
        "behavior": "immediate-or-cancel",  # This ensures no residual open orders
        "account": [valid_account]          # Provided as an array
    }
    
    headers = gemini_auth_headers("/v1/order/new", payload, api_key, api_secret)
    response = requests.post(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        print("Error creating order, status code:", response.status_code)
        print("Response text:", response.text)
        raise e
    return response.json()


def cancel_gemini_order(order_id: str) -> dict:
    """
    Cancel an order on Gemini Sandbox via POST /v1/order/cancel.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/order/cancel"
    nonce = str(int(time.time() * 1000))
    payload = {
        "request": "/v1/order/cancel",
        "nonce": nonce,
        "order_id": order_id
    }
    headers = gemini_auth_headers("/v1/order/cancel", payload, api_key, api_secret)
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()

def main():
    # Retrieve account info
    try:
        print("Retrieving Gemini Sandbox Account Balances...")
        account_info = get_gemini_account_info()
        print("Account Info:")
        print(json.dumps(account_info, indent=2))
    except Exception as e:
        print("Error retrieving account info:", str(e))
    
    # Create a test buy order
    try:
        print("Creating a test buy order on Gemini Sandbox...")
        order_response = create_gemini_order(product="btcusd", side="buy", quantity="0.001", price="20000")
        print("Order Creation Response:")
        print(json.dumps(order_response, indent=2))
    except Exception as e:
        print("Error creating order:", str(e))
    
    # Optionally, test cancellation (if a valid order_id is obtained)
    """
    if isinstance(order_response, dict) and "order_id" in order_response:
        try:
            print("Cancelling order with order_id:", order_response["order_id"])
            cancel_response = cancel_gemini_order(order_response["order_id"])
            print("Order Cancellation Response:")
            print(json.dumps(cancel_response, indent=2))
        except Exception as e:
            print("Error cancelling order:", str(e))
    """

if __name__ == "__main__":
    main()
