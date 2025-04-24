# Trading Bot Maker

Trading Bot Maker is a modular, customizable platform for algorithmic cryptocurrency trading. Designed for both experimentation and educational purposes, it enables users to build, deploy, and monitor trading bots on Coinbase Pro’s sandbox testnet while leveraging market insights from the Token Metrics API.

---

## 🚀 Key Features

- **Custom Bot Configuration**  
  Create multiple trading bots with adjustable parameters:
  - **Buy/Sell Thresholds**: Define the Token Metrics trader-grade levels that trigger orders.
  - **Budget Management**: Allocate a budget per bot; trades deduct from and credit back to the remaining budget.
  - **Polling & Chart Intervals**: Set how frequently the system fetches grades, updates charts, and evaluates trade signals.

- **Real‑Time Monitoring**  
  - **Dashboard**: Live price charts annotated with buy/sell markers and an execution log.
  - **Bots History**: Review past bot runs, performance metrics, and trade details.

- **Future‑Ready Architecture**  
  - **Modular Design**: Separate backend, trading logic, and frontend components make it easy to extend functionality.
  - **API‑Driven**: Swap or add new data sources (e.g., sentiment analysis, investor grades) without overhauling core code.

---

## 🔧 Setup & Installation

**1. Backend**  
```bash
cd TradingBotMaker/backend
python3 -m venv venv         # (macOS/Linux) or python -m venv venv (Windows)
source venv/bin/activate     # or venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env         # then edit .env with your API keys
python manage.py runserver 0.0.0.0:8000
```

**2. Frontend**  
```bash
cd ../frontend
npm install
npm start                   # Launches React app at http://localhost:3000
```

> **Note:** This project is configured for sandbox use only. Do not use real funds.

---

## 🛠️ API Usage

### Token Metrics API
- **Endpoint**: `/v2/trader-grades`  
- **Purpose**: Retrieves the latest `TM_TRADER_GRADE` for a given token (e.g., Bitcoin)  
- **Integration**: `data_collection.py` fetches grades, then `quant_analysis.py` computes EMAs and trade signals.

### Coinbase Pro Sandbox
- **Endpoints**: `/accounts`, `/orders`  
- **Purpose**: Executes test buy/sell orders based on generated signals  
- **Integration**: `live_trading.py` manages order placement, budget updates, and error handling.

All sensitive credentials (API keys, secrets) are loaded from the backend’s `.env` file to ensure security.

---

## 🌟 Usage Workflow

1. **Connect Coinbase** (planned): Link your sandbox account via API keys in the Connect page.  
2. **Build a Bot**: On **New Bot**, configure thresholds, budget, and intervals.  
3. **Deploy**: Start the bot—watch the live chart populate with buy/sell markers and view logs.  
4. **Monitor**: Switch to the **Dashboard** to track performance; visit **Bots** to review past runs.

---

## 📈 Project Impact & Roadmap

- **Hands‑On Learning**: Empowers users to experiment with quantitative strategies and understand price dynamics.  
- **Scalable Platform**: Easily extend support to additional tokens, data feeds (e.g., sentiment scores, investor grades), and advanced analytics.  
- **Community Collaboration**: Open‑source structure invites contributions—add adapters for new exchanges or visualization enhancements.

**Next Steps:**  
- Multi‑asset support (e.g., Ethereum, altcoins)  
- Integration of sentiment and investor‑grade APIs  
- Production‑grade wallet connection and order management  

---


