"""
ROCKY inside THINK — Diagnostic Engine
========================================

Rocky is the live operator intelligence embedded in the THINK panel.

His job:
1. Explain what's happening (BRAIN, Arena, Nursery, MOLT)
2. Keep Nursery stocked with the best babies
3. Build a playbook for tightening BRAIN over time

Architecture:
- RockyThinkEngine: main reasoning class
- RockyDataLayer: visibility into system state
- RockyResponse: structured response format
- PlaybookLogger: captures high-signal observations

Rocky's constraints:
- Cannot override BRAIN (BRAIN controls money)
- Cannot place trades
- Reports missing visibility honestly
- Always recommends ONE next action
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
        self.playbook_entry = None
        self.timestamp = datetime.utcnow().isoformat()
    
    def to_dict(self):
        return {
            'diagnosis': self.diagnosis,
            'evidence': self.evidence,
            'confidence': round(self.confidence, 2),
            'recommended_action': self.recommended_action,
            'missing_visibility': self.missing_visibility,
            'timestamp': self.timestamp,
            'playbook_entry': self.playbook_entry,
        }


class PlaybookLogger:
    """Captures high-signal observations for BRAIN tightening."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.playbook_file = workspace_dir / 'rocky_playbook.jsonl'
    
    def log_entry(self, entry: Dict[str, Any]):
        """Log a high-signal observation to playbook."""
        entry['timestamp'] = datetime.utcnow().isoformat()
        
        with open(self.playbook_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def get_recent_entries(self, limit: int = 20) -> List[Dict]:
        """Get recent playbook entries."""
        if not self.playbook_file.exists():
            return []
        
        entries = []
        with open(self.playbook_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        return entries[-limit:]
    
    def get_entries_by_category(self, category: str) -> List[Dict]:
        """Get entries by category (BRAIN_RULE, NURSERY_RULE, etc)."""
        if not self.playbook_file.exists():
            return []
        
        entries = []
        with open(self.playbook_file, 'r') as f:
            for line in f:
                if line.strip():
                    entry = json.loads(line)
                    if entry.get('category') == category:
                        entries.append(entry)
        
        return entries


class RockyDataLayer:
    """Visibility into system state for Rocky."""
    
    def __init__(self, dashboard_state: Dict, data_layer, simulator, nursery_bridge, evolution_engine):
        """
        Initialize Rocky's data access layer.
        
        Args:
            dashboard_state: Global dashboard state dict
            data_layer: DataLayer instance (trades, metrics)
            simulator: ExecutionSimulator instance (Arena)
            nursery_bridge: NurseryRealityBridge instance
            evolution_engine: EvolutionEngine instance
        """
        self.dashboard_state = dashboard_state
        self.data_layer = data_layer
        self.simulator = simulator
        self.nursery_bridge = nursery_bridge
        self.evolution_engine = evolution_engine
    
    def get_brain_state(self) -> Tuple[str, str, str]:
        """Get current BRAIN state."""
        state = self.dashboard_state.get('brain_state', 'UNKNOWN')
        reason_code = self.dashboard_state.get('brain_reason_code', 'unknown')
        reason_text = self.dashboard_state.get('brain_reason_text', 'not evaluated')
        return state, reason_code, reason_text
    
    def get_brain_enforcement(self) -> Dict:
        """Get BRAIN enforcement flags."""
        return self.dashboard_state.get('brain_enforcement', {})
    
    def get_arena_metrics(self) -> Dict:
        """Get current Arena metrics."""
        return self.dashboard_state.get('metrics', {})
    
    def get_arena_trades_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent Arena trades."""
        return self.data_layer.get_recent_trades(limit=limit) or []
    
    def get_nursery_candidates(self) -> List[Dict]:
        """Get active Nursery baby candidates."""
        return self.evolution_engine.babies or []
    
    def get_nursery_metrics(self) -> List[Dict]:
        """Get metrics for all active Nursery babies."""
        return self.nursery_bridge.get_all_baby_metrics()
    
    def get_molt_suggestions(self) -> List[Dict]:
        """Get recent MOLT suggestions (if available)."""
        # TODO: Wire to MOLT feed when available
        return []
    
    def get_arena_strategy(self) -> Dict:
        """Get current active Arena strategy."""
        return self.dashboard_state.get('parent_strategy', {})
    
    def get_signal_health(self) -> Dict:
        """Get signal quality metrics."""
        return self.data_layer.get_signal_health() or {}
    
    def get_execution_quality(self) -> Dict:
        """Get execution quality (slippage, fill rates)."""
        return self.data_layer.get_execution_quality() or {}
    
    def get_equity_curves(self) -> Dict:
        """Get paper/shadow/backtest equity curves."""
        return {
            'paper': self.simulator.get_paper_equity_curve() or [],
            'shadow': self.simulator.get_shadow_equity_curve() or [],
            'backtest': self.simulator.get_backtest_equity_curve() or [],
        }
    
    def check_visibility(self, key: str) -> Tuple[bool, str]:
        """
        Check if Rocky has visibility into a specific system component.
        
        Returns: (is_visible, message)
        """
        visibility_map = {
            'brain_state': bool(self.dashboard_state.get('brain_state')),
            'arena_metrics': bool(self.dashboard_state.get('metrics')),
            'arena_trades': bool(self.data_layer),
            'nursery_candidates': bool(self.evolution_engine.babies),
            'nursery_metrics': bool(self.nursery_bridge),
            'molt_suggestions': bool(self.get_molt_suggestions()),
        }
        
        is_visible = visibility_map.get(key, False)
        
        if not is_visible:
            messages = {
                'brain_state': 'I cannot see current BRAIN state',
                'arena_metrics': 'I cannot see Arena metrics',
                'arena_trades': 'I cannot see recent trades',
                'nursery_candidates': 'I cannot see Nursery candidates (no active babies)',
                'nursery_metrics': 'I cannot calculate Nursery metrics',
                'molt_suggestions': 'I cannot see MOLT suggestions (not yet integrated)',
            }
            return False, messages.get(key, f'Missing visibility: {key}')
        
        return True, f'{key} visible'


class RockyThinkEngine:
    """Main Rocky reasoning engine."""
    
    def __init__(self, workspace_dir: Path, data_layer: RockyDataLayer):
        self.workspace_dir = workspace_dir
        self.data_layer = data_layer
        self.playbook = PlaybookLogger(workspace_dir)
    
    def query(self, user_query: str) -> RockyResponse:
        """
        Process a user query and generate Rocky's response.
        
        Args:
            user_query: User's question or request
        
        Returns:
            RockyResponse with diagnosis, evidence, confidence, action
        """
        response = RockyResponse()
        
        # Normalize query
        query_lower = user_query.lower().strip()
        
        # Route to appropriate handler
        if self._is_brain_query(query_lower):
            return self._handle_brain_query(user_query)
        elif self._is_nursery_query(query_lower):
            return self._handle_nursery_query(user_query)
        elif self._is_arena_query(query_lower):
            return self._handle_arena_query(user_query)
        elif self._is_system_health_query(query_lower):
            return self._handle_system_health_query(user_query)
        else:
            return self._handle_general_query(user_query)
    
    def _is_brain_query(self, query: str) -> bool:
        """Check if query is about BRAIN."""
        keywords = ['brain', 'flat', 'throttle', 'stop', 'enforcement', 'block', 'restrict']
        return any(kw in query for kw in keywords)
    
    def _is_nursery_query(self, query: str) -> bool:
        """Check if query is about Nursery."""
        keywords = ['nursery', 'baby', 'babies', 'candidate', 'spawn', 'respawn', 'import']
        return any(kw in query for kw in keywords)
    
    def _is_arena_query(self, query: str) -> bool:
        """Check if query is about Arena."""
        keywords = ['arena', 'strategy', 'parent', 'trading', 'execution', 'trades', 'pnl']
        return any(kw in query for kw in keywords)
    
    def _is_system_health_query(self, query: str) -> bool:
        """Check if query is about overall system health."""
        keywords = ['health', 'biggest risk', 'biggest problem', 'weakness', 'issue', 'analyze']
        return any(kw in query for kw in keywords)
    
    def _handle_brain_query(self, query: str) -> RockyResponse:
        """Handle questions about BRAIN state."""
        response = RockyResponse()
        
        state, reason_code, reason_text = self.data_layer.get_brain_state()
        enforcement = self.data_layer.get_brain_enforcement()
        
        response.diagnosis = f"Current BRAIN state: {state}"
        response.evidence = [
            f"State: {state}",
            f"Reason: {reason_code}",
            f"Details: {reason_text}",
        ]
        
        if enforcement:
            if enforcement.get('allows_trade') == False:
                response.evidence.append("✓ Trading is BLOCKED")
            if enforcement.get('throttle_active'):
                response.evidence.append(f"✓ Trading THROTTLED (size factor: {enforcement.get('position_size_factor', 1.0)})")
        
        # Determine recommended action
        if state == 'STOP':
            response.recommended_action = "Investigate why STOP was triggered. Check Arena metrics for failure signals."
        elif state == 'FLAT':
            response.recommended_action = "Wait for divergence recovery or respawn Nursery from baseline to explore new direction."
        elif state == 'THROTTLE':
            response.recommended_action = "Monitor for recovery. If instability persists, consider strategy reset."
        else:
            response.recommended_action = "Continue monitoring. System is operating normally."
        
        response.confidence = 0.95  # High confidence on state reporting
        
        return response
    
    def _handle_nursery_query(self, query: str) -> RockyResponse:
        """Handle questions about Nursery governance."""
        from rocky_nursery_governance import RockyNurseryGovernance
        
        response = RockyResponse()
        governance = RockyNurseryGovernance()
        
        candidates = self.data_layer.get_nursery_candidates()
        
        if not candidates:
            response.diagnosis = "Nursery is currently empty."
            response.evidence = ["No active baby candidates"]
            response.recommended_action = "Spawn new Nursery from current Arena parent to start evolution."
            response.confidence = 1.0
            return response
        
        # Get metrics for all babies
        metrics = self.data_layer.get_nursery_metrics()
        
        if not metrics:
            response.diagnosis = "Nursery has candidates but no execution metrics yet."
            response.evidence = [f"Active babies: {len(candidates)}"]
            response.recommended_action = "Let babies run for more cycles to accumulate meaningful metrics."
            response.confidence = 0.7
            return response
        
        # Analyze Nursery health
        avg_trades = sum(m.get('trades', 0) for m in metrics) / len(metrics) if metrics else 0
        avg_pnl = sum(m.get('shadow_pnl', 0) for m in metrics) / len(metrics) if metrics else 0
        avg_flip_rate = sum(m.get('sign_flip_rate', 0) for m in metrics) / len(metrics) if metrics else 0
        
        # Find best baby
        best_baby = max(metrics, key=lambda m: m.get('shadow_pnl', 0)) if metrics else None
        
        response.diagnosis = f"Nursery has {len(candidates)} active candidates."
        response.evidence = [
            f"Avg trades per baby: {avg_trades:.1f}",
            f"Avg shadow PnL: {avg_pnl:.2f} bps",
            f"Avg sign flip rate: {avg_flip_rate:.1f}%",
        ]
        
        if best_baby:
            response.evidence.append(f"Best baby: {best_baby['variant_id']} ({best_baby['shadow_pnl']:.2f} bps)")
        
        # Evaluate Nursery health
        if avg_trades < 10:
            response.recommended_action = "Let Nursery run longer to accumulate data."
            response.confidence = 0.6
        elif avg_flip_rate > 30:
            response.recommended_action = "Nursery shows high sign flip rate. Consider respawning with tighter parameters."
            response.confidence = 0.75
        elif best_baby and best_baby['shadow_pnl'] > 50:
            response.recommended_action = f"Best baby {best_baby['variant_id']} shows edge. Consider promoting for validation."
            response.confidence = 0.8
        else:
            response.recommended_action = "Keep current Nursery running. Edge is still weak."
            response.confidence = 0.7
        
        return response
    
    def _handle_arena_query(self, query: str) -> RockyResponse:
        """Handle questions about Arena strategy."""
        response = RockyResponse()
        
        metrics = self.data_layer.get_arena_metrics()
        strategy = self.data_layer.get_arena_strategy()
        
        if not metrics:
            response.diagnosis = "Arena has no metrics yet."
            response.evidence = ["System not yet initialized"]
            response.recommended_action = "Start a new run."
            response.confidence = 1.0
            return response
        
        # Extract key metrics
        paper_return = metrics.get('paper_return_pct', 0)
        shadow_return = metrics.get('shadow_return_pct', 0)
        divergence = paper_return - shadow_return
        total_trades = metrics.get('total_trades', 0)
        win_rate = metrics.get('rolling_win_rate', 0)
        
        response.diagnosis = f"Arena strategy {strategy.get('id', 'unknown')} is executing."
        response.evidence = [
            f"Trades executed: {total_trades}",
            f"Paper return: {paper_return:.2f}%",
            f"Shadow return: {shadow_return:.2f}%",
            f"Divergence: {divergence:.2f}%",
            f"Win rate: {win_rate:.1f}%",
        ]
        
        # Determine health
        if divergence > 5.0:
            response.recommended_action = "Large paper/shadow divergence detected. Strategy may be overfitting."
            response.confidence = 0.85
        elif total_trades > 100 and win_rate > 55:
            response.recommended_action = "Strategy showing positive edge. Continue execution."
            response.confidence = 0.8
        elif total_trades < 20:
            response.recommended_action = "Let strategy run for more trades to establish edge validity."
            response.confidence = 0.6
        else:
            response.recommended_action = "Strategy is neutral. Monitor for edge development."
            response.confidence = 0.7
        
        return response
    
    def _handle_system_health_query(self, query: str) -> RockyResponse:
        """Handle system health assessment queries."""
        response = RockyResponse()
        
        # Aggregate all system data
        brain_state, _, _ = self.data_layer.get_brain_state()
        arena_metrics = self.data_layer.get_arena_metrics()
        nursery_metrics = self.data_layer.get_nursery_metrics()
        
        issues = []
        
        # Check BRAIN
        if brain_state in ['STOP', 'FLAT']:
            issues.append(f"BRAIN in {brain_state} state")
        
        # Check Arena
        if arena_metrics:
            divergence = (arena_metrics.get('paper_return_pct', 0) - 
                         arena_metrics.get('shadow_return_pct', 0))
            if divergence > 5.0:
                issues.append(f"High paper/shadow divergence ({divergence:.2f}%)")
        
        # Check Nursery
        if not self.data_layer.get_nursery_candidates():
            issues.append("Nursery is empty")
        elif nursery_metrics:
            weak_babies = [m for m in nursery_metrics 
                          if m.get('shadow_pnl', 0) < -100]
            if len(weak_babies) / len(nursery_metrics) > 0.5:
                issues.append(f"Majority of Nursery babies are weak")
        
        if not issues:
            response.diagnosis = "System is healthy."
            response.evidence = ["No major issues detected"]
            response.recommended_action = "Continue normal operation."
            response.confidence = 0.9
        else:
            response.diagnosis = f"System has {len(issues)} issue(s)."
            response.evidence = issues
            
            # Prioritize action
            if "BRAIN in STOP state" in issues:
                response.recommended_action = "Investigate STOP trigger. Review Arena strategy for failures."
            elif "empty" in response.diagnosis.lower():
                response.recommended_action = "Spawn new Nursery from current Arena parent."
            else:
                response.recommended_action = "Address top issue: " + issues[0]
            
            response.confidence = 0.8
        
        return response
    
    def _handle_general_query(self, query: str) -> RockyResponse:
        """Handle general or ambiguous queries."""
        response = RockyResponse()
        
        response.diagnosis = "I can help you with:"
        response.evidence = [
            "• System health analysis (biggest problems?)",
            "• BRAIN state (why are we FLAT/STOP/THROTTLE?)",
            "• Arena strategy evaluation (is it valid?)",
            "• Nursery governance (which babies should we keep?)",
            "• BRAIN tightening insights (how to improve over time?)",
        ]
        response.recommended_action = "Ask a specific question about BRAIN, Arena, or Nursery."
        response.confidence = 0.5
        
        return response
