"""
Market Configuration Layer — Single Source of Truth

Arena and Nursery babies both read from this. Change one value, everything adapts.
No hardcoding. No divergence. Market-agnostic execution.
"""

from enum import Enum
from typing import Dict, Any, Optional


class SupportedMarkets(Enum):
    """Supported execution venues."""
    COINBASE = "coinbase"
    POLYMARKET = "polymarket"
    DERIBIT = "deribit"
    SIMULATOR = "simulator"  # For testing


class MarketConfig:
    """
    Single source of truth for which market is active.
    
    Arena reads this. Babies read this. They stay in sync.
    """
    
    # Current active market
    _active_market = SupportedMarkets.COINBASE
    
    # Market-specific configs
    _market_configs = {
        SupportedMarkets.COINBASE: {
            'name': 'coinbase',
            'assets': ['BTC-USD', 'ETH-USD'],
            'min_order_size': 0.001,
            'order_type': 'market',
            'requires_auth': True,
        },
        SupportedMarkets.POLYMARKET: {
            'name': 'polymarket',
            'assets': ['outcomes-list'],  # Polymarket uses outcome IDs
            'min_order_size': 0.01,
            'order_type': 'limit',
            'requires_auth': True,
        },
        SupportedMarkets.DERIBIT: {
            'name': 'deribit',
            'assets': ['BTC_USD', 'ETH_USD'],
            'min_order_size': 0.001,
            'order_type': 'market',
            'requires_auth': True,
        },
        SupportedMarkets.SIMULATOR: {
            'name': 'simulator',
            'assets': ['BTC', 'ETH'],
            'min_order_size': 0.001,
            'order_type': 'market',
            'requires_auth': False,
        },
    }
    
    @classmethod
    def get_active_market(cls) -> str:
        """Get current active market name."""
        return cls._active_market.value
    
    @classmethod
    def set_active_market(cls, market: str) -> bool:
        """Switch to a different market. Returns True if successful."""
        try:
            # Try to find matching market
            for supported in SupportedMarkets:
                if supported.value == market.lower():
                    cls._active_market = supported
                    print(f"[MARKET] Switched to {market}")
                    return True
            print(f"[MARKET] ERROR: Unknown market '{market}'")
            return False
        except Exception as e:
            print(f"[MARKET] ERROR switching market: {e}")
            return False
    
    @classmethod
    def get_market_config(cls) -> Dict[str, Any]:
        """Get configuration for current active market."""
        return cls._market_configs[cls._active_market].copy()
    
    @classmethod
    def get_assets(cls) -> list:
        """Get supported assets for current market."""
        return cls._market_configs[cls._active_market]['assets']
    
    @classmethod
    def get_min_order_size(cls) -> float:
        """Get minimum order size for current market."""
        return cls._market_configs[cls._active_market]['min_order_size']
    
    @classmethod
    def get_order_type(cls) -> str:
        """Get default order type for current market."""
        return cls._market_configs[cls._active_market]['order_type']
    
    @classmethod
    def requires_auth(cls) -> bool:
        """Does current market require API auth?"""
        return cls._market_configs[cls._active_market]['requires_auth']
    
    @classmethod
    def is_simulator(cls) -> bool:
        """Is simulator mode active?"""
        return cls._active_market == SupportedMarkets.SIMULATOR
    
    @classmethod
    def is_live_market(cls) -> bool:
        """Is this a live market (not simulator)?"""
        return not cls.is_simulator()


class ExecutionRouter:
    """Route orders to the correct market."""
    
    @staticmethod
    def execute_signal(signal: Dict[str, Any], executor_map: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Route a signal to the correct executor based on active market.
        
        Args:
            signal: {asset, direction, qty, price (optional)}
            executor_map: {
                'coinbase': CoinbaseExecutor,
                'polymarket': PolymarketExecutor,
                'simulator': SimulatorExecutor,
                ...
            }
        
        Returns: Order result or None if failed
        """
        active_market = MarketConfig.get_active_market()
        executor = executor_map.get(active_market)
        
        if not executor:
            print(f"[ROUTER] ERROR: No executor for market '{active_market}'")
            return None
        
        try:
            order = executor.place_order(signal)
            print(f"[ROUTER] Order placed on {active_market}: {order}")
            return order
        except Exception as e:
            print(f"[ROUTER] ERROR executing on {active_market}: {e}")
            return None


# Initialize
print(f"[MARKET CONFIG] Initialized. Active market: {MarketConfig.get_active_market()}")
