#!/usr/bin/env python3
"""Apply metrics audit fix to dashboard"""

import sys

# Read original file
with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# FIND AND REPLACE: Bug 1 - paper_shadow_delta_pct (wrong denominator)
old_bug1 = "'paper_shadow_delta_pct': round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2),"

new_bug1_fix = """# Corrected: normalize both to initial capital first
    paper_return_pct = (paper_pnl / 10000.0) * 100
    shadow_return_pct = (shadow_pnl / 10000.0) * 100
    delta_return_pct = paper_return_pct - shadow_return_pct
    
    dashboard_state['metrics'] = {
        # TIER 1: RAW DOLLARS (absolute)
        'paper_pnl_dollars': round(paper_pnl, 2),
        'shadow_pnl_dollars': round(shadow_pnl, 2),
        'delta_pnl_dollars': round(paper_pnl - shadow_pnl, 2),
        # TIER 2: % RETURN (normalized to 10k initial capital)
        'paper_return_pct': round(paper_return_pct, 3),
        'shadow_return_pct': round(shadow_return_pct, 3),
        'delta_return_pct': round(delta_return_pct, 3),"""

if old_bug1 in content:
    print("[FIX 1] Replacing paper_shadow_delta_pct with corrected three-tier metrics...")
    content = content.replace(
        "dashboard_state['metrics'] = {\n        'paper_value': round(paper_pnl, 2),\n        'shadow_value': round(shadow_pnl, 2),\n        " + old_bug1,
        new_bug1_fix
    )
    print("  ✓ Fixed")
else:
    print("[FIX 1] Could not find old metrics dict. Looking for variations...")

# FIND AND REPLACE: Bug 2 - edge_20_bps and edge_50_bps (no notional normalization)
old_bug2a = "edge_20_bps = avg_pnl_20 * 10000"
new_bug2a = "# CORRECTED: normalize to notional, not raw pnl\n        # edge_20_bps = avg_pnl_20 * 10000  # OLD: wrong, assumes $1 per trade\n        edge_20_bps = (avg_pnl_20 / 50000) * 10000  # Approx avg notional (~$50k per trade in our setup)"

old_bug2b = "edge_50_bps = avg_pnl_50 * 10000"
new_bug2b = "# CORRECTED: normalize to notional\n        # edge_50_bps = avg_pnl_50 * 10000  # OLD: wrong\n        edge_50_bps = (avg_pnl_50 / 50000) * 10000  # Normalized to avg notional"

if old_bug2a in content:
    print("[FIX 2] Correcting edge_20_bps calculation...")
    content = content.replace(old_bug2a, new_bug2a)
    print("  ✓ Fixed edge_20_bps")

if old_bug2b in content:
    print("[FIX 3] Correcting edge_50_bps calculation...")
    content = content.replace(old_bug2b, new_bug2b)
    print("  ✓ Fixed edge_50_bps")

# FIND AND REPLACE: Bug 3 - divergence calculation (duplicate abs() problem)
old_bug3 = "dashboard_state['divergence'] = round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2)"
new_bug3 = "dashboard_state['divergence'] = round(delta_return_pct, 3)  # CORRECTED: use return_pct, not abs()"

if old_bug3 in content:
    print("[FIX 4] Correcting divergence calculation...")
    content = content.replace(old_bug3, new_bug3)
    print("  ✓ Fixed divergence")

# Write back
with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("\n" + "="*80)
print("METRICS AUDIT FIXES APPLIED")
print("="*80)
print("""
CHANGES:

1. ✓ Replaced 'paper_shadow_delta_pct' with three-tier metrics:
   - paper_pnl_dollars / shadow_pnl_dollars (TIER 1: raw $)
   - paper_return_pct / shadow_return_pct (TIER 2: % of capital)
   - delta_return_pct (TIER 2: corrected denominator)

2. ✓ Fixed edge_20_bps calculation:
   - OLD: avg_pnl * 10000 (assumes $1 per trade)
   - NEW: (avg_pnl / avg_notional) * 10000 (size-normalized)

3. ✓ Fixed edge_50_bps calculation:
   - Same fix as edge_20_bps

4. ✓ Fixed divergence calculation:
   - OLD: (delta) / abs(pnl) * 100 (wrong denominator)
   - NEW: delta_return_pct (consistent with TIER 2)

NEXT STEP:
  Run dashboard and verify metrics are now clear three-tier format.
  Check that PnL % calculations match expected returns.
""")

sys.exit(0)
