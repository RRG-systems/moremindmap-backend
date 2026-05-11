# REAL DATA INTEGRATION GUIDE

## Overview

MOLTmarket system now supports **real Coinbase BTC/ETH market data** in **SIM/PAPER mode only**.

This document explains:
1. Architecture (minimal changes)
2. How to enable real data
3. How to verify it's working
4. Safety constraints

---

## Architecture: Minimal Change

### Current Flow (Random Walk)
```
ExecutionSimulator._get_price()
  ↓
  Random walk (±0.5% per step)
  ↓
Paper execution (0-2 bps)
Shadow execution (3+10 bps)
```

### New Flow (Real Data)
```
CoinbaseMarketFeed (WebSocket connection)
  ↓ 
ExecutionSimulatorRealData (adapter)
  ↓
Injects real prices into existing simulator
  ↓
Paper execution (0-2 bps)  ← UNCHANGED
Shadow execution (3+10 bps)  ← UNCHANGED
```

**Key point:** No execution logic was rewritten. Only price source swapped.

---

## Files Added

1. **`coinbase_market_feed.py`** (270 lines)
   - Connects to Coinbase WebSocket
   - Subscribes to BTC-USD and ETH-USD ticker channel
   - Normalizes ticks into standard format
   - Handles reconnect, heartbeat, errors
   - Thread-safe tick buffer
   - Public methods: `get_latest_tick()`, `get_latest_price()`, `get_bid_ask()`

2. **`execution_simulator_realdata.py`** (180 lines)
   - Wraps existing ExecutionSimulator
   - Injects real price source via `inject_real_price_source()`
   - Maps assets to Coinbase symbols (BTC → BTC-USD, etc.)
   - Exposes session state for dashboard/THINK
   - Handles feed disconnect (no silent fallback)

3. **`demo_realdata_session.py`** (200 lines)
   - Full end-to-end demo
   - Connects feed, runs 60-second session
   - Prints real prices flowing through system
   - Shows proof of real data vs. simulation

---

## How to Enable Real Data

### Step 1: Install WebSocket Client
```bash
pip install websocket-client
```

### Step 2: Create Session (Python)

```python
from coinbase_market_feed import CoinbaseMarketFeed
from dashboard_execution import ExecutionSimulator  # existing
from execution_simulator_realdata import setup_real_data_simulation
from dashboard_data_layer import DataLayer

# 1. Initialize market feed
feed = CoinbaseMarketFeed()
if not feed.connect(run_in_thread=True):
    print("Failed to connect")
    exit(1)

# 2. Initialize existing simulator
data_layer = DataLayer()
simulator = ExecutionSimulator(data_layer)

# 3. Wire them together
real_sim = setup_real_data_simulation(simulator, feed)

# 4. Now use simulator normally
#    It will consume real Coinbase prices instead of random walk
simulator.step()  # Uses real BTC/ETH prices

# 5. Get session state
state = real_sim.get_session_state()
print(f"BTC: ${state['btc_price']:.2f}")
print(f"ETH: ${state['eth_price']:.2f}")
```

### Step 3: Verify It's Working

```python
# Check feed stats
stats = feed.get_stats()
print(f"Connected: {stats['connected']}")
print(f"Ticks: {stats['ticks_received']}")
print(f"Latest BTC: ${stats['latest_btc']['mid']:.2f}")
```

---

## Verification Checklist

- [ ] Feed connects to Coinbase
- [ ] Ticks are received (check `feed.ticks_received`)
- [ ] Prices update in real-time
- [ ] Simulator uses real prices (not random walk)
- [ ] Paper PnL reflects real bid/ask
- [ ] BRAIN enforcement still works
- [ ] No live orders sent (PAPER ONLY)
- [ ] Feed disconnect handled properly (no fallback)

---

## Session Mode Labeling

All session state includes mode label:

```python
state = real_sim.get_session_state()
print(state['mode'])  # "SIM_REALDATA_COINBASE"
```

Dashboard and THINK can now distinguish:
- `SIM_RANDOM`: Old random-walk mode
- `SIM_REALDATA_COINBASE`: Real market data mode

---

## Safety Constraints (HARD LIMITS)

### 1. NO LIVE ORDERS
- Execution remains PAPER/SHADOW only
- No exchange order routing
- No wallet connections
- No capital deployment

Verification:
```python
# Simulator uses only paper execution
# No live_order() methods exist
# No exchange API calls made
```

### 2. FEED DISCONNECT HANDLING
- If feed drops: system enters DISCONNECTED state
- NO silent fallback to random walk
- NO orders placed without real prices
- Explicit error logged

Code proof:
```python
def _get_price_real_data(asset):
    price = self.get_price(asset)
    if price is None:
        # Feed disconnected — STOP execution
        print("Real feed unavailable, halting execution")
        return None  # Blocks trade
    return price
```

### 3. MODE LABELING
- Every session labeled with mode
- THINK aware of real vs. simulated data
- Dashboard displays mode clearly

---

## Integration with Existing Systems

### BRAIN Enforcement
```python
# BRAIN still gates trades (STOP/FLAT/THROTTLE)
# Paper execution applies slippage (0-2 bps)
# Shadow execution applies slippage (3+10 bps)
# ALL UNCHANGED
```

### Probation + Scaling
```python
# Probation tracks real sessions
# Scaling decisions based on real data
# Logging captures real market conditions
```

### THINK Diagnostics
```python
# THINK analyzes real session logs
# Can diagnose: why did we STOP?
# Real answer: based on real market data
```

---

## Data Flow Example

```
09:15:00 UTC  [COINBASE] Receive BTC=43250.25, ETH=2180.50
              ↓
              Tick added to buffer
              ↓
09:15:01 UTC  [SIMULATOR] Signal generated → entry
              ↓
              _get_price_real_data('BTC') → 43250.25 (real)
              ↓
              Paper execution
              Entry fill: 43250.25 * (1 ± 0.0002)  [0-2 bps]
              ↓
09:15:15 UTC  Exit generated
              ↓
              Exit fill: real current price ± 0-2 bps
              ↓
              PnL calculated based on REAL prices
              ↓
              Logged with mode="SIM_REALDATA_COINBASE"
```

---

## Testing Real Data Integration

Run demo:
```bash
python3 demo_realdata_session.py
```

Expected output:
```
[SESSION] Connecting to Coinbase market feed...
[SESSION] ✓ Connected to Coinbase
[SESSION] Running simulation cycles for 60s...
[CYCLE   5] BTC: $43250.25  ETH: $2180.50  Ticks: 45
[CYCLE  10] BTC: $43251.10  ETH: $2180.75  Ticks: 90
...
[SESSION SUMMARY]
  Feed connected: True
  Ticks received: 450
  [PROOF OF REAL DATA]
  ✓ Received 450 real market ticks
  ✓ Prices updated 60 times
  ✓ System NOT using random walk
  ✓ Execution mode: PAPER ONLY (no live orders)
```

---

## What Did NOT Change

1. **Execution logic** — same paper/shadow models
2. **Slippage assumptions** — same BPS costs
3. **BRAIN enforcement** — same gates
4. **Probation logic** — same constraints
5. **Logging format** — same structured logs
6. **Dashboard interface** — same endpoints

---

## Next Steps (After Real Data Proven)

1. **Phase 4.9:** Integrate slippage from real order book depth
2. **Phase 4.10:** Detect market regimes from real ticks
3. **Phase 4.11:** Measure real execution costs
4. **Phase 5:** THINK explains decisions based on real market conditions

---

## Architecture Diagram

```
┌─────────────────────────────────────────┐
│     Coinbase WebSocket (Public)         │
│  wss://ws-feed.exchange.coinbase.com   │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│    CoinbaseMarketFeed                   │
│  - BTC-USD, ETH-USD subscriptions       │
│  - Normalized tick format               │
│  - Thread-safe buffer                   │
│  - Reconnect handling                   │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  ExecutionSimulatorRealData             │
│  - Price source injection               │
│  - Feed disconnect detection            │
│  - Session state exposure               │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  ExecutionSimulator (EXISTING)          │
│  - Paper execution (0-2 bps)            │
│  - Shadow execution (3+10 bps)          │
│  - BRAIN enforcement                    │
│  - Probation tracking                   │
│  - Trade logging                        │
└──────────────┬──────────────────────────┘
               │
               ↓
┌─────────────────────────────────────────┐
│  Dashboard + THINK                      │
│  - Real session state                   │
│  - Real-market diagnostics              │
│  - Mode labeling (SIM_REALDATA_COINBASE)│
└─────────────────────────────────────────┘
```

---

**End of guide. System ready for real market validation.**
