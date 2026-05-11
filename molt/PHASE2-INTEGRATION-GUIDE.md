# Phase 2 Integration Guide
## Hypothesis Input + Event Hooks

This guide explains how to integrate Phase 2 into existing MOLTmarket code.

---

## What Was Built

### 1. hypothesis_engine.py
- `HypothesisEngine` — Create and manage hypotheses
- `HypothesisValidator` — Validate hypotheses for bot creation
- Functions for Rocky to help formalize hypotheses from user intent

### 2. event_hooks.py
- `THINKEventHook` — Connect Arena events to THINK Memory database
- 5 event types: bot spawn, mutation spawn, evaluation complete, mutation result, decision made
- Thin layer: no business logic, just database writes

### 3. test-phase2-flow.py
- End-to-end test: hypothesis → bot → mutation → evaluation → decision
- Demonstrates all 5 Rocky query patterns working
- Run to verify integration

---

## Integration Steps

### Step 1: Initialize THINK Memory Database

```bash
cd ~/.openclaw/workspace/molt
node init-think-memory.js
```

Output:
```
✓ THINK Memory database initialized
  Database: /Users/rrg/.openclaw/workspace/molt/think-memory.db
  Tables: hypotheses, bots, mutations, decisions
  Status: Ready for use
```

### Step 2: Run the Test

```bash
cd ~/.openclaw/workspace/molt
python3 test-phase2-flow.py
```

Expected output:
```
============================================================
PHASE 2 TEST: Hypothesis → Bot → Mutation → Evaluation → Decision
============================================================

STEP 1: Create Hypothesis
✓ Hypothesis created and verified

STEP 2: Spawn Initial Bot (Manual Creation)
✓ Bot spawned and verified

... (all steps pass)

============================================================
✓ PHASE 2 COMPLETE: All tests passed
============================================================
```

### Step 3: Wire Event Hooks into Evolution Engine

In `evolution_engine.py`, add imports:

```python
from hypothesis_engine import HypothesisEngine, HypothesisValidator
from event_hooks import THINKEventHook

# Initialize at module level
_think_hook = None

def init_think_hooks():
    global _think_hook
    _think_hook = THINKEventHook()
    _think_hook.connect()

def close_think_hooks():
    global _think_hook
    if _think_hook:
        _think_hook.close()
```

### Step 4: Add Hooks to Bot Spawn

In `evolution_engine.py`, at `spawn_baby_variants()`:

**BEFORE:**
```python
def spawn_baby_variants(self):
    # ... existing spawn logic ...
    baby = {
        'variant_id': baby_id,
        # ... existing fields ...
    }
    self.babies.append(baby)
```

**AFTER:**
```python
def spawn_baby_variants(self):
    # ... existing spawn logic ...
    baby = {
        'variant_id': baby_id,
        'hypothesis_id': hypothesis_id,  # ADD THIS
        # ... existing fields ...
    }
    self.babies.append(baby)
    
    # ADD THIS: Wire to THINK Memory
    if _think_hook:
        _think_hook.on_bot_spawned(
            bot_id=baby_id,
            hypothesis_id=hypothesis_id,
            creation_source='seed_agent',  # or 'manual', 'molt_feed'
            dna_json=baby['parameters'],
            parent_bot_id=parent_id,
            generation=baby['generation'],
            current_run_id=None
        )
```

### Step 5: Add Hook to Mutation Creation

In `mutation_engine.py`:

```python
# After mutation is created
mutation_id = f"mut_{uuid4().hex[:8]}"

if _think_hook:
    _think_hook.on_mutation_spawned(
        mutation_id=mutation_id,
        source_bot_id=parent_bot_id,
        resulting_bot_ids=baby_ids,  # 11 babies
        hypothesis_id=hypothesis_id,
        diagnosis=diagnosis,  # from Rocky proposal
        mutation_type=mutation_type,  # 'selectivity', 'exit', etc.
        parameter_changes=parameter_changes,
        rationale=rationale,  # from Rocky proposal
        expected_effect=expected_effect
    )
```

### Step 6: Add Hook to Evaluation

In evaluation code (wherever bot metrics are computed):

```python
# After evaluation completes and metrics are ready
metrics = {
    'trades': evaluation_result['trades'],
    'flip_rate': evaluation_result['flip_rate'],
    'shadow_pnl': evaluation_result['pnl'],
    'divergence': evaluation_result['divergence'],
    'drawdown': evaluation_result['max_drawdown'],
    'survival': evaluation_result['survival_rate'],
    'trajectory': trajectory_status,
    'control_action': control_action
}

if _think_hook:
    _think_hook.on_evaluation_complete(bot_id, metrics)
```

### Step 7: Add Hook to Mutation Result Classification

When mutation is classified (after comparing babies):

```python
# After evaluating all babies and comparing to parent
if best_baby_pnl > parent_pnl:
    result = 'helped'
    result_summary = f"Mutation improved PnL by {improvement_pct:.1f}%"
elif best_baby_pnl < parent_pnl * 0.95:
    result = 'hurt'
    result_summary = f"Mutation degraded performance by {degradation_pct:.1f}%"
else:
    result = 'inconclusive'
    result_summary = "No clear win or loss"

if _think_hook:
    _think_hook.on_mutation_result_classified(
        mutation_id=mutation_id,
        result=result,
        result_summary=result_summary
    )
```

### Step 8: Add Hooks to Decision Points

**On Bot Promotion:**
```python
if _think_hook:
    _think_hook.on_bot_promoted(
        bot_id=baby_id,
        hypothesis_id=hypothesis_id,
        reason="User promoted bot to capital allocation",
        context_snapshot=current_metrics
    )
```

**On Bot Kill:**
```python
if _think_hook:
    _think_hook.on_bot_killed(
        bot_id=baby_id,
        hypothesis_id=hypothesis_id,
        reason="Mutation failed validation",
        context_snapshot=current_metrics
    )
```

**On User Approve/Reject:**
```python
if _think_hook:
    _think_hook.on_decision_made(
        decision_type='approve_proposal',  # or reject_proposal
        source='user',
        reason=user_reason,
        related_mutation_id=mutation_id,
        related_hypothesis_id=hypothesis_id,
        context_snapshot=current_state
    )
```

---

## Validation Checklist

After integration, verify:

- [ ] Hypotheses table has entries
- [ ] Each bot links to a hypothesis_id
- [ ] Mutations have 11 resulting_bot_ids each
- [ ] Babies link back to mutations via created_by_mutation_id
- [ ] Evaluation updates latest_metrics_json
- [ ] Mutations get result ('helped'/'hurt'/'inconclusive')
- [ ] Decisions record promotions/kills
- [ ] Rocky's queries return sensible data

**Quick check:**
```sql
SELECT 
    (SELECT COUNT(*) FROM hypotheses) as hyp_count,
    (SELECT COUNT(*) FROM bots) as bot_count,
    (SELECT COUNT(*) FROM mutations) as mut_count,
    (SELECT COUNT(*) FROM decisions) as dec_count;
```

---

## What NOT to Change

Do NOT modify:
- Arena execution logic
- DNA/parameter structure
- Existing mutation classification
- Bot spawn naming convention
- Dashboard display logic

ONLY add:
- Imports at top
- Initialize hook on startup
- Call hook methods at event boundaries
- Close hook on shutdown

---

## Rocky's Queries

After integration, Rocky can use these queries:

```python
from think_memory_queries import THINKMemory

memory = THINKMemory()
memory.init()

# 1. Why does this bot exist?
origin = memory.explainBotOrigin('bot_id')

# 2. What has been tried on this hypothesis?
history = memory.hypothesisMutationHistory('hypothesis_id')

# 3. Is this problem new or repeated?
attempts = memory.findPriorAttempts('high flip rate')

# 4. Has this hypothesis ever worked?
summary = memory.hypothesisPerformanceSummary('hypothesis_id')

# 5. Why promote/kill?
context = memory.promotionDecisionContext('bot_id')
```

---

## Next Steps

After Phase 2 integration:

1. **Phase 3:** Seed agents (2 archetypes: Overfitter + Explorer)
2. **Phase 4:** MOLT feed (signal / experimental / noise tiers)
3. **Phase 5:** 3-window UI refactor
4. **Phase 6:** LAB mode (slow experimentation)
5. **Phase 7:** SIM mode (pressure training)

---

## Files

- `hypothesis_engine.py` — Hypothesis creation + validation
- `event_hooks.py` — Event → database layer
- `test-phase2-flow.py` — Integration test
- `PHASE2-INTEGRATION-GUIDE.md` — This file
