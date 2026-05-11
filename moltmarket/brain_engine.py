#!/usr/bin/env python3
"""
BRAIN Engine — Phase 1: State Machine + Hard Guards

Capital preservation autopilot.
No overrides. No negotiation.
Every action has a reason code.

States:
- NORMAL: trading allowed, normal allocation
- THROTTLE: reduced size, instability warning
- STOP: no new trades, bot unsafe
- FLAT: no qualified candidate, observe only

Hard Guards:
- max_daily_loss_usd: stop trading if breached
- max_bot_drawdown_pct: stop if active bot drawdown exceeds
- throttle_instability_threshold: throttle on variance spike
- no_qualified_candidate: go FLAT if no backup available
"""

from datetime import datetime, date
from typing import Dict, Optional, List
from enum import Enum
from dataclasses import dataclass, asdict
import json


class BrainState(Enum):
    """Valid BRAIN states"""
    NORMAL = "NORMAL"
    THROTTLE = "THROTTLE"
    STOP = "STOP"
    FLAT = "FLAT"


@dataclass
class BrainConfig:
    """BRAIN configuration — hard rules"""
    max_daily_loss_usd: float = 500.0  # stop if daily PnL < -$500
    max_bot_drawdown_pct: float = 5.0  # stop if bot drawdown > 5%
    throttle_instability_threshold: float = 25.0  # throttle if sign flips > 25%
    session_day_definition: str = "calendar"  # "calendar" or "session" (NYT session boundary)


@dataclass
class BrainStatus:
    """BRAIN status report — every action has reason"""
    state: str  # NORMAL | THROTTLE | STOP | FLAT
    reason_code: str  # machine-readable reason
    reason_text: str  # human-readable explanation
    active_bot_id: Optional[str] = None
    daily_loss_usd: float = 0.0
    bot_drawdown_pct: float = 0.0
    instability_pct: float = 0.0
    timestamp: str = ""
    
    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return asdict(self)


class BrainEngine:
    """
    BRAIN: Deterministic capital preservation engine
    
    Evaluates:
    - Daily loss limits
    - Per-bot drawdown limits
    - Instability warnings
    - Candidate availability
    
    Outputs:
    - State transitions (deterministic)
    - Reason codes (for THINK integration)
    - Status reports (for dashboard)
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        self.state = BrainState.NORMAL
        self.active_bot_id: Optional[str] = None
        self.daily_loss_usd: float = 0.0
        self.last_reason_code: str = "initialized"
        self.last_reason_text: str = "BRAIN engine initialized"
        self.session_start_time = datetime.utcnow()
        self.session_start_date = date.today()
    
    def evaluate(
        self,
        active_bot_id: Optional[str] = None,
        active_bot_drawdown_pct: float = 0.0,
        daily_loss_usd: float = 0.0,
        instability_pct: float = 0.0,
        qualified_candidates_available: bool = False
    ) -> BrainStatus:
        """
        Evaluate BRAIN state based on current metrics.
        
        Args:
            active_bot_id: current active bot (None if flat)
            active_bot_drawdown_pct: current drawdown %
            daily_loss_usd: cumulative daily loss (negative = loss)
            instability_pct: sign flip rate %
            qualified_candidates_available: is there a replacement ready?
        
        Returns:
            BrainStatus with state, reason_code, reason_text
        """
        
        # GUARD 1: Max daily loss exceeded
        if daily_loss_usd < -self.config.max_daily_loss_usd:
            self.state = BrainState.STOP
            self.last_reason_code = "daily_loss_limit"
            self.last_reason_text = (
                f"Daily loss limit breached: ${daily_loss_usd:.2f} < -${self.config.max_daily_loss_usd}"
            )
            self.daily_loss_usd = daily_loss_usd
            self.active_bot_id = active_bot_id
            return self._build_status(
                state=BrainState.STOP,
                reason_code="daily_loss_limit",
                reason_text=self.last_reason_text,
                active_bot_id=active_bot_id,
                daily_loss_usd=daily_loss_usd,
                bot_drawdown_pct=active_bot_drawdown_pct,
                instability_pct=instability_pct
            )
        
        # GUARD 2: Bot drawdown exceeded
        if active_bot_id and active_bot_drawdown_pct > self.config.max_bot_drawdown_pct:
            self.state = BrainState.STOP
            self.last_reason_code = "bot_drawdown_limit"
            self.last_reason_text = (
                f"Bot drawdown limit breached: {active_bot_drawdown_pct:.1f}% > {self.config.max_bot_drawdown_pct}%"
            )
            self.daily_loss_usd = daily_loss_usd
            self.active_bot_id = active_bot_id
            return self._build_status(
                state=BrainState.STOP,
                reason_code="bot_drawdown_limit",
                reason_text=self.last_reason_text,
                active_bot_id=active_bot_id,
                daily_loss_usd=daily_loss_usd,
                bot_drawdown_pct=active_bot_drawdown_pct,
                instability_pct=instability_pct
            )
        
        # GUARD 3: Instability spike → THROTTLE
        if instability_pct > self.config.throttle_instability_threshold:
            self.state = BrainState.THROTTLE
            self.last_reason_code = "instability_warning"
            self.last_reason_text = (
                f"Instability spike detected: {instability_pct:.1f}% > {self.config.throttle_instability_threshold}% threshold"
            )
            self.daily_loss_usd = daily_loss_usd
            self.active_bot_id = active_bot_id
            return self._build_status(
                state=BrainState.THROTTLE,
                reason_code="instability_warning",
                reason_text=self.last_reason_text,
                active_bot_id=active_bot_id,
                daily_loss_usd=daily_loss_usd,
                bot_drawdown_pct=active_bot_drawdown_pct,
                instability_pct=instability_pct
            )
        
        # GUARD 4: If currently STOP, check for qualified replacement
        if self.state == BrainState.STOP:
            if qualified_candidates_available:
                # Candidate available — stay in STOP, ready for transition
                self.last_reason_code = "stop_awaiting_replacement"
                self.last_reason_text = "STOP active; qualified replacement candidate available"
                return self._build_status(
                    state=BrainState.STOP,
                    reason_code="stop_awaiting_replacement",
                    reason_text=self.last_reason_text,
                    active_bot_id=active_bot_id,
                    daily_loss_usd=daily_loss_usd,
                    bot_drawdown_pct=active_bot_drawdown_pct,
                    instability_pct=instability_pct
                )
            else:
                # No replacement available → go FLAT
                self.state = BrainState.FLAT
                self.last_reason_code = "no_qualified_candidate"
                self.last_reason_text = "STOP active; no qualified replacement candidate available → FLAT"
                self.active_bot_id = None
                return self._build_status(
                    state=BrainState.FLAT,
                    reason_code="no_qualified_candidate",
                    reason_text=self.last_reason_text,
                    active_bot_id=None,
                    daily_loss_usd=daily_loss_usd,
                    bot_drawdown_pct=active_bot_drawdown_pct,
                    instability_pct=instability_pct
                )
        
        # GUARD 5: If currently FLAT, check if replacement available
        if self.state == BrainState.FLAT:
            if not qualified_candidates_available:
                # Still flat
                self.last_reason_code = "no_qualified_candidate"
                self.last_reason_text = "FLAT: no qualified candidate available"
                return self._build_status(
                    state=BrainState.FLAT,
                    reason_code="no_qualified_candidate",
                    reason_text=self.last_reason_text,
                    active_bot_id=None,
                    daily_loss_usd=daily_loss_usd,
                    bot_drawdown_pct=active_bot_drawdown_pct,
                    instability_pct=instability_pct
                )
            # If candidate available, stay FLAT but signal readiness (don't auto-promote yet)
        
        # DEFAULT: Within all constraints → NORMAL
        if self.state != BrainState.THROTTLE:
            self.state = BrainState.NORMAL
            self.last_reason_code = "within_constraints"
            self.last_reason_text = "All constraints met. Normal trading allowed."
            self.daily_loss_usd = daily_loss_usd
            self.active_bot_id = active_bot_id
            return self._build_status(
                state=BrainState.NORMAL,
                reason_code="within_constraints",
                reason_text=self.last_reason_text,
                active_bot_id=active_bot_id,
                daily_loss_usd=daily_loss_usd,
                bot_drawdown_pct=active_bot_drawdown_pct,
                instability_pct=instability_pct
            )
        
        # If THROTTLE, stay THROTTLE
        self.daily_loss_usd = daily_loss_usd
        self.active_bot_id = active_bot_id
        return self._build_status(
            state=BrainState.THROTTLE,
            reason_code="instability_warning",
            reason_text=self.last_reason_text,
            active_bot_id=active_bot_id,
            daily_loss_usd=daily_loss_usd,
            bot_drawdown_pct=active_bot_drawdown_pct,
            instability_pct=instability_pct
        )
    
    def _build_status(
        self,
        state: BrainState,
        reason_code: str,
        reason_text: str,
        active_bot_id: Optional[str] = None,
        daily_loss_usd: float = 0.0,
        bot_drawdown_pct: float = 0.0,
        instability_pct: float = 0.0
    ) -> BrainStatus:
        """Build a BrainStatus response"""
        return BrainStatus(
            state=state.value,
            reason_code=reason_code,
            reason_text=reason_text,
            active_bot_id=active_bot_id,
            daily_loss_usd=daily_loss_usd,
            bot_drawdown_pct=bot_drawdown_pct,
            instability_pct=instability_pct,
            timestamp=datetime.utcnow().isoformat()
        )
    
    def set_daily_loss(self, loss_usd: float):
        """Update daily loss tracking"""
        self.daily_loss_usd = loss_usd
    
    def set_active_bot(self, bot_id: Optional[str]):
        """Update active bot ID"""
        self.active_bot_id = bot_id
    
    def get_current_state(self) -> str:
        """Get current state as string"""
        return self.state.value
    
    def get_current_reason(self) -> Dict:
        """Get current reason code and text"""
        return {
            'code': self.last_reason_code,
            'text': self.last_reason_text
        }


# =====================================================
# VALIDATION TEST CASES (Run this to verify Phase 1)
# =====================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("BRAIN Engine — Phase 1 Validation Tests")
    print("="*70)
    
    config = BrainConfig(
        max_daily_loss_usd=500.0,
        max_bot_drawdown_pct=5.0,
        throttle_instability_threshold=25.0
    )
    
    brain = BrainEngine(config)
    
    # TEST 1: Normal trading
    print("\n[TEST 1] Normal trading → NORMAL")
    status = brain.evaluate(
        active_bot_id="bot_001",
        active_bot_drawdown_pct=2.0,
        daily_loss_usd=-100.0,
        instability_pct=10.0,
        qualified_candidates_available=False
    )
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    assert status.state == "NORMAL", "Expected NORMAL"
    print("  ✓ PASS")
    
    # TEST 2: Instability spike → THROTTLE
    print("\n[TEST 2] Instability spike → THROTTLE")
    status = brain.evaluate(
        active_bot_id="bot_001",
        active_bot_drawdown_pct=2.0,
        daily_loss_usd=-100.0,
        instability_pct=30.0,
        qualified_candidates_available=False
    )
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    assert status.state == "THROTTLE", "Expected THROTTLE"
    print("  ✓ PASS")
    
    # TEST 3: Bot drawdown breach → STOP
    print("\n[TEST 3] Bot drawdown breach → STOP")
    status = brain.evaluate(
        active_bot_id="bot_001",
        active_bot_drawdown_pct=7.0,
        daily_loss_usd=-100.0,
        instability_pct=10.0,
        qualified_candidates_available=True
    )
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    assert status.state == "STOP", "Expected STOP"
    print("  ✓ PASS")
    
    # TEST 4: Daily loss breach → STOP
    print("\n[TEST 4] Daily loss breach → STOP")
    status = brain.evaluate(
        active_bot_id="bot_001",
        active_bot_drawdown_pct=2.0,
        daily_loss_usd=-600.0,
        instability_pct=10.0,
        qualified_candidates_available=True
    )
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    assert status.state == "STOP", "Expected STOP"
    print("  ✓ PASS")
    
    # TEST 5: STOP with no candidate → FLAT
    print("\n[TEST 5] STOP with no candidate → FLAT")
    brain.state = BrainState.STOP
    status = brain.evaluate(
        active_bot_id="bot_001",
        active_bot_drawdown_pct=2.0,
        daily_loss_usd=-100.0,
        instability_pct=10.0,
        qualified_candidates_available=False
    )
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    assert status.state == "FLAT", "Expected FLAT"
    print("  ✓ PASS")
    
    print("\n" + "="*70)
    print("✓ All Phase 1 tests passed")
    print("="*70 + "\n")
