# EVALUATE BOT — SURVIVAL GATE ADDITION

**Status:** COMPLETE ✓  
**Date:** 2026-04-17 22:10 MST  
**Goal:** Add kill switch / survival check to evaluation engine

---

## WHAT WAS ADDED

Three new checks in the `evaluate_arena_bot()` endpoint:

### 1. MAX DRAWDOWN CHECK

**What it does:**
- Tracks equity curve from simulator (shadow preferred)
- Measures peak-to-trough percentage decline
- Fails if max drawdown > 5%

**Implementation:**
```python
# Calculate max drawdown from equity curve
peak = 10000.0
for value in equity_values:
    if value > peak:
        peak = value
    drawdown = (peak - value) / peak * 100
    max_drawdown_pct = max(max_drawdown_pct, drawdown)

# Fail if > 5%
if max_drawdown_pct > 5.0:
    FAIL
```

**Display:** `✔ or ✖ Max Drawdown: X%`

---

### 2. STABILITY CHECK

**What it does:**
- Detects sudden equity collapses
- Looks for any single step drop > 2% of starting capital
- Fails if detected

**Implementation:**
```python
# Look for sudden large moves
for i in range(1, len(equity_values)):
    prev = equity_values[i-1]
    curr = equity_values[i]
    move_pct = (prev - curr) / prev * 100
    
    # Flag if any step loses > 2%
    if move_pct > 2.0:
        sudden_collapse = True
        FAIL
```

**Display:** `✔ or ✖ Stability Check: STABLE / UNSTABLE`

---

### 3. SURVIVAL GATE

**Combined logic:**
```python
survival_pass = (max_drawdown_pct <= 5.0) AND (no_sudden_collapse)

status = PASS if (all_checks_pass AND survival_pass) else FAIL
```

**Key:** Bot can fail even if sample size is large if survival is poor.

---

## RECOMMENDATION LOGIC

Now survival-aware:

| Scenario | Recommendation |
|----------|---|
| All pass | "✓ Ready for deployment" |
| Drawdown > 5% | "✗ Not ready. Drawdown too severe. Reduce aggressiveness." |
| Sudden collapse | "✗ Not ready. Strategy destabilizes during run. Review exits." |
| Other failure | "✗ Not ready. Review failed checks." |

---

## RESPONSE OBJECT

Added `survival` data to JSON response:

```json
{
  "status": "FAIL",
  "checks": [
    {"name": "Sample Size", "value": "50 trades", "passed": true},
    {"name": "Flip Rate", "value": "12.5%", "passed": true},
    {"name": "Max Drawdown", "value": "6.2%", "passed": false},
    {"name": "Stability Check", "value": "UNSTABLE", "passed": false}
  ],
  "reasons": [
    "Excessive drawdown (6.2% > 5.0%)",
    "Sudden equity instability detected"
  ],
  "recommendation": "✗ Not ready. Drawdown too severe. Reduce aggressiveness.",
  "survival": {
    "max_drawdown_pct": 6.2,
    "sudden_collapse": true,
    "pass": false
  }
}
```

---

## UI DISPLAY

No redesign needed. Survival checks appear as standard check items:

```
✓ Evaluation Result

Sample Size: 50 trades ✔
Flip Rate: 12.5% ✔
Avg PnL (Adjusted): 0.0050 ✔
Divergence: 8.2% ✔
Max Drawdown: 6.2% ✖
Stability Check: UNSTABLE ✖

Issues:
→ Excessive drawdown (6.2% > 5.0%)
→ Sudden equity instability detected

Recommendation:
✗ Not ready. Drawdown too severe. Reduce aggressiveness.
```

---

## DATA SOURCE

- **Equity curve:** `simulator.shadow_equity` (preferred) or `simulator.paper_equity`
- **Scope:** Current run only (no historical blending)
- **Timing:** Real-time as trading happens

---

## THRESHOLDS (EASY TO ADJUST)

```python
drawdown_threshold = 5.0        # Max acceptable drawdown (%)
sudden_drop_threshold = 2.0     # Single-step loss (% of $10k start)
```

Both are constants at top of function, easily changeable.

---

## FILES MODIFIED

| File | Changes |
|------|---------|
| `/Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py` | Added survival checks + recommendations (lines 1187-1279) |
| `/Users/rrg/.openclaw/workspace/moltmarket/templates/dashboard.html` | No changes (checks display via existing loop) |
| `/Users/rrg/.openclaw/workspace/moltmarket/static/dashboard.js` | No changes (renders all checks automatically) |

---

## BEHAVIOR AFTER PATCH

✓ Bot can PASS profitability but FAIL survival  
✓ Bot can PASS all traditional checks but FAIL on drawdown  
✓ New checks integrated into existing UI  
✓ Recommendations become survival-aware  
✓ Survival data available in API response  

---

## DOES NOT ADD

❌ VaR calculation  
❌ Sharpe ratio  
❌ Monte Carlo  
❌ New dashboard pages  
❌ Complex curve analysis  
❌ Machine learning  

**Just a practical kill switch for bots that survive in theory but blow up in practice.**

---

## READY FOR PRODUCTION

Minimal, focused, integrated into existing framework.

Evaluate Bot now answers:

1. **Is it profitable?** (profitability checks)
2. **Could it survive real money?** (survival gate)

Both must pass for PASS status.
