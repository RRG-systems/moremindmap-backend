#!/usr/bin/env python3
"""
Replacement Logic — Phase 4.5 (CRITICAL)
When active bot dies, automatic fallback to next viable candidate.

Rules:
- If active bot → STOP or allocation = 0
- → Find best PASSING candidate
- → Auto-promote or require confirmation (configurable)
- → Start at 1% allocation
- → If no candidates → FLAT (no trading)
"""

from typing import Dict, List, Optional, Tuple
from phase4_money_layer import MoneyLayer


class ReplacementLogic:
    """Handles bot replacement when active bot fails"""
    
    def __init__(self, money_layer: MoneyLayer, auto_promote: bool = False):
        self.money = money_layer
        self.auto_promote = auto_promote  # True = auto-replace, False = require confirm
        self.candidate_pool = []  # Bots that PASS promotion gate
        self.replacement_log = []
    
    def register_candidate(self, bot_id: str, promotion_result: Dict) -> None:
        """
        Register a bot as a potential replacement candidate.
        
        Args:
            bot_id: Bot ID
            promotion_result: Result from promotion_gate.check_promotion_readiness
        """
        
        if promotion_result.get('promotion_allowed'):
            self.candidate_pool.append({
                'bot_id': bot_id,
                'gates_passed': promotion_result.get('gate_summary'),
                'metrics': {
                    'survival': promotion_result['checks']['survival']['actual'],
                    'drawdown': promotion_result['checks']['max_drawdown']['actual'],
                    'trades': promotion_result['checks']['trade_count']['actual'],
                },
                'score': self._score_bot(promotion_result),
                'registered_at': promotion_result['timestamp']
            })
    
    def _score_bot(self, promotion_result: Dict) -> float:
        """
        Score a bot for replacement ranking.
        Higher score = better candidate.
        
        Scoring: survival (40%) + low_drawdown (30%) + trade_count (30%)
        """
        
        survival = float(promotion_result['checks']['survival']['actual'].rstrip('%'))
        drawdown = float(promotion_result['checks']['max_drawdown']['actual'].rstrip('%'))
        trades = promotion_result['checks']['trade_count']['actual']
        
        # Normalize scores (0-100)
        survival_score = survival  # Already 0-100
        drawdown_score = max(0, 100 - drawdown * 5)  # Lower DD = better
        trade_score = min(100, (trades / 50) * 100)  # More trades = better (cap at 50)
        
        # Weighted score
        score = (survival_score * 0.4) + (drawdown_score * 0.3) + (trade_score * 0.3)
        
        return score
    
    def get_best_candidate(self) -> Optional[Dict]:
        """Get highest-scoring replacement candidate"""
        if not self.candidate_pool:
            return None
        
        return max(self.candidate_pool, key=lambda x: x['score'])
    
    def check_active_bot_health(
        self,
        active_bot_id: str,
        allocation_pct: float,
        risk_state: str
    ) -> Tuple[bool, str]:
        """
        Check if active bot needs replacement.
        
        Returns:
            (needs_replacement, reason)
        """
        
        if not active_bot_id:
            return False, "No active bot"
        
        # Trigger 1: STOP state
        if risk_state == "STOP":
            return True, f"Active bot in STOP state (unrecoverable)"
        
        # Trigger 2: Zero allocation
        if allocation_pct <= 0:
            return True, f"Active bot allocation killed (0%)"
        
        return False, "Active bot healthy"
    
    def trigger_replacement(
        self,
        old_bot_id: str,
        reason: str
    ) -> Dict:
        """
        Trigger replacement process.
        
        If auto_promote: Replace immediately.
        Else: Return replacement_required (operator confirms).
        """
        
        best = self.get_best_candidate()
        
        if not best:
            # No candidates
            result = {
                'status': 'NO_CANDIDATES',
                'old_bot': old_bot_id,
                'reason': reason,
                'action': 'SYSTEM_FLAT',
                'message': 'No replacement candidates. System goes flat (no trading).',
                'timestamp': ''
            }
        elif self.auto_promote:
            # Auto-replace
            self.money.active_bot_id = best['bot_id']
            self.money.allocator.allocations[best['bot_id']]['allocation_pct'] = 1.0  # Reset to 1%
            
            result = {
                'status': 'REPLACEMENT_AUTO',
                'old_bot': old_bot_id,
                'new_bot': best['bot_id'],
                'reason': reason,
                'score': best['score'],
                'new_allocation': 1.0,
                'action': 'ACTIVE',
                'message': f"Auto-replaced: {old_bot_id} → {best['bot_id']} (1% allocation)",
                'timestamp': ''
            }
        else:
            # Require confirmation
            result = {
                'status': 'REPLACEMENT_PENDING',
                'old_bot': old_bot_id,
                'candidate': best['bot_id'],
                'reason': reason,
                'score': best['score'],
                'action': 'AWAIT_CONFIRMATION',
                'message': f"Replacement pending: Operator confirm to replace {old_bot_id} with {best['bot_id']}",
                'timestamp': ''
            }
        
        self.replacement_log.append(result)
        return result
    
    def confirm_replacement(self, new_bot_id: str) -> Dict:
        """Operator confirms replacement"""
        
        old_bot = self.money.active_bot_id
        self.money.active_bot_id = new_bot_id
        self.money.allocator.allocations[new_bot_id]['allocation_pct'] = 1.0
        
        result = {
            'status': 'REPLACEMENT_CONFIRMED',
            'old_bot': old_bot,
            'new_bot': new_bot_id,
            'action': 'ACTIVE',
            'message': f"Replacement confirmed: {new_bot_id} now active (1%)"
        }
        
        self.replacement_log.append(result)
        return result
    
    def get_replacement_log(self, limit: int = 10) -> list:
        """Get replacement history"""
        return self.replacement_log[-limit:]


if __name__ == '__main__':
    from pathlib import Path
    from promotion_gate import PromotionGate
    
    print("\n" + "=" * 80)
    print("Replacement Logic Test")
    print("=" * 80)
    
    money = MoneyLayer(Path.cwd())
    replacement = ReplacementLogic(money, auto_promote=False)  # Require confirmation
    
    gate = PromotionGate()
    
    # Register candidates
    print("\n[SETUP] Register replacement candidates")
    
    candidates = [
        ("bot-candidate-a", {
            'trade_count': 40,
            'survival_pct': 94.0,
            'max_drawdown': 5.5,
            'divergence': 2.0,
            'trajectory': 'IMPROVING',
            'hypothesis_status': 'promising',
            'avg_pnl_bps': 25.0
        }),
        ("bot-candidate-b", {
            'trade_count': 35,
            'survival_pct': 91.0,
            'max_drawdown': 7.0,
            'divergence': 3.5,
            'trajectory': 'STABLE',
            'hypothesis_status': 'testing',
            'avg_pnl_bps': 15.0
        }),
    ]
    
    for bot_id, metrics in candidates:
        allowed, results = gate.check_promotion_readiness(
            bot_id=bot_id,
            trade_count=metrics['trade_count'],
            survival_pct=metrics['survival_pct'],
            max_drawdown=metrics['max_drawdown'],
            divergence=metrics['divergence'],
            trajectory=metrics['trajectory'],
            hypothesis_status=metrics['hypothesis_status'],
            avg_pnl_bps=metrics['avg_pnl_bps']
        )
        if allowed:
            replacement.register_candidate(bot_id, results)
    
    print(f"Registered {len(replacement.candidate_pool)} candidates")
    
    # Test 1: Active bot health check (good)
    print("\n[TEST 1] Active bot health (good)")
    needs_replace, reason = replacement.check_active_bot_health(
        active_bot_id="bot-active-001",
        allocation_pct=1.0,
        risk_state="NORMAL"
    )
    print(f"Needs replacement: {needs_replace}")
    
    # Test 2: Active bot health check (STOP)
    print("\n[TEST 2] Active bot health (STOP)")
    needs_replace, reason = replacement.check_active_bot_health(
        active_bot_id="bot-active-001",
        allocation_pct=1.0,
        risk_state="STOP"
    )
    print(f"Needs replacement: {needs_replace}")
    print(f"Reason: {reason}")
    
    # Test 3: Trigger replacement (with confirmation required)
    print("\n[TEST 3] Trigger replacement (confirm mode)")
    result = replacement.trigger_replacement(
        old_bot_id="bot-active-001",
        reason="STOP triggered"
    )
    print(f"Status: {result['status']}")
    print(f"Message: {result['message']}")
    print(f"Action: {result['action']}")
    
    # Test 4: Confirm replacement
    print("\n[TEST 4] Confirm replacement")
    money.active_bot_id = "bot-active-001"
    result = replacement.confirm_replacement("bot-candidate-a")
    print(f"Status: {result['status']}")
    print(f"New active bot: {result['new_bot']}")
    print(f"New allocation: {money.allocator.get_allocation('bot-candidate-a')}%")
    
    print("\n" + "=" * 80)
