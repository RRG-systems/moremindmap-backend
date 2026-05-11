#!/usr/bin/env python3
"""
Execution Enforcer — Phase 4.5
Wires money layer discipline into live execution.

NO override. NO bypass.
Every trade is gated by capital/risk rules.
"""

from typing import Dict, Tuple, Optional
from phase4_money_layer import MoneyLayer


class ExecutionEnforcer:
    """Enforces capital/risk rules on every trade execution"""
    
    def __init__(self, money_layer: MoneyLayer):
        self.money = money_layer
        self.execution_log = []
    
    def check_trade_eligibility(
        self,
        bot_id: str,
        base_size: float
    ) -> Tuple[bool, float, str]:
        """
        Check if a trade can execute.
        
        Returns:
            (can_execute, actual_size, reason)
        """
        
        # Check 1: Is there an active bot?
        if not self.money.active_bot_id:
            return False, 0.0, "No active bot. System flat."
        
        # Check 2: Is this the active bot?
        if bot_id != self.money.active_bot_id:
            return False, 0.0, f"Bot {bot_id} is not active ({self.money.active_bot_id} is)"
        
        # Check 3: Risk state allows trading?
        if self.money.risk_state == "STOP":
            return False, 0.0, f"STOP triggered. No new trades allowed."
        
        # Check 4: Get allocation
        allocation_pct = self.money.allocator.get_allocation(bot_id)
        if allocation_pct <= 0:
            return False, 0.0, f"Bot allocation is 0%. No capital."
        
        # Check 5: Calculate actual size
        if self.money.risk_state == "THROTTLE":
            size_multiplier = 0.5
            reason_suffix = " (throttled 50%)"
        else:
            size_multiplier = 1.0
            reason_suffix = ""
        
        actual_size = base_size * (allocation_pct / 100.0) * size_multiplier
        
        return True, actual_size, f"Trade allowed. Size: {actual_size:.4f} ({allocation_pct}% alloc × {size_multiplier}x risk){reason_suffix}"
    
    def execute_trade(
        self,
        bot_id: str,
        base_size: float,
        trade_details: Dict
    ) -> Dict:
        """
        Execute a trade under capital/risk enforcement.
        
        Returns:
            execution result with actual size
        """
        
        can_execute, actual_size, reason = self.check_trade_eligibility(bot_id, base_size)
        
        result = {
            'bot_id': bot_id,
            'base_size': base_size,
            'actual_size': actual_size,
            'can_execute': can_execute,
            'reason': reason,
            'allocation_pct': self.money.allocator.get_allocation(bot_id),
            'risk_state': self.money.risk_state,
            'active_bot': self.money.active_bot_id
        }
        
        if can_execute:
            result['status'] = 'EXECUTED'
            result['trade_details'] = trade_details
            result['actual_size'] = actual_size
        else:
            result['status'] = 'BLOCKED'
            result['reason'] = reason
        
        self.execution_log.append(result)
        return result
    
    def get_execution_log(self, limit: int = 20) -> list:
        """Get recent execution decisions"""
        return self.execution_log[-limit:]


if __name__ == '__main__':
    from capital_allocator import CapitalAllocator
    from promotion_gate import PromotionGate
    from control_layer import ControlLayer
    from pathlib import Path
    
    print("\n" + "=" * 80)
    print("Execution Enforcer Test")
    print("=" * 80)
    
    # Setup
    money = MoneyLayer(Path.cwd())
    enforcer = ExecutionEnforcer(money)
    
    # Test 1: No active bot
    print("\n[TEST 1] No active bot")
    can_exec, size, reason = enforcer.check_trade_eligibility("bot-001", 1.0)
    print(f"Can execute: {can_exec}")
    print(f"Reason: {reason}")
    
    # Test 2: Promote a bot
    print("\n[TEST 2] Promote bot and execute trade")
    money.active_bot_id = "bot-001"
    money.allocator.allocate_promoted_bot("bot-001")
    can_exec, size, reason = enforcer.check_trade_eligibility("bot-001", 1.0)
    print(f"Can execute: {can_exec}")
    print(f"Actual size: {size:.4f} (from base 1.0)")
    print(f"Reason: {reason}")
    
    # Test 3: Trade execution
    print("\n[TEST 3] Trade execution logging")
    result = enforcer.execute_trade("bot-001", 1.0, {'side': 'long', 'price': 100.0})
    print(f"Status: {result['status']}")
    print(f"Actual size: {result['actual_size']:.4f}")
    
    # Test 4: THROTTLE reduces size
    print("\n[TEST 4] THROTTLE reduces size")
    money.risk_state = "THROTTLE"
    can_exec, size, reason = enforcer.check_trade_eligibility("bot-001", 1.0)
    print(f"Can execute: {can_exec}")
    print(f"Actual size: {size:.4f} (throttled 50%)")
    
    # Test 5: STOP blocks
    print("\n[TEST 5] STOP blocks trades")
    money.risk_state = "STOP"
    can_exec, size, reason = enforcer.check_trade_eligibility("bot-001", 1.0)
    print(f"Can execute: {can_exec}")
    print(f"Reason: {reason}")
    
    print("\n" + "=" * 80)
