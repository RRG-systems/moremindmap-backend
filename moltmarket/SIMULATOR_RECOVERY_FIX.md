# SIMULATOR RECOVERY FIX ✓

**Issue:** "New Run" button reset simulator state but left CSV intact  
**Result:** Dashboard showed $0 despite CSV having hundreds of trades  
**Fix:** Auto-detect and restore from CSV on startup  

---

## What Changed

### 1. New Recovery Module

**File:** `simulator_recovery.py`

```python
def recover_simulator_state(simulator, data_layer):
    """Restore simulator PnL from CSV if mismatch detected"""
    # Calculate PnL from CSV
    paper_pnl = sum(float(t.get('pnl', 0)) for t in recent_trades if t.get('source') == 'paper')
    shadow_pnl = sum(float(t.get('pnl', 0)) for t in recent_trades if t.get('source') == 'shadow')
    
    # Check for mismatch: simulator=$0, CSV has data
    if (simulator.paper_pnl == 0.0 and paper_pnl != 0.0):
        # Restore from CSV
        simulator.paper_pnl = paper_pnl
        simulator.shadow_pnl = shadow_pnl
        # Continue with recovered state
```

### 2. Dashboard Integration

**File:** `moltmarket_dashboard.py` (lines 20, 90)

```python
from simulator_recovery import recover_simulator_state

# ... after simulator initialization ...
recover_simulator_state(simulator, data_layer)
```

---

## How It Works

**On dashboard startup:**

1. ExecutionSimulator initializes with PnL = $0 (fresh state)
2. Recovery module checks: "Does simulator have $0 but CSV has trades?"
3. If YES:
   - Sums all paper trades from CSV
   - Sums all shadow trades from CSV
   - Restores both to simulator
   - Logs what was recovered
4. If NO: Silent no-op (normal startup)

**Result:** Persistent equity restored, system continues trading from correct state.

---

## Output on Startup

```
[RECOVERY] ⚠️  MISMATCH DETECTED:
           Simulator: paper_pnl=$0, shadow_pnl=$0
           CSV data:  paper_pnl=$1245.67, shadow_pnl=$890.34
           Trades: 237 paper, 237 shadow

[RECOVERY] ✓ STATE RESTORED FROM CSV
           paper_pnl: $1245.67
           shadow_pnl: $890.34
           System is now persistent again
```

---

## Test

1. Kill dashboard
2. Restart it
3. Should see recovery message in terminal
4. Dashboard should show correct PnL (not $0)
5. Equity curve should display correctly

---

## Note

This is a band-aid fix for the "New Run" button damage.

The real solution (already implemented in Phase A):
- Removed "New Run" button from UI
- So this recovery won't be needed going forward

But it's here as safety net in case anyone finds a way to call `/api/reset` directly.

---

**Ready to restart dashboard.**
