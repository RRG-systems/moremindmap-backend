#!/usr/bin/env python3
"""
Hypothesis Engine — Phase 2 Foundation
Manages hypothesis creation and linking to bot lifecycle.

This is the input layer for THINK Memory.
No bot exists without a hypothesis.
"""

import json
import sqlite3
from datetime import datetime
from uuid import uuid4
from pathlib import Path


class HypothesisEngine:
    """
    Create and manage hypotheses that drive bot creation and evaluation.
    Integrates with THINK Memory (SQLite).
    """
    
    # Valid target regimes
    VALID_REGIMES = ['ranging', 'trending', 'high_vol', 'low_vol', 'mixed']
    
    def __init__(self, think_db_path=None):
        """
        Initialize hypothesis engine.
        
        Args:
            think_db_path: Path to THINK Memory SQLite database
                          Default: ~/.openclaw/workspace/molt/think-memory.db
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
            self.db_conn.close()
            self.db_conn = None
    
    def create_hypothesis(self, title, description, target_market, target_regime, 
                         expected_behavior, failure_modes=None):
        """
        Create a new hypothesis and store in THINK Memory.
        
        Args:
            title: Short name (e.g., "Mean Reversion Low Vol")
            description: Longer explanation of the edge claim
            target_market: Market (e.g., "BTC", "ETH", "SPX")
            target_regime: One of VALID_REGIMES
            expected_behavior: What "working" should look like
            failure_modes: List of ways this hypothesis can fail
        
        Returns:
            hypothesis_id (string)
        
        Raises:
            ValueError if inputs invalid
        """
        # Validate inputs
        if not title or not description:
            raise ValueError("title and description required")
        
        if target_regime not in self.VALID_REGIMES:
            raise ValueError(f"target_regime must be one of {self.VALID_REGIMES}")
        
        # Generate ID
        hypothesis_id = f"hyp_{uuid4().hex[:8]}"
        
        # Prepare data
        failure_modes = failure_modes or []
        allowed_clusters = ['entry', 'exit', 'hold', 'selectivity', 'size', 'concentration']
        
        # Insert into database
        cursor = self.db_conn.cursor()
        cursor.execute("""
            INSERT INTO hypotheses 
            (hypothesis_id, title, description, target_market, target_regime,
             expected_behavior, failure_modes, allowed_parameter_clusters,
             supporting_bots, status, notes_summary, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
        """, [
            hypothesis_id,
            title,
            description,
            target_market,
            target_regime,
            expected_behavior,
            json.dumps(failure_modes),
            json.dumps(allowed_clusters),
            json.dumps([]),  # supporting_bots starts empty
            'testing',  # initial status
            None  # notes_summary
        ])
        self.db_conn.commit()
        
        print(f"[HYPOTHESIS] Created {hypothesis_id}")
        print(f"  Title: {title}")
        print(f"  Regime: {target_regime}")
        print(f"  Market: {target_market}")
        
        return hypothesis_id
    
    def get_hypothesis(self, hypothesis_id):
        """
        Retrieve hypothesis from database.
        
        Args:
            hypothesis_id: The hypothesis ID
        
        Returns:
            Dict with hypothesis data, or None if not found
        """
        cursor = self.db_conn.cursor()
        cursor.execute("SELECT * FROM hypotheses WHERE hypothesis_id = ?", [hypothesis_id])
        row = cursor.fetchone()
        
        if not row:
            return None
        
        # Convert to dict and parse JSON fields
        hyp = dict(row)
        hyp['failure_modes'] = json.loads(hyp['failure_modes'] or '[]')
        hyp['allowed_parameter_clusters'] = json.loads(hyp['allowed_parameter_clusters'] or '[]')
        hyp['supporting_bots'] = json.loads(hyp['supporting_bots'] or '[]')
        
        return hyp
    
    def list_hypotheses(self, status=None):
        """
        List all hypotheses, optionally filtered by status.
        
        Args:
            status: Filter by status ('testing', 'promising', 'weak', 'broken', 'retired')
        
        Returns:
            List of hypothesis dicts
        """
        cursor = self.db_conn.cursor()
        
        if status:
            cursor.execute(
                "SELECT * FROM hypotheses WHERE status = ? ORDER BY updated_at DESC",
                [status]
            )
        else:
            cursor.execute("SELECT * FROM hypotheses ORDER BY updated_at DESC")
        
        rows = cursor.fetchall()
        
        hypotheses = []
        for row in rows:
            hyp = dict(row)
            hyp['failure_modes'] = json.loads(hyp['failure_modes'] or '[]')
            hyp['allowed_parameter_clusters'] = json.loads(hyp['allowed_parameter_clusters'] or '[]')
            hyp['supporting_bots'] = json.loads(hyp['supporting_bots'] or '[]')
            hypotheses.append(hyp)
        
        return hypotheses
    
    def generate_hypothesis_from_bot_intent(self, intent):
        """
        Helper: Rocky suggests a hypothesis structure based on user intent.
        
        This is for when a user doesn't have a pre-defined hypothesis.
        Rocky helps formalize it.
        
        Args:
            intent: String describing what the user wants to test
        
        Returns:
            Dict with suggested hypothesis fields
        
        Example:
            intent = "I want to trade mean reversion on low volatility moves"
            suggestion = {
                'title': 'Mean Reversion Low Vol',
                'description': 'Short-term price reversals after low-vol deviation moves',
                'target_regime': 'low_vol',
                'expected_behavior': 'Prices revert within 5-10 minutes',
                'failure_modes': ['Regime shift to trending', 'Execution drag kills signal', ...]
            }
        """
        # Very basic intent parsing
        intent_lower = intent.lower()
        
        suggestion = {
            'title': 'User-Proposed Strategy',
            'description': intent,
            'target_market': 'BTC',  # Default
            'target_regime': 'mixed',  # Default
            'expected_behavior': 'Testing...',
            'failure_modes': ['Untested']
        }
        
        # Simple keyword detection
        if 'mean' in intent_lower and 'revert' in intent_lower:
            suggestion['title'] = 'Mean Reversion'
            suggestion['target_regime'] = 'ranging'
            suggestion['expected_behavior'] = 'Price reverts to mean within 5-10 minutes'
            suggestion['failure_modes'] = [
                'Regime shift to trending',
                'Execution drag kills signal',
                'Entry threshold misaligned'
            ]
        
        if 'trend' in intent_lower or 'momentum' in intent_lower:
            suggestion['title'] = 'Trend Following'
            suggestion['target_regime'] = 'trending'
            suggestion['expected_behavior'] = 'Captures continuation after breakout'
            suggestion['failure_modes'] = [
                'Fake breakout',
                'Trend reversal',
                'Stop placement too tight'
            ]
        
        if 'low vol' in intent_lower:
            suggestion['target_regime'] = 'low_vol'
        elif 'high vol' in intent_lower:
            suggestion['target_regime'] = 'high_vol'
        
        if 'eth' in intent_lower or 'ethereum' in intent_lower:
            suggestion['target_market'] = 'ETH'
        elif 'spx' in intent_lower or 'sp500' in intent_lower:
            suggestion['target_market'] = 'SPX'
        
        return suggestion


class HypothesisValidator:
    """
    Validate hypothesis before bot creation.
    Ensures bot has proper hypothesis linkage.
    """
    
    def __init__(self, hypothesis_engine):
        """
        Initialize validator with hypothesis engine reference.
        
        Args:
            hypothesis_engine: HypothesisEngine instance
        """
        self.engine = hypothesis_engine
    
    def validate_for_bot_creation(self, hypothesis_id):
        """
        Check if hypothesis is valid for bot creation.
        
        Args:
            hypothesis_id: The hypothesis ID
        
        Returns:
            (valid: bool, reason: str)
        """
        hyp = self.engine.get_hypothesis(hypothesis_id)
        
        if not hyp:
            return False, f"Hypothesis {hypothesis_id} not found"
        
        if hyp['status'] == 'broken':
            return False, f"Hypothesis is marked as broken. Cannot spawn new bots."
        
        if hyp['status'] == 'retired':
            return False, f"Hypothesis is retired. Use a different hypothesis."
        
        # All other statuses (testing, promising, weak) are OK
        return True, "OK"
    
    def validate_mutation_on_hypothesis(self, hypothesis_id, mutation_type):
        """
        Check if mutation type is allowed on this hypothesis.
        
        Args:
            hypothesis_id: The hypothesis ID
            mutation_type: One of 'entry', 'exit', 'hold', 'selectivity', 'size', 'concentration'
        
        Returns:
            (allowed: bool, reason: str)
        """
        hyp = self.engine.get_hypothesis(hypothesis_id)
        
        if not hyp:
            return False, f"Hypothesis {hypothesis_id} not found"
        
        allowed_clusters = hyp['allowed_parameter_clusters']
        
        if mutation_type not in allowed_clusters:
            return False, f"Mutation type '{mutation_type}' not in allowed clusters for this hypothesis"
        
        return True, "OK"


# =====================================================
# HELPER: Rocky proposes hypothesis from user intent
# =====================================================

def rocky_help_formalize_hypothesis(user_intent):
    """
    Quick helper function: Rocky helps user formalize hypothesis from intent.
    
    This is called when user wants to test something but hasn't formally
    defined the hypothesis yet.
    
    Args:
        user_intent: String describing what user wants to test
    
    Returns:
        Dict with suggested hypothesis fields
    """
    engine = HypothesisEngine()
    suggestion = engine.generate_hypothesis_from_bot_intent(user_intent)
    return suggestion
