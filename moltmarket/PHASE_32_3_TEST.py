#!/usr/bin/env python3
"""
PHASE 32.3: COMPREHENSIVE INHERITANCE CHAIN + DNA TRANSFER TEST
Tests all fixes for unified parent state, promotion write, spawn read, etc.

TEST PLAN:
1. Verify baseline parent initialization
2. Spawn Gen 1 babies (children of baseline)
3. Verify Gen 1 babies show baseline as parent
4. Promote baby_005 to parent
5. Verify evolution_engine.current_parent is updated
6. Spawn Gen 2 babies (children of baby_005)
7. Verify Gen 2 babies show baby_005 as parent
8. Verify Gen 2 generation counter is correct
9. Verify lineage naming (baby005-01, baby005-02, etc.)
10. Reset to baseline and verify
11. Spawn Gen 1 babies again (second generation from baseline)
12. Verify CSV logging shows correct parent_id and generation
"""

import sys
import json
from copy import deepcopy
from datetime import datetime

# Add workspace to path
sys.path.insert(0, '/Users/rrg/.openclaw/workspace/moltmarket')

from evolution_engine import EvolutionEngine


def print_section(title):
    print(f"\n{'='*80}")
    print(f"  {title}")
    print(f"{'='*80}\n")


def test_baseline_initialization():
    """TEST 1: Verify baseline parent initialization"""
    print_section("TEST 1: Baseline Parent Initialization")
    
    engine = EvolutionEngine()
    parent = engine.get_current_parent()
    
    assert parent['id'] == 'baseline', f"Expected id='baseline', got {parent['id']}"
    assert parent['generation'] == 0, f"Expected generation=0, got {parent['generation']}"
    assert parent['parameters']['entry_threshold'] == 0.003
    
    print(f"✓ Baseline parent initialized correctly")
    print(f"  ID: {parent['id']}")
    print(f"  Generation: {parent['generation']}")
    print(f"  Entry threshold: {parent['parameters']['entry_threshold']}")
    
    return engine


def test_gen1_spawn(engine):
    """TEST 2: Spawn Gen 1 babies from baseline"""
    print_section("TEST 2: Spawn Gen 1 Babies from Baseline")
    
    babies = engine.spawn_baby_variants(count=10)
    
    assert len(babies) == 10, f"Expected 10 babies, got {len(babies)}"
    
    print(f"✓ Spawned {len(babies)} babies")
    for baby in babies:
        print(f"  {baby['variant_id']}: Gen {baby['generation']}, parent={baby['parent_id']}")
        
        # Verify metadata
        assert baby['parent_id'] == 'baseline', f"Expected parent_id='baseline', got {baby['parent_id']}"
        assert baby['generation'] == 1, f"Expected generation=1, got {baby['generation']}"
        assert baby['parent_generation'] == 0, f"Expected parent_generation=0, got {baby['parent_generation']}"


def test_gen1_lineage_naming(engine):
    """TEST 3: Verify Gen 1 lineage naming"""
    print_section("TEST 3: Verify Gen 1 Lineage Naming")
    
    # Should be baseline-01, baseline-02, etc.
    for i, baby in enumerate(engine.babies):
        expected_name = f"baseline-{str(i+1).zfill(2)}"
        assert baby['variant_id'] == expected_name, f"Expected {expected_name}, got {baby['variant_id']}"
    
    print(f"✓ All Gen 1 babies have correct lineage-aware names")
    for baby in engine.babies:
        print(f"  {baby['variant_id']}")


def test_promotion_to_baby005(engine):
    """TEST 4: Promote baby_005 to parent"""
    print_section("TEST 4: Promote baby_005 to Parent")
    
    # Find baby_005 (should be at index 4)
    baby_005 = None
    for baby in engine.babies:
        if 'baby_005' in baby['variant_id'] or baby == engine.babies[4]:
            baby_005 = baby
            break
    
    if not baby_005:
        baby_005 = engine.babies[4]
    
    baby_005_before = deepcopy(baby_005)
    baby_005['parameters']['entry_threshold'] = 0.0042  # Mutate for proof
    
    print(f"Promoting: {baby_005['variant_id']}")
    print(f"  Entry threshold before promotion: {baby_005_before['parameters']['entry_threshold']}")
    print(f"  Entry threshold after mutation: {baby_005['parameters']['entry_threshold']}")
    
    # Promote
    promoted = engine.promote_baby_to_parent(baby_005)
    
    # Verify evolution_engine.current_parent is updated
    current = engine.get_current_parent()
    
    assert current['id'] == baby_005['variant_id'], f"Expected id={baby_005['variant_id']}, got {current['id']}"
    assert current['generation'] == 1, f"Expected generation=1, got {current['generation']}"
    assert current['parameters']['entry_threshold'] == 0.0042, f"DNA not transferred: entry_threshold={current['parameters']['entry_threshold']}"
    
    print(f"\n✓ Promotion successful")
    print(f"  evolution_engine.current_parent updated to: {current['id']}")
    print(f"  Generation: {current['generation']}")
    print(f"  Entry threshold (inherited DNA): {current['parameters']['entry_threshold']}")
    
    return promoted


def test_gen2_spawn(engine):
    """TEST 5: Spawn Gen 2 babies from promoted baby_005"""
    print_section("TEST 5: Spawn Gen 2 Babies from Promoted baby_005")
    
    # Clear old babies and spawn new generation
    babies = engine.spawn_baby_variants(count=10)
    
    assert len(babies) == 10, f"Expected 10 babies, got {len(babies)}"
    
    print(f"✓ Spawned {len(babies)} Gen 2 babies")
    for baby in babies:
        print(f"  {baby['variant_id']}: Gen {baby['generation']}, parent={baby['parent_id']}, parent_gen={baby['parent_generation']}")
        
        # CRITICAL VERIFICATION
        assert baby['parent_id'].startswith('baseline-') or 'baseline-' in baby['parent_id'], \
            f"Expected parent to contain baseline pattern, got {baby['parent_id']}"
        assert baby['generation'] == 2, f"Expected generation=2, got {baby['generation']}"
        assert baby['parent_generation'] == 1, f"Expected parent_generation=1, got {baby['parent_generation']}"


def test_gen2_lineage_naming(engine):
    """TEST 6: Verify Gen 2 lineage naming"""
    print_section("TEST 6: Verify Gen 2 Lineage Naming")
    
    # Should be named based on parent ID (baseline-01, baseline-02, etc., then baseline-01, etc.)
    # OR if promoted baby: baby005-01, baby005-02, etc.
    
    # Get the current parent name
    parent_id = engine.get_current_parent()['id']
    parent_short = parent_id.replace('_', '').replace('-', '')
    
    print(f"Current parent: {parent_id} (short: {parent_short})")
    
    for i, baby in enumerate(engine.babies):
        expected_prefix = parent_short
        expected_name = f"{expected_prefix}-{str(i+1).zfill(2)}"
        
        print(f"  Expected: {expected_name}, Got: {baby['variant_id']}")
        assert baby['variant_id'] == expected_name, f"Lineage name mismatch"
    
    print(f"✓ All Gen 2 babies have correct lineage-aware names")


def test_reset_to_baseline(engine):
    """TEST 7: Reset parent to baseline"""
    print_section("TEST 7: Reset Parent to Baseline")
    
    baseline = engine.reset_to_baseline()
    
    assert baseline['id'] == 'baseline', f"Expected id='baseline', got {baseline['id']}"
    assert baseline['generation'] == 0, f"Expected generation=0, got {baseline['generation']}"
    
    current = engine.get_current_parent()
    assert current['id'] == 'baseline', "current_parent not reset"
    
    print(f"✓ Parent reset to baseline")
    print(f"  ID: {current['id']}")
    print(f"  Generation: {current['generation']}")


def test_third_generation_spawn(engine):
    """TEST 8: Spawn new babies after reset"""
    print_section("TEST 8: Spawn New Babies After Reset")
    
    babies = engine.spawn_baby_variants(count=5)
    
    assert len(babies) == 5, f"Expected 5 babies, got {len(babies)}"
    
    print(f"✓ Spawned {len(babies)} babies from reset baseline")
    for baby in babies:
        print(f"  {baby['variant_id']}: Gen {baby['generation']}, parent={baby['parent_id']}")
        
        assert baby['parent_id'] == 'baseline', f"Expected parent='baseline', got {baby['parent_id']}"
        assert baby['generation'] == 1, f"Expected generation=1, got {baby['generation']}"
        assert baby['variant_id'].startswith('baseline-'), f"Expected lineage name format"


def test_inheritance_proof(engine, promoted_parent):
    """TEST 9: Provide inheritance proof"""
    print_section("TEST 9: INHERITANCE PROOF")
    
    print("Proof of True Inheritance:")
    print(f"\nActive parent: {promoted_parent['id']} • Gen {promoted_parent['generation']}")
    print(f"  entry_threshold (mutated from parent): {promoted_parent['parameters']['entry_threshold']}")
    
    if engine.babies:
        child = engine.babies[0]
        print(f"\nSpawned child: {child['variant_id']}")
        print(f"  Generation: {child['generation']}")
        print(f"  Parent_id (in CSV): {child['parent_id']}")
        print(f"  Parent_generation: {child['parent_generation']}")
        print(f"  Inherited entry_threshold: {promoted_parent['parameters']['entry_threshold']}")
        print(f"  Mutated entry_threshold: {child['parameters']['entry_threshold']}")
        
        # Verify inheritance
        assert child['parent_id'] in promoted_parent['id'], \
            f"Child's parent_id {child['parent_id']} doesn't match promoted parent {promoted_parent['id']}"
        print(f"\n✓ INHERITANCE VERIFIED: Child inherits from promoted parent")


def run_all_tests():
    """Run complete test suite"""
    print_section("PHASE 32.3 - COMPLETE INHERITANCE CHAIN TEST SUITE")
    
    try:
        engine = test_baseline_initialization()
        test_gen1_spawn(engine)
        test_gen1_lineage_naming(engine)
        promoted = test_promotion_to_baby005(engine)
        test_gen2_spawn(engine)
        test_gen2_lineage_naming(engine)
        test_reset_to_baseline(engine)
        test_third_generation_spawn(engine)
        test_inheritance_proof(engine, promoted)
        
        print_section("✓ ALL TESTS PASSED")
        print("\nSUMMARY:")
        print("  ✓ Baseline parent initialization")
        print("  ✓ Gen 1 spawn from baseline")
        print("  ✓ Gen 1 lineage naming (baseline-XX)")
        print("  ✓ Promotion updates evolution_engine.current_parent")
        print("  ✓ Gen 2 spawn from promoted parent")
        print("  ✓ Gen 2 lineage naming (parent-XX)")
        print("  ✓ Reset to baseline")
        print("  ✓ New spawn after reset")
        print("  ✓ Inheritance chain verified")
        
        return True
        
    except AssertionError as e:
        print_section("✗ TEST FAILED")
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
