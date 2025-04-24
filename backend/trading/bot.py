import time
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

import ccxt
from pprint import pprint

# ─── tm_investor logic (unchanged) ────────────────────────────────────────────────
def fetch_past_hour_signals(api_key: str, symbol: str = None, token_id: int = None) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    start_iso = one_hour_ago.isoformat().replace('+00:00', 'Z')
    end_iso   = now.isoformat().replace('+00:00', 'Z')

    url = 'https://api.tokenmetrics.com/v2/trading-signals'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'api_key': api_key
    }
    params = {'start_date': start_iso, 'end_date': end_iso}
    if symbol:   params['symbol']   = symbol.replace('-', '')
    if token_id: params['token_id'] = token_id

    resp = requests.get(url, headers=headers, params=params)
    resp.raise_for_status()
    data = resp.json().get('data', [])
    df   = pd.json_normalize(data)
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'])

    if token_id is not None and 'TOKEN_ID' in df.columns:
        df = df[df['TOKEN_ID'] == token_id]
    elif symbol and 'SYMBOL' in df.columns:
        df = df[df['SYMBOL'] == symbol.replace('-', '')]

    return df

def fetch_current_signal(api_key: str, symbol: str = None, token_id: int = None) -> pd.Series:
    df = fetch_past_hour_signals(api_key, symbol, token_id)
    if df.empty:
        raise ValueError("No signals in the past hour.")
    return df.sort_values('DATE').iloc[-1]


# ─── Trading + Budget logic ──────────────────────────────────────────────────────

# SETTINGS & STATE
TM_API_KEY       = 'hack-b3f7d3e9-421d-47a3-b4e0-44dca99c0f0d'
TOKEN_ID         = 3375         # Bitcoin
BUY_THRESHOLD    = 80
SELL_THRESHOLD   = 50
ORDER_VALUE      = 100          # max USDT to spend per buy signal
INITIAL_BUDGET   = 1000         # your starting budget in USDT

budget = INITIAL_BUDGET         # mutable state

# initialize sandbox exchange
exchange = ccxt.binanceus({
    'apiKey':    "V4m8XeEUDdg5EQXBV3Ojfx3RSBWEu0GRq8LaInAIpKWncvcGc8r123K085gqMVQf",
    'secret':    "cx2bJAZiSVZmrWLPEwSZGTzyn5Hcq5n7a2uJVJNi4Gnm3VhU3RTbaFFwneBLDEq9",
    'enableRateLimit': True,
})
exchange.set_sandbox_mode(True)

SYMBOL = 'BTC/USDT'

def get_usdt_balance():
    return exchange.fetch_balance()['total'].get('USDT', 0)

def get_asset_balance(symbol):
    asset = symbol.split('/')[0]
    return exchange.fetch_balance()['total'].get(asset, 0)

def place_buy(symbol, usdt_amount):
    """
    Returns the actual USDT spent (order['cost']).
    """
    ticker = exchange.fetch_ticker(symbol)
    price  = ticker['last']
    amount = usdt_amount / price
    order  = exchange.create_market_order(symbol, 'buy', amount)
    cost   = order.get('cost', amount * price)
    pprint(order)
    return cost

def place_sell(symbol, amount):
    """
    Returns the USDT received (order['cost']).
    """
    order    = exchange.create_market_order(symbol, 'sell', amount)
    proceeds = order.get('cost', 0)
    pprint(order)
    return proceeds

def main_loop(poll_interval_sec=30):
    global budget

    while True:
        try:
            sig   = fetch_current_signal(TM_API_KEY, token_id=TOKEN_ID)
            grade = float(sig['TM_TRADER_GRADE'])
            print(f"[{sig['DATE']}] Grade = {grade} | Budget = {budget:.2f} USDT")

            # 1) BUY
            if grade >= BUY_THRESHOLD:
                usdt_bal = get_usdt_balance()
                # cap spend by both your balance and remaining budget
                to_spend = min(ORDER_VALUE, usdt_bal, budget)
                if to_spend > 0:
                    print(f"→ Buying up to {to_spend:.2f} USDT of {SYMBOL}")
                    actual_spent = place_buy(SYMBOL, to_spend)
                    budget -= actual_spent
                    print(f"   Spent {actual_spent:.2f} USDT, new budget = {budget:.2f}")
                else:
                    print("→ No budget or balance to buy.")

            # 2) SELL
            elif grade <= SELL_THRESHOLD:
                asset_bal = get_asset_balance(SYMBOL)
                if asset_bal > 0:
                    print(f"→ Selling {asset_bal:.6f} {SYMBOL.split('/')[0]}")
                    gained = place_sell(SYMBOL, asset_bal)
                    budget += gained
                    print(f"   Gained {gained:.2f} USDT, new budget = {budget:.2f}")
                else:
                    print("→ No asset holdings to sell.")

            else:
                print(f"→ Grade between thresholds ({SELL_THRESHOLD}–{BUY_THRESHOLD}), holding.")

        except Exception as e:
            print("Error:", e)

        time.sleep(poll_interval_sec)

if __name__ == '__main__':
    main_loop()
