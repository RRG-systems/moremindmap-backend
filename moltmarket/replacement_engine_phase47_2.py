#!/usr/bin/env python3
"""
PHASE 4.6.3: Replacement Engine Enhanced
Churn prevention + confidence collapse → FLAT

Fixes the churn issue by:
1. Tracking replacement attempts
2. Detecting low diversity in candidate pool
3. Computing confidence score
4. Going FLAT when all candidates look the same
"""

import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import deque


class ReplacementEnginePhase463:
    """
    Enhanced replacement engine with churn prevention.
    
    Key addition: Detects when all candidates are effectively identical
    and triggers FLAT instead of cycling through them.
    """
    
    def __init__(self, workspace_dir: str, data_layer=None):
        """Initialize replacement engine with churn tracking"""
        self.workspace = Path(workspace_dir)
        self.data_layer = data_layer
        self.nursery_file = self.workspace / 'variant_nursery.csv'
        
        # Qualification thresholds
        self.MIN_TRADE_COUNT = 20
        self.MAX_DRAWDOWN = 0.10
        self.MIN_SCORE_THRESHOLD = 0.50
        
        # Scoring weights (stability-first)
        self.WEIGHT_STABILITY = 0.40
        self.WEIGHT_DRAWDOWN = 0.30
        self.WEIGHT_SAMPLE_SIZE = 0.20
        self.WEIGHT_PNL = 0.10
        
        self.SIMILARITY_PENALTY = 0.20
        
        # PHASE 4.6.3: Churn prevention
        self.replacement_attempts = deque(maxlen=20)  # Track last 20 cycles
        self.MAX_REPLACEMENT_ATTEMPTS = 3  # Max 3 replacements in window
        self.DIVERSITY_TOLERANCE = 0.05  # 5% tolerance band for similarity
        self.MIN_CONFIDENCE_THRESHOLD = 0.15  # Min variance between candidates
        
        self.replacement_log = []
        self.churn_detected = False
    
    def record_replacement_attempt(self):
        """Record that a replacement was attempted"""
        self.replacement_attempts.append(datetime.utcnow())
    
    def get_recent_replacement_count(self) -> int:
        """Get number of replacements in recent window"""
        return len(self.replacement_attempts)
    
    def detect_churn(self) -> Tuple[bool, str]:
        """
        PART 2: Churn detection
        
        Detects: Too many replacement attempts in short period.
        """
        recent_count = self.get_recent_replacement_count()
        
        if recent_count >= self.MAX_REPLACEMENT_ATTEMPTS:
            return True, f"Too many replacements ({recent_count} >= {self.MAX_REPLACEMENT_ATTEMPTS})"
        
        return False, ""
    
    def get_candidate_pool(self, exclude_bot_id: Optional[str] = None) -> List[Dict]:
        """Extract candidates from nursery"""
        if not self.nursery_file.exists():
            print(f"[REPLACEMENT] Nursery file not found: {self.nursery_file}")
            return []
        
        candidates = []
        
        try:
            with open(self.nursery_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    bot_id = row.get('variant_id', '')
                    
                    if exclude_bot_id and bot_id == exclude_bot_id:
                        continue
                    
                    try:
                        trade_count = int(row.get('trade_count', 0))
                        pnl = float(row.get('shadow_pnl', 0))
                        drawdown = float(row.get('degradation_pct', 0)) / 100.0
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
                        continue
            
            return candidates
        
        except Exception as e:
            print(f"[REPLACEMENT] ERROR reading nursery: {type(e).__name__}: {e}")
            return []
    
    def filter_qualified_candidates(self, candidates: List[Dict]) -> List[Dict]:
        """Filter qualified candidates"""
        qualified = []
        
        for candidate in candidates:
            if candidate['trade_count'] < self.MIN_TRADE_COUNT:
                continue
            if candidate['drawdown'] > self.MAX_DRAWDOWN:
                continue
            if candidate['sign_flip_rate'] > 0.30:
                continue
            
            qualified.append(candidate)
        
        return qualified
    
    def calculate_stability_score(self, candidate: Dict) -> float:
        """Calculate stability metric"""
        sign_flips = candidate['sign_flip_rate']
        drawdown = candidate['drawdown']
        
        stability = (1.0 - sign_flips) * (1.0 - drawdown)
        return max(0.0, min(1.0, stability))
    
    def calculate_candidate_score(self, candidate: Dict, failed_bot_id: Optional[str] = None) -> float:
        """Calculate comprehensive score"""
        stability = self.calculate_stability_score(candidate)
        drawdown_penalty = min(1.0, candidate['drawdown'] / self.MAX_DRAWDOWN)
        sample_size = min(candidate['trade_count'] / 100.0, 1.0)
        pnl_normalized = max(0.0, min(1.0, (candidate['pnl'] + 100.0) / 200.0))
        
        score = (
            stability * self.WEIGHT_STABILITY +
            (1.0 - drawdown_penalty) * self.WEIGHT_DRAWDOWN +
            sample_size * self.WEIGHT_SAMPLE_SIZE +
            pnl_normalized * self.WEIGHT_PNL
        )
        
        return max(0.0, min(1.0, score))
    
    def compute_candidate_diversity(self, qualified: List[Dict]) -> float:
        """
        PART 3 & 4: Compute diversity/confidence score
        
        If candidates are very similar (low diversity),
        confidence is low.
        """
        if len(qualified) <= 1:
            return 0.0
        
        # Score all candidates
        scores = [self.calculate_candidate_score(c) for c in qualified]
        
        # Calculate variance (diversity)
        if len(scores) < 2:
            return 0.0
        
        mean_score = sum(scores) / len(scores)
        variance = sum((s - mean_score) ** 2 for s in scores) / len(scores)
        std_dev = variance ** 0.5
        
        # Convert to 0-1 confidence scale (higher variance = higher confidence)
        # If std_dev is very small, confidence is low
        confidence = min(1.0, std_dev * 10)  # Scale factor to make meaningful
        
        return confidence
    
    def check_diversity_collapse(self, qualified: List[Dict]) -> Tuple[bool, str]:
        """
        PART 3: Diversity / similarity check
        
        If all candidates are within small tolerance band,
        treat as low diversity → FLAT.
        """
        if len(qualified) <= 1:
            return False, ""
        
        # Score all candidates
        scores = [self.calculate_candidate_score(c) for c in qualified]
        min_score = min(scores)
        max_score = max(scores)
        diff = max_score - min_score
        
        # If difference is too small, candidates are effectively identical
        if diff < self.DIVERSITY_TOLERANCE:
            confidence = self.compute_candidate_diversity(qualified)
            if confidence < self.MIN_CONFIDENCE_THRESHOLD:
                return True, f"Low diversity detected (confidence: {confidence:.3f})"
        
        return False, ""
    
    def select_replacement(self, exclude_bot_id: Optional[str] = None) -> Tuple[Optional[Dict], bool, str]:
        """
        Enhanced selection with churn prevention.
        
        Returns: (selected_candidate, should_flat, flat_reason)
        """
        print(f"\n[REPLACEMENT] Starting candidate evaluation...")
        
        # Check 1: Churn detection (PART 2)
        churn_detected, churn_reason = self.detect_churn()
        if churn_detected:
            print(f"[REPLACEMENT] CHURN DETECTED: {churn_reason}")
            return None, True, churn_reason
        
        # Check 2: Get candidate pool
        candidates = self.get_candidate_pool(exclude_bot_id)
        
        if not candidates:
            print(f"[REPLACEMENT] FLAT: No candidates available")
            return None, True, "No candidates available"
        
        # Check 3: Filter qualified
        qualified = self.filter_qualified_candidates(candidates)
        
        if not qualified:
            print(f"[REPLACEMENT] FLAT: No qualified candidates")
            return None, True, "No qualified candidates"
        
        # Check 4: Diversity collapse (PART 3)
        diversity_collapsed, diversity_reason = self.check_diversity_collapse(qualified)
        if diversity_collapsed:
            print(f"[REPLACEMENT] FLAT: {diversity_reason}")
            return None, True, diversity_reason
        
        # Check 5: Score and select
        scored = []
        for candidate in qualified:
            score = self.calculate_candidate_score(candidate, exclude_bot_id)
            scored.append((score, candidate))
        
        scored.sort(key=lambda x: x[0], reverse=True)
        
        print(f"\n[REPLACEMENT] Top candidates:")
        for i, (score, candidate) in enumerate(scored[:3], 1):
            print(f"  {i}. {candidate['bot_id']}: score={score:.3f}")
        
        # Check 6: Minimum threshold
        best_score, best_candidate = scored[0]
        
        if best_score < self.MIN_SCORE_THRESHOLD:
            print(f"\n[REPLACEMENT] FLAT: Best score ({best_score:.3f}) below threshold")
            return None, True, "Best candidate below score threshold"
        
        # Check 7: Selection successful
        print(f"\n[REPLACEMENT] SELECTED: {best_candidate['bot_id']}")
        self.record_replacement_attempt()
        
        return best_candidate, False, ""
    
    def get_replacement_log(self, limit: int = 20) -> List[Dict]:
        """Get recent replacement decisions"""
        return self.replacement_log[-limit:]


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PHASE 4.6.3: Replacement Engine Enhanced — Churn Prevention Test")
    print("=" * 80)
    
    engine = ReplacementEnginePhase463(workspace_dir=Path.cwd())
    
    # Test 1: Churn detection
    print("\nTest 1: Churn detection (too many replacements)")
    print("-" * 80)
    
    # Simulate 4 replacement attempts
    for i in range(4):
        engine.record_replacement_attempt()
    
    churn, reason = engine.detect_churn()
    print(f"Replacement attempts: {engine.get_recent_replacement_count()}")
    print(f"Churn detected: {churn}")
    print(f"Reason: {reason}")
    
    assert churn, "Should detect churn after 4 attempts"
    print("✅ PASS\n")
    
    # Test 2: Diversity check
    print("Test 2: Diversity collapse detection")
    print("-" * 80)
    
    # Create identical candidates
    identical_candidates = [
        {'bot_id': f'baby_{i}', 'trade_count': 30, 'pnl': 100.0, 'drawdown': 0.03, 'sign_flip_rate': 0.08}
        for i in range(3)
    ]
    
    engine2 = ReplacementEnginePhase463(workspace_dir=Path.cwd())
    collapsed, reason = engine2.check_diversity_collapse(identical_candidates)
    
    print(f"Identical candidates (all similar metrics)")
    print(f"Diversity collapsed: {collapsed}")
    if reason:
        print(f"Reason: {reason}")
    
    assert collapsed, "Should detect diversity collapse with identical candidates"
    print("✅ PASS\n")
    
    print("=" * 80)
    print("✅ PHASE 4.6.3 TESTS PASSED")
    print("=" * 80 + "\n")
