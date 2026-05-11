#!/usr/bin/env python3
"""
Debug script: Trace complete baby spawn → execute → display flow
"""

import sys
import sqlite3
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'moltmarket'))

from evolution_engine import EvolutionEngine

def check_db_state(label):
    """Query MOLT database for current baby count"""
    try:
        db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Count bots
        cursor.execute("SELECT COUNT(*) FROM bots")
        count = cursor.fetchone()[0]
        print(f"[DB {label}] Total bots: {count}")
        
        # Get recent IDs
        cursor.execute("SELECT bot_id FROM bots ORDER BY created_at DESC LIMIT 5")
        recent = cursor.fetchall()
        if recent:
            print(f"[DB {label}] Recent bots: {[r[0] for r in recent]}")
        
        conn.close()
        return count
    except Exception as e:
        print(f"[DB {label}] ERROR: {e}")
        return 0

def check_evolution_engine():
    """Check what evolution_engine sees"""
    engine = EvolutionEngine()
    print(f"[ENGINE INIT] Before hydrate: {len(engine.babies)} babies in memory")
    
    # Call hydrate explicitly
    try:
        engine.hydrate_from_database()
        print(f"[ENGINE HYDRATE] After hydrate: {len(engine.babies)} babies in memory")
        
        if engine.babies:
            for i, baby in enumerate(engine.babies[:3]):
                print(f"[ENGINE BABY {i}] id={baby.get('variant_id', '?')} status={baby.get('status', '?')}")
    except Exception as e:
        print(f"[ENGINE HYDRATE] ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    print("\n" + "="*60)
    print("NURSERY DATA FLOW DEBUG")
    print("="*60 + "\n")
    
    print("[STEP 1] Check DB state BEFORE anything")
    count_before = check_db_state("BEFORE")
    
    print("\n[STEP 2] Initialize EvolutionEngine (should hydrate)")
    check_evolution_engine()
    
    print("\n[STEP 3] Check DB state AFTER init")
    count_after = check_db_state("AFTER")
    
    print(f"\n[RESULT] DB babies before: {count_before}, after: {count_after}")
    print("[EXPECTED] count_after > count_before (or same if DB persisted)")
