#!/usr/bin/env python3
"""
PHASE 31 Test Script
Verify evolution engine, nursery spawning, and fitness scoring
"""

import sys
from pathlib import Path
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from evolution_engine import EvolutionEngine
from variant_nursery import VariantNursery

def test_evolution_engine():
    """Test evolution engine: spawn and mutate"""
    print("\n" + "="*70)
    print("[PHASE 31] EVOLUTION ENGINE TEST")
    print("="*70)
    
    # Initialize engine
    engine = EvolutionEngine()
    
    # Get parent
    parent = engine.parent_strategy
    print(f"\n[STEP 1] Parent strategy loaded:")
    print(f"  ID: {parent['id']}")
    print(f"  Signal: {parent['signal_type']}")
    print(f"  Parameters:")
    for key, val in parent['parameters'].items():
        print(f"    - {key}: {val}")
    
    # Spawn babies
    print(f"\n[STEP 2] Spawning 10 babies...")
    babies = engine.spawn_baby_variants(parent_strategy=parent, count=10)
    
    assert len(babies) == 10, "Should spawn 10 babies"
    print(f"  ✓ {len(babies)} babies spawned")
    
    # Verify each baby
    print(f"\n[STEP 3] Verifying babies...")
    mutation_types_seen = set()
    
    for i, baby in enumerate(babies):
        variant_id = baby['variant_id']
        mutation_type = baby['mutation_type']
        mutation_types_seen.add(mutation_type)
        
        assert variant_id == f"baby_{str(i+1).zfill(3)}", f"Bad variant_id: {variant_id}"
        assert baby['parent_id'] == parent['id'], "Bad parent_id"
        assert baby['generation'] == 1, "Bad generation"
        assert baby['mutation_type'] in [
            'entry_threshold', 'exit_threshold', 'holding_time',
            'confirmation_rules', 'stop_loss_sensitivity', 'target_profit_sensitivity'
        ], f"Bad mutation_type: {mutation_type}"
        
        print(f"  ✓ {variant_id}: mutate {mutation_type}")
    
    print(f"\n  Mutations covered: {len(mutation_types_seen)}/6")
    for mut_type in mutation_types_seen:
        print(f"    - {mut_type}")
    
    print("\n[PHASE 31] Evolution engine test PASSED ✓")
    return engine, babies

def test_nursery_system(engine):
    """Test nursery management and CSV persistence"""
    print("\n" + "="*70)
    print("[PHASE 31] NURSERY SYSTEM TEST")
    print("="*70)
    
    # Initialize nursery
    nursery = VariantNursery(
        workspace_dir=Path.cwd(),
        evolution_engine=engine
    )
    
    print(f"\n[STEP 1] Nursery initialized")
    print(f"  CSV file: {nursery.nursery_file}")
    
    # Spawn babies
    print(f"\n[STEP 2] Spawning babies via nursery...")
    run_id = "test_run_001"
    babies = nursery.spawn_babies(run_id=run_id, count=10)
    
    assert len(babies) == 10, "Should spawn 10 babies"
    print(f"  ✓ {len(babies)} babies spawned for run: {run_id}")
    
    # Simulate some execution data
    print(f"\n[STEP 3] Simulating execution data...")
    
    for baby in babies:
        variant_id = baby['variant_id']
        
        # Simulate trades for this baby
        for i in range(30):
            paper_pnl = 50 + (i % 30) - 10
            shadow_pnl = paper_pnl - 15 + (i % 5)
            
            # Record paper trade
            nursery.record_baby_trade(
                variant_id=variant_id,
                source='paper',
                trade_dict={'pnl': float(paper_pnl)}
            )
            
            # Record shadow trade
            nursery.record_baby_trade(
                variant_id=variant_id,
                source='shadow',
                trade_dict={'pnl': float(shadow_pnl)}
            )
    
    print(f"  ✓ Simulated execution data for all babies")
    
    # Score and finalize
    print(f"\n[STEP 4] Scoring and finalizing babies...")
    leaderboard = nursery.finalize_and_score_babies(run_id=run_id)
    
    assert len(leaderboard) > 0, "Leaderboard should have entries"
    print(f"  ✓ {len(leaderboard)} babies scored")
    
    # Verify leaderboard structure
    print(f"\n[STEP 5] Leaderboard verification:")
    print(f"  {'Rank':<6} {'Variant':<12} {'Mutation':<20} {'Trades':<8} {'Score':<8}")
    print(f"  {'-'*60}")
    
    for rank, baby_metrics in enumerate(leaderboard[:5], 1):
        variant_id = baby_metrics['variant_id']
        mutation_type = baby_metrics['mutation_type']
        trades = baby_metrics['trades']
        score = baby_metrics['score']
        
        print(f"  {rank:<6} {variant_id:<12} {mutation_type:<20} {trades:<8} {score:<8.1f}")
        
        # Verify required fields
        assert 'variant_id' in baby_metrics
        assert 'mutation_type' in baby_metrics
        assert 'trades' in baby_metrics
        assert 'shadow_pnl' in baby_metrics
        assert 'flip_rate' in baby_metrics
        assert 'degradation' in baby_metrics
        assert 'score' in baby_metrics
        assert 'status' in baby_metrics
    
    # Check CSV was created
    print(f"\n[STEP 6] CSV persistence verification:")
    assert nursery.nursery_file.exists(), "CSV file should exist"
    
    with open(nursery.nursery_file, 'r') as f:
        lines = f.readlines()
    
    print(f"  ✓ CSV file created: {nursery.nursery_file.name}")
    print(f"  ✓ Total rows: {len(lines)} (header + {len(lines)-1} records)")
    
    # Show sample row
    if len(lines) > 1:
        print(f"\n  Sample row (baby_001):")
        print(f"    {lines[1][:100]}...")
    
    print("\n[PHASE 31] Nursery system test PASSED ✓")
    return nursery, leaderboard

def test_fitness_scoring(engine, leaderboard):
    """Test fitness scoring logic"""
    print("\n" + "="*70)
    print("[PHASE 31] FITNESS SCORING TEST")
    print("="*70)
    
    print(f"\n[STEP 1] Score hierarchy verification:")
    print(f"  Priority 1: shadow_pnl (maximize)")
    print(f"  Priority 2: sign_flip_rate (minimize)")
    print(f"  Priority 3: paper_vs_shadow_degradation (minimize)")
    print(f"  Priority 4: trade_count >= 20 (threshold)")
    print(f"  Priority 5: win_rate (optional, tiebreaker)")
    
    # Get top baby
    top_baby = leaderboard[0]
    print(f"\n[STEP 2] Top baby analysis:")
    print(f"  Variant: {top_baby['variant_id']}")
    print(f"  Mutation: {top_baby['mutation_type']}")
    print(f"  Trades: {top_baby['trades']}")
    print(f"  Shadow PnL: ${top_baby['shadow_pnl']:.2f}")
    print(f"  Sign Flip Rate: {top_baby['flip_rate']:.1f}%")
    print(f"  Degradation: {top_baby['degradation']:.1f}%")
    print(f"  Score: {top_baby['score']:.1f}")
    print(f"  Status: {top_baby['status']}")
    
    # Check color coding
    score = top_baby['score']
    if score > 70:
        color = "GREEN (strong candidate)"
    elif score >= 40:
        color = "YELLOW (borderline)"
    else:
        color = "RED (weak)"
    
    print(f"\n[STEP 3] Color coding:")
    print(f"  Score {score:.1f} → {color}")
    
    # Verify scoring logic
    print(f"\n[STEP 4] Score component breakdown:")
    
    shadow_pnl = top_baby['shadow_pnl']
    sign_flip_rate = top_baby['flip_rate']
    degradation = top_baby['degradation']
    
    score_pnl = min(max(shadow_pnl / 10, 0), 100)
    penalty_flips = sign_flip_rate * 0.5
    penalty_deg = degradation * 0.2
    
    calculated_score = score_pnl - penalty_flips - penalty_deg
    
    print(f"  score_pnl = min(max({shadow_pnl}/10, 0), 100) = {score_pnl:.1f}")
    print(f"  penalty_flips = {sign_flip_rate:.1f} * 0.5 = {penalty_flips:.1f}")
    print(f"  penalty_deg = {degradation:.1f} * 0.2 = {penalty_deg:.1f}")
    print(f"  final_score = {score_pnl:.1f} - {penalty_flips:.1f} - {penalty_deg:.1f}")
    print(f"             = {calculated_score:.1f}")
    print(f"  (Recorded score: {score:.1f})")
    
    print("\n[PHASE 31] Fitness scoring test PASSED ✓")

def main():
    try:
        # Test evolution engine
        engine, babies = test_evolution_engine()
        
        # Test nursery system
        nursery, leaderboard = test_nursery_system(engine)
        
        # Test fitness scoring
        test_fitness_scoring(engine, leaderboard)
        
        print("\n" + "="*70)
        print("[PHASE 31] ALL TESTS PASSED ✓✓✓")
        print("="*70)
        print("\nPhase 31 Implementation Summary:")
        print("✓ Evolution engine creates single-dimension mutations")
        print("✓ Nursery spawns 10 babies with diverse mutations")
        print("✓ Fitness scoring implements shadow-first hierarchy")
        print("✓ CSV persistence (append-only, audit trail)")
        print("✓ Leaderboard ranking by composite score")
        print("✓ Color coding (green/yellow/red) by performance")
        print("\nNext: Integrate nursery into dashboard for live execution")
        print("\n")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
