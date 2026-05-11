"""
Baby Execution Bridge — Connect signals to live markets

Babies generate signals. This bridge routes them to the active market.
Uses MarketConfig to stay in sync with Arena.
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
from market_config import MarketConfig, ExecutionRouter
import json


class BabySignal:
    """Represents a signal from a baby."""
    
    def __init__(self, baby_id: str, asset: str, direction: str, qty: float, price: Optional[float] = None):
        self.baby_id = baby_id
        self.asset = asset
        self.direction = direction  # 'buy' or 'sell'
        self.qty = qty
        self.price = price  # For limit orders
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'baby_id': self.baby_id,
            'asset': self.asset,
            'direction': self.direction,
            'qty': self.qty,
            'price': self.price,
            'timestamp': self.timestamp,
        }


class BabyExecutionBridge:
    """
    Execute baby signals on the active market.
    
    Baby generates signal → BabyExecutionBridge → Active market executor
    """
    
    def __init__(self, executor_map: Dict[str, Any]):
        """
        Args:
            executor_map: {
                'coinbase': CoinbaseExecutor(),
                'polymarket': PolymarketExecutor(),
                'simulator': SimulatorExecutor(),
            }
        """
        self.executor_map = executor_map
        self.signal_history = []  # Track all signals
        self.order_history = []   # Track all orders placed
    
    def execute_baby_signal(self, baby_id: str, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Execute a baby's signal on the active market.
        
        Args:
            baby_id: Which baby generated this signal
            signal: {asset, direction, qty, price (optional)}
        
        Returns: Order confirmation or None
        """
        try:
            # Validate signal
            if not signal.get('asset'):
                print(f"[BABY EXEC] ERROR: No asset in signal from {baby_id}")
                return None
            
            if not signal.get('direction'):
                print(f"[BABY EXEC] ERROR: No direction in signal from {baby_id}")
                return None
            
            if not signal.get('qty'):
                print(f"[BABY EXEC] ERROR: No qty in signal from {baby_id}")
                return None
            
            # Check market minimum
            min_size = MarketConfig.get_min_order_size()
            if signal['qty'] < min_size:
                print(f"[BABY EXEC] WARNING: {baby_id} signal qty {signal['qty']} < min {min_size}")
                return None
            
            # Create signal object
            baby_signal = BabySignal(
                baby_id=baby_id,
                asset=signal['asset'],
                direction=signal['direction'],
                qty=signal['qty'],
                price=signal.get('price')
            )
            
            # Log signal
            self.signal_history.append(baby_signal.to_dict())
            
            # Route to active market
            active_market = MarketConfig.get_active_market()
            print(f"[BABY EXEC] {baby_id} signal → {active_market}: {signal['asset']} {signal['direction']} {signal['qty']}")
            
            order = ExecutionRouter.execute_signal(signal, self.executor_map)
            
            if order:
                # Log successful order
                order['baby_id'] = baby_id
                order['market'] = active_market
                order['timestamp'] = datetime.utcnow().isoformat()
                self.order_history.append(order)
                
                print(f"[BABY EXEC] ✓ Order placed: {baby_id} on {active_market}")
                return order
            else:
                print(f"[BABY EXEC] ✗ Order FAILED: {baby_id}")
                return None
        
        except Exception as e:
            print(f"[BABY EXEC] ERROR executing signal from {baby_id}: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_baby_signal_history(self, baby_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get signal history for a specific baby."""
        return [s for s in self.signal_history[-limit:] if s['baby_id'] == baby_id]
    
    def get_baby_order_history(self, baby_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get order history for a specific baby."""
        return [o for o in self.order_history[-limit:] if o.get('baby_id') == baby_id]
    
    def get_recent_executions(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recent executions across all babies."""
        return self.order_history[-limit:]
    
    def get_execution_stats(self) -> Dict[str, Any]:
        """Get execution statistics."""
        return {
            'total_signals': len(self.signal_history),
            'total_orders': len(self.order_history),
            'active_market': MarketConfig.get_active_market(),
            'success_rate': len(self.order_history) / max(len(self.signal_history), 1),
        }


class CoinbaseExecutor:
    """Execute orders on Coinbase."""
    
    def __init__(self, coinbase_client=None):
        self.client = coinbase_client
    
    def place_order(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Place order on Coinbase."""
        if not self.client:
            print("[COINBASE] No client configured")
            return None
        
        try:
            product_id = signal['asset']  # e.g., "BTC-USD"
            side = signal['direction'].lower()  # 'buy' or 'sell'
            size = float(signal['qty'])
            
            order = self.client.place_order(
                product_id=product_id,
                side=side,
                order_type='market',
                size=size
            )
            
            return {
                'status': 'success',
                'order_id': order.get('id'),
                'product_id': product_id,
                'side': side,
                'size': size,
                'executor': 'coinbase',
            }
        except Exception as e:
            print(f"[COINBASE] ERROR: {e}")
            return None


class SimulatorExecutor:
    """Execute orders through simulator (for testing)."""
    
    def __init__(self, simulator=None):
        self.simulator = simulator
    
    def place_order(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Place order through simulator."""
        if not self.simulator:
            print("[SIMULATOR] No simulator configured")
            return None
        
        try:
            # Execute through simulator
            trade = self.simulator.execute_trade(
                asset=signal['asset'],
                direction=signal['direction'],
                size=signal['qty'],
                price=signal.get('price'),
            )
            
            return {
                'status': 'success',
                'trade_id': trade.get('id'),
                'asset': signal['asset'],
                'direction': signal['direction'],
                'size': signal['qty'],
                'pnl': trade.get('pnl', 0),
                'executor': 'simulator',
            }
        except Exception as e:
            print(f"[SIMULATOR] ERROR: {e}")
            return None


# Future: Add PolymarketExecutor, DeribitExecutor, etc.
