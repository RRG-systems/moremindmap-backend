#!/usr/bin/env python3
"""
Fix evolution_engine.py hydrate method to use correct DB schema
"""

import re

with open('evolution_engine.py', 'r') as f:
    content = f.read()

# Find and replace the entire hydrate method
pattern = r'    def hydrate_from_database\(self\):.*?self\.babies = \[\]'

new_method = '''    def hydrate_from_database(self):
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
            self.babies = []'''

# Replace
content = re.sub(pattern, new_method, content, flags=re.DOTALL)

with open('evolution_engine.py', 'w') as f:
    f.write(content)

print("✓ Fixed hydrate method")
