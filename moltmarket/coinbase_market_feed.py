#!/usr/bin/env python3
"""
COINBASE MARKET FEED ADAPTER

Real-time BTC/ETH market data from Coinbase WebSocket.
Read-only, no auth required.

Output: normalized tick stream for simulator consumption
Format:
{
    "timestamp": ISO8601,
    "symbol": "BTC-USD" or "ETH-USD",
    "bid": float,
    "ask": float,
    "mid": float,
    "last": float,
    "sequence": int
}
"""

import json
import threading
import time
from datetime import datetime
from typing import Dict, Optional, Callable, List
from collections import deque
import websocket

try:
    import queue
except ImportError:
    import Queue as queue


class CoinbaseMarketFeed:
    """
    Real-time Coinbase market data ingestion.
    
    Public WebSocket (no auth required):
    wss://ws-feed.exchange.coinbase.com
    
    Subscriptions:
    - BTC-USD (ticker channel)
    - ETH-USD (ticker channel)
    """
    
    def __init__(self, max_buffer_size: int = 10000):
        self.url = "wss://ws-feed.exchange.coinbase.com"
        self.symbols = ["BTC-USD", "ETH-USD"]
        
        # Tick buffer (keep recent ticks)
        self.tick_buffer = {sym: deque(maxlen=max_buffer_size) for sym in self.symbols}
        
        # Latest tick per symbol
        self.latest_ticks = {sym: None for sym in self.symbols}
        
        # Connection state
        self.ws = None
        self.connected = False
        self.last_heartbeat = None
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Callbacks
        self.on_tick_callback: Optional[Callable] = None
        self.on_connect_callback: Optional[Callable] = None
        self.on_disconnect_callback: Optional[Callable] = None
        
        # Stats
        self.ticks_received = 0
        self.connection_count = 0
        self.errors = []
    
    def on_message(self, ws, message: str):
        """Handle WebSocket message"""
        try:
            data = json.loads(message)
            msg_type = data.get('type')
            
            # Heartbeat (keep-alive)
            if msg_type == 'heartbeat':
                self.last_heartbeat = datetime.utcnow()
                return
            
            # Subscriptions confirmation
            if msg_type == 'subscriptions':
                print(f"[COINBASE] Subscribed: {data.get('channels')}")
                return
            
            # Ticker update
            if msg_type == 'ticker':
                self._process_ticker(data)
        
        except json.JSONDecodeError as e:
            self.errors.append(f"JSON decode error: {e}")
        except Exception as e:
            self.errors.append(f"Message handler error: {e}")
    
    def _process_ticker(self, data: Dict):
        """Process ticker message into normalized tick"""
        try:
            symbol = data.get('product_id')
            
            if symbol not in self.symbols:
                return
            
            # Extract price data
            bid = float(data.get('best_bid', 0))
            ask = float(data.get('best_ask', 0))
            last = float(data.get('price', 0))
            
            # Calculate mid
            mid = (bid + ask) / 2 if (bid > 0 and ask > 0) else last
            
            # Create normalized tick
            tick = {
                'timestamp': data.get('time'),  # ISO8601 from Coinbase
                'symbol': symbol,
                'bid': bid,
                'ask': ask,
                'mid': mid,
                'last': last,
                'sequence': data.get('sequence', 0),
            }
            
            # Store
            with self.lock:
                self.tick_buffer[symbol].append(tick)
                self.latest_ticks[symbol] = tick
                self.ticks_received += 1
            
            # Invoke callback
            if self.on_tick_callback:
                self.on_tick_callback(tick)
        
        except Exception as e:
            self.errors.append(f"Ticker processing error: {e}")
    
    def on_error(self, ws, error):
        """Handle WebSocket error"""
        print(f"[COINBASE] WebSocket error: {error}")
        self.errors.append(f"WebSocket error: {error}")
    
    def on_close(self, ws, close_status_code, close_msg):
        """Handle WebSocket close"""
        print(f"[COINBASE] WebSocket closed (code: {close_status_code})")
        with self.lock:
            self.connected = False
        
        if self.on_disconnect_callback:
            self.on_disconnect_callback()
    
    def on_open(self, ws):
        """Handle WebSocket open"""
        print(f"[COINBASE] WebSocket connected")
        
        with self.lock:
            self.connected = True
            self.connection_count += 1
        
        # Subscribe to ticker channel
        subscribe_msg = {
            "type": "subscribe",
            "product_ids": self.symbols,
            "channels": ["ticker"]
        }
        
        ws.send(json.dumps(subscribe_msg))
        print(f"[COINBASE] Subscribed to: {self.symbols}")
        
        if self.on_connect_callback:
            self.on_connect_callback()
    
    def connect(self, run_in_thread: bool = True) -> bool:
        """
        Connect to Coinbase WebSocket
        
        Args:
            run_in_thread: If True, run in background thread
        
        Returns:
            True if connecting/connected, False on immediate failure
        """
        try:
            # Configure WebSocket
            websocket.enableTrace(False)
            
            self.ws = websocket.WebSocketApp(
                self.url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
            
            if run_in_thread:
                # Run in background thread
                self.ws_thread = threading.Thread(
                    target=self.ws.run_forever,
                    kwargs={'ping_interval': 30}  # Heartbeat every 30s
                )
                self.ws_thread.daemon = True
                self.ws_thread.start()
                print(f"[COINBASE] Connection thread started")
                
                # Wait briefly for connection to establish
                time.sleep(2)
                return self.connected
            else:
                # Run blocking
                self.ws.run_forever(ping_interval=30)
                return True
        
        except Exception as e:
            print(f"[COINBASE] Connection failed: {e}")
            self.errors.append(f"Connection failed: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from WebSocket"""
        if self.ws:
            self.ws.close()
            with self.lock:
                self.connected = False
            print(f"[COINBASE] Disconnected")
    
    def is_connected(self) -> bool:
        """Check if connected and receiving data"""
        with self.lock:
            return self.connected
    
    def get_latest_tick(self, symbol: str) -> Optional[Dict]:
        """Get latest tick for symbol"""
        if symbol not in self.symbols:
            return None
        
        with self.lock:
            return self.latest_ticks[symbol]
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get latest mid price for symbol"""
        tick = self.get_latest_tick(symbol)
        if tick:
            return tick.get('mid')
        return None
    
    def get_bid_ask(self, symbol: str) -> Optional[tuple]:
        """Get latest bid/ask for symbol"""
        tick = self.get_latest_tick(symbol)
        if tick:
            return (tick.get('bid'), tick.get('ask'))
        return None
    
    def get_tick_history(self, symbol: str, limit: Optional[int] = None) -> List[Dict]:
        """Get tick history for symbol"""
        if symbol not in self.symbols:
            return []
        
        with self.lock:
            history = list(self.tick_buffer[symbol])
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_stats(self) -> Dict:
        """Get feed statistics"""
        with self.lock:
            return {
                'connected': self.connected,
                'ticks_received': self.ticks_received,
                'connections': self.connection_count,
                'last_heartbeat': self.last_heartbeat.isoformat() if self.last_heartbeat else None,
                'latest_btc': self.latest_ticks.get('BTC-USD'),
                'latest_eth': self.latest_ticks.get('ETH-USD'),
                'error_count': len(self.errors),
                'recent_errors': self.errors[-5:] if self.errors else [],
            }
    
    def set_on_tick(self, callback: Callable):
        """Register callback for each tick"""
        self.on_tick_callback = callback
    
    def set_on_connect(self, callback: Callable):
        """Register callback for connection"""
        self.on_connect_callback = callback
    
    def set_on_disconnect(self, callback: Callable):
        """Register callback for disconnection"""
        self.on_disconnect_callback = callback


# Test/demo
if __name__ == '__main__':
    print("\n" + "="*80)
    print("COINBASE MARKET FEED — Connection Test")
    print("="*80)
    
    feed = CoinbaseMarketFeed()
    
    tick_count = [0]
    
    def on_tick(tick):
        tick_count[0] += 1
        if tick_count[0] % 10 == 0:
            print(f"[TICK {tick_count[0]:4d}] {tick['symbol']}: "
                  f"bid=${tick['bid']:.2f} mid=${tick['mid']:.2f} ask=${tick['ask']:.2f}")
    
    def on_connect():
        print("[FEED] Connected and receiving data")
    
    def on_disconnect():
        print("[FEED] Disconnected")
    
    feed.set_on_tick(on_tick)
    feed.set_on_connect(on_connect)
    feed.set_on_disconnect(on_disconnect)
    
    print("\nConnecting to Coinbase...")
    if feed.connect(run_in_thread=True):
        print("Connected. Receiving for 30 seconds...\n")
        time.sleep(30)
        
        print("\n" + "-"*80)
        print("FEED STATISTICS")
        print("-"*80)
        stats = feed.stats()
        for key, value in stats.items():
            if key != 'recent_errors':
                print(f"  {key}: {value}")
        
        print("\n" + "-"*80)
        print("LATEST PRICES")
        print("-"*80)
        for symbol in ["BTC-USD", "ETH-USD"]:
            price = feed.get_latest_price(symbol)
            if price:
                print(f"  {symbol}: ${price:.2f}")
        
        feed.disconnect()
    else:
        print("Failed to connect")
    
    print("\n" + "="*80 + "\n")
