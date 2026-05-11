# TECHNICAL BREAKDOWN — What's Wrong & Why (For Architect Review)

**Date:** Sun Apr 26, 2026 20:38 MST  
**Session:** 7h 44m  
**Status:** 80% complete, 3 known bugs, foundation solid

---

## The Three Problems We Hit Today

### Problem 1: FEED MISMATCH (FIXED ✅)

**What Was Wrong:**
Arena and Nursery traded through **two completely separate execution pipelines**.

**Arena Path:**
```
simulator.step()
  → _generate_signal()
    → _execute_paper() [internal tracking]
    → _execute_shadow() [internal tracking]
    → self.paper_pnl += X
    → self.shadow_pnl += Y
```

**Nursery Path:**
```
execute_baby_variant(baby)
  → unified_executor.execute_signal(source='baby', trader_id=baby_id, signal)
    → unified_ledger.add_trade(trader_id, pnl, ...)
    → leaderboard reads from unified_ledger
```

**Consequence:**
- Promoted baby's strategy DNA → Arena
- But Arena still executed its own internal logic
- Ledger never saw Arena trades
- Promoting a baby had **zero effect on Arena execution**

**The Fix:**
Modified `dashboard_execution.py._generate_signal()` (lines 163-210):
```python
# OLD: Internal execution (isolated)
self._execute_paper(asset, signal, side, entry_price, brain_state)
self._execute_shadow(asset, signal, side, entry_price, brain_state)

# NEW: Unified executor (same as Nursery)
trade = self.unified_executor.execute_signal(
    source='arena',
    trader_id=promoted_baby_id,
    signal={'asset': asset, 'side': side, ...}
)
```

**Result:** Both Arena and Nursery now log to unified_ledger with trader_id → same feed, same ledger ✅

---

### Problem 2: TRACKING SYSTEM MISMATCH (FIXED ✅)

**What Was Wrong:**
Three tracking systems grew independently without coordination:

```
evolution_engine.babies[]
    │ (spawned babies live here)
    │
    ├─→ Leaderboard reads: "which babies have trades?"
    │                       (queries unified_ledger by trader_id)
    │
    ├─→ Promotion reads: "find this baby in evolution_engine.babies"
    │                    (searches local list)
    │
    └─→ unified_ledger
                │ (all trades with trader_id logged here)
```

**The Mismatch:**
- Nursery babies spawn → added to `evolution_engine.babies`
- On first trade → `unified_ledger` records it with `trader_id=baby_id`
- **But:** Baby object never transferred to persistent registry
- **Result:** Leaderboard sees babies in ledger, promotion can't find them

**Example Timeline:**
1. T=0: Spawn baby_005 → added to evolution_engine.babies
2. T=2: Baby trades → logged to unified_ledger as trader_id='baby_005'
3. T=4: Leaderboard queries unified_ledger → sees baby_005, +$50 PnL
4. T=6: User clicks "promote baby_005"
5. T=6.5: Promotion searches evolution_engine.babies → **NOT FOUND** (was cleared after previous promotion)
6. **ERROR:** "variant not found"

**The Architecture We Built (Three Layers):**

```
┌─────────────────────────────────────────────────────────────┐
│ SOURCE OF TRUTH LAYER (Persistent, Durable)                │
├─────────────────────────────────────────────────────────────┤
│ baby_registry.jsonl (IDENTITY)                              │
│   → variant_id, parent_id, generation, dna, status, dates   │
│                                                              │
│ unified_ledger (PERFORMANCE)                                │
│   → All trades with trader_id, PnL, win_rate, etc          │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ CONSISTENCY LAYER (Per-Cycle Snapshot)                      │
├─────────────────────────────────────────────────────────────┤
│ _ledger_cache (in dashboard_state)                          │
│   → Snapshot of ALL baby metrics from unified_ledger        │
│   → Both leaderboard & promotion read from same snapshot    │
│   → Refreshed every 2 seconds (metrics cycle)               │
└─────────────────────────────────────────────────────────────┘
                             ↓
┌─────────────────────────────────────────────────────────────┐
│ RUNTIME LAYER (Temporary, Clearable)                        │
├─────────────────────────────────────────────────────────────┤
│ evolution_engine.babies[]                                   │
│   → Active babies currently executing in Nursery            │
│   → Cleared on promotion, respawned from new parent         │
│   → Can be rebuilt from registry + ledger without loss      │
└─────────────────────────────────────────────────────────────┘
```

**Why This Works:**
- **Single source of truth per layer**
- **No sync loops** (was the Option B trap)
- **Consistent reads** (cache guarantees both endpoints see same data)
- **Recoverable** (if runtime layer clears, rebuild from persistent layers)

**Implementation:**
1. Added `baby_registry.py` (150 lines) with JSONL persistence
2. Added `sync_registry_with_evolution_engine()` at startup
3. Added `_ledger_cache` building in `update_metrics()` (every 2 sec)
4. Modified promotion to read from cache instead of evolution_engine.babies

---

### Problem 3: BRAIN STATE OVERRIDE BUG (PARTIALLY FIXED ⚠️)

**What's Wrong:**
Promotion sets `brain_state='CALIBRATION'` but metrics evaluation immediately overrides it to `FLAT`.

**The Override Logic:**
```python
# In update_metrics() line 635
if not dashboard_state.get('trading_enabled', False):
    dashboard_state['brain_state'] = 'FLAT'  # ← ALWAYS resets to FLAT
    print(f"[BRAIN] Trading disabled, state=FLAT")
```

**Why It Fails:**
1. Promotion sets `trading_enabled=True` and `brain_state='CALIBRATION'`
2. Metrics update runs 2 seconds later
3. If `trading_enabled` somehow becomes False, FLAT override fires
4. **Result:** BRAIN stuck on FLAT, Arena doesn't trade

**Current Fix (Partial):**
Added protection (line 638):
```python
if not dashboard_state.get('trading_enabled', False):
    if dashboard_state.get('brain_mode') != 'CALIBRATION':  # ← NEW CHECK
        dashboard_state['brain_state'] = 'FLAT'
```

**Why It's Still Fragile:**
- Doesn't address WHY `trading_enabled` resets
- CALIBRATION mode check is implicit (not explicit state machine)
- Could still fail if promotion doesn't set `trading_enabled` correctly

**Better Fix (Tomorrow):**
1. **Root cause:** Find where `trading_enabled` resets to False
2. **State machine:** Build explicit BRAIN state transitions:
   ```python
   BRAIN_STATES = {
       'FLAT': {'can_transition_to': ['CALIBRATION', 'NORMAL']},
       'CALIBRATION': {'can_transition_to': ['AGGRESSIVE', 'MODERATE', 'CONSERVATIVE', 'STOP'], 'protected': True},
       'AGGRESSIVE': {'can_transition_to': ['MODERATE', 'CONSERVATIVE', 'STOP']},
       ...
   }
   ```
3. **Test:** Run promotion → verify BRAIN stays CALIBRATION for 60 seconds

---

## The Respawn Bug (LOW PRIORITY)

**What's Wrong:**
After promotion, only 1 baby spawns instead of 10.

**Expected:**
```python
evolution_engine.babies = []                    # Clear old
evolution_engine.spawn_baby_variants(count=10)  # Spawn 10 new
assert len(evolution_engine.babies) == 10       # ✓
```

**Actual:**
```python
assert len(evolution_engine.babies) == 1        # ✗ Only 1!
```

**Likely Cause:**
Exception in `spawn_baby_variants()` loop (line 304 in evolution_engine.py) stops early. First baby (i=0, CANONICAL) succeeds, then mutation loop crashes on i=1.

**Where to Check:**
```python
for i in range(count):  # Should loop 10 times
    baby = deepcopy(parent_strategy)
    
    if i == 0:
        # First baby (no mutation) — likely succeeds
        mutated_baby = baby
    else:
        # Babies 1-9 (mutations) — where it probably fails
        mutation_dim = mutation_dimensions[(i-1) % len(mutation_dimensions)]
        mutated_baby = self.mutate_one_dimension(...)  # ← EXCEPTION HERE?
    
    # If exception happens, loop breaks, only 1 baby added
```

**Fix (20 min):**
1. Wrap loop in try/except with detailed logging
2. Check if `parent_strategy` has required fields (`parameters`, `id`, etc.)
3. Verify `mutate_one_dimension()` doesn't crash on promoted baby DNA

---

## Why We Degraded from Last Night

**Last Night (Apr 25):**
- Leaderboard read from `evolution_engine.babies` (spawned list)
- Promotion read from `evolution_engine.babies` (spawned list)
- **Same source** → no mismatch ✓

**Today (Apr 26 — Morning):**
- Fixed feed sync (Arena uses unified_executor now) ✓
- But promoted babies still in evolution_engine.babies... until they got retired

**Today (Apr 26 — Afternoon):**
- Architect decision: Move to three-layer model
- Leaderboard now reads from unified_ledger (authoritative for trades)
- Promotion still reads from evolution_engine.babies (but babies not there after respawn)
- **Timing mismatch:** Leaderboard sees babies at T, promotion sees different set at T+ΔT

**Key Lesson:**
When refactoring multi-system coordination:
- **Logical consistency** ≠ **Temporal consistency**
- Ledger cache solved logical (same source), but timing still matters
- Need explicit sync points or state snapshots

---

## What's Working Well

✅ **Feed is unified** — Arena and Nursery both use unified_executor and unified_ledger  
✅ **Registry model is sound** — Three-layer separation is clean and recoverable  
✅ **Ledger cache works** — Both endpoints now read same metrics snapshot  
✅ **Calibration logic is correct** — PnL delta driving BRAIN state transitions properly  
✅ **Simulator ID visibility** — Great diagnostic tool (proves same feed)  

---

## What Needs Work

⚠️ **Respawn count** — Why only 1 baby spawns (exception in loop?)  
⚠️ **BRAIN state fragility** — `trading_enabled` override needs proper state machine  
⚠️ **Timing resilience** — Cache refresh tied to metrics cycle, could desync  
❌ **Test coverage** — Zero tests (should add before live trading)  

---

## Tomorrow's Priority Order

1. **Debug respawn** (20 min) — Add logging, find exception, fix
2. **Fix BRAIN state machine** (30 min) — Explicit transitions, no magic overrides
3. **Validate full cycle** (30 min) — Spawn → trade → promote → respawn → execute → calibrate
4. **Live trading test** (1-2h) — Run 5 cycles, monitor PnL consistency
5. **Add tests** (1h) — Regression coverage for all 3 problems

---

## Architect Questions for Review

1. **Three-layer model:** Is this the right level of abstraction, or should we collapse back to two?
2. **State machine:** Should BRAIN be extracted to separate class, or is inline OK?
3. **Cache coherence:** Should cache refresh be event-driven instead of cycle-tied?
4. **Respawn exception:** Any hypothesis on what breaks in mutation loop?
5. **Test strategy:** Before live money, what test coverage do you want?

---

**Confidence Level:** 85% (foundation is solid, 3 bugs are fixable, no architectural flaws found)

**Ready for:** Architect review, bug fixes, live trading tests starting tomorrow morning
