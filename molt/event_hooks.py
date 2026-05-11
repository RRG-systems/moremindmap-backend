#!/usr/bin/env python3
"""
Event Hooks — Phase 2 Foundation
Wires Arena events → THINK Memory updates

These hooks are called from:
1. Bot spawn points (new bot created)
2. Mutation application (babies spawned)
3. Evaluation completion (metrics snapshot)
4. Mutation result classification (helped/hurt/inconclusive)
5. Decision points (approve/reject, promote/kill, control actions)

CRITICAL: These are APPEND ONLY. Do not modify existing records.
THIN LAYER: No business logic here. Just events → database writes.
"""

import json
import sqlite3
from datetime import datetime
from uuid import uuid4
from pathlib import Path


class THINKEventHook:
    """
    Connect Arena events to THINK Memory writes.
    Thin layer that translates system events to database records.
    """
    
    def __init__(self, think_db_path=None):
        """
        Initialize event hook layer.
        
        Args:
            think_db_path: Path to THINK Memory SQLite database
        """
        if not think_db_path:
            think_db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
        
        self.db_path = think_db_path
        self.db_conn = None
    
    def connect(self):
        """Open database connection"""
        self.db_conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row
        return self.db_conn
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.commit()
            self.db_conn.close()
            self.db_conn = None
    
    def _execute(self, sql, params):
        """Execute SQL and commit"""
        cursor = self.db_conn.cursor()
        cursor.execute(sql, params)
        self.db_conn.commit()
        return cursor.lastrowid
    
    # =====================================================
    # EVENT 1: BOT_SPAWNED
    # =====================================================
    
    def on_bot_spawned(self, bot_id, hypothesis_id, creation_source, dna_json,
                       parent_bot_id=None, generation=1, current_run_id=None):
        """
        Hook: Bot created (initial or baby variant)
        
        Args:
            bot_id: Unique bot identifier
            hypothesis_id: Hypothesis this bot expresses
            creation_source: 'manual' | 'rocky_proposal' | 'seed_agent' | 'molt_feed'
            dna_json: Dict of bot parameters
            parent_bot_id: Parent bot ID (if spawned from mutation)
            generation: Generation number
            current_run_id: Which arena run (if active)
        
        Returns:
            None (writes to database)
        """
        # Convert dna to JSON string if dict
        if isinstance(dna_json, dict):
            dna_json_str = json.dumps(dna_json)
        else:
            dna_json_str = dna_json
        
        print(f"[THINK] Event: BOT_SPAWNED {bot_id} (hyp={hypothesis_id})")
        
        sql = """
            INSERT INTO bots
            (bot_id, parent_bot_id, generation, hypothesis_id, creation_source,
             dna_json, role, current_status, current_run_id, latest_metrics_json,
             created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """
        
        self._execute(sql, [
            bot_id,
            parent_bot_id or None,
            generation or 1,
            hypothesis_id,
            creation_source,
            dna_json_str,
            'baby',  # New bots start as babies
            'testing',  # New bots are testing
            current_run_id or None,
            json.dumps({})  # metrics start empty
        ])
    
    # =====================================================
    # EVENT 2: MUTATION_SPAWNED
    # =====================================================
    
    def on_mutation_spawned(self, mutation_id, source_bot_id, resulting_bot_ids,
                           hypothesis_id, diagnosis, mutation_type, parameter_changes,
                           rationale, expected_effect=None, source_proposal_id=None):
        """
        Hook: Mutation creates babies
        
        Args:
            mutation_id: Unique mutation identifier
            source_bot_id: Bot that was mutated
            resulting_bot_ids: List of 11 baby bot IDs (canonical + 10 variants)
            hypothesis_id: Hypothesis being tested
            diagnosis: Problem identified (e.g., "high flip rate")
            mutation_type: 'entry' | 'exit' | 'hold' | 'selectivity' | 'size' | 'concentration'
            parameter_changes: Dict of {param: {before: X, after: Y}, ...}
            rationale: Why this mutation was chosen
            expected_effect: What we expect to improve
            source_proposal_id: If from Rocky proposal, the proposal ID
        
        Returns:
            None (writes to database)
        """
        # Convert parameter_changes to JSON string if dict
        if isinstance(parameter_changes, dict):
            param_changes_str = json.dumps(parameter_changes)
        else:
            param_changes_str = parameter_changes
        
        # Convert resulting_bot_ids to JSON string if list
        if isinstance(resulting_bot_ids, list):
            resulting_ids_str = json.dumps(resulting_bot_ids)
        else:
            resulting_ids_str = resulting_bot_ids
        
        print(f"[THINK] Event: MUTATION_SPAWNED {mutation_id}")
        print(f"  Source: {source_bot_id}")
        print(f"  Type: {mutation_type}")
        print(f"  Diagnosis: {diagnosis}")
        print(f"  Babies: {len(json.loads(resulting_ids_str)) if isinstance(resulting_ids_str, str) else len(resulting_ids_str)}")
        
        sql = """
            INSERT INTO mutations
            (mutation_id, source_bot_id, resulting_bot_ids, hypothesis_id,
             source_proposal_id, diagnosis, mutation_type, parameter_changes,
             rationale, expected_effect, result, created_at, evaluated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, NULL)
        """
        
        self._execute(sql, [
            mutation_id,
            source_bot_id,
            resulting_ids_str,
            hypothesis_id,
            source_proposal_id or None,
            diagnosis,
            mutation_type,
            param_changes_str,
            rationale,
            expected_effect or None,
            'pending'  # Mutations start pending
        ])
        
        # Link each baby bot to this mutation
        cursor = self.db_conn.cursor()
        baby_ids = json.loads(resulting_ids_str) if isinstance(resulting_ids_str, str) else resulting_ids_str
        
        for baby_id in baby_ids:
            cursor.execute(
                "UPDATE bots SET created_by_mutation_id = ? WHERE bot_id = ?",
                [mutation_id, baby_id]
            )
        self.db_conn.commit()
    
    # =====================================================
    # EVENT 3: EVALUATION_COMPLETE
    # =====================================================
    
    def on_evaluation_complete(self, bot_id, metrics_snapshot):
        """
        Hook: Bot evaluation completed, metrics available
        
        Args:
            bot_id: Bot that was evaluated
            metrics_snapshot: Dict with metrics
                {
                    'trades': int,
                    'flip_rate': float,
                    'shadow_pnl': float,
                    'divergence': float,
                    'drawdown': float,
                    'survival': float,
                    'trajectory': str (optional),
                    'control_action': str (optional)
                }
        
        Returns:
            None (writes to database)
        """
        if isinstance(metrics_snapshot, dict):
            metrics_str = json.dumps(metrics_snapshot)
        else:
            metrics_str = metrics_snapshot
        
        print(f"[THINK] Event: EVALUATION_COMPLETE {bot_id}")
        print(f"  Metrics: {metrics_snapshot if isinstance(metrics_snapshot, dict) else json.loads(metrics_snapshot)}")
        
        sql = """
            UPDATE bots
            SET latest_metrics_json = ?, current_status = 'active', updated_at = CURRENT_TIMESTAMP
            WHERE bot_id = ?
        """
        
        self._execute(sql, [metrics_str, bot_id])
    
    # =====================================================
    # EVENT 4: MUTATION_RESULT_CLASSIFIED
    # =====================================================
    
    def on_mutation_result_classified(self, mutation_id, result, result_summary):
        """
        Hook: Mutation evaluated and classified (helped/hurt/inconclusive)
        
        Args:
            mutation_id: The mutation ID
            result: 'helped' | 'hurt' | 'inconclusive'
            result_summary: Brief explanation of the result
        
        Returns:
            None (writes to database)
        """
        print(f"[THINK] Event: MUTATION_RESULT_CLASSIFIED {mutation_id}")
        print(f"  Result: {result}")
        print(f"  Summary: {result_summary}")
        
        sql = """
            UPDATE mutations
            SET result = ?, result_summary = ?, evaluated_at = CURRENT_TIMESTAMP
            WHERE mutation_id = ?
        """
        
        self._execute(sql, [result, result_summary, mutation_id])
    
    # =====================================================
    # EVENT 5: DECISION_MADE
    # =====================================================
    
    def on_decision_made(self, decision_type, source, reason, related_bot_id=None,
                        related_hypothesis_id=None, related_mutation_id=None,
                        context_snapshot=None):
        """
        Hook: User or system makes decision
        
        Args:
            decision_type: 'approve_proposal' | 'reject_proposal' | 'promote_bot' |
                          'kill_bot' | 'start_new_run' | 'hold' | 'switch' | 'control_action'
            source: 'user' | 'rocky' | 'control_layer'
            reason: Why this decision was made
            related_bot_id: Bot involved (if any)
            related_hypothesis_id: Hypothesis involved (if any)
            related_mutation_id: Mutation involved (if any)
            context_snapshot: Dict of key metrics at decision time
        
        Returns:
            decision_id (string)
        """
        decision_id = f"dec_{uuid4().hex[:8]}"
        
        if isinstance(context_snapshot, dict):
            context_str = json.dumps(context_snapshot)
        else:
            context_str = context_snapshot or json.dumps({})
        
        print(f"[THINK] Event: DECISION_MADE {decision_id}")
        print(f"  Type: {decision_type}")
        print(f"  Source: {source}")
        print(f"  Reason: {reason}")
        
        sql = """
            INSERT INTO decisions
            (decision_id, related_bot_id, related_hypothesis_id, related_mutation_id,
             source, decision_type, context_snapshot, reason, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        """
        
        self._execute(sql, [
            decision_id,
            related_bot_id or None,
            related_hypothesis_id or None,
            related_mutation_id or None,
            source,
            decision_type,
            context_str,
            reason
        ])
        
        return decision_id
    
    # =====================================================
    # Helper: Record PROMOTE decision
    # =====================================================
    
    def on_bot_promoted(self, bot_id, hypothesis_id, reason, context_snapshot=None):
        """
        Convenience method: Bot promoted to capital allocation
        
        Args:
            bot_id: Bot being promoted
            hypothesis_id: Its hypothesis
            reason: Why this bot is ready
            context_snapshot: Current metrics
        
        Returns:
            decision_id
        """
        # Update bot status
        cursor = self.db_conn.cursor()
        cursor.execute(
            "UPDATE bots SET current_status = 'promoted', updated_at = CURRENT_TIMESTAMP WHERE bot_id = ?",
            [bot_id]
        )
        self.db_conn.commit()
        
        # Record decision
        return self.on_decision_made(
            decision_type='promote_bot',
            source='user',
            reason=reason,
            related_bot_id=bot_id,
            related_hypothesis_id=hypothesis_id,
            context_snapshot=context_snapshot
        )
    
    # =====================================================
    # Helper: Record KILL decision
    # =====================================================
    
    def on_bot_killed(self, bot_id, hypothesis_id, reason, context_snapshot=None):
        """
        Convenience method: Bot killed / retired
        
        Args:
            bot_id: Bot being killed
            hypothesis_id: Its hypothesis
            reason: Why this bot failed
            context_snapshot: Final metrics
        
        Returns:
            decision_id
        """
        # Update bot status
        cursor = self.db_conn.cursor()
        cursor.execute(
            "UPDATE bots SET current_status = 'failed', retired_at = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP WHERE bot_id = ?",
            [bot_id]
        )
        self.db_conn.commit()
        
        # Record decision
        return self.on_decision_made(
            decision_type='kill_bot',
            source='user',
            reason=reason,
            related_bot_id=bot_id,
            related_hypothesis_id=hypothesis_id,
            context_snapshot=context_snapshot
        )
