# TEMPORARY: Just the patch section to understand the sync

        if trade_result:
            print(f"[NURSERY BRIDGE] {baby_id}: executed trade")
            print(f"  Asset: {trade_result['asset']}, Side: {trade_result['side']}")
            print(f"  Paper PnL: {trade_result['paper_pnl']:.2f} bps | Shadow PnL: {trade_result['shadow_pnl']:.2f} bps")
            print(f"  Sign flip: {trade_result['sign_flip']}")
            
            # SYNC: Update evolution_engine.execution_states from nursery_bridge ledger
            ledger = nursery_bridge.get_baby_ledger(baby_id)
            if baby_id not in evolution_engine.execution_states:
                evolution_engine.execution_states[baby_id] = {
                    'variant_id': baby_id,
                    'trades': [],
                    'paper_pnl': 0.0,
                    'shadow_pnl': 0.0,
                    'paper_trade_count': 0,
                    'shadow_trade_count': 0,
                }
            
            # Sync from ledger
            state = evolution_engine.execution_states[baby_id]
            state['trades'] = ledger.get('trades', [])
            state['paper_pnl'] = ledger.get('paper_pnl', 0.0)
            state['shadow_pnl'] = ledger.get('shadow_pnl', 0.0)
            state['paper_trade_count'] = len([t for t in ledger.get('trades', []) if t.get('source') == 'paper'])
            state['shadow_trade_count'] = len([t for t in ledger.get('trades', []) if t.get('source') == 'shadow'])
        else:
            # No signal generated
            pass
