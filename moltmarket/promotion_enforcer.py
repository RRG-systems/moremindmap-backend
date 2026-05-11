#!/usr/bin/env python3
"""
Promotion Enforcer — Phase 4.5
Blocks any promotion that doesn't pass ALL gates.
NO bypass. NO force promote.
"""

from typing import Dict, Tuple
from promotion_gate import PromotionGate
from phase4_money_layer import MoneyLayer


class PromotionEnforcer:
    """Enforces promotion discipline"""
    
    def __init__(self, promotion_gate: PromotionGate, money_layer: MoneyLayer):
        self.gate = promotion_gate
        self.money = money_layer
        self.promotion_log = []
    
    def can_promote(
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
        Check if promotion is allowed.
        
        If any gate fails, promotion is BLOCKED.
        No override. No "force promote" option.
        
        Returns:
            (promotion_allowed, detailed_results)
        """
        
        allowed, results = self.gate.check_promotion_readiness(
            bot_id=bot_id,
            trade_count=trade_count,
            survival_pct=survival_pct,
            max_drawdown=max_drawdown,
            divergence=divergence,
            trajectory=trajectory,
            hypothesis_status=hypothesis_status,
            avg_pnl_bps=avg_pnl_bps
        )
        
        # Log attempt
        self.promotion_log.append({
            'bot_id': bot_id,
            'allowed': allowed,
            'gate_summary': results['gate_summary'],
            'timestamp': results['timestamp']
        })
        
        return allowed, results
    
    def promote_bot(
        self,
        bot_id: str,
        metrics: Dict
    ) -> Dict:
        """
        Attempt to promote a bot.
        
        If gates pass: promote and allocate.
        If gates fail: return error with reasons.
        """
        
        # Run gate check
        allowed, results = self.can_promote(
            bot_id=bot_id,
            trade_count=metrics['trade_count'],
            survival_pct=metrics['survival_pct'],
            max_drawdown=metrics['max_drawdown'],
            divergence=metrics['divergence'],
            trajectory=metrics['trajectory'],
            hypothesis_status=metrics['hypothesis_status'],
            avg_pnl_bps=metrics['avg_pnl_bps']
        )
        
        if not allowed:
            # BLOCKED
            failed_gates = [k for k, v in results['checks'].items() if not v['pass']]
            return {
                'status': 'PROMOTION_BLOCKED',
                'bot_id': bot_id,
                'reason': results['gate_summary'],
                'failed_gates': failed_gates,
                'details': results['checks'],
                'timestamp': results['timestamp']
            }
        
        # ALLOWED: Promote and allocate
        promo_result = self.money.promote_bot(bot_id)
        
        return {
            'status': 'PROMOTION_SUCCESS',
            'bot_id': bot_id,
            'allocation': promo_result['allocation'],
            'reason': 'All gates passed. Promoted with 1% initial allocation.',
            'active_bot': self.money.active_bot_id,
            'timestamp': promo_result['timestamp']
        }
    
    def get_promotion_log(self, limit: int = 20) -> list:
        """Get recent promotion attempts"""
        return self.promotion_log[-limit:]


if __name__ == '__main__':
    from pathlib import Path
    
    print("\n" + "=" * 80)
    print("Promotion Enforcer Test")
    print("=" * 80)
    
    gate = PromotionGate()
    money = MoneyLayer(Path.cwd())
    enforcer = PromotionEnforcer(gate, money)
    
    # Test 1: Good bot (should promote)
    print("\n[TEST 1] Good bot (should PROMOTE)")
    result = enforcer.promote_bot(
        "bot-good-001",
        {
            'trade_count': 35,
            'survival_pct': 93.0,
            'max_drawdown': 6.5,
            'divergence': 2.5,
            'trajectory': 'IMPROVING',
            'hypothesis_status': 'promising',
            'avg_pnl_bps': 20.0
        }
    )
    print(f"Status: {result['status']}")
    print(f"Allocation: {result.get('allocation', {}).get('allocation_pct')}%")
    print(f"Active bot: {result.get('active_bot')}")
    
    # Test 2: Bad bot (should block)
    print("\n[TEST 2] Bad bot (should BLOCK)")
    result = enforcer.promote_bot(
        "bot-bad-001",
        {
            'trade_count': 15,
            'survival_pct': 80.0,
            'max_drawdown': 12.0,
            'divergence': 8.0,
            'trajectory': 'DEGRADING',
            'hypothesis_status': 'weak',
            'avg_pnl_bps': -50.0
        }
    )
    print(f"Status: {result['status']}")
    print(f"Reason: {result['reason']}")
    print(f"Failed gates: {result.get('failed_gates', [])}")
    
    # Test 3: Barely passes
    print("\n[TEST 3] Barely passes")
    result = enforcer.promote_bot(
        "bot-marginal-001",
        {
            'trade_count': 30,
            'survival_pct': 90.0,
            'max_drawdown': 10.0,
            'divergence': 5.0,
            'trajectory': 'STABLE',
            'hypothesis_status': 'testing',
            'avg_pnl_bps': -95.0
        }
    )
    print(f"Status: {result['status']}")
    
    print("\n" + "=" * 80)
