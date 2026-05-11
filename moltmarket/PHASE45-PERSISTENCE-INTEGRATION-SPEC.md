# Phase 4.5 Persistence Integration — FINAL LOCK
## Single Source of Truth + Safe State Recovery

**Status:** IN PROGRESS
**Last Updated:** 2026-04-19 18:13 MST

---

## ARCHITECTURE LOCK

```
DATABASE (bots table)
    ↓
    └─ Authoritative bot state
    └─ Parent-child relationships
    └─ Execution history

money_state.json
    ↓
    └─ Authoritative capital state
    └─ active_bot_id
    └─ allocation %
    └─ risk_state (STOP/THROTTLE/NORMAL)

evolution_engine (runtime)
    ↓
    └─ Hydrates from both on startup
    └─ Never writes directly
    └─ Always syncs back to disk
```

---

## PART 1 — INITIALIZATION (ON STARTUP)

**File:** `moltmarket_dashboard.py` → `initialize()` function

**Sequence:**

```python
def initialize():
    global evolution_engine, nursery, molt_ui, dashboard_state
    
    # STEP 1: Load money state from disk
    money_persistence = MoneyStatePersistence()
    money_state_on_disk = money_persistence.get_state()
    
    # STEP 2: Restore to dashboard_state
    dashboard_state['active_bot_id'] = money_state_on_disk.get('active_bot_id')
    dashboard_state['active_bot_allocation'] = money_state_on_disk.get('allocations', {}).get(
        money_state_on_disk.get('active_bot_id'), 0
    )
    dashboard_state['risk_state'] = money_state_on_disk.get('risk_state', 'NORMAL')
    
    # STEP 3: Hydrate evolution_engine from database
    evolution_engine.hydrate_from_database()
    
    # STEP 4: Validate consistency
    if not validate_state_consistency():
        print("[INIT] STATE INCONSISTENCY DETECTED — SYSTEM FLAT")
        dashboard_state['active_bot_id'] = None
        dashboard_state['active_bot_allocation'] = 0
        return False
    
    return True
```

**Validation:**
- active_bot_id exists in bots table
- allocation matches money_state.json
- hypothesis links are valid
- If ANY fail → set FLAT (no trading)

---

## PART 2 — SPAWN INTEGRATION

**File:** `variant_nursery.py` → `spawn_babies()` + database transaction

**Sequence:**

```python
def spawn_babies(self, run_id, count=10):
    parent = self.evolution_engine.current_parent
    parent_id = parent['id']
    
    # CRITICAL: Clear ONLY this parent's children
    # (Don't wipe full history)
    self._clear_previous_spawn(parent_id)
    
    # Spawn in memory
    babies = self.evolution_engine.spawn_baby_variants(count=count)
    
    # ATOMIC: Write all to database or fail all
    try:
        self._persist_babies_to_database(babies)
        print(f"[SPAWN] {len(babies)} persisted to database")
    except Exception as e:
        print(f"[SPAWN] DATABASE WRITE FAILED: {e}")
        print(f"[SPAWN] ROLLING BACK — no babies registered")
        self.babies_spawned = False
        return []
    
    self.babies_spawned = True
    return babies

def _clear_previous_spawn(self, parent_id):
    """Delete only babies from this parent (not full history)"""
    sql = "DELETE FROM bots WHERE parent_id = ?"
    cursor.execute(sql, [parent_id])
    print(f"[SPAWN] Cleared previous spawn set for {parent_id}")

def _persist_babies_to_database(self, babies):
    """Write all babies in transaction"""
    for baby in babies:
        sql = """
            INSERT INTO bots (bot_id, parent_id, generation, ...)
            VALUES (?, ?, ?, ...)
        """
        cursor.execute(sql, [...])
    connection.commit()  # All or nothing
```

---

## PART 3 — PROMOTION INTEGRATION

**File:** `moltmarket_dashboard.py` → `promote_baby()` function

**Sequence:**

```python
def promote_baby(variant_id):
    # ... validation ...
    
    # STEP 1: Promote in evolution engine
    promoted_parent = evolution_engine.promote_baby_to_parent(baby)
    
    # STEP 2: Update money_state immediately
    money_persistence = MoneyStatePersistence()
    money_persistence.register_bot(variant_id, promoted_parent.get('hypothesis_id'), 1.0)
    
    # STEP 3: Persist to disk (atomic)
    money_persistence.save_state()
    
    # STEP 4: Update dashboard_state
    dashboard_state['active_bot_id'] = variant_id
    dashboard_state['active_bot_allocation'] = 1.0
    dashboard_state['active_bot_hypothesis'] = promoted_parent.get('hypothesis_id')
    
    print(f"[PROMOTION] {variant_id} active + 1% allocation + persisted to disk")
    
    return {"status": "success", "active_bot": variant_id, "allocation": 1.0}
```

**Atomic Write:** If `money_persistence.save_state()` fails, promotion is rejected. No partial state.

---

## PART 4 — NEW RUN HANDLER (CRITICAL RULE)

**File:** `moltmarket_dashboard.py` → `/api/run/reset` or `/api/new_run`

**LOCKED BEHAVIOR:**

```python
@app.route('/api/new_run', methods=['POST'])
def new_run():
    """New Run resets metrics, NOT strategy state"""
    
    global dashboard_state, simulator
    
    # RESET ONLY (session-level):
    dashboard_state['run_pnl'] = 0.0
    dashboard_state['run_trades'] = 0
    dashboard_state['run_start_time'] = datetime.utcnow()
    simulator.reset_charts()  # Clear visuals
    
    # DO NOT RESET (strategy-level):
    # - active_bot_id
    # - active_bot_allocation
    # - evolution_engine.babies
    # - evolution_engine.current_parent
    # - hypothesis_links
    # - mutation_lineage
    # - bots table
    # - money_state.json
    
    print("[NEW_RUN] Metrics reset. Strategy state preserved.")
    print(f"[NEW_RUN] Active bot: {dashboard_state['active_bot_id']}")
    print(f"[NEW_RUN] Allocation: {dashboard_state['active_bot_allocation']}%")
    
    return jsonify({
        "status": "success",
        "message": "New run started",
        "active_bot": dashboard_state['active_bot_id'],
        "allocation": dashboard_state['active_bot_allocation']
    }), 200
```

**CRITICAL:** Do NOT delete THINK memory or bot history. Only clear session artifacts.

---

## PART 5 — VALIDATION TEST (REQUIRED)

**Test Sequence:**

```
1. START SERVER
   ✓ System hydrates from money_state.json
   ✓ evolution_engine loads babies from database
   ✓ State validation passes
   → ready for trading

2. SPAWN BABIES
   ✓ Old spawn set cleared (parent-specific)
   ✓ 11 new babies created in memory
   ✓ All 11 written to database atomically
   ✓ Database query shows all 11 bots

3. PROMOTE BABY
   ✓ Promoted bot marked as active
   ✓ money_state.json updated with active_bot_id + 1%
   ✓ dashboard_state reflects promotion
   ✓ API /api/money-state returns active bot + 1%

4. CLICK "NEW RUN"
   ✓ Metrics reset (PnL=0, trades=0)
   ✓ Active bot persists (NOT cleared)
   ✓ Allocation persists (NOT cleared)
   ✓ money_state.json unchanged

5. RESTART SERVER
   ✓ System loads money_state.json
   ✓ Same active_bot_id restored
   ✓ Same allocation restored
   ✓ evolution_engine has full baby history
   → Ready to spawn next generation
```

---

## FILES TO MODIFY

1. **moltmarket_dashboard.py**
   - `initialize()` — load + validate
   - `spawn_nursery()` — database sync
   - `promote_baby()` — atomic promotion
   - `/api/new_run` — reset metrics only

2. **money_state_persistence.py**
   - Atomic write validation
   - Consistency checks
   - Error recovery

3. **variant_nursery.py**
   - `spawn_babies()` — transaction wrapper
   - `_clear_previous_spawn()` — selective wipe
   - `_persist_babies_to_database()` — atomic insert

4. **evolution_engine.py**
   - `hydrate_from_database()` — load from bots table
   - Populate execution_states from historical trades

---

## FINAL RULE

**Memory and database must never diverge.**

- Persist immediately after mutation
- Restore accurately on startup
- Fail safely if inconsistent
- No shortcuts
- No silent corruption
- No hidden state

---

**Status:** SPEC LOCKED — BUILDING NOW
