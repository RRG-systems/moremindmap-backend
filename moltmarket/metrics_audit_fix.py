#!/usr/bin/env python3
"""
METRICS AUDIT FIX
Three-tier metrics: RAW $ | % RETURN | BPS EDGE

All clearly separated and correctly normalized.
"""

# CONSTANTS
INITIAL_CAPITAL = 10000.0  # Standard starting capital for simulator

def audit_metrics_calculation():
    """Corrected metrics with full audit trail"""
    
    # TIER 1: RAW DOLLAR PnL
    print("\n" + "="*80)
    print("TIER 1: RAW DOLLAR PnL (ABSOLUTE)")
    print("="*80)
    
    paper_pnl_dollars = 125.47  # Raw dollars
    shadow_pnl_dollars = 89.32  # Raw dollars
    
    print(f"paper_pnl_dollars: ${paper_pnl_dollars:.2f}")
    print(f"shadow_pnl_dollars: ${shadow_pnl_dollars:.2f}")
    print(f"delta_dollars: ${paper_pnl_dollars - shadow_pnl_dollars:.2f}")
    
    # TIER 2: % RETURN (normalized to initial capital)
    print("\n" + "="*80)
    print("TIER 2: % RETURN (normalized to initial capital)")
    print("="*80)
    
    paper_return_pct = (paper_pnl_dollars / INITIAL_CAPITAL) * 100
    shadow_return_pct = (shadow_pnl_dollars / INITIAL_CAPITAL) * 100
    
    print(f"Initial capital: ${INITIAL_CAPITAL:.2f}")
    print(f"paper_return_pct: {paper_return_pct:.3f}%")
    print(f"shadow_return_pct: {shadow_return_pct:.3f}%")
    
    # BUG FIX: Don't use abs() — use consistent denominator
    delta_return_pct = paper_return_pct - shadow_return_pct
    print(f"delta_return_pct: {delta_return_pct:.3f}% (paper vs shadow)")
    
    # TIER 3: BPS EDGE (normalized to notional, not count)
    print("\n" + "="*80)
    print("TIER 3: BPS EDGE (normalized to notional)")
    print("="*80)
    
    # Example: 20 trades with varying notional
    trades_20 = [
        {'pnl': 10.0, 'notional': 77000},   # BTC: $10 on $77k
        {'pnl': 1.0, 'notional': 2375},    # ETH: $1 on $2.3k
        {'pnl': 5.0, 'notional': 50000},   # Large
        {'pnl': -2.0, 'notional': 25000},  # Loss
        # ... etc, 20 total
    ]
    
    print(f"\nExample: {len(trades_20)} trades")
    
    # WRONG WAY (current code):
    total_pnl_wrong = sum(t['pnl'] for t in trades_20)
    avg_pnl_wrong = total_pnl_wrong / len(trades_20)
    edge_bps_wrong = avg_pnl_wrong * 10000  # BUG: assumes $1 per trade
    print(f"\n❌ WRONG METHOD:")
    print(f"   total_pnl: ${total_pnl_wrong:.2f}")
    print(f"   avg_pnl: ${avg_pnl_wrong:.2f}")
    print(f"   edge_bps: {edge_bps_wrong:.0f} bps")
    print(f"   PROBLEM: Treats all trades equally, ignores size")
    
    # RIGHT WAY: normalize to notional
    total_return = sum(t['pnl'] / t['notional'] for t in trades_20)
    avg_return = total_return / len(trades_20)
    edge_bps_right = avg_return * 10000
    print(f"\n✓ RIGHT METHOD:")
    print(f"   total_return (notional-weighted): {total_return:.6f}")
    print(f"   avg_return: {avg_return:.6f}")
    print(f"   edge_bps: {edge_bps_right:.2f} bps")
    print(f"   CORRECT: Each trade normalized to its size")
    
    # TIER 3B: Alternative — edge as % of capital deployed
    print(f"\n✓ ALTERNATIVE: Edge as % of capital deployed")
    total_notional = sum(t['notional'] for t in trades_20)
    avg_notional = total_notional / len(trades_20)
    capital_ratio = avg_notional / INITIAL_CAPITAL
    edge_pct_of_capital = avg_return * 100
    print(f"   avg_notional_per_trade: ${avg_notional:.2f}")
    print(f"   capital_deployed: {capital_ratio:.1f}x initial")
    print(f"   edge_pct_of_capital: {edge_pct_of_capital:.4f}%")
    print(f"   edge_bps_of_capital: {edge_pct_of_capital * 100:.2f} bps")


def corrected_metrics_dict():
    """What the corrected metrics dict should look like"""
    
    print("\n" + "="*80)
    print("CORRECTED METRICS DICTIONARY")
    print("="*80)
    
    corrected = {
        # TIER 1: RAW DOLLARS
        'paper_pnl_dollars': 125.47,
        'shadow_pnl_dollars': 89.32,
        'backtest_pnl_dollars': 156.23,
        'delta_pnl_dollars': 36.15,  # paper - shadow
        
        # TIER 2: % RETURN
        'paper_return_pct': 1.2547,  # (125.47 / 10000) * 100
        'shadow_return_pct': 0.8932,  # (89.32 / 10000) * 100
        'backtest_return_pct': 1.5623,
        'delta_return_pct': 0.3615,  # paper - shadow, NOT delta of %, but delta THEN %
        
        # TIER 3: BPS EDGE (20-trade rolling)
        'rolling_edge_20_bps': 18.5,  # avg_pnl_per_$notional * 10000
        'rolling_edge_50_bps': 22.3,
        
        # TIER 4: Win rate (separate concept)
        'rolling_win_rate_20': 65.0,  # % of winning trades
        'rolling_win_rate_50': 58.0,
        
        # TIER 5: Risk metrics
        'rolling_max_drawdown_50': 145.23,  # raw dollars
        'rolling_max_drawdown_50_pct': 1.4523,  # as % of capital
    }
    
    print("\nDo NOT mix these:")
    print("  ❌ 'value': 125.47 (is this $ or %?)")
    print("  ✓ 'pnl_dollars': 125.47")
    print("  ✓ 'return_pct': 1.2547")
    print()
    print("Do NOT mix denominators:")
    print("  ❌ edge_bps = avg_pnl * 10000 (assumes $1 per trade)")
    print("  ✓ edge_bps = avg_return_pct * 100 (notional-normalized)")
    print()
    print("Do NOT use abs() when calculating deltas:")
    print("  ❌ delta_pct = (shadow - paper) / abs(paper) * 100")
    print("  ✓ delta_pct = (shadow_return_pct) - (paper_return_pct)")
    
    return corrected


if __name__ == '__main__':
    audit_metrics_calculation()
    corrected = corrected_metrics_dict()
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    print("""
THREE TIERS (ALWAYS SEPARATE):

1. RAW DOLLARS (paper_pnl_dollars, shadow_pnl_dollars)
   - Absolute $$ gained/lost
   - Units: $USD
   
2. % RETURN (paper_return_pct, shadow_return_pct)
   - Normalized to initial capital
   - Units: %
   - Formula: (pnl_dollars / initial_capital) * 100
   
3. BPS EDGE (rolling_edge_20_bps, rolling_edge_50_bps)
   - Normalized to notional per trade
   - Units: basis points (0.01%)
   - Formula: (avg_pnl / avg_notional) * 10000

NEVER:
  - Mix $ and % in same metric name
  - Use abs() for delta calculations
  - Calculate edge_bps from raw_pnl without notional normalization
""")
