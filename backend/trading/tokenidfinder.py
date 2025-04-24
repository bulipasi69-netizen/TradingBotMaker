import requests

API_KEY = 'hack-b3f7d3e9-421d-47a3-b4e0-44dca99c0f0d'
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
