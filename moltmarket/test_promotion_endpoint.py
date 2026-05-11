#!/usr/bin/env python3
"""
Test script for PHASE 32.1 Backend Promotion Endpoint

This script provides manual testing and debugging for the promotion endpoint.
Run AFTER dashboard is started (http://127.0.0.1:5050).

Usage:
  python test_promotion_endpoint.py --check-status
  python test_promotion_endpoint.py --promote baby_variant_001
  python test_promotion_endpoint.py --full-test
"""

import requests
import json
import time
import sys
from datetime import datetime
from pathlib import Path

# PHASE 32.6: Port Configuration
# Port 5000 is reserved by macOS AirTunes — DO NOT USE
PORT = 5050
BASE_URL = f"http://127.0.0.1:{PORT}"

# ANSI colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"
BOLD = "\033[1m"


def print_header(text):
    print(f"\n{BOLD}{BLUE}{'='*60}{RESET}")
    print(f"{BOLD}{BLUE}{text:^60}{RESET}")
    print(f"{BOLD}{BLUE}{'='*60}{RESET}\n")


def print_success(text):
    print(f"{GREEN}✓ {text}{RESET}")


def print_error(text):
    print(f"{RED}✗ {text}{RESET}")


def print_info(text):
    print(f"{BLUE}ℹ {text}{RESET}")


def print_json(data, indent=2):
    print(json.dumps(data, indent=indent))


def check_nursery_status():
    """Check current nursery status"""
    print_header("Checking Nursery Status")
    
    try:
        response = requests.get(f"{BASE_URL}/api/nursery/status", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            print_success("Nursery status retrieved")
            print_json(data)
            
            # Detailed analysis
            print(f"\n{BOLD}Status Analysis:{RESET}")
            print_info(f"Nursery Status: {data.get('nursery_status', 'unknown')}")
            print_info(f"Active Babies: {data.get('active_babies', 0)}")
            print_info(f"Current Parent: {data.get('parent_strategy', {}).get('id', 'unknown')}")
            print_info(f"Parent Generation: {data.get('parent_strategy', {}).get('generation', 0)}")
            
            return data
        else:
            print_error(f"Status code {response.status_code}: {response.text}")
            return None
    
    except requests.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}. Is dashboard running?")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def get_leaderboard():
    """Get current nursery leaderboard"""
    print_header("Retrieving Nursery Leaderboard")
    
    try:
        response = requests.get(f"{BASE_URL}/api/nursery/leaderboard", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            leaderboard = data.get('leaderboard', [])
            
            print_success(f"Retrieved {len(leaderboard)} baby variants")
            
            if leaderboard:
                print(f"\n{BOLD}Top 3 Candidates:{RESET}")
                for i, baby in enumerate(leaderboard[:3]):
                    print(f"  {i+1}. {baby['variant_id']}")
                    print(f"     Score: {baby.get('score', 'N/A')}")
                    print(f"     Trades: {baby.get('trades', 0)}")
                    print(f"     Shadow PnL: {baby.get('shadow_pnl', 0)}")
                    print()
            
            return leaderboard
        else:
            print_error(f"Status code {response.status_code}")
            return None
    
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def promote_variant(variant_id):
    """Promote a specific variant to parent strategy"""
    print_header(f"Promoting Variant: {variant_id}")
    
    print_info(f"Sending promotion request for {variant_id}...")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/nursery/promote/{variant_id}",
            timeout=10
        )
        
        print_info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print_success("Promotion successful!")
            print_json(data)
            
            # Detailed summary
            print(f"\n{BOLD}Promotion Summary:{RESET}")
            print_success(f"Promoted: {data.get('promoted_variant')}")
            print_success(f"Retired: {data.get('retired_count')} babies")
            print_success(f"New generation: {data.get('parent_strategy', {}).get('generation')}")
            
            return data
        
        elif response.status_code == 400:
            data = response.json()
            print_error(f"Validation failed: {data.get('error')}")
            return None
        
        elif response.status_code == 404:
            print_error(f"Variant '{variant_id}' not found")
            return None
        
        elif response.status_code == 500:
            data = response.json()
            print_error(f"Server error: {data.get('error')}")
            return None
        
        else:
            print_error(f"Unexpected status code {response.status_code}: {response.text}")
            return None
    
    except requests.ConnectionError:
        print_error(f"Cannot connect to {BASE_URL}")
        return None
    except Exception as e:
        print_error(f"Error: {str(e)}")
        return None


def verify_csv_update(variant_id):
    """Verify that variant_nursery.csv was updated correctly"""
    print_header("Verifying CSV Update")
    
    csv_file = Path.cwd() / 'variant_nursery.csv'
    
    if not csv_file.exists():
        print_error(f"CSV file not found at {csv_file}")
        return False
    
    try:
        import csv
        
        promoted_row = None
        retired_count = 0
        
        with open(csv_file, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['variant_id'] == variant_id:
                    promoted_row = row
                    if row.get('status') == 'promoted':
                        print_success(f"Found promoted row for {variant_id}")
                elif row.get('status') == 'retired':
                    retired_count += 1
        
        if promoted_row:
            print_info(f"Promoted status: {promoted_row.get('status')}")
            print_info(f"Promoted at: {promoted_row.get('promoted_at', 'N/A')}")
            print_info(f"Retired babies: {retired_count}")
            return True
        else:
            print_error(f"No promoted row found for {variant_id}")
            return False
    
    except Exception as e:
        print_error(f"Error reading CSV: {str(e)}")
        return False


def run_full_test():
    """Run comprehensive test sequence"""
    print_header("FULL TEST SEQUENCE")
    
    print_info("Step 1: Check current nursery status")
    status = check_nursery_status()
    
    if not status:
        print_error("Cannot proceed - dashboard unreachable")
        return False
    
    if status.get('active_babies', 0) == 0:
        print_error("No active babies in nursery. Spawn babies first with POST /api/nursery/spawn")
        return False
    
    print_info("\nStep 2: Get leaderboard")
    leaderboard = get_leaderboard()
    
    if not leaderboard or len(leaderboard) == 0:
        print_error("No leaderboard data available")
        return False
    
    top_baby = leaderboard[0]['variant_id']
    top_score = leaderboard[0].get('score', 'N/A')
    top_trades = leaderboard[0].get('trades', 0)
    
    print_info(f"\nTop candidate: {top_baby} (score: {top_score}, trades: {top_trades})")
    
    if top_trades < 30:
        print_error(f"Top candidate has only {top_trades} trades (need 30). Wait for more execution.")
        return False
    
    print_info("\nStep 3: Promote top candidate")
    promotion = promote_variant(top_baby)
    
    if not promotion:
        print_error("Promotion failed")
        return False
    
    print_info("\nStep 4: Verify CSV update")
    time.sleep(1)  # Brief delay for file write
    csv_verified = verify_csv_update(top_baby)
    
    if not csv_verified:
        print_error("CSV verification failed")
        return False
    
    print_info("\nStep 5: Final status check")
    final_status = check_nursery_status()
    
    if final_status and final_status.get('active_babies') == 0:
        print_success("Nursery successfully cleared")
    else:
        print_error("Nursery still has active babies")
        return False
    
    print_header("TEST COMPLETE - ALL CHECKS PASSED")
    print_success("Promotion endpoint working correctly")
    return True


def main():
    if len(sys.argv) < 2:
        print_header("PHASE 32.1 Promotion Endpoint Test Utility")
        print(f"""
Usage:
  {sys.argv[0]} --status              Check current nursery status
  {sys.argv[0]} --leaderboard         Get nursery leaderboard
  {sys.argv[0]} --promote <variant>   Promote a specific variant
  {sys.argv[0]} --full-test           Run complete test sequence
  {sys.argv[0]} --help                Show this message

Examples:
  {sys.argv[0]} --status
  {sys.argv[0]} --promote baby_variant_001
  {sys.argv[0]} --full-test

Notes:
  - Dashboard must be running: python moltmarket_dashboard.py
  - Babies must be spawned first: POST /api/nursery/spawn
  - Babies must have 30+ trades to promote
""")
        return
    
    command = sys.argv[1].lower()
    
    if command == '--status' or command == '-s':
        check_nursery_status()
    
    elif command == '--leaderboard' or command == '-l':
        get_leaderboard()
    
    elif command == '--promote' or command == '-p':
        if len(sys.argv) < 3:
            print_error("Usage: --promote <variant_id>")
            sys.exit(1)
        variant_id = sys.argv[2]
        promote_variant(variant_id)
    
    elif command == '--full-test' or command == '-t':
        success = run_full_test()
        sys.exit(0 if success else 1)
    
    elif command == '--help' or command == '-h':
        print("Test utility for PHASE 32.1 promotion endpoint")
        print("See usage above")
    
    else:
        print_error(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == '__main__':
    main()
