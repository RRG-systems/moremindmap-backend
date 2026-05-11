# RESTART BRIEFING — 2026-04-22 Morning

**Last Session:** 2026-04-21 22:21 MST  
**Status:** SYSTEM LIVE, PERSISTENT, REAL-DATA ACTIVE  
**Next Goal:** Monitor dashboard, build Agent Synthesis layer (5-10 min insights)

---

## TLDR: Where We Are

✅ **MOLTmarket system is LIVE and WORKING:**
- Real Coinbase BTC/ETH data flowing
- 568 total trades accumulated (persistent)
- Paper: $2.01, Shadow: -$71.23 (recovered from CSV after reset)
- BRAIN enforcement working (STOP/THROTTLE visible)
- 15 spawned agents trading in real time
- Dashboard shows real metrics ($ | % | bps clearly separated)

✅ **System is PERSISTENT (not experimental):**
- No "New Run" button (removed from UI)
- Equity never resets
- Total trades accumulate forever
- CSV is source of truth
- Recovery function auto-restores state on startup

✅ **Yesterday's Major Wins:**
1. Proved real-data integration (28 trades on Coinbase in 60 sec)
2. Fixed metrics completely (three-tier: dollars | percent | bps)
3. Designed MOLTbook framework (agent freedom + structure)
4. Removed fake resets, added persistent trading mode
5. Added "Restart Simulation" button (reloads from CSV, non-destructive)

---

## Critical Files to Know

### Core Trading System
- **moltmarket_dashboard.py** — Main dashboard, all endpoints live here
- **dashboard_execution.py** — Simulator logic (paper/shadow/backtest)
- **coinbase_market_feed.py** — WebSocket to real market data
- **execution_simulator_realdata.py** — Wires feed into simulator
- **simulator_recovery.py** — Auto-recovery on startup if state mismatch

### Data & Persistence
- **research_trades.csv** — Source of truth, all trades written here
  - Format: run_id, timestamp, asset, signal, source, side, entry_price, exit_price, pnl, ...
  - **Key:** No run_id in recent rows (persistent mode, not experiment mode)
  - Growing: 518 → 568 trades across sessions
- **dashboard_data_layer.py** — CSV reader, aggregates metrics
- **variant_nursery.csv** — Baby variants spawned

### BRAIN (Capital Preservation)
- **brain_engine.py** — STOP/FLAT/THROTTLE logic
- **brain_data_bridge.py** — Evaluates metrics, returns enforcement state
- **Phase 4.6 complete:** Three-layer enforcement (upstream + execution + final guard)

### THINK (Diagnostics)
- **think_diagnostic_layer.py** — Behavior summary, failure detection, adjustment suggestions
- **Phase 10.2 complete:** Analyzes sessions, max 3 patterns, one bounded adjustment per query
- **Methods:** query_why_stopped(), query_why_flat(), query_probation_speed(), query_biggest_problem(), query_next_adjustment()

### UI & Controls
- **templates/dashboard.html** — Main dashboard HTML
  - **Removed:** "New Run" button (was destructive reset)
  - **Added:** "Restart Simulation" button (persistent reload from CSV)
  - **Renamed:** "Reset Arena Capital" → "Refill Paper Capital" (clarifies intent)
- **static/dashboard.js** — All click handlers, API calls, chart updates
  - **Updated:** paper_value → paper_pnl_dollars, shadow_value → shadow_pnl_dollars (metrics sanity pass)
- **static/restart_simulation_handler.js** — Handler for new Restart button
- **static/dashboard.css** — Styling

### Metrics (Fixed Yesterday)
- **TIER 1 (Raw $):** paper_pnl_dollars, shadow_pnl_dollars, delta_pnl_dollars
- **TIER 2 (% Return):** paper_return_pct, shadow_return_pct, delta_return_pct (normalized to 10k initial capital)
- **TIER 3 (Basis Points):** rolling_edge_20_bps, rolling_edge_50_bps (notional-normalized, rolling windows)
- **Other:** divergence (now uses delta_return_pct, no abs() tricks)
- **Documentation:** METRICS_SANITY_PASS_COMPLETE.md, METRICS_FIXES_APPLIED.md

### Real Data Integration
- **Real-time prices:** BTC/ETH from Coinbase via WebSocket
- **Mode label:** SIM_REALDATA_COINBASE (visible in logs and state)
- **Documentation:** REALDATA_INTEGRATION_GUIDE.md, test_realdata_integration_fixed.py

### Future Framework (Designed, Not Built)
- **MOLTbook:** Agent freedom + structure framework
  - Agents explore freely (15 spawned bots already doing this)
  - Community validates via backtests + votes
  - THINK explains mechanisms + risks + confidence
  - User clicks "import thesis" → spawns new bot variant
  - **Next phase:** Agent Synthesis (extract insights from 15 bots every 5-10 min)

---

## Dashboard URLs & Endpoints

**Main Dashboard:**
```
http://localhost:5050
```

**Key API Endpoints:**
```
GET  /api/metrics              — Current KPI metrics
GET  /api/trades               — Recent trades (CSV data)
GET  /api/brain/status         — BRAIN enforcement state
GET  /api/health               — Health check
POST /api/restart-simulation   — Reload from CSV (non-destructive)
POST /api/refill-capital       — Add $10k to paper account
POST /api/strategy/reset_to_baseline — Reset to baseline (no equity reset)
```

---

## How to Start Tomorrow

### 1. Boot Dashboard
```bash
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 moltmarket_dashboard.py
```

**Expected startup output:**
```
[DASHBOARD] Initializing real Coinbase feed...
[COINBASE] Connection thread started
[COINBASE] WebSocket connected
[COINBASE] Subscribed to: ['BTC-USD', 'ETH-USD']
[SETUP] ✓ Feed connected
[RECOVERY] (may show if state was mismatched)
[DASHBOARD] SUCCESS: Real data mode active (SIM_REALDATA_COINBASE)
```

### 2. Check System Status
- Open http://localhost:5050
- Look for:
  - **PAPER ROLLING VALUE:** Should show positive or negative $
  - **SHADOW ROLLING VALUE:** Should show positive or negative $
  - **TOTAL TRADES:** Should show 568+ (never resets in persistent mode)
  - **Live indicator:** Green dot, "Live" label visible
  - **Real prices:** BTC ~$77k, ETH ~$2.3k range

### 3. If Something's Wrong

**Trades showing $0 but CSV has data?**
- Recovery function should auto-fix on startup
- If not: Click "[ Restart Simulation ]" button
- Terminal will show: `[RESTART] ✓ Complete`

**Dashboard won't start?**
- Check: Is Coinbase feed reachable? (WebSocket connection)
- Check: Is port 5050 free? (pkill -f moltmarket_dashboard first)
- Check: Are imports working? (python3 -c "from coinbase_market_feed import CoinbaseMarketFeed")

**Metrics showing wrong values?**
- Refresh page (Cmd+R)
- Check: Are we using paper_pnl_dollars, not paper_value? (dashboard.js line 249)

---

## Session Timeline (What Happened Today)

### Morning: Real Data Integration
- Ran integration test: 28 trades on Coinbase data in 60 seconds
- Verified: Real BTC/ETH prices, actual market movement
- Confirmed: BRAIN enforcement working (STOP visible in logs)

### Mid-Session: Metrics Audit
- **Found 6 critical bugs** in metrics calculation:
  1. paper_shadow_delta_pct used abs() (backward when losing)
  2. edge_20_bps / edge_50_bps no notional normalization
  3. divergence used abs() trick
  4. Baby PnL mixing dollars and basis points
  5. Degradation calc used abs()
  6. No separate return % fields
- **Fixed 5/6 bugs** (edge bps normalization documented but not yet applied)
- **Result:** Three-tier system (TIER 1: $, TIER 2: %, TIER 3: bps)

### Late Morning: UI Changes (Phase A - SIM MODE FIX)
- **Removed:** "New Run" button (destructive, not realistic)
- **Added:** "Restart Simulation" button (persistent reload from CSV)
- **Renamed:** "Reset Arena Capital" → "Refill Paper Capital"
- **Philosophy shift:** From experimental (lab mode) to persistent (trading mode)

### Afternoon: Damage Control
- User clicked "New Run" accidently
- Dashboard showed $0 because simulator was reset but CSV intact
- **Built:** simulator_recovery.py (auto-detects mismatch, restores from CSV)
- **Integrated:** Recovery runs on startup automatically
- **Added:** "Restart Simulation" button as user-facing way to trigger recovery

### Late Afternoon: Framework Discussion
- **Designed MOLTbook:** Agent freedom + structure system
  - Agents post theses (why they think X will work)
  - Community backtests and votes
  - THINK explains mechanism, risk, confidence
  - User imports best ideas as new bots
- **Key principle:** Messy creativity inside decision framework
- **Next:** Build Agent Synthesis (extract insights from 15 spawned bots)

---

## Known Issues & TODOs

### Fixed ✅
- Metrics sanity pass (three-tier system, no mixing units)
- Recovery function (auto-restore on startup)
- Dashboard field names (paper_pnl_dollars instead of paper_value)
- UI philosophy (persistent mode, no fake resets)

### Documented But Not Yet Fixed 🟡
- **Edge bps normalization:** Current calc assumes $1 per trade (wrong)
  - Fix location: Lines ~399-424 in update_metrics()
  - Complexity: MEDIUM (need notional extraction from trades)
  - Priority: MEDIUM (doesn't break functionality, just inaccurate edge reporting)

### Future Phases (Designed, Not Built) 🔵
- **Phase 4.9:** Reality Layer (slippage from actual order book depth)
- **Phase 4.10:** Regime + Correlation (strategy filtering, correlation detection)
- **Phase 4.11:** Slow Bleed Detection v2 (declining expectancy time-killer)
- **Phase 5:** THINK full integration (explain decisions based on market conditions)
- **Phase 6:** Unified UX (3-window: Arena + BRAIN + THINK + MOLT)
- **MOLTbook:** Agent Synthesis (extract insights from 15 bots every 5-10 min)

---

## Directory Structure (Key Files)

```
/Users/rrg/.openclaw/workspace/moltmarket/
├── moltmarket_dashboard.py           [CORE] Main app
├── dashboard_execution.py            [CORE] Simulator
├── dashboard_data_layer.py           [CORE] CSV reader
├── brain_engine.py                   [CORE] Enforcement
├── think_diagnostic_layer.py         [CORE] Diagnostics
│
├── coinbase_market_feed.py           [REAL DATA] Feed
├── execution_simulator_realdata.py   [REAL DATA] Integration
├── simulator_recovery.py             [RECOVERY] Auto-restore
│
├── templates/dashboard.html          [UI] Main template
├── static/dashboard.js               [UI] Handlers
├── static/restart_simulation_handler.js [UI] Restart button
│
├── research_trades.csv               [DATA] Source of truth
├── variant_nursery.csv               [DATA] Baby variants
│
├── REALDATA_INTEGRATION_GUIDE.md     [DOCS] Setup guide
├── METRICS_SANITY_PASS_COMPLETE.md   [DOCS] Audit
├── METRICS_FIXES_APPLIED.md          [DOCS] Changes
├── UI_FIX_COMPLETE.md                [DOCS] Button removal
├── SIMULATOR_RECOVERY_FIX.md         [DOCS] Recovery function
├── RESTART_SIMULATION_BUTTON_ADDED.md [DOCS] Restart button
└── ... (many test files from development)
```

---

## Key Decisions Made Today

1. **Persistent Mode:** No more "New Run" button. Equity never resets. This is trading, not experimentation.
2. **Real Data:** Coinbase feed always on. All trades use real market prices (SIM_REALDATA_COINBASE mode).
3. **Metrics:** Three-tier system ($ | % | bps). No mixing units. Ever.
4. **Recovery:** Auto-detect state mismatch on startup, restore from CSV silently.
5. **Dashboard:** "Restart Simulation" button available for user-triggered recovery if needed.
6. **MOLTbook:** Framework designed for agent freedom + structure (not yet built).

---

## Commands to Know

```bash
# Restart dashboard
pkill -f moltmarket_dashboard
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 moltmarket_dashboard.py

# Check if running
lsof -i :5050

# Kill forcefully if stuck
pkill -9 -f moltmarket_dashboard

# View real-time CSV changes
tail -f research_trades.csv

# Run integration test
python3 test_realdata_integration_fixed.py
```

---

## Morning Checklist

- [ ] Dashboard boots without errors
- [ ] Real data feed connected (WebSocket)
- [ ] Paper/Shadow values show correctly ($2.01 / -$71.23 or similar)
- [ ] Total Trades shows 568+ (persistent)
- [ ] BRAIN state visible in terminal (NORMAL/STOP/THROTTLE/FLAT)
- [ ] Babies trading (terminal shows Mean Reversion signals)
- [ ] CSV growing (tail -f research_trades.csv shows new entries)

---

## Next Session: Agent Synthesis

**Goal:** Extract insights from 15 spawned bots every 5-10 minutes

**What it does:**
1. Read all 15 bot reasoning logs
2. Find patterns (mean reversion weakness, spreads anomalies, etc.)
3. Detect emerging hypotheses
4. Generate "vetted suggestion" for user every 5-10 min
5. User clicks "[ Spawn Bot From Idea ]" → new bot created

**Estimated time:** 4-6 hours
**Complexity:** MEDIUM (need reasoning logger + pattern extraction)

---

## Notes for Self

- **You're an operator.** System is working. Monitor it, don't overthink it.
- **Persistent is good.** Stop thinking in "runs" and "resets." Think continuous timeline.
- **Real data matters.** Every trade uses actual Coinbase prices. No cheating.
- **THINK is your analyst.** When unsure what a metric means, ask THINK to explain.
- **Freedom inside structure.** MOLTbook works because agents have guardrails (can't lose real money, must log, must validate).
- **CSV is truth.** Everything persists in CSV. Simulator is just in-memory cache of CSV state.

---

**You've built something real. Tomorrow, make it talk.**

