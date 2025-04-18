# backend/trading/backtesting.py

import pandas as pd

def simple_backtest(data: pd.DataFrame) -> float:
    """
    Computes the average daily portfolio return and estimates the annual compound return.
    """
    avg_daily_return = data['PortfolioReturnPCT'].mean()
    annual_return = (1 + avg_daily_return) ** 365 - 1
    return annual_return

if __name__ == "__main__":
    data = pd.read_csv('trading/data/TMdata.csv', parse_dates=['DATE'])
    data.fillna(method='ffill', inplace=True)
    data['DailyReturnPCT'] = data['Close'] / data['Open'] - 1
    from quant_analysis import calculate_EMAs, calculate_portfolio_returns
    data = calculate_EMAs(data, grade_col='TM_TRADER_GRADE')
    data = calculate_portfolio_returns(data)
    ann_return = simple_backtest(data)
    print("Estimated Annual Return:", ann_return)
