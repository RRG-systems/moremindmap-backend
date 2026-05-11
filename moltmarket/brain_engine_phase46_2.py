#!/usr/bin/env python3
"""
PHASE 4.6.2 / 4.11: BRAIN Engine Enhanced
Threshold tuning + Slow bleed detection

Fixes the critical failure mode:
System was bleeding slowly without triggering STOP.

New capabilities:
1. Tightened drawdown thresholds (early warning bands)
2. Slow bleed detection (rolling window analysis)
3. Negative drift detection
4. Recovery trend check (avoid killing recovering bots)
"""

from datetime import datetime
from typing import Dict, Optional, List, Tuple
from dataclasses import dataclass, asdict
from collections import deque


@dataclass
class BrainConfig:
    """BRAIN configuration — hard rules (PHASE 4.6.2 tuned)"""
    # Daily loss limits
    max_daily_loss_usd: float = 500.0
    
    # Drawdown thresholds (PHASE 4.6.2: TIGHTENED)
    throttle_drawdown_pct: float = 5.0   # Early warning band
    stop_drawdown_pct: float = 8.0       # Hard stop
    
    # Instability threshold
    throttle_instability_threshold: float = 25.0
    
    # Slow bleed detection (NEW)
    slow_bleed_window_size: int = 20     # Last 20 trades
    slow_bleed_avg_pnl_threshold: float = -0.5  # Avg loss per trade
    slow_bleed_recovery_window: int = 5  # Last 5 trades for recovery check
    
    # Negative drift detection (NEW)
    negative_drift_window: int = 10      # Last 10 trades
    negative_drift_threshold: float = -0.3  # Slightly negative


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
    timestamp: str = ""
    
    def to_dict(self):
        """Convert to JSON-serializable dict"""
        return asdict(self)


class BrainEnginePhase462:
    """
    BRAIN with slow bleed detection.
    
    PHASE 4.6.2 improvements:
    - Tightened drawdown thresholds
    - Slow bleed detection (rolling window)
    - Negative drift detection
    - Recovery trend check
    """
    
    def __init__(self, config: Optional[BrainConfig] = None):
        self.config = config or BrainConfig()
        
        # Trade history for slow bleed detection
        self.recent_trades = deque(maxlen=50)  # Keep last 50 trades
    
    def record_trade(self, pnl: float):
        """Record a trade for rolling window analysis"""
        self.recent_trades.append(pnl)
    
    def _calculate_avg_pnl(self, window_size: int) -> Optional[float]:
        """Calculate average P&L over rolling window"""
        if len(self.recent_trades) < window_size:
            return None
        
        recent = list(self.recent_trades)[-window_size:]
        return sum(recent) / len(recent)
    
    def _detect_recovery_trend(self, window_size: int) -> bool:
        """
        Check if recent trades show recovery/improvement.
        
        PART 3: Recovery check — avoid false positives
        """
        if len(self.recent_trades) < window_size:
            return False
        
        recent = list(self.recent_trades)[-window_size:]
        
        # Simple heuristic: if last trades are positive, bot is recovering
        positive_recent = sum(1 for p in recent if p > 0)
        recovery_threshold = window_size * 0.6  # 60% positive
        
        if positive_recent >= recovery_threshold:
            return True
        
        return False
    
    def _detect_slow_bleed(self) -> Tuple[bool, str]:
        """
        PART 2: Slow bleed detection (critical)
        
        Detects: continuous small losses over time without recovery.
        
        Returns: (is_bleeding, reason_code)
        """
        # Need enough samples
        if len(self.recent_trades) < self.config.slow_bleed_window_size:
            return False, ""
        
        # Calculate average P&L over window
        avg_pnl = self._calculate_avg_pnl(self.config.slow_bleed_window_size)
        
        if avg_pnl is None or avg_pnl >= 0:
            return False, ""
        
        # Check if losing consistently
        if avg_pnl < self.config.slow_bleed_avg_pnl_threshold:
            
            # But check for recovery trend first (PART 3)
            if self._detect_recovery_trend(self.config.slow_bleed_recovery_window):
                # Recently improving → don't trigger
                return False, ""
            
            # Consistent loss without recovery → BLEED DETECTED
            return True, "slow_bleed_detected"
        
        return False, ""
    
    def _detect_negative_drift(self) -> Tuple[bool, str]:
        """
        PART 2: Negative drift detection (intermediate warning)
        
        Detects: slightly negative P&L trend (early warning before full bleed).
        
        Returns: (has_drift, reason_code)
        """
        if len(self.recent_trades) < self.config.negative_drift_window:
            return False, ""
        
        avg_pnl = self._calculate_avg_pnl(self.config.negative_drift_window)
        
        if avg_pnl is None:
            return False, ""
        
        if avg_pnl < self.config.negative_drift_threshold and avg_pnl < 0:
            return True, "negative_drift"
        
        return False, ""
    
    def evaluate(self, 
                 active_bot_id: Optional[str],
                 bot_drawdown_pct: float = 0.0,
                 daily_loss_usd: float = 0.0,
                 sign_flip_pct: float = 0.0) -> BrainStatus:
        """
        PART 4: Evaluate BRAIN state
        
        Priority order:
        1. STOP (hard conditions)
           - daily loss
           - severe drawdown (PHASE 4.6.2: 8%)
           - slow bleed detected
        
        2. THROTTLE (warning conditions)
           - early drawdown band (PHASE 4.6.2: 5%)
           - negative drift
           - instability
        
        3. NORMAL
        
        Returns: BrainStatus with state + reason
        """
        
        # Initialize status
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
        
        # No active bot → FLAT
        if not active_bot_id:
            status.state = "FLAT"
            status.reason_code = "no_active_bot"
            status.reason_text = "No active bot — dealer mode"
            return status
        
        # ========== HARD STOP CONDITIONS ==========
        
        # Check 1: Daily loss limit (hard guard)
        if daily_loss_usd < -self.config.max_daily_loss_usd:
            status.state = "STOP"
            status.reason_code = "daily_loss_limit"
            status.reason_text = f"Daily loss (${daily_loss_usd:.2f}) exceeds limit (-${self.config.max_daily_loss_usd:.2f})"
            return status
        
        # Check 2: Severe drawdown (PHASE 4.6.2: 8%)
        if bot_drawdown_pct >= self.config.stop_drawdown_pct:
            status.state = "STOP"
            status.reason_code = "severe_drawdown"
            status.reason_text = f"Bot drawdown ({bot_drawdown_pct:.1f}%) exceeds limit ({self.config.stop_drawdown_pct:.1f}%)"
            return status
        
        # Check 3: Slow bleed detected (NEW - CRITICAL)
        bleed_detected, bleed_code = self._detect_slow_bleed()
        if bleed_detected:
            status.state = "STOP"
            status.reason_code = bleed_code
            status.reason_text = f"Slow bleed detected: consistent losses over {self.config.slow_bleed_window_size} trades"
            status.bleed_detected = True
            avg_pnl = self._calculate_avg_pnl(self.config.slow_bleed_window_size)
            if avg_pnl is not None:
                status.reason_text += f" (avg: ${avg_pnl:.2f}/trade)"
            return status
        
        # ========== WARNING CONDITIONS (THROTTLE) ==========
        
        # Check 4: Early drawdown band (PHASE 4.6.2: 5%)
        if bot_drawdown_pct >= self.config.throttle_drawdown_pct:
            status.state = "THROTTLE"
            status.reason_code = "early_drawdown_warning"
            status.reason_text = f"Early drawdown warning ({bot_drawdown_pct:.1f}%) — reducing size"
            return status
        
        # Check 5: Negative drift (NEW - INTERMEDIATE WARNING)
        drift_detected, drift_code = self._detect_negative_drift()
        if drift_detected:
            status.state = "THROTTLE"
            status.reason_code = drift_code
            status.reason_text = "Negative drift detected — reducing position size"
            avg_pnl = self._calculate_avg_pnl(self.config.negative_drift_window)
            if avg_pnl is not None:
                status.reason_text += f" (avg: ${avg_pnl:.2f}/trade)"
            return status
        
        # Check 6: Instability threshold
        if sign_flip_pct >= self.config.throttle_instability_threshold:
            status.state = "THROTTLE"
            status.reason_code = "instability_detected"
            status.reason_text = f"Sign flip rate ({sign_flip_pct:.1f}%) exceeds threshold ({self.config.throttle_instability_threshold:.1f}%)"
            return status
        
        # ========== NORMAL ==========
        
        status.state = "NORMAL"
        status.reason_code = "nominal"
        status.reason_text = "System nominal"
        avg_pnl = self._calculate_avg_pnl(self.config.negative_drift_window)
        if avg_pnl is not None:
            status.avg_pnl_recent = avg_pnl
            status.reason_text += f" (recent avg: ${avg_pnl:.2f}/trade)"
        
        return status
    
    def get_status(self) -> Dict:
        """Get current BRAIN status for API/dashboard"""
        return {
            'state': 'NORMAL',
            'reason_code': 'nominal',
            'reason_text': 'System nominal',
            'timestamp': datetime.utcnow().isoformat(),
        }


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PHASE 4.6.2 / 4.11: BRAIN Engine Enhanced — Quick Test")
    print("=" * 80)
    
    # Test 1: Slow bleed detection
    print("\nTest 1: Slow bleed detection")
    print("-" * 80)
    
    config = BrainConfig()
    brain = BrainEnginePhase462(config)
    
    # Simulate 20 trades, each losing $0.75 (below threshold of -0.5)
    # This should trigger slow bleed
    print("Recording 20 trades, each with -$0.75 P&L:")
    for i in range(20):
        brain.record_trade(-0.75)
    
    status = brain.evaluate(
        active_bot_id='test_bot',
        bot_drawdown_pct=3.0,
        daily_loss_usd=-100.0,
        sign_flip_pct=10.0
    )
    
    print(f"  State: {status.state}")
    print(f"  Reason code: {status.reason_code}")
    print(f"  Reason text: {status.reason_text}")
    print(f"  Bleed detected: {status.bleed_detected}")
    
    assert status.state == "STOP", f"Expected STOP, got {status.state}"
    assert status.reason_code == "slow_bleed_detected", f"Expected slow_bleed_detected, got {status.reason_code}"
    print("  ✅ PASS")
    
    # Test 2: Recovery check (don't kill recovering bot)
    print("\nTest 2: Recovery trend check (don't trigger on recovering bot)")
    print("-" * 80)
    
    brain2 = BrainEnginePhase462(config)
    
    # 20 trades with small losses, but last 5 are positive (recovering)
    print("Recording 20 trades: 15 losses, then 5 positive (recovering):")
    for i in range(15):
        brain2.record_trade(-0.75)
    for i in range(5):
        brain2.record_trade(+2.0)  # Strong recovery
    
    status2 = brain2.evaluate(
        active_bot_id='test_bot',
        bot_drawdown_pct=4.0,
        daily_loss_usd=-50.0,
        sign_flip_pct=10.0
    )
    
    print(f"  State: {status2.state}")
    print(f"  Reason code: {status2.reason_code}")
    print(f"  Reason text: {status2.reason_text}")
    
    assert status2.state == "NORMAL", f"Recovering bot should be NORMAL, got {status2.state}"
    print("  ✅ PASS: Recovering bot not killed")
    
    # Test 3: Early drawdown band (THROTTLE)
    print("\nTest 3: Early drawdown warning (THROTTLE)")
    print("-" * 80)
    
    brain3 = BrainEnginePhase462(config)
    
    status3 = brain3.evaluate(
        active_bot_id='test_bot',
        bot_drawdown_pct=5.5,  # Between 5% (THROTTLE) and 8% (STOP)
        daily_loss_usd=-50.0,
        sign_flip_pct=10.0
    )
    
    print(f"  Drawdown: 5.5%")
    print(f"  State: {status3.state}")
    print(f"  Reason code: {status3.reason_code}")
    
    assert status3.state == "THROTTLE", f"Expected THROTTLE at 5.5% drawdown, got {status3.state}"
    assert status3.reason_code == "early_drawdown_warning", f"Expected early_drawdown_warning, got {status3.reason_code}"
    print("  ✅ PASS: Early drawdown detected")
    
    # Test 4: Negative drift (intermediate warning)
    print("\nTest 4: Negative drift detection (THROTTLE)")
    print("-" * 80)
    
    brain4 = BrainEnginePhase462(config)
    
    # Record 10 trades, each slightly negative (avg -0.4 per trade)
    print("Recording 10 trades, each with -$0.4 P&L:")
    for i in range(10):
        brain4.record_trade(-0.4)
    
    status4 = brain4.evaluate(
        active_bot_id='test_bot',
        bot_drawdown_pct=2.0,
        daily_loss_usd=-50.0,
        sign_flip_pct=10.0
    )
    
    print(f"  State: {status4.state}")
    print(f"  Reason code: {status4.reason_code}")
    print(f"  Reason text: {status4.reason_text}")
    
    assert status4.state == "THROTTLE", f"Expected THROTTLE on negative drift, got {status4.state}"
    assert status4.reason_code == "negative_drift", f"Expected negative_drift, got {status4.reason_code}"
    print("  ✅ PASS: Negative drift detected")
    
    print("\n" + "=" * 80)
    print("✅ ALL PHASE 4.6.2 TESTS PASSED")
    print("=" * 80 + "\n")
