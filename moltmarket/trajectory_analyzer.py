#!/usr/bin/env python3
"""
Trajectory Analyzer — Phase 7
Detect direction of change: improving, degrading, or stable.
"""

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Tuple


class TrajectoryAnalyzer:
    """Analyze bot trajectory based on recent vs full-run metrics."""
    
    RECENT_WINDOW_SIZE = 10  # Last N trades for recent metrics
    
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.trajectory_log = self.workspace / 'trajectory_logs.jsonl'
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create trajectory log if it doesn't exist."""
        if not self.trajectory_log.exists():
            self.trajectory_log.touch()
    
    def compute_trajectory_signals(
        self,
        full_run_metrics: Dict,
        recent_window_metrics: Dict
    ) -> Dict[str, bool]:
        """
        Compute directional signals for each metric.
        
        Args:
            full_run_metrics: Full-run aggregated metrics
            recent_window_metrics: Last N trades metrics
        
        Returns:
            Dict of signals: {'pnl': True/False, 'flip': True/False, ...}
            True = improving, False = degrading
        """
        signals = {}
        
        # PnL: higher is better
        full_pnl = full_run_metrics.get('avg_pnl', 0)
        recent_pnl = recent_window_metrics.get('avg_pnl', 0)
        signals['pnl'] = recent_pnl > full_pnl
        print(f"[TRAJECTORY] PnL: {recent_pnl:.6f} vs {full_pnl:.6f} → {'improving' if signals['pnl'] else 'degrading'}")
        
        # Flip rate: lower is better
        full_flip = full_run_metrics.get('flip_rate', 0)
        recent_flip = recent_window_metrics.get('flip_rate', 0)
        signals['flip_rate'] = recent_flip < full_flip
        print(f"[TRAJECTORY] Flip: {recent_flip:.1f}% vs {full_flip:.1f}% → {'improving' if signals['flip_rate'] else 'degrading'}")
        
        # Drawdown: lower is better
        full_dd = full_run_metrics.get('drawdown', 0)
        recent_dd = recent_window_metrics.get('drawdown', 0)
        signals['drawdown'] = recent_dd < full_dd
        print(f"[TRAJECTORY] Drawdown: {recent_dd:.1f}% vs {full_dd:.1f}% → {'improving' if signals['drawdown'] else 'degrading'}")
        
        # Divergence: lower is better
        full_div = full_run_metrics.get('divergence', 0)
        recent_div = recent_window_metrics.get('divergence', 0)
        signals['divergence'] = recent_div < full_div
        print(f"[TRAJECTORY] Divergence: {recent_div:.1f}% vs {full_div:.1f}% → {'improving' if signals['divergence'] else 'degrading'}")
        
        return signals
    
    def classify_trajectory(self, signals: Dict[str, bool]) -> str:
        """
        Classify overall trajectory from signals.
        
        Args:
            signals: Dict of improving/degrading signals
        
        Returns:
            "IMPROVING", "DEGRADING", or "STABLE"
        """
        if not signals:
            return "STABLE"
        
        improving_count = sum(1 for v in signals.values() if v)
        total_count = len(signals)
        
        improving_pct = (improving_count / total_count) * 100
        
        if improving_pct > 60:
            result = "IMPROVING"
        elif improving_pct < 40:
            result = "DEGRADING"
        else:
            result = "STABLE"
        
        print(f"[TRAJECTORY] Overall: {improving_pct:.0f}% improving → {result}")
        return result
    
    def analyze_baby_trajectory(
        self,
        baby_id: str,
        full_run_metrics: Dict,
        recent_window_metrics: Dict
    ) -> Dict:
        """
        Analyze trajectory for a single baby.
        
        Args:
            baby_id: Baby identifier
            full_run_metrics: Full-run metrics
            recent_window_metrics: Recent window metrics
        
        Returns:
            Trajectory dict
        """
        signals = self.compute_trajectory_signals(full_run_metrics, recent_window_metrics)
        trajectory = self.classify_trajectory(signals)
        
        return {
            'bot_id': baby_id,
            'trajectory': trajectory,
            'signals': signals,
            'recent_window_size': self.RECENT_WINDOW_SIZE,
        }
    
    def analyze_group_trajectory(
        self,
        babies: List[Dict],
        group_name: str
    ) -> Dict:
        """
        Analyze trajectory for a group of babies.
        
        Args:
            babies: List of baby dicts with trajectory info
            group_name: "control" or "mutated"
        
        Returns:
            Group-level trajectory
        """
        if not babies:
            return {
                'group': group_name,
                'count': 0,
                'improving_pct': 0,
                'degrading_pct': 0,
                'stable_pct': 0,
                'trajectory': 'STABLE',
            }
        
        trajectories = [b.get('trajectory', 'STABLE') for b in babies]
        
        improving = trajectories.count('IMPROVING')
        degrading = trajectories.count('DEGRADING')
        stable = trajectories.count('STABLE')
        
        total = len(babies)
        improving_pct = (improving / total) * 100
        degrading_pct = (degrading / total) * 100
        stable_pct = (stable / total) * 100
        
        # Classify group
        if improving_pct > 60:
            group_trajectory = 'IMPROVING'
        elif degrading_pct > 60:
            group_trajectory = 'DEGRADING'
        else:
            group_trajectory = 'MIXED'
        
        result = {
            'group': group_name,
            'count': total,
            'improving_pct': round(improving_pct, 1),
            'degrading_pct': round(degrading_pct, 1),
            'stable_pct': round(stable_pct, 1),
            'trajectory': group_trajectory,
        }
        
        print(f"[TRAJECTORY] {group_name.upper()}: {improving}↑ {degrading}↓ {stable}→ = {group_trajectory}")
        
        return result
    
    def analyze_full_trajectory(
        self,
        control_babies: List[Dict],
        mutated_babies: List[Dict],
        generation: int
    ) -> Dict:
        """
        Analyze full trajectory for control vs mutated.
        
        Args:
            control_babies: Control group babies with trajectory info
            mutated_babies: Mutated group babies with trajectory info
            generation: Generation number
        
        Returns:
            Full trajectory result
        """
        control_traj = self.analyze_group_trajectory(control_babies, "control")
        mutated_traj = self.analyze_group_trajectory(mutated_babies, "mutated")
        
        result = {
            'timestamp': datetime.utcnow().isoformat(),
            'generation': generation,
            'control': control_traj,
            'mutated': mutated_traj,
        }
        
        return result
    
    def log_trajectory(self, trajectory_dict: Dict) -> bool:
        """
        Log trajectory analysis to file.
        
        Args:
            trajectory_dict: Result from analyze_full_trajectory()
        
        Returns:
            True if successful
        """
        try:
            with open(self.trajectory_log, 'a') as f:
                f.write(json.dumps(trajectory_dict) + '\n')
            print(f"[TRAJECTORY] Logged: {trajectory_dict['control']['trajectory']} vs {trajectory_dict['mutated']['trajectory']}")
            return True
        except Exception as e:
            print(f"[TRAJECTORY] ERROR logging: {e}")
            return False
    
    def get_latest_trajectory(self) -> Optional[Dict]:
        """Get most recent trajectory analysis."""
        try:
            if not self.trajectory_log.exists():
                return None
            
            with open(self.trajectory_log, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            latest = json.loads(lines[-1])
            return latest
        except Exception as e:
            print(f"[TRAJECTORY] ERROR retrieving latest: {e}")
            return None
