# trading_bot_with_plot.py  ––– now with balance & trade log ---
import requests, ccxt, pandas as pd, plotly.graph_objects as go
from datetime import datetime, timedelta, timezone
from dash import Dash, dcc, html, callback_context
from dash.dependencies import Input, Output
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]     
dotenv_path = BACKEND_DIR / ".env"                     
load_dotenv(dotenv_path=dotenv_path, override=True)
API_KEY = os.environ["TOKEN_METRICS_API_KEY"] 
BINANCEUS_API_KEY = os.environ["BINANCEUS_API_KEY"]
BINANCEUS_API_SECRET = os.environ["BINANCEUS_API_SECRET"]
# ─── Token Metrics & Trading constants ─────────────────────────────────────────
TM_API_KEY       = API_KEY
TOKEN_ID         = 3375          # Bitcoin
BUY_THRESHOLD    = 80
SELL_THRESHOLD   = 50
ORDER_VALUE      = 100           # USDT per buy
INITIAL_BUDGET   = 1000          # “dry-powder” budget you allow the bot to spend
PRICE_INTERVAL   = 10            # seconds – price line refresh
TRADE_INTERVAL   = 30            # seconds – check TM grade & maybe trade
budget           = INITIAL_BUDGET

# ─── Exchange setup (Binance US sandbox) ───────────────────────────────────────
exchange = ccxt.binanceus({
    'apiKey': BINANCEUS_API_KEY,
    'secret': BINANCEUS_API_SECRET,
    'enableRateLimit': True,
})
exchange.set_sandbox_mode(True)
SYMBOL = 'BTC/USDT'                                 # quote/ base   (ccxt style)

# ─── Helpers ───────────────────────────────────────────────────────────────────
def fetch_past_hour_signals(api_key: str, token_id: int) -> pd.DataFrame:
    now = datetime.now(timezone.utc)
    params = {
        'start_date': (now - timedelta(hours=1)).isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'end_date'  :  now.isoformat(timespec='seconds').replace('+00:00', 'Z'),
        'token_id'  : token_id
    }
    r = requests.get(
        'https://api.tokenmetrics.com/v2/trading-signals',
        headers={'Accept':'application/json','Content-Type':'application/json','api_key':api_key},
        params=params
    )
    r.raise_for_status()
    df = pd.json_normalize(r.json().get('data', []))
    if 'DATE' in df: df['DATE'] = pd.to_datetime(df['DATE'])
    return df

def fetch_current_signal(api_key: str, token_id: int):
    df = fetch_past_hour_signals(api_key, token_id)
    return df.sort_values('DATE').iloc[-1] if not df.empty else None

def usdt_balance():   return exchange.fetch_balance()['total'].get('USDT', 0)
def btc_balance():    return exchange.fetch_balance()['total'].get('BTC' , 0)

# Return order amount actually executed (ccxt “filled”) for clarity
def place_buy(symbol: str, usdt_amount: float):
    price  = exchange.fetch_ticker(symbol)['last']
    amount = usdt_amount / price
    order  = exchange.create_market_order(symbol, 'buy', amount)
    return order['filled'], price, order['cost']         # BTC purchased, price, USDT spent

def place_sell(symbol: str, amount: float):
    price  = exchange.fetch_ticker(symbol)['last']
    order  = exchange.create_market_order(symbol, 'sell', amount)
    return order['filled'], price, order['cost']         # BTC sold, price, USDT received

# ─── Live data storage for plot + trade log ────────────────────────────────────
price_times, price_values = [], []
buy_times,   buy_prices   = [], []
sell_times,  sell_prices  = [], []
trade_log = []                    # plain-text history for the UI

# ─── Dash UI ───────────────────────────────────────────────────────────────────
app = Dash(__name__)
CORS(app.server, resources={r"/*": {"origins": "http://localhost:3000"}})

app.layout = html.Div([
    html.H3("BTC Live Trading Bot w/ Token Metrics Grade"),
    html.Div(id='balance-info', style={'marginBottom': '10px', 'fontWeight': '600'}),
    dcc.Graph(id='live-graph'),
    html.H4("Trade log"),
    html.Div(id='trade-log', style={'maxHeight': '250px','overflowY': 'auto',
                                    'border': '1px solid #444','padding': '6px',
                                    'fontFamily':'monospace','fontSize':'0.85rem'}),
    dcc.Interval(id='price-interval', interval=PRICE_INTERVAL*1000, n_intervals=0),
    dcc.Interval(id='trade-interval', interval=TRADE_INTERVAL*1000, n_intervals=0)
])

# ─── Callback: update graph, balance bar, and trade log ------------------------
@app.callback(
    Output('live-graph',   'figure'),
    Output('balance-info', 'children'),
    Output('trade-log',    'children'),
    [Input('price-interval', 'n_intervals'),
     Input('trade-interval', 'n_intervals')]
)
def refresh(price_tick, trade_tick):
    global budget
    trigger = callback_context.triggered[0]['prop_id'].split('.')[0]
    now     = datetime.now()

    # 1) Always refresh price line if price interval fired
    if trigger == 'price-interval':
        price = exchange.fetch_ticker(SYMBOL)['last']
        price_times.append(now); price_values.append(price)

    # 2) Every TRADE_INTERVAL: check TM grade and maybe trade
    if trigger == 'trade-interval':
        sig = fetch_current_signal(TM_API_KEY, TOKEN_ID)
        if sig is not None:
            grade = float(sig['TM_TRADER_GRADE'])
            price = exchange.fetch_ticker(SYMBOL)['last']

            # BUY logic --------------------------------------------------------
            if grade >= BUY_THRESHOLD:
                to_spend = min(ORDER_VALUE, usdt_balance(), budget)
                if to_spend > 0:
                    filled, exec_price, cost = place_buy(SYMBOL, to_spend)
                    budget   -= cost
                    buy_times.append(now); buy_prices.append(exec_price)
                    trade_log.append(
                        f"{now:%H:%M:%S}  BUY  {filled:.6f} BTC @ {exec_price:.2f}  "
                        f"USDT-spent: {cost:.2f}"
                    )

            # SELL logic -------------------------------------------------------
            elif grade <= SELL_THRESHOLD:
                amt = btc_balance()
                if amt > 0:
                    filled, exec_price, proceeds = place_sell(SYMBOL, amt)
                    budget += proceeds
                    sell_times.append(now); sell_prices.append(exec_price)
                    trade_log.append(
                        f"{now:%H:%M:%S}  SELL {filled:.6f} BTC @ {exec_price:.2f}  "
                        f"USDT-recv: {proceeds:.2f}"
                    )

        # keep only most recent 50 log lines
        trade_log[:] = trade_log[-50:]

    # 3) Build figure
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=price_times, y=price_values,
                             mode='lines', name='Price', line={'color':'#000'}))
    fig.add_trace(go.Scatter(x=buy_times, y=buy_prices,
                             mode='markers', name='Buys',
                             marker={'color':'green','size':10}))
    fig.add_trace(go.Scatter(x=sell_times, y=sell_prices,
                             mode='markers', name='Sells',
                             marker={'color':'red','size':10}))
    fig.update_layout(margin=dict(l=45,r=15,t=35,b=25),
                      xaxis_title='Time', yaxis_title='Price (USDT)',
                      legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1))

    # 4) Compose balance string + trade-log HTML
    bal_text = (f"USDT: {usdt_balance():,.2f} | "
                f"BTC: {btc_balance():.6f} | "
                f'Remaining budget: {budget:,.2f} USDT')
    log_children = [html.Div(line) for line in reversed(trade_log)]  # newest on top

    return fig, bal_text, log_children

# ─── Main ──────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True)
