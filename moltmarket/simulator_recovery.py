#!/usr/bin/env python3
"""
RECOVERY: Restore simulator state from CSV if mismatch detected

Problem: "New Run" button reset simulator PnL to $0 but left CSV intact
Solution: On startup, detect mismatch and restore PnL from CSV

This ensures persistent equity after accidental resets.
"""

def recover_simulator_state(simulator, data_layer):
    """
    Restore simulator PnL from CSV if mismatch detected.
    
    Call this after simulator initialization but before trading loop starts.
    
    Returns: True if recovery happened, False otherwise
    """
    try:
        recent_trades = data_layer.get_recent_trades(limit=10000)
        if not recent_trades or len(recent_trades) == 0:
            return False
        
        # Calculate PnL from CSV
        paper_pnl = sum(float(t.get('pnl', 0)) for t in recent_trades if t.get('source') == 'paper')
        shadow_pnl = sum(float(t.get('pnl', 0)) for t in recent_trades if t.get('source') == 'shadow')
        paper_trades = len([t for t in recent_trades if t.get('source') == 'paper'])
        shadow_trades = len([t for t in recent_trades if t.get('source') == 'shadow'])
        
        # Check for mismatch
        if (simulator.paper_pnl == 0.0 and paper_pnl != 0.0) or (simulator.shadow_pnl == 0.0 and shadow_pnl != 0.0):
            print(f"\n[RECOVERY] ⚠️  MISMATCH DETECTED:")
            print(f"           Simulator: paper_pnl=$0, shadow_pnl=$0")
            print(f"           CSV data:  paper_pnl=${paper_pnl:.2f}, shadow_pnl=${shadow_pnl:.2f}")
            print(f"           Trades: {paper_trades} paper, {shadow_trades} shadow")
            
            # Restore from CSV
            simulator.paper_pnl = paper_pnl
            simulator.shadow_pnl = shadow_pnl
            simulator.paper_trades = paper_trades
            simulator.shadow_trades = shadow_trades
            
            print(f"\n[RECOVERY] ✓ STATE RESTORED FROM CSV")
            print(f"           paper_pnl: ${paper_pnl:.2f}")
            print(f"           shadow_pnl: ${shadow_pnl:.2f}")
            print(f"           System is now persistent again\n")
            return True
        
        return False
    
    except Exception as e:
        print(f"[RECOVERY] ✗ Error: {e}")
        return False
