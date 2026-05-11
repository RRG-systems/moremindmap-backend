"""
ROCKY Operator Log — Record every decision, calibration, observation.

This is the playbook. Every calibration, every promotion, every insight.
Future ROCKYs (or D.J.) can review this and learn what worked.
"""

import json
from datetime import datetime
from pathlib import Path


class RockyOperatorLog:
    """Log ROCKY's decisions for learning and playbook building."""
    
    def __init__(self, log_file=None):
        self.log_file = log_file or str(
            Path.home() / '.openclaw' / 'workspace' / 'moltmarket' / 'rocky_operator_log.jsonl'
        )
    
    def log_calibration(self, style, baby_stats, reason, expected_outcome):
        """Log a calibration decision."""
        entry = {
            'type': 'calibration',
            'timestamp': datetime.now().isoformat(),
            'style': style,
            'baby_stats': baby_stats,
            'reason': reason,
            'expected_outcome': expected_outcome,
        }
        self._append(entry)
        print(f"[ROCKY LOG] Calibration logged: {style}")
    
    def log_observation(self, category, observation, confidence=0.8):
        """Log an observation for future learning."""
        entry = {
            'type': 'observation',
            'timestamp': datetime.now().isoformat(),
            'category': category,  # BRAIN_RULE, NURSERY_RULE, MARKET_PATTERN, etc.
            'observation': observation,
            'confidence': confidence,
        }
        self._append(entry)
        print(f"[ROCKY LOG] Observation logged: {category}")
    
    def log_promotion(self, baby_id, baby_stats, reasoning):
        """Log when a baby gets promoted."""
        entry = {
            'type': 'promotion',
            'timestamp': datetime.now().isoformat(),
            'baby_id': baby_id,
            'baby_stats': baby_stats,
            'reasoning': reasoning,
        }
        self._append(entry)
    
    def log_performance_comparison(self, arena_pnl, best_baby_pnl, improvement):
        """Log performance vs arena."""
        entry = {
            'type': 'performance_comparison',
            'timestamp': datetime.now().isoformat(),
            'arena_pnl': arena_pnl,
            'best_baby_pnl': best_baby_pnl,
            'improvement_vs_arena': improvement,
        }
        self._append(entry)
    
    def _append(self, entry):
        """Append entry to JSONL log."""
        try:
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(entry) + '\n')
        except Exception as e:
            print(f"[ROCKY LOG ERROR] {e}")
    
    def get_all_entries(self):
        """Get all logged entries."""
        entries = []
        try:
            with open(self.log_file, 'r') as f:
                for line in f:
                    if line.strip():
                        entries.append(json.loads(line))
        except FileNotFoundError:
            pass
        return entries
    
    def get_calibration_history(self):
        """Get all calibration decisions made."""
        entries = self.get_all_entries()
        return [e for e in entries if e['type'] == 'calibration']
    
    def generate_playbook(self):
        """Generate a human-readable playbook from observations."""
        entries = self.get_all_entries()
        observations = [e for e in entries if e['type'] == 'observation']
        
        playbook = {
            'generated_at': datetime.now().isoformat(),
            'total_observations': len(observations),
            'by_category': {},
        }
        
        for obs in observations:
            cat = obs['category']
            if cat not in playbook['by_category']:
                playbook['by_category'][cat] = []
            playbook['by_category'][cat].append(obs['observation'])
        
        return playbook


# Global instance
rocky_log = RockyOperatorLog()


def setup_rocky_log_endpoints(app):
    """Wire Rocky log endpoints into Flask."""
    from flask import jsonify
    
    @app.route('/api/rocky/log/entries', methods=['GET'])
    def get_log_entries():
        """Get all logged entries."""
        entries = rocky_log.get_all_entries()
        return jsonify({'entries': entries, 'count': len(entries)}), 200
    
    @app.route('/api/rocky/log/calibrations', methods=['GET'])
    def get_calibration_history():
        """Get calibration history."""
        cals = rocky_log.get_calibration_history()
        return jsonify({'calibrations': cals, 'count': len(cals)}), 200
    
    @app.route('/api/rocky/log/playbook', methods=['GET'])
    def get_playbook():
        """Get generated playbook."""
        playbook = rocky_log.generate_playbook()
        return jsonify(playbook), 200
    
    print("[ROCKY LOG] ✓ Endpoints wired")
