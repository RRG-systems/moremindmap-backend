"""
Unified Execution Pipeline — Market-Agnostic, Single Source of Truth

All trades (Arena + Babies) flow through ONE pipeline.
Reads active market from MarketConfig.
Single ledger, no sync issues, future-proof.

When market changes: update one line, everything adapts.
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
from market_config import MarketConfig
import json


class TradeRecord:
    """Single trade record (compatible with all markets)."""
    
    def __init__(self, source: str, trader_id: str, asset: str, side: str, 
                 entry_price: float, exit_price: float, size: float = 1.0,
                 pnl: float = 0.0, pnl_bps: float = 0.0):
        self.source = source  # 'arena' or 'baby_<id>'
        self.trader_id = trader_id  # Arena ID or Baby variant_id
        self.asset = asset
        self.side = side  # 'long' or 'short'
        self.entry_price = entry_price
        self.exit_price = exit_price
        self.size = size
        self.pnl = pnl  # In dollars
        self.pnl_bps = pnl_bps  # In basis points
        self.timestamp = datetime.utcnow().isoformat()
        self.market = MarketConfig.get_active_market()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'source': self.source,
            'trader_id': self.trader_id,
            'asset': self.asset,
            'side': self.side,
            'entry_price': self.entry_price,
            'exit_price': self.exit_price,
            'size': self.size,
            'pnl': self.pnl,
            'pnl_bps': self.pnl_bps,
            'timestamp': self.timestamp,
            'market': self.market,
        }


class UnifiedLedger:
    """
    Single source of truth for all trades (Arena + Babies).
    
    No sync issues. One place to read from.
    Automatically reads market from MarketConfig.
    """
    
    def __init__(self):
        self.trades: List[TradeRecord] = []
        self.trader_pnl: Dict[str, float] = {}  # Cumulative PnL per trader
        self.trader_trades: Dict[str, int] = {}  # Trade count per trader
    
    def record_trade(self, trade: TradeRecord) -> None:
        """Record a single trade."""
        self.trades.append(trade)
        
        # Update aggregates
        if trade.trader_id not in self.trader_pnl:
            self.trader_pnl[trade.trader_id] = 0.0
            self.trader_trades[trade.trader_id] = 0
        
        self.trader_pnl[trade.trader_id] += trade.pnl
        self.trader_trades[trade.trader_id] += 1
        
        print(f"[LEDGER] {trade.source} ({trade.trader_id}): {trade.asset} {trade.side} | "
              f"PnL: ${trade.pnl:.2f} ({trade.pnl_bps:.1f} bps) | "
              f"Cumulative: ${self.trader_pnl[trade.trader_id]:.2f}")
    
    def get_trader_metrics(self, trader_id: str) -> Dict[str, Any]:
        """Get metrics for a specific trader (Arena or Baby)."""
        trades = [t for t in self.trades if t.trader_id == trader_id]
        
        if not trades:
            return {
                'trader_id': trader_id,
                'total_trades': 0,
                'total_pnl': 0.0,
                'shadow_pnl': 0.0,  # Compatible with baby metrics
                'win_rate': 0.0,
                'win_count': 0,
                'loss_count': 0,
            }
        
        pnl = sum(t.pnl for t in trades)
        wins = sum(1 for t in trades if t.pnl > 0)
        losses = sum(1 for t in trades if t.pnl < 0)
        
        return {
            'trader_id': trader_id,
            'total_trades': len(trades),
            'total_pnl': pnl,
            'shadow_pnl': pnl,  # Unified: shadow PnL is the truth
            'win_rate': (wins / len(trades) * 100) if trades else 0.0,
            'win_count': wins,
            'loss_count': losses,
        }
    
    def get_all_trades(self, source: Optional[str] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent trades, optionally filtered by source."""
        if source:
            trades = [t for t in self.trades if t.source == source]
        else:
            trades = self.trades
        
        return [t.to_dict() for t in trades[-limit:]]
    
    def get_recent_trades_by_trader(self, trader_id: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Get recent trades for a specific trader."""
        trades = [t for t in self.trades if t.trader_id == trader_id]
        return [t.to_dict() for t in trades[-limit:]]
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get state of current active market."""
        return {
            'active_market': MarketConfig.get_active_market(),
            'total_trades': len(self.trades),
            'traders': len(self.trader_pnl),
            'total_pnl': sum(self.trader_pnl.values()),
            'trader_breakdown': {
                trader_id: {
                    'pnl': pnl,
                    'trades': self.trader_trades[trader_id],
                }
                for trader_id, pnl in self.trader_pnl.items()
            }
        }


class UnifiedExecutor:
    """
    Execute signals from Arena and Babies through one pipeline.
    
    All execution goes through here.
    Automatically uses active market from MarketConfig.
    Single ledger output.
    """
    
    def __init__(self, market_executors: Dict[str, Any], unified_ledger: UnifiedLedger):
        """
        Args:
            market_executors: {
                'coinbase': CoinbaseExecutor(),
                'polymarket': PolymarketExecutor(),
                'simulator': SimulatorExecutor(),
            }
            unified_ledger: Single source of truth
        """
        self.market_executors = market_executors
        self.ledger = unified_ledger
    
    def execute_signal(self, source: str, trader_id: str, signal: Dict[str, Any]) -> Optional[TradeRecord]:
        """
        Execute a signal (from Arena or Baby).
        
        Args:
            source: 'arena' or 'baby_<id>'
            trader_id: Arena ID or Baby variant_id
            signal: {asset, side, entry_price, exit_price, size}
        
        Returns: TradeRecord or None
        """
        try:
            # Get active market
            market = MarketConfig.get_active_market()
            executor = self.market_executors.get(market)
            
            if not executor:
                print(f"[EXECUTOR] ERROR: No executor for market '{market}'")
                return None
            
            # Execute on the active market
            result = executor.execute(signal)
            
            if not result:
                print(f"[EXECUTOR] Execution failed on {market}")
                return None
            
            # Create trade record
            trade = TradeRecord(
                source=source,
                trader_id=trader_id,
                asset=signal['asset'],
                side=signal['side'],
                entry_price=result['entry_price'],
                exit_price=result['exit_price'],
                size=result.get('size', 1.0),
                pnl=result['pnl'],
                pnl_bps=result['pnl_bps']
            )
            
            # Record in unified ledger
            self.ledger.record_trade(trade)
            
            return trade
        
        except Exception as e:
            print(f"[EXECUTOR] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def get_trader_metrics(self, trader_id: str) -> Dict[str, Any]:
        """Get metrics for Arena or Baby (read from unified ledger)."""
        return self.ledger.get_trader_metrics(trader_id)
    
    def get_market_state(self) -> Dict[str, Any]:
        """Get current market state."""
        return self.ledger.get_market_state()


class SimulatorExecutor:
    """Execute through simulator (for testing/paper trading)."""
    
    def __init__(self, simulator):
        self.simulator = simulator
    
    def execute(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Execute signal through simulator."""
        try:
            # Get simulated fills
            entry = signal['entry_price'] * (1 + 0.0001)  # +1 bp slippage
            # Use signal's exit_price if provided (for parity), else get from simulator
            if 'exit_price' in signal and signal['exit_price']:
                exit_price = signal['exit_price']
            else:
                exit_price = self.simulator._get_price(signal['asset'])
            exit_fill = exit_price * (1 - 0.0001)  # -1 bp slippage
            
            # Calculate PnL
            if signal['side'] == 'long':
                pnl_dollars = (exit_fill - entry) * signal.get('size', 1.0)
                pnl_bps = (exit_fill - entry) / entry * 10000
            else:
                pnl_dollars = (entry - exit_fill) * signal.get('size', 1.0)
                pnl_bps = (entry - exit_fill) / entry * 10000
            
            return {
                'entry_price': entry,
                'exit_price': exit_fill,
                'size': signal.get('size', 1.0),
                'pnl': pnl_dollars,
                'pnl_bps': pnl_bps,
                'market': 'simulator',
            }
        except Exception as e:
            print(f"[SIMULATOR EXECUTOR] ERROR: {e}")
            return None


# TODO: Add PolymarketExecutor, DeribitExecutor, etc.
# Each follows same interface: execute(signal) -> {entry_price, exit_price, size, pnl, pnl_bps}
