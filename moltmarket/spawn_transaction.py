"""
Spawn Transaction Manager — Phase 4.5 Persistence Integration
Ensures atomic database writes for baby spawning
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime


class SpawnTransaction:
    """Manages atomic spawn operations with database"""
    
    def __init__(self, db_path: Path = None):
        self.db_path = db_path or Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
    
    def spawn_and_persist(self, babies, parent_id):
        """
        Write all babies to database atomically
        
        babies: list of baby dicts
        parent_id: parent strategy ID
        
        Returns: (success: bool, message: str)
        """
        if not babies:
            return False, "No babies to spawn"
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # STEP 1: Clear previous spawn for this parent
            cursor.execute("DELETE FROM bots WHERE parent_bot_id = ?", (parent_id,))
            cleared_count = cursor.rowcount
            print(f"[SPAWN_TX] Cleared {cleared_count} previous spawn set for {parent_id}")
            
            # STEP 2: Insert all babies with debug logging
            print(f"[SPAWN_TX] Inserting {len(babies)} babies:")
            for baby in babies:
                bot_id = baby.get('variant_id')
                print(f"[SPAWN_TX]   → {bot_id} (mutation={baby.get('mutation_type')})")
                cursor.execute("""
                    INSERT INTO bots (
                        bot_id,
                        parent_bot_id,
                        generation,
                        mutation_type,
                        dna_json,
                        hypothesis_id,
                        creation_source,
                        role,
                        created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    baby.get('variant_id'),
                    parent_id,
                    baby.get('generation', 0),
                    baby.get('mutation_type', 'NONE'),
                    json.dumps(baby.get('parameters', {})),
                    baby.get('hypothesis_id', 'unknown'),
                    'spawn',  # creation_source
                    'baby',   # role
                    datetime.utcnow().isoformat()
                ))
            
            # STEP 3: Commit all at once (atomic)
            conn.commit()
            
            # Verify all inserts succeeded
            cursor.execute("SELECT COUNT(*) FROM bots WHERE parent_bot_id = ?", (parent_id,))
            actual_count = cursor.fetchone()[0]
            conn.close()
            
            print(f"[SPAWN_TX] ✓ Committed {len(babies)} babies to database (atomic)")
            print(f"[SPAWN_TX] Verified: {actual_count} babies now in DB for parent {parent_id}")
            return True, f"Spawned and persisted {len(babies)} babies"
            
        except sqlite3.IntegrityError as e:
            print(f"[SPAWN_TX] ✗ INTEGRITY ERROR (likely bot_id collision):")
            print(f"[SPAWN_TX]   Error: {e}")
            print(f"[SPAWN_TX]   Parent: {parent_id}")
            print(f"[SPAWN_TX]   Attempted babies: {[b.get('variant_id') for b in babies[:3]]}...")
            
            # Check what's actually in the database
            try:
                cursor.execute("SELECT bot_id FROM bots WHERE parent_bot_id = ? LIMIT 5", (parent_id,))
                existing = cursor.fetchall()
                if existing:
                    print(f"[SPAWN_TX]   Existing bots for parent: {[row[0] for row in existing]}")
            except:
                pass
            
            conn.rollback()
            conn.close()
            return False, f"Database constraint failed: {e}"
        
        except Exception as e:
            print(f"[SPAWN_TX] ✗ Unexpected error: {e}")
            try:
                conn.rollback()
                conn.close()
            except:
                pass
            return False, f"Spawn failed: {e}"
    
    def clear_spawn_set(self, parent_id):
        """Clear only babies from a specific parent"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM bots WHERE parent_bot_id = ?", (parent_id,))
            cleared = cursor.rowcount
            conn.commit()
            conn.close()
            print(f"[SPAWN_TX] Cleared {cleared} babies from {parent_id}")
            return True, cleared
        except Exception as e:
            return False, str(e)
    
    def verify_babies_in_database(self, parent_id):
        """Verify that all babies are actually in the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bots WHERE parent_bot_id = ?", (parent_id,))
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except Exception as e:
            print(f"[SPAWN_TX] Error verifying babies: {e}")
            return -1
