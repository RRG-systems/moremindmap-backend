#!/usr/bin/env python3
"""
MANUAL LIVE CHECK: STOP Enforcement
Trigger STOP state in dashboard and verify zero new trades execute
"""

import sys
from pathlib import Path
from dashboard_execution import ExecutionSimulator
from dashboard_data_layer import DataLayer
from datetime import datetime


def simulate_live_stop_scenario():
    """Simulate live scenario: BRAIN transitions to STOP mid-run"""
    print("\n" + "=" * 80)
    print("MANUAL LIVE CHECK: STOP Enforcement")
    print("=" * 80)
    
    # Simulate dashboard_state as it would be in production
    dashboard_state = {
        'brain_state': 'NORMAL',
        'brain_reason_code': 'nominal',
        'brain_reason_text': 'System nominal',
    }
    
    def get_brain_status():
        """Live callback — reads dashboard_state"""
        return {
            'state': dashboard_state['brain_state'],
            'reason_code': dashboard_state['brain_reason_code'],
            'reason_text': dashboard_state['brain_reason_text'],
        }
    
    data_layer = DataLayer(workspace_dir=Path.cwd())
    simulator = ExecutionSimulator(data_layer, brain_status_getter=get_brain_status)
    
    print("\n[SCENARIO] Live trading session")
    print("=" * 80)
    
    # Phase 1: NORMAL trading
    print("\n[PHASE 1] Trading normally (NORMAL state)")
    print("-" * 80)
    initial_trades = len(data_layer.get_recent_trades(limit=10000))
    
    for i in range(3):
        simulator._generate_signal()
        print(f"  Signal {i+1} generated")
    
    trades_phase1 = len(data_layer.get_recent_trades(limit=10000)) - initial_trades
    print(f"\nPhase 1 result: {trades_phase1} trades generated")
    assert trades_phase1 == 6, f"Expected 6 trades in NORMAL, got {trades_phase1}"
    
    # Phase 2: STOP triggered
    print("\n[PHASE 2] EMERGENCY: Daily loss limit reached → STOP triggered")
    print("-" * 80)
    
    dashboard_state['brain_state'] = 'STOP'
    dashboard_state['brain_reason_code'] = 'daily_loss_limit'
    dashboard_state['brain_reason_text'] = 'Daily loss limit of $500 reached'
    
    print(f"Dashboard updated:")
    print(f"  state: {dashboard_state['brain_state']}")
    print(f"  code: {dashboard_state['brain_reason_code']}")
    print(f"  text: {dashboard_state['brain_reason_text']}")
    
    # Try to generate signals while STOP is active
    initial_trades = len(data_layer.get_recent_trades(limit=10000))
    
    print(f"\nAttempting to generate 5 signals with STOP active...")
    for i in range(5):
        simulator._generate_signal()
        print(f"  Signal {i+1} attempted")
    
    trades_phase2 = len(data_layer.get_recent_trades(limit=10000)) - initial_trades
    print(f"\nPhase 2 result: {trades_phase2} trades generated")
    
    if trades_phase2 != 0:
        print(f"\n❌ FAIL: {trades_phase2} trades executed during STOP!")
        print("System is UNSAFE. Do not proceed to Phase 4.7.")
        return False
    
    # Phase 3: Recovery
    print("\n[PHASE 3] Manual recovery: STOP cleared → NORMAL")
    print("-" * 80)
    
    dashboard_state['brain_state'] = 'NORMAL'
    dashboard_state['brain_reason_code'] = 'recovery'
    dashboard_state['brain_reason_text'] = 'Daily loss limit cleared, resuming'
    
    print(f"Dashboard updated:")
    print(f"  state: {dashboard_state['brain_state']}")
    print(f"  code: {dashboard_state['brain_reason_code']}")
    print(f"  text: {dashboard_state['brain_reason_text']}")
    
    initial_trades = len(data_layer.get_recent_trades(limit=10000))
    
    print(f"\nAttempting to generate 3 signals with NORMAL (recovered)...")
    for i in range(3):
        simulator._generate_signal()
        print(f"  Signal {i+1} generated")
    
    trades_phase3 = len(data_layer.get_recent_trades(limit=10000)) - initial_trades
    print(f"\nPhase 3 result: {trades_phase3} trades generated")
    assert trades_phase3 == 6, f"Expected 6 trades in recovered NORMAL, got {trades_phase3}"
    
    # Summary
    print("\n" + "=" * 80)
    print("MANUAL CHECK COMPLETE")
    print("=" * 80)
    print(f"\nPhase 1 (NORMAL):        {trades_phase1} trades ✅")
    print(f"Phase 2 (STOP):          {trades_phase2} trades ✅ (zero slip-through)")
    print(f"Phase 3 (NORMAL again):  {trades_phase3} trades ✅")
    print("\n✅ MANUAL VERIFICATION PASSED")
    print("\nKey findings:")
    print("- STOP truly blocks ALL trades (zero slip-through)")
    print("- State transitions enforced in real-time")
    print("- Recovery to NORMAL works as expected")
    print("\nSystem is SAFE to proceed to Phase 4.7")
    print("=" * 80 + "\n")
    
    return True


if __name__ == '__main__':
    try:
        result = simulate_live_stop_scenario()
        if not result:
            sys.exit(1)
    except AssertionError as e:
        print(f"\n❌ ASSERTION FAILED: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
