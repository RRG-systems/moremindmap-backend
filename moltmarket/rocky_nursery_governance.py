"""
ROCKY — Nursery Governance Logic

Evaluate Nursery babies against Arena parent.
Decision: promote best baby, respawn, import MOLT, or keep current.

Primary metric: Shadow PnL (realistic, friction included)
"""

from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class BabyFitness:
    """Baby's fitness score and evaluation."""
    variant_id: str
    trades: int
    shadow_pnl: float
    paper_pnl: float
    sign_flip_rate: float
    degradation: float
    is_promotable: bool
    recommendation: str


@dataclass
class NurseryHealth:
    """Overall Nursery health assessment."""
    total_babies: int
    avg_shadow_pnl: float
    best_baby: BabyFitness
    worst_baby: BabyFitness
    clone_diversity: float  # 0-1, how diverse are the mutations?
    vs_arena: str  # "WINNING", "LOSING", "NEUTRAL"
    health_status: str  # "STRONG", "WEAK", "EMPTY"


class RockyNurseryGovernance:
    """Make promotion/respawn/import decisions for Nursery."""
    
    def __init__(self):
        pass
    
    def evaluate_baby(self, baby_metrics: Dict) -> BabyFitness:
        """
        Evaluate single baby's fitness.
        
        Args:
            baby_metrics: dict with variant_id, trades, shadow_pnl, paper_pnl, sign_flip_rate, degradation
        
        Returns:
            BabyFitness with recommendation
        """
        variant_id = baby_metrics['variant_id']
        trades = baby_metrics.get('trades', 0)
        shadow_pnl = baby_metrics.get('shadow_pnl', 0)
        paper_pnl = baby_metrics.get('paper_pnl', 0)
        sign_flip_rate = baby_metrics.get('sign_flip_rate', 0)
        degradation = baby_metrics.get('degradation', 0)
        
        # Promotability criteria
        is_promotable = (
            trades >= 30 and  # Enough data
            shadow_pnl > 50 and  # Positive edge
            sign_flip_rate < 15  # Not overfitting
        )
        
        # Recommendation
        if is_promotable and shadow_pnl > 100:
            recommendation = "PROMOTE — Strong edge, low overfitting"
        elif is_promotable and shadow_pnl > 50:
            recommendation = "CONSIDER — Positive but modest edge"
        elif trades < 20:
            recommendation = "WAIT — Need more data"
        elif sign_flip_rate > 25:
            recommendation = "RETIRE — Overfitting detected"
        elif shadow_pnl < -100:
            recommendation = "RETIRE — Negative edge"
        else:
            recommendation = "MONITOR — Neutral, keep running"
        
        return BabyFitness(
            variant_id=variant_id,
            trades=trades,
            shadow_pnl=shadow_pnl,
            paper_pnl=paper_pnl,
            sign_flip_rate=sign_flip_rate,
            degradation=degradation,
            is_promotable=is_promotable,
            recommendation=recommendation,
        )
    
    def evaluate_nursery(
        self, 
        nursery_metrics: List[Dict], 
        arena_metrics: Dict
    ) -> NurseryHealth:
        """
        Evaluate entire Nursery against Arena parent.
        
        Args:
            nursery_metrics: List of baby metrics dicts
            arena_metrics: Arena's current metrics (paper_return_pct, shadow_return_pct, total_trades)
        
        Returns:
            NurseryHealth assessment
        """
        if not nursery_metrics:
            return NurseryHealth(
                total_babies=0,
                avg_shadow_pnl=0,
                best_baby=None,
                worst_baby=None,
                clone_diversity=0,
                vs_arena="UNKNOWN",
                health_status="EMPTY",
            )
        
        # Evaluate each baby
        babies = [self.evaluate_baby(m) for m in nursery_metrics]
        
        # Calculate Nursery stats
        total_babies = len(babies)
        avg_shadow_pnl = sum(b.shadow_pnl for b in babies) / len(babies) if babies else 0
        best_baby = max(babies, key=lambda b: b.shadow_pnl)
        worst_baby = min(babies, key=lambda b: b.shadow_pnl)
        
        # Compare vs Arena
        arena_shadow_return = arena_metrics.get('shadow_return_pct', 0)
        arena_trades = arena_metrics.get('total_trades', 0)
        
        # Convert Arena return % to bps for comparison
        arena_shadow_bps = arena_shadow_return * 100
        
        if best_baby.shadow_pnl > arena_shadow_bps + 50:
            vs_arena = "WINNING"
        elif best_baby.shadow_pnl < arena_shadow_bps - 50:
            vs_arena = "LOSING"
        else:
            vs_arena = "NEUTRAL"
        
        # Clone diversity (simplified: look at mutation types)
        # TODO: when evolution_engine exposes mutation types
        clone_diversity = self._estimate_diversity(babies)
        
        # Health status
        if total_babies == 0:
            health_status = "EMPTY"
        elif avg_shadow_pnl < -50 and total_babies > 5:
            health_status = "WEAK"
        elif best_baby.shadow_pnl > 100 or vs_arena == "WINNING":
            health_status = "STRONG"
        else:
            health_status = "NEUTRAL"
        
        return NurseryHealth(
            total_babies=total_babies,
            avg_shadow_pnl=avg_shadow_pnl,
            best_baby=best_baby,
            worst_baby=worst_baby,
            clone_diversity=clone_diversity,
            vs_arena=vs_arena,
            health_status=health_status,
        )
    
    def _estimate_diversity(self, babies: List[BabyFitness]) -> float:
        """
        Estimate clone diversity (0-1).
        
        For now: rough estimate based on spread of shadow_pnl.
        When evolution_engine exposes mutations, use mutation distance.
        """
        if len(babies) < 2:
            return 0.0
        
        shadow_pnls = [b.shadow_pnl for b in babies]
        min_pnl = min(shadow_pnls)
        max_pnl = max(shadow_pnls)
        
        spread = (max_pnl - min_pnl) / max(abs(min_pnl), abs(max_pnl), 1.0)
        return min(spread, 1.0)
    
    def recommend_nursery_action(
        self,
        nursery_health: NurseryHealth,
        arena_metrics: Dict
    ) -> Tuple[str, str]:
        """
        Recommend next Nursery action.
        
        Returns:
            (action, reasoning) where action is:
            - "PROMOTE" — best baby is ready
            - "RESPAWN" — current batch is weak, restart from Arena parent
            - "KEEP_RUNNING" — Nursery is competitive, keep current
            - "IMPORT_MOLT" — no strong babies, consider importing MOLT idea
        """
        
        if nursery_health.total_babies == 0:
            return "RESPAWN", "Nursery empty. Spawn fresh from Arena parent."
        
        if nursery_health.health_status == "STRONG" and nursery_health.best_baby.is_promotable:
            return "PROMOTE", f"Best baby {nursery_health.best_baby.variant_id} ready. Shadow PnL: {nursery_health.best_baby.shadow_pnl:.1f}bps."
        
        if nursery_health.vs_arena == "WINNING":
            return "KEEP_RUNNING", "Nursery beating Arena. Keep current pool."
        
        if nursery_health.health_status == "WEAK" and nursery_health.total_babies > 5:
            # Majority of babies are negative. Reset.
            return "RESPAWN", "Nursery pool too weak. Respawn from Arena parent."
        
        if nursery_health.clone_diversity < 0.2:
            return "RESPAWN", "Nursery too similar (low diversity). Respawn for fresh mutations."
        
        # Default: keep running, give more time
        return "KEEP_RUNNING", f"Nursery neutral. Best baby at {nursery_health.best_baby.shadow_pnl:.1f}bps. Waiting for edge development."
    
    def molt_import_recommendation(
        self,
        molt_candidates: List[Dict],
        nursery_health: NurseryHealth
    ) -> Tuple[bool, str]:
        """
        Should we import a MOLT candidate?
        
        Args:
            molt_candidates: List of MOLT suggestions with thesis/score
            nursery_health: Current Nursery health
        
        Returns:
            (should_import, reasoning)
        """
        
        if not molt_candidates:
            return False, "No MOLT candidates available"
        
        if nursery_health.health_status == "STRONG":
            return False, "Nursery already strong. No need to import."
        
        if nursery_health.health_status == "EMPTY":
            return True, "Nursery empty. Should import MOLT candidate to bootstrap."
        
        # If weakest baby is very negative, import might help diversify
        if nursery_health.worst_baby.shadow_pnl < -150:
            best_molt = max(molt_candidates, key=lambda m: m.get('score', 0))
            return True, f"Nursery weak. Import MOLT candidate: {best_molt.get('thesis', 'unknown')}"
        
        return False, "Nursery has potential. Keep current pool."
