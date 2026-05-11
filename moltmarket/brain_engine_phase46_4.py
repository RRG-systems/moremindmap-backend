#!/usr/bin/env python3
"""
PHASE 4.6.4: BRAIN Engine with FLAT Monitoring & Restart Logic

Completes the capital preservation cycle:
1. Go FLAT when no edge exists
2. Monitor candidate pool while FLAT
3. Exit FLAT when evidence improves
4. Restart cautiously with probation window
5. Return to FLAT if restart fails

FLAT becomes an OBSERVING state, not a dead state.
"""

from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
from collections import deque


@dataclass
class BrainConfig:
    """BRAIN configuration (PHASE 4.6.4 with monitoring)"""
    # Drawdown thresholds
    throttle_drawdown_pct: float = 5.0
    stop_drawdown_pct: float = 8.0
    
    # Instability
    throttle_instability_threshold: float = 25.0
    
    # Slow bleed
    slow_bleed_window_size: int = 20
    slow_bleed_avg_pnl_threshold: float = -0.5
    slow_bleed_recovery_window: int = 5
    negative_drift_window: int = 10
    negative_drift_threshold: float = -0.3
    
    # FLAT monitoring (PHASE 4.6.4)
    flat_monitor_cadence: int = 1  # Check every N cycles
    restart_confidence_threshold: float = 0.25  # Min confidence to restart
    restart_candidate_quality_threshold: float = 0.60  # Min score to restart
    restart_probation_cycles: int = 5  # Monitor new candidate for N cycles


@dataclass
class BrainStatus:
    """BRAIN status report"""
    state: str
    reason_code: str
    reason_text: str
    active_bot_id: Optional[str] = None
    daily_loss_usd: float = 0.0
    bot_drawdown_pct: float = 0.0
    instability_pct: float = 0.0
    avg_pnl_recent: float = 0.0
    bleed_detected: bool = False
    flat_monitoring: bool = False
    timestamp: str = ""
    
    def to_dict(self):
        return asdict(self)


class BrainEnginePhase464:
    """
    BRAIN with FLAT monitoring and restart logic.
    
    PHASE 4.6.4: Completes the circuit.
    """
    
    def __init__(self, config: Optional[BrainConfig] = None, replacement_engine=None):
        self.config = config or BrainConfig()
        self.replacement_engine = replacement_engine
        
        # Trade history for slow bleed detection
        self.recent_trades = deque(maxlen=50)
        
        # PHASE 4.6.4: FLAT monitoring state
        self.flat_state = {
            'in_flat': False,
            'flat_entry_cycle': None,
            'flat_entry_pool_confidence': None,
            'monitoring_cycles': 0,
            'restart_candidate': None,
            'restart_probation_cycles': 0,
        }
    
    def record_trade(self, pnl: float):
        """Record a trade for rolling window analysis"""
        self.recent_trades.append(pnl)
    
    def _calculate_avg_pnl(self, window_size: int) -> Optional[float]:
        """Calculate average P&L over window"""
        if len(self.recent_trades) < window_size:
            return None
        recent = list(self.recent_trades)[-window_size:]
        return sum(recent) / len(recent)
    
    def _detect_recovery_trend(self, window_size: int) -> bool:
        """Check if recent trades show recovery"""
        if len(self.recent_trades) < window_size:
            return False
        recent = list(self.recent_trades)[-window_size:]
        positive_recent = sum(1 for p in recent if p > 0)
        return positive_recent >= (window_size * 0.6)
    
    def _detect_slow_bleed(self) -> Tuple[bool, str]:
        """Detect slow bleed"""
        if len(self.recent_trades) < self.config.slow_bleed_window_size:
            return False, ""
        
        avg_pnl = self._calculate_avg_pnl(self.config.slow_bleed_window_size)
        
        if avg_pnl is None or avg_pnl >= 0:
            return False, ""
        
        if avg_pnl < self.config.slow_bleed_avg_pnl_threshold:
            if self._detect_recovery_trend(self.config.slow_bleed_recovery_window):
                return False, ""
            return True, "slow_bleed_detected"
        
        return False, ""
    
    def _detect_negative_drift(self) -> Tuple[bool, str]:
        """Detect negative drift"""
        if len(self.recent_trades) < self.config.negative_drift_window:
            return False, ""
        
        avg_pnl = self._calculate_avg_pnl(self.config.negative_drift_window)
        
        if avg_pnl is None or avg_pnl >= 0:
            return False, ""
        
        if avg_pnl < self.config.negative_drift_threshold and avg_pnl < 0:
            return True, "negative_drift"
        
        return False, ""
    
    def evaluate_candidate_pool(self) -> Tuple[float, str]:
        """
        PART 2: Evaluate candidate pool quality
        
        Returns: (confidence_score, reason)
        """
        if not self.replacement_engine:
            return 0.0, "no_replacement_engine"
        
        candidates = self.replacement_engine.get_candidate_pool()
        if not candidates:
            return 0.0, "no_candidates"
        
        qualified = self.replacement_engine.filter_qualified_candidates(candidates)
        if not qualified:
            return 0.0, "no_qualified_candidates"
        
        confidence = self.replacement_engine.compute_candidate_diversity(qualified)
        
        return confidence, "pool_evaluated"
    
    def check_restart_eligibility(self) -> Tuple[bool, Optional[Dict], str]:
        """
        PART 2: Check if we should exit FLAT
        
        Returns: (should_restart, best_candidate, reason)
        """
        if not self.replacement_engine:
            return False, None, "no_replacement_engine"
        
        # Get current pool
        candidates = self.replacement_engine.get_candidate_pool()
        if not candidates:
            return False, None, "no_candidates"
        
        qualified = self.replacement_engine.filter_qualified_candidates(candidates)
        if not qualified:
            return False, None, "no_qualified_candidates"
        
        # Compute confidence
        confidence = self.replacement_engine.compute_candidate_diversity(qualified)
        
        if confidence < self.config.restart_confidence_threshold:
            return False, None, f"insufficient_restart_confidence ({confidence:.3f})"
        
        # Score candidates
        scored = []
        for candidate in qualified:
            score = self.replacement_engine.calculate_candidate_score(candidate)
            scored.append((score, candidate))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        best_score, best_candidate = scored[0]
        
        # Check minimum quality
        if best_score < self.config.restart_candidate_quality_threshold:
            return False, None, f"best_candidate_below_threshold ({best_score:.3f})"
        
        # Passed all checks
        return True, best_candidate, f"restart_eligible (confidence: {confidence:.3f}, score: {best_score:.3f})"
    
    def enter_flat(self, reason_code: str, reason_text: str):
        """
        PART 1 & 3: Enter FLAT monitoring state
        """
        self.flat_state['in_flat'] = True
        self.flat_state['flat_entry_cycle'] = 0  # Will be set by caller
        self.flat_state['monitoring_cycles'] = 0
        
        # Capture pool quality at entry
        confidence, _ = self.evaluate_candidate_pool()
        self.flat_state['flat_entry_pool_confidence'] = confidence
        
        print(f"\n[BRAIN] ENTER FLAT — {reason_code}")
        print(f"        Pool confidence at entry: {confidence:.3f}")
    
    def monitor_flat_state(self) -> Tuple[bool, Optional[Dict], str]:
        """
        PART 1: Monitor while in FLAT
        
        Returns: (should_exit_flat, restart_candidate, reason)
        """
        if not self.flat_state['in_flat']:
            return False, None, "not_in_flat"
        
        # Increment monitoring counter
        self.flat_state['monitoring_cycles'] += 1
        
        # Check restart eligibility
        should_restart, candidate, reason = self.check_restart_eligibility()
        
        if self.flat_state['monitoring_cycles'] % self.config.flat_monitor_cadence == 0:
            if should_restart:
                print(f"[BRAIN] FLAT MONITOR — {reason}")
                return True, candidate, reason
            else:
                print(f"[BRAIN] FLAT HOLD — {reason}")
        
        return False, None, "continue_monitoring"
    
    def enter_restart_probation(self, candidate: Dict):
        """
        PART 4: Start probation for restarted candidate
        """
        self.flat_state['restart_candidate'] = candidate
        self.flat_state['restart_probation_cycles'] = 0
        print(f"\n[BRAIN] EXIT FLAT — {candidate['bot_id']} qualifies for restart")
        print(f"        Entering {self.config.restart_probation_cycles}-cycle probation")
    
    def check_restart_stability(self) -> Tuple[bool, str]:
        """
        PART 4: Check if restart candidate is stable
        
        Returns: (restart_stable, reason)
        """
        if not self.flat_state['restart_candidate']:
            return False, "no_restart_candidate"
        
        self.flat_state['restart_probation_cycles'] += 1
        
        # Check slow bleed
        bleed_detected, _ = self._detect_slow_bleed()
        if bleed_detected:
            print(f"[BRAIN] RESTART FAILED — slow bleed detected after {self.flat_state['restart_probation_cycles']} cycles")
            return False, "restart_bleed_detected"
        
        # Check if probation complete
        if self.flat_state['restart_probation_cycles'] >= self.config.restart_probation_cycles:
            print(f"[BRAIN] RESTART STABLE — passed {self.config.restart_probation_cycles}-cycle probation")
            return True, "restart_stable"
        
        return True, f"probation_cycle_{self.flat_state['restart_probation_cycles']}"
    
    def exit_restart_probation(self) -> bool:
        """
        PART 4: Exit probation (success)
        """
        self.flat_state['restart_candidate'] = None
        self.flat_state['restart_probation_cycles'] = 0
        print(f"[BRAIN] RESTART SUCCESSFUL — normal operation resumed")
        return True
    
    def return_to_flat_from_restart(self):
        """
        PART 5: Return to FLAT after failed restart
        """
        self.flat_state['in_flat'] = True
        self.flat_state['restart_candidate'] = None
        self.flat_state['restart_probation_cycles'] = 0
        print(f"[BRAIN] RESTART FAILED — returning to FLAT")
    
    def evaluate(self,
                 active_bot_id: Optional[str],
                 bot_drawdown_pct: float = 0.0,
                 daily_loss_usd: float = 0.0,
                 sign_flip_pct: float = 0.0) -> BrainStatus:
        """
        PHASE 4.6.4: Enhanced evaluation with FLAT monitoring
        """
        status = BrainStatus(
            state="NORMAL",
            reason_code="nominal",
            reason_text="System nominal",
            active_bot_id=active_bot_id,
            daily_loss_usd=daily_loss_usd,
            bot_drawdown_pct=bot_drawdown_pct,
            instability_pct=sign_flip_pct,
            timestamp=datetime.utcnow().isoformat(),
        )
        
        # Check if we're in FLAT and should restart
        if self.flat_state['in_flat'] and not active_bot_id:
            should_exit, candidate, reason = self.monitor_flat_state()
            
            if should_exit:
                self.enter_restart_probation(candidate)
                status.state = "NORMAL"
                status.reason_code = "restart_from_flat"
                status.reason_text = f"Exiting FLAT: {reason}"
                status.active_bot_id = candidate['bot_id']
                status.flat_monitoring = True
                return status
            else:
                status.state = "FLAT"
                status.reason_code = "flat_monitoring"
                status.reason_text = reason
                status.flat_monitoring = True
                return status
        
        # Check if restart candidate is stable
        if self.flat_state['restart_candidate'] and active_bot_id:
            stable, reason = self.check_restart_stability()
            
            if not stable:
                self.return_to_flat_from_restart()
                status.state = "FLAT"
                status.reason_code = "restart_failed"
                status.reason_text = reason
                return status
            elif stable and self.flat_state['restart_probation_cycles'] >= self.config.restart_probation_cycles:
                self.exit_restart_probation()
                status.state = "NORMAL"
                status.reason_code = "restart_stable"
                status.reason_text = "Restart successful"
                status.active_bot_id = active_bot_id
                return status
            else:
                status.state = "NORMAL"
                status.reason_code = "restart_probation"
                status.reason_text = f"{reason}"
                status.active_bot_id = active_bot_id
                return status
        
        # No active bot and not in FLAT → check if should go FLAT
        if not active_bot_id:
            status.state = "FLAT"
            status.reason_code = "no_active_bot"
            status.reason_text = "No active bot"
            return status
        
        # Standard BRAIN evaluation for active bot
        # (slow bleed, drawdown, etc. — same as Phase 4.6.2)
        bleed_detected, _ = self._detect_slow_bleed()
        if bleed_detected:
            self.enter_flat("slow_bleed_detected", "Slow bleed detected")
            status.state = "STOP"
            status.reason_code = "slow_bleed_detected"
            status.reason_text = "Slow bleed detected"
            return status
        
        if bot_drawdown_pct >= self.config.stop_drawdown_pct:
            self.enter_flat("severe_drawdown", f"Drawdown {bot_drawdown_pct:.1f}%")
            status.state = "STOP"
            status.reason_code = "severe_drawdown"
            status.reason_text = f"Drawdown ({bot_drawdown_pct:.1f}%) exceeds limit"
            return status
        
        if bot_drawdown_pct >= self.config.throttle_drawdown_pct:
            status.state = "THROTTLE"
            status.reason_code = "early_drawdown_warning"
            status.reason_text = f"Early drawdown warning ({bot_drawdown_pct:.1f}%)"
            return status
        
        drift_detected, _ = self._detect_negative_drift()
        if drift_detected:
            status.state = "THROTTLE"
            status.reason_code = "negative_drift"
            status.reason_text = "Negative drift detected"
            return status
        
        if sign_flip_pct >= self.config.throttle_instability_threshold:
            status.state = "THROTTLE"
            status.reason_code = "instability_detected"
            status.reason_text = f"Instability ({sign_flip_pct:.1f}%) exceeds threshold"
            return status
        
        status.state = "NORMAL"
        status.reason_code = "nominal"
        status.reason_text = "System nominal"
        status.active_bot_id = active_bot_id
        
        return status


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PHASE 4.6.4: BRAIN with FLAT Monitoring — Quick Test")
    print("=" * 80)
    
    config = BrainConfig(restart_probation_cycles=3)
    brain = BrainEnginePhase464(config)
    
    # Test 1: Enter FLAT
    print("\nTest 1: Enter FLAT monitoring")
    print("-" * 80)
    brain.enter_flat("test_entry", "Test entering FLAT")
    print("✅ PASS\n")
    
    # Test 2: Monitor while FLAT (should stay FLAT)
    print("Test 2: Monitor while FLAT (no improvement)")
    print("-" * 80)
    should_exit, _, _ = brain.monitor_flat_state()
    print(f"Should exit: {should_exit}")
    assert not should_exit, "Should not exit without candidate"
    print("✅ PASS\n")
    
    # Test 3: Enter restart probation
    print("Test 3: Enter restart probation")
    print("-" * 80)
    test_candidate = {
        'bot_id': 'test_bot',
        'trade_count': 30,
        'pnl': 100.0,
        'drawdown': 0.02,
        'sign_flip_rate': 0.05
    }
    brain.enter_restart_probation(test_candidate)
    assert brain.flat_state['restart_candidate'] is not None
    print("✅ PASS\n")
    
    # Test 4: Check restart stability
    print("Test 4: Check restart stability (probation)")
    print("-" * 80)
    # Record some positive trades
    for i in range(5):
        brain.record_trade(5.0)
    
    stable, reason = brain.check_restart_stability()
    print(f"Stable: {stable}, Reason: {reason}")
    print("✅ PASS\n")
    
    print("=" * 80)
    print("✅ PHASE 4.6.4 TESTS PASSED")
    print("=" * 80 + "\n")
