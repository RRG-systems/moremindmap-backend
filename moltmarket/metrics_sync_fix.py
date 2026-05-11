#!/usr/bin/env python3
"""Complete metrics sync fix for baby objects"""

with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# Replace the incomplete sync with complete one
old_sync = """                # SYNC: Update baby metrics from unified ledger
                metrics = unified_ledger.get_trader_metrics(baby_id)
                if metrics:
                    baby['total_trades'] = metrics.get('trade_count', 0)
                    baby['shadow_pnl'] = metrics.get('shadow_pnl', 0.0)
                    baby['paper_pnl'] = metrics.get('paper_pnl', 0.0)
                    baby['win_rate'] = metrics.get('win_rate', 0.0)
                    baby['flip_rate'] = metrics.get('flip_rate', 0.0)
                    print(f"[BABY SYNC] {baby_id}: trades={baby['total_trades']}, pnl=${baby['shadow_pnl']:.2f}")"""

new_sync = """                # SYNC: Update baby metrics from unified ledger
                if unified_ledger:
                    metrics = unified_ledger.get_trader_metrics(baby_id)
                    if metrics:
                        baby['total_trades'] = metrics.get('trade_count', 0)
                        baby['shadow_pnl'] = metrics.get('shadow_pnl', 0.0)
                        baby['paper_pnl'] = metrics.get('paper_pnl', 0.0)
                        baby['win_rate'] = metrics.get('win_rate', 0.0)
                        baby['flip_rate'] = metrics.get('flip_rate', 0.0)
                        baby['degradation_pct'] = metrics.get('degradation_pct', 0.0)
                        baby['score'] = metrics.get('score', 0.0)
                        print(f"[BABY SYNC] {baby_id}: trades={baby['total_trades']}, shadow_pnl=${baby['shadow_pnl']:.2f}, paper_pnl=${baby['paper_pnl']:.2f}, flip={baby['flip_rate']:.1f}%")"""

content = content.replace(old_sync, new_sync)

with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("✓ Expanded metrics sync")
