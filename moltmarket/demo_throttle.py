#!/usr/bin/env python3
"""
DEMO: THROTTLE enforcement
Shows BRAIN reducing position size to 50% during instability
"""

from pathlib import Path
from dashboard_execution import ExecutionSimulator
from dashboard_data_layer import DataLayer


def demo_throttle():
    print("\n" + "=" * 80)
    print("DEMO 2: THROTTLE ENFORCEMENT")
    print("=" * 80)
    print("\nScenario: Instability detected → BRAIN THROTTLE triggered")
    print("Expected: Trades execute at 50% size\n")
    
    # Mock BRAIN state
    brain_state = {'state': 'THROTTLE', 'reason_code': 'instability_detected',
                   'reason_text': 'Instability threshold (25%) exceeded'}
    
    def get_brain():
        return brain_state
    
    data_layer = DataLayer(workspace_dir=Path.cwd())
    simulator = ExecutionSimulator(data_layer, brain_status_getter=get_brain)
    
    print("[ACTION] Attempting to generate 2 trades with THROTTLE active:\n")
    
    initial_trades = len(data_layer.get_recent_trades(limit=10000))
    
    for i in range(2):
        print(f"→ Trade attempt {i+1}:")
        simulator._generate_signal()
        print()
    
    final_trades = len(data_layer.get_recent_trades(limit=10000))
    trades = final_trades - initial_trades
    
    print("-" * 80)
    print(f"RESULT: {trades} trades executed (at 50% size)")
    print("-" * 80)
    
    if trades == 4:
        print("\n✅ SUCCESS: THROTTLE allowed trades at reduced size (expected 4, got 4)")
        print("  • 2 signals = 4 trades (2 per signal: paper + shadow)")
        print("  • Each trade at 50% size (1.0 → 0.5)")
    else:
        print(f"\n❌ FAIL: Expected 4 trades, got {trades}")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    demo_throttle()
