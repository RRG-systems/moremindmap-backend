#!/usr/bin/env python3
"""
EXECUTION SIMULATOR — REAL DATA MODE

Wraps existing ExecutionSimulator to consume real Coinbase market ticks
instead of random-walk prices.

This is a MINIMAL ADAPTER — no logic rewrites, just price source swap.

Mode: SIM_REALDATA_COINBASE
Execution: PAPER ONLY (no live orders)
"""

from datetime import datetime
from typing import Optional
from coinbase_market_feed import CoinbaseMarketFeed


class ExecutionSimulatorRealData:
    """
    Adapter layer: connects real Coinbase feed to existing ExecutionSimulator
    
    Replaces:
    - _get_price() → reads from Coinbase tick
    - random_walk simulation → real market prices
    
    Preserves:
    - paper execution (0-2 bps slippage)
    - shadow execution (3 + 10 bps round-trip)
    - BRAIN enforcement
    - probation / scaling logic
    - all existing logging
    """
    
    def __init__(self, existing_simulator, market_feed: CoinbaseMarketFeed):
        """
        Args:
            existing_simulator: ExecutionSimulator instance to wrap
            market_feed: CoinbaseMarketFeed instance (should be connected)
        """
        self.simulator = existing_simulator
        self.feed = market_feed
        self.mode = "SIM_REALDATA_COINBASE"
        
        # Track state
        self.connected = False
        self.last_tick_time = None
        self.tick_count = 0
        
        # Map simulator assets to Coinbase symbols
        self.asset_to_symbol = {
            'BTC': 'BTC-USD',
            'ETH': 'ETH-USD',
        }
        
        # Register tick callback
        self.feed.set_on_tick(self._on_market_tick)
        self.feed.set_on_connect(self._on_feed_connect)
        self.feed.set_on_disconnect(self._on_feed_disconnect)
    
    def _on_market_tick(self, tick):
        """Callback when market tick received"""
        self.tick_count += 1
        self.last_tick_time = tick.get('timestamp')
    
    def _on_feed_connect(self):
        """Callback when feed connects"""
        self.connected = True
        print(f"[{self.mode}] Real market feed connected")
    
    def _on_feed_disconnect(self):
        """Callback when feed disconnects"""
        self.connected = False
        print(f"[{self.mode}] Real market feed disconnected — HALTING SIMULATION")
    
    def is_ready(self) -> bool:
        """Check if real feed is connected and ready"""
        return self.feed.is_connected()
    
    def get_mode(self) -> str:
        """Get simulation mode"""
        return self.mode
    
    def get_price(self, asset: str) -> Optional[float]:
        """
        Get current price for asset from REAL Coinbase feed.
        
        SURGICAL CHANGE: Replaces simulator._get_price()
        
        Returns:
            float: mid price from Coinbase
            None: if feed disconnected or asset not available
        """
        if not self.feed.is_connected():
            print(f"[{self.mode}] ERROR: Feed disconnected, cannot get price for {asset}")
            return None
        
        # Map asset to Coinbase symbol
        symbol = self.asset_to_symbol.get(asset)
        if not symbol:
            return None
        
        # Get latest price from feed
        price = self.feed.get_latest_price(symbol)
        if price is None:
            print(f"[{self.mode}] WARNING: No price available for {symbol}")
        
        return price
    
    def get_bid_ask(self, asset: str) -> Optional[tuple]:
        """
        Get bid/ask for asset from real feed.
        
        Returns:
            (bid, ask) tuple, or None if unavailable
        """
        if not self.feed.is_connected():
            return None
        
        symbol = self.asset_to_symbol.get(asset)
        if not symbol:
            return None
        
        return self.feed.get_bid_ask(symbol)
    
    def inject_real_price_source(self):
        """
        CRITICAL: Inject real price getter into existing simulator.
        
        This replaces simulator._get_price with our real feed reader.
        
        Must be called AFTER simulator is initialized and feed is connected.
        """
        if not self.feed.is_connected():
            print(f"[{self.mode}] ERROR: Feed not connected, cannot inject price source")
            return False
        
        # Save original method
        self.original_get_price = self.simulator._get_price
        
        # Replace with real feed reader
        def _get_price_real_data(asset):
            price = self.get_price(asset)
            if price is None:
                # Feed disconnected — STOP execution
                print(f"[{self.mode}] CRITICAL: Real feed unavailable, halting execution")
                return None
            return price
        
        self.simulator._get_price = _get_price_real_data
        
        print(f"[{self.mode}] Price source injected: simulator now consuming real Coinbase data")
        return True
    
    def restore_simulated_prices(self):
        """Restore simulator to random-walk prices (debug only)"""
        if hasattr(self, 'original_get_price'):
            self.simulator._get_price = self.original_get_price
            print(f"[{self.mode}] Price source restored to simulated random walk")
    
    def get_session_state(self):
        """
        Get current session state for dashboard/THINK.
        
        Includes real market state + simulation state.
        """
        return {
            'mode': self.mode,
            'feed_connected': self.feed.is_connected(),
            'ticks_received': self.feed.ticks_received,
            'last_tick_time': self.last_tick_time,
            'btc_price': self.feed.get_latest_price('BTC-USD'),
            'eth_price': self.feed.get_latest_price('ETH-USD'),
            'paper_pnl': self.simulator.paper_pnl,
            'paper_trades': self.simulator.paper_trades,
            'shadow_pnl': self.simulator.shadow_pnl,
            'shadow_trades': self.simulator.shadow_trades,
            'paper_equity': self.simulator.get_current_equity(),
        }
    
    def get_feed_stats(self):
        """Get market feed statistics"""
        return self.feed.get_stats()


# Integration helper
def setup_real_data_simulation(simulator, market_feed: CoinbaseMarketFeed) -> ExecutionSimulatorRealData:
    """
    Setup real-data simulation in one call.
    
    Usage:
        feed = CoinbaseMarketFeed()
        feed.connect()
        
        sim = ExecutionSimulator(data_layer)
        real_sim = setup_real_data_simulation(sim, feed)
        
        # Now simulator uses real prices:
        sim.step()  # Will use real Coinbase prices
    
    Returns:
        ExecutionSimulatorRealData adapter
    """
    adapter = ExecutionSimulatorRealData(simulator, market_feed)
    
    if not adapter.inject_real_price_source():
        print("[SETUP] WARNING: Failed to inject real price source")
        return None
    
    return adapter


if __name__ == '__main__':
    print("\n" + "="*80)
    print("EXECUTION SIMULATOR — REAL DATA ADAPTER TEST")
    print("="*80)
    
    print("\nThis adapter is tested via integration with ExecutionSimulator.")
    print("See: phase48_integration_harness.py with real data")
    print("\n" + "="*80 + "\n")
