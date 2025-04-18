# Trading Bot Project

This repository contains a complete trading bot system for cryptocurrency markets. The system performs data collection, quantitative analysis, backtesting, and live trading on Coinbase Pro's sandbox (testnet). It uses a Django backend for the trading logic and a React frontend for the user interface.

> **Note:** This project is configured for testnet/sandbox use only. Do not use real funds.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Project Structure](#project-structure)
- [Setup Instructions](#setup-instructions)
  - [Backend Setup](#backend-setup)
  - [Frontend Setup](#frontend-setup)



---

## Project Overview

This project implements:
- **Data Collection:** Retrieves market data from Coinbase Pro Testnet and token metrics from the Token Metrics API.
- **Quantitative Analysis:** Computes exponential moving averages (EMA) on signals (TM_TRADER_GRADE) to generate buy/sell signals.
- **Backtesting:** Runs a simple backtest to estimate portfolio returns.
- **Live Trading (Testnet):** Connects to Coinbase Pro sandbox to execute test orders based on generated signals.

Sensitive API keys and credentials are stored securely in a `.env` file.

---

## Project Structure
TradingBotMaker/
├── backend/
│   ├── manage.py
│   ├── .env.example         # Sample environment variable file (copy to .env)
│   ├── requirements.txt     # Python dependencies for the backend
│   ├── botmaker_backend/    # Django project (settings, urls, wsgi)
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── api/                 # Django app for API endpoints (Coinbase OAuth etc.)
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── serializers.py
│   │   └── views.py
│   └── trading/             # Trading bot modules
│       ├── __init__.py
│       ├── data_collection.py
│       ├── quant_analysis.py
│       ├── backtesting.py
│       ├── live_trading.py
│       └── bot.py         # Main orchestration module for trading
└── frontend/                # React frontend (UI)
    ├── package.json
    ├── public/
    │   └── index.html
    └── src/
        ├── index.js
        ├── App.js
        └── components/
            ├── Dashboard.js
            ├── Bots.js
            ├── NewBot.js
            └── ConnectCoinbase.js


Below is a complete, single-file copy‑and‑paste version of the setup instructions in Markdown. You can save all the text into a file (for example, `SETUP.md`) and share it with your friend.

```markdown
# Setup Instructions

## Backend Setup

1. **Clone the Repository:**
   ```bash
   git clone <your_repository_url>
   cd TradingBotMaker/backend
   ```

2. **Create and Activate a Virtual Environment:**

   **On macOS/Linux:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

   **On Windows:**
   ```bash
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup Environment Variables:**
   - Copy the sample `.env.example` file to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Open the newly created `.env` file and update it with your credentials. 
  

5. **Run the Django Server:**
   ```bash
   python manage.py runserver 0.0.0.0:8000
   ```

## Frontend Setup

1. **Navigate to the Frontend Folder:**
   ```bash
   cd ../frontend
   ```

2. **Install Node.js Dependencies:**
   ```bash
   npm install
   ```

3. **Start the React App:**
   ```bash
   npm start
   ```
   Your app should now run at [http://localhost:3000](http://localhost:3000).

---

4. **TODO**
   - Fix xscrapper (currently getting unauthenticated error, before the error was the crawlers was able to get data but not build data set because it would never complete)
   - Check if token metrics api is working again
   - finish crypto_sentiment
   - once all parts are working, implement it all together in bot.py
   - once bot.py is working, implement so that you can make multiple bots 
   - store the bots in the background
   - make dashboard see performance of the bots
   
