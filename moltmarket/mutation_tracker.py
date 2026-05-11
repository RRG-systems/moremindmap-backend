#!/usr/bin/env python3
"""
Mutation Tracker — Phase 6
Track and compare control vs mutated baby performance.
"""

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, List, Optional, Tuple


class MutationTracker:
    """Track mutation results and compare control vs mutated performance."""
    
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.results_log = self.workspace / 'mutation_results.jsonl'
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create results log if it doesn't exist."""
        if not self.results_log.exists():
            self.results_log.touch()
    
    def collect_baby_metrics(self, baby_id: str, arena_metrics: Dict) -> Dict:
        """
        Collect current metrics for a baby.
        
        Args:
            baby_id: Baby identifier
            arena_metrics: Current arena metrics for this baby
        
        Returns:
            Standardized metrics dict
        """
        return {
            'baby_id': baby_id,
            'total_trades': arena_metrics.get('total_trades', 0),
            'flip_rate': arena_metrics.get('sign_flip_rate_pct', 0),
            'avg_pnl_per_trade': arena_metrics.get('avg_pnl_per_trade', 0),
            'paper_vs_shadow_delta': arena_metrics.get('paper_vs_shadow_delta', 0),
            'max_drawdown': arena_metrics.get('max_drawdown', 0),
            'survival_pass': arena_metrics.get('survival_pass', False),
            'timestamp': datetime.utcnow().isoformat(),
        }
    
    def group_babies(self, babies: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Group babies into CONTROL and MUTATED.
        
        Args:
            babies: List of baby dicts with is_control and mutation_applied flags
        
        Returns:
            (control_babies, mutated_babies)
        """
        control = [b for b in babies if b.get('is_control', False)]
        mutated = [b for b in babies if b.get('mutation_applied', False)]
        
        print(f"[TRACKER] Grouped {len(control)} control + {len(mutated)} mutated babies")
        
        return control, mutated
    
    def compute_group_metrics(self, babies: List[Dict], group_name: str) -> Dict:
        """
        Compute average metrics for a group of babies.
        
        Args:
            babies: List of baby dicts with metrics
            group_name: "control" or "mutated"
        
        Returns:
            Group-level metrics
        """
        if not babies:
            return {
                'group': group_name,
                'count': 0,
                'avg_pnl': 0,
                'avg_flip_rate': 0,
                'avg_drawdown': 0,
                'survival_rate': 0,
            }
        
        # Extract metrics
        pnls = []
        flip_rates = []
        drawdowns = []
        survives = []
        
        for baby in babies:
            if 'arena_metrics' in baby:
                m = baby['arena_metrics']
                pnls.append(m.get('avg_pnl_per_trade', 0))
                flip_rates.append(m.get('flip_rate', 0))
                drawdowns.append(m.get('max_drawdown', 0))
                survives.append(1 if m.get('survival_pass', False) else 0)
        
        # Compute averages
        avg_pnl = mean(pnls) if pnls else 0
        avg_flip = mean(flip_rates) if flip_rates else 0
        avg_dd = mean(drawdowns) if drawdowns else 0
        survival_rate = (mean(survives) * 100) if survives else 0
        
        result = {
            'group': group_name,
            'count': len(babies),
            'avg_pnl': round(avg_pnl, 6),
            'avg_flip_rate': round(avg_flip, 2),
            'avg_drawdown': round(avg_dd, 2),
            'survival_rate': round(survival_rate, 1),
        }
        
        print(f"[TRACKER] {group_name.upper()}: {len(babies)} babies, avg_pnl={avg_pnl:.6f}, survival={survival_rate:.1f}%")
        
        return result
    
    def classify_result(self, control_metrics: Dict, mutated_metrics: Dict) -> str:
        """
        Classify mutation outcome.
        
        Args:
            control_metrics: Control group metrics
            mutated_metrics: Mutated group metrics
        
        Returns:
            "HELPED", "HURT", or "INCONCLUSIVE"
        """
        control_pnl = control_metrics.get('avg_pnl', 0)
        mutated_pnl = mutated_metrics.get('avg_pnl', 0)
        
        control_survival = control_metrics.get('survival_rate', 0)
        mutated_survival = mutated_metrics.get('survival_rate', 0)
        
        # HELPED: Better PnL AND survival maintained or improved
        if mutated_pnl > control_pnl and mutated_survival >= control_survival:
            result = "HELPED"
        # HURT: Worse PnL
        elif mutated_pnl < control_pnl:
            result = "HURT"
        # INCONCLUSIVE: Trade-off or no clear winner
        else:
            result = "INCONCLUSIVE"
        
        print(f"[TRACKER] Result: {result}")
        print(f"          (Control: {control_pnl:.6f} PnL, {control_survival:.1f}% survival)")
        print(f"          (Mutated: {mutated_pnl:.6f} PnL, {mutated_survival:.1f}% survival)")
        
        return result
    
    def compute_mutation_results(
        self,
        babies: List[Dict],
        mutation_type: str,
        generation: int
    ) -> Dict:
        """
        Compute and classify mutation results.
        
        Args:
            babies: List of baby dicts with is_control, mutation_applied, arena_metrics
            mutation_type: The mutation type applied (EXIT, SELECTIVITY, SIZE, NONE)
            generation: Generation number
        
        Returns:
            Result dict ready for logging/display
        """
        # Group babies
        control_babies, mutated_babies = self.group_babies(babies)
        
        # Compute group metrics
        control_metrics = self.compute_group_metrics(control_babies, "control")
        mutated_metrics = self.compute_group_metrics(mutated_babies, "mutated")
        
        # Classify outcome
        result = self.classify_result(control_metrics, mutated_metrics)
        
        # Build result dict
        result_dict = {
            'timestamp': datetime.utcnow().isoformat(),
            'mutation_type': mutation_type,
            'generation': generation,
            'result': result,
            'control': control_metrics,
            'mutated': mutated_metrics,
        }
        
        return result_dict
    
    def log_result(self, result_dict: Dict) -> bool:
        """
        Log mutation result to file.
        
        Args:
            result_dict: Result dict from compute_mutation_results()
        
        Returns:
            True if successful
        """
        try:
            with open(self.results_log, 'a') as f:
                f.write(json.dumps(result_dict) + '\n')
            print(f"[TRACKER] Result logged: {result_dict['result']}")
            return True
        except Exception as e:
            print(f"[TRACKER] ERROR logging result: {e}")
            return False
    
    def get_latest_result(self) -> Optional[Dict]:
        """Get most recent mutation result."""
        try:
            if not self.results_log.exists():
                return None
            
            with open(self.results_log, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                return None
            
            # Parse last line
            latest = json.loads(lines[-1])
            return latest
        except Exception as e:
            print(f"[TRACKER] ERROR retrieving latest result: {e}")
            return None
