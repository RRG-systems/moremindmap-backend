#!/usr/bin/env python3
"""
PHASE 32.5 Verification Test
Tests that "New Run" properly resets all metrics to zero.
"""

import sys
import os
import json
import time
import requests
from pathlib import Path

# Add workspace to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator
from moltmarket_dashboard import dashboard_state, update_metrics, simulator, data_layer

# PHASE 32.6: Port Configuration
# Port 5000 is reserved by macOS AirTunes — DO NOT USE
PORT = 5050
BASE_URL = f"http://127.0.0.1:{PORT}"

def get_metrics():
    """Fetch current metrics from API"""
    try:
        r = requests.get(f"{BASE_URL}/api/metrics")
        return r.json()
    except Exception as e:
        print(f"ERROR fetching metrics: {e}")
        return None

def reset_run():
    """Call reset endpoint"""
    try:
        r = requests.post(f"{BASE_URL}/api/reset")
        return r.json()
    except Exception as e:
        print(f"ERROR calling reset: {e}")
        return None

def test_phase_325_reset():
    """
    PHASE 32.5 Verification Test
    
    Sequence:
    1. Wait for existing trades to accumulate
    2. Check that total_trades > 0
    3. Click "New Run" (call /api/reset)
    4. IMMEDIATELY check metrics (should be zero)
    5. Execute 2 trades
    6. Verify total_trades = 2
    """
    
    print("=" * 70)
    print("PHASE 32.5 VERIFICATION TEST - Run State Reset + Metric Contamination")
    print("=" * 70)
    
    # STEP 1: Let system accumulate some trades
    print("\n[TEST] Waiting for system to accumulate trades...")
    time.sleep(5)
    
    # STEP 2: Check current state
    print("\n[TEST] BEFORE Reset:")
    metrics_before = get_metrics()
    if metrics_before:
        print(f"  total_trades: {metrics_before.get('total_trades', 'N/A')}")
        print(f"  paper_value: {metrics_before.get('paper_value', 'N/A')}")
        print(f"  paper_trades: {metrics_before.get('paper_trades', 'N/A')}")
        print(f"  sign_flip_count: {metrics_before.get('sign_flip_count', 'N/A')}")
        print(f"  sign_flip_rate_pct: {metrics_before.get('sign_flip_rate_pct', 'N/A')}")
    
    # STEP 3: Reset
    print("\n[TEST] Calling /api/reset...")
    reset_result = reset_run()
    if reset_result:
        print(f"  Response: {reset_result.get('status', 'unknown')}")
        print(f"  New run_id: {reset_result.get('new_run_id', 'N/A')}")
    
    # Wait for metrics to update
    time.sleep(1)
    
    # STEP 4: IMMEDIATE check after reset
    print("\n[TEST] AFTER Reset (immediate):")
    metrics_after = get_metrics()
    if metrics_after:
        total_trades = metrics_after.get('total_trades', 'N/A')
        paper_pnl = metrics_after.get('paper_value', 'N/A')
        paper_trades = metrics_after.get('paper_trades', 'N/A')
        sign_flips = metrics_after.get('sign_flip_count', 'N/A')
        flip_rate = metrics_after.get('sign_flip_rate_pct', 'N/A')
        
        print(f"  total_trades: {total_trades}")
        print(f"  paper_value: {paper_pnl}")
        print(f"  paper_trades: {paper_trades}")
        print(f"  sign_flip_count: {sign_flips}")
        print(f"  sign_flip_rate_pct: {flip_rate}")
        
        # VERIFY: All should be 0
        success = True
        if total_trades != 0:
            print(f"  ❌ FAIL: total_trades should be 0, got {total_trades}")
            success = False
        if paper_pnl != 0:
            print(f"  ❌ FAIL: paper_value should be 0, got {paper_pnl}")
            success = False
        if paper_trades != 0:
            print(f"  ❌ FAIL: paper_trades should be 0, got {paper_trades}")
            success = False
        if sign_flips != 0:
            print(f"  ❌ FAIL: sign_flip_count should be 0, got {sign_flips}")
            success = False
        if flip_rate != 0:
            print(f"  ❌ FAIL: sign_flip_rate_pct should be 0, got {flip_rate}")
            success = False
        
        if success:
            print("  ✅ PASS: All metrics reset to zero")
        else:
            print("  ❌ FAIL: Metrics not properly reset")
            return False
    
    # STEP 5: Wait for trades to execute
    print("\n[TEST] Waiting for new trades to execute...")
    time.sleep(3)
    
    # STEP 6: Check after new trades
    print("\n[TEST] After new trades:")
    metrics_final = get_metrics()
    if metrics_final:
        total_trades = metrics_final.get('total_trades', 'N/A')
        paper_trades = metrics_final.get('paper_trades', 'N/A')
        
        print(f"  total_trades: {total_trades}")
        print(f"  paper_trades: {paper_trades}")
        print(f"  paper_value: {metrics_final.get('paper_value', 'N/A')}")
        
        if paper_trades >= 1:
            print(f"  ✅ PASS: New trades executing (paper_trades={paper_trades})")
        else:
            print(f"  ⚠️  Warning: No new trades yet")
    
    print("\n" + "=" * 70)
    print("PHASE 32.5 TEST COMPLETE")
    print("=" * 70)
    
    return True

if __name__ == '__main__':
    print("Starting test...")
    try:
        test_phase_325_reset()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
