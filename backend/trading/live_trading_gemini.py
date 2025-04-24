import os
import json
import time
import base64
import hmac
import hashlib
import requests
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(os.path.join(BASE_DIR, '.env'))


def gemini_auth_headers(request_path: str, payload: dict, api_key: str, api_secret: str) -> dict:
    """
    Create Gemini authentication headers by signing the base64-encoded JSON payload.
    """
    # Compact JSON
    payload_json = json.dumps(payload, separators=(',', ':'))
    encoded_payload = base64.b64encode(payload_json.encode())
    signature = hmac.new(api_secret.encode(), encoded_payload, hashlib.sha384).hexdigest()
    return {
        'Content-Type': 'text/plain',
        'Cache-Control': 'no-cache',
        'X-GEMINI-APIKEY': api_key,
        'X-GEMINI-PAYLOAD': encoded_payload.decode(),
        'X-GEMINI-SIGNATURE': signature
    }


def get_gemini_account_info() -> list:
    """
    Retrieve account balances from Gemini Sandbox; fallback to dummy if endpoint returns 404.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/balances"
    nonce = str(int(time.time() * 1000))
    payload = {"request": "/v1/balances", "nonce": nonce}
    headers = gemini_auth_headers("/v1/balances", payload, api_key, api_secret)

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError:
        if response.status_code == 404:
            print("Warning: /v1/balances returned 404. Using dummy account info.")
            return [{"currency": "USD", "available": "100000", "hold": "0", "balance": "100000", "account": "primary"}]
        raise

def get_current_price(product: str) -> str:
    """
    Fetch the current ask price for the given symbol from Gemini public ticker.
    """
    url  = f"https://api.sandbox.gemini.com/v1/pubticker/{product.lower()}"
    resp = requests.get(url)
    resp.raise_for_status()
    data = resp.json()
    # use the ask price so our buy will hit the book
    ask = data.get("ask")
    return str(ask)

def create_gemini_order(product: str, side: str, quantity: str, price: str = None) -> dict:
    """
    Place a fill-or-kill limit order on Gemini Sandbox.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/order/new"
    nonce = str(int(time.time() * 1000))

    # Determine account for order
    account_info = get_gemini_account_info()
    valid_account = account_info[0].get("account", "primary")

    # Construct the payload with Fill-Or-Kill option
    payload = {
        "request": "/v1/order/new",
        "nonce":   nonce,
        "symbol":  product.lower(),
        "amount":  quantity,
        "side":    side.lower(),
        "type":    "exchange market",   # ← CHANGED to market
        "account": valid_account
    }

    headers  = gemini_auth_headers("/v1/order/new", payload, api_key, api_secret)
    response = requests.post(url, headers=headers)
    try:
        response.raise_for_status()
    except requests.HTTPError:
        print("Error creating order, status code:", response.status_code)
        print("Response text:", response.text)
        raise
    return response.json()


def cancel_gemini_order(order_id: str) -> dict:
    """
    Cancel an existing order on Gemini Sandbox.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    api_secret = os.getenv("GEMINI_API_SECRET")
    if not api_key or not api_secret:
        raise Exception("Gemini API key or secret not set in environment.")

    url = "https://api.sandbox.gemini.com/v1/order/cancel"
    nonce = str(int(time.time() * 1000))
    payload = {"request": "/v1/order/cancel", "nonce": nonce, "order_id": order_id}
    headers = gemini_auth_headers("/v1/order/cancel", payload, api_key, api_secret)
    response = requests.post(url, headers=headers)
    response.raise_for_status()
    return response.json()


def main():
    # Retrieve and display account balances
    try:
        print("Retrieving Gemini Sandbox Account Balances...")
        account_info = get_gemini_account_info()
        print(json.dumps(account_info, indent=2))
    except Exception as e:
        print("Error retrieving account info:", str(e))

    # Place a fill-or-kill buy order example
    try:
        print("Placing Fill-Or-Kill limit buy order on Gemini Sandbox...")

        product = "btcusd"
        price   = get_current_price(product)
        print(f"Current ask for {product.upper()}: ${price}")
        
        order_response = create_gemini_order(
            product="btcusd", side="buy", quantity="0.001", price=price
        )
        print("Order Creation Response:")
        print(json.dumps(order_response, indent=2))
    except Exception as e:
        print("Error creating order:", str(e))

    # Optional: Cancel the test order
    # if "order_id" in order_response:
    #     cancel_response = cancel_gemini_order(order_response["order_id"])
    #     print("Cancellation Response:", cancel_response)

if __name__ == "__main__":
    main()
