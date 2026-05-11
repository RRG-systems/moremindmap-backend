#!/usr/bin/env python3
"""
Money State Persistence — Phase 4.5 FINAL LOCK
Survives session resets. "New Run" clears metrics, NOT strategy.

RULE:
New Run = clear dashboard view
NOT = restart trading system

Strategy state MUST persist.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class MoneyStatePersistence:
    """Persists strategy state across session resets"""
    
    def __init__(self, workspace_dir: Path = None):
        self.workspace = workspace_dir or Path.cwd()
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.state_file = self.workspace / 'money_state.json'
        self.strategy_state = self._load_or_init()
    
    def _load_or_init(self) -> Dict:
        """Load persisted state or initialize"""
        if self.state_file.exists():
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        
        # Initialize fresh state
        return {
            'active_bot_id': None,
            'risk_state': 'NORMAL',
            'candidate_pool': [],
            'allocations': {},
            'hypothesis_links': {},
            'mutation_lineage': {},
            'last_updated': datetime.utcnow().isoformat(),
            'version': '1.0'
        }
    
    def save_state(self) -> None:
        """Persist strategy state to disk"""
        self.strategy_state['last_updated'] = datetime.utcnow().isoformat()
        with open(self.state_file, 'w') as f:
            json.dump(self.strategy_state, f, indent=2)
    
    def get_strategy_state(self) -> Dict:
        """Get full strategy state (persists across New Run)"""
        return {
            'active_bot_id': self.strategy_state.get('active_bot_id'),
            'risk_state': self.strategy_state.get('risk_state'),
            'candidate_pool': self.strategy_state.get('candidate_pool'),
            'allocations': self.strategy_state.get('allocations'),
            'hypothesis_links': self.strategy_state.get('hypothesis_links'),
            'mutation_lineage': self.strategy_state.get('mutation_lineage'),
        }
    
    def update_strategy_state(self, **updates) -> None:
        """Update strategy state (persists)"""
        for key, value in updates.items():
            if key in self.strategy_state:
                self.strategy_state[key] = value
        self.save_state()
    
    def on_new_run(self) -> Dict:
        """
        Called when user clicks "New Run"
        
        Resets metrics, NOT strategy state.
        Returns what to reset.
        """
        
        return {
            'action': 'NEW_RUN',
            'timestamp': datetime.utcnow().isoformat(),
            'reset_metrics': True,  # PnL, trades, charts
            'preserve_strategy': True,  # active_bot, allocation, hypothesis links
            'strategy_state': self.get_strategy_state(),
            'message': 'Metrics reset. Strategy state preserved.'
        }
    
    def register_bot(self, bot_id: str, hypothesis_id: str, allocation_pct: float) -> None:
        """Register bot with hypothesis link"""
        self.strategy_state['hypothesis_links'][bot_id] = hypothesis_id
        self.strategy_state['allocations'][bot_id] = allocation_pct
        self.save_state()
    
    def set_active_bot(self, bot_id: str) -> None:
        """Set active bot"""
        self.strategy_state['active_bot_id'] = bot_id
        self.save_state()
    
    def set_risk_state(self, state: str) -> None:
        """Set risk state"""
        self.strategy_state['risk_state'] = state
        self.save_state()
    
    def add_candidate(self, bot_id: str, score: float, metrics: Dict) -> None:
        """Add candidate to pool"""
        if bot_id not in [c['bot_id'] for c in self.strategy_state['candidate_pool']]:
            self.strategy_state['candidate_pool'].append({
                'bot_id': bot_id,
                'score': score,
                'metrics': metrics
            })
            self.save_state()
    
    def update_allocation(self, bot_id: str, allocation_pct: float) -> None:
        """Update bot allocation"""
        self.strategy_state['allocations'][bot_id] = allocation_pct
        self.save_state()
    
    def link_mutation(self, bot_id: str, parent_bot_id: str, mutation_type: str) -> None:
        """Link mutation for traceability"""
        if bot_id not in self.strategy_state['mutation_lineage']:
            self.strategy_state['mutation_lineage'][bot_id] = {
                'parent': parent_bot_id,
                'type': mutation_type,
                'created_at': datetime.utcnow().isoformat()
            }
            self.save_state()
    
    def clear_metrics_only(self) -> Dict:
        """Clear only metrics (called by New Run)"""
        # This is what gets reset
        return {
            'pnl': 0.0,
            'trades': 0,
            'charts': {},
            'session_metrics': {}
        }


if __name__ == '__main__':
    print("\n" + "=" * 80)
    print("Money State Persistence Test")
    print("=" * 80)
    
    from pathlib import Path
    persist = MoneyStatePersistence(Path('/tmp/test_money_state'))
    
    # Test 1: Register bot
    print("\n[TEST 1] Register bot")
    persist.register_bot('bot-001', 'hyp-mr-001', 1.0)
    persist.set_active_bot('bot-001')
    print(f"Active bot: {persist.strategy_state['active_bot_id']}")
    print(f"Hypothesis: {persist.strategy_state['hypothesis_links'].get('bot-001')}")
    
    # Test 2: Update allocation
    print("\n[TEST 2] Update allocation")
    persist.update_allocation('bot-001', 1.5)
    print(f"Allocation: {persist.strategy_state['allocations']['bot-001']}%")
    
    # Test 3: Add candidate
    print("\n[TEST 3] Add candidate")
    persist.add_candidate('bot-002', 85.5, {'survival': 92.0})
    print(f"Candidates: {len(persist.strategy_state['candidate_pool'])}")
    
    # Test 4: New Run (metrics reset, strategy persists)
    print("\n[TEST 4] New Run (strategy persists)")
    new_run = persist.on_new_run()
    print(f"Action: {new_run['action']}")
    print(f"Preserve strategy: {new_run['preserve_strategy']}")
    print(f"Active bot still: {new_run['strategy_state']['active_bot_id']}")
    print(f"Allocation still: {new_run['strategy_state']['allocations']}")
    
    # Test 5: Reload from disk
    print("\n[TEST 5] Reload from disk (persistence)")
    persist2 = MoneyStatePersistence(Path('/tmp/test_money_state'))
    print(f"Reloaded active bot: {persist2.strategy_state['active_bot_id']}")
    print(f"Reloaded allocation: {persist2.strategy_state['allocations']}")
    print(f"Reloaded candidates: {len(persist2.strategy_state['candidate_pool'])}")
    
    print("\n" + "=" * 80)
