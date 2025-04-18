#!/usr/bin/env python3
"""
analyze_crypto_sentiment.py

Reads a CSV of crypto-news posts and uses Macrocosmos Apex to
annotate each item with:
  - coin:      which cryptocurrency is affected
  - sentiment: "good" or "bad"
  - score:     integer in [-10, 10]
  - reasoning: (optional) brief justification

Usage:
    export MACROCOSMOS_API_KEY="your-api-key"
    pip install macrocosmos python-dotenv pandas
    python analyze_crypto_sentiment.py input.csv output.csv
"""

import os
import json
import sys
import pandas as pd
from dotenv import load_dotenv
import macrocosmos as mc
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent  
load_dotenv(os.path.join(BASE_DIR, '.env'))
API_KEY = os.getenv("MACROCOSMOS_API_KEY")


# initialize Apex client :contentReference[oaicite:0]{index=0}
client = mc.ApexClient(api_key=API_KEY)

def analyze_news(input_csv: str, output_csv: str):
    df = pd.read_csv(input_csv)
    results = []

    for _, row in df.iterrows():
        # build the chat prompt
        system_msg = {
            "role": "system",
            "content": (
                "You are a sentiment-analysis assistant specialized in cryptocurrency news. "
                "For the given news item, identify the cryptocurrency mentioned, determine "
                "if the news is good or bad for that cryptocurrency, and assign an integer score "
                "from -10 (most negative) to +10 (most positive). "
                "Respond strictly in JSON with keys: coin, sentiment, score, reasoning."
            )
        }
        user_msg = {
            "role": "user",
            "content": row["content"]
        }

        # call the Apex chat/completions endpoint
        resp = client.chat.completions.create(
            messages=[system_msg, user_msg],
            json_format=True,
            sampling_parameters={          # ← move your length setting here
                "max_new_tokens": 128
            },
        )              


        # parse the returned JSON
        raw = resp.choices[0].message.content
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            # fallback if the model didn't obey format
            data = {
                "coin": None,
                "sentiment": None,
                "score": None,
                "reasoning": raw
            }

        # collect merged row
        results.append({
            **row.to_dict(),
            "coin":      data.get("coin"),
            "sentiment": data.get("sentiment"),
            "score":     data.get("score"),
            "reasoning": data.get("reasoning")
        })

    # write out
    out_df = pd.DataFrame(results)
    out_df.to_csv(output_csv, index=False)
    print(f"✅ Analysis complete: {output_csv}")

if __name__ == "__main__":
    
    analyze_news('trading/data/sentiment_input.csv', 'trading/data/sentiment_output.csv')
