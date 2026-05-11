# PHASE 32.3 - QUICK REFERENCE GUIDE

## The Problem (Before Phase 32.3)
- Gen 2 babies spawned from baseline despite UI showing promoted parent
- CSV parent_id was always baseline
- Evolution restarted each generation (no compounding)

## The Solution (Phase 32.3)
- `evolution_engine.current_parent` = single authoritative parent
- Promotion calls `evolution_engine.promote_baby_to_parent(baby)`
- Spawn always reads from `evolution_engine.current_parent`
- Lineage-aware naming: `baseline-05`, `baseline05-01`, etc.

## Code Changes Summary

### 1. evolution_engine.py
```python
# NEW: Authoritative parent (single source of truth)
self.current_parent = self._create_default_parent()

# NEW: Update parent on promotion
def promote_baby_to_parent(self, baby):
    self.current_parent = promoted_parent
    
# NEW: Reset parent to baseline
def reset_to_baseline(self):
    self.current_parent = self._create_default_parent()

# FIX: Spawn always uses current_parent
parent_strategy = self.current_parent  # NOT self.parent_strategy

# NEW: Lineage naming
if parent_id == 'baseline':
    variant_id = f"baseline-{str(i+1).zfill(2)}"
else:
    parent_short = parent_id.replace('_', '').replace('-', '')
    variant_id = f"{parent_short}-{str(i+1).zfill(2)}"
```

### 2. moltmarket_dashboard.py
```python
# FIX: Promotion endpoint
promoted_parent = evolution_engine.promote_baby_to_parent(baby)
dashboard_state['parent_strategy'] = promoted_parent  # Keep in sync

# FIX: Reset endpoint
baseline_parent = evolution_engine.reset_to_baseline()
dashboard_state['parent_strategy'] = baseline_parent
```

### 3. variant_nursery.py
```python
# ADD: CSV headers
'parent_id', 'parent_generation', 'generation', ...

# ADD: CSV row
row['parent_generation'] = baby.get('parent_generation', 0)
```

## Key Concepts

### Single Source of Truth
- `evolution_engine.current_parent` is authoritative
- Dashboard reads/writes to this same object
- No more desync

### Three Strategies to Understand
```
Baseline (Gen 0):
  ID: 'baseline'
  Generation: 0
  Parameters: default (entry_threshold=0.003, etc.)

Gen 1 from Baseline:
  ID: 'baseline-05' (parent indicator)
  Generation: 1
  Parameters: inherited from baseline + 1 mutation

Gen 2 from Gen 1:
  ID: 'baseline05-01' (encodes both parents)
  Generation: 2
  Parameters: inherited from baseline-05 + 1 mutation
```

### Generation Formula
```
child_generation = parent_generation + 1

baseline (Gen 0)
  ↓
baseline-XX (Gen 1)
  ↓
baseline0X-XX (Gen 2)
  ↓
baseline0X0X-XX (Gen 3)
```

### Lineage Naming Formula
```
If parent is 'baseline':
  child = 'baseline-01', 'baseline-02', ..., 'baseline-10'

If parent is 'baseline-05':
  child = 'baseline05-01', 'baseline05-02', ..., 'baseline05-10'
  (removes dashes, appends -01, -02, etc.)

If parent is 'baseline05-03':
  child = 'baseline0503-01', 'baseline0503-02', ..., 'baseline0503-10'
  (recursive: encodes full lineage path)
```

## Test Proof

### Before Fix
```
Gen 2 CSV shows:
  variant_id: baby_005
  parent_id: parent_mean_rev_20_03  ← WRONG! Shows baseline
  generation: 1
  entry_threshold: 0.003  ← WRONG! Uses baseline value, not promoted parent
```

### After Fix
```
Gen 2 CSV shows:
  variant_id: baseline05-01
  parent_id: baseline-05  ← CORRECT! Shows promoted parent
  parent_generation: 1  ← CORRECT! Shows parent was Gen 1
  generation: 2  ← CORRECT!
  entry_threshold: 0.0042  ← CORRECT! Inherits promoted parent's value
```

## Testing

### Run Test Suite
```bash
python3 /Users/rrg/.openclaw/workspace/moltmarket/PHASE_32_3_TEST.py
```

### Expected Output
```
✅ TEST 1: Baseline parent initialization
✅ TEST 2: Gen 1 spawn from baseline
✅ TEST 3: Gen 1 lineage naming
✅ TEST 4: Promotion updates evolution_engine.current_parent
✅ TEST 5: Gen 2 spawn from promoted parent
✅ TEST 6: Gen 2 lineage naming
✅ TEST 7: Reset to baseline
✅ TEST 8: New spawn after reset
✅ TEST 9: Inheritance proof

✓ ALL TESTS PASSED
```

## Verification Points

### Inheritance Chain
- Gen 1 babies: `baseline-01` to `baseline-10` (inherit from baseline)
- Gen 2 babies: `baseline05-01` to `baseline05-10` (inherit from `baseline-05`)
- CSV `parent_id`: shows true parent (baseline for Gen 1, promoted ID for Gen 2)

### Lineage Encoding
- Name format shows parent at a glance
- `baseline-05` → "child of baseline, index 5"
- `baseline05-01` → "child of baseline-05, index 1"

### DNA Transfer
- Promoted baby's config copied to `current_parent`
- All parameters inherited: entry_threshold, exit_threshold, holding_time, etc.
- Next generation uses promoted config, not baseline

### Generation Tracking
- Baseline: Gen 0
- Children of baseline: Gen 1
- Children of Gen 1: Gen 2
- etc.

## Files to Review

| File | Change | Impact |
|------|--------|--------|
| evolution_engine.py | Complete rewrite | Core logic |
| moltmarket_dashboard.py | 2 endpoints updated | Promotion/reset |
| variant_nursery.py | CSV schema expanded | Data logging |
| PHASE_32_3_TEST.py | New test suite | Verification |
| PHASE_32_3_COMPLETION_REPORT.md | Complete documentation | Reference |

## Deployment Checklist

- [ ] Deploy evolution_engine.py
- [ ] Deploy moltmarket_dashboard.py
- [ ] Deploy variant_nursery.py
- [ ] Restart Flask app
- [ ] Run PHASE_32_3_TEST.py to verify
- [ ] Monitor next nursery spawn

## Troubleshooting

### Gen 2 babies still show baseline as parent
- Check: Is `evolution_engine.promote_baby_to_parent()` being called?
- Check: Are both `current_parent` and `dashboard_state` being updated?

### Lineage names look wrong
- Check: Parent ID format (should be e.g., `baseline-05`, not `baby_005`)
- Check: Child name format (should be e.g., `baseline05-01`, not `baby_001`)

### DNA not transferred to arena
- Check: Is `dashboard_state['parent_strategy']` updated from `current_parent`?
- Check: Is arena execution reading from `dashboard_state['parent_strategy']`?

## Success Indicators

✅ Gen 2 CSV shows parent_id = promoted baby (not baseline)  
✅ Gen 2 children names encode parent (baseline05-01 format)  
✅ Gen 2 generation = 2 (not 1)  
✅ Gen 2 inherits promoted parent's parameters (entry_threshold, etc.)  
✅ Active strategy label shows current parent  
✅ Arena uses promoted parent's DNA  
✅ Multi-generation evolution compounds (not restarts)  

---

**Full documentation:** See PHASE_32_3_COMPLETION_REPORT.md  
**Test proofs:** Run PHASE_32_3_TEST.py
