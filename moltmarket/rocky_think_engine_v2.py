"""
ROCKY inside THINK — Complete Diagnostic Engine v2

Full reasoning for: BRAIN, Arena, Nursery, MOLT governance, BRAIN tightening.
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


class RockyResponse:
    """Structured response from Rocky."""
    
    def __init__(self):
        self.diagnosis = ""
        self.evidence = []
        self.confidence = 0.0
        self.recommended_action = ""
        self.missing_visibility = []
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            'diagnosis': self.diagnosis,
            'evidence': self.evidence,
            'confidence': round(self.confidence, 2),
            'recommended_action': self.recommended_action,
            'missing_visibility': self.missing_visibility,
            'timestamp': self.timestamp,
        }


class RockyDataLayer:
    """Visibility into system state."""
    
    def __init__(self, dashboard_state, data_layer, simulator, nursery_bridge, evolution_engine):
        self.dashboard_state = dashboard_state
        self.data_layer = data_layer
        self.simulator = simulator
        self.nursery_bridge = nursery_bridge
        self.evolution_engine = evolution_engine
    
    def get_brain_state(self):
        state = self.dashboard_state.get('brain_state', 'UNKNOWN')
        reason = self.dashboard_state.get('brain_reason_code', 'unknown')
        text = self.dashboard_state.get('brain_reason_text', '')
        return state, reason, text
    
    def get_brain_enforcement(self):
        return self.dashboard_state.get('brain_enforcement', {})
    
    def get_arena_metrics(self):
        return self.dashboard_state.get('metrics', {})
    
    def get_nursery_candidates(self):
        return self.evolution_engine.babies or []
    
    def get_nursery_metrics(self):
        return self.nursery_bridge.get_all_baby_metrics()
    
    def get_molt_suggestions(self):
        return []  # Not yet integrated


class RockyThinkEngine:
    """Main reasoning engine."""
    
    def __init__(self, workspace_dir, data_layer):
        self.workspace_dir = workspace_dir
        self.data_layer = data_layer
    
    def query(self, user_query):
        """Process query and return Rocky's response."""
        query_lower = user_query.lower().strip()
        
        # Route based on query type
        if any(kw in query_lower for kw in ['brain', 'flat', 'stop', 'throttle', 'enforce']):
            return self._brain_query(user_query)
        elif any(kw in query_lower for kw in ['nursery', 'baby', 'candidate', 'spawn']):
            return self._nursery_query(user_query)
        elif any(kw in query_lower for kw in ['arena', 'strategy', 'parent', 'trading']):
            return self._arena_query(user_query)
        elif any(kw in query_lower for kw in ['health', 'risk', 'problem', 'biggest', 'analyze']):
            return self._system_health_query(user_query)
        else:
            return self._help_query(user_query)
    
    def _brain_query(self, query):
        """BRAIN state and enforcement."""
        response = RockyResponse()
        
        state, reason, text = self.data_layer.get_brain_state()
        enforcement = self.data_layer.get_brain_enforcement()
        
        response.diagnosis = f"BRAIN state: {state}"
        response.evidence = [
            f"State: {state}",
            f"Reason: {reason}",
            f"Details: {text}",
        ]
        
        if enforcement.get('allows_trade') == False:
            response.evidence.append("Trading blocked")
        if enforcement.get('throttle_active'):
            response.evidence.append(f"Trading throttled (size: {enforcement.get('position_size_factor', 1.0)})")
        
        if state == 'STOP':
            response.recommended_action = "Check Arena for failures. May need strategy reset."
            response.confidence = 0.95
        elif state == 'FLAT':
            response.recommended_action = "Wait for recovery or respawn Nursery from baseline."
            response.confidence = 0.9
        elif state == 'THROTTLE':
            response.recommended_action = "Monitor instability. Reset if it persists."
            response.confidence = 0.85
        else:
            response.recommended_action = "System operating normally. Continue."
            response.confidence = 0.95
        
        return response
    
    def _nursery_query(self, query):
        """Nursery governance and baby eval."""
        response = RockyResponse()
        
        candidates = self.data_layer.get_nursery_candidates()
        
        if not candidates:
            response.diagnosis = "Nursery empty."
            response.evidence = ["No active babies"]
            response.recommended_action = "Spawn new Nursery from Arena parent."
            response.confidence = 1.0
            return response
        
        metrics = self.data_layer.get_nursery_metrics()
        
        if not metrics:
            response.diagnosis = f"Nursery spawned: {len(candidates)} babies, no metrics yet."
            response.evidence = ["Babies accumulating trades"]
            response.recommended_action = "Let them run, check back soon."
            response.confidence = 0.6
            return response
        
        # Evaluate nursery
        best = max(metrics, key=lambda m: m.get('shadow_pnl', 0))
        avg_pnl = sum(m.get('shadow_pnl', 0) for m in metrics) / len(metrics)
        arena_shadow = self.data_layer.get_arena_metrics().get('shadow_return_pct', 0) * 100
        
        response.diagnosis = f"Nursery: {len(candidates)} babies. Best: {best['variant_id']} ({best['shadow_pnl']:.0f}bps)"
        response.evidence = [
            f"Avg shadow PnL: {avg_pnl:.0f}bps",
            f"vs Arena: {arena_shadow:.0f}bps",
            f"Trades: {sum(m.get('trades', 0) for m in metrics)}/{len(metrics)*20}",
        ]
        
        if best['shadow_pnl'] > arena_shadow + 100:
            response.recommended_action = f"Nursery winning. Promote {best['variant_id']}."
            response.confidence = 0.85
        elif avg_pnl > 50:
            response.recommended_action = "Nursery healthy. Keep running."
            response.confidence = 0.75
        elif avg_pnl < -50:
            response.recommended_action = "Nursery weak. Respawn from Arena."
            response.confidence = 0.8
        else:
            response.recommended_action = "Nursery neutral. Let it develop."
            response.confidence = 0.65
        
        return response
    
    def _arena_query(self, query):
        """Arena strategy health."""
        response = RockyResponse()
        
        metrics = self.data_layer.get_arena_metrics()
        
        if not metrics:
            response.diagnosis = "Arena: no data yet."
            response.evidence = ["System not initialized"]
            response.recommended_action = "Start a new run."
            response.confidence = 1.0
            return response
        
        paper_ret = metrics.get('paper_return_pct', 0)
        shadow_ret = metrics.get('shadow_return_pct', 0)
        div = paper_ret - shadow_ret
        trades = metrics.get('total_trades', 0)
        win_rate = metrics.get('rolling_win_rate', 0)
        
        response.diagnosis = f"Arena: {trades} trades, {win_rate:.0f}% win rate"
        response.evidence = [
            f"Paper: {paper_ret:.2f}% | Shadow: {shadow_ret:.2f}%",
            f"Divergence: {div:.2f}%",
            f"Edge: {shadow_ret/max(trades,1)*100:.0f}bps" if trades > 0 else "No trades yet",
        ]
        
        if div > 5.0:
            response.recommended_action = "High divergence. Strategy may be overfitting."
            response.confidence = 0.85
        elif trades > 100 and win_rate > 55:
            response.recommended_action = "Strong edge. Continue."
            response.confidence = 0.85
        elif trades < 20:
            response.recommended_action = "Need more trades. Let strategy run."
            response.confidence = 0.7
        elif shadow_ret < -2.0:
            response.recommended_action = "Strategy losing. Consider reset."
            response.confidence = 0.8
        else:
            response.recommended_action = "Strategy neutral. Monitor development."
            response.confidence = 0.7
        
        return response
    
    def _system_health_query(self, query):
        """Overall system health."""
        response = RockyResponse()
        
        brain_state, _, _ = self.data_layer.get_brain_state()
        arena_metrics = self.data_layer.get_arena_metrics()
        nursery_cands = self.data_layer.get_nursery_candidates()
        
        issues = []
        
        if brain_state in ['STOP', 'FLAT']:
            issues.append(f"BRAIN {brain_state}")
        
        if arena_metrics and (arena_metrics.get('paper_return_pct', 0) - arena_metrics.get('shadow_return_pct', 0)) > 5.0:
            issues.append("High paper/shadow divergence")
        
        if not nursery_cands:
            issues.append("Nursery empty")
        
        if not issues:
            response.diagnosis = "System healthy."
            response.evidence = ["No major issues"]
            response.recommended_action = "Continue normal operation."
            response.confidence = 0.9
        else:
            response.diagnosis = f"Issues detected: {', '.join(issues)}"
            response.evidence = issues
            
            if "STOP" in issues:
                response.recommended_action = "Investigate STOP trigger. May need reset."
            elif "empty" in issues:
                response.recommended_action = "Spawn Nursery from Arena parent."
            else:
                response.recommended_action = f"Address: {issues[0]}"
            
            response.confidence = 0.8
        
        return response
    
    def _help_query(self, query):
        """Help/general query."""
        response = RockyResponse()
        
        response.diagnosis = "I help with:"
        response.evidence = [
            "• BRAIN state & enforcement",
            "• Nursery health & baby ranking",
            "• Arena strategy evaluation",
            "• System risk analysis",
        ]
        response.recommended_action = "Ask about BRAIN, Nursery, Arena, or system health."
        response.confidence = 0.5
        
        return response
