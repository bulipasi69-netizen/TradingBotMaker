import ccxt
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

# thresholds
BUY_THRESHOLD  = 80.0
SELL_THRESHOLD = 50.0

# CCXT setup (BinanceUS sandbox)
exchange = ccxt.binanceus({'enableRateLimit': True})
exchange.set_sandbox_mode(True)
SYMBOL = 'BTC/USDT'

TM_API_URL = 'https://api.tokenmetrics.com/v2/trading-signals'
TM_API_KEY = ''  # pull from env in view

def fetch_signals(token_id: int) -> pd.DataFrame:
    now    = datetime.now(timezone.utc)
    since  = now - timedelta(days=1)
    params = {
        'start_date': since.isoformat().replace('+00:00','Z'),
        'end_date':   now.isoformat().replace('+00:00','Z'),
        'token_id':   token_id
    }
    headers = {
        'Accept':'application/json',
        'Content-Type':'application/json',
        'api_key': TM_API_KEY
    }
    r = requests.get(TM_API_URL, headers=headers, params=params)
    r.raise_for_status()
    df = pd.json_normalize(r.json().get('data', []))
    if 'DATE' in df:
        df['DATE'] = pd.to_datetime(df['DATE'])
    return df

def fetch_prices() -> pd.DataFrame:
    """Fetch hourly OHLCV for last 24h."""
    now   = exchange.milliseconds()
    since = now - 24*3600*1000
    ohlcv = exchange.fetch_ohlcv(SYMBOL, '1h', since=since)
    df    = pd.DataFrame(ohlcv, columns=['ts','open','high','low','close','vol'])
    df['DATE'] = pd.to_datetime(df['ts'], unit='ms')
    return df

def get_bot_plot_data(token_id: int, tm_key: str):
    global TM_API_KEY
    TM_API_KEY = tm_key

    price_df = fetch_prices()
    sig_df   = fetch_signals(token_id)

    # align: for each price bar, find last signal before that bar
    buys, sells = [], []
    for _, row in price_df.iterrows():
        t = row.DATE
        # grab the signal at or before t
        past = sig_df[sig_df.DATE <= t]
        if past.empty: continue
        latest = past.sort_values('DATE').iloc[-1]
        grade  = float(latest['TM_TRADER_GRADE'])
        if grade >= BUY_THRESHOLD:
            buys.append({'time': t,       'price': row.close})
        elif grade <= SELL_THRESHOLD:
            sells.append({'time': t,      'price': row.close})

    return {
        'times':  price_df.DATE.dt.isoformat().tolist(),
        'prices': price_df.close.tolist(),
        'buys':   buys,
        'sells':  sells,
    }
