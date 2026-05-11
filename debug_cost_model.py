#!/usr/bin/env python3
"""Debug: Show what's happening with costs"""

import numpy as np

# Phase 18 baseline edge
phase18_pnl_per_trade = 0.00776  # dollars per trade
phase18_win_rate = 53.6  # percent
phase18_avg_per_win = phase18_pnl_per_trade / (phase18_win_rate / 100) if phase18_win_rate > 0 else 0

print("="*70)
print("PROBLEM ANALYSIS: Why is win rate 0% after costs?")
print("="*70)

print("\nPhase 18 Baseline (Frictionless Simulation):")
print(f"  Win rate: {phase18_win_rate}%")
print(f"  PnL/trade: ${phase18_pnl_per_trade:.5f}")
print(f"  Implied avg win: ${phase18_avg_per_win:.5f}" if phase18_avg_per_win > 0 else "  N/A")

print("\nTrade Mechanics (Phase 18):")
print("  Position size: $5")
print("  Target exit: +2.0% = $0.10")
print("  Stop loss: -2.0% = -$0.10")
print("  Average win (rough): $0.10")
print("  Average loss (rough): -$0.10")

print("\nWith 53.6% win rate:")
win_pct = 0.536
loss_pct = 1 - win_pct
avg_win = 0.10
avg_loss = -0.10
expected_pnl_frictionless = win_pct * avg_win + loss_pct * avg_loss
print(f"  E[PnL] = {win_pct:.1%} × ${avg_win:.2f} + {loss_pct:.1%} × ${avg_loss:.2f}")
print(f"  E[PnL] = ${expected_pnl_frictionless:.5f} per trade")

print("\n" + "="*70)
print("NOW: Apply Realistic Costs")
print("="*70)

# Cost model
entry_cost_pct = 0.016  # 1.6% (spread + slippage + fee)
exit_cost_pct = 0.016   # 1.6%
total_cost_pct = entry_cost_pct + exit_cost_pct

print(f"\nCosts on $5 trade:")
print(f"  Entry cost: 1.6% × $5 = ${entry_cost_pct * 5:.3f}")
print(f"  Exit cost: 1.6% × $5 = ${exit_cost_pct * 5:.3f}")
print(f"  Total round-trip: 3.2% = ${total_cost_pct * 5:.3f}")

print(f"\nAfter costs (winning trade scenario):")
print(f"  Gross entry: $5.00")
print(f"  Entry cost: -${entry_cost_pct * 5:.3f}")
print(f"  Net position: ${5 - entry_cost_pct * 5:.3f}")

print(f"\n  Target exit price: +2% = $5.10")
print(f"  Exit at: $5.10")
print(f"  Exit cost: 1.6% × $5.10 = ${exit_cost_pct * 5.10:.3f}")
print(f"  Net proceeds: ${5.10 - exit_cost_pct * 5.10:.3f}")

entry_net = 5.0 - (entry_cost_pct * 5)
exit_gross = 5.0 * 1.02
exit_net = exit_gross - (exit_cost_pct * exit_gross)
winning_trade_net_pnl = exit_net - entry_net

print(f"\n  PnL per winning trade: ${winning_trade_net_pnl:.5f}")
print(f"  Win before costs: +$0.10")
print(f"  Win after costs: ${winning_trade_net_pnl:.5f}")
print(f"  Cost erosion: ${0.10 - winning_trade_net_pnl:.5f} (NEGATIVE!)")

print(f"\n  ⚠️  PROBLEM: Costs ({total_cost_pct*100:.1f}%) > Target ({2.0:.1f}%)")
print(f"  Even winners don't win after costs!")

print("\n" + "="*70)
print("ROOT CAUSE")
print("="*70)

print(f"""
The issue is FUNDAMENTAL:

1. Phase 18 used ±2% target/stop (symmetric)
2. With 53.6% win rate, EV ≈ +0.16% per trade
3. That's only 0.16% margin = 16 basis points
4. Realistic costs (320 bps round-trip) = 3.2%
5. 3.2% >> 0.16% → costs kill any profit

CRITICAL INSIGHT:
The edge is TOO THIN to survive real market costs.

The signal works (52-53% win rate), but:
- It only wins by 2% per winner
- It loses by 2% per loser
- With 53.6% win rate: EV = (53.6% × 2%) - (46.4% × 2%) = 0.144%
- This is only 14.4 basis points per trade
- Costs are 320 basis points (22× larger!)

SOLUTION: Need ±3-5% target/stop, not ±2%
""")

print("Testing higher targets:")
for target_pct in [2.0, 3.0, 4.0, 5.0]:
    gross_win = target_pct / 100 * 5
    net_win = gross_win - (total_cost_pct * (5 + gross_win / 2))  # Rough
    net_ev = 0.536 * net_win - 0.464 * (total_cost_pct * 5)
    print(f"  {target_pct}% target: approx EV ${net_ev:.5f}")
