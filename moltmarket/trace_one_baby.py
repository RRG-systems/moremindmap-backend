#!/usr/bin/env python3
"""Surgical trace for ONE baby through entire chain"""

with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# Add trace IMMEDIATELY after execute_signal call
old_trace1 = """            print(f"[TRACE BABY] execute_signal returned: {trade is not None}")
            
            if trade:
                print(f"[BABY] {baby_id}: trade | {trade.asset} {trade.side} | ${trade.pnl:.2f} ({trade.pnl_bps:.1f} bps)")
                
                # SYNC: Update baby metrics from unified ledger"""

new_trace1 = """            print(f"[TRACE BABY] execute_signal returned: {trade is not None}")
            
            if trade:
                print(f"[BABY] {baby_id}: trade | {trade.asset} {trade.side} | ${trade.pnl:.2f} ({trade.pnl_bps:.1f} bps)")
                
                # STEP 1: Log what executor gave us
                print(f"[CHAIN STEP 1] After execute_signal for {baby_id}:")
                print(f"  trade object exists: {trade is not None}")
                
                # STEP 2: Check unified_ledger immediately
                if unified_ledger:
                    ledger_metrics = unified_ledger.get_trader_metrics(baby_id)
                    if ledger_metrics:
                        print(f"[CHAIN STEP 2] Unified ledger metrics for {baby_id}:")
                        print(f"  trade_count: {ledger_metrics.get('trade_count', '?')}")
                        print(f"  shadow_pnl: {ledger_metrics.get('shadow_pnl', '?')}")
                        print(f"  paper_pnl: {ledger_metrics.get('paper_pnl', '?')}")
                        print(f"  flip_rate: {ledger_metrics.get('flip_rate', '?')}")
                    else:
                        print(f"[CHAIN STEP 2] NO metrics found in ledger for {baby_id}")
                else:
                    print(f"[CHAIN STEP 2] unified_ledger is None!")
                
                # SYNC: Update baby metrics from unified ledger"""

content = content.replace(old_trace1, new_trace1)

# Add trace AFTER sync
old_trace2 = """                        print(f"[BABY SYNC] {baby_id}: trades={baby['total_trades']}, shadow_pnl=${baby['shadow_pnl']:.2f}, paper_pnl=${baby['paper_pnl']:.2f}, flip={baby['flip_rate']:.1f}%")"""

new_trace2 = """                        print(f"[BABY SYNC] {baby_id}: trades={baby['total_trades']}, shadow_pnl=${baby['shadow_pnl']:.2f}, paper_pnl=${baby['paper_pnl']:.2f}, flip={baby['flip_rate']:.1f}%")
                        
                        # STEP 3: Log baby object after sync
                        print(f"[CHAIN STEP 3] Baby object after sync for {baby_id}:")
                        print(f"  baby['total_trades']: {baby.get('total_trades', '?')}")
                        print(f"  baby['shadow_pnl']: {baby.get('shadow_pnl', '?')}")
                        print(f"  baby['paper_pnl']: {baby.get('paper_pnl', '?')}")
                        print(f"  baby['flip_rate']: {baby.get('flip_rate', '?')}")
                        print(f"  baby['degradation_pct']: {baby.get('degradation_pct', '?')}")"""

content = content.replace(old_trace2, new_trace2)

# Add trace in leaderboard before JSON serialization
old_trace3 = """                baby_entry = {
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
                }
                leaderboard.append(baby_entry)"""

new_trace3 = """                baby_entry = {
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
                }
                
                # STEP 4: Log what we're putting in JSON for trace baby
                if 'baseline_holding_time_d41db9a4' in variant_id or 'baseline_holding_time_25248386' in variant_id:
                    print(f"[CHAIN STEP 4] Leaderboard entry for {variant_id}:")
                    print(f"  trades: {baby_entry['trades']}")
                    print(f"  shadow_pnl: {baby_entry['shadow_pnl']}")
                    print(f"  paper_pnl: {baby_entry['paper_pnl']}")
                    print(f"  flip_rate: {baby_entry['flip_rate']}")
                
                leaderboard.append(baby_entry)"""

content = content.replace(old_trace3, new_trace3)

with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("✓ Added surgical chain trace")
