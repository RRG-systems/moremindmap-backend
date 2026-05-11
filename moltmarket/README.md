# MOLTmarket Live Validation Dashboard v1

Research console for live paper/shadow execution with historical backtest overlay.

## Quick Start

```bash
cd moltmarket
python moltmarket_dashboard.py
```

Then open: **http://localhost:5000**

## What It Does

### Three Execution Layers

1. **Paper** - Idealized fills (best-ask/best-bid, 0-2 bps slippage)
2. **Shadow** - Realistic fills (degraded fills +3/-3 bps, 2-5 bps slippage, 10 bps round-trip cost)
3. **Backtest** - Historical reference (walk-forward on past 30-60 days)

All three run simultaneously and are displayed in a single dashboard.

### Dashboard Features

**KPI Cards (Top):**
- Paper Rolling Value
- Shadow Rolling Value
- Paper vs Shadow Delta (%)
- Backtest Edge (bps)
- Total Trades
- Rolling Win Rate (%)
- Avg PnL / Trade (bps)
- Current Signal / Asset

**Main Chart:**
- Equity curves overlay (paper, shadow, backtest)
- Time range selector (1h, 4h, 1d)
- Toggle visibility per layer

**Secondary Panels:**
- Execution degradation (slippage, fill rates)
- Rolling edge (20-trade and 50-trade windows)
- Regime indicator

**Trade Breakdowns:**
- By Asset (BTC, ETH, SOL)
- By Signal (Mean Reversion, Weekend Bias, Vol MR, Trend)
- By Regime (high vol, low vol, trending, ranging)
- By Direction (long/short)

**Recent Trades Table:**
- Last 30 trades (scrollable)
- Color-coded by source (paper/shadow/backtest)
- Columns: time, asset, signal, source, side, entry, exit, PnL, duration

## Data Files

CSV files created in workspace directory for further analysis:

1. **research_trades.csv** - Every trade executed
   - Columns: timestamp, asset, signal, source, side, entry_price, exit_price, expected_fill, shadow_fill, pnl, pnl_bps, duration, regime

2. **research_runs.csv** - Session summaries
   - Columns: run_id, mode, asset, signal, start_time, end_time, trades, win_rate, avg_pnl, total_pnl, drawdown

3. **signal_health.csv** - Rolling signal metrics
   - Columns: timestamp, asset, signal, rolling_20_edge, rolling_50_edge, rolling_win_rate, rolling_drawdown

4. **execution_quality.csv** - Execution metrics
   - Columns: timestamp, asset, signal, expected_entry, shadow_entry, expected_exit, shadow_exit, slippage_bps, paper_shadow_delta

## File Structure

```
moltmarket/
├── moltmarket_dashboard.py       # Main app
├── dashboard_data_layer.py       # CSV handling + metrics
├── dashboard_execution.py        # Paper/shadow/backtest simulation
├── templates/
│   └── dashboard.html            # UI template
├── static/
│   ├── dashboard.css             # Dark theme styling
│   └── dashboard.js              # Client-side interactivity
├── requirements.txt              # Python dependencies
└── README.md                     # This file
```

## Design Notes

- **Dark theme** inspired by Polymarket's research console
- **Research-focused**: clean cards, strong typography, minimal clutter
- **Real-time updates**: 1-second polling interval
- **Screenshot-friendly**: one screenshot tells the full story
- **No product UI**: no auth, billing, strategy editor, or deployment

## How Execution Works

### Paper Flow
1. Signal generated
2. Entry at idealized fill (best bid/ask)
3. Slippage: 0-2 bps randomly applied
4. Trade held for random duration (60-3600s)
5. Exit at idealized fill
6. PnL calculated with minimal friction

### Shadow Flow
1. Same signal as paper
2. Entry with degraded fill (ask +3 bps if long, bid -3 bps if short)
3. Additional slippage: 2-5 bps randomly applied
4. Exit with degraded fill (opposite side)
5. Round-trip cost: 10 bps deducted
6. PnL shows realistic execution impact

### Backtest Flow
1. Historical signals replayed on past data
2. Same regime/signal/asset as paper/shadow
3. Same execution model as shadow (realistic fills)
4. Equity curve shown for reference

## Metrics Explained

**Win Rate**: % of trades with positive PnL
**Edge (bps)**: Average PnL per trade in basis points
**Slippage**: Difference between ideal and executed fill
**Paper vs Shadow Delta**: How much execution quality costs in %

## Real-Time Updates

- Dashboard updates every 1 second
- New signals generated with ~15% probability per step
- CSV files appended with each trade
- No data loss on refresh

## Development Notes

To modify signal generation:
- Edit `dashboard_execution.py`: `_generate_signal()` method

To change execution model:
- Edit slippage parameters in `_execute_paper()` and `_execute_shadow()`

To add new assets/signals:
- Update `self.assets` and `self.signals` lists in `ExecutionSimulator.__init__()`

## Next Steps (Future Versions)

- Real signal integration (hook into live signal feed)
- Historical data replay for backtest
- User-configurable execution parameters
- Detailed execution quality analysis
- Export to clipboard for reporting
