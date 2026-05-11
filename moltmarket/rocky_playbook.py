"""
ROCKY Playbook & Logbook System

Captures high-signal observations for BRAIN tightening and operator learning.
Future OpenClaws learn from this.
"""

import json
from datetime import datetime
from pathlib import Path


class PlaybookEntry:
    """High-signal observation for the playbook."""
    
    CATEGORIES = [
        'BRAIN_RULE',        # How to tighten BRAIN
        'NURSERY_RULE',      # How to keep Nursery healthy
        'REALITY_RULE',      # What's real vs illusion
        'FAILURE_PATTERN',   # What went wrong and why
        'OPERATOR_GUIDE',    # Tips for humans
        'UX_RULE',          # What confuses operators
    ]
    
    def __init__(self, category, pattern, why_it_matters, rule, confidence=0.0, source='unknown', context=''):
        assert category in self.CATEGORIES, f"Invalid category: {category}"
        
        self.timestamp = datetime.utcnow().isoformat()
        self.category = category
        self.pattern = pattern
        self.why_it_matters = why_it_matters
        self.rule = rule
        self.confidence = confidence
        self.source = source  # 'arena', 'nursery', 'molt', 'brain', 'operator'
        self.context = context
    
    def to_dict(self):
        return {
            'timestamp': self.timestamp,
            'category': self.category,
            'pattern': self.pattern,
            'why_it_matters': self.why_it_matters,
            'rule': self.rule,
            'confidence': self.confidence,
            'source': self.source,
            'context': self.context,
        }


class RockyPlaybook:
    """Persistent playbook of high-signal observations."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.playbook_file = workspace_dir / 'rocky_playbook.jsonl'
        self.ensure_file()
    
    def ensure_file(self):
        """Create playbook file if it doesn't exist."""
        if not self.playbook_file.exists():
            self.playbook_file.touch()
    
    def log(self, entry: PlaybookEntry):
        """Add entry to playbook."""
        with open(self.playbook_file, 'a') as f:
            f.write(json.dumps(entry.to_dict()) + '\n')
        
        print(f"[PLAYBOOK] {entry.category}: {entry.pattern} ({entry.confidence:.0%})")
    
    def get_all(self, limit=None) -> list:
        """Get all entries."""
        entries = []
        if not self.playbook_file.exists():
            return entries
        
        with open(self.playbook_file, 'r') as f:
            for line in f:
                if line.strip():
                    entries.append(json.loads(line))
        
        if limit:
            return entries[-limit:]
        return entries
    
    def get_by_category(self, category) -> list:
        """Get entries by category."""
        all_entries = self.get_all()
        return [e for e in all_entries if e['category'] == category]
    
    def get_by_source(self, source) -> list:
        """Get entries by source (arena, nursery, brain, operator)."""
        all_entries = self.get_all()
        return [e for e in all_entries if e['source'] == source]
    
    def summarize(self) -> dict:
        """Get playbook summary."""
        entries = self.get_all()
        
        summary = {
            'total_entries': len(entries),
            'by_category': {},
            'top_patterns': [],
            'high_confidence': [],
        }
        
        # Count by category
        for cat in PlaybookEntry.CATEGORIES:
            count = len([e for e in entries if e['category'] == cat])
            if count > 0:
                summary['by_category'][cat] = count
        
        # Top patterns (by confidence)
        sorted_by_confidence = sorted(entries, key=lambda e: e['confidence'], reverse=True)
        summary['top_patterns'] = [e['pattern'] for e in sorted_by_confidence[:5]]
        summary['high_confidence'] = [
            {'pattern': e['pattern'], 'confidence': e['confidence']}
            for e in sorted_by_confidence[:3]
        ]
        
        return summary


class RockyOperatorPlaybook:
    """Meta-playbook: learning what future operators need to know."""
    
    def __init__(self, workspace_dir: Path):
        self.workspace_dir = workspace_dir
        self.operator_guide_file = workspace_dir / 'operator_playbook.md'
    
    def generate_guide(self, playbook: RockyPlaybook) -> str:
        """Generate markdown guide from playbook."""
        entries = playbook.get_all()
        
        guide = "# Operator's Playbook\n\n"
        guide += f"Generated: {datetime.utcnow().isoformat()}\n"
        guide += f"Based on {len(entries)} observations\n\n"
        
        # BRAIN Rules
        brain_rules = playbook.get_by_category('BRAIN_RULE')
        if brain_rules:
            guide += "## BRAIN Tightening Rules\n\n"
            for rule in brain_rules[-5:]:  # Latest 5
                guide += f"### {rule['pattern']}\n"
                guide += f"**Confidence:** {rule['confidence']:.0%}\n"
                guide += f"**Why:** {rule['why_it_matters']}\n"
                guide += f"**Rule:** {rule['rule']}\n\n"
        
        # Nursery Rules
        nursery_rules = playbook.get_by_category('NURSERY_RULE')
        if nursery_rules:
            guide += "## Nursery Stewardship Rules\n\n"
            for rule in nursery_rules[-5:]:
                guide += f"### {rule['pattern']}\n"
                guide += f"**Confidence:** {rule['confidence']:.0%}\n"
                guide += f"**Rule:** {rule['rule']}\n\n"
        
        # Failure Patterns
        failures = playbook.get_by_category('FAILURE_PATTERN')
        if failures:
            guide += "## Common Failure Patterns\n\n"
            for failure in failures[-5:]:
                guide += f"### {failure['pattern']}\n"
                guide += f"**What went wrong:** {failure['why_it_matters']}\n\n"
        
        # UX Rules
        ux_rules = playbook.get_by_category('UX_RULE')
        if ux_rules:
            guide += "## Operator Experience Tips\n\n"
            for ux in ux_rules[-5:]:
                guide += f"- {ux['pattern']}: {ux['rule']}\n"
        
        return guide
    
    def publish_guide(self, guide_text: str):
        """Write guide to file."""
        with open(self.operator_guide_file, 'w') as f:
            f.write(guide_text)
        
        print(f"[PLAYBOOK] Operator guide published to {self.operator_guide_file}")
        return self.operator_guide_file
