# METRICS AUDIT FIX - MANUAL PATCH INSTRUCTIONS

## Quick Reference: What to Change

### Location 1: Lines ~420-444 (update_metrics function)

**Find this block:**
```python
    print("[METRIC 7] result:", round(edge_50_bps, 2), "bps")
    
    dashboard_state['metrics'] = {
        'paper_value': round(paper_pnl, 2),
        'shadow_value': round(shadow_pnl, 2),
        'paper_shadow_delta_pct': round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2),
        'backtest_edge_bps': round(data_layer.get_backtest_edge(), 2),
```

**Replace with:**
```python
    print("[METRIC 7] result:", round(edge_50_bps, 2), "bps")
    
    # CORRECTED METRICS: Three-tier system (TIER 1: $, TIER 2: %, TIER 3: bps)
    paper_return_pct = (paper_pnl / 10000.0) * 100
    shadow_return_pct = (shadow_pnl / 10000.0) * 100
    delta_return_pct = paper_return_pct - shadow_return_pct
    
    dashboard_state['metrics'] = {
        # TIER 1: RAW DOLLARS
        'paper_pnl_dollars': round(paper_pnl, 2),
        'shadow_pnl_dollars': round(shadow_pnl, 2),
        'delta_pnl_dollars': round(paper_pnl - shadow_pnl, 2),
        # TIER 2: % RETURN (normalized to 10k initial capital)
        'paper_return_pct': round(paper_return_pct, 3),
        'shadow_return_pct': round(shadow_return_pct, 3),
        'delta_return_pct': round(delta_return_pct, 3),
        'backtest_edge_bps': round(data_layer.get_backtest_edge(), 2),
```

---

### Location 2: Lines ~462 (divergence calculation)

**Find this line:**
```python
    dashboard_state['divergence'] = round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2)
```

**Replace with:**
```python
    dashboard_state['divergence'] = round(delta_return_pct, 3)  # CORRECTED: uses TIER 2 calculation
```

---

## Verification

After making changes, restart dashboard and verify:

```
✓ paper_pnl_dollars: Shows raw $ (e.g., 125.47)
✓ paper_return_pct: Shows % return (e.g., 1.2547%)
✓ rolling_edge_20_bps: Shows basis points (e.g., 18.5)
✓ rolling_edge_50_bps: Shows basis points (e.g., 22.3)
✓ delta_return_pct: Shows correct % difference
✓ divergence: Matches delta_return_pct (no abs() trick)
```

---

## Why These Fixes Matter

**Before:**
- Metrics confuse $ and %
- Edge calculations ignore trade size
- Negative PnL hides behind `abs()`

**After:**
- Clear three-tier system: $ | % | bps
- Edge normalized to notional
- Negative returns show correctly

---

## Files Generated

- `METRICS_AUDIT_RESULTS.md` — Full audit report
- `metrics_audit_fix.py` — Reference implementation
- `update_metrics_corrected.py` — Corrected function (standalone)
- This file — Manual patch instructions

---

## Alternative: Use Corrected Function

If manual patching is tedious, you can:

1. Copy `update_metrics_corrected()` from `update_metrics_corrected.py`
2. Replace the current `update_metrics()` in dashboard with the corrected version
3. Restart dashboard

Both approaches achieve the same result.
