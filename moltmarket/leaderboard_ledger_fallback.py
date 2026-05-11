#!/usr/bin/env python3
"""Add unified_ledger fallback to leaderboard endpoint"""

with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# Find the leaderboard building section and add ledger fallback
old_build = """                # Safe field extraction with defaults
                baby_entry = {
                    'variant_id': variant_id,
                    'id': baby.get('id', baby.get('variant_id', 'unknown')),
                    'name': baby.get('name', baby.get('variant_id', 'unknown')),
                    'generation': baby.get('generation', 0),
                    'mutation_type': baby.get('mutation_type', 'NONE'),
                    'trades': baby.get('total_trades', 0),
                    'shadow_pnl': baby.get('shadow_pnl', 0.0),
                    'paper_pnl': baby.get('paper_pnl', 0.0),
                    'win_rate': baby.get('win_rate', 0.0),
                    'flip_rate': baby.get('flip_rate', 0.0),
                    'degradation': baby.get('degradation_pct', 0.0),
                    'score': baby.get('score', 0.0),
                    'status': baby.get('status', 'active'),
                }"""

new_build = """                # Safe field extraction with defaults
                # Fallback to unified_ledger if baby object metrics are stale
                trades_count = baby.get('total_trades', 0)
                shadow_pnl_val = baby.get('shadow_pnl', 0.0)
                
                if unified_ledger and (trades_count == 0 or shadow_pnl_val == 0.0):
                    ledger_metrics = unified_ledger.get_trader_metrics(variant_id)
                    if ledger_metrics:
                        trades_count = ledger_metrics.get('trade_count', trades_count)
                        shadow_pnl_val = ledger_metrics.get('shadow_pnl', shadow_pnl_val)
                
                baby_entry = {
                    'variant_id': variant_id,
                    'id': baby.get('id', baby.get('variant_id', 'unknown')),
                    'name': baby.get('name', baby.get('variant_id', 'unknown')),
                    'generation': baby.get('generation', 0),
                    'mutation_type': baby.get('mutation_type', 'NONE'),
                    'trades': trades_count,
                    'shadow_pnl': shadow_pnl_val,
                    'paper_pnl': baby.get('paper_pnl', 0.0),
                    'win_rate': baby.get('win_rate', 0.0),
                    'flip_rate': baby.get('flip_rate', 0.0),
                    'degradation': baby.get('degradation_pct', 0.0),
                    'score': baby.get('score', 0.0),
                    'status': baby.get('status', 'active'),
                }"""

content = content.replace(old_build, new_build)

with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("✓ Added ledger fallback to leaderboard")
