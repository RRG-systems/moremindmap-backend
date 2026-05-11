# METRICS SANITY PASS — COMPLETE AUDIT

**Date:** 2026-04-21 21:09 MST  
**Status:** AUDIT COMPLETE + FIX READY  
**Goal:** Separate dollars, percent returns, and bps cleanly  

---

## Summary: Three Output Paths Audited

| Path | Files | Status | Issues Found |
|------|-------|--------|--------------|
| **Terminal Logs** | moltmarket_dashboard.py | 🔴 BROKEN | Uses `abs()`, mixes $ and % |
| **Dashboard API** | moltmarket_dashboard.py | 🔴 BROKEN | Same issues |
| **Nursery CSV** | variant_nursery.py | 🟡 PARTIAL | Has `paper_pnl`, `shadow_pnl` but no return % |
| **THINK Summaries** | think_diagnostic_layer.py | 🟢 OK | Uses `pnl_pct` correctly |

---

## Critical Issues Found

### Issue 1: Lines 440-442 in moltmarket_dashboard.py

**Current (BROKEN):**
```python
'paper_value': round(paper_pnl, 2),
'shadow_value': round(shadow_pnl, 2),
'paper_shadow_delta_pct': round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2),
```

**Problems:**
1. Field name `paper_value` unclear (is it $ or %?)
2. Uses `abs()` — breaks when paper_pnl is negative
3. Mixes raw dollars with percentage calculation
4. No separate `paper_return_pct` field

**Fixed:**
```python
# TIER 1: RAW DOLLARS
'paper_pnl_dollars': round(paper_pnl, 2),
'shadow_pnl_dollars': round(shadow_pnl, 2),
'delta_pnl_dollars': round(paper_pnl - shadow_pnl, 2),
# TIER 2: % RETURN (normalized to 10k initial capital)
'paper_return_pct': round((paper_pnl / 10000.0) * 100, 3),
'shadow_return_pct': round((shadow_pnl / 10000.0) * 100, 3),
'delta_return_pct': round(((paper_pnl / 10000.0) - (shadow_pnl / 10000.0)) * 100, 3),
```

---

### Issue 2: Line 475 in moltmarket_dashboard.py

**Current (BROKEN):**
```python
dashboard_state['divergence'] = round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2)
```

**Problem:** Same `abs()` issue, inconsistent with TIER 2

**Fixed:**
```python
dashboard_state['divergence'] = round(delta_return_pct, 3)  # Use TIER 2
```

---

### Issue 3: Lines 543-583 in moltmarket_dashboard.py (Baby Execution)

**Current:**
```python
paper_pnl = (paper_exit_fill - paper_entry_fill) / paper_entry_fill * 10000
# ... later ...
state['paper_pnl'] += paper_pnl  # Accumulating basis points?
new_paper_equity = 10000.0 + state['paper_pnl']  # Mixing $ and bps
```

**Problem:** Mixing basis points (from return calc) with dollar equity calculation

**Fixed:** Keep baby PnL in dollars consistently:
```python
paper_pnl_dollars = (paper_exit_fill - paper_entry_fill)
state['paper_pnl'] += paper_pnl_dollars  # In dollars
new_paper_equity = 10000.0 + state['paper_pnl']  # Now correct
```

---

### Issue 4: Lines 631 in moltmarket_dashboard.py (Degradation Calc)

**Current:**
```python
degradation = (paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100
```

**Problem:** Uses `abs()`, inconsistent units

**Fixed:**
```python
degradation_pct = ((paper_pnl - shadow_pnl) / shadow_pnl) * 100 if shadow_pnl != 0 else 0
```

---

### Issue 5: variant_nursery.py CSV Headers

**Current:** Has `paper_pnl` and `shadow_pnl` but no return %

**Need to add:**
- `paper_return_pct` (for tracking scaling)
- `shadow_return_pct` (for comparing execution)

---

### Issue 6: Edge calculation (Lines 399-424)

**Current:**
```python
edge_20_bps = avg_pnl_20 * 10000  # Assumes $1 per trade
```

**Problem:** No notional normalization

**Fixed:** (Already documented in METRICS_AUDIT_RESULTS.md)
```python
edge_20_bps = (avg_return / len(trades)) * 10000  # Properly normalized
```

---

## Complete Fix Checklist

### Dashboard metrics dict (Lines 440-475)
- [ ] Replace `paper_value` → `paper_pnl_dollars`
- [ ] Replace `shadow_value` → `shadow_pnl_dollars`
- [ ] Add `delta_pnl_dollars`
- [ ] Replace `paper_shadow_delta_pct` → `paper_return_pct`, `shadow_return_pct`, `delta_return_pct`
- [ ] Fix `divergence` to use `delta_return_pct`

### Baby execution (Lines 543-587)
- [ ] Verify baby PnL stays in dollars (not bps)
- [ ] Verify equity calculation: 10000 + pnl_dollars (not pnl_bps)

### Degradation calc (Line 631)
- [ ] Remove `abs()` trick
- [ ] Use consistent denominator

### Edge calculations (Lines 399-424)
- [ ] Add notional normalization to edge_20_bps
- [ ] Add notional normalization to edge_50_bps

### Nursery CSV (variant_nursery.py)
- [ ] Add `paper_return_pct` column
- [ ] Add `shadow_return_pct` column
- [ ] Update write logic to calculate return %

### THINK layer (think_diagnostic_layer.py)
- [ ] Verify uses `pnl_pct = (pnl / start_equity) * 100` ✓ (already correct)

---

## Final Output Format

**Terminal logs should show:**
```
[CYCLE 50] BTC: $77,600 | Trades: 25 | PnL: $145.67 (1.457%) | Edge: 18.5 bps
```

**Dashboard API should return:**
```json
{
  "paper_pnl_dollars": 145.67,
  "paper_return_pct": 1.457,
  "rolling_edge_20_bps": 18.5,
  "shadow_pnl_dollars": 98.34,
  "shadow_return_pct": 0.983,
  "delta_return_pct": 0.474,
  "divergence": 0.474
}
```

**Nursery CSV should have:**
```
run_id,variant_id,...,paper_pnl,paper_return_pct,shadow_pnl,shadow_return_pct,...
```

**THINK summary should say:**
```
P&L: $145.67 (+1.457%) | Trades: 25 | Edge: 18.5 bps
```

---

## Implementation Order

1. **Priority 1 (Breaking):** Fix dashboard metrics dict (Issue 1)
2. **Priority 1 (Breaking):** Fix divergence (Issue 2)
3. **Priority 2 (Correctness):** Fix baby PnL units (Issue 3)
4. **Priority 2 (Correctness):** Fix degradation calc (Issue 4)
5. **Priority 3 (Enhancement):** Add return % to nursery CSV (Issue 5)
6. **Priority 3 (Enhancement):** Fix edge normalization (Issue 6)

---

## Testing

After fixes applied:

```bash
# Start dashboard
python3 moltmarket_dashboard.py

# Watch for 30 minutes
# Verify in terminal output:
✓ PnL shows as $ (e.g., $125.47)
✓ Return % shows separately (e.g., 1.2547%)
✓ Edge shows in bps (e.g., 18.5)
✓ All three units distinct

# Check API at http://localhost:5050/api/metrics
✓ paper_pnl_dollars vs paper_return_pct clearly separated
✓ No field name ambiguity

# Check nursery CSV
✓ Has paper_return_pct column
✓ Values match dashboard calculations
```

---

## Sign-off

**Audit Status:** ✓ COMPLETE  
**Issues Found:** 6  
**Severity:** 3 HIGH, 2 MEDIUM, 1 LOW  
**Fix Complexity:** MODERATE  
**Estimated Time:** 30 minutes manual patching  

Ready to apply fixes? Y/N

