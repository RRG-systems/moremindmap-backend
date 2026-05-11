#!/usr/bin/env python3
"""
Arena Integration Layer — Phase 2.5
Wires MOLTmarket Arena events into THINK Memory.

This module connects evolution_engine.py to the THINK event hooks.
Minimal, non-invasive: reads events from Arena, writes to THINK Memory.
"""

import sys
import sqlite3
from pathlib import Path
from datetime import datetime
from uuid import uuid4

# Enable SQLite thread safety
sqlite3.threadsafety = 3  # SERIALIZE mode - safe for multi-threaded access

# Import event hooks
sys.path.insert(0, str(Path(__file__).parent))
from event_hooks import THINKEventHook
from hypothesis_engine import HypothesisEngine


class ArenaEventBridge:
    """
    Bridge between MOLTmarket Arena and THINK Memory.
    Translates Arena events into THINK Memory records.
    """
    
    def __init__(self):
        """Initialize the bridge"""
        self.hook = None
        self.hyp_engine = None
        self.current_hypothesis_id = None
        self._mutations_in_flight = {}  # Track mutations being evaluated
    
    def connect(self):
        """Connect to THINK Memory"""
        # Note: THINKEventHook and HypothesisEngine already handle their own connections
        # with check_same_thread=False for thread safety
        self.hook = THINKEventHook()
        self.hook.connect()
        
        self.hyp_engine = HypothesisEngine()
        self.hyp_engine.connect()
        
        print("[ARENA] Connected to THINK Memory (thread-safe mode)")
    
    def close(self):
        """Close database connections"""
        if self.hook:
            self.hook.close()
        if self.hyp_engine:
            self.hyp_engine.close()
    
    # =====================================================
    # EVENT 1: Bot Spawned (from evolution_engine spawn_baby_variants)
    # =====================================================
    
    def on_baby_spawned(self, variant_id, mutated_dna, parent_variant_id, 
                       generation, hypothesis_id=None):
        """
        Hook: Baby variant spawned in evolution engine
        
        Called from evolution_engine.spawn_baby_variants()
        
        Args:
            variant_id: Baby variant ID (e.g., "baseline-01")
            mutated_dna: Baby's DNA dict
            parent_variant_id: Parent's variant ID
            generation: Generation number
            hypothesis_id: Optional hypothesis ID (if known)
        """
        if not self.hook:
            return
        
        # Use default hypothesis if not provided
        if not hypothesis_id:
            if not self.current_hypothesis_id:
                # Create default hypothesis on first spawn
                self.current_hypothesis_id = self.hyp_engine.create_hypothesis(
                    title="Mean Reversion (Production)",
                    description="Live production hypothesis for mean reversion trading",
                    target_market="BTC",
                    target_regime="ranging",
                    expected_behavior="Captures reversals within 5-10 minutes",
                    failure_modes=["Regime shift", "Execution slippage"]
                )
            hypothesis_id = self.current_hypothesis_id
        else:
            self.current_hypothesis_id = hypothesis_id
        
        # Determine creation source
        creation_source = 'manual' if parent_variant_id == 'baseline' else 'arena_mutation'
        
        # Call event hook
        self.hook.on_bot_spawned(
            bot_id=variant_id,
            hypothesis_id=hypothesis_id,
            creation_source=creation_source,
            dna_json=mutated_dna,
            parent_bot_id=parent_variant_id if parent_variant_id != 'baseline' else None,
            generation=generation,
            current_run_id='arena_live'
        )
        
        print(f"[ARENA→THINK] Baby spawned: {variant_id} (gen {generation})")
    
    # =====================================================
    # EVENT 2: Mutation Spawned (batch of babies from one mutation)
    # =====================================================
    
    def on_mutation_started(self, mutation_id, source_variant_id, baby_variant_ids,
                           mutation_dimension, parent_dna, mutated_dna_list,
                           hypothesis_id=None):
        """
        Hook: Mutation started (spawning babies)
        
        Called when evolution engine starts evaluating variants.
        
        Args:
            mutation_id: Unique mutation ID
            source_variant_id: Parent variant that was mutated
            baby_variant_ids: List of baby variant IDs
            mutation_dimension: Parameter mutated (e.g., 'entry_threshold')
            parent_dna: Parent's DNA
            mutated_dna_list: List of baby DNAs
            hypothesis_id: Optional hypothesis ID
        """
        if not self.hook:
            return
        
        if not hypothesis_id:
            hypothesis_id = self.current_hypothesis_id or 'default'
        
        # Classify mutation type from dimension
        mutation_type = self._classify_mutation_type(mutation_dimension)
        
        # Build parameter changes
        param_changes = {}
        if mutated_dna_list and len(mutated_dna_list) > 0:
            baby_dna = mutated_dna_list[0]
            if mutation_dimension in baby_dna and mutation_dimension in parent_dna:
                param_changes[mutation_dimension] = {
                    'before': parent_dna[mutation_dimension],
                    'after': baby_dna[mutation_dimension]
                }
        
        # Diagnose: what problem are we trying to fix?
        diagnosis = self._diagnose_from_dimension(mutation_dimension)
        
        # Store mutation for later result classification
        self._mutations_in_flight[mutation_id] = {
            'source_variant_id': source_variant_id,
            'baby_variant_ids': baby_variant_ids,
            'hypothesis_id': hypothesis_id,
            'mutation_dimension': mutation_dimension
        }
        
        # Call event hook
        self.hook.on_mutation_spawned(
            mutation_id=mutation_id,
            source_bot_id=source_variant_id,
            resulting_bot_ids=baby_variant_ids,
            hypothesis_id=hypothesis_id,
            diagnosis=diagnosis,
            mutation_type=mutation_type,
            parameter_changes=param_changes,
            rationale=f"Testing {mutation_dimension} adjustment",
            expected_effect=f"Improve performance by adjusting {mutation_dimension}"
        )
        
        print(f"[ARENA→THINK] Mutation started: {mutation_id}")
        print(f"  Source: {source_variant_id}")
        print(f"  Babies: {len(baby_variant_ids)}")
        print(f"  Type: {mutation_type} ({mutation_dimension})")
    
    # =====================================================
    # EVENT 3: Evaluation Complete
    # =====================================================
    
    def on_variant_evaluated(self, variant_id, trades, flip_rate, pnl, divergence,
                            drawdown, survival, trajectory=None):
        """
        Hook: Baby variant evaluated
        
        Called after evaluation runs on a variant.
        
        Args:
            variant_id: The variant that was evaluated
            trades: Number of trades
            flip_rate: Flip rate (0-1)
            pnl: Shadow PnL
            divergence: Divergence metric
            drawdown: Max drawdown
            survival: Survival rate (0-1)
            trajectory: Trajectory status ('improving', 'stable', 'degrading')
        """
        if not self.hook:
            return
        
        metrics = {
            'trades': trades,
            'flip_rate': flip_rate,
            'shadow_pnl': pnl,
            'divergence': divergence,
            'drawdown': drawdown,
            'survival': survival,
            'trajectory': trajectory or 'unknown',
            'control_action': None
        }
        
        self.hook.on_evaluation_complete(variant_id, metrics)
        
        print(f"[ARENA→THINK] Evaluation complete: {variant_id}")
        print(f"  Flip rate: {flip_rate:.2%}, PnL: +{pnl*100:.2f}%, Survival: {survival:.0%}")
    
    # =====================================================
    # EVENT 4: Mutation Result Classification
    # =====================================================
    
    def classify_mutation_result(self, mutation_id, parent_score, best_baby_score):
        """
        Hook: Classify mutation result after babies are evaluated
        
        Args:
            mutation_id: The mutation ID
            parent_score: Parent variant's score
            best_baby_score: Best baby's score
        """
        if not self.hook or mutation_id not in self._mutations_in_flight:
            return
        
        # Determine result
        if best_baby_score > parent_score * 1.05:  # 5% improvement threshold
            result = 'helped'
            result_summary = f"Best baby improved over parent by {(best_baby_score/parent_score - 1)*100:.1f}%"
        elif best_baby_score < parent_score * 0.95:  # 5% degradation threshold
            result = 'hurt'
            result_summary = f"Best baby degraded {(1 - best_baby_score/parent_score)*100:.1f}% vs parent"
        else:
            result = 'inconclusive'
            result_summary = "Results within margin of error. Continue testing."
        
        # Call hook
        self.hook.on_mutation_result_classified(
            mutation_id=mutation_id,
            result=result,
            result_summary=result_summary
        )
        
        # Clean up
        del self._mutations_in_flight[mutation_id]
        
        print(f"[ARENA→THINK] Mutation classified: {mutation_id}")
        print(f"  Result: {result}")
        print(f"  Summary: {result_summary}")
    
    # =====================================================
    # EVENT 5: Promotion/Kill Decision
    # =====================================================
    
    def on_variant_promoted(self, variant_id, hypothesis_id, trades, flip_rate, pnl,
                           reason="User promoted variant"):
        """
        Hook: Variant promoted to production
        
        Args:
            variant_id: The variant being promoted
            hypothesis_id: Its hypothesis
            trades: Trade count
            flip_rate: Flip rate
            pnl: PnL
            reason: Why it was promoted
        """
        if not self.hook:
            return
        
        context = {
            'trades': trades,
            'flip_rate': flip_rate,
            'shadow_pnl': pnl
        }
        
        self.hook.on_bot_promoted(
            bot_id=variant_id,
            hypothesis_id=hypothesis_id,
            reason=reason,
            context_snapshot=context
        )
        
        print(f"[ARENA→THINK] Variant promoted: {variant_id}")
        print(f"  Reason: {reason}")
    
    def on_variant_killed(self, variant_id, hypothesis_id, reason="Variant retired"):
        """
        Hook: Variant killed/retired
        
        Args:
            variant_id: The variant being killed
            hypothesis_id: Its hypothesis
            reason: Why it was killed
        """
        if not self.hook:
            return
        
        self.hook.on_bot_killed(
            bot_id=variant_id,
            hypothesis_id=hypothesis_id,
            reason=reason,
            context_snapshot={}
        )
        
        print(f"[ARENA→THINK] Variant killed: {variant_id}")
        print(f"  Reason: {reason}")
    
    # =====================================================
    # HELPERS
    # =====================================================
    
    def _classify_mutation_type(self, mutation_dimension):
        """Map mutation dimension to THINK mutation type"""
        mapping = {
            'entry_threshold': 'entry',
            'exit_threshold': 'exit',
            'holding_time': 'hold',
            'selectivity_percentile': 'selectivity',
            'trade_size': 'size',
            'max_open_positions': 'concentration',
            'stop_loss_sensitivity': 'exit',
            'target_profit_sensitivity': 'exit',
            'pressure_level': 'selectivity',
            'confirmation_ticks': 'entry',
        }
        return mapping.get(mutation_dimension, 'entry')
    
    def _diagnose_from_dimension(self, mutation_dimension):
        """Diagnose what problem we're trying to fix"""
        if 'entry' in mutation_dimension.lower():
            return "optimize entry sensitivity"
        elif 'exit' in mutation_dimension.lower():
            return "optimize exit behavior"
        elif 'holding' in mutation_dimension.lower() or 'time' in mutation_dimension.lower():
            return "optimize holding duration"
        elif 'selectivity' in mutation_dimension.lower() or 'pressure' in mutation_dimension.lower():
            return "reduce entry frequency"
        elif 'size' in mutation_dimension.lower():
            return "optimize position sizing"
        elif 'concentration' in mutation_dimension.lower() or 'open' in mutation_dimension.lower():
            return "optimize position concentration"
        else:
            return f"test {mutation_dimension}"


# =====================================================
# GLOBAL BRIDGE INSTANCE
# =====================================================

_arena_bridge = None


def init_arena_bridge():
    """Initialize the global arena bridge"""
    global _arena_bridge
    _arena_bridge = ArenaEventBridge()
    _arena_bridge.connect()
    return _arena_bridge


def get_arena_bridge():
    """Get the global arena bridge"""
    global _arena_bridge
    if not _arena_bridge:
        _arena_bridge = init_arena_bridge()
    return _arena_bridge


def close_arena_bridge():
    """Close the global arena bridge"""
    global _arena_bridge
    if _arena_bridge:
        _arena_bridge.close()
        _arena_bridge = None
