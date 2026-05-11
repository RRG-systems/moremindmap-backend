#!/usr/bin/env python3
"""
Brain Data Bridge — Phase 1.5: Dashboard Integration

Extracts live metrics from dashboard_state and simulator.
Feeds them into BrainEngine for real-time evaluation.

Bridge pattern:
1. Extract metrics from dashboard/simulator
2. Calculate derived metrics (drawdown, instability, pnl)
3. Feed to BrainEngine.evaluate()
4. Store BrainStatus in memory
5. Expose via API for dashboard display + THINK consumption
"""

from datetime import datetime, date
from typing import Dict, Optional, Tuple
from brain_engine import BrainEngine, BrainConfig, BrainStatus
import json


class BrainDataBridge:
    """
    Adapter between dashboard/simulator state and BRAIN engine.
    
    Responsibilities:
    - Extract live metrics
    - Calculate derived metrics (drawdown, instability, etc.)
    - Maintain session/daily tracking
    - Feed to BRAIN for evaluation
    - Store status for consumption
    """
    
    def __init__(self, brain_config: Optional[BrainConfig] = None):
        self.brain = BrainEngine(config=brain_config or BrainConfig())
        self.current_status: Optional[BrainStatus] = None
        self.session_start_date = date.today()
        self.session_start_pnl = 0.0
        self.trading_blocked = False  # enforcement flag
        self.trading_throttled = False  # enforcement flag
        self.no_active_strategy = False  # enforcement flag
    
    def extract_live_metrics(
        self,
        dashboard_state: Dict,
        simulator: Optional[object] = None
    ) -> Dict:
        """
        Extract live metrics from dashboard state and simulator.
        
        Args:
            dashboard_state: from moltmarket_dashboard.py
            simulator: ExecutionSimulator instance
        
        Returns:
            dict with keys:
            - current_pnl_usd
            - peak_equity
            - current_equity
            - active_bot_id
            - bot_drawdown_pct
            - instability_pct (sign flip rate proxy)
            - candidate_available (stub for now)
        """
        
        metrics = dashboard_state.get('metrics', {})
        
        # PNL Tracking
        paper_value = metrics.get('paper_value', 0.0)
        shadow_value = metrics.get('shadow_value', 0.0)
        
        # Use shadow as "real" PnL (includes slippage)
        current_pnl_usd = shadow_value
        
        # Drawdown calculation
        if simulator:
            try:
                shadow_curve = getattr(simulator, 'shadow_equity', [10000.0])
                if isinstance(shadow_curve, list) and len(shadow_curve) > 0:
                    # Calculate peak-to-trough drawdown
                    peak = 10000.0
                    current_value = shadow_curve[-1] if shadow_curve else 10000.0
                    trough = current_value
                    
                    for value in shadow_curve:
                        if value > peak:
                            peak = value
                        if value < trough:
                            trough = value
                    
                    current_equity = current_value
                    peak_equity = peak
                    drawdown_pct = ((peak - current_equity) / peak * 100) if peak > 0 else 0.0
                else:
                    current_equity = 10000.0
                    peak_equity = 10000.0
                    drawdown_pct = 0.0
            except Exception as e:
                print(f"[BRAIN] Error extracting simulator equity: {e}")
                current_equity = 10000.0
                peak_equity = 10000.0
                drawdown_pct = 0.0
        else:
            current_equity = 10000.0
            peak_equity = 10000.0
            drawdown_pct = 0.0
        
        # Instability metric (sign flip rate as proxy)
        instability_pct = metrics.get('sign_flip_rate_pct', 0.0)
        
        # Active bot
        active_bot_id = dashboard_state.get('active_bot_id')
        
        # Candidate availability (stub — will be wired to nursery leaderboard)
        candidate_available = False  # TODO: wire to nursery ranking
        
        return {
            'current_pnl_usd': current_pnl_usd,
            'peak_equity': peak_equity,
            'current_equity': current_equity,
            'active_bot_id': active_bot_id,
            'bot_drawdown_pct': drawdown_pct,
            'instability_pct': instability_pct,
            'candidate_available': candidate_available,
        }
    
    def evaluate(
        self,
        dashboard_state: Dict,
        simulator: Optional[object] = None
    ) -> BrainStatus:
        """
        Main entry point: evaluate BRAIN state against current conditions.
        
        Args:
            dashboard_state: live dashboard state
            simulator: ExecutionSimulator instance
        
        Returns:
            BrainStatus with state, reason_code, metrics
        """
        
        # Extract live metrics
        live_metrics = self.extract_live_metrics(dashboard_state, simulator)
        
        # Evaluate BRAIN
        self.current_status = self.brain.evaluate(
            active_bot_id=live_metrics['active_bot_id'],
            active_bot_drawdown_pct=live_metrics['bot_drawdown_pct'],
            daily_loss_usd=live_metrics['current_pnl_usd'],
            instability_pct=live_metrics['instability_pct'],
            qualified_candidates_available=live_metrics['candidate_available']
        )
        
        # Apply enforcement flags
        self._apply_enforcement_flags()
        
        return self.current_status
    
    def _apply_enforcement_flags(self):
        """Set enforcement flags based on BRAIN state"""
        state = self.current_status.state
        
        self.trading_blocked = (state == "STOP")
        self.trading_throttled = (state == "THROTTLE")
        self.no_active_strategy = (state == "FLAT")
        
        if state == "STOP":
            print(f"[BRAIN] ⛔ STOP: {self.current_status.reason_text}")
        elif state == "THROTTLE":
            print(f"[BRAIN] ⚠️  THROTTLE: {self.current_status.reason_text}")
        elif state == "FLAT":
            print(f"[BRAIN] 🔇 FLAT: {self.current_status.reason_text}")
        else:
            print(f"[BRAIN] ✓ NORMAL")
    
    def get_status(self) -> Optional[BrainStatus]:
        """Get current BrainStatus"""
        return self.current_status
    
    def get_status_dict(self) -> Dict:
        """Get status as JSON-serializable dict"""
        if not self.current_status:
            return {
                'state': 'UNKNOWN',
                'reason_code': 'not_evaluated',
                'reason_text': 'BRAIN has not evaluated yet',
                'timestamp': datetime.utcnow().isoformat()
            }
        return self.current_status.to_dict()
    
    def get_enforcement_flags(self) -> Dict[str, bool]:
        """Get enforcement flags for dashboard"""
        return {
            'trading_blocked': self.trading_blocked,
            'trading_throttled': self.trading_throttled,
            'no_active_strategy': self.no_active_strategy,
        }
    
    def is_trading_allowed(self) -> bool:
        """Check if trading is allowed (not STOP or FLAT)"""
        if not self.current_status:
            return True  # default to allow if not evaluated
        return self.current_status.state not in ["STOP", "FLAT"]
    
    def is_throttled(self) -> bool:
        """Check if trading is throttled"""
        if not self.current_status:
            return False
        return self.current_status.state == "THROTTLE"


# =====================================================
# INTEGRATION HELPERS (for dashboard)
# =====================================================

def create_brain_data_bridge(config: Optional[BrainConfig] = None) -> BrainDataBridge:
    """Factory function to create bridge with config"""
    return BrainDataBridge(config)


# =====================================================
# SIMULATION / TEST
# =====================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("Brain Data Bridge — Integration Test")
    print("="*70)
    
    # Create bridge
    bridge = BrainDataBridge()
    
    # Simulate dashboard state (normal conditions)
    print("\n[TEST 1] Normal conditions")
    dashboard_state = {
        'metrics': {
            'paper_value': 50.0,
            'shadow_value': 40.0,
            'sign_flip_rate_pct': 10.0,
        },
        'active_bot_id': 'bot_001',
    }
    
    status = bridge.evaluate(dashboard_state, simulator=None)
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    print(f"  PnL: ${status.daily_loss_usd:.2f}")
    print(f"  Enforcement flags: {bridge.get_enforcement_flags()}")
    assert status.state == "NORMAL", "Expected NORMAL"
    print("  ✓ PASS")
    
    # Simulate big loss
    print("\n[TEST 2] Big loss → STOP")
    dashboard_state['metrics']['shadow_value'] = -600.0
    status = bridge.evaluate(dashboard_state, simulator=None)
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    print(f"  Enforcement flags: {bridge.get_enforcement_flags()}")
    assert status.state == "STOP", "Expected STOP"
    assert bridge.trading_blocked == True, "Expected trading_blocked=True"
    print("  ✓ PASS")
    
    # Simulate instability
    print("\n[TEST 3] Instability → THROTTLE")
    dashboard_state['metrics']['shadow_value'] = 50.0
    dashboard_state['metrics']['sign_flip_rate_pct'] = 35.0
    status = bridge.evaluate(dashboard_state, simulator=None)
    print(f"  State: {status.state}")
    print(f"  Reason: {status.reason_code}")
    print(f"  Enforcement flags: {bridge.get_enforcement_flags()}")
    assert status.state == "THROTTLE", "Expected THROTTLE"
    assert bridge.trading_throttled == True, "Expected trading_throttled=True"
    print("  ✓ PASS")
    
    # Get status for THINK consumption
    print("\n[TEST 4] Status for THINK")
    status_dict = bridge.get_status_dict()
    print(f"  State: {status_dict['state']}")
    print(f"  Reason Code: {status_dict['reason_code']}")
    print(f"  Reason Text: {status_dict['reason_text']}")
    print(f"  JSON serializable: {json.dumps(status_dict, default=str)}")
    print("  ✓ PASS")
    
    print("\n" + "="*70)
    print("✓ All integration tests passed")
    print("="*70 + "\n")
