#!/usr/bin/env python3
"""
MOLT Persistence Layer (Phase 3.1)

Handles:
- Agent post logging (notes, proposals, disagreements)
- Hypothesis creation and linking
- Bot spawn tracking (11-baby spawns)
- Full lineage: agent post → hypothesis → bot IDs
"""

import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Optional


class MOLTPersistence:
    """Persistence layer for MOLT feed data"""
    
    def __init__(self, db_path: Optional[str] = None):
        if db_path is None:
            db_path = str(Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db')
        self.db_path = db_path
        self.conn = None
    
    def connect(self):
        """Connect to database"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
    
    def _execute(self, query: str, params: tuple = ()):
        """Execute query with auto-commit"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        self.conn.commit()
        return cursor
    
    def _fetchone(self, query: str, params: tuple = ()):
        """Fetch single row"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchone()
    
    def _fetchall(self, query: str, params: tuple = ()):
        """Fetch all rows"""
        cursor = self.conn.cursor()
        cursor.execute(query, params)
        return cursor.fetchall()
    
    # =====================================================
    # MOLT FEED OPERATIONS
    # =====================================================
    
    def log_agent_note(self, agent_name: str, content: str, topic: str = "general") -> str:
        """
        Log agent note to MOLT feed
        
        Args:
            agent_name: 'Overfitter' | 'Explorer' | 'Risk Manager'
            content: full note text
            topic: 'performance', 'exploration', 'risk', etc.
        
        Returns:
            molt_id
        """
        molt_id = f"molt-note-{uuid4().hex[:12]}"
        
        self._execute("""
            INSERT INTO molt_feed (molt_id, agent_name, post_type, content_text, topic)
            VALUES (?, ?, ?, ?, ?)
        """, (molt_id, agent_name, 'note', content, topic))
        
        print(f"[MOLT] Logged note from {agent_name}: {molt_id}")
        return molt_id
    
    def log_agent_proposal(
        self,
        agent_name: str,
        content: str,
        hypothesis_id: str,
        spawned_bot_ids: List[str],
        topic: str = "proposal"
    ) -> str:
        """
        Log agent proposal to MOLT feed
        Links to hypothesis and spawned bots
        
        Args:
            agent_name: 'Overfitter' | 'Explorer' | 'Risk Manager'
            content: full proposal text
            hypothesis_id: created hypothesis
            spawned_bot_ids: [canonical_id, variant_1, ..., variant_10]
            topic: description of proposal
        
        Returns:
            molt_id
        """
        molt_id = f"molt-proposal-{uuid4().hex[:12]}"
        bot_ids_json = json.dumps(spawned_bot_ids)
        
        self._execute("""
            INSERT INTO molt_feed 
            (molt_id, agent_name, post_type, content_text, topic, 
             linked_hypothesis_id, linked_bot_ids)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (molt_id, agent_name, 'proposal', content, topic, 
              hypothesis_id, bot_ids_json))
        
        print(f"[MOLT] Logged proposal from {agent_name}: {molt_id} → {hypothesis_id}")
        return molt_id
    
    def log_agent_disagreement(
        self,
        agent_name: str,
        content: str,
        replies_to_molt_id: str,
        replies_to_agent_name: str
    ) -> str:
        """
        Log agent disagreement/response to MOLT feed
        
        Args:
            agent_name: responding agent
            content: response text
            replies_to_molt_id: prior molt_id being responded to
            replies_to_agent_name: name of agent being responded to
        
        Returns:
            molt_id
        """
        molt_id = f"molt-disagreement-{uuid4().hex[:12]}"
        
        self._execute("""
            INSERT INTO molt_feed 
            (molt_id, agent_name, post_type, content_text, 
             replies_to_molt_id, replies_to_agent_name)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (molt_id, agent_name, 'disagreement', content, 
              replies_to_molt_id, replies_to_agent_name))
        
        print(f"[MOLT] Logged disagreement from {agent_name}: {molt_id}")
        return molt_id
    
    # =====================================================
    # MOLT SPAWN OPERATIONS
    # =====================================================
    
    def log_molt_spawn(
        self,
        molt_id: str,
        hypothesis_id: str,
        spawned_bot_ids: List[str],
        spawn_reason: str = ""
    ) -> str:
        """
        Log explicit spawn lineage: agent proposal → hypothesis → 11 bots
        
        Args:
            molt_id: which agent post triggered this
            hypothesis_id: created hypothesis
            spawned_bot_ids: [canonical, variant_1, ..., variant_10]
            spawn_reason: brief reason for spawn
        
        Returns:
            spawn_id
        """
        spawn_id = f"spawn-{uuid4().hex[:12]}"
        canonical_bot_id = spawned_bot_ids[0]
        variant_bot_ids = json.dumps(spawned_bot_ids[1:])
        
        self._execute("""
            INSERT INTO molt_spawns 
            (spawn_id, molt_id, hypothesis_id, canonical_bot_id, 
             variant_bot_ids, spawn_reason)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (spawn_id, molt_id, hypothesis_id, canonical_bot_id, 
              variant_bot_ids, spawn_reason))
        
        print(f"[MOLT] Logged spawn: {spawn_id} → {hypothesis_id} ({len(spawned_bot_ids)} bots)")
        return spawn_id
    
    # =====================================================
    # QUERY OPERATIONS
    # =====================================================
    
    def get_molt_feed(self, limit: int = 50, agent_filter: Optional[str] = None) -> List[Dict]:
        """
        Query MOLT feed
        
        Args:
            limit: max posts to return
            agent_filter: filter by agent_name (e.g. 'Overfitter')
        
        Returns:
            list of molt_feed rows as dicts
        """
        query = "SELECT * FROM molt_feed"
        params = []
        
        if agent_filter:
            query += " WHERE agent_name = ?"
            params.append(agent_filter)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        rows = self._fetchall(query, tuple(params))
        return [dict(row) for row in rows] if rows else []
    
    def get_molt_spawns_for_hypothesis(self, hypothesis_id: str) -> List[Dict]:
        """
        Get all spawns for a hypothesis
        
        Args:
            hypothesis_id: hypothesis to query
        
        Returns:
            list of molt_spawns rows
        """
        query = """
            SELECT * FROM molt_spawns 
            WHERE hypothesis_id = ?
            ORDER BY created_at DESC
        """
        rows = self._fetchall(query, (hypothesis_id,))
        return [dict(row) for row in rows] if rows else []
    
    def get_molt_lineage(self, molt_id: str) -> Dict:
        """
        Get full lineage for a molt post:
        molt_id → hypothesis → bot_ids
        
        Args:
            molt_id: agent post to trace
        
        Returns:
            dict with post, hypothesis, spawned bots, and variant results
        """
        # Get molt post
        molt_row = self._fetchone(
            "SELECT * FROM molt_feed WHERE molt_id = ?",
            (molt_id,)
        )
        if not molt_row:
            return {}
        
        molt_data = dict(molt_row)
        
        # Get spawned bots if this was a proposal
        if molt_data['post_type'] == 'proposal':
            spawn_row = self._fetchone(
                "SELECT * FROM molt_spawns WHERE molt_id = ?",
                (molt_id,)
            )
            if spawn_row:
                spawn_data = dict(spawn_row)
                
                # Get bot metrics for all spawned bots
                canonical_id = spawn_data['canonical_bot_id']
                variant_ids = json.loads(spawn_data['variant_bot_ids'])
                all_bot_ids = [canonical_id] + variant_ids
                
                bot_metrics = []
                for bot_id in all_bot_ids:
                    bot_row = self._fetchone(
                        "SELECT bot_id, latest_metrics_json FROM bots WHERE bot_id = ?",
                        (bot_id,)
                    )
                    if bot_row:
                        metrics = json.loads(bot_row['latest_metrics_json']) if bot_row['latest_metrics_json'] else {}
                        bot_metrics.append({
                            'bot_id': bot_id,
                            'is_canonical': bot_id == canonical_id,
                            'metrics': metrics
                        })
                
                molt_data['spawn'] = {
                    'spawn_id': spawn_data['spawn_id'],
                    'hypothesis_id': spawn_data['hypothesis_id'],
                    'canonical_bot_id': canonical_id,
                    'variant_count': len(variant_ids),
                    'bot_metrics': bot_metrics
                }
        
        return molt_data
    
    def get_agent_history(self, agent_name: str, limit: int = 20) -> List[Dict]:
        """
        Get all posts from an agent
        
        Args:
            agent_name: 'Overfitter' | 'Explorer' | 'Risk Manager'
            limit: max posts
        
        Returns:
            list of agent's molt_feed posts
        """
        query = """
            SELECT * FROM molt_feed 
            WHERE agent_name = ?
            ORDER BY created_at DESC
            LIMIT ?
        """
        rows = self._fetchall(query, (agent_name, limit))
        return [dict(row) for row in rows] if rows else []
    
    def get_disagreement_thread(self, molt_id: str) -> List[Dict]:
        """
        Get all responses to a post (disagreement thread)
        
        Args:
            molt_id: original post
        
        Returns:
            list of replies in chronological order
        """
        query = """
            SELECT * FROM molt_feed 
            WHERE replies_to_molt_id = ?
            ORDER BY created_at ASC
        """
        rows = self._fetchall(query, (molt_id,))
        return [dict(row) for row in rows] if rows else []
    
    def get_molt_statistics(self) -> Dict:
        """
        Get overall MOLT statistics
        
        Returns:
            dict with counts by agent, post type, etc.
        """
        stats = {}
        
        # Total posts
        total = self._fetchone("SELECT COUNT(*) as cnt FROM molt_feed")
        stats['total_posts'] = total['cnt'] if total else 0
        
        # By agent
        agents = self._fetchall("""
            SELECT agent_name, COUNT(*) as cnt 
            FROM molt_feed 
            GROUP BY agent_name
        """)
        stats['by_agent'] = {row['agent_name']: row['cnt'] for row in agents}
        
        # By type
        types = self._fetchall("""
            SELECT post_type, COUNT(*) as cnt 
            FROM molt_feed 
            GROUP BY post_type
        """)
        stats['by_type'] = {row['post_type']: row['cnt'] for row in types}
        
        # Spawned hypotheses
        hyp_count = self._fetchone("""
            SELECT COUNT(DISTINCT hypothesis_id) as cnt 
            FROM molt_spawns
        """)
        stats['hypotheses_spawned'] = hyp_count['cnt'] if hyp_count else 0
        
        # Total bots spawned
        bot_count = self._fetchone("""
            SELECT COUNT(*) as cnt 
            FROM molt_spawns
        """)
        # Each spawn creates 11 bots (1 canonical + 10 variants)
        stats['total_bots_spawned'] = (bot_count['cnt'] if bot_count else 0) * 11
        
        return stats
    
    def get_thread(self, molt_id: str) -> List[Dict]:
        """Get conversation thread (root + replies)"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM molt_feed WHERE molt_id = ?", (molt_id,))
        root = cursor.fetchone()
        if not root:
            conn.close()
            return []
        
        thread = [dict(root)]
        
        cursor.execute("""
            SELECT * FROM molt_feed 
            WHERE replies_to_molt_id = ? 
            ORDER BY created_at ASC
        """, (molt_id,))
        
        replies = cursor.fetchall()
        for reply in replies:
            thread.append(dict(reply))
        
        conn.close()
        return thread
    
    def get_recent_posts(self, limit: int = 5, exclude_replies: bool = False) -> List[Dict]:
        """Get recent posts for agents to react to"""
        query = "SELECT * FROM molt_feed"
        
        if exclude_replies:
            query += " WHERE replies_to_molt_id IS NULL"
        
        query += " ORDER BY created_at DESC LIMIT ?"
        
        rows = self._fetchall(query, (limit,))
        return [dict(row) for row in rows] if rows else []


# =====================================================
# TEST / DEBUG
# =====================================================

if __name__ == '__main__':
    # Quick test
    molt = MOLTPersistence()
    molt.connect()
    
    print("\n" + "=" * 70)
    print("MOLT Persistence Layer - Test")
    print("=" * 70)
    
    # Log a note
    note_id = molt.log_agent_note(
        "Overfitter",
        "[Agent Overfitter]\n\n**WE'VE GOT IT!**\n\nbaseline-01 is PRINTING.",
        "performance"
    )
    
    # Get statistics
    stats = molt.get_molt_statistics()
    print(f"\nMOLT Statistics:\n{json.dumps(stats, indent=2)}")
    
    molt.close()
