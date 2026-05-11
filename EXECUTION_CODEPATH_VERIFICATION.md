═══════════════════════════════════════════════════════════════════════════════
EXECUTION CODEPATH VERIFICATION — REAL vs PLACEHOLDER
═══════════════════════════════════════════════════════════════════════════════

EXECUTION SIMULATOR: /Users/rrg/.openclaw/workspace/moltmarket/dashboard_execution.py
ARENA EXECUTION: /Users/rrg/moltmarket/engine/multi_market_arena.py (NOT used for dashboard)
DATA LAYER: /Users/rrg/.openclaw/workspace/moltmarket/dashboard_data_layer.py

═══════════════════════════════════════════════════════════════════════════════
1. SLIPPAGE
═══════════════════════════════════════════════════════════════════════════════

STATUS: PARTIAL (simulated in ExecutionSimulator, but NOT in main arena bot)

PAPER EXECUTION:
  File: dashboard_execution.py, line ~130-145
  Code:
    entry_fill = entry_price * (1 + random.uniform(-0.0002, 0.0002))  # ±2 bps
  Status: ✓ REAL (applied to fills)

SHADOW EXECUTION:
  File: dashboard_execution.py, line ~183-190
  Code:
    entry_fill = entry_price * 1.0003          # ask +3 bps
    slippage_bps = random.uniform(0.0002, 0.0005)
    entry_fill *= (1 + slippage_bps)           # +2-5 bps random
  Status: ✓ REAL (applied to fills)

MAIN ARENA BOT:
  File: multi_market_arena.py, line 398-400
  Code:
    if order.side == "BUY":
        fill_price = market.ask
    elif order.side == "SELL":
        fill_price = market.bid
  Status: ✗ PLACEHOLDER (zero slippage, fills at exact bid/ask)
  Comment: "Deterministic fills, no latency/slippage simulation" (line 15)

VERDICT: 
  ✓ REAL in ExecutionSimulator (dashboard display)
  ✗ PLACEHOLDER in MultiMarketArena (actual arena execution)
  ⚠️  MISMATCH: Dashboard shows slippage that doesn't exist in real arena bot

───────────────────────────────────────────────────────────────────────────────
2. DEPTH-AWARE FILLS
───────────────────────────────────────────────────────────────────────────────

STATUS: ✗ PLACEHOLDER (measured but never used)

DEPTH DATA EXISTS:
  File: multi_market_arena.py
  Data structure: MarketSnapshot has bid_size, ask_size
  Status: Data available but ignored

FILL LOGIC:
  File: multi_market_arena.py, line 398-400
  Code:
    fill_price = market.ask  # No depth check
    # No conditional: if order.size > market.ask_size
  Status: ✗ PLACEHOLDER (full fills always, no depth limit)

EXECUTIONS IMULATOR:
  File: dashboard_execution.py
  Status: No depth checking (always fills)

VERDICT:
  ✗ PLACEHOLDER (measured but unused in both systems)
  ⚠️  RISK: Unrealistic fills if order size > available depth

───────────────────────────────────────────────────────────────────────────────
3. FEES
───────────────────────────────────────────────────────────────────────────────

STATUS: PARTIAL (only in shadow execution, NOT in paper or arena)

PAPER EXECUTION:
  File: dashboard_execution.py, line ~130-165
  Code:
    pnl = (exit_fill - entry_fill) / entry_fill * 10000
    # NO FEE DEDUCTION
  Status: ✗ PLACEHOLDER (zero fees)

SHADOW EXECUTION:
  File: dashboard_execution.py, line ~183-225
  Code:
    roundtrip_cost = (entry_price * 0.001) / entry_price  # 10 bps hardcoded
    pnl_bps = (exit_fill - entry_fill) / entry_fill * 10000 - 100  # -100 bps (10 bps)
  Status: ✓ REAL (10 bps roundtrip cost hardcoded, applied to PnL calculation)

MAIN ARENA BOT:
  File: multi_market_arena.py, line 350-365
  Code:
    realized_pnl = (exit_price - position.entry_price) * position.shares
    # NO FEE DEDUCTION
  Status: ✗ PLACEHOLDER (zero fees)

WHERE FEES ARE APPLIED:
  - Shadow: PnL calculation line 215-218 (bps subtraction)
  - Paper: Not applied (line 150)
  - Arena: Not applied (line 350)

VERDICT:
  ✓ REAL in shadow (10 bps hardcoded roundtrip)
  ✗ PLACEHOLDER in paper (zero)
  ✗ PLACEHOLDER in arena (zero)
  ⚠️  INCONSISTENCY: Shadow has 10 bps, paper and arena have 0

───────────────────────────────────────────────────────────────────────────────
4. PAPER VS SHADOW DIFFERENTIATION
───────────────────────────────────────────────────────────────────────────────

STATUS: PARTIAL (some differentiation exists in sim, but mismatch with arena)

EXECUTION SIMULATOR:
  File: dashboard_execution.py

  PAPER (line 130-165):
    - Entry: ±2 bps random (realistic)
    - Exit: ±2 bps random
    - Fees: 0 bps
    - PnL: (exit - entry) / entry * 10000
    Status: ✓ REAL differentiation

  SHADOW (line 183-225):
    - Entry: +3 bps +2-5 bps random = 5-8 bps degradation
    - Exit: -3 bps on exits
    - Fees: -10 bps roundtrip
    - PnL: same calc but -100 bps
    Status: ✓ REAL differentiation

  RESULT: Paper typically shows +X bps, Shadow shows +X-10 bps
  Status: ✓ REAL (different fills and costs)

MAIN ARENA BOT:
  File: multi_market_arena.py, line 398-400
  Code:
    if order.side == "BUY":
        fill_price = market.ask
    else:
        fill_price = market.bid
  Status: ✗ IDENTICAL for both (single fill_price, no differentiation)

  Paper vs Shadow delta: 0.0 (hardcoded placeholder)
  Status: ✗ PLACEHOLDER

VERDICT:
  ✓ REAL in ExecutionSimulator (shadow worse than paper)
  ✗ PLACEHOLDER in MultiMarketArena (identical execution)
  ⚠️  MISMATCH: Dashboard shows differentiation, arena doesn't apply it

───────────────────────────────────────────────────────────────────────────────
5. PARTIAL FILLS
───────────────────────────────────────────────────────────────────────────────

STATUS: ✗ PLACEHOLDER (never happens, always full fills)

EXECUTION SIMULATOR:
  File: dashboard_execution.py, line ~130, 183
  Code:
    # No partial fill logic anywhere
    # Trades record pnl without partial fill tracking
  Status: ✗ PLACEHOLDER (always full fills)

MAIN ARENA BOT:
  File: multi_market_arena.py, line 398-415
  Code:
    # No depth checking, no partial fill logic
    position = OpenPosition(
        shares=order.size,  # ALWAYS full size
    )
  Status: ✗ PLACEHOLDER (always full fills)

PARTIAL FILLS PANEL:
  File: templates/dashboard.html
  Status: Hard-coded static value (0 partial fills)
  Status: ✗ PLACEHOLDER (never updates)

VERDICT:
  ✗ PLACEHOLDER (both simulator and arena always fill full size)
  ⚠️  RISK: Unrealistic if order size > available depth

───────────────────────────────────────────────────────────────────────────────
6. EXECUTION DEGRADATION PANEL
───────────────────────────────────────────────────────────────────────────────

STATUS: ✓ PARTIALLY REAL (mixed real + placeholder metrics)

"Paper Slippage" (0-2 bps):
  Calculated from: dashboard_data_layer.py, line 373-374
  Logic:
    entry_slippage_bps = abs(shadow_entry - expected_entry) / expected_entry * 10000
  Source: Comparing 'shadow_fill' vs 'expected_fill' from trade records
  Status: ✓ REAL (computed from actual execution data)

"Shadow Slippage" (2-5 bps):
  Calculated from: dashboard_data_layer.py, line 373-374
  Status: ✓ REAL (same calculation)

"Round-Trip Cost" (10 bps):
  Source: dashboard_execution.py, line 218 hardcoded roundtrip_cost
  Status: ✓ REAL (hardcoded in shadow execution)

Exit Slippage:
  File: dashboard_data_layer.py, line 376-381
  Code:
    estimated_shadow_exit = expected_exit * 0.9997
    exit_slippage_bps = abs(estimated_shadow_exit - expected_exit) / expected_exit * 10000
  Status: ⚠️  PARTIALLY REAL (estimated using 0.9997 multiplier, not actual exit data)

VERDICT:
  ✓ REAL (metrics calculated from trade data)
  ⚠️  PARTIAL (exit slippage is estimated, not from actual fills)

───────────────────────────────────────────────────────────────────────────────
SUMMARY TABLE
───────────────────────────────────────────────────────────────────────────────

METRIC                    | Dashboard Sim | Main Arena Bot | Status
──────────────────────────┼───────────────┼────────────────┼──────────────────
Slippage                  | ✓ REAL (2-5)  | ✗ PLACEHOLDER  | MISMATCH ⚠️
Depth-aware fills         | ✗ PLACEHOLDER | ✗ PLACEHOLDER  | BOTH FAKE ✗
Fees                      | ✓ REAL (10bp) | ✗ PLACEHOLDER  | MISMATCH ⚠️
Paper vs Shadow diff      | ✓ REAL        | ✗ PLACEHOLDER  | MISMATCH ⚠️
Partial fills             | ✗ PLACEHOLDER | ✗ PLACEHOLDER  | BOTH FAKE ✗
Exec degradation panel    | ✓ REAL        | N/A            | WORKS ✓

───────────────────────────────────────────────────────────────────────────────
THE CRITICAL MISMATCH
───────────────────────────────────────────────────────────────────────────────

Dashboard ExecutionSimulator ("what you see"):
  - Slippage: 2-8 bps applied
  - Fees: 10 bps (shadow only)
  - Paper vs Shadow: Differentiated
  - Result: REALISTIC display

Main Arena Bot ("what actually runs"):
  - Slippage: 0 bps
  - Fees: 0 bps
  - Paper vs Shadow: Identical
  - Result: UNREALISTIC execution

CONSEQUENCE:
  Dashboard metrics look good (+2-5 bps edge)
  But real arena bot has fake profits (+25-200 bps fake edge)
  
  If Evaluate Bot passes based on dashboard metrics:
  Bot is actually LOSING MONEY in real execution

───────────────────────────────────────────────────────────────────────────────
CRITICAL QUESTION
───────────────────────────────────────────────────────────────────────────────

When you click "EVALUATE BOT" in the dashboard, which bot's metrics are being read?

A) ExecutionSimulator results (dashboard trades)
B) MultiMarketArena results (actual arena)

Answer determines whether profitability protection works or not.

If A: Metrics are REAL now ✓
If B: Needs all 3 fixes before deployment ✗

---

**Files Modified:**
- None yet. This is verification pass only.

**Key Files to Reference:**
- Dashboard sim: /Users/rrg/.openclaw/workspace/moltmarket/dashboard_execution.py
- Main arena: /Users/rrg/moltmarket/engine/multi_market_arena.py
- Data layer: /Users/rrg/.openclaw/workspace/moltmarket/dashboard_data_layer.py
- Evaluation: /Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py (lines 995-1041)
