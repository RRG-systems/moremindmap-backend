#!/usr/bin/env python3
"""
PHASE 32.3: Evolution Engine with UNIFIED PARENT STATE
Spawns, mutates, and scores baby strategies using existing Mean Reversion framework

CRITICAL PHASE 32.3 CHANGES:
1. UNIFIED PARENT STATE: self.current_parent is single source of truth
2. PROMOTION WRITES: update self.current_parent directly (not just dashboard_state)
3. SPAWN READS: always use self.current_parent (never baseline unless it's the current_parent)
4. LINEAGE NAMING: children encode parent ID (baby005-01, baby005-02, etc.)
5. GENERATION TRACKING: each child's generation = parent_generation + 1
6. ARENA DNA: promoted baby's config becomes new current_parent
"""

import random
import json
from copy import deepcopy
from datetime import datetime
from uuid import uuid4


class EvolutionEngine:
    """
    Central evolution system for MOLTmarket strategies.
    Uses EXISTING execution layers (paper/shadow) for variant evaluation.
    
    PHASE 32.3: UNIFIED PARENT STATE
    Single source of truth for current parent strategy used by:
    1. spawn_baby_variants() - inherits from this
    2. promotion writes - updates this
    3. CSV logging - reads parent_id from this
    4. active strategy display - shows this
    5. arena config - runs with this config
    """
    
    def __init__(self):
        """Initialize evolution engine with default Mean Reversion parent"""
        # PHASE 32.3: AUTHORITATIVE parent strategy (single source of truth)
        # Updated only when a baby is promoted to main arena
        self.current_parent = self._create_default_parent()
        
        # Keep legacy reference for compatibility
        self.parent_strategy = self.current_parent
        
        self.babies = []
        self.execution_states = {}
        self.fitness_scores = {}
        
        # THINK Memory integration (Phase 2.6)
        self.arena_bridge = None
        
        # Load babies from database on startup
        self.hydrate_from_database()
        try:
            import sys
            from pathlib import Path
            molt_path = str(Path.home() / '.openclaw' / 'workspace' / 'molt')
            if molt_path not in sys.path:
                sys.path.insert(0, molt_path)
            from arena_integration import init_arena_bridge
            self.arena_bridge = init_arena_bridge()
            print("[ARENA] THINK Memory bridge initialized")
        except Exception as e:
            print(f"[ARENA] THINK Memory bridge unavailable: {type(e).__name__}: {e}")
    
    def _create_default_parent(self):
        """
        Create default parent strategy: Mean Reversion (20-tick, 0.3% deviation)
        This is the PHASE 28 locked-in strategy
        """
        return {
            'id': 'baseline',
            'name': 'Baseline Mean Reversion',
            'signal_type': 'mean_reversion',
            'parameters': {
                'entry_threshold': 0.003,           # 0.3% deviation
                'exit_threshold': 0.002,            # 0.2% profit target
                'holding_time': 300,                # 5 minutes (300 seconds)
                'confirmation_ticks': 1,           # Require 1 tick confirmation
                'stop_loss_sensitivity': 1.0,       # 1x stop loss multiplier
                'target_profit_sensitivity': 1.0,  # 1x target profit multiplier
            },
            'generation': 0,
            'created_timestamp': datetime.utcnow().isoformat(),
        }
    
    
    def hydrate_from_database(self):
        """
        Restore babies and execution state from database
        Called on startup to rebuild runtime from persistent storage
        """
        import sqlite3
        from pathlib import Path
        
        db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
        
        if not db_path.exists():
            print("[EVOLUTION HYDRATE] No database found — starting fresh")
            return
        
        try:
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Fetch all active bot records
            cursor.execute("""
                SELECT bot_id, parent_bot_id, generation, mutation_type, 
                       dna_json, hypothesis_id, created_at, current_status
                FROM bots 
                WHERE current_status = 'active'
                ORDER BY created_at DESC
            """)
            
            bot_records = cursor.fetchall()
            
            self.babies = []
            for record in bot_records:
                try:
                    # Parse DNA (parameters)
                    dna = json.loads(record['dna_json'] or '{}')
                    
                    # Reconstruct baby dict from database
                    baby = {
                        'variant_id': record['bot_id'],
                        'id': record['bot_id'],
                        'parent_id': record['parent_bot_id'],
                        'generation': record['generation'] or 0,
                        'mutation_type': record['mutation_type'] or 'NONE',
                        'parameters': dna,
                        'hypothesis_id': record['hypothesis_id'],
                        'created_at': record['created_at'],
                        'status': record['current_status'],
                        'total_trades': 0,
                        'shadow_pnl': 0.0,
                        'paper_pnl': 0.0,
                        'win_rate': 0.0,
                        'flip_rate': 0.0,
                        'degradation_pct': 0.0,
                        'score': 0.0,
                    }
                    
                    self.babies.append(baby)
                    
                    # Initialize execution state
                    self.execution_states[record['bot_id']] = {
                        'paper_equity': [],
                        'shadow_equity': [],
                        'trades': [],
                        'paper_pnl': 0.0,
                        'shadow_pnl': 0.0,
                        'paper_trade_count': 0,
                        'shadow_trade_count': 0,
                    }
                except Exception as item_error:
                    print(f"[EVOLUTION HYDRATE] Skipping bot {record.get('bot_id', '?')}: {item_error}")
                    continue
            
            conn.close()
            
            if self.babies:
                baby_ids = [b['variant_id'] for b in self.babies[:3]]
                print(f"[EVOLUTION HYDRATE] Loaded {len(self.babies)} babies from database: {baby_ids}...")
            else:
                print(f"[EVOLUTION HYDRATE] No active babies found in database")
            
        except Exception as e:
            print(f"[EVOLUTION HYDRATE] CRITICAL ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.babies = []
            for record in bot_records:
                # Reconstruct baby dict from database
                baby = {
                    'variant_id': record['bot_id'],
                    'parent_id': record['parent_bot_id'],
                    'generation': record['generation'],
                    'mutation_type': record['mutation_type'],
                    'parameters': json.loads(record['parameters'] or '{}'),
                    'hypothesis_id': record['hypothesis_id'],
                    'created_at': record['created_at'],
                }
                
                self.babies.append(baby)
                
                # Initialize execution state
                self.execution_states[record['bot_id']] = {
                    'paper_equity': [],
                    'shadow_equity': [],
                    'trades': [],
                    'paper_pnl': 0.0,
                    'shadow_pnl': 0.0,
                    'paper_trade_count': 0,
                    'shadow_trade_count': 0,
                }
            
            conn.close()
            
            print(f"[EVOLUTION HYDRATE] Loaded {len(self.babies)} babies from database")
            
        except Exception as e:
            print(f"[EVOLUTION HYDRATE] ERROR: {e}")
            import traceback
            traceback.print_exc()
            self.babies = []

    def promote_baby_to_parent(self, baby_variant):
        """
        PHASE 32.3: CRITICAL FIX - Update authoritative parent when baby is promoted
        
        This is called during promotion flow to make a baby the new parent.
        ONLY SOURCE that updates current_parent.
        
        baby_variant: Full baby strategy dict to promote
        """
        print(f"[EVOLUTION] Promoting {baby_variant['variant_id']} to parent (Gen {baby_variant['generation']})")
        
        # Create promoted parent from baby
        promoted_parent = deepcopy(baby_variant)
        
        # Update metadata
        promoted_parent['id'] = baby_variant['variant_id']  # baby_005 becomes the parent id
        promoted_parent['promoted_from'] = 'nursery'
        promoted_parent['promoted_at'] = datetime.utcnow().isoformat()
        
        # Increment generation for next children
        promoted_parent['generation'] = baby_variant['generation']  # Keep this generation
        
        # Store previous parent for reference
        promoted_parent['previous_parent'] = self.current_parent
        
        # UPDATE AUTHORITATIVE PARENT (single source of truth)
        self.current_parent = promoted_parent
        self.parent_strategy = promoted_parent  # Keep legacy reference in sync
        
        print(f"[EVOLUTION] Parent updated: {promoted_parent['id']} • Gen {promoted_parent['generation']}")
        return promoted_parent
    
    def reset_to_baseline(self):
        """
        PHASE 32.3: Reset parent strategy to baseline
        Preserves equity/P&L but resets strategy to original
        """
        print("[EVOLUTION] Resetting parent to baseline")
        self.current_parent = self._create_default_parent()
        self.parent_strategy = self.current_parent
        print("[EVOLUTION] Parent reset to baseline • Gen 0")
        return self.current_parent
    
    def get_current_parent(self):
        """Get the authoritative current parent strategy"""
        return self.current_parent
    
    def mutate_one_dimension(self, variant, dimension, intensity=0.05):
        """
        CRITICAL: Use EXISTING mutation logic (do NOT create new framework)
        
        Mutate a SINGLE dimension of a strategy by intensity amount.
        Intensity = 0.05 means 5% adjustment.
        
        Supported dimensions:
        1. entry_threshold
        2. exit_threshold
        3. holding_time
        4. confirmation_rules (confirmation_ticks)
        5. stop_loss_sensitivity
        6. target_profit_sensitivity
        """
        mutated = deepcopy(variant)
        params = mutated['parameters']
        
        if dimension == 'entry_threshold':
            # Adjust by ±5-10% of current value
            adjustment = params['entry_threshold'] * intensity * random.choice([-1, 1])
            params['entry_threshold'] = max(0.001, params['entry_threshold'] + adjustment)
            
        elif dimension == 'exit_threshold':
            # Adjust by ±5-10%
            adjustment = params['exit_threshold'] * intensity * random.choice([-1, 1])
            params['exit_threshold'] = max(0.001, params['exit_threshold'] + adjustment)
            
        elif dimension == 'holding_time':
            # Adjust by ±10-20% (in seconds)
            adjustment = params['holding_time'] * intensity * random.choice([-1, 1])
            params['holding_time'] = max(60, int(params['holding_time'] + adjustment))
            
        elif dimension == 'confirmation_rules':
            # Toggle confirmation_ticks: 0 or 1
            params['confirmation_ticks'] = 1 - params['confirmation_ticks']
            
        elif dimension == 'stop_loss_sensitivity':
            # Adjust by ±5%
            adjustment = params['stop_loss_sensitivity'] * intensity * random.choice([-1, 1])
            params['stop_loss_sensitivity'] = max(0.5, params['stop_loss_sensitivity'] + adjustment)
            
        elif dimension == 'target_profit_sensitivity':
            # Adjust by ±5%
            adjustment = params['target_profit_sensitivity'] * intensity * random.choice([-1, 1])
            params['target_profit_sensitivity'] = max(0.5, params['target_profit_sensitivity'] + adjustment)
        
        return mutated
    
    def spawn_baby_variants(self, parent_strategy=None, count=10):
        """
        Spawn N baby variants from AUTHORITATIVE current parent strategy.
        Each baby mutates a SINGLE dimension.
        
        PHASE 32.3 FIX:
        - Always use self.current_parent (single source of truth)
        - Ignore parent_strategy parameter (for backwards compatibility only)
        - Generate lineage-aware names: children encode parent ID
        - Pass through true parent generation
        - Children generation = parent generation + 1
        
        Returns list of baby strategies ready for execution.
        """
        # PHASE 32.3: CRITICAL - use authoritative current parent, NEVER override
        parent_strategy = self.current_parent
        
        print(f"[EVOLUTION] Spawning {count} babies from parent: {parent_strategy['id']} (Gen {parent_strategy.get('generation', 0)})")
        
        self.babies = []
        
        mutation_dimensions = [
            'entry_threshold',
            'exit_threshold',
            'holding_time',
            'confirmation_rules',
            'stop_loss_sensitivity',
            'target_profit_sensitivity',
        ]
        
        # Get parent metadata for lineage naming
        parent_id = parent_strategy['id']
        parent_gen = parent_strategy.get('generation', 0)
        child_gen = parent_gen + 1
        
        # Extract parent short name for lineage naming
        # baseline → baseline
        # baby_005 → baby005 (remove underscores)
        # gen2_baby_001 → gen2baby001 (remove underscores/dashes)
        if parent_id == 'baseline':
            parent_short = 'baseline'
        else:
            parent_short = parent_id.replace('_', '').replace('-', '')
        
        for i in range(count):
            # Create baby by copying parent
            baby = deepcopy(parent_strategy)
            
            # CRITICAL: First baby (i=0) is CANONICAL (no mutation)
            # Babies 1-10 have mutations
            if i == 0:
                mutation_dim = 'NONE'  # Canonical form
                mutated_baby = baby  # No mutation applied
            else:
                # Select mutation dimension (cycle through mutations for i=1..count)
                mutation_dim = mutation_dimensions[(i-1) % len(mutation_dimensions)]
                
                # Apply SINGLE mutation using existing engine
                mutated_baby = self.mutate_one_dimension(
                    variant=baby,
                    dimension=mutation_dim,
                    intensity=0.05  # 5% controlled mutation
                )
            
            # PHASE 4.5: Globally unique ID (no collision risk)
            # Format: parent-short_mutation-dim_uuid-timestamp
            # Example: baseline_entry_threshold_a1b2c3d4_1713612000
            unique_suffix = str(uuid4())[:8]
            timestamp = int(datetime.utcnow().timestamp())
            variant_id = f"{parent_short}_{mutation_dim}_{unique_suffix}_{timestamp}"
            
            # Add baby metadata
            mutated_baby['variant_id'] = variant_id
            mutated_baby['parent_id'] = parent_id  # True parent (baseline or promoted baby)
            mutated_baby['parent_generation'] = parent_gen  # True parent's generation
            mutated_baby['mutation_type'] = mutation_dim
            mutated_baby['generation'] = child_gen  # Child generation = parent_gen + 1
            mutated_baby['created_timestamp'] = datetime.utcnow().isoformat()
            
            # Initialize execution state
            self.execution_states[mutated_baby['variant_id']] = {
                'paper_equity': [],
                'shadow_equity': [],
                'trades': [],
                'paper_pnl': 0.0,
                'shadow_pnl': 0.0,
                'paper_trade_count': 0,
                'shadow_trade_count': 0,
            }
            
            self.babies.append(mutated_baby)
            
            # MOLT hooks disabled - skip for now
            print(f"  ✓ {variant_id} (Gen {child_gen}): mutate {mutation_dim}")
        
        print(f"[EVOLUTION] {len(self.babies)} babies spawned")
        return self.babies
            #     
            #     def record_baby_execution(self, variant_id, source, trade_data):
            #         """
            #         Record execution result for a baby variant.
            #         
            #         source: 'paper' or 'shadow'
            #         trade_data: dict with trade metrics
            #         """
            #         if variant_id not in self.execution_states:
            #             self.execution_states[variant_id] = {
            #                 'paper_equity': [],
            #                 'shadow_equity': [],
            #                 'trades': [],
            #                 'paper_pnl': 0.0,
            #                 'shadow_pnl': 0.0,
            #                 'paper_trade_count': 0,
            #                 'shadow_trade_count': 0,
            #             }
            #         
            #         state = self.execution_states[variant_id]
            #         
            #         if source == 'paper':
            #             state['paper_equity'].append(trade_data.get('equity_value', 0))
            #             state['paper_pnl'] += float(trade_data.get('pnl', 0))
            #             state['paper_trade_count'] += 1
            #             state['trades'].append({'source': 'paper', **trade_data})
            #             
            #         elif source == 'shadow':
            #             state['shadow_equity'].append(trade_data.get('equity_value', 0))
            #             state['shadow_pnl'] += float(trade_data.get('pnl', 0))
            #             state['shadow_trade_count'] += 1
            #             state['trades'].append({'source': 'shadow', **trade_data})
            #     
            #     def score_variant(self, variant_id):
            #         """
            #         Calculate fitness score for a baby variant.
            #         
            #         CRITICAL: Shadow-first priority hierarchy
            #         1. shadow_pnl (maximize)
            #         2. sign_flip_rate (minimize)
            #         3. paper_vs_shadow_degradation (minimize)
            #         4. trade_count (minimum threshold)
            #         5. win_rate (optional, lower weight)
            #         
            #         Returns composite fitness score or -999 if insufficient data.
            #         """
            #         if variant_id not in self.execution_states:
            #             return -999.0
            #         
            #         state = self.execution_states[variant_id]
            #         
            #         # Get metrics
            #         shadow_pnl = state['shadow_pnl']
            #         paper_pnl = state['paper_pnl']
            #         trade_count = state['shadow_trade_count']
            #         
            #         # Calculate sign flips (paper win → shadow loss)
            #         sign_flips = 0
            #         trades = state['trades']
            #         
            #         # Group trades by timestamp to find paper/shadow pairs
            #         paper_trades = [t for t in trades if t.get('source') == 'paper']
            #         shadow_trades = [t for t in trades if t.get('source') == 'shadow']
            #         
            #         # Count sign flips
            #         for p, s in zip(paper_trades, shadow_trades):
            #             p_pnl = float(p.get('pnl', 0))
            #             s_pnl = float(s.get('pnl', 0))
            #             if p_pnl > 0 and s_pnl < 0:
            #                 sign_flips += 1
            #         
            #         sign_flip_rate = (sign_flips / max(1, len(paper_trades)) * 100) if paper_trades else 0.0
            #         
            #         # Calculate degradation
            #         degradation_pct = ((paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100) if shadow_pnl != 0 else 0.0
            #         
            #         # Filter: minimum trade count
            #         if trade_count < 20:
            #             return -999.0  # Disqualified - insufficient sample
            #         
            #         # PRIMARY SCORE: Shadow PnL (scaled 0-100)
            #         # Assume max realistic PnL is $1000 for normalization
            #         score_pnl = min(max(shadow_pnl / 10.0, 0), 100)  # Normalize to 0-100
            #         
            #         # SECONDARY: Penalize sign flips (each 1% = -0.5 points)
            #         penalty_flips = sign_flip_rate * 0.5
            #         
            #         # TERTIARY: Penalize degradation (each 1% = -0.2 points)
            #         penalty_degradation = degradation_pct * 0.2
            #         
            #         # Composite score
            #         final_score = score_pnl - penalty_flips - penalty_degradation
            #         
            #         # Store for later retrieval
            #         self.fitness_scores[variant_id] = {
            #             'score': final_score,
            #             'shadow_pnl': shadow_pnl,
            #             'paper_pnl': paper_pnl,
            #             'sign_flip_rate': sign_flip_rate,
            #             'degradation_pct': degradation_pct,
            #             'trade_count': trade_count,
            #         }
            #         
            #         return final_score
            #     
            #     def get_baby_status(self, variant_id):
            #         """Get current status of a baby variant"""
            #         if variant_id not in self.execution_states:
            #             return None
            #         
            #         state = self.execution_states[variant_id]
            #         score = self.fitness_scores.get(variant_id, {})
            #         
            #         status = {
            #             'variant_id': variant_id,
            #             'paper_pnl': state['paper_pnl'],
            #             'shadow_pnl': state['shadow_pnl'],
            #             'paper_trades': state['paper_trade_count'],
            #             'shadow_trades': state['shadow_trade_count'],
            #             'fitness_score': score.get('score', -999),
            #             'sign_flip_rate': score.get('sign_flip_rate', 0),
            #             'degradation_pct': score.get('degradation_pct', 0),
            #         }
            #         
            #         # THINK Memory: Record evaluation (Phase 2.6)
            #         if self.arena_bridge and state['shadow_trade_count'] > 0:
            #             self.arena_bridge.on_variant_evaluated(
            #                 variant_id=variant_id,
            #                 trades=state['shadow_trade_count'],
            #                 flip_rate=score.get('sign_flip_rate', 0) / 100.0,
            #                 pnl=state['shadow_pnl'],
            #                 divergence=score.get('degradation_pct', 0) / 100.0,
            #                 drawdown=0.0,
            #                 survival=1.0 if state['shadow_pnl'] > 0 else 0.0,
            #                 trajectory='unknown'
            #             )
            #         
            #         return status
            #     
            #     def get_nursery_leaderboard(self):
            #         """
            #         Get all babies ranked by fitness score.
            #         Returns list sorted by score (descending).
            #         """
            #         leaderboard = []
            #         
            #         for baby in self.babies:
            #             variant_id = baby['variant_id']
            #             baby_status = self.get_baby_status(variant_id)
            #             
            #             if baby_status:
            #                 # Score each variant
            #                 score = self.score_variant(variant_id)
            #                 baby_status['fitness_score'] = score
            #                 
            #                 leaderboard.append({
            #                     'variant_id': variant_id,
            #                     'mutation_type': baby.get('mutation_type', ''),
            #                     'trades': baby_status['shadow_trades'],
            #                     'shadow_pnl': round(baby_status['shadow_pnl'], 2),
            #                     'flip_rate': round(baby_status['sign_flip_rate'], 1),
            #                     'degradation': round(baby_status['degradation_pct'], 1),
            #                     'score': round(score, 1),
            #                     'status': 'active',
            #                 })
            #         
            #         # Sort by score (descending)
            #         leaderboard.sort(key=lambda x: x['score'], reverse=True)
            #         
            #         return leaderboard
            #     
            #     def get_strongest_baby(self):
            #         """
            #         Identify the strongest surviving baby variant.
            #         Returns the baby with highest fitness score.
            #         """
            #         leaderboard = self.get_nursery_leaderboard()
            #         
            #         if not leaderboard:
            #             return None
            #         
            #         # Return top-ranked baby (already sorted)
            #         winner = leaderboard[0]
            #         
            #         # Find full baby data
            #         for baby in self.babies:
            #             if baby['variant_id'] == winner['variant_id']:
            #                 return {
            #                     'baby': baby,
            #                     'metrics': winner,
            #                 }
            #         
            #         return None
            #     
            #     def get_baby_by_id(self, variant_id):
            #         """Get full baby strategy data by variant_id"""
            #         for baby in self.babies:
            #             if baby['variant_id'] == variant_id:
            #             for record in bot_records:
            #                 # Reconstruct baby dict from database
            #                 baby = {
            #                     'variant_id': record['bot_id'],
            #                     'parent_id': record['parent_bot_id'],
            #                     'generation': record['generation'],
            #                     'mutation_type': record['mutation_type'],
            #                     'parameters': json.loads(record['parameters'] or '{}'),
            #                     'hypothesis_id': record['hypothesis_id'],
            #                     'created_at': record['created_at'],
            #                 }
            #                 
            #                 self.babies.append(baby)
            #                 
            #                 # Initialize execution state
            #                 self.execution_states[record['bot_id']] = {
            #                     'paper_equity': [],
            #                     'shadow_equity': [],
            #                     'trades': [],
            #                     'paper_pnl': 0.0,
            #                     'shadow_pnl': 0.0,
            #                     'paper_trade_count': 0,
            #                     'shadow_trade_count': 0,
            #                 }
            #             
            #             conn.close()
            #             
            #             print(f"[EVOLUTION] Hydrated {len(self.babies)} babies from database")
            #             
            #         except Exception as e:
            #             print(f"[EVOLUTION] WARNING: Could not hydrate from database: {e}")
            #             self.babies = []
