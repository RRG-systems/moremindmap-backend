# PHASE 32.1 - Backend Promotion Endpoint Specification

## Overview
PHASE 32.1 implements a complete backend promotion workflow for the MOLTmarket variant nursery system. The endpoint allows manual promotion of a winning baby variant into the main arena, replacing the parent strategy while preserving all historical data.

## Architecture

### Endpoint: POST /api/nursery/promote/<variant_id>

**Purpose:** Promote a single baby variant to parent strategy status

**Input:**
- `variant_id` (path parameter): ID of baby variant to promote
- Request body: Empty (POST only)

**Output:**
```json
{
  "status": "success",
  "promoted_variant": "baby_variant_001",
  "new_parent_id": "baby_variant_001",
  "retired_count": 9,
  "parent_strategy": {
    "id": "baby_variant_001",
    "parent_variant_id": "baby_variant_001",
    "mutation_type": "entry_threshold",
    "parameter_value": 0.325,
    "generation": 1,
    "promoted_from": "nursery",
    "promoted_at": "2026-04-16T15:17:00.000000",
    "previous_generation": {
      "id": "parent_mean_reversion",
      "mutation_type": "mean_reversion_20_03",
      "generation": 0,
      "promoted_from": "baseline"
    }
  }
}
```

## Implementation Details

### Step 1: Validate Baby Exists
- Check `evolution_engine.babies` for active nursery
- Search for baby with matching `variant_id`
- Return 400 if no nursery exists
- Return 404 if variant not found

### Step 2: Collect Fitness Metrics
- Retrieve execution state from `evolution_engine.execution_states[variant_id]`
- Query `evolution_engine.get_nursery_leaderboard()` to get fitness scores
- Extract: `trade_count`, `score`, `shadow_pnl`, `sign_flip_rate`

### Step 3: Validate Eligibility
**Promotion Criteria:**
- ✓ Minimum 30 trades in shadow execution
- ✓ Valid fitness score (score > -999)
- ✓ Status not already 'promoted'
- ✓ Status not already 'retired'

**Rejection Response (400):**
```json
{
  "error": "insufficient trades: 25"
}
```

### Step 4: State Transitions

#### 4a. Mark Winner as "promoted"
```python
baby['status'] = 'promoted'
baby['promoted_at'] = datetime.now().isoformat()
```

#### 4b. Mark Losers as "retired"
```python
for b in evolution_engine.babies:
    if b['variant_id'] != variant_id:
        b['status'] = 'retired'
        b['retired_at'] = datetime.now().isoformat()
```

#### 4c. Replace Parent Strategy Config
```python
dashboard_state['parent_strategy'] = {
    'id': variant_id,
    'parent_variant_id': variant_id,
    'mutation_type': baby.get('mutation_type'),
    'parameter_value': baby.get('parameter_value'),
    'generation': baby.get('generation') + 1,
    'promoted_from': 'nursery',
    'promoted_at': datetime.now().isoformat(),
    'previous_generation': old_parent_strategy  # For lineage tracking
}
```

#### 4d. Clear Nursery State
```python
evolution_engine.babies = []
dashboard_state['nursery_status'] = 'inactive'
```

### Step 5: CSV Persistence

**variant_nursery.csv Update:**
- For promoted baby: `status='promoted'`, add `promoted_at` timestamp
- For retired babies: `status='retired'`, add `retired_at` timestamp
- All other fields preserved (immutable history)

**CSV Columns (Append-Only):**
```
run_id,
variant_id,
parent_id,
generation,
mutation_type,
parameter_value,
trade_count,
paper_pnl,
shadow_pnl,
sign_flip_rate,
degradation_pct,
score,
status,
timestamp,
promoted_at,          # Optional: added on promotion
retired_at            # Optional: added on retirement
```

### Step 6: Terminal Logging

Complete promotion flow produces these logs:

```
[NURSERY] promotion requested for baby_variant_001
[NURSERY] promotion validation: trades=45, score=2850.25
[NURSERY] promotion validation passed
[NURSERY] marking baby_variant_001 as promoted
[NURSERY] retiring baby_variant_002
[NURSERY] retiring baby_variant_003
...
[NURSERY] 9 babies marked retired
[NURSERY] replacing parent strategy with baby_variant_001 config
[NURSERY] parent strategy replaced
[NURSERY] clearing nursery execution state
[NURSERY] nursery state cleared
[NURSERY] recording promotion to variant_nursery.csv
[NURSERY] promotion recorded in CSV
[NURSERY] promotion complete for baby_variant_001
```

## Helper Endpoints

### GET /api/nursery/status
**Purpose:** Check current nursery state for debugging

**Response:**
```json
{
  "parent_strategy": {
    "id": "baby_variant_001",
    "generation": 1,
    "promoted_from": "nursery"
  },
  "current_run_id": "2026-04-16-15-17-00",
  "nursery_status": "inactive",
  "active_babies": 0,
  "babies": []
}
```

## Success Criteria

After successful promotion:

✅ Endpoint listens for POST requests at `/api/nursery/promote/<variant_id>`

✅ Validation rejects babies with:
- < 30 trades
- Invalid score (≤ -999)
- Already promoted/retired status

✅ Valid promotion atomically:
- Marks winner as "promoted"
- Marks losers as "retired"
- Replaces parent strategy config
- Increments generation counter
- Clears nursery state

✅ CSV is updated with:
- `promoted_at` timestamps for winner
- `retired_at` timestamps for losers
- All history preserved (no row deletion)

✅ Terminal shows detailed `[NURSERY]` logs

✅ Response includes success JSON with counts

✅ Historical data completely intact

## Error Handling

### Error Cases (with HTTP codes)

| Condition | Code | Response |
|-----------|------|----------|
| No active nursery | 400 | `{"error": "no active nursery"}` |
| Baby not found | 404 | `{"error": "variant not found"}` |
| No execution state | 400 | `{"error": "no execution state"}` |
| No fitness metrics | 400 | `{"error": "no metrics available"}` |
| < 30 trades | 400 | `{"error": "insufficient trades: N"}` |
| Invalid score | 400 | `{"error": "invalid score: N"}` |
| Exception thrown | 500 | `{"error": "exception message"}` |

## Data Flow Diagram

```
POST /api/nursery/promote/baby_variant_001
│
├─ [1] Validate nursery exists
│   └─ Check evolution_engine.babies
│
├─ [2] Find baby by variant_id
│   └─ Search evolution_engine.babies[]
│
├─ [3] Get execution state
│   └─ Fetch evolution_engine.execution_states[variant_id]
│
├─ [4] Get fitness metrics
│   └─ Query evolution_engine.get_nursery_leaderboard()
│
├─ [5] Validate eligibility
│   ├─ Check trade_count >= 30
│   ├─ Check score > -999
│   └─ Check status valid
│
├─ [6] State transitions
│   ├─ baby['status'] = 'promoted'
│   ├─ Other babies: status = 'retired'
│   ├─ Replace dashboard_state['parent_strategy']
│   └─ Clear evolution_engine.babies[]
│
├─ [7] Update CSV
│   ├─ Read variant_nursery.csv
│   ├─ Update promoted baby row
│   ├─ Update retired baby rows
│   └─ Write back (append-only)
│
└─ [8] Return success JSON
    └─ 200 with promotion details
```

## Testing

### Manual Test (cURL)

```bash
# Check nursery status
curl http://localhost:5000/api/nursery/status

# Promote baby variant (after spawning and scoring)
curl -X POST http://localhost:5000/api/nursery/promote/baby_variant_001

# Expected response:
# {
#   "status": "success",
#   "promoted_variant": "baby_variant_001",
#   "retired_count": 9,
#   ...
# }
```

### Test Sequence

1. Start dashboard: `python moltmarket_dashboard.py`
2. Spawn nursery: `POST /api/nursery/spawn`
3. Wait for trades: Monitor `/api/nursery/leaderboard`
4. Finalize scoring: `POST /api/nursery/finalize`
5. Promote winner: `POST /api/nursery/promote/baby_variant_001`
6. Verify state: `GET /api/nursery/status` → should show `nursery_status: "inactive"`

## CSV History Example

### Before Promotion
```
run_id,variant_id,status,timestamp
2026-04-16-15-17-00,baby_variant_001,active,2026-04-16T15:17:15.123456
2026-04-16-15-17-00,baby_variant_002,active,2026-04-16T15:17:15.123456
2026-04-16-15-17-00,baby_variant_003,active,2026-04-16T15:17:15.123456
```

### After Promotion
```
run_id,variant_id,status,timestamp,promoted_at,retired_at
2026-04-16-15-17-00,baby_variant_001,promoted,2026-04-16T15:17:15.123456,2026-04-16T15:18:45.654321,
2026-04-16-15-17-00,baby_variant_002,retired,2026-04-16T15:17:15.123456,,2026-04-16T15:18:45.654321
2026-04-16-15-17-00,baby_variant_003,retired,2026-04-16T15:17:15.123456,,2026-04-16T15:18:45.654321
```

## Integration Notes

✅ **Does NOT:**
- Add frontend UI buttons (backend only)
- Change dashboard display
- Add UI styling
- Auto-spawn generation 2
- Modify scoring/mutation logic
- Change execution loop
- Wire frontend yet

✅ **Core Features:**
- Atomic promotion transaction
- Complete state transition
- CSV history preservation
- Detailed terminal logging
- Generation lineage tracking
- Error handling & validation
- Manual promotion (no auto-promotion)

## Next Phases

**PHASE 32.2:** Wire frontend button to promotion endpoint
**PHASE 32.3:** Auto-spawn generation 2 from promoted baby
**PHASE 32.4:** Dashboard display of promotion history
