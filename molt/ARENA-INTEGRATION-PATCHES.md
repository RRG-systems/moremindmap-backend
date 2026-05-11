# Arena Integration Patches
## Where to Wire Event Hooks into evolution_engine.py

This document shows exact locations where to add THINK Memory event hook calls.

---

## PATCH 1: Initialize Bridge on Startup

**Location:** `evolution_engine.py`, `EvolutionEngine.__init__()`

**Current code:**
```python
def __init__(self):
    """Initialize evolution engine with default Mean Reversion parent"""
    self.current_parent = self._create_default_parent()
    self.parent_strategy = self.current_parent
    self.babies = []
    self.execution_states = {}
    self.fitness_scores = {}
```

**Add after:**
```python
def __init__(self):
    """Initialize evolution engine with default Mean Reversion parent"""
    self.current_parent = self._create_default_parent()
    self.parent_strategy = self.current_parent
    self.babies = []
    self.execution_states = {}
    self.fitness_scores = {}
    
    # THINK Memory integration
    try:
        from arena_integration import init_arena_bridge
        self.arena_bridge = init_arena_bridge()
    except ImportError:
        print("[ARENA] THINK Memory bridge not available (optional)")
        self.arena_bridge = None
```

---

## PATCH 2: Hook Baby Spawn

**Location:** `evolution_engine.py`, `spawn_baby_variants()`, after babies are created

**Current code (around line 230):**
```python
mutated_baby['variant_id'] = variant_id
self.babies.append(mutated_baby)
self.execution_states[mutated_baby['variant_id']] = {
    'variant_id': variant_id,
    'trades': [],
    'scores': [],
    'last_evaluated': None,
}
```

**Add after the execution_states block:**
```python
            # THINK Memory: Record baby spawn
            if self.arena_bridge:
                self.arena_bridge.on_baby_spawned(
                    variant_id=variant_id,
                    mutated_dna=mutated_baby['parameters'],
                    parent_variant_id=parent_short,
                    generation=child_gen
                )
```

---

## PATCH 3: Hook Mutation Batch

**Location:** `evolution_engine.py`, `spawn_baby_variants()`, at END of method before return

**Current code (around line 250):**
```python
print(f"[EVOLUTION] Spawned {len(self.babies)} babies from parent ({parent_short})")
return self.babies
```

**Replace with:**
```python
print(f"[EVOLUTION] Spawned {len(self.babies)} babies from parent ({parent_short})")

# THINK Memory: Record mutation batch
if self.arena_bridge:
    mutation_id = f"mut_{uuid4().hex[:8]}"
    baby_ids = [b['variant_id'] for b in self.babies if b['generation'] == child_gen]
    mutated_dnas = [b['parameters'] for b in self.babies if b['generation'] == child_gen]
    
    self.arena_bridge.on_mutation_started(
        mutation_id=mutation_id,
        source_variant_id=parent_short,
        baby_variant_ids=baby_ids,
        mutation_dimension=mutation_dim,
        parent_dna=parent_strategy['parameters'],
        mutated_dna_list=mutated_dnas
    )

return self.babies
```

---

## PATCH 4: Hook Evaluation Complete

**Location:** Where evaluation metrics are computed (likely in dashboard or run loop)

**When you have:** trades, flip_rate, pnl, divergence, drawdown, survival for a variant

**Add:**
```python
# THINK Memory: Record evaluation
if hasattr(evolution_engine, 'arena_bridge') and evolution_engine.arena_bridge:
    evolution_engine.arena_bridge.on_variant_evaluated(
        variant_id=variant_id,
        trades=len(trades),
        flip_rate=trade_flips / len(trades) if trades else 0,
        pnl=total_pnl,
        divergence=divergence_metric,
        drawdown=max_drawdown,
        survival=survival_rate,
        trajectory=trajectory_status
    )
```

---

## PATCH 5: Hook Variant Promotion

**Location:** `evolution_engine.py`, `promote_baby_to_parent()`

**Current code (around line 100):**
```python
def promote_baby_to_parent(self, baby_variant):
    """PHASE 32.3: CRITICAL FIX - Update authoritative parent when baby is promoted"""
    print(f"[EVOLUTION] Promoting {baby_variant['variant_id']} to parent (Gen {baby_variant['generation']})")
    
    promoted_parent = deepcopy(baby_variant)
    promoted_parent['id'] = baby_variant['variant_id']
    promoted_parent['promoted_from'] = 'nursery'
    promoted_parent['promoted_at'] = datetime.utcnow().isoformat()
    promoted_parent['generation'] = baby_variant['generation']
    promoted_parent['previous_parent'] = self.current_parent
    
    self.current_parent = promoted_parent
    self.parent_strategy = promoted_parent
    
    print(f"[EVOLUTION] Parent updated: {promoted_parent['id']} • Gen {promoted_parent['generation']}")
    return promoted_parent
```

**Add after parent update:**
```python
    self.current_parent = promoted_parent
    self.parent_strategy = promoted_parent
    
    # THINK Memory: Record promotion decision
    if self.arena_bridge:
        self.arena_bridge.on_variant_promoted(
            variant_id=baby_variant['variant_id'],
            hypothesis_id=None,  # Use default
            trades=len(baby_variant.get('trades', [])),
            flip_rate=baby_variant.get('flip_rate', 0),
            pnl=baby_variant.get('shadow_pnl', 0),
            reason="Promoted by user from evaluation"
        )
    
    print(f"[EVOLUTION] Parent updated: {promoted_parent['id']} • Gen {promoted_parent['generation']}")
    return promoted_parent
```

---

## PATCH 6: Hook Variant Retirement

**Location:** Wherever variants are retired/killed

**When a variant is no longer being tested:**
```python
# THINK Memory: Record kill/retirement
if hasattr(evolution_engine, 'arena_bridge') and evolution_engine.arena_bridge:
    evolution_engine.arena_bridge.on_variant_killed(
        variant_id=variant_id,
        hypothesis_id=None,
        reason=f"Variant retired: {reason}"
    )
```

---

## Integration Checklist

- [ ] Import ArenaEventBridge in evolution_engine.py
- [ ] Add arena_bridge to __init__
- [ ] Add on_baby_spawned hook in spawn_baby_variants()
- [ ] Add on_mutation_started hook at end of spawn_baby_variants()
- [ ] Add on_variant_evaluated hook when metrics are computed
- [ ] Add on_variant_promoted hook in promote_baby_to_parent()
- [ ] Add on_variant_killed hook in retirement logic
- [ ] Test with real runs (see next section)

---

## Testing Integration

After integration, verify that real system data flows to THINK Memory:

```bash
# 1. Start a live run
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 dashboard_execution.py

# 2. In another terminal, query THINK Memory
cd /Users/rrg/.openclaw/workspace/molt
/opt/homebrew/bin/python3 -c "
import sqlite3
db = sqlite3.connect('think-memory.db')
db.row_factory = sqlite3.Row
cursor = db.cursor()

# Check bots
cursor.execute('SELECT COUNT(*) as cnt FROM bots')
print('Bots in THINK Memory:', cursor.fetchone()['cnt'])

# Check mutations
cursor.execute('SELECT COUNT(*) as cnt FROM mutations')
print('Mutations in THINK Memory:', cursor.fetchone()['cnt'])

# Check decisions
cursor.execute('SELECT COUNT(*) as cnt FROM decisions')
print('Decisions in THINK Memory:', cursor.fetchone()['cnt'])
"

# 3. Query Rocky's reasoning
cd /Users/rrg/.openclaw/workspace/molt
/opt/homebrew/bin/python3 -c "
from rocky_reasoning import rocky_quick_thought
# Get latest bot ID from THINK Memory, then ask Rocky
response = rocky_quick_thought('Should I promote this?', 'latest_bot_id')
print('Rocky says:', response)
"
```

---

## Files

- `arena_integration.py` — Integration bridge (ready to use)
- `ARENA-INTEGRATION-PATCHES.md` — This document
- Patches above show exact code locations

---

## Safety Notes

- All event hooks are **append-only**. No existing logic is modified.
- THINK Memory is **read-by-Rocky-only**. Arena doesn't depend on it.
- If THINK Memory is unavailable, Arena continues normally (optional feature).
- Errors in integration don't affect Arena execution.

---

## What Happens After Integration

1. **Arena runs normally** (nothing changes in execution)
2. **Event hooks capture state** into THINK Memory
3. **Rocky reads THINK Memory** to reason about decisions
4. **User queries Rocky** with bot IDs
5. **Rocky grounds answers in real system history**

Example query chain:
```
User: "Should I promote bot_v5?"
    ↓
Rocky queries THINK Memory:
    - Why does bot_v5 exist?
    - What mutations improved this hypothesis?
    - Has this hypothesis worked before?
    - Is current bot trajectory improving?
    ↓
Rocky answers: "YES: Decent sample, improving trajectory, 
                mutations on this hypothesis have worked. 
                Ready for capital. (confidence: high)"
```

---

**Status:** Ready for integration into live Arena.
