# backend/trading/live_trading.py

import os
import cbpro  # Coinbase Pro Python client

def connect_to_coinbase_pro_testnet():
    """
    Connect to Coinbase Pro Testnet using cbpro.
    Loads API keys from the environment.
    """
    api_key = os.getenv("COINBASE_PRO_API_KEY")
    secret = os.getenv("COINBASE_PRO_API_SECRET")
    passphrase = os.getenv("COINBASE_PRO_PASSPHRASE")
    api_url = "https://api-public.sandbox.pro.coinbase.com"
    auth_client = cbpro.AuthenticatedClient(api_key, secret, passphrase, api_url)
    return auth_client

def get_account_balance(auth_client):
    """Get accounts balance from Coinbase Pro Testnet."""
    return auth_client.get_accounts()

def create_order(auth_client, product_id: str, side: str, size: str, price: str):
    """
    Create a limit order on Coinbase Pro Testnet.
    """
    order = auth_client.place_limit_order(
        product_id=product_id,
        side=side,
        price=price,
        size=size
    )
    return order

if __name__ == "__main__":
    auth_client = connect_to_coinbase_pro_testnet()
    balance = get_account_balance(auth_client)
    print("Account Balance:")
    for account in balance:
        print(account)
    
    # Test order creation:
    order = create_order(auth_client, product_id="BTC-USD", side="buy", size="0.001", price="10000")
    print("Order Created:", order)
