#!/usr/bin/env python3
"""
DEMO: STOP enforcement
Shows BRAIN blocking trades when daily loss limit hit
"""

from pathlib import Path
from dashboard_execution import ExecutionSimulator
from dashboard_data_layer import DataLayer


def demo_stop():
    print("\n" + "=" * 80)
    print("DEMO 1: STOP ENFORCEMENT")
    print("=" * 80)
    print("\nScenario: Daily loss limit of $500 hit → BRAIN STOP triggered")
    print("Expected: All new trades blocked\n")
    
    # Mock BRAIN state
    brain_state = {'state': 'STOP', 'reason_code': 'daily_loss_limit', 
                   'reason_text': 'Daily loss limit of $500 reached'}
    
    def get_brain():
        return brain_state
    
    data_layer = DataLayer(workspace_dir=Path.cwd())
    simulator = ExecutionSimulator(data_layer, brain_status_getter=get_brain)
    
    print("[ACTION] Attempting to generate 3 trades with STOP active:\n")
    
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
        print("\n✅ SUCCESS: STOP blocked all trades (expected 0, got 0)")
    else:
        print(f"\n❌ FAIL: {trades} trades leaked through! System unsafe!")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == '__main__':
    demo_stop()
