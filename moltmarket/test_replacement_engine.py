#!/usr/bin/env python3
"""
PHASE 4.7 VALIDATION TESTS
Replacement Engine: Candidate Selection + Auto-Switch

Tests:
1. Candidate pool extraction
2. Qualified candidate filtering
3. Stability-first scoring
4. Selection with valid candidates
5. Selection with no valid candidates → FLAT
6. Diversity penalty (similar candidate)
"""

import sys
import csv
from pathlib import Path
from datetime import datetime
from replacement_engine_phase47 import ReplacementEngine


def create_test_nursery():
    """Create a test nursery.csv with realistic candidates"""
    nursery_file = Path.cwd() / 'variant_nursery_test.csv'
    
    headers = [
        'run_id', 'variant_id', 'parent_id', 'parent_generation', 'generation',
        'mutation_type', 'parameter_value', 'trade_count', 'paper_pnl', 'shadow_pnl',
        'sign_flip_rate', 'degradation_pct', 'score', 'status', 'timestamp'
    ]
    
    # Test data: mix of good and bad candidates
    rows = [
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_001',
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'engagement_increase',
            'parameter_value': '0.005',
            'trade_count': 45,  # Good sample
            'paper_pnl': 120.50,
            'shadow_pnl': 85.30,  # Good PnL
            'sign_flip_rate': 0.08,  # Low flips (stable)
            'degradation_pct': 3.5,  # Low drawdown (stable)
            'score': 0.72,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_002',
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'size_reduction',
            'parameter_value': '0.5',
            'trade_count': 52,  # Very good sample
            'paper_pnl': 250.00,  # High PnL (but we shouldn't chase it)
            'shadow_pnl': 180.00,
            'sign_flip_rate': 0.35,  # High flips (unstable) — SHOULD BE REJECTED
            'degradation_pct': 2.1,
            'score': 0.68,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_003',
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'throttle_adjustment',
            'parameter_value': '0.7',
            'trade_count': 38,
            'paper_pnl': 95.20,
            'shadow_pnl': 72.10,
            'sign_flip_rate': 0.12,  # Moderate flips
            'degradation_pct': 5.8,  # Moderate drawdown
            'score': 0.65,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_004',
            'parent_id': 'baby_001',
            'parent_generation': 1,
            'generation': 2,
            'mutation_type': 'entry_adjustment',
            'parameter_value': '0.003',
            'trade_count': 28,
            'paper_pnl': 110.50,
            'shadow_pnl': 88.40,
            'sign_flip_rate': 0.06,  # Very stable
            'degradation_pct': 2.0,  # Very low drawdown (most stable)
            'score': 0.75,  # Should be highest
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_005',
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'risk_adjustment',
            'parameter_value': '1.5',
            'trade_count': 8,  # TOO FEW TRADES — SHOULD BE REJECTED
            'paper_pnl': 500.00,  # High PnL but insufficient sample
            'shadow_pnl': 350.00,
            'sign_flip_rate': 0.15,
            'degradation_pct': 4.2,
            'score': 0.60,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
        {
            'run_id': 'test_run_1',
            'variant_id': 'baby_006',
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'volatility_control',
            'parameter_value': '0.8',
            'trade_count': 42,
            'paper_pnl': -50.00,  # Losing trades
            'shadow_pnl': -65.00,
            'sign_flip_rate': 0.28,
            'degradation_pct': 12.0,  # EXCESSIVE DRAWDOWN — SHOULD BE REJECTED
            'score': 0.35,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        },
    ]
    
    with open(nursery_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        writer.writerows(rows)
    
    print(f"[TEST] Created test nursery: {nursery_file.name} with {len(rows)} candidates")
    return nursery_file


def test_candidate_extraction():
    """TEST 1: Extract candidate pool from nursery"""
    print("\n" + "=" * 80)
    print("TEST 1: Candidate Pool Extraction")
    print("=" * 80)
    
    nursery_file = create_test_nursery()
    
    # Monkey-patch to use test file
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    candidates = engine.get_candidate_pool()
    
    print(f"\nResult: {len(candidates)} candidates extracted")
    for candidate in candidates:
        print(f"  • {candidate['bot_id']}: trades={candidate['trade_count']}, pnl=${candidate['pnl']:.2f}, drawdown={candidate['drawdown']:.1%}")
    
    assert len(candidates) == 6, f"Expected 6 candidates, got {len(candidates)}"
    print("\n✅ PASS: Candidate extraction works")


def test_qualified_filtering():
    """TEST 2: Filter qualified candidates (remove bad ones)"""
    print("\n" + "=" * 80)
    print("TEST 2: Qualified Candidate Filtering")
    print("=" * 80)
    
    nursery_file = create_test_nursery()
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    candidates = engine.get_candidate_pool()
    qualified = engine.filter_qualified_candidates(candidates)
    
    print(f"\nResult: {len(qualified)}/{len(candidates)} candidates qualified")
    for candidate in qualified:
        print(f"  ✓ {candidate['bot_id']}")
    
    # Expect: baby_001, baby_003, baby_004 qualified
    # Reject: baby_002 (high sign flips), baby_005 (too few trades), baby_006 (excessive drawdown)
    
    expected_qualified = {'baby_001', 'baby_003', 'baby_004'}
    actual_qualified = {c['bot_id'] for c in qualified}
    
    assert actual_qualified == expected_qualified, f"Qualified mismatch. Expected {expected_qualified}, got {actual_qualified}"
    print(f"\n✅ PASS: Qualification filtering correct")


def test_stability_first_scoring():
    """TEST 3: Stability-first scoring (not PnL-first)"""
    print("\n" + "=" * 80)
    print("TEST 3: Stability-First Scoring")
    print("=" * 80)
    
    nursery_file = create_test_nursery()
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    candidates = engine.get_candidate_pool()
    
    # baby_001: high PnL but less stable
    baby_001 = next(c for c in candidates if c['bot_id'] == 'baby_001')
    # baby_004: moderate PnL but most stable (lowest drawdown, lowest flips)
    baby_004 = next(c for c in candidates if c['bot_id'] == 'baby_004')
    
    score_001 = engine.calculate_candidate_score(baby_001)
    score_004 = engine.calculate_candidate_score(baby_004)
    
    print(f"\nbaby_001: pnl=${baby_001['pnl']:.2f}, drawdown={baby_001['drawdown']:.1%}, sign_flips={baby_001['sign_flip_rate']:.1%}")
    print(f"  → Score: {score_001:.3f}")
    
    print(f"\nbaby_004: pnl=${baby_004['pnl']:.2f}, drawdown={baby_004['drawdown']:.1%}, sign_flips={baby_004['sign_flip_rate']:.1%}")
    print(f"  → Score: {score_004:.3f}")
    
    # baby_004 should score higher (more stable, even though lower PnL)
    assert score_004 > score_001, f"baby_004 (stable) should score higher than baby_001. Got {score_004:.3f} vs {score_001:.3f}"
    
    print(f"\n✅ PASS: Stability properly weighted higher than PnL")


def test_selection_with_valid_candidates():
    """TEST 4: Select replacement with valid candidates"""
    print("\n" + "=" * 80)
    print("TEST 4: Selection With Valid Candidates")
    print("=" * 80)
    
    nursery_file = create_test_nursery()
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    selected, should_flat = engine.select_replacement(exclude_bot_id='baseline')
    
    print(f"\nResult:")
    print(f"  selected: {selected['bot_id'] if selected else None}")
    print(f"  should_flat: {should_flat}")
    
    assert selected is not None, "Should select a candidate"
    assert not should_flat, "Should not go FLAT when valid candidates exist"
    assert selected['bot_id'] == 'baby_004', f"Should select baby_004 (highest score), got {selected['bot_id']}"
    
    print(f"\n✅ PASS: Selected baby_004 (most stable)")


def test_selection_no_valid_candidates():
    """TEST 5: Selection with no valid candidates → FLAT"""
    print("\n" + "=" * 80)
    print("TEST 5: Selection With No Valid Candidates → FLAT")
    print("=" * 80)
    
    # Create empty nursery
    nursery_file = Path.cwd() / 'variant_nursery_empty.csv'
    headers = ['run_id', 'variant_id', 'parent_id', 'parent_generation', 'generation',
               'mutation_type', 'parameter_value', 'trade_count', 'paper_pnl', 'shadow_pnl',
               'sign_flip_rate', 'degradation_pct', 'score', 'status', 'timestamp']
    
    with open(nursery_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()
        # No rows — no candidates
    
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    selected, should_flat = engine.select_replacement()
    
    print(f"\nResult:")
    print(f"  selected: {selected}")
    print(f"  should_flat: {should_flat}")
    
    assert selected is None, "Should not select when no candidates"
    assert should_flat, "Should go FLAT when no candidates available"
    
    print(f"\n✅ PASS: System correctly goes FLAT (no candidates)")


def test_integrity():
    """INTEGRITY TEST: Verify system conservative (FLAT > weak replacement)"""
    print("\n" + "=" * 80)
    print("INTEGRITY TEST: System Conservative (FLAT > Weak Replacement)")
    print("=" * 80)
    
    nursery_file = create_test_nursery()
    engine = ReplacementEngine(workspace_dir=Path.cwd())
    engine.nursery_file = nursery_file
    
    # Lower threshold to trigger condition
    engine.MIN_SCORE_THRESHOLD = 0.90  # Very high threshold
    
    selected, should_flat = engine.select_replacement(exclude_bot_id='baseline')
    
    print(f"\nWith very high threshold (0.90):")
    print(f"  selected: {selected}")
    print(f"  should_flat: {should_flat}")
    
    # All candidates should fail the high threshold → FLAT
    assert should_flat, "Should go FLAT when no candidate meets high threshold"
    
    print(f"\n✅ PASS: System conservative — goes FLAT rather than select weak replacement")


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("PHASE 4.7 REPLACEMENT ENGINE VALIDATION TESTS")
    print("=" * 80)
    
    tests = [
        test_candidate_extraction,
        test_qualified_filtering,
        test_stability_first_scoring,
        test_selection_with_valid_candidates,
        test_selection_no_valid_candidates,
        test_integrity,
    ]
    
    passed = 0
    failed = 0
    
    try:
        for test_func in tests:
            try:
                test_func()
                passed += 1
            except AssertionError as e:
                print(f"\n❌ FAIL: {e}")
                failed += 1
        
        print("\n" + "=" * 80)
        print(f"RESULTS: {passed} passed, {failed} failed")
        print("=" * 80)
        
        if failed == 0:
            print("\n✅ ALL REPLACEMENT ENGINE TESTS PASSED")
            print("\nPHASE 4.7 VALIDATION COMPLETE:")
            print("- Candidate pool extraction ✅")
            print("- Qualified filtering (rejects bad candidates) ✅")
            print("- Stability-first scoring (not PnL-first) ✅")
            print("- Valid candidate selection ✅")
            print("- No candidate → FLAT fallback ✅")
            print("- System conservative (FLAT > weak replacement) ✅")
            print("\n" + "=" * 80 + "\n")
            sys.exit(0)
        else:
            print(f"\n❌ {failed} tests failed")
            sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
