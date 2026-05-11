"""
Arena Metrics Engine — Read parent strategy performance from unified ledger.

All trades (Arena + Babies) logged to research_trades.csv.
This engine reads Arena trades (source='paper' or 'shadow') and computes metrics.
"""

import csv
from pathlib import Path
from collections import defaultdict
from datetime import datetime


class ArenaMetricsEngine:
    """Compute Arena (parent strategy) metrics from trade ledger."""
    
    def __init__(self, trades_file=None):
        self.trades_file = trades_file or str(
            Path.home() / '.openclaw' / 'workspace' / 'moltmarket' / 'research_trades.csv'
        )
    
    def get_arena_metrics(self):
        """Compute all Arena metrics from ledger."""
        trades = self._read_trades()
        
        if not trades:
            return {
                'status': 'no_trades',
                'strategy_name': 'Baseline Mean Reversion',
                'trades': 0,
                'win_rate': 0.0,
                'pnl': 0.0,
                'shadow_pnl': 0.0,
                'paper_pnl': 0.0,
                'avg_pnl_per_trade': 0.0,
                'best_trade': 0.0,
                'worst_trade': 0.0,
                'win_count': 0,
                'loss_count': 0,
                'breakeven_count': 0,
            }
        
        # Separate shadow vs paper
        shadow_trades = [t for t in trades if t.get('source') == 'shadow']
        paper_trades = [t for t in trades if t.get('source') == 'paper']
        
        # Compute metrics
        shadow_pnl = sum(float(t.get('pnl', 0)) for t in shadow_trades)
        paper_pnl = sum(float(t.get('pnl', 0)) for t in paper_trades)
        total_pnl = shadow_pnl + paper_pnl
        
        # Win rate (all trades)
        wins = sum(1 for t in trades if float(t.get('pnl', 0)) > 0)
        losses = sum(1 for t in trades if float(t.get('pnl', 0)) < 0)
        breakeven = sum(1 for t in trades if float(t.get('pnl', 0)) == 0)
        
        win_rate = (wins / len(trades) * 100) if trades else 0
        
        # Best/worst
        pnls = [float(t.get('pnl', 0)) for t in trades]
        best_trade = max(pnls) if pnls else 0
        worst_trade = min(pnls) if pnls else 0
        avg_pnl = sum(pnls) / len(pnls) if pnls else 0
        
        return {
            'status': 'ok',
            'strategy_name': 'Baseline Mean Reversion',
            'trades': len(trades),
            'win_rate': round(win_rate, 2),
            'pnl': round(total_pnl, 2),
            'shadow_pnl': round(shadow_pnl, 2),
            'paper_pnl': round(paper_pnl, 2),
            'avg_pnl_per_trade': round(avg_pnl, 2),
            'best_trade': round(best_trade, 2),
            'worst_trade': round(worst_trade, 2),
            'win_count': wins,
            'loss_count': losses,
            'breakeven_count': breakeven,
            'timestamp': datetime.now().isoformat(),
        }
    
    def _read_trades(self):
        """Read all trades from CSV."""
        trades = []
        try:
            with open(self.trades_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Skip separators
                    if row.get('signal') == 'RUN_SEPARATOR':
                        continue
                    # Skip rows with missing PnL
                    if not row.get('pnl') or str(row.get('pnl', '')).strip() == '':
                        continue
                    trades.append(row)
        except FileNotFoundError:
            pass
        
        return trades
    
    def get_arena_vs_babies(self):
        """Compare Arena performance vs Nursery babies."""
        arena_metrics = self.get_arena_metrics()
        
        # Get baby metrics (requires nursery endpoint)
        # For now, just return Arena metrics
        return {
            'arena': arena_metrics,
            'comparison': {
                'arena_pnl': arena_metrics['pnl'],
                'arena_win_rate': arena_metrics['win_rate'],
                'arena_trades': arena_metrics['trades'],
            }
        }


# Global instance
arena_engine = ArenaMetricsEngine()


def setup_arena_metrics_endpoint(app):
    """Wire Arena metrics endpoints into Flask."""
    from flask import jsonify
    
    @app.route('/api/arena/metrics', methods=['GET'])
    def arena_metrics():
        """Get Arena (parent strategy) metrics."""
        try:
            metrics = arena_engine.get_arena_metrics()
            return jsonify(metrics), 200
        except Exception as e:
            print(f"[ARENA METRICS ERROR] {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    @app.route('/api/arena/vs-babies', methods=['GET'])
    def arena_vs_babies():
        """Compare Arena vs Nursery babies."""
        try:
            comparison = arena_engine.get_arena_vs_babies()
            return jsonify(comparison), 200
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500
    
    print("[ARENA METRICS] ✓ Endpoints wired")
