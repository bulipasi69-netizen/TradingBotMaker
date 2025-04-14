# backend/trading/quant_analysis.py

import pandas as pd

def calculate_daily_return(data: pd.DataFrame) -> pd.DataFrame:
    # Compute DailyReturnPCT as (Close / Open - 1) if it does not exist
    if 'DailyReturnPCT' not in data.columns:
        data['DailyReturnPCT'] = data['Close'] / data['Open'] - 1
    return data

def calculate_EMAs(data: pd.DataFrame, grade_col: str = 'TM_TRADER_GRADE') -> pd.DataFrame:
    """
    Calculate fast (EMA_3) and slow (EMA_7) exponential moving averages.
    """
    data['EMA_fast'] = data[grade_col].ewm(span=3, adjust=False).mean()
    data['EMA_slow'] = data[grade_col].ewm(span=7, adjust=False).mean()
    data['Signal'] = data['EMA_fast'] >= data['EMA_slow']  # True indicates a buy signal
    return data

def calculate_portfolio_returns(data: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate portfolio returns based on the computed DailyReturnPCT and Signal.
    """
    data['PortfolioReturnPCT'] = data.apply(
        lambda row: row['DailyReturnPCT'] if row['Signal'] else -row['DailyReturnPCT'], axis=1)
    return data

if __name__ == "__main__":
    # Update the path if necessary.
    data = pd.read_csv('data/TMdata.csv', parse_dates=['DATE'])
    data = calculate_daily_return(data)
    data = calculate_EMAs(data, grade_col='TM_TRADER_GRADE')
    data = calculate_portfolio_returns(data)
    print(data[['DATE', 'EMA_fast', 'EMA_slow', 'Signal', 'PortfolioReturnPCT']].head())
