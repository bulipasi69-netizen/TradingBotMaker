import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import os
from pathlib import Path
from dotenv import load_dotenv


def fetch_past_hour_signals(api_key: str, symbol: str = None, token_id: int = None) -> pd.DataFrame:
    """
    Fetches Token Metrics trading signals over the past hour using UTC-aware timestamps.

    Parameters:
    - api_key: Your Token Metrics API key (e.g., "tm-xxx").
    - symbol: Optional ticker symbol filter (e.g., "BTC").
      NOTE: some alternative assets share symbols (e.g. Osmosis allBTC), so filtering by TOKEN_ID is more precise.
    - token_id: Optional Token Metrics numeric ID filter.

    Returns:
    - A pandas DataFrame with the signals data filtered to your asset.
    """
    # Define time window: past hour (UTC aware)
    now = datetime.now(timezone.utc)
    one_hour_ago = now - timedelta(hours=1)
    start_iso = one_hour_ago.isoformat().replace('+00:00', 'Z')
    end_iso = now.isoformat().replace('+00:00', 'Z')

    url = 'https://api.tokenmetrics.com/v2/trading-signals'
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json',
        'api_key': api_key
    }
    params = {'start_date': start_iso, 'end_date': end_iso}
    if symbol:
        params['symbol'] = symbol.replace('-', '')
    if token_id:
        params['token_id'] = token_id

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    payload = response.json().get('data', [])

    # Normalize to DataFrame
    df = pd.json_normalize(payload)
    if 'DATE' in df.columns:
        df['DATE'] = pd.to_datetime(df['DATE'])

    # Further filter by TOKEN_ID or SYMBOL if provided
    if token_id is not None and 'TOKEN_ID' in df.columns:
        df = df[df['TOKEN_ID'] == token_id]
    elif symbol and 'SYMBOL' in df.columns:
        df = df[df['SYMBOL'] == symbol.replace('-', '')]

    return df


def fetch_current_signal(api_key: str, symbol: str = None, token_id: int = None) -> pd.Series:
    """
    Fetches the single most recent Token Metrics signal from the past hour for a given asset.

    Returns:
    - A pandas Series representing that latest signal.
    """
    df = fetch_past_hour_signals(api_key, symbol, token_id)
    if df.empty:
        raise ValueError("No signals returned in the past hour for the specified asset.")
    # Sort by timestamp and take the last entry
    latest = df.sort_values('DATE').iloc[-1]
    return latest


if __name__ == '__main__':
    BACKEND_DIR = Path(__file__).resolve().parents[1]     
    dotenv_path = BACKEND_DIR / ".env"                     
    load_dotenv(dotenv_path=dotenv_path, override=True)
    API_KEY = os.environ["TOKEN_METRICS_API_KEY"] 
    # Example: get the current Bitcoin signal by TOKEN_ID
    current = fetch_current_signal(API_KEY, token_id=3375)
    print("As of", current['DATE'], \
          f"Symbol: {current.get('SYMBOL','N/A')}", \
          f"Trader Grade: {current.get('TM_INVESTOR_GRADE','N/A')}", \
          f"Signal: {current.get('CURRENT_SIGNAL','N/A')}")
