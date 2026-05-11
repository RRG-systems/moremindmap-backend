#!/usr/bin/env python3
"""
Phase 4: Money Reality Layer
Integrates: Risk Controls + Promotion Gate + Capital Allocator

Makes the system behave like something trusted with real money.
"""

import json
from datetime import datetime
from typing import Dict, Optional, Tuple
from pathlib import Path

from control_layer import ControlLayer
from promotion_gate import PromotionGate
from capital_allocator import CapitalAllocator


class MoneyLayer:
    """Unified money reality layer"""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace = workspace_dir or Path.cwd()
        self.control = ControlLayer(self.workspace)
        self.promotion = PromotionGate()
        self.allocator = CapitalAllocator()
        self.active_bot_id = None
        self.risk_state = "NORMAL"  # NORMAL | THROTTLE | STOP
        
    def evaluate_risk_state(
        self,
        survival_pass: bool,
        max_drawdown: float,
        avg_pnl_bps: float,
        total_trades: int,
        trajectory: str,
        last_mutation_result: str = None
    ) -> Dict:
        """
        Evaluate current risk state.
        
        Returns:
            {
                'risk_state': 'NORMAL' | 'THROTTLE' | 'STOP',
                'control_action': str,
                'should_trade': bool,
                'position_size_multiplier': float (1.0 = normal, 0.5 = throttled, 0.0 = stopped)
            }
        """
        
        action, reason = self.control.classify_control_action(
            survival_pass=survival_pass,
            max_drawdown=max_drawdown,
            avg_pnl_bps=avg_pnl_bps,
            total_trades=total_trades,
            trajectory=trajectory,
            last_mutation_result=last_mutation_result or "INCONCLUSIVE"
        )
        
        # Map control action to risk state
        if action == "STOP":
            self.risk_state = "STOP"
            size_multiplier = 0.0
            should_trade = False
        elif action == "THROTTLE":
            self.risk_state = "THROTTLE"
            size_multiplier = 0.5
            should_trade = True
        else:
            self.risk_state = "NORMAL"
            size_multiplier = 1.0
            should_trade = True
        
        return {
            'risk_state': self.risk_state,
            'control_action': action,
            'reason': reason,
            'should_trade': should_trade,
            'position_size_multiplier': size_multiplier,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def check_promotion_readiness(
        self,
        bot_id: str,
        trade_count: int,
        survival_pct: float,
        max_drawdown: float,
        divergence: float,
        trajectory: str,
        hypothesis_status: str,
        avg_pnl_bps: float
    ) -> Tuple[bool, Dict]:
        """
        Check if bot is ready for promotion.
        
        Returns:
            (promotion_allowed, detailed_results)
        """
        return self.promotion.check_promotion_readiness(
            bot_id=bot_id,
            trade_count=trade_count,
            survival_pct=survival_pct,
            max_drawdown=max_drawdown,
            divergence=divergence,
            trajectory=trajectory,
            hypothesis_status=hypothesis_status,
            avg_pnl_bps=avg_pnl_bps
        )
    
    def promote_bot(self, bot_id: str) -> Dict:
        """
        Promote a bot to active status.
        
        Assumes promotion readiness already checked.
        """
        allocation = self.allocator.allocate_promoted_bot(bot_id)
        self.active_bot_id = bot_id
        
        return {
            'bot_id': bot_id,
            'status': 'PROMOTED',
            'allocation': allocation,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def update_active_bot_state(
        self,
        survival_pct: float,
        max_drawdown: float,
        trajectory: str,
        days_active: float,
        trades_in_period: int
    ) -> Dict:
        """
        Update active bot state and allocation.
        
        Returns action needed.
        """
        
        if not self.active_bot_id:
            return {'status': 'no_active_bot'}
        
        current_alloc = self.allocator.get_allocation(self.active_bot_id)
        new_alloc, reason = self.allocator.evaluate_allocation_update(
            bot_id=self.active_bot_id,
            current_allocation=current_alloc,
            survival_pct=survival_pct,
            max_drawdown=max_drawdown,
            trajectory=trajectory,
            days_active=days_active,
            trades_in_period=trades_in_period
        )
        
        # Apply update
        if new_alloc == 0.0:
            self.allocator.allocations[self.active_bot_id]['status'] = 'KILLED'
            action = 'KILL'
        elif new_alloc < current_alloc:
            action = 'REDUCE'
        elif new_alloc > current_alloc:
            action = 'GROW'
        else:
            action = 'HOLD'
        
        # Update allocation
        self.allocator.allocations[self.active_bot_id]['allocation_pct'] = new_alloc
        
        return {
            'bot_id': self.active_bot_id,
            'action': action,
            'previous_allocation': current_alloc,
            'new_allocation': new_alloc,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    def get_money_state(self, total_capital: float = 100.0) -> Dict:
        """
        Get complete money layer state.
        
        This is what the UI shows.
        """
        
        alloc_summary = self.allocator.summarize_allocations(total_capital)
        
        return {
            'risk_state': self.risk_state,
            'active_bot_id': self.active_bot_id,
            'capital': {
                'total': total_capital,
                'allocated': alloc_summary['total_allocated'],
                'available': alloc_summary['total_available'],
                'by_bot': alloc_summary['allocation_pct_by_bot']
            },
            'allocations': alloc_summary['bots'],
            'timestamp': datetime.utcnow().isoformat()
        }


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Phase 4: Money Layer Integration Test")
    print("=" * 80)
    
    money = MoneyLayer()
    
    # Test 1: Risk state evaluation
    print("\n[TEST 1] Risk state evaluation")
    risk_state = money.evaluate_risk_state(
        survival_pass=True,
        max_drawdown=7.0,
        avg_pnl_bps=15.0,
        total_trades=40,
        trajectory="IMPROVING"
    )
    print(f"Risk state: {risk_state['risk_state']}")
    print(f"Should trade: {risk_state['should_trade']}")
    print(f"Size multiplier: {risk_state['position_size_multiplier']}")
    
    # Test 2: Promotion check
    print("\n[TEST 2] Promotion readiness")
    can_promote, results = money.check_promotion_readiness(
        bot_id="bot-001",
        trade_count=35,
        survival_pct=93.0,
        max_drawdown=6.5,
        divergence=2.5,
        trajectory="IMPROVING",
        hypothesis_status="promising",
        avg_pnl_bps=20.0
    )
    print(f"Can promote: {can_promote}")
    print(f"Summary: {results['gate_summary']}")
    
    # Test 3: Promote and allocate
    print("\n[TEST 3] Promote and allocate")
    if can_promote:
        promo = money.promote_bot("bot-001")
        print(f"Bot promoted: {promo['bot_id']}")
        print(f"Initial allocation: {promo['allocation']['allocation_pct']}%")
    
    # Test 4: Update active bot (good performance)
    print("\n[TEST 4] Update active bot (good performance)")
    update = money.update_active_bot_state(
        survival_pct=95.0,
        max_drawdown=4.0,
        trajectory="IMPROVING",
        days_active=4.0,
        trades_in_period=25
    )
    print(f"Action: {update['action']}")
    print(f"New allocation: {update['new_allocation']}% (from {update['previous_allocation']}%)")
    
    # Test 5: Update active bot (degradation)
    print("\n[TEST 5] Update active bot (degradation)")
    update = money.update_active_bot_state(
        survival_pct=80.0,
        max_drawdown=9.0,
        trajectory="DEGRADING",
        days_active=5.0,
        trades_in_period=15
    )
    print(f"Action: {update['action']}")
    print(f"New allocation: {update['new_allocation']}% (from {update['previous_allocation']}%)")
    
    # Test 6: Money state display
    print("\n[TEST 6] Money state display")
    state = money.get_money_state(total_capital=100.0)
    print(f"Risk state: {state['risk_state']}")
    print(f"Active bot: {state['active_bot_id']}")
    print(f"Capital allocated: {state['capital']['allocated']:.1f}% / {state['capital']['total']:.0f}k")
    print(f"Capital available: {state['capital']['available']:.1f}% / {state['capital']['total']:.0f}k")
    
    print("\n" + "=" * 80)
