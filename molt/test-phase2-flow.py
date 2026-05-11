#!/usr/bin/env python3
"""
Test Script: Phase 2 Complete Flow
Demonstrates: Hypothesis → Bot → Mutation → Evaluation → Decision

This test validates that THINK Memory correctly captures system state.
"""

import json
import sqlite3
from pathlib import Path
from hypothesis_engine import HypothesisEngine, HypothesisValidator
from event_hooks import THINKEventHook


def setup_database():
    """Initialize THINK Memory database"""
    db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
    schema_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory-schema.sql'
    
    print("=" * 60)
    print("SETUP: Initializing THINK Memory Database")
    print("=" * 60)
    
    # Check if schema file exists
    if not schema_path.exists():
        print(f"ERROR: Schema file not found at {schema_path}")
        print("Run: node ~/.openclaw/workspace/molt/init-think-memory.js")
        return False
    
    # Remove old database if it exists
    if db_path.exists():
        print(f"Removing old database: {db_path}")
        db_path.unlink()
    
    # Create new database and run schema
    conn = sqlite3.connect(str(db_path))
    with open(schema_path, 'r') as f:
        schema = f.read()
    conn.executescript(schema)
    conn.commit()
    conn.close()
    
    print(f"✓ Database initialized: {db_path}")
    return True


def test_phase2_flow():
    """Test complete Phase 2 flow"""
    
    if not setup_database():
        return False
    
    print("\n" + "=" * 60)
    print("PHASE 2 TEST: Hypothesis → Bot → Mutation → Evaluation → Decision")
    print("=" * 60)
    
    # Connect to database
    hyp_engine = HypothesisEngine()
    hyp_engine.connect()
    
    hook = THINKEventHook()
    hook.connect()
    
    try:
        # =====================================================
        # STEP 1: Create Hypothesis
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 1: Create Hypothesis")
        print("-" * 60)
        
        hypothesis_id = hyp_engine.create_hypothesis(
            title="Mean Reversion (Low Vol)",
            description="Price reversals exist in low volatility regimes within 5-10 minutes",
            target_market="BTC",
            target_regime="low_vol",
            expected_behavior="Quick reversal captures on -2% to -5% moves",
            failure_modes=[
                "Regime shift to trending market",
                "Execution drag kills signal",
                "Entry threshold misaligned"
            ]
        )
        
        # Verify hypothesis was created
        hyp = hyp_engine.get_hypothesis(hypothesis_id)
        assert hyp is not None, "Hypothesis not found in database"
        assert hyp['status'] == 'testing', "Hypothesis should be in testing status"
        print(f"✓ Hypothesis created and verified")
        print(f"  ID: {hypothesis_id}")
        print(f"  Status: {hyp['status']}")
        
        # =====================================================
        # STEP 2: Spawn Initial Bot
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 2: Spawn Initial Bot (Manual Creation)")
        print("-" * 60)
        
        bot_id_v1 = "bot_meanrev_v1"
        bot_dna_v1 = {
            'entry_threshold': 0.025,      # -2.5% deviation
            'exit_threshold': 0.015,       # +1.5% profit target
            'hold_time': 300,              # 5 minutes
            'selectivity': 0.8,            # 80% selectivity
            'trade_size': 100,             # $100 per trade
            'max_open_positions': 3        # Max 3 open
        }
        
        hook.on_bot_spawned(
            bot_id=bot_id_v1,
            hypothesis_id=hypothesis_id,
            creation_source='manual',
            dna_json=bot_dna_v1,
            parent_bot_id=None,
            generation=1,
            current_run_id='arena_001'
        )
        
        # Query back the bot
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM bots WHERE bot_id = ?", [bot_id_v1])
        bot_row = cursor.fetchone()
        assert bot_row is not None, "Bot not found"
        assert bot_row['hypothesis_id'] == hypothesis_id, "Bot not linked to hypothesis"
        print(f"✓ Bot spawned and verified")
        print(f"  ID: {bot_id_v1}")
        print(f"  Hypothesis: {bot_row['hypothesis_id']}")
        print(f"  DNA: {json.loads(bot_row['dna_json'])}")
        conn.close()
        
        # =====================================================
        # STEP 3: Evaluate Bot
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 3: Evaluate Bot (Get Metrics)")
        print("-" * 60)
        
        metrics_v1 = {
            'trades': 42,
            'flip_rate': 0.18,             # 18% flip rate (high)
            'shadow_pnl': 0.032,           # +3.2%
            'divergence': 0.045,
            'drawdown': 0.08,              # 8% max drawdown
            'survival': 0.95,
            'trajectory': 'stable',
            'control_action': None
        }
        
        hook.on_evaluation_complete(bot_id_v1, metrics_v1)
        
        # Verify metrics were stored
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT latest_metrics_json FROM bots WHERE bot_id = ?", [bot_id_v1])
        row = cursor.fetchone()
        stored_metrics = json.loads(row['latest_metrics_json'])
        assert stored_metrics['flip_rate'] == 0.18, "Metrics not stored correctly"
        print(f"✓ Bot evaluation stored")
        print(f"  Flip Rate: {stored_metrics['flip_rate']} (HIGH - needs mutation)")
        print(f"  PnL: +{stored_metrics['shadow_pnl']*100:.1f}%")
        conn.close()
        
        # =====================================================
        # STEP 4: Spawn Mutation (Diagnose Problem)
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 4: Diagnose Problem & Spawn Mutation")
        print("-" * 60)
        
        diagnosis = "high flip rate"
        mutation_type = "selectivity"
        
        print(f"Diagnosis: {diagnosis}")
        print(f"Mutation Type: {mutation_type}")
        print(f"Rationale: Reduce entry frequency to lower whipsaw trades")
        
        # Create 11 baby bot IDs (1 canonical + 10 variants)
        baby_ids = [
            f"bot_meanrev_v2_canonical",
            f"bot_meanrev_v2_var01",
            f"bot_meanrev_v2_var02",
            f"bot_meanrev_v2_var03",
            f"bot_meanrev_v2_var04",
            f"bot_meanrev_v2_var05",
            f"bot_meanrev_v2_var06",
            f"bot_meanrev_v2_var07",
            f"bot_meanrev_v2_var08",
            f"bot_meanrev_v2_var09",
            f"bot_meanrev_v2_var10",
        ]
        
        mutation_id = "mut_001"
        parameter_changes = {
            'selectivity': {
                'before': 0.8,
                'after': 0.6
            }
        }
        
        # First create baby bot records (they start with no metrics)
        bot_dna_v2 = {
            'entry_threshold': 0.025,
            'exit_threshold': 0.015,
            'hold_time': 300,
            'selectivity': 0.6,  # MUTATED from 0.8
            'trade_size': 100,
            'max_open_positions': 3
        }
        
        for idx, baby_id in enumerate(baby_ids):
            hook.on_bot_spawned(
                bot_id=baby_id,
                hypothesis_id=hypothesis_id,
                creation_source='rocky_proposal',
                dna_json=bot_dna_v2,
                parent_bot_id=bot_id_v1,
                generation=2,
                current_run_id='arena_001'
            )
        
        hook.on_mutation_spawned(
            mutation_id=mutation_id,
            source_bot_id=bot_id_v1,
            resulting_bot_ids=baby_ids,
            hypothesis_id=hypothesis_id,
            diagnosis=diagnosis,
            mutation_type=mutation_type,
            parameter_changes=parameter_changes,
            rationale="Tighter selectivity should reduce false entries",
            expected_effect="Lower flip rate",
            source_proposal_id=None
        )
        
        # Verify mutation and baby bots
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM mutations WHERE mutation_id = ?", [mutation_id])
        mut_row = cursor.fetchone()
        assert mut_row is not None, "Mutation not found"
        resulting_ids = json.loads(mut_row['resulting_bot_ids'])
        assert len(resulting_ids) == 11, f"Expected 11 babies, got {len(resulting_ids)}"
        
        cursor.execute("SELECT COUNT(*) as cnt FROM bots WHERE created_by_mutation_id = ?", [mutation_id])
        baby_count = cursor.fetchone()['cnt']
        assert baby_count == 11, f"Expected 11 babies in bots table, got {baby_count}"
        
        print(f"✓ Mutation recorded")
        print(f"  Mutation ID: {mutation_id}")
        print(f"  Babies created: {len(resulting_ids)}")
        print(f"  Parameter changes: {parameter_changes}")
        conn.close()
        
        # =====================================================
        # STEP 5: Evaluate Best Baby
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 5: Evaluate Best Baby (Canonical)")
        print("-" * 60)
        
        canonical_bot_id = baby_ids[0]
        
        metrics_v2_canonical = {
            'trades': 45,
            'flip_rate': 0.12,             # IMPROVED from 0.18
            'shadow_pnl': 0.045,           # Better returns
            'divergence': 0.038,           # Better divergence
            'drawdown': 0.075,             # Better drawdown
            'survival': 0.96,              # Better survival
            'trajectory': 'improving',
            'control_action': None
        }
        
        hook.on_evaluation_complete(canonical_bot_id, metrics_v2_canonical)
        
        print(f"✓ Canonical baby evaluated")
        print(f"  Flip Rate: {metrics_v2_canonical['flip_rate']} (DOWN from 0.18 ✓)")
        print(f"  PnL: +{metrics_v2_canonical['shadow_pnl']*100:.1f}%")
        
        # =====================================================
        # STEP 6: Classify Mutation Result
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 6: Classify Mutation Result")
        print("-" * 60)
        
        hook.on_mutation_result_classified(
            mutation_id=mutation_id,
            result='helped',
            result_summary='Selectivity tightening reduced flip rate from 18% to 12%. Mutation successful.'
        )
        
        # Verify result was stored
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT result, result_summary FROM mutations WHERE mutation_id = ?", [mutation_id])
        row = cursor.fetchone()
        assert row['result'] == 'helped', "Result not stored"
        print(f"✓ Mutation result classified")
        print(f"  Result: {row['result']}")
        print(f"  Summary: {row['result_summary']}")
        conn.close()
        
        # =====================================================
        # STEP 7: Promote Bot Decision
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 7: User Approves Promotion")
        print("-" * 60)
        
        decision_id = hook.on_bot_promoted(
            bot_id=canonical_bot_id,
            hypothesis_id=hypothesis_id,
            reason="Mutation helped. Flip rate improved. Ready for capital allocation.",
            context_snapshot=metrics_v2_canonical
        )
        
        # Verify decision
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM decisions WHERE decision_id = ?", [decision_id])
        dec_row = cursor.fetchone()
        assert dec_row is not None, "Decision not found"
        assert dec_row['decision_type'] == 'promote_bot', "Wrong decision type"
        
        cursor.execute("SELECT current_status FROM bots WHERE bot_id = ?", [canonical_bot_id])
        bot_status = cursor.fetchone()['current_status']
        assert bot_status == 'promoted', f"Bot status should be promoted, got {bot_status}"
        
        print(f"✓ Promotion decision recorded")
        print(f"  Decision ID: {decision_id}")
        print(f"  Bot Status: {bot_status}")
        conn.close()
        
        # =====================================================
        # STEP 8: Verify Rocky Can Query Everything
        # =====================================================
        
        print("\n" + "-" * 60)
        print("STEP 8: Verify Rocky's 5 Core Queries Work")
        print("-" * 60)
        
        conn = sqlite3.connect(str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query 1: Why does this bot exist?
        cursor.execute("SELECT * FROM bots WHERE bot_id = ?", [canonical_bot_id])
        bot = dict(cursor.fetchone())
        cursor.execute("SELECT * FROM mutations WHERE mutation_id = ?", [bot['created_by_mutation_id']])
        mut = dict(cursor.fetchone())
        
        print(f"\n1. Why does {canonical_bot_id} exist?")
        print(f"   - Parent: {bot['parent_bot_id']}")
        print(f"   - Generation: {bot['generation']}")
        print(f"   - Created by mutation: {mut['mutation_id']}")
        print(f"   - Diagnosis: {mut['diagnosis']}")
        print(f"   - Rationale: {mut['rationale']}")
        
        # Query 2: What has been tried on this hypothesis?
        cursor.execute("""
            SELECT mutation_type, result, COUNT(*) as count
            FROM mutations
            WHERE hypothesis_id = ?
            GROUP BY mutation_type, result
        """, [hypothesis_id])
        results = cursor.fetchall()
        
        print(f"\n2. What has been tried on hypothesis {hypothesis_id}?")
        for row in results:
            print(f"   - {row['mutation_type']}: {row['result']} ({row['count']})")
        
        # Query 3: Is this problem new or repeated?
        cursor.execute("""
            SELECT * FROM mutations
            WHERE diagnosis = ?
            ORDER BY created_at DESC
        """, ['high flip rate'])
        similar = cursor.fetchall()
        
        print(f"\n3. Has 'high flip rate' been tried before?")
        print(f"   - Found {len(similar)} prior attempt(s)")
        
        # Query 4: Has this hypothesis ever worked?
        cursor.execute("""
            SELECT COUNT(*) as total_bots,
                   SUM(CASE WHEN current_status = 'promoted' THEN 1 ELSE 0 END) as promoted_count
            FROM bots
            WHERE hypothesis_id = ?
        """, [hypothesis_id])
        hyp_summary = dict(cursor.fetchone())
        
        print(f"\n4. Has hypothesis {hypothesis_id} ever worked?")
        print(f"   - Total bots: {hyp_summary['total_bots']}")
        print(f"   - Promoted: {hyp_summary['promoted_count']}")
        
        # Query 5: Why promote/kill?
        cursor.execute("""
            SELECT * FROM decisions
            WHERE related_bot_id = ?
            ORDER BY timestamp DESC
        """, [canonical_bot_id])
        decisions = cursor.fetchall()
        
        print(f"\n5. Why promote/kill {canonical_bot_id}?")
        for dec in decisions:
            print(f"   - {dec['decision_type']}: {dec['reason']}")
        
        conn.close()
        
        # =====================================================
        # SUCCESS
        # =====================================================
        
        print("\n" + "=" * 60)
        print("✓ PHASE 2 COMPLETE: All tests passed")
        print("=" * 60)
        print("\nWhat was tested:")
        print("  1. Hypothesis creation and storage")
        print("  2. Bot spawning linked to hypothesis")
        print("  3. Metrics evaluation snapshot")
        print("  4. Mutation spawning (1 parent → 11 babies)")
        print("  5. Mutation result classification")
        print("  6. Decision recording (approve/promote)")
        print("  7. Rocky's 5 core queries all functional")
        print("\nNext steps:")
        print("  - Wire event hooks into Arena code")
        print("  - Build MOLT feed with seed agents")
        print("  - Build 3-window UI refactor")
        
        return True
        
    finally:
        hyp_engine.close()
        hook.close()


if __name__ == '__main__':
    import sys
    try:
        success = test_phase2_flow()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
