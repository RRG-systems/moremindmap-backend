"""
BABY REGISTRY - Authoritative source for baby identity, lifecycle, and lineage

Persistent registry (JSONL file) tracking:
- variant_id (unique identifier)
- parent_id (lineage)
- generation (depth from baseline)
- dna (strategy parameters)
- status (active, promoted, retired, dead)
- spawned_at (creation timestamp)
- promoted_at (promotion timestamp, if applicable)

This is the source of truth for baby identity and lifecycle.
Performance (PnL, trades, win_rate) comes from unified_ledger.
Runtime execution state (evolution_engine.babies[]) is a cache only.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


class BabyRegistry:
    def __init__(self, registry_file: str = "baby_registry.jsonl"):
        self.registry_file = Path(registry_file)
        self.registry = {}
        self.load()
    
    def load(self):
        """Load registry from disk"""
        if self.registry_file.exists():
            with open(self.registry_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entry = json.loads(line)
                        self.registry[entry['variant_id']] = entry
            print(f"[REGISTRY] Loaded {len(self.registry)} babies from {self.registry_file}")
        else:
            print(f"[REGISTRY] New registry created at {self.registry_file}")
    
    def save(self):
        """Save registry to disk (append mode)"""
        with open(self.registry_file, 'a') as f:
            # This is inefficient for updates; for now write full file
            pass
    
    def register_baby(self, variant_id: str, parent_id: str, generation: int, dna: Dict) -> Dict:
        """Register a new baby (called on first trade)"""
        if variant_id in self.registry:
            return self.registry[variant_id]
        
        entry = {
            'variant_id': variant_id,
            'parent_id': parent_id,
            'generation': generation,
            'dna': dna,
            'status': 'active',
            'spawned_at': datetime.utcnow().isoformat(),
            'promoted_at': None,
        }
        
        self.registry[variant_id] = entry
        self._append_to_file(entry)
        print(f"[REGISTRY] Registered baby: {variant_id} (parent={parent_id}, gen={generation})")
        return entry
    
    def get_baby(self, variant_id: str) -> Optional[Dict]:
        """Get baby info from registry"""
        return self.registry.get(variant_id)
    
    def get_all_active(self) -> List[Dict]:
        """Get all active babies"""
        return [b for b in self.registry.values() if b['status'] == 'active']
    
    def promote_baby(self, variant_id: str):
        """Mark baby as promoted"""
        if variant_id in self.registry:
            self.registry[variant_id]['status'] = 'promoted'
            self.registry[variant_id]['promoted_at'] = datetime.utcnow().isoformat()
            self._rewrite_registry()
            print(f"[REGISTRY] Promoted: {variant_id}")
    
    def retire_baby(self, variant_id: str):
        """Mark baby as retired"""
        if variant_id in self.registry:
            self.registry[variant_id]['status'] = 'retired'
            self._rewrite_registry()
            print(f"[REGISTRY] Retired: {variant_id}")
    
    def _append_to_file(self, entry: Dict):
        """Append single entry to JSONL file"""
        with open(self.registry_file, 'a') as f:
            f.write(json.dumps(entry) + '\n')
    
    def _rewrite_registry(self):
        """Rewrite entire registry to file (for updates)"""
        with open(self.registry_file, 'w') as f:
            for entry in self.registry.values():
                f.write(json.dumps(entry) + '\n')


# Global instance
baby_registry = None


def init_registry(registry_file: str = "baby_registry.jsonl") -> BabyRegistry:
    """Initialize global registry"""
    global baby_registry
    baby_registry = BabyRegistry(registry_file)
    return baby_registry


def get_registry() -> BabyRegistry:
    """Get global registry"""
    global baby_registry
    if baby_registry is None:
        baby_registry = BabyRegistry()
    return baby_registry
