# CRITICAL: Arena & Nursery Must Share Same Execution Feed

## The Problem (You Found It)

**Arena trades in one system, Nursery trades in another.**

- **Arena:** dashboard_execution.py `_execute_paper()` / `_execute_shadow()`
  - Internal paper_pnl, paper_trades counters
  - NOT logged to unified_ledger
  - NOT using unified_executor
  - Result: Isolated, private execution

- **Nursery:** execute_baby_variant()
  - Calls `unified_executor.execute_signal()`
  - Trades logged to unified_ledger with trader_id=baby_id
  - Leaderboard reads from unified_ledger
  - Result: All babies in same ledger

**Consequence:** Promoting a baby has ZERO effect on Arena because Arena doesn't know about the baby or the unified ledger.

---

## The Fix: One-Line Mental Model

**Make Arena use the same executor as Nursery.**

Instead of:
```python
self._execute_paper(asset, signal, side, entry_price)
self._execute_shadow(asset, signal, side, entry_price)
```

Do:
```python
unified_executor.execute_signal(
    source='arena',
    trader_id=evolution_engine.current_parent.get('id', 'baseline'),
    signal={'asset': asset, 'side': side, 'entry_price': entry_price, ...}
)
```

---

## Step-by-Step Fix

### 1. Modify dashboard_execution.py `_generate_signal()` (line 159)

**OLD:**
```python
def _generate_signal(self):
    # ... setup ...
    self._execute_paper(asset, signal, side, entry_price, brain_state)
    self._execute_shadow(asset, signal, side, entry_price, brain_state)
```

**NEW:**
```python
def _generate_signal(self):
    # ... setup ...
    # Get promoted baby ID (or 'baseline' if no promotion)
    promoted_dna = getattr(self, 'promoted_parent_dna', None)
    arena_trader_id = promoted_dna.get('bot_id', 'baseline') if promoted_dna else 'baseline'
    
    # Build signal for unified executor
    signal = {
        'asset': asset,
        'side': side,
        'entry_price': entry_price,
        'exit_price': exit_price,  # Get from _get_price(asset) again
        'size': 1.0,
    }
    
    # Execute through unified pipeline (same as Nursery babies)
    if self.unified_executor:
        trade = self.unified_executor.execute_signal(
            source='arena',
            trader_id=arena_trader_id,
            signal=signal
        )
        if trade:
            print(f"[ARENA] Trade logged to unified ledger: {arena_trader_id}")
    else:
        print(f"[ARENA ERROR] unified_executor is None")
```

### 2. Remove or deprecate `_execute_paper()` and `_execute_shadow()`

These methods are now obsolete. Delete them or mark as legacy.

### 3. Wire unified_executor into dashboard_execution.py

In moltmarket_dashboard.py, when creating the simulator:

```python
simulator = ExecutionSimulator(data_layer, brain_status_getter=get_current_brain_status)
simulator.unified_executor = unified_executor  # Wire it in
simulator.evolution_engine = evolution_engine  # For current_parent access
```

### 4. Test Sequence

1. Start dashboard
2. Spawn babies → Nursery trades logged to unified_ledger ✓
3. Promote baby → Baby becomes evolution_engine.current_parent
4. Wait 10 sec → Arena should now:
   - Call `unified_executor.execute_signal(source='arena', trader_id=promoted_baby_id)`
   - Trades appear in unified_ledger with trader_id=promoted_baby_id (not 'baseline')
   - Leaderboard shows promoted baby with Arena PnL included
5. Verify:
   - Same simulator (prices) ✓
   - Same executor ✓
   - Same ledger ✓
   - **Same feed** ✓

---

## Why This Matters

Right now:
- Nursery: "I traded BTC at $45,000"
- Arena: "I traded BTC at $45,020 (different internal price)"
- They're seeing different markets

After fix:
- Nursery: "I traded BTC at $45,000" (from simulator)
- Arena: "I traded BTC at $45,000" (from same simulator, same executor)
- **Same feed, same ledger, evolution works**

---

## Success Criteria

- ✅ Arena trades appear in unified_ledger with source='arena'
- ✅ When baby promoted, Arena trades are logged with trader_id=promoted_baby_id
- ✅ Leaderboard shows promoted baby with Arena PnL
- ✅ Nursery babies are still in leaderboard with their own PnL
- ✅ No internal _execute_paper/shadow tracking (all via unified executor)

---

## Critical Note

**This is THE blocker.** Until this is fixed, the entire evolution system is promoting babies that have been training in a different market than where they'll trade. 

On real money, this becomes:
- Nursery: Trades in simulated Coinbase
- Arena: Trades in real Coinbase
- Zero correlation between baby performance and real execution

Fix this first, everything else follows.
