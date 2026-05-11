#!/usr/bin/env python3
"""
Diagnostic test: Are babies executing trades through unified pipeline?
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path.cwd()))

from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator
from evolution_engine import EvolutionEngine
from variant_nursery import VariantNursery
from nursery_reality_bridge import NurseryRealityBridge
from market_config import MarketConfig
from unified_execution_pipeline import UnifiedLedger, UnifiedExecutor, SimulatorExecutor as UnifiedSimulatorExecutor

print("[TEST] Starting baby execution diagnostic...\n")

# Initialize components
data_layer = DataLayer(workspace_dir=Path.cwd())
simulator = ExecutionSimulator(data_layer)
evolution_engine = EvolutionEngine()
nursery = VariantNursery(workspace_dir=Path.cwd(), evolution_engine=evolution_engine)
nursery_bridge = NurseryRealityBridge(simulator, data_layer)

# Market config
MarketConfig.set_active_market('coinbase')
print(f"[TEST] Active market: {MarketConfig.get_active_market()}\n")

# Unified pipeline
unified_ledger = UnifiedLedger()
unified_simulator_executor = UnifiedSimulatorExecutor(simulator)
unified_market_executors = {
    'simulator': unified_simulator_executor,
    'coinbase': unified_simulator_executor,
}
unified_executor = UnifiedExecutor(unified_market_executors, unified_ledger)
print("[TEST] Unified executor initialized\n")

# Spawn babies
print("[TEST] Spawning 5 babies...")
run_id = 'test_run_' + str(Path.cwd()).split('/')[-1]
babies = nursery.spawn_babies(run_id=run_id, count=5)
print(f"[TEST] Spawned {len(babies)} babies: {[b['variant_id'] for b in babies]}\n")

# Manually execute one baby
print("[TEST] Manually executing one baby 10 times...\n")
test_baby = babies[0]
baby_id = test_baby['variant_id']

for cycle in range(10):
    print(f"--- Cycle {cycle+1} ---")
    
    # Generate signal
    import random
    asset = random.choice(['BTC', 'ETH'])
    side = random.choice(['long', 'short'])
    entry_price = simulator._get_price(asset)
    exit_price = simulator._get_price(asset)
    
    signal = {
        'asset': asset,
        'side': side,
        'entry_price': entry_price,
        'exit_price': exit_price,
        'size': 1.0,
    }
    
    print(f"Signal: {asset} {side} (entry: ${entry_price:.2f}, exit: ${exit_price:.2f})")
    
    # Execute through unified pipeline
    trade = unified_executor.execute_signal(
        source='baby',
        trader_id=baby_id,
        signal=signal
    )
    
    if trade:
        print(f"✓ TRADE EXECUTED: ${trade.pnl:.2f} ({trade.pnl_bps:.1f} bps)")
    else:
        print(f"✗ TRADE FAILED: No trade returned")
    
    print()

# Check ledger
print("\n=== LEDGER STATE ===")
metrics = unified_ledger.get_trader_metrics(baby_id)
print(f"Baby {baby_id}:")
print(f"  Total trades: {metrics['total_trades']}")
print(f"  Total PnL: ${metrics['total_pnl']:.2f}")
print(f"  Shadow PnL: ${metrics['shadow_pnl']:.2f}")
print(f"  Win rate: {metrics['win_rate']:.1f}%")

print(f"\n=== LEDGER BREAKDOWN ===")
all_trades = unified_ledger.get_all_trades()
print(f"Total trades in ledger: {len(all_trades)}")
for i, trade in enumerate(all_trades[-5:]):
    print(f"  {i+1}. {trade['trader_id']}: {trade['asset']} {trade['side']} | ${trade['pnl']:.2f}")

if len(all_trades) == 0:
    print("\n✗ PROBLEM: No trades in ledger!")
    print("This means unified_executor.execute_signal() is not recording trades.")
else:
    print(f"\n✓ SUCCESS: {len(all_trades)} trades recorded in unified ledger!")
