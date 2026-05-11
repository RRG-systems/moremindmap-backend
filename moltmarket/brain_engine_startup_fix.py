#!/usr/bin/env python3
"""
STARTUP INITIALIZATION FIX — Option A

Explicit FLAT initialization when no active bot exists.
Startup safe-state defaults to FLAT, not undefined.

Key principle: No active bot = valid FLAT state, not broken state.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class BrainConfig:
    """BRAIN configuration"""
    throttle_drawdown_pct: float = 5.0
    stop_drawdown_pct: float = 8.0
    throttle_instability_threshold: float = 25.0
    
    slow_bleed_window_size: int = 20
    slow_bleed_avg_pnl_threshold: float = -0.5
    slow_bleed_recovery_window: int = 5
    negative_drift_window: int = 10
    negative_drift_threshold: float = -0.3
    
    flat_monitor_cadence: int = 1
    restart_confidence_threshold: float = 0.25
    restart_candidate_quality_threshold: float = 0.60
    restart_probation_cycles: int = 5


@dataclass
class BrainStatus:
    """BRAIN status report"""
    state: str
    reason_code: str
    reason_text: str
    active_bot_id: Optional[str] = None
    timestamp: str = ""
    
    def to_dict(self):
        return asdict(self)


class BrainEngineStartupFix:
    """
    BRAIN with explicit startup initialization (Option A).
    
    No active bot at startup = FLAT state, not undefined.
    """
    
    def __init__(self, config: Optional[BrainConfig] = None, replacement_engine=None):
        self.config = config or BrainConfig()
        self.replacement_engine = replacement_engine
        
        # Startup state
        self.startup_initialized = False
        self.active_bot = None
        self.state = "UNKNOWN"
        self.flat_monitoring_active = False
        
    def initialize_startup(self, 
                          restored_active_bot: Optional[str] = None,
                          bot_validator_fn = None) -> BrainStatus:
        """
        PART 1 & 2: Explicit startup initialization
        
        Args:
            restored_active_bot: Bot ID from persisted state (if any)
            bot_validator_fn: Function to validate restored bot (optional)
        
        Returns:
            Initial BrainStatus
        """
        if self.startup_initialized:
            return BrainStatus(
                state=self.state,
                reason_code="already_initialized",
                reason_text="System already initialized",
                active_bot_id=self.active_bot,
                timestamp=datetime.utcnow().isoformat(),
            )
        
        # PART 2: Validate restored bot if provided
        if restored_active_bot:
            is_valid = True
            
            # If validator provided, use it
            if bot_validator_fn:
                is_valid = bot_validator_fn(restored_active_bot)
            
            if is_valid:
                # Restore bot
                self.active_bot = restored_active_bot
                self.state = "NORMAL"
                self.startup_initialized = True
                
                print(f"\n[BRAIN] STARTUP — restored active bot {restored_active_bot}")
                
                return BrainStatus(
                    state="NORMAL",
                    reason_code="startup_bot_restored",
                    reason_text=f"Restored bot: {restored_active_bot}",
                    active_bot_id=self.active_bot,
                    timestamp=datetime.utcnow().isoformat(),
                )
            else:
                # Invalid restored bot
                self.active_bot = None
                self.state = "FLAT"
                self.flat_monitoring_active = True
                self.startup_initialized = True
                
                print(f"\n[BRAIN] STARTUP FAILSAFE — invalid restored bot, entering FLAT")
                
                return BrainStatus(
                    state="FLAT",
                    reason_code="invalid_restored_bot",
                    reason_text="Restored bot failed validation, entering FLAT",
                    active_bot_id=None,
                    timestamp=datetime.utcnow().isoformat(),
                )
        
        # PART 1: No active bot → FLAT startup
        self.active_bot = None
        self.state = "FLAT"
        self.flat_monitoring_active = True
        self.startup_initialized = True
        
        print(f"\n[BRAIN] STARTUP — no valid active bot, entering FLAT")
        print(f"        FLAT monitoring starts immediately (cycle 1+)")
        
        return BrainStatus(
            state="FLAT",
            reason_code="startup_no_active_bot",
            reason_text="No valid active bot at startup, entering FLAT monitoring",
            active_bot_id=None,
            timestamp=datetime.utcnow().isoformat(),
        )
    
    def evaluate_startup_flat(self) -> Tuple[bool, Optional[Dict], str]:
        """
        PART 3: Evaluate candidate pool while in FLAT startup
        
        Returns: (should_exit_flat, best_candidate, reason)
        """
        if not self.state == "FLAT":
            return False, None, "not_in_flat"
        
        if not self.replacement_engine:
            return False, None, "no_replacement_engine"
        
        print(f"[BRAIN] FLAT MONITOR — evaluating candidates from startup state")
        
        # Get candidate pool
        candidates = self.replacement_engine.get_candidate_pool()
        if not candidates:
            return False, None, "no_candidates"
        
        # Filter qualified
        qualified = self.replacement_engine.filter_qualified_candidates(candidates)
        if not qualified:
            return False, None, "no_qualified_candidates"
        
        # Compute confidence
        confidence = self.replacement_engine.compute_candidate_diversity(qualified)
        
        if confidence < self.config.restart_confidence_threshold:
            return False, None, f"insufficient_confidence ({confidence:.3f})"
        
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
        print(f"        ✓ Candidate pool improved (confidence: {confidence:.3f}, best score: {best_score:.3f})")
        return True, best_candidate, f"startup_edge_detected"
    
    def exit_startup_flat(self, candidate: Dict) -> BrainStatus:
        """Exit FLAT after startup, select candidate"""
        self.active_bot = candidate['bot_id']
        self.state = "NORMAL"
        
        print(f"\n[BRAIN] FLAT EXIT — {candidate['bot_id']} selected after startup")
        
        return BrainStatus(
            state="NORMAL",
            reason_code="startup_flat_exit",
            reason_text=f"Selected {candidate['bot_id']} after startup FLAT",
            active_bot_id=self.active_bot,
            timestamp=datetime.utcnow().isoformat(),
        )


if __name__ == '__main__':
    print("\n" + "="*80)
    print("STARTUP INITIALIZATION FIX — Tests")
    print("="*80)
    
    # Test 1: Startup with no active bot
    print("\nTest 1: Startup with no active bot")
    print("-"*80)
    brain = BrainEngineStartupFix()
    status = brain.initialize_startup(restored_active_bot=None)
    assert status.state == "FLAT", f"Expected FLAT, got {status.state}"
    assert status.reason_code == "startup_no_active_bot"
    assert brain.flat_monitoring_active == True
    print("✅ PASS: System correctly enters FLAT on startup\n")
    
    # Test 2: Startup with valid restored bot
    print("Test 2: Startup with valid restored bot")
    print("-"*80)
    brain2 = BrainEngineStartupFix()
    status2 = brain2.initialize_startup(
        restored_active_bot="bot_123",
        bot_validator_fn=lambda x: True  # Always valid
    )
    assert status2.state == "NORMAL", f"Expected NORMAL, got {status2.state}"
    assert status2.active_bot_id == "bot_123"
    assert brain2.active_bot == "bot_123"
    print("✅ PASS: System correctly restores valid bot\n")
    
    # Test 3: Startup with invalid restored bot
    print("Test 3: Startup with invalid restored bot")
    print("-"*80)
    brain3 = BrainEngineStartupFix()
    status3 = brain3.initialize_startup(
        restored_active_bot="bot_broken",
        bot_validator_fn=lambda x: False  # Always invalid
    )
    assert status3.state == "FLAT", f"Expected FLAT, got {status3.state}"
    assert status3.reason_code == "invalid_restored_bot"
    assert brain3.active_bot is None
    print("✅ PASS: System correctly fails safe to FLAT\n")
    
    # Test 4: Startup idempotency (second init should no-op)
    print("Test 4: Startup idempotency")
    print("-"*80)
    brain4 = BrainEngineStartupFix()
    status4a = brain4.initialize_startup(restored_active_bot=None)
    status4b = brain4.initialize_startup(restored_active_bot=None)
    assert status4b.reason_code == "already_initialized"
    print("✅ PASS: Second init is no-op\n")
    
    print("="*80)
    print("✅ ALL STARTUP INITIALIZATION TESTS PASSED")
    print("="*80 + "\n")
