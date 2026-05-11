#!/usr/bin/env python3
"""
PHASE 31: Evolution Engine for Strategy Variants
Spawns, mutates, and scores baby strategies using existing Mean Reversion framework
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
        self.current_parent = self._create_default_parent()
        
        # Keep legacy reference for compatibility
        self.parent_strategy = self.current_parent
        
        self.babies = []
        self.execution_states = {}
        self.fitness_scores = {}
    
    def _create_default_parent(self):
        """
        Create default parent strategy: Mean Reversion (20-tick, 0.3% deviation)
        This is the PHASE 28 locked-in strategy
        """
        return {
            'id': 'parent_mean_rev_20_03',
            'name': 'Mean Reversion (20-tick, 0.3%)',
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
        
        Returns list of baby strategies ready for execution.
        """
        # PHASE 32.3: CRITICAL - use authoritative current parent, never override
        parent_strategy = self.current_parent
        
        self.babies = []
        
        mutation_dimensions = [
            'entry_threshold',
            'exit_threshold',
            'holding_time',
            'confirmation_rules',
            'stop_loss_sensitivity',
            'target_profit_sensitivity',
        ]
        
        for i in range(count):
            # Create baby by copying parent
            baby = deepcopy(parent_strategy)
            
            # Select mutation dimension (cycle through if more babies than dimensions)
            mutation_dim = mutation_dimensions[i % len(mutation_dimensions)]
            
            # Apply SINGLE mutation using existing engine
            mutated_baby = self.mutate_one_dimension(
                variant=baby,
                dimension=mutation_dim,
                intensity=0.05  # 5% controlled mutation
            )
            
            # Add baby metadata
            mutated_baby['variant_id'] = f"baby_{str(i+1).zfill(3)}"
            mutated_baby['parent_id'] = parent_strategy['id']
            mutated_baby['mutation_type'] = mutation_dim
            mutated_baby['generation'] = 1
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
        
        return self.babies
    
    def record_baby_execution(self, variant_id, source, trade_data):
        """
        Record execution result for a baby variant.
        
        source: 'paper' or 'shadow'
        trade_data: dict with trade metrics
        """
        if variant_id not in self.execution_states:
            self.execution_states[variant_id] = {
                'paper_equity': [],
                'shadow_equity': [],
                'trades': [],
                'paper_pnl': 0.0,
                'shadow_pnl': 0.0,
                'paper_trade_count': 0,
                'shadow_trade_count': 0,
            }
        
        state = self.execution_states[variant_id]
        
        if source == 'paper':
            state['paper_equity'].append(trade_data.get('equity_value', 0))
            state['paper_pnl'] += float(trade_data.get('pnl', 0))
            state['paper_trade_count'] += 1
            state['trades'].append({'source': 'paper', **trade_data})
            
        elif source == 'shadow':
            state['shadow_equity'].append(trade_data.get('equity_value', 0))
            state['shadow_pnl'] += float(trade_data.get('pnl', 0))
            state['shadow_trade_count'] += 1
            state['trades'].append({'source': 'shadow', **trade_data})
    
    def score_variant(self, variant_id):
        """
        Calculate fitness score for a baby variant.
        
        CRITICAL: Shadow-first priority hierarchy
        1. shadow_pnl (maximize)
        2. sign_flip_rate (minimize)
        3. paper_vs_shadow_degradation (minimize)
        4. trade_count (minimum threshold)
        5. win_rate (optional, lower weight)
        
        Returns composite fitness score or -999 if insufficient data.
        """
        if variant_id not in self.execution_states:
            return -999.0
        
        state = self.execution_states[variant_id]
        
        # Get metrics
        shadow_pnl = state['shadow_pnl']
        paper_pnl = state['paper_pnl']
        trade_count = state['shadow_trade_count']
        
        # Calculate sign flips (paper win → shadow loss)
        sign_flips = 0
        trades = state['trades']
        
        # Group trades by timestamp to find paper/shadow pairs
        paper_trades = [t for t in trades if t.get('source') == 'paper']
        shadow_trades = [t for t in trades if t.get('source') == 'shadow']
        
        # Count sign flips
        for p, s in zip(paper_trades, shadow_trades):
            p_pnl = float(p.get('pnl', 0))
            s_pnl = float(s.get('pnl', 0))
            if p_pnl > 0 and s_pnl < 0:
                sign_flips += 1
        
        sign_flip_rate = (sign_flips / max(1, len(paper_trades)) * 100) if paper_trades else 0.0
        
        # Calculate degradation
        degradation_pct = ((paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100) if shadow_pnl != 0 else 0.0
        
        # Filter: minimum trade count
        if trade_count < 20:
            return -999.0  # Disqualified - insufficient sample
        
        # PRIMARY SCORE: Shadow PnL (scaled 0-100)
        # Assume max realistic PnL is $1000 for normalization
        score_pnl = min(max(shadow_pnl / 10.0, 0), 100)  # Normalize to 0-100
        
        # SECONDARY: Penalize sign flips (each 1% = -0.5 points)
        penalty_flips = sign_flip_rate * 0.5
        
        # TERTIARY: Penalize degradation (each 1% = -0.2 points)
        penalty_degradation = degradation_pct * 0.2
        
        # Composite score
        final_score = score_pnl - penalty_flips - penalty_degradation
        
        # Store for later retrieval
        self.fitness_scores[variant_id] = {
            'score': final_score,
            'shadow_pnl': shadow_pnl,
            'paper_pnl': paper_pnl,
            'sign_flip_rate': sign_flip_rate,
            'degradation_pct': degradation_pct,
            'trade_count': trade_count,
        }
        
        return final_score
    
    def get_baby_status(self, variant_id):
        """Get current status of a baby variant"""
        if variant_id not in self.execution_states:
            return None
        
        state = self.execution_states[variant_id]
        score = self.fitness_scores.get(variant_id, {})
        
        return {
            'variant_id': variant_id,
            'paper_pnl': state['paper_pnl'],
            'shadow_pnl': state['shadow_pnl'],
            'paper_trades': state['paper_trade_count'],
            'shadow_trades': state['shadow_trade_count'],
            'fitness_score': score.get('score', -999),
            'sign_flip_rate': score.get('sign_flip_rate', 0),
            'degradation_pct': score.get('degradation_pct', 0),
        }
    
    def get_nursery_leaderboard(self):
        """
        Get all babies ranked by fitness score.
        Returns list sorted by score (descending).
        """
        leaderboard = []
        
        for baby in self.babies:
            variant_id = baby['variant_id']
            baby_status = self.get_baby_status(variant_id)
            
            if baby_status:
                # Score each variant
                score = self.score_variant(variant_id)
                baby_status['fitness_score'] = score
                
                leaderboard.append({
                    'variant_id': variant_id,
                    'mutation_type': baby.get('mutation_type', ''),
                    'trades': baby_status['shadow_trades'],
                    'shadow_pnl': round(baby_status['shadow_pnl'], 2),
                    'flip_rate': round(baby_status['sign_flip_rate'], 1),
                    'degradation': round(baby_status['degradation_pct'], 1),
                    'score': round(score, 1),
                    'status': 'active',
                })
        
        # Sort by score (descending)
        leaderboard.sort(key=lambda x: x['score'], reverse=True)
        
        return leaderboard
    
    def get_strongest_baby(self):
        """
        Identify the strongest surviving baby variant.
        Returns the baby with highest fitness score.
        """
        leaderboard = self.get_nursery_leaderboard()
        
        if not leaderboard:
            return None
        
        # Return top-ranked baby (already sorted)
        winner = leaderboard[0]
        
        # Find full baby data
        for baby in self.babies:
            if baby['variant_id'] == winner['variant_id']:
                return {
                    'baby': baby,
                    'metrics': winner,
                }
        
        return None
    
    def get_baby_by_id(self, variant_id):
        """Get full baby strategy data by variant_id"""
        for baby in self.babies:
            if baby['variant_id'] == variant_id:
                return baby
        return None
