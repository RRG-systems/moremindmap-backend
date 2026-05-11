#!/usr/bin/env python3
"""
PHASE 4.7: Replacement Engine
Candidate selection + auto-switch logic when active bot fails

Conservative, stability-first approach:
- Better to FLAT than select weak candidate
- Stability weighted higher than PnL
- Similarity penalty to avoid repeating failure
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional


class ReplacementEngine:
    """
    Selects replacement candidates from nursery when active bot fails.
    
    PHILOSOPHY:
    - Stability > PnL
    - Conservative > aggressive
    - FLAT > weak replacement
    """
    
    def __init__(self, workspace_dir: str, data_layer=None):
        """
        Initialize replacement engine.
        
        workspace_dir: Path to MOLTmarket workspace
        data_layer: DataLayer instance for accessing trade history
        """
        self.workspace = Path(workspace_dir)
        self.data_layer = data_layer
        self.nursery_file = self.workspace / 'variant_nursery.csv'
        
        # Qualification thresholds
        self.MIN_TRADE_COUNT = 20  # Minimum trades to be considered
        self.MAX_DRAWDOWN = 0.10   # 10% max drawdown
        self.MIN_SCORE_THRESHOLD = 0.50  # Minimum score to proceed (else FLAT)
        
        # Scoring weights (stability-first)
        self.WEIGHT_STABILITY = 0.40   # Highest weight
        self.WEIGHT_DRAWDOWN = 0.30    # Penalty weight
        self.WEIGHT_SAMPLE_SIZE = 0.20
        self.WEIGHT_PNL = 0.10         # Lowest weight — don't chase returns
        
        # Similarity penalty
        self.SIMILARITY_PENALTY = 0.20  # Reduce score by 20% if too similar
        
        self.replacement_log = []
    
    def get_candidate_pool(self, exclude_bot_id: Optional[str] = None) -> List[Dict]:
        """
        Extract candidates from nursery.
        
        exclude_bot_id: Bot to exclude from pool (usually current/failed bot)
        
        Returns: List of candidate dicts with metrics
        """
        if not self.nursery_file.exists():
            print(f"[REPLACEMENT] Nursery file not found: {self.nursery_file}")
            return []
        
        candidates = []
        
        try:
            with open(self.nursery_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    bot_id = row.get('variant_id', '')
                    
                    # Skip excluded bot
                    if exclude_bot_id and bot_id == exclude_bot_id:
                        continue
                    
                    # Parse metrics
                    try:
                        trade_count = int(row.get('trade_count', 0))
                        pnl = float(row.get('shadow_pnl', 0))  # Use shadow (realistic)
                        drawdown = float(row.get('degradation_pct', 0)) / 100.0  # Convert to decimal
                        sign_flips = float(row.get('sign_flip_rate', 0))
                        existing_score = float(row.get('score', 0))
                        
                        candidate = {
                            'bot_id': bot_id,
                            'parent_id': row.get('parent_id', ''),
                            'generation': int(row.get('generation', 0)),
                            'mutation_type': row.get('mutation_type', ''),
                            'trade_count': trade_count,
                            'pnl': pnl,
                            'drawdown': drawdown,
                            'sign_flip_rate': sign_flips,
                            'existing_score': existing_score,
                        }
                        candidates.append(candidate)
                    except (ValueError, TypeError) as e:
                        print(f"[REPLACEMENT] Skipping row (parse error): {bot_id} — {e}")
                        continue
            
            print(f"[REPLACEMENT] Candidate pool: {len(candidates)} bots from nursery")
            return candidates
        
        except Exception as e:
            print(f"[REPLACEMENT] ERROR reading nursery: {type(e).__name__}: {e}")
            return []
    
    def filter_qualified_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """
        Filter out candidates that don't meet minimum criteria.
        
        PART 2: Minimum Qualification Filter
        """
        qualified = []
        
        for candidate in candidates:
            bot_id = candidate['bot_id']
            trade_count = candidate['trade_count']
            drawdown = candidate['drawdown']
            sign_flips = candidate['sign_flip_rate']
            
            # Check 1: Minimum trade count
            if trade_count < self.MIN_TRADE_COUNT:
                print(f"[REPLACEMENT] REJECT {bot_id}: insufficient trades ({trade_count} < {self.MIN_TRADE_COUNT})")
                continue
            
            # Check 2: Excessive drawdown
            if drawdown > self.MAX_DRAWDOWN:
                print(f"[REPLACEMENT] REJECT {bot_id}: excessive drawdown ({drawdown:.1%} > {self.MAX_DRAWDOWN:.1%})")
                continue
            
            # Check 3: Extreme sign flip rate (indicator of unreliability)
            if sign_flips > 0.30:  # More than 30% flips = unreliable
                print(f"[REPLACEMENT] REJECT {bot_id}: high sign flip rate ({sign_flips:.1%})")
                continue
            
            # Passed all filters
            qualified.append(candidate)
        
        print(f"[REPLACEMENT] Qualified candidates: {len(qualified)}/{len(candidates)}")
        return qualified
    
    def calculate_stability_score(self, candidate: Dict) -> float:
        """
        Calculate stability metric for candidate.
        
        Lower variance = higher stability
        Proxy: low sign flip rate + moderate trade count + low drawdown
        """
        sign_flips = candidate['sign_flip_rate']
        trade_count = candidate['trade_count']
        drawdown = candidate['drawdown']
        
        # Stability = inverse of variability
        # Low sign flips = stable, low drawdown = stable
        stability = (1.0 - sign_flips) * (1.0 - drawdown)
        
        # Normalize to 0-1
        stability = max(0.0, min(1.0, stability))
        
        return stability
    
    def calculate_candidate_score(self, candidate: Dict, failed_bot_id: Optional[str] = None) -> float:
        """
        Calculate comprehensive score for candidate.
        
        PART 3: Candidate Scoring (stability-first, conservative)
        """
        stability = self.calculate_stability_score(candidate)
        
        # Drawdown penalty (lower is better)
        drawdown_penalty = candidate['drawdown'] / self.MAX_DRAWDOWN  # 0-1 scale
        drawdown_penalty = min(1.0, drawdown_penalty)
        
        # Sample size score (more data = more trust)
        # Scale: 20 trades = 0.0, 100+ trades = 1.0
        sample_size = min(candidate['trade_count'] / 100.0, 1.0)
        
        # PnL score (LOWEST weight, don't chase returns)
        # Normalize around 0: -$100 to +$100 → 0-1 scale
        pnl_normalized = (candidate['pnl'] + 100.0) / 200.0
        pnl_normalized = max(0.0, min(1.0, pnl_normalized))
        
        # Weighted score
        score = (
            stability * self.WEIGHT_STABILITY +
            (1.0 - drawdown_penalty) * self.WEIGHT_DRAWDOWN +
            sample_size * self.WEIGHT_SAMPLE_SIZE +
            pnl_normalized * self.WEIGHT_PNL
        )
        
        # PART 4: Diversity filter — penalize similarity to failed bot
        if failed_bot_id:
            if self._is_similar_to_failed_bot(candidate, failed_bot_id):
                score *= (1.0 - self.SIMILARITY_PENALTY)  # Reduce by 20%
                print(f"[REPLACEMENT] Similarity penalty applied to {candidate['bot_id']}")
        
        return max(0.0, min(1.0, score))
    
    def _is_similar_to_failed_bot(self, candidate: Dict, failed_bot_id: str) -> bool:
        """
        Check if candidate is too similar to failed bot (avoid repeating failure).
        
        PART 4: Diversity filter
        """
        # Simple heuristic: if same parent and recent generation
        # (Could expand to parameter comparison later)
        
        # For now: if same parent and within 2 generations, consider similar
        # This prevents selecting a near-clone of the failed bot
        
        # TODO: In production, could compare parameter vectors
        return False  # Placeholder — implement if parent/generation data available
    
    def select_replacement(self, exclude_bot_id: Optional[str] = None) -> Tuple[Optional[Dict], bool]:
        """
        PART 5: Selection logic
        
        Returns: (selected_candidate, should_use_flat)
        - If valid candidate found: (candidate_dict, False)
        - If no valid candidate: (None, True)  → BRAIN should go FLAT
        """
        print(f"\n[REPLACEMENT] Starting candidate evaluation...")
        
        # Step 1: Get candidate pool
        candidates = self.get_candidate_pool(exclude_bot_id)
        
        if not candidates:
            print(f"[REPLACEMENT] FLAT: No candidates available")
            return None, True
        
        # Step 2: Filter qualified
        qualified = self.filter_qualified_candidates(candidates)
        
        if not qualified:
            print(f"[REPLACEMENT] FLAT: No qualified candidates (all rejected)")
            return None, True
        
        # Step 3: Score all qualified candidates
        scored = []
        for candidate in qualified:
            score = self.calculate_candidate_score(candidate, exclude_bot_id)
            scored.append((score, candidate))
        
        # Step 4: Sort by score (highest first)
        scored.sort(key=lambda x: x[0], reverse=True)
        
        # Log top 3
        print(f"\n[REPLACEMENT] Top candidates:")
        for i, (score, candidate) in enumerate(scored[:3], 1):
            print(f"  {i}. {candidate['bot_id']}: score={score:.3f} | trades={candidate['trade_count']} | pnl=${candidate['pnl']:.2f}")
        
        # Step 5: Check if best candidate passes minimum threshold
        best_score, best_candidate = scored[0]
        
        if best_score < self.MIN_SCORE_THRESHOLD:
            print(f"\n[REPLACEMENT] FLAT: Best candidate score ({best_score:.3f}) below threshold ({self.MIN_SCORE_THRESHOLD:.3f})")
            return None, True
        
        # Step 6: Selection successful
        print(f"\n[REPLACEMENT] SELECTED: {best_candidate['bot_id']} (score={best_score:.3f})")
        return best_candidate, False
    
    def execute_switch(self, new_candidate: Dict, old_bot_id: str, reason_code: str) -> Dict:
        """
        PART 6: Switch execution
        
        Log switch decision and return update for BRAIN state.
        """
        switch_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'old_bot_id': old_bot_id,
            'new_bot_id': new_candidate['bot_id'],
            'reason': reason_code,
            'new_bot_score': 0,  # Will be populated by caller
            'action': 'SWITCH',
        }
        
        print(f"\n[BRAIN] SWITCH — from {old_bot_id} to {new_candidate['bot_id']}")
        print(f"  reason: {reason_code}")
        print(f"  generation: {new_candidate['generation']}")
        print(f"  trades: {new_candidate['trade_count']}")
        
        self.replacement_log.append(switch_record)
        
        return {
            'active_bot_id': new_candidate['bot_id'],
            'replacement_reason': reason_code,
        }
    
    def execute_flat(self, old_bot_id: str, reason_code: str) -> Dict:
        """
        PART 7: FLAT fallback
        
        No valid replacement available — system must go FLAT.
        """
        flat_record = {
            'timestamp': datetime.utcnow().isoformat(),
            'old_bot_id': old_bot_id,
            'reason': reason_code,
            'action': 'FLAT',
        }
        
        print(f"\n[BRAIN] FLAT — no qualified replacement candidate")
        print(f"  old_bot: {old_bot_id}")
        print(f"  reason: {reason_code}")
        
        self.replacement_log.append(flat_record)
        
        return {
            'active_bot_id': None,
            'replacement_reason': reason_code,
        }
    
    def get_replacement_log(self, limit: int = 20) -> List[Dict]:
        """Get recent replacement decisions"""
        return self.replacement_log[-limit:]


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PHASE 4.7 Replacement Engine Test")
    print("=" * 80)
    
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    
    # Test 1: Get candidates
    print("\n[TEST 1] Get candidate pool...")
    candidates = engine.get_candidate_pool()
    print(f"Result: {len(candidates)} candidates")
    
    # Test 2: Filter qualified
    print("\n[TEST 2] Filter qualified...")
    qualified = engine.filter_qualified_candidates(candidates)
    print(f"Result: {len(qualified)} qualified")
    
    # Test 3: Select replacement
    print("\n[TEST 3] Select replacement (exclude 'baseline')...")
    selected, should_flat = engine.select_replacement(exclude_bot_id='baseline')
    if selected:
        print(f"Result: Selected {selected['bot_id']}")
    else:
        print(f"Result: No qualified candidate → FLAT")
    
    print("\n" + "=" * 80)
