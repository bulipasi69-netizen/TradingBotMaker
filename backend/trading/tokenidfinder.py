import requests
import os
from pathlib import Path
from dotenv import load_dotenv


BACKEND_DIR = Path(__file__).resolve().parents[1]     
dotenv_path = BACKEND_DIR / ".env"                     
load_dotenv(dotenv_path=dotenv_path, override=True)
API_KEY = os.environ["TOKEN_METRICS_API_KEY"] 
url     = 'https://api.tokenmetrics.com/v2/tokens'
headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'api_key': API_KEY
}

resp   = requests.get(url, headers=headers)
resp.raise_for_status()
tokens = resp.json().get('data', [])

# get all entries whose symbol is exactly 'ETH'
eth_tokens = [t for t in tokens if t.get('TOKEN_SYMBOL') == 'ETH']

# display them
for t in eth_tokens:
    print(f"ID: {t['TOKEN_ID']}, Name: {t['TOKEN_NAME']}, Symbol: {t['TOKEN_SYMBOL']}")
