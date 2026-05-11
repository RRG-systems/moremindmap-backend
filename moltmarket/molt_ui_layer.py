#!/usr/bin/env python3
"""
MOLT UI Layer — Phase 3.2
Serves MOLT Feed data for the web interface

Bridges MOLT persistence → Flask JSON API
"""

import json
import sys
from pathlib import Path
from typing import List, Dict, Optional

sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
from molt_persistence import MOLTPersistence


class MOLTUILayer:
    """REST layer for MOLT Feed UI"""
    
    def __init__(self):
        self.molt = MOLTPersistence()
        self.molt.connect()
    
    def close(self):
        """Close connections"""
        self.molt.close()
    
    def get_feed(
        self,
        post_type_filter: Optional[str] = None,
        agent_filter: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get MOLT feed for UI
        
        Args:
            post_type_filter: 'proposal' | 'disagreement' | 'note' | None
            agent_filter: 'Overfitter' | 'Explorer' | 'Risk Manager' | None
            limit: max posts to return
        
        Returns:
            list of feed items with enriched data
        """
        import sqlite3
        
        conn = sqlite3.connect(str(self.molt.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        query = "SELECT * FROM molt_feed WHERE 1=1"
        params = []
        
        if post_type_filter:
            query += " AND post_type = ?"
            params.append(post_type_filter)
        
        if agent_filter:
            query += " AND agent_name = ?"
            params.append(agent_filter)
        
        query += " ORDER BY created_at DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        posts = cursor.fetchall()
        
        # Enrich posts with spawn data
        enriched = []
        for post in posts:
            post_dict = dict(post)
            
            # Get spawn info if this was a proposal
            if post_dict['post_type'] == 'proposal' and post_dict['linked_hypothesis_id']:
                spawns = self.molt.get_molt_spawns_for_hypothesis(post_dict['linked_hypothesis_id'])
                if spawns:
                    spawn_data = spawns[0]  # Most recent
                    post_dict['spawn_info'] = {
                        'spawn_id': spawn_data['spawn_id'],
                        'hypothesis_id': spawn_data['hypothesis_id'],
                        'canonical_bot_id': spawn_data['canonical_bot_id'],
                        'variant_count': len(json.loads(spawn_data['variant_bot_ids']))
                    }
            
            enriched.append(post_dict)
        
        conn.close()
        return enriched
    
    def get_lineage(self, molt_id: str) -> Dict:
        """
        Get full lineage for a molt post (for detail view)
        
        Returns dict with:
        - post info
        - hypothesis info (if proposal)
        - spawned bots and their metrics
        """
        import sqlite3
        
        lineage_data = self.molt.get_molt_lineage(molt_id)
        
        if not lineage_data:
            return {}
        
        # Add hypothesis details
        if lineage_data.get('linked_hypothesis_id'):
            conn = sqlite3.connect(str(self.molt.db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT hypothesis_id, title, description, target_market, 
                       target_regime, expected_behavior, failure_modes, status
                FROM hypotheses
                WHERE hypothesis_id = ?
            """, (lineage_data['linked_hypothesis_id'],))
            
            hyp = cursor.fetchone()
            if hyp:
                hyp_dict = dict(hyp)
                if hyp_dict.get('failure_modes'):
                    hyp_dict['failure_modes'] = json.loads(hyp_dict['failure_modes'])
                lineage_data['hypothesis'] = hyp_dict
            
            conn.close()
        
        return lineage_data
    
    def spawn_from_molt(self, molt_id: str) -> Dict:
        """
        Spawn new babies from an existing MOLT proposal
        
        Uses existing hypothesis backend to create 11 babies
        Logs spawn lineage normally
        
        Returns spawn_id and created bot IDs
        """
        import sqlite3
        from uuid import uuid4
        from copy import deepcopy
        
        sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
        from hypothesis_engine import HypothesisEngine
        
        # Get molt post
        lineage = self.molt.get_molt_lineage(molt_id)
        
        if not lineage or lineage.get('post_type') != 'proposal':
            return {'status': 'error', 'message': 'Invalid molt_id or not a proposal'}
        
        hypothesis_id = lineage.get('linked_hypothesis_id')
        if not hypothesis_id:
            return {'status': 'error', 'message': 'No hypothesis linked to this proposal'}
        
        # Spawn 11 babies
        spawned_bot_ids = []
        conn = sqlite3.connect(str(self.molt.db_path))
        cursor = conn.cursor()
        
        # Canonical
        canonical_id = f"bot-moltuispawn-canonical-{uuid4().hex[:8]}"
        canonical_dna = {
            "entry_threshold": 2.0,
            "exit_threshold": 1.5,
            "hold_time": 300,
            "selectivity": 0.7,
            "trade_size": 1.0,
            "max_open_positions": 5
        }
        
        cursor.execute("""
            INSERT INTO bots 
            (bot_id, hypothesis_id, creation_source, dna_json, role, current_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (canonical_id, hypothesis_id, 'molt_ui_spawn', json.dumps(canonical_dna), 'baby', 'testing'))
        spawned_bot_ids.append(canonical_id)
        
        # 10 variants
        mutation_ranges = [
            ("entry_threshold", [1.5, 2.5]),
            ("exit_threshold", [1.0, 2.0]),
            ("hold_time", [200, 400]),
            ("selectivity", [0.5, 0.9]),
            ("trade_size", [0.8, 1.2]),
        ]
        
        import random
        for i in range(10):
            variant_id = f"bot-moltuispawn-variant-{i+1:02d}-{uuid4().hex[:8]}"
            variant_dna = deepcopy(canonical_dna)
            param_name, (min_val, max_val) = mutation_ranges[i % len(mutation_ranges)]
            variant_dna[param_name] = random.uniform(min_val, max_val)
            
            cursor.execute("""
                INSERT INTO bots 
                (bot_id, hypothesis_id, creation_source, dna_json, role, current_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (variant_id, hypothesis_id, 'molt_ui_spawn', json.dumps(variant_dna), 'baby', 'testing'))
            spawned_bot_ids.append(variant_id)
        
        conn.commit()
        
        # Log spawn in molt_spawns
        spawn_id = self.molt.log_molt_spawn(
            molt_id=molt_id,
            hypothesis_id=hypothesis_id,
            spawned_bot_ids=spawned_bot_ids,
            spawn_reason="user_spawn_from_molt_ui"
        )
        
        conn.close()
        
        return {
            'status': 'success',
            'spawn_id': spawn_id,
            'hypothesis_id': hypothesis_id,
            'canonical_bot_id': canonical_id,
            'variant_count': 10,
            'total_spawned': len(spawned_bot_ids),
            'all_bot_ids': spawned_bot_ids
        }
    
    def get_statistics(self) -> Dict:
        """Get MOLT statistics"""
        return self.molt.get_molt_statistics()
    
    def get_agent_names(self) -> List[str]:
        """Get list of all agents with posts"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.molt.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT agent_name FROM molt_feed ORDER BY agent_name")
        agents = [row[0] for row in cursor.fetchall()]
        conn.close()
        return agents
    
    def get_post_types(self) -> List[str]:
        """Get list of all post types"""
        import sqlite3
        
        conn = sqlite3.connect(str(self.molt.db_path))
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT post_type FROM molt_feed ORDER BY post_type")
        types = [row[0] for row in cursor.fetchall()]
        conn.close()
        return types
    
    def get_thread(self, molt_id: str) -> List[Dict]:
        """Get full thread (root + all replies)"""
        return self.molt.get_thread(molt_id)
