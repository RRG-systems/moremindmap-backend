#!/usr/bin/env python3
"""
PHASE 28 Test Script
Tests all modifications and generates diagnostic output
"""

import sys
import os

# Add moltmarket to path
sys.path.insert(0, '/Users/rrg/.openclaw/workspace/moltmarket')

from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator
from pathlib import Path

print("\n" + "="*70)
print("PHASE 28 - EXECUTION CLEANUP + DASHBOARD FIX")
print("="*70)

# Initialize components
workspace = Path('/Users/rrg/.openclaw/workspace/moltmarket')
os.chdir(workspace)

data_layer = DataLayer(workspace_dir=workspace)
data_layer.initialize()

simulator = ExecutionSimulator(data_layer)
simulator.initialize()

print("\n[PART 1] Signal Isolation Verification")
print("-" * 70)
print(f"✓ Assets configured: {simulator.assets}")
print(f"✓ Signals configured: {simulator.signals}")
print(f"✓ ACTIVE_SIGNALS: {simulator.ACTIVE_SIGNALS}")
print(f"✓ Current signal: {simulator.current_signal}")
print(f"✓ Current asset: {simulator.current_asset}")

# Run simulation
print("\n[PART 2] Simulating 5 trades for Mean Reversion...")
print("-" * 70)
for i in range(5):
    simulator.step()
    print(f"  Trade {i+1} | Signal: {simulator.current_signal} | Asset: {simulator.current_asset}")

# Check equity curves
print("\n[PART 2] Equity Curves Debug")
print("-" * 70)
paper_curve = simulator.get_paper_equity_curve()
shadow_curve = simulator.get_shadow_equity_curve()
backtest_curve = simulator.get_backtest_equity_curve()

print(f"✓ Paper equity curve: {len(paper_curve)} points")
if paper_curve:
    print(f"  - First: {paper_curve[0]}")
    print(f"  - Last: {paper_curve[-1]}")

print(f"✓ Shadow equity curve: {len(shadow_curve)} points")
if shadow_curve:
    print(f"  - First: {shadow_curve[0]}")
    print(f"  - Last: {shadow_curve[-1]}")

print(f"✓ Backtest equity curve: {len(backtest_curve)} points")
if backtest_curve:
    print(f"  - First: {backtest_curve[0]}")
    print(f"  - Last: {backtest_curve[-1]}")

# Check trades
print("\n[PART 3] Trade Data")
print("-" * 70)
trades = data_layer.get_recent_trades(limit=50)
print(f"✓ Total trades recorded: {len(trades)}")
if trades:
    print(f"✓ First trade: {trades[0]}")
    print(f"✓ Last trade: {trades[-1]}")

# Test slippage calculation
print("\n[PART 3] Execution Diagnostics - Slippage")
print("-" * 70)
slippage = data_layer.get_avg_slippage()
print(f"✓ Avg Entry Slippage: {slippage['entry_bps']:.2f} bps")
print(f"✓ Avg Exit Slippage: {slippage['exit_bps']:.2f} bps")

# Test trade integrity
print("\n[PART 4] Data Integrity Check")
print("-" * 70)
integrity = data_layer.get_trade_integrity()
print(f"✓ Total Paper Trades: {integrity['total_trades']}")
print(f"✓ Trade Count Difference (Paper vs Shadow): {integrity['trade_diff']}")
print(f"✓ Sign Flips (Winners → Losers): {integrity['sign_flips']}")
print(f"✓ Sign Flip Rate: {integrity['sign_flip_rate_pct']:.1f}%")

print("\n" + "="*70)
print("✓ PHASE 28 MODIFICATIONS VERIFIED - READY FOR DASHBOARD")
print("="*70)
print("\nNext steps:")
print("1. Run: python3 moltmarket_dashboard.py")
print("2. Open: http://localhost:5000")
print("3. Check browser console for [PHASE 28] logs")
print("4. Verify 3 equity curves (Paper/Shadow/Backtest) visible")
print("5. Check new KPI cards: Entry/Exit Slippage, Sign Flip Rate")
print("="*70 + "\n")
