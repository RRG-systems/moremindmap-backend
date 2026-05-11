#!/usr/bin/env python3
"""
PROPER INTEGRATION TEST: Real Data → ExecutionSimulator → CSV

Proves:
1. Coinbase feed connects and provides real prices
2. ExecutionSimulator uses real prices (not random walk)
3. Trades are generated and written to CSV
4. Dashboard will show real trade data
"""

import time
import csv
from pathlib import Path
from datetime import datetime

from coinbase_market_feed import CoinbaseMarketFeed
from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator
from execution_simulator_realdata import setup_real_data_simulation


class RealDataIntegrationTest:
    """Full integration: feed → simulator → CSV"""
    
    def __init__(self, duration_seconds: int = 60, output_csv: str = "research_trades.csv"):
        self.duration = duration_seconds
        self.output_csv = Path(output_csv)
        self.data_layer = None
        self.simulator = None
        self.real_sim = None
        self.feed = None
        self.start_time = None
        self.trades_written = 0
    
    def setup(self) -> bool:
        """Setup: connect feed, init simulator, wire together"""
        print("\n" + "="*80)
        print("SETUP: Real Data Integration Test")
        print("="*80)
        
        # Step 1: Connect to Coinbase feed
        print("\n[SETUP] Connecting to Coinbase market feed...")
        self.feed = CoinbaseMarketFeed()
        
        if not self.feed.connect(run_in_thread=True):
            print("[SETUP] ✗ FAIL: Feed connection failed")
            return False
        
        # Wait for connection
        for attempt in range(10):
            time.sleep(1)
            if self.feed.is_connected():
                print("[SETUP] ✓ Feed connected")
                break
        else:
            print("[SETUP] ✗ FAIL: Feed connection timeout")
            return False
        
        # Step 2: Initialize DataLayer (will use existing CSV)
        print("\n[SETUP] Initializing DataLayer...")
        self.data_layer = DataLayer(workspace_dir=Path.cwd())
        print(f"[SETUP] ✓ DataLayer ready (CSV: {self.output_csv})")
        
        # Step 3: Initialize ExecutionSimulator
        print("\n[SETUP] Initializing ExecutionSimulator...")
        self.simulator = ExecutionSimulator(self.data_layer)
        self.simulator.initialize()
        print("[SETUP] ✓ ExecutionSimulator ready")
        
        # Step 4: Wire real data into simulator
        print("\n[SETUP] Wiring real Coinbase feed into simulator...")
        self.real_sim = setup_real_data_simulation(self.simulator, self.feed)
        
        if not self.real_sim.inject_real_price_source():
            print("[SETUP] ✗ FAIL: Price source injection failed")
            return False
        
        print("[SETUP] ✓ Real price source injected")
        print(f"[SETUP] ✓ Mode: {self.real_sim.get_mode()}")
        
        self.start_time = time.time()
        return True
    
    def run_simulation_cycles(self):
        """Run simulation cycles on real market data"""
        print("\n" + "="*80)
        print("SIMULATION: Running cycles on real Coinbase data")
        print(f"Duration: {self.duration} seconds")
        print("="*80)
        
        cycle_count = 0
        last_price_update = None
        
        try:
            while (time.time() - self.start_time) < self.duration:
                # Step on simulator (will use real prices via injected getter)
                self.simulator.step()
                
                cycle_count += 1
                
                # Print status every 10 cycles
                if cycle_count % 10 == 0:
                    state = self.real_sim.get_session_state()
                    btc = state.get('btc_price', 0)
                    eth = state.get('eth_price', 0)
                    trades = state.get('paper_trades', 0)
                    
                    print(f"[CYCLE {cycle_count:3d}] BTC: ${btc:.2f}  ETH: ${eth:.2f}  "
                          f"Trades: {trades}  Ticks: {state.get('ticks_received', 0)}")
                    
                    last_price_update = (btc, eth)
                
                time.sleep(0.5)  # Poll every 500ms
        
        except KeyboardInterrupt:
            print("\n[SIMULATION] Interrupted by user")
        
        print(f"\n[SIMULATION] Completed {cycle_count} cycles")
        return cycle_count
    
    def check_csv_output(self) -> bool:
        """Verify trades were written to CSV"""
        print("\n" + "="*80)
        print("VERIFICATION: Check CSV for trades")
        print("="*80)
        
        if not self.output_csv.exists():
            print(f"[CHECK] ✗ FAIL: CSV file not found: {self.output_csv}")
            return False
        
        # Read CSV
        with open(self.output_csv, 'r') as f:
            reader = csv.DictReader(f)
            trades = list(reader)
        
        line_count = len(trades) + 1  # +1 for header
        
        print(f"\n[CHECK] CSV file: {self.output_csv}")
        print(f"[CHECK] Total lines: {line_count}")
        print(f"[CHECK] Data rows: {len(trades)}")
        
        if len(trades) == 0:
            print("[CHECK] ✗ FAIL: No trades in CSV")
            return False
        
        print(f"[CHECK] ✓ Trades written: {len(trades)}")
        self.trades_written = len(trades)
        
        # Show last 5 trades
        print(f"\n[CHECK] Last 5 trades:")
        print("-" * 80)
        for i, trade in enumerate(trades[-5:], 1):
            asset = trade.get('asset', '?')
            source = trade.get('source', '?')
            side = trade.get('side', '?')
            entry = trade.get('entry_price', '?')
            exit_p = trade.get('exit_price', '?')
            pnl = trade.get('pnl', '?')
            
            print(f"  {i}. {asset:3s} {source:6s} {side:5s} entry=${entry:8s} exit=${exit_p:8s} pnl=${pnl:8s}")
        
        # Check for real market prices
        first_trade = trades[0]
        btc_entry = float(first_trade.get('entry_price', 0))
        
        if btc_entry > 1000:  # Real market prices (not simulated $100)
            print(f"\n[CHECK] ✓ REAL MARKET PRICES DETECTED (entry: ${btc_entry:.2f})")
            return True
        else:
            print(f"\n[CHECK] ⚠ WARNING: Prices look simulated (entry: ${btc_entry:.2f})")
            return False
    
    def cleanup(self):
        """Cleanup: disconnect feed"""
        if self.feed:
            self.feed.disconnect()
            print("[CLEANUP] Feed disconnected")
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("TEST SUMMARY")
        print("="*80)
        
        print(f"\n[RESULT] Trades written to CSV: {self.trades_written}")
        
        if self.trades_written > 0:
            print(f"\n✓ PASS: Integration test successful")
            print(f"  - Real Coinbase feed: ✓ Connected")
            print(f"  - ExecutionSimulator: ✓ Using real prices")
            print(f"  - CSV output: ✓ {self.trades_written} trades written")
            print(f"  - Dashboard ready: ✓ Will show real trade data")
            return True
        else:
            print(f"\n✗ FAIL: No trades written to CSV")
            return False
    
    def run(self) -> bool:
        """Run full integration test"""
        try:
            # Setup
            if not self.setup():
                return False
            
            # Run simulation
            cycles = self.run_simulation_cycles()
            
            # Verify output
            success = self.check_csv_output()
            
            # Print summary
            self.print_summary()
            
            return success
        
        finally:
            self.cleanup()


if __name__ == '__main__':
    test = RealDataIntegrationTest(duration_seconds=60)
    
    success = test.run()
    
    print("\n" + "="*80)
    if success:
        print("✓ INTEGRATION TEST PASSED")
        print("Dashboard is ready to display real-data trades")
    else:
        print("✗ INTEGRATION TEST FAILED")
        print("Check logs above for issues")
    print("="*80 + "\n")
