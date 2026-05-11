#!/usr/bin/env python3
"""
PHASE 31: Variant Nursery Management
Manages concurrent execution, scoring, and persistence of baby strategy variants
"""

import csv
from pathlib import Path
from datetime import datetime


class VariantNursery:
    """
    Manages the nursery of baby variant strategies.
    Handles concurrent execution, fitness scoring, and CSV persistence.
    """
    
    def __init__(self, workspace_dir, evolution_engine):
        """
        Initialize nursery system.
        
        workspace_dir: Path to MOLTmarket workspace
        evolution_engine: Reference to EvolutionEngine instance
        """
        self.workspace = Path(workspace_dir)
        self.evolution_engine = evolution_engine
        self.nursery_file = self.workspace / 'variant_nursery.csv'
        self.babies_spawned = False
        
        # CSV headers (append-only schema)
        self.csv_headers = [
            'run_id',
            'variant_id',
            'parent_id',
            'parent_generation',
            'generation',
            'mutation_type',
            'parameter_value',
            'trade_count',
            'paper_pnl',
            'shadow_pnl',
            'sign_flip_rate',
            'degradation_pct',
            'score',
            'status',
            'timestamp',
        ]
        
        # Initialize CSV if needed
        self._ensure_csv_file()
    
    def _ensure_csv_file(self):
        """Create variant_nursery.csv if it doesn't exist"""
        if not self.nursery_file.exists():
            with open(self.nursery_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
            print(f"[PHASE 31] Created {self.nursery_file.name}")
    
    def spawn_babies(self, run_id, count=10):
        """
        Spawn baby variants for this run.
        Each baby mutates a SINGLE dimension of parent strategy.
        
        PHASE 4.5: ATOMIC transaction — memory never gets ahead of database
        
        run_id: Identifier for this experimental run
        count: Number of babies to spawn (default 10)
        
        Returns list of spawned babies (only if DB write succeeds).
        """
        from spawn_transaction import SpawnTransaction
        
        print(f"\n[PHASE 31 - NURSERY] Spawning {count} baby variants...")
        
        # Get parent ID
        parent_id = self.evolution_engine.current_parent['id']
        
        # Spawn in memory
        babies = self.evolution_engine.spawn_baby_variants(count=count)
        
        print(f"[PHASE 31 - NURSERY] {len(babies)} babies spawned in memory")
        
        # PHASE 4.5: Atomic database write
        tx = SpawnTransaction()
        success, message = tx.spawn_and_persist(babies, parent_id)
        
        if not success:
            print(f"[PHASE 31 - NURSERY] ✗ DATABASE WRITE FAILED: {message}")
            print(f"[PHASE 31 - NURSERY] Discarding memory spawn (no corruption)")
            self.babies_spawned = False
            return []
        
        # Only mark as spawned if database write succeeded
        self.babies_spawned = True
        
        print(f"[PHASE 31 - NURSERY] ✓ {len(babies)} babies persisted to database (atomic)")
        print(f"[PHASE 31 - NURSERY] Babies:")
        for baby in babies:
            mutation_dim = baby.get('mutation_type', '')
            variant_id = baby.get('variant_id', '')
            print(f"  ✓ {variant_id}: mutate {mutation_dim}")
        
        return babies
    
    def record_baby_trade(self, variant_id, source, trade_dict):
        """
        Record a trade execution for a baby variant.
        
        variant_id: ID of baby variant
        source: 'paper' or 'shadow'
        trade_dict: Trade result dict
        """
        trade_data = {
            'pnl': float(trade_dict.get('pnl', 0)),
            'equity_value': 10000.0,  # Placeholder - would come from execution layer
        }
        
        self.evolution_engine.record_baby_execution(variant_id, source, trade_data)
    
    def finalize_and_score_babies(self, run_id):
        """
        Score all baby variants using fitness hierarchy.
        Persist results to CSV.
        
        CRITICAL SCORING HIERARCHY (shadow-first):
        1. shadow_pnl (maximize)
        2. sign_flip_rate (minimize)
        3. paper_vs_shadow_degradation (minimize)
        4. trade_count >= 20 (minimum threshold)
        5. win_rate (optional)
        
        run_id: Current experiment run ID
        """
        print(f"\n[PHASE 31 - NURSERY] Scoring {len(self.evolution_engine.babies)} babies...")
        
        leaderboard = self.evolution_engine.get_nursery_leaderboard()
        
        # Persist each baby to CSV
        for rank, baby_metrics in enumerate(leaderboard):
            variant_id = baby_metrics['variant_id']
            baby = self.evolution_engine.get_baby_by_id(variant_id)
            
            if not baby:
                continue
            
            # Determine status: top baby is candidate_winner, rest active
            status = 'candidate_winner' if rank == 0 else 'active'
            
            # Get parameter value that was mutated
            mutation_type = baby.get('mutation_type', '')
            param_value = baby.get('parameters', {}).get(
                self._dimension_to_param(mutation_type),
                'N/A'
            )
            
            # Build CSV row
            row = {
                'run_id': run_id,
                'variant_id': variant_id,
                'parent_id': baby.get('parent_id', ''),
                'parent_generation': baby.get('parent_generation', 0),
                'generation': baby.get('generation', 1),
                'mutation_type': mutation_type,
                'parameter_value': param_value,
                'trade_count': baby_metrics['trades'],
                'paper_pnl': baby_metrics.get('paper_pnl', 0),
                'shadow_pnl': baby_metrics['shadow_pnl'],
                'sign_flip_rate': baby_metrics['flip_rate'],
                'degradation_pct': baby_metrics['degradation'],
                'score': baby_metrics['score'],
                'status': status,
                'timestamp': datetime.utcnow().isoformat(),
            }
            
            # Append to CSV
            self._append_to_csv([row])
            
            print(f"  ✓ {variant_id} (score: {baby_metrics['score']}) → {status}")
        
        print(f"[PHASE 31 - NURSERY] Scoring complete. Top candidate: {leaderboard[0]['variant_id']}")
        
        return leaderboard
    
    def _dimension_to_param(self, dimension):
        """Map mutation dimension to parameter name"""
        mapping = {
            'entry_threshold': 'entry_threshold',
            'exit_threshold': 'exit_threshold',
            'holding_time': 'holding_time',
            'confirmation_rules': 'confirmation_ticks',
            'stop_loss_sensitivity': 'stop_loss_sensitivity',
            'target_profit_sensitivity': 'target_profit_sensitivity',
        }
        return mapping.get(dimension, dimension)
    
    def _append_to_csv(self, rows):
        """Append rows to variant_nursery.csv"""
        with open(self.nursery_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.csv_headers)
            for row in rows:
                writer.writerow(row)
    
    def get_nursery_leaderboard(self):
        """Get current nursery leaderboard (sorted by score)"""
        return self.evolution_engine.get_nursery_leaderboard()
    
    def get_strongest_baby(self):
        """Get the strongest baby variant (highest fitness score)"""
        return self.evolution_engine.get_strongest_baby()
    
    def promote_baby(self, variant_id):
        """
        MANUAL PROMOTION WORKFLOW:
        Mark a baby as promoted (status → 'promoted' in CSV)
        
        Does NOT auto-promote. Requires explicit decision from D.J.
        
        variant_id: ID of baby to promote
        """
        # Read CSV, find row with variant_id, update status
        rows = []
        with open(self.nursery_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Find and update
        updated = False
        for row in rows:
            if row['variant_id'] == variant_id:
                row['status'] = 'promoted'
                updated = True
                break
        
        if updated:
            # Rewrite CSV
            with open(self.nursery_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"[PHASE 31 - NURSERY] {variant_id} promoted to 'promoted' status")
            return True
        
        return False
    
    def retire_baby(self, variant_id):
        """
        Mark a baby as retired (no longer competing).
        Status → 'retired' in CSV.
        
        variant_id: ID of baby to retire
        """
        # Read CSV, find row with variant_id, update status
        rows = []
        with open(self.nursery_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        
        # Find and update
        updated = False
        for row in rows:
            if row['variant_id'] == variant_id:
                row['status'] = 'retired'
                updated = True
                break
        
        if updated:
            # Rewrite CSV
            with open(self.nursery_file, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=self.csv_headers)
                writer.writeheader()
                writer.writerows(rows)
            
            print(f"[PHASE 31 - NURSERY] {variant_id} retired")
            return True
        
        return False
    
    def get_candidate_for_promotion(self):
        """
        Get the top candidate baby for manual promotion.
        Returns strongest baby with full metrics.
        """
        winner = self.evolution_engine.get_strongest_baby()
        
        if not winner:
            return None
        
        baby = winner['baby']
        metrics = winner['metrics']
        
        return {
            'variant_id': baby['variant_id'],
            'mutation_type': baby['mutation_type'],
            'parent_id': baby['parent_id'],
            'parameters': baby['parameters'],
            'metrics': metrics,
        }
