# backend/trading/bot.py

import pandas as pd
from trading.quant_analysis import calculate_EMAs, calculate_portfolio_returns
from trading.backtesting import simple_backtest
from trading.live_trading import connect_to_coinbase_pro_testnet, create_order

def run_trading_bot():
    # Step 1: Collect historical data; here we assume the CSV from previous data collection exists.
    data = pd.read_csv('data/TMdata.csv', parse_dates=['DATE'])
    data.fillna(method='ffill', inplace=True)
    
    # Calculate daily return (if not already present)
    if 'DailyReturnPCT' not in data.columns:
        data['DailyReturnPCT'] = data['Close'] / data['Open'] - 1
    
    # Step 2: Perform quantitative analysis by calculating EMAs and the trading signal.
    data = calculate_EMAs(data, grade_col='TM_TRADER_GRADE')
    data = calculate_portfolio_returns(data)
    
    # Optionally, run a backtest and display estimated returns.
    ann_return = simple_backtest(data)
    print("Estimated Annual Return from Backtesting: {:.2%}".format(ann_return))
    
    # Step 3: Live Trading Simulation on Coinbase Pro Testnet
    latest_signal = data.iloc[-1]['Signal']
    auth_client = connect_to_coinbase_pro_testnet()
    product_id = "BTC-USD"
    
    # For demonstration, use static price levels.
    if latest_signal:
        print("Buy signal detected. Creating buy order on Testnet...")
        order = create_order(auth_client, product_id=product_id, side="buy", size="0.001", price="10000")
    else:
        print("Sell signal detected. Creating sell order on Testnet...")
        order = create_order(auth_client, product_id=product_id, side="sell", size="0.001", price="11000")
    
    print("Order Executed:", order)

if __name__ == "__main__":
    run_trading_bot()
