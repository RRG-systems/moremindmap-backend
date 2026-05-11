"""
State Validator — Phase 4.5 Persistence Integration
Ensures memory and database consistency on startup
"""

import sqlite3
import json
from pathlib import Path


class StateValidator:
    """Validates that in-memory state matches database + money_state.json"""
    
    def __init__(self, db_path: Path = None, money_state_path: Path = None):
        self.db_path = db_path or Path.cwd() / '../molt/think-memory.db'
        self.money_state_path = money_state_path or Path.cwd() / 'money_state.json'
        self.errors = []
        self.warnings = []
    
    def validate_full_system(self, active_bot_id, allocation_pct, babies_count):
        """
        Comprehensive validation of system state
        
        Returns: (is_valid: bool, errors: list, warnings: list)
        """
        self.errors = []
        self.warnings = []
        
        # Check 1: money_state.json exists and is readable
        if not self._validate_money_state():
            return False, self.errors, self.warnings
        
        # Check 2: Database exists and is accessible
        if not self._validate_database():
            return False, self.errors, self.warnings
        
        # Check 3: If active_bot_id is set, it must exist in database
        if active_bot_id:
            if not self._validate_active_bot_in_database(active_bot_id):
                return False, self.errors, self.warnings
        
        # Check 4: Allocation must be valid
        if not self._validate_allocation(allocation_pct):
            return False, self.errors, self.warnings
        
        # Check 5: Babies in memory should match database
        if not self._validate_babies_consistency(babies_count):
            self.warnings.append(f"Baby count mismatch (memory={babies_count}, db={self._count_bots_in_database()})")
        
        is_valid = len(self.errors) == 0
        return is_valid, self.errors, self.warnings
    
    def _validate_money_state(self):
        """Check money_state.json exists and is valid JSON"""
        try:
            if not self.money_state_path.exists():
                self.warnings.append(f"money_state.json not found at {self.money_state_path}")
                return True  # Not an error, will be created
            
            with open(self.money_state_path, 'r') as f:
                json.load(f)
            
            return True
        except json.JSONDecodeError as e:
            self.errors.append(f"money_state.json is corrupt: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Cannot read money_state.json: {e}")
            return False
    
    def _validate_database(self):
        """Check database exists and is accessible"""
        try:
            if not self.db_path.exists():
                self.warnings.append(f"Database not found at {self.db_path}")
                return True  # Not an error, will be created on first spawn
            
            conn = sqlite3.connect(self.db_path)
            conn.execute("SELECT 1 FROM bots LIMIT 1")
            conn.close()
            
            return True
        except sqlite3.DatabaseError as e:
            self.errors.append(f"Database corrupted: {e}")
            return False
        except Exception as e:
            self.errors.append(f"Cannot access database: {e}")
            return False
    
    def _validate_active_bot_in_database(self, active_bot_id):
        """Verify active_bot_id exists in bots table"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM bots WHERE bot_id = ?", (active_bot_id,))
            result = cursor.fetchone()
            conn.close()
            
            if not result:
                self.errors.append(f"Active bot '{active_bot_id}' not found in database")
                return False
            
            return True
        except Exception as e:
            self.errors.append(f"Cannot validate active bot: {e}")
            return False
    
    def _validate_allocation(self, allocation_pct):
        """Verify allocation is in valid range"""
        if allocation_pct is None or allocation_pct < 0 or allocation_pct > 100:
            self.errors.append(f"Allocation out of range: {allocation_pct}%")
            return False
        
        return True
    
    def _validate_babies_consistency(self, memory_count):
        """Check that baby count is reasonable"""
        db_count = self._count_bots_in_database()
        
        # Allow for small discrepancies (new spawn not yet persisted)
        if abs(memory_count - db_count) > 2:
            self.warnings.append(f"Large discrepancy: memory={memory_count}, db={db_count}")
        
        return True
    
    def _count_bots_in_database(self):
        """Get current bot count from database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM bots")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
    
    def print_report(self, is_valid):
        """Print validation report"""
        status = "✓ VALID" if is_valid else "✗ INVALID"
        print(f"\n[STATE VALIDATOR] {status}")
        
        if self.errors:
            print("\n[ERRORS]")
            for err in self.errors:
                print(f"  ✗ {err}")
        
        if self.warnings:
            print("\n[WARNINGS]")
            for warn in self.warnings:
                print(f"  ⚠ {warn}")
        
        if not self.errors and not self.warnings:
            print("  ✓ All checks passed")
        
        print()
