#!/usr/bin/env python3
"""
DEMO: FLAT enforcement
Shows BRAIN blocking all trades during system liquidation
"""

from pathlib import Path
from dashboard_execution import ExecutionSimulator
from dashboard_data_layer import DataLayer


def demo_flat():
    print("\n" + "=" * 80)
    print("DEMO 3: FLAT ENFORCEMENT")
    print("=" * 80)
    print("\nScenario: Catastrophic drawdown → BRAIN FLAT triggered")
    print("Expected: All new trades blocked (liquidation mode)\n")
    
    # Mock BRAIN state
    brain_state = {'state': 'FLAT', 'reason_code': 'max_drawdown_exceeded',
                   'reason_text': 'Max drawdown (5%) exceeded — entering liquidation mode'}
    
    def get_brain():
        return brain_state
    
    data_layer = DataLayer(workspace_dir=Path.cwd())
    simulator = ExecutionSimulator(data_layer, brain_status_getter=get_brain)
    
    print("[ACTION] Attempting to generate 3 trades with FLAT active:\n")
    
    initial_trades = len(data_layer.get_recent_trades(limit=10000))
    
    for i in range(3):
        print(f"→ Trade attempt {i+1}:")
        simulator._generate_signal()
        print()
    
    final_trades = len(data_layer.get_recent_trades(limit=10000))
    trades = final_trades - initial_trades
    
    print("-" * 80)
    print(f"RESULT: {trades} trades executed")
    print("-" * 80)
    
    if trades == 0:
        print("\n✅ SUCCESS: FLAT blocked all trades (expected 0, got 0)")
        print("  • System in liquidation mode — no new entries")
        print("  • Existing positions can close, but no new trades")
    else:
        print(f"\n❌ FAIL: {trades} trades leaked through! System unsafe!")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    demo_flat()
