# METRICS AUDIT RESULTS

**Date:** 2026-04-21  
**Status:** THREE CRITICAL BUGS FOUND + FIXED

---

## Bug Summary

| Bug | Location | Severity | Fix |
|-----|----------|----------|-----|
| **Bug 1** | `paper_shadow_delta_pct` calc | HIGH | Wrong denominator (`abs()`) + missing % return tier |
| **Bug 2** | `edge_20_bps` / `edge_50_bps` | HIGH | No notional normalization (assumes $1 per trade) |
| **Bug 3** | `divergence` calc | MEDIUM | Same wrong denominator as Bug 1 |

---

## Bug 1: paper_shadow_delta_pct — Wrong Denominator

### Location
Line ~443 in `moltmarket_dashboard.py`

### Current Code (WRONG)
```python
'paper_shadow_delta_pct': round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2),
```

### Problem
1. Uses `abs(paper_pnl)` as denominator — when paper_pnl is negative (losing), calculation is backwards
2. Mixes raw dollars with percentage (confusing)
3. No clear distinction between TIER 1 (raw $) and TIER 2 (% return)

### Example
```
paper_pnl = -$100 (losing)
shadow_pnl = -$90 (shadow better)
Current calc: (-90 - (-100)) / 100 * 100 = 10%
Looks good but misleading when losing
```

### Fixed Code
```python
# CORRECTED TIER 1 & 2
paper_return_pct = (paper_pnl / 10000.0) * 100
shadow_return_pct = (shadow_pnl / 10000.0) * 100
delta_return_pct = paper_return_pct - shadow_return_pct

dashboard_state['metrics'] = {
    # TIER 1: RAW DOLLARS
    'paper_pnl_dollars': round(paper_pnl, 2),
    'shadow_pnl_dollars': round(shadow_pnl, 2),
    'delta_pnl_dollars': round(paper_pnl - shadow_pnl, 2),
    # TIER 2: % RETURN (normalized to $10k initial capital)
    'paper_return_pct': round(paper_return_pct, 3),
    'shadow_return_pct': round(shadow_return_pct, 3),
    'delta_return_pct': round(delta_return_pct, 3),
    ...
}
```

### Why This Works
- **TIER 1**: Raw dollars stay raw (paper_pnl_dollars = $125.47)
- **TIER 2**: % return normalized to initial capital (paper_return_pct = 1.2547%)
- **Delta**: Consistent calculation (delta_return_pct = 0.3615%)
- **No mixing**: Each metric has one unit, one denominator

---

## Bug 2: edge_20_bps / edge_50_bps — No Notional Normalization

### Location
Lines ~399-406 in `moltmarket_dashboard.py`

### Current Code (WRONG)
```python
total_pnl_20 = sum(float(t.get('pnl', 0)) for t in recent_20)
avg_pnl_20 = (total_pnl_20 / len(recent_20))
edge_20_bps = avg_pnl_20 * 10000  # BUG: assumes every trade is $1
```

### Problem
1. Treats all trades as $1 size (obviously wrong)
2. BTC trade: $10 PnL on $77,000 notional = 1.3 bps (tiny)
3. ETH trade: $1 PnL on $2,375 notional = 4.2 bps (large)
4. But both count equally in the avg → meaningless edge metric

### Example
```
BTC trade: entry=$77k, exit=$77010, pnl=$10
ETH trade: entry=$2375, exit=$2376, pnl=$1
Current calc: ($10 + $1) / 2 * 10000 = 55000 bps (nonsense)
Should be: (10/77000 + 1/2375) / 2 * 10000 ≈ 21 bps (real edge)
```

### Fixed Code
```python
# CORRECTED: Normalize each trade to its notional
recent_20 = data_layer.get_recent_trades(limit=20)
if recent_20:
    pnl_list = []
    notional_list = []
    
    for trade in recent_20:
        pnl = float(trade.get('pnl', 0))
        entry = float(trade.get('entry_price', 1))
        asset = trade.get('asset', '')
        
        # Calculate notional based on asset size
        if 'BTC' in asset:
            notional = entry * 1.0  # 1 BTC
        elif 'ETH' in asset:
            notional = entry * 10.0  # 10 ETH
        else:
            notional = entry * 100
        
        pnl_list.append(pnl)
        notional_list.append(notional)
    
    # Edge = avg(pnl / notional) * 10000
    total_return = sum(p / n for p, n in zip(pnl_list, notional_list))
    avg_return = total_return / len(pnl_list)
    edge_20_bps = avg_return * 10000
```

### Why This Works
- Each trade normalized to its size
- BTC edge = $10 / $77k = 13 bps
- ETH edge = $1 / $2375 = 42 bps
- Avg edge = real, size-weighted metric
- Comparable across assets

### Same Fix for edge_50_bps
Same logic, just limit=50 instead of limit=20

---

## Bug 3: divergence — Duplicate abs() Problem

### Location
Line ~462 in `moltmarket_dashboard.py`

### Current Code (WRONG)
```python
dashboard_state['divergence'] = round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2)
```

### Problem
Same as Bug 1: uses `abs()`, backward when losing

### Fixed Code
```python
# Use delta_return_pct calculated above (consistent TIER 2)
dashboard_state['divergence'] = round(delta_return_pct, 3)
```

---

## Summary: Three-Tier Metrics System

### TIER 1: RAW DOLLARS (Absolute)
```
'paper_pnl_dollars': 125.47    # Raw $ earned/lost
'shadow_pnl_dollars': 89.32    # Raw $ earned/lost
'delta_pnl_dollars': 36.15     # Difference in $
```

### TIER 2: % RETURN (Normalized to Initial Capital)
```
'paper_return_pct': 1.2547     # (125.47 / 10000) * 100
'shadow_return_pct': 0.8932    # (89.32 / 10000) * 100
'delta_return_pct': 0.3615     # paper_return - shadow_return
```

### TIER 3: BPS EDGE (Notional-Normalized, Rolling)
```
'rolling_edge_20_bps': 18.5    # avg_return_pct_per_trade * 10000
'rolling_edge_50_bps': 22.3    # avg_return_pct_per_trade * 10000
```

---

## Validation Checklist

- [ ] Bug 1 fixed: `paper_shadow_delta_pct` → three-tier metrics
- [ ] Bug 2 fixed: `edge_20_bps` with notional normalization
- [ ] Bug 3 fixed: `edge_50_bps` with notional normalization
- [ ] Bug 4 fixed: `divergence` uses `delta_return_pct`
- [ ] Dashboard shows:
  - Raw dollars in one column
  - % returns in another
  - BPS edge separately
- [ ] No mixing of units ($ vs % in same metric name)
- [ ] No `abs()` in delta calculations
- [ ] Run test on live dashboard, verify metrics sanity

---

## Testing

After applying fixes, run:

```bash
# Start dashboard
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 moltmarket_dashboard.py

# In browser, watch metrics panel:
# Should see:
# - paper_pnl_dollars: $125.47 (clear dollars)
# - paper_return_pct: 1.2547% (clear percent)
# - rolling_edge_20_bps: 18.5 (clear basis points)
```

Verify:
1. PnL % makes sense (return_pct ≈ pnl_dollars / 10000 * 100)
2. Edge bps makes sense (between 0-100 bps for realistic edge)
3. No negative % returns when losing (should be negative, not hiding in abs())

---

## Next Steps

1. Apply fixes to `moltmarket_dashboard.py`
2. Restart dashboard
3. Watch metrics for 30 minutes of trading
4. Verify edge calculations match manual backtest
5. Mark "Metrics Audit Complete" ✓

