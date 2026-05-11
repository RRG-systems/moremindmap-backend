#!/usr/bin/env python3
"""
Capital Allocator — Phase 4
Simple first allocator: enforce discipline, not complexity.

Rules:
- Promoted bots start with SMALL allocation
- Allocation grows only with sustained performance
- Allocation cuts immediately on failure
- No large initial sizing
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from pathlib import Path


class CapitalAllocator:
    """Simple, rules-based capital allocation"""
    
    # Initial allocation for promoted bot
    INITIAL_ALLOCATION = 1.0  # 1% of capital
    
    # Growth increments
    GROWTH_INCREMENT = 0.5  # 0.5% per period
    MAX_ALLOCATION_PER_BOT = 5.0  # 5% max per bot
    
    # Reduction thresholds
    SURVIVAL_WARNING = 85.0  # % — start reducing
    SURVIVAL_CRITICAL = 70.0  # % — kill it
    DRAWDOWN_WARNING = 8.0  # % — reduce
    DRAWDOWN_CRITICAL = 12.0  # % — stop
    
    # Validation period (how long before allowing growth)
    VALIDATION_PERIOD_DAYS = 3
    MIN_TRADES_FOR_GROWTH = 20
    
    def __init__(self):
        self.allocations = {}  # bot_id -> allocation_pct
    
    def allocate_promoted_bot(self, bot_id: str, parent_bot_id: str = None) -> Dict:
        """
        Allocate capital to newly promoted bot.
        
        Starts SMALL. Grows only with proof.
        
        Args:
            bot_id: New promoted bot
            parent_bot_id: Previous active bot (if any)
        
        Returns:
            allocation info
        """
        
        allocation = {
            'bot_id': bot_id,
            'allocation_pct': self.INITIAL_ALLOCATION,
            'status': 'ACTIVE',
            'promoted_at': datetime.utcnow().isoformat(),
            'validation_period_ends': (datetime.utcnow() + timedelta(days=self.VALIDATION_PERIOD_DAYS)).isoformat(),
            'reason': f"Promoted: starting allocation {self.INITIAL_ALLOCATION}% (validation period {self.VALIDATION_PERIOD_DAYS}d)"
        }
        
        self.allocations[bot_id] = allocation
        
        return allocation
    
    def evaluate_allocation_update(
        self,
        bot_id: str,
        current_allocation: float,
        survival_pct: float,
        max_drawdown: float,
        trajectory: str,
        days_active: float,
        trades_in_period: int
    ) -> Tuple[float, str]:
        """
        Evaluate if allocation should grow, hold, or shrink.
        
        Args:
            bot_id: Bot to evaluate
            current_allocation: Current allocation %
            survival_pct: Survival percentage (0-100)
            max_drawdown: Maximum drawdown %
            trajectory: IMPROVING | DEGRADING | STABLE
            days_active: Days since promotion
            trades_in_period: Trades in this period
        
        Returns:
            (new_allocation, reason)
        """
        
        # Priority 1: CRITICAL failures → reduce or kill
        if survival_pct < self.SURVIVAL_CRITICAL:
            new_alloc = 0.0
            return new_alloc, f"KILL: Survival critical ({survival_pct:.1f}%)"
        
        if max_drawdown > self.DRAWDOWN_CRITICAL:
            new_alloc = 0.0
            return new_alloc, f"KILL: Drawdown critical ({max_drawdown:.1f}%)"
        
        # Priority 2: Warnings → reduce
        if survival_pct < self.SURVIVAL_WARNING:
            new_alloc = current_allocation * 0.5
            return new_alloc, f"REDUCE 50%: Survival warning ({survival_pct:.1f}%)"
        
        if max_drawdown > self.DRAWDOWN_WARNING:
            new_alloc = current_allocation * 0.7
            return new_alloc, f"REDUCE 30%: Drawdown warning ({max_drawdown:.1f}%)"
        
        if trajectory == "DEGRADING":
            new_alloc = current_allocation * 0.8
            return new_alloc, f"REDUCE 20%: Degrading trajectory"
        
        # Priority 3: Growth conditions
        # Only grow if:
        # - validation period ended
        # - sustained performance
        # - enough trades
        # - not at max
        
        if (days_active >= self.VALIDATION_PERIOD_DAYS and
            survival_pct >= 92.0 and
            max_drawdown < 6.0 and
            trajectory in ["IMPROVING", "STABLE"] and
            trades_in_period >= self.MIN_TRADES_FOR_GROWTH and
            current_allocation < self.MAX_ALLOCATION_PER_BOT):
            
            new_alloc = min(
                current_allocation + self.GROWTH_INCREMENT,
                self.MAX_ALLOCATION_PER_BOT
            )
            return new_alloc, f"GROW +{self.GROWTH_INCREMENT}%: Sustained performance ({days_active:.1f}d, {trades_in_period} trades)"
        
        # Default: hold
        return current_allocation, f"HOLD: {days_active:.1f}d active, survival {survival_pct:.1f}%, dd {max_drawdown:.1f}%"
    
    def get_allocation(self, bot_id: str) -> float:
        """Get current allocation for bot"""
        return self.allocations.get(bot_id, {}).get('allocation_pct', 0.0)
    
    def get_total_allocated(self) -> float:
        """Get total allocation across all bots"""
        return sum(alloc.get('allocation_pct', 0.0) for alloc in self.allocations.values() if alloc.get('status') == 'ACTIVE')
    
    def get_capital_available(self, total_capital: float = 100.0) -> float:
        """Get unallocated capital"""
        return total_capital - self.get_total_allocated()
    
    def summarize_allocations(self, total_capital: float = 100.0) -> Dict:
        """Get full allocation summary"""
        active_bots = [b for b in self.allocations.values() if b.get('status') == 'ACTIVE']
        total_alloc = sum(b.get('allocation_pct', 0.0) for b in active_bots)
        
        return {
            'total_capital': total_capital,
            'active_bots': len(active_bots),
            'total_allocated': total_alloc,
            'total_available': total_capital - total_alloc,
            'bots': active_bots,
            'allocation_pct_by_bot': {b['bot_id']: b['allocation_pct'] for b in active_bots}
        }


if __name__ == '__main__':
    allocator = CapitalAllocator()
    
    print("\n" + "=" * 80)
    print("Capital Allocator Test")
    print("=" * 80)
    
    # Test 1: Promote bot
    print("\n[TEST 1] Promote new bot")
    alloc = allocator.allocate_promoted_bot("bot-promoted-001")
    print(f"Bot: {alloc['bot_id']}")
    print(f"Initial allocation: {alloc['allocation_pct']}%")
    print(f"Reason: {alloc['reason']}")
    
    # Test 2: Evaluate after validation period with good performance
    print("\n[TEST 2] Grow allocation after validation")
    new_alloc, reason = allocator.evaluate_allocation_update(
        bot_id="bot-promoted-001",
        current_allocation=1.0,
        survival_pct=95.0,
        max_drawdown=4.0,
        trajectory="IMPROVING",
        days_active=4.0,
        trades_in_period=25
    )
    print(f"New allocation: {new_alloc}% (from 1.0%)")
    print(f"Reason: {reason}")
    
    # Test 3: Reduce on degradation
    print("\n[TEST 3] Reduce on degradation")
    new_alloc, reason = allocator.evaluate_allocation_update(
        bot_id="bot-promoted-001",
        current_allocation=2.0,
        survival_pct=82.0,
        max_drawdown=9.0,
        trajectory="DEGRADING",
        days_active=5.0,
        trades_in_period=15
    )
    print(f"New allocation: {new_alloc}% (from 2.0%)")
    print(f"Reason: {reason}")
    
    # Test 4: Kill on critical
    print("\n[TEST 4] Kill on critical failure")
    new_alloc, reason = allocator.evaluate_allocation_update(
        bot_id="bot-promoted-001",
        current_allocation=1.5,
        survival_pct=65.0,
        max_drawdown=15.0,
        trajectory="DEGRADING",
        days_active=5.0,
        trades_in_period=10
    )
    print(f"New allocation: {new_alloc}% (from 1.5%)")
    print(f"Reason: {reason}")
    
    # Test 5: Summary
    print("\n[TEST 5] Summary")
    allocator.allocate_promoted_bot("bot-a")
    allocator.allocate_promoted_bot("bot-b")
    summary = allocator.summarize_allocations(total_capital=100.0)
    print(f"Total capital: ${summary['total_capital']:.0f}k")
    print(f"Active bots: {summary['active_bots']}")
    print(f"Allocated: {summary['total_allocated']:.1f}%")
    print(f"Available: {summary['total_available']:.1f}%")
    
    print("\n" + "=" * 80)
