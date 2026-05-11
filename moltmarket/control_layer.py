#!/usr/bin/env python3
"""
Control Layer — Phase 8
Detect when to stop, throttle, switch, or continue.
Capital protection via simple, hard rules.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class ControlLayer:
    """Capital protection layer with simple decision rules."""
    
    # Hard thresholds
    MAX_DRAWDOWN_THRESHOLD = 8.0  # %
    CATASTROPHIC_DRAWDOWN = 10.0  # % (allows early STOP)
    MIN_PNL_THRESHOLD = -5.0      # bps
    TRADE_COUNT_THRESHOLD = 30
    TRADE_COUNT_SWITCH = 40
    MIN_SAMPLE_GATE = 20  # No control action before this many trades
    
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.control_log = self.workspace / 'control_logs.jsonl'
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create control log if it doesn't exist."""
        if not self.control_log.exists():
            self.control_log.touch()
    
    def evaluate_stop_condition(
        self,
        survival_pass: bool,
        max_drawdown: float,
        avg_pnl_bps: float,
        total_trades: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check STOP conditions (highest priority).
        
        Args:
            survival_pass: Survival gate result
            max_drawdown: Maximum drawdown %
            avg_pnl_bps: Average PnL in basis points
            total_trades: Total trades executed
        
        Returns:
            (should_stop, reason)
        """
        # PHASE 9.1: Minimum sample gate
        if total_trades < self.MIN_SAMPLE_GATE:
            # Exception: allow early STOP only for catastrophic drawdown
            if max_drawdown > self.CATASTROPHIC_DRAWDOWN:
                return True, f"CATASTROPHIC drawdown {max_drawdown:.1f}% (early stop only)"
            # Otherwise, no action
            return False, None
        
        # Condition 1: Survival check
        if not survival_pass:
            return True, "Survival gate failed — unacceptable loss profile"
        
        # Condition 2: Drawdown exceeds maximum
        if max_drawdown > self.MAX_DRAWDOWN_THRESHOLD:
            return True, f"Drawdown {max_drawdown:.1f}% exceeds {self.MAX_DRAWDOWN_THRESHOLD}% threshold"
        
        # Condition 3: Significant losses with enough sample
        if avg_pnl_bps < self.MIN_PNL_THRESHOLD and total_trades > self.TRADE_COUNT_THRESHOLD:
            return True, f"Negative PnL {avg_pnl_bps:.1f} bps with {total_trades} trades"
        
        return False, None
    
    def evaluate_throttle_condition(
        self,
        trajectory: str,
        avg_pnl_bps: float
    ) -> tuple[bool, Optional[str]]:
        """
        Check THROTTLE conditions.
        
        Args:
            trajectory: IMPROVING / DEGRADING / STABLE
            avg_pnl_bps: Average PnL in basis points
        
        Returns:
            (should_throttle, reason)
        """
        # Degrading + negative PnL = reduce exposure
        if trajectory == "DEGRADING" and avg_pnl_bps < 0:
            return True, f"Degrading trajectory with negative PnL ({avg_pnl_bps:.1f} bps)"
        
        return False, None
    
    def evaluate_switch_condition(
        self,
        trajectory: str,
        last_mutation_result: str,
        total_trades: int
    ) -> tuple[bool, Optional[str]]:
        """
        Check SWITCH conditions.
        
        Args:
            trajectory: IMPROVING / DEGRADING / STABLE
            last_mutation_result: HELPED / HURT / INCONCLUSIVE
            total_trades: Total trades executed
        
        Returns:
            (should_switch, reason)
        """
        # Degrading + failed mutation + enough data
        if (trajectory == "DEGRADING" and 
            last_mutation_result == "HURT" and 
            total_trades > self.TRADE_COUNT_SWITCH):
            return True, f"Mutation failed + degrading trajectory after {total_trades} trades"
        
        return False, None
    
    def classify_control_action(
        self,
        survival_pass: bool,
        max_drawdown: float,
        avg_pnl_bps: float,
        total_trades: int,
        trajectory: str,
        last_mutation_result: str
    ) -> tuple[str, str]:
        """
        Classify control action using priority rules.
        
        Args:
            survival_pass: Survival gate result
            max_drawdown: Maximum drawdown %
            avg_pnl_bps: Average PnL in basis points
            total_trades: Total trades executed
            trajectory: IMPROVING / DEGRADING / STABLE
            last_mutation_result: HELPED / HURT / INCONCLUSIVE
        
        Returns:
            (action, reason)
        """
        # Priority 1: STOP
        should_stop, reason = self.evaluate_stop_condition(
            survival_pass, max_drawdown, avg_pnl_bps, total_trades
        )
        if should_stop:
            print(f"[CONTROL] STOP: {reason}")
            return "STOP", reason
        
        # Priority 2: THROTTLE
        should_throttle, reason = self.evaluate_throttle_condition(trajectory, avg_pnl_bps)
        if should_throttle:
            print(f"[CONTROL] THROTTLE: {reason}")
            return "THROTTLE", reason
        
        # Priority 3: SWITCH
        should_switch, reason = self.evaluate_switch_condition(
            trajectory, last_mutation_result, total_trades
        )
        if should_switch:
            print(f"[CONTROL] SWITCH: {reason}")
            return "SWITCH", reason
        
        # Default: NORMAL
        print(f"[CONTROL] NORMAL: Within acceptable bounds")
        return "NORMAL", "Within acceptable bounds"
    
    def evaluate_control(
        self,
        arena_metrics: Dict,
        trajectory_data: Dict,
        mutation_result: Dict
    ) -> Dict:
        """
        Evaluate control action based on current state.
        
        Args:
            arena_metrics: Current arena metrics snapshot
            trajectory_data: Latest trajectory analysis (or None)
            mutation_result: Latest mutation result (or None)
        
        Returns:
            Control decision dict
        """
        # Extract metrics
        survival_pass = arena_metrics.get('survival_pass', False)
        max_drawdown = arena_metrics.get('max_drawdown', 0)
        avg_pnl = arena_metrics.get('avg_pnl_per_trade', 0)
        total_trades = arena_metrics.get('total_trades', 0)
        
        # PHASE 9.1 FIX: avg_pnl is already in correct units from dashboard
        # No conversion needed (dashboard_state already has it normalized)
        avg_pnl_bps = avg_pnl
        
        # Extract trajectory
        trajectory = "STABLE"
        if trajectory_data:
            # Could be control or mutated; we care about mutated trajectory
            if trajectory_data.get('mutated'):
                trajectory = trajectory_data['mutated'].get('trajectory', 'STABLE')
        
        # Extract mutation result
        last_mutation_result = "INCONCLUSIVE"
        if mutation_result:
            last_mutation_result = mutation_result.get('result', 'INCONCLUSIVE')
        
        # Classify action
        action, reason = self.classify_control_action(
            survival_pass, max_drawdown, avg_pnl_bps, total_trades,
            trajectory, last_mutation_result
        )
        
        # PHASE 9.1: Map action to display
        display_action = action
        if action == "WARMUP":
            display_action = "WARMUP"
        
        # Build result
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'action': display_action,
            'reason': reason,
            'metrics_snapshot': {
                'pnl_bps': round(avg_pnl_bps, 1),
                'drawdown_pct': round(max_drawdown, 1),
                'flip_rate': arena_metrics.get('sign_flip_rate_pct', 0),
                'total_trades': total_trades,
                'survival_pass': survival_pass,
                'trajectory': trajectory,
                'mutation_result': last_mutation_result,
            },
        }
        
        return result
    
    def log_control_decision(self, decision: Dict) -> bool:
        """
        Log control decision to file.
        
        Args:
            decision: Control decision dict
        
        Returns:
            True if successful
        """
        try:
            with open(self.control_log, 'a') as f:
                f.write(json.dumps(decision) + '\n')
            print(f"[CONTROL] Logged: {decision['action']}")
            return True
        except Exception as e:
            print(f"[CONTROL] ERROR logging: {e}")
            return False
    
    def get_latest_control_decision(self) -> Optional[Dict]:
        """Get most recent control decision."""
        try:
            if not self.control_log.exists():
                return None
            
            with open(self.control_log, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            latest = json.loads(lines[-1])
            return latest
        except Exception as e:
            print(f"[CONTROL] ERROR retrieving latest: {e}")
            return None
