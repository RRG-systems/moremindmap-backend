# Quick Start - 30 Seconds

## 1. Install Dependencies
```bash
cd moltmarket
pip install -r requirements.txt
```

## 2. Run Dashboard
```bash
python moltmarket_dashboard.py
```

## 3. Open Browser
Go to: **http://localhost:5000**

Done! 🎉

---

## What You'll See

**Top Row (KPIs):**
- Paper Rolling Value (ideal fills)
- Shadow Rolling Value (realistic fills)
- Paper vs Shadow Delta (execution cost)
- Backtest Edge (historical reference)
- Total Trades, Win Rate, Avg PnL, Current Signal

**Main Chart:**
- Three equity curves (paper, shadow, backtest)
- Toggle visibility per layer

**Breakdown Tables:**
- By Asset (BTC, ETH, SOL)
- By Signal (Mean Reversion, Weekend Bias, etc.)
- By Regime (high vol, low vol, trending, ranging)
- By Direction (long/short)

**Recent Trades:**
- Last 30 trades
- Color-coded by source (paper=cyan, shadow=orange, backtest=green)

---

## Data Files Created

These appear in the workspace directory:

1. `research_trades.csv` - Every trade
2. `research_runs.csv` - Session summaries
3. `signal_health.csv` - Rolling metrics
4. `execution_quality.csv` - Slippage tracking

All are append-friendly for continuous logging.

---

## How It Works

### Three Execution Layers

**Paper** 
- Real-time signals
- Best bid/ask fills
- 0-2 bps slippage
- For testing signal quality

**Shadow**
- Same signals as paper
- Degraded fills (+3/-3 bps)
- 2-5 bps slippage + 10 bps round-trip
- For realistic cost estimation

**Backtest**
- Historical reference
- 45-day walk-forward
- Same execution model as shadow
- For comparing vs. past

All three run simultaneously in one dashboard.

---

## Stop It

Press **Ctrl+C** in the terminal.

Data is automatically saved to CSV files. No data loss.

---

## Troubleshooting

**Port 5000 in use?**
```bash
# Kill the process
lsof -i :5000 | grep LISTEN | awk '{print $2}' | xargs kill -9

# Or specify different port in moltmarket_dashboard.py
# Line: app.run(host='127.0.0.1', port=5001)  # Change to 5001
```

**Missing Flask?**
```bash
pip install Flask==2.3.2
```

**Python not found?**
```bash
# Use python3 explicitly
python3 moltmarket_dashboard.py
```

---

## File Structure

```
moltmarket/
├── moltmarket_dashboard.py       # Main app (start here)
├── dashboard_data_layer.py       # CSV handling
├── dashboard_execution.py        # Paper/shadow/backtest
├── templates/
│   └── dashboard.html            # UI
├── static/
│   ├── dashboard.css             # Styling
│   └── dashboard.js              # Interactivity
├── requirements.txt              # Dependencies
└── README.md                     # Full docs
```

---

## One Screenshot Tells the Story

The dashboard shows:
- Paper PnL vs Shadow PnL (execution impact)
- Backtest reference curve (historical comparison)
- Win rate, edge, trade count (key metrics)
- Recent trades breakdown (what's happening right now)

All in one view. Screenshot-friendly.

---

**That's it!** Happy validating. 🚀
