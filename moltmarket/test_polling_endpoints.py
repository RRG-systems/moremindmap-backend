#!/usr/bin/env python3
"""
Test script for PHASE 32.5E: Polling endpoints fix
Verifies all 4 endpoints return 200 OK with valid JSON
"""

import json
import sys
from pathlib import Path

# Add current dir to path
sys.path.insert(0, str(Path(__file__).parent))

from flask import Flask
from moltmarket_dashboard import app

def test_endpoints():
    """Test all 4 polling endpoints"""
    
    # Create test client
    client = app.test_client()
    
    endpoints = [
        ('/api/metrics', 'Metrics endpoint'),
        ('/api/trades', 'Trades endpoint'),
        ('/api/equity-curves', 'Equity curves endpoint'),
        ('/api/breakdowns', 'Breakdowns endpoint'),
    ]
    
    print("\n" + "="*70)
    print("PHASE 32.5E: Dashboard Polling Endpoints Test")
    print("="*70 + "\n")
    
    all_pass = True
    
    for endpoint, description in endpoints:
        print(f"Testing: {endpoint} ({description})")
        print("-" * 70)
        
        try:
            # Make GET request
            response = client.get(endpoint)
            
            # Check status code
            status_ok = response.status_code == 200
            print(f"  Status: {response.status_code} {'✓' if status_ok else '✗ FAIL'}")
            
            if not status_ok:
                all_pass = False
                print(f"  ERROR: Expected 200, got {response.status_code}")
                print(f"  Response body: {response.data.decode()[:200]}")
                print()
                continue
            
            # Check Content-Type
            content_type_ok = 'application/json' in response.content_type
            print(f"  Content-Type: {response.content_type} {'✓' if content_type_ok else '✗ FAIL'}")
            
            # Try to parse JSON
            try:
                data = response.get_json()
                json_ok = True
                print(f"  JSON: Valid ✓")
                print(f"  Response preview: {str(data)[:100]}...")
            except Exception as e:
                all_pass = False
                json_ok = False
                print(f"  JSON: Invalid ✗")
                print(f"  Error: {e}")
                print(f"  Body: {response.data.decode()[:200]}")
            
            # Summary for this endpoint
            if status_ok and json_ok:
                print(f"  Result: PASS ✓\n")
            else:
                print(f"  Result: FAIL ✗\n")
                all_pass = False
            
        except Exception as e:
            print(f"  Exception: {e}")
            print(f"  Result: ERROR ✗\n")
            all_pass = False
    
    print("="*70)
    if all_pass:
        print("ALL TESTS PASSED ✓")
        print("="*70)
        return 0
    else:
        print("SOME TESTS FAILED ✗")
        print("="*70)
        return 1

if __name__ == '__main__':
    sys.exit(test_endpoints())
