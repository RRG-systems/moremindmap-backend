#!/usr/bin/env python3
"""
Promotion Gate — Phase 4
Hard discipline for promoting babies to active status.

NO discretionary "it feels good" logic.
Only promotion if ALL gates pass.
"""

import json
from datetime import datetime
from typing import Dict, List, Tuple
from pathlib import Path


class PromotionGate:
    """Enforces strict promotion requirements"""
    
    # Minimum requirements
    MIN_TRADE_COUNT = 30
    MIN_SURVIVAL_THRESHOLD = 90.0  # %
    MAX_DRAWDOWN_ACCEPTABLE = 10.0  # %
    MAX_DIVERGENCE_ACCEPTABLE = 5.0  # %
    TRAJECTORY_ACCEPTABLE = ["IMPROVING", "STABLE"]
    
    def __init__(self):
        pass
    
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
        Check if a bot is ready for promotion.
        
        ALL gates must pass. If any fail, promotion is rejected.
        
        Args:
            bot_id: Bot identifier
            trade_count: Total trades executed
            survival_pct: Survival percentage (0-100)
            max_drawdown: Maximum drawdown (%)
            divergence: Paper-shadow divergence (%)
            trajectory: "IMPROVING" | "DEGRADING" | "STABLE"
            hypothesis_status: "testing" | "promising" | "weak" | "broken"
            avg_pnl_bps: Average PnL in basis points
        
        Returns:
            (promotion_allowed, detailed_results)
        """
        
        results = {
            'bot_id': bot_id,
            'timestamp': datetime.utcnow().isoformat(),
            'checks': {}
        }
        
        all_pass = True
        
        # Check 1: Minimum trade count
        trade_check = trade_count >= self.MIN_TRADE_COUNT
        results['checks']['trade_count'] = {
            'pass': trade_check,
            'requirement': f">= {self.MIN_TRADE_COUNT}",
            'actual': trade_count,
            'message': 'Sample size sufficient' if trade_check else f'Insufficient data ({trade_count}/{self.MIN_TRADE_COUNT})'
        }
        if not trade_check:
            all_pass = False
        
        # Check 2: Survival gate
        survival_check = survival_pct >= self.MIN_SURVIVAL_THRESHOLD
        results['checks']['survival'] = {
            'pass': survival_check,
            'requirement': f">= {self.MIN_SURVIVAL_THRESHOLD}%",
            'actual': f"{survival_pct:.1f}%",
            'message': 'Acceptable loss profile' if survival_check else f'Unacceptable loss profile ({survival_pct:.1f}%)'
        }
        if not survival_check:
            all_pass = False
        
        # Check 3: Drawdown limit
        drawdown_check = max_drawdown <= self.MAX_DRAWDOWN_ACCEPTABLE
        results['checks']['max_drawdown'] = {
            'pass': drawdown_check,
            'requirement': f"<= {self.MAX_DRAWDOWN_ACCEPTABLE}%",
            'actual': f"{max_drawdown:.1f}%",
            'message': 'Drawdown within limits' if drawdown_check else f'Drawdown exceeds limit ({max_drawdown:.1f}%)'
        }
        if not drawdown_check:
            all_pass = False
        
        # Check 4: Divergence (paper vs shadow)
        divergence_check = divergence <= self.MAX_DIVERGENCE_ACCEPTABLE
        results['checks']['divergence'] = {
            'pass': divergence_check,
            'requirement': f"<= {self.MAX_DIVERGENCE_ACCEPTABLE}%",
            'actual': f"{divergence:.1f}%",
            'message': 'Execution quality acceptable' if divergence_check else f'Paper-shadow gap too large ({divergence:.1f}%)'
        }
        if not divergence_check:
            all_pass = False
        
        # Check 5: Trajectory
        trajectory_check = trajectory in self.TRAJECTORY_ACCEPTABLE
        results['checks']['trajectory'] = {
            'pass': trajectory_check,
            'requirement': f"in {self.TRAJECTORY_ACCEPTABLE}",
            'actual': trajectory,
            'message': 'Performance direction acceptable' if trajectory_check else f'Degrading trajectory not promotable'
        }
        if not trajectory_check:
            all_pass = False
        
        # Check 6: Hypothesis status
        hypothesis_check = hypothesis_status not in ["weak", "broken"]
        results['checks']['hypothesis_status'] = {
            'pass': hypothesis_check,
            'requirement': 'not "weak" or "broken"',
            'actual': hypothesis_status,
            'message': 'Hypothesis viable' if hypothesis_check else f'Hypothesis marked {hypothesis_status}'
        }
        if not hypothesis_check:
            all_pass = False
        
        # Check 7: Positive expected value
        pnl_check = avg_pnl_bps > -100  # Allow slightly negative if other signals strong
        results['checks']['expected_value'] = {
            'pass': pnl_check,
            'requirement': '> -100 bps',
            'actual': f"{avg_pnl_bps:.1f} bps",
            'message': 'Positive expected value' if pnl_check else 'Consistent losses'
        }
        if not pnl_check:
            all_pass = False
        
        # Final decision
        results['promotion_allowed'] = all_pass
        results['gate_summary'] = self._summarize_gates(results['checks'])
        
        return all_pass, results
    
    def _summarize_gates(self, checks: Dict) -> str:
        """Create human-readable gate summary"""
        passed = sum(1 for c in checks.values() if c['pass'])
        total = len(checks)
        
        if passed == total:
            return f"✓ ALL GATES PASS ({passed}/{total})"
        else:
            failures = [k for k, v in checks.items() if not v['pass']]
            return f"✗ GATES FAIL: {', '.join(failures)} ({passed}/{total} pass)"
    
    def should_reduce_allocation(
        self,
        active_bot_id: str,
        current_allocation: float,
        survival_pct: float,
        max_drawdown: float,
        trajectory: str
    ) -> Tuple[bool, str, float]:
        """
        Check if active bot allocation should be reduced.
        
        Returns:
            (should_reduce, reason, new_allocation)
        """
        
        # Critical: Survival drop below 85%
        if survival_pct < 85.0:
            new_alloc = current_allocation * 0.5  # Cut by 50%
            return True, f"Survival dropped to {survival_pct:.1f}%", new_alloc
        
        # Serious: Drawdown spike
        if max_drawdown > 8.0:
            new_alloc = current_allocation * 0.7  # Cut by 30%
            return True, f"Drawdown spiked to {max_drawdown:.1f}%", new_alloc
        
        # Warning: Degrading trajectory
        if trajectory == "DEGRADING":
            new_alloc = current_allocation * 0.8  # Cut by 20%
            return True, f"Trajectory degrading", new_alloc
        
        return False, "Within acceptable bounds", current_allocation
    
    def should_kill_bot(
        self,
        active_bot_id: str,
        survival_pct: float,
        max_drawdown: float
    ) -> Tuple[bool, str]:
        """
        Check if active bot should be killed (no recovery expected).
        
        Returns:
            (should_kill, reason)
        """
        
        # Catastrophic: Survival <70%
        if survival_pct < 70.0:
            return True, f"Survival catastrophically low ({survival_pct:.1f}%)"
        
        # Catastrophic: Drawdown >12%
        if max_drawdown > 12.0:
            return True, f"Drawdown critical ({max_drawdown:.1f}%)"
        
        return False, "Bot still viable"


if __name__ == '__main__':
    gate = PromotionGate()
    
    print("\n" + "=" * 80)
    print("Promotion Gate Test")
    print("=" * 80)
    
    # Test case 1: Good bot (should pass)
    print("\n[TEST 1] Good bot (should PASS)")
    passed, results = gate.check_promotion_readiness(
        bot_id="bot-good-001",
        trade_count=50,
        survival_pct=95.0,
        max_drawdown=7.0,
        divergence=2.0,
        trajectory="IMPROVING",
        hypothesis_status="promising",
        avg_pnl_bps=25.0
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Summary: {results['gate_summary']}")
    for check, detail in results['checks'].items():
        status = "✓" if detail['pass'] else "✗"
        print(f"  {status} {check}: {detail['message']}")
    
    # Test case 2: Bad bot (should fail)
    print("\n[TEST 2] Bad bot (should FAIL)")
    passed, results = gate.check_promotion_readiness(
        bot_id="bot-bad-001",
        trade_count=15,
        survival_pct=80.0,
        max_drawdown=12.0,
        divergence=8.0,
        trajectory="DEGRADING",
        hypothesis_status="weak",
        avg_pnl_bps=-50.0
    )
    print(f"Result: {'PASS' if passed else 'FAIL'}")
    print(f"Summary: {results['gate_summary']}")
    for check, detail in results['checks'].items():
        status = "✓" if detail['pass'] else "✗"
        print(f"  {status} {check}: {detail['message']}")
    
    # Test case 3: Allocation reduction
    print("\n[TEST 3] Allocation reduction check")
    should_reduce, reason, new_alloc = gate.should_reduce_allocation(
        active_bot_id="active-001",
        current_allocation=10.0,
        survival_pct=83.0,
        max_drawdown=5.0,
        trajectory="DEGRADING"
    )
    print(f"Result: {'REDUCE' if should_reduce else 'HOLD'}")
    print(f"Reason: {reason}")
    print(f"New allocation: {new_alloc:.2f} (from 10.00)")
    
    print("\n" + "=" * 80)
