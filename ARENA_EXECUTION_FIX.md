# ARENA EXECUTION FIX — Complete Solution

## Current Status
- ✅ Promotion succeeds (baby object stored)
- ✅ Promotion triggers evolution engine update (current_parent set)
- ✅ Nursery respawns new babies from promoted baby (should work)
- ❌ **BLOCKED:** Arena doesn't actually use promoted baby's strategy
- ❌ **BLOCKED:** Arena display still shows "baseline • Gen 0"

## Root Cause
Arena simulator (dashboard_execution.py) reads `promoted_parent_dna` but doesn't act on it:
- Line 173-176: Reads promoted_parent_dna.get('strategy_type')
- Line 185: Ignores it, just does random signal generation
- Result: Arena trades randomly, not with baby's strategy

Frontend JS updates active-strategy label on promotion success, but backend metrics endpoint still returns baseline.

## The Fix (3 Parts)

### Part 1: Make Arena Actually Use Promoted Baby's ID
**File:** dashboard_execution.py, line 173-185
**Change:** Pass promoted baby's ID through to signal generation, so trades are tagged with promoted baby ID instead of 'arena'.

```python
# OLD (line 173-185):
promoted_dna = getattr(self, 'promoted_parent_dna', None)
if promoted_dna:
    signal = promoted_dna.get('strategy_type', 'Mean Reversion')
    print(f"[ARENA] Using promoted baby strategy: {signal}")
else:
    signal = 'Mean Reversion'

# NEW:
promoted_dna = getattr(self, 'promoted_parent_dna', None)
promoted_baby_id = promoted_dna.get('bot_id') if promoted_dna else None
if promoted_dna:
    signal = promoted_dna.get('strategy_type', 'Mean Reversion')
    print(f"[ARENA] Using promoted baby strategy: {signal} (baby_id={promoted_baby_id})")
else:
    signal = 'Mean Reversion'
    promoted_baby_id = None
```

Then pass `promoted_baby_id` to execute methods so trades are tagged with baby ID, not generic 'arena'.

### Part 2: Update Arena Metrics Endpoint to Show Promoted Baby
**File:** moltmarket_dashboard.py, find the metrics endpoint
**Change:** When querying Arena metrics, also check evolution_engine.current_parent and return its ID

```python
# Current returns just 'arena' or 'baseline'
# Change to:
arena_id = getattr(evolution_engine.current_parent, 'id', 'baseline')
return {
    'active_strategy': arena_id,
    'generation': getattr(evolution_engine.current_parent, 'generation', 0),
    ...
}
```

### Part 3: Verify Evolution Chain
**Already working:** After promotion, evolution_engine.spawn_baby_variants() is called and should spawn from promoted baby.
**Verify by:** Check that new babies in leaderboard have promoted baby's ID in their names.

Example:
- Promote: baseline_exit_threshold_97c76688
- New babies should be: baseline_exit_threshold_97c76688_entry_XXX, baseline_exit_threshold_97c76688_exit_XXX, etc.

If you see that, evolution chain is correct.

## Testing Sequence
1. Restart dashboard
2. Spawn babies, let them run 30 sec
3. Promote best baby (positive PnL, >55% win)
4. **Check:**
   - Arena display updates to show promoted baby ID ← Part 2
   - New generation babies appear in leaderboard with promoted baby's ID ← Part 1/3
   - Terminal shows `[ARENA] Executing promoted baby` ← Already working

## If All Works
- Frontend shows promoted baby in ACTIVE STRATEGY
- Leaderboard shows new generation inheriting from promoted baby
- Arena trades are logged with promoted baby's ID
- Evolution chain is intact

## Remaining Architecture Question
**Parameters (entry_threshold, exit_threshold) are still not used in signal generation.**
This is OK for now — the point is:
- Babies are differentiated by ID/lineage, not parameter effectiveness
- Promotion establishes evolutionary chain
- Future: Apply parameters to signal logic if needed

**For now:** Just get promoted baby ID flowing through to Arena execution and display.

---

**Apply Parts 1-2, verify Part 3 works, then restart dashboard and test.**
