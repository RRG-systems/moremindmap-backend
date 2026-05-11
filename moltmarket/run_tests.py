#!/usr/bin/env python3
"""
PHASE 32.6 PORT MIGRATION VERIFICATION

Tests all 4 required endpoints on port 5050
"""

import subprocess
import time
import sys
import requests
import json

PORT = 5050
BASE_URL = f"http://127.0.0.1:{PORT}"

def test_endpoint(url, expected_status=200):
    """Test a single endpoint"""
    try:
        response = requests.get(url, timeout=5)
        status_ok = response.status_code == expected_status
        json_ok = False
        try:
            data = response.json()
            json_ok = True
        except:
            pass
        
        return {
            'url': url,
            'status': response.status_code,
            'status_ok': status_ok,
            'json_ok': json_ok,
            'error': None if status_ok and json_ok else 'Failed'
        }
    except Exception as e:
        return {
            'url': url,
            'status': None,
            'status_ok': False,
            'json_ok': False,
            'error': str(e)
        }

def main():
    print("\n" + "="*60)
    print("PHASE 32.6: PORT MIGRATION VERIFICATION")
    print("="*60)
    print(f"\nStarting dashboard on port {PORT}...\n")
    
    # Start server
    proc = subprocess.Popen(
        [sys.executable, 'moltmarket_dashboard.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd='/Users/rrg/.openclaw/workspace/moltmarket'
    )
    
    # Wait for server startup
    time.sleep(4)
    
    # Check if process is still running
    if proc.poll() is not None:
        print("✗ Server failed to start. Output:")
        output = proc.stdout.read()
        print(output[-500:] if len(output) > 500 else output)
        return False
    
    print(f"✓ Server process started (PID: {proc.pid})")
    
    # Test endpoints
    print(f"\n{'-'*60}")
    print("Testing endpoints on port {PORT}:")
    print(f"{'-'*60}\n")
    
    endpoints = [
        f"{BASE_URL}/api/metrics",
        f"{BASE_URL}/api/trades",
        f"{BASE_URL}/api/equity-curves",
        f"{BASE_URL}/api/breakdowns",
    ]
    
    results = []
    for endpoint in endpoints:
        result = test_endpoint(endpoint)
        results.append(result)
        
        status_icon = "✓" if result['status_ok'] and result['json_ok'] else "✗"
        print(f"{status_icon} {result['url']}")
        print(f"  Status: {result['status']} (expected 200)")
        print(f"  JSON: {'valid' if result['json_ok'] else 'invalid'}")
        if result['error']:
            print(f"  Error: {result['error']}")
        print()
    
    # Kill server
    proc.terminate()
    try:
        proc.wait(timeout=2)
    except:
        proc.kill()
    
    # Summary
    print(f"{'-'*60}")
    print("SUMMARY")
    print(f"{'-'*60}\n")
    
    passed = sum(1 for r in results if r['status_ok'] and r['json_ok'])
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✓ ALL TESTS PASSED")
        return True
    else:
        print("\n✗ SOME TESTS FAILED")
        return False

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
