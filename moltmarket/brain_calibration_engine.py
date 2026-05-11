"""
BRAIN Calibration Engine — Real-time BRAIN tuning via style selection.

When a baby gets promoted:
1. Analyze performance signature (win rate, sign flips, edge strength)
2. Recommend calibration style (Conservative/Moderate/Aggressive)
3. Apply settings instantly to BRAIN config
4. New babies spawn from tuned parent

Three modes:
- CONSERVATIVE: Lower risk, fewer trades, tight exits
- MODERATE: Balanced, steady edge, normal execution
- AGGRESSIVE: High conviction, larger positions, more trades
"""

import json
from pathlib import Path
from datetime import datetime


class BrainCalibrationEngine:
    """Apply BRAIN calibrations based on style."""
    
    def __init__(self, brain_config_file=None):
        self.brain_config_file = brain_config_file or str(
            Path.home() / '.openclaw' / 'workspace' / 'moltmarket' / 'brain_config.json'
        )
        self.calibrations = {
            'CONSERVATIVE': {
                'sign_flip_threshold': 0.30,     # High threshold = fewer trades
                'entry_threshold': 0.05,         # Loose entries
                'exit_threshold': 0.03,          # Conservative exits
                'position_size': 0.5,            # Small bets
                'enforcement': 'THROTTLE',       # Rate limit execution
                'max_concurrent_trades': 3,
                'description': 'Low risk, high conviction only'
            },
            'MODERATE': {
                'sign_flip_threshold': 0.20,     # Medium threshold
                'entry_threshold': 0.03,         # Normal entries
                'exit_threshold': 0.015,         # Normal exits
                'position_size': 1.0,            # Normal bets
                'enforcement': 'FLAT',           # Normal execution
                'max_concurrent_trades': 8,
                'description': 'Balanced risk/reward'
            },
            'AGGRESSIVE': {
                'sign_flip_threshold': 0.10,     # Low threshold = more trades
                'entry_threshold': 0.01,         # Tight entries
                'exit_threshold': 0.005,         # Quick exits
                'position_size': 1.5,            # Large bets
                'enforcement': 'FULL',           # Full execution
                'max_concurrent_trades': 15,
                'description': 'High conviction, rapid execution'
            }
        }
    
    def calibrate(self, style, baby_stats=None):
        """Apply calibration and return config."""
        style = style.upper()
        
        if style not in self.calibrations:
            return {'status': 'error', 'message': f'Unknown style: {style}'}
        
        config = self.calibrations[style].copy()
        config['style'] = style
        config['calibrated_at'] = datetime.now().isoformat()
        
        # Save to BRAIN config
        self._save_config(config)
        
        return {
            'status': 'success',
            'style': style,
            'config': config,
            'message': f'BRAIN calibrated to {style}'
        }
    
    def _save_config(self, config):
        """Save calibration to BRAIN config file."""
        try:
            # Try to preserve existing config and merge
            existing = {}
            if Path(self.brain_config_file).exists():
                with open(self.brain_config_file, 'r') as f:
                    existing = json.load(f)
            
            # Merge new calibration
            existing.update(config)
            
            with open(self.brain_config_file, 'w') as f:
                json.dump(existing, f, indent=2)
            
            print(f"[BRAIN CALIBRATION] ✓ Saved {config['style']} to {self.brain_config_file}")
        except Exception as e:
            print(f"[BRAIN CALIBRATION] ERROR saving config: {e}")
    
    def get_recommendation(self, baby_stats):
        """Recommend calibration based on baby performance."""
        if not baby_stats:
            return 'MODERATE'  # Default safe choice
        
        win_rate = baby_stats.get('win_rate', 50)
        sign_flip_rate = baby_stats.get('flip_rate', 50)
        trades = baby_stats.get('trades', 0)
        shadow_pnl = baby_stats.get('shadow_pnl', 0)
        
        # Decision logic
        if win_rate > 55 and trades > 30:
            # Strong performer, high conviction
            return 'AGGRESSIVE'
        elif win_rate > 52 and sign_flip_rate < 40:
            # Good performer, stable
            return 'MODERATE'
        else:
            # Weak or uncertain
            return 'CONSERVATIVE'
    
    def get_all_calibrations(self):
        """Return all available calibrations."""
        return self.calibrations


# Global instance
calibration_engine = BrainCalibrationEngine()


def setup_brain_calibration_endpoint(app):
    """Wire calibration endpoint into Flask."""
    from flask import jsonify, request
    
    @app.route('/api/brain/calibrate', methods=['POST'])
    def brain_calibrate():
        """Calibrate BRAIN to a style (Conservative/Moderate/Aggressive)."""
        try:
            data = request.get_json()
            style = data.get('style', 'MODERATE').upper()
            baby_stats = data.get('baby_stats')
            
            result = calibration_engine.calibrate(style, baby_stats)
            
            if result['status'] == 'success':
                return jsonify(result), 200
            else:
                return jsonify(result), 400
        
        except Exception as e:
            print(f"[BRAIN CALIBRATE ERROR] {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/brain/calibrations', methods=['GET'])
    def brain_get_calibrations():
        """Get all available calibrations."""
        cals = calibration_engine.get_all_calibrations()
        return jsonify({'calibrations': cals}), 200
    
    @app.route('/api/brain/recommend', methods=['POST'])
    def brain_recommend():
        """Get recommendation based on baby stats."""
        try:
            data = request.get_json()
            baby_stats = data.get('stats')
            
            recommendation = calibration_engine.get_recommendation(baby_stats)
            
            return jsonify({
                'status': 'ok',
                'recommended_style': recommendation,
                'details': calibration_engine.calibrations[recommendation]
            }), 200
        
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    print("[BRAIN CALIBRATION] ✓ Endpoints wired")
