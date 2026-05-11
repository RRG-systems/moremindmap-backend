# PHASE 31 QUICK START - BABY VARIANT NURSERY

## What Got Built

A concurrent evolution system that creates 10 baby strategy variants, runs them simultaneously, scores them with a shadow-first fitness metric, and displays results on the dashboard.

**TL;DR:** MOLTmarket can now evolve strategies automatically while keeping the main strategy running.

---

## Core Components

### 1. Evolution Engine (`evolution_engine.py`)
```python
engine = EvolutionEngine()
babies = engine.spawn_baby_variants(count=10)  # Creates 10 babies
score = engine.score_variant('baby_001')       # Scores by fitness
leaderboard = engine.get_nursery_leaderboard() # Ranks all babies
```

### 2. Variant Nursery (`variant_nursery.py`)
```python
nursery = VariantNursery(workspace_dir, evolution_engine)
nursery.spawn_babies(run_id='test', count=10)
nursery.finalize_and_score_babies(run_id='test')  # Persists to CSV
nursery.promote_baby('baby_001')                   # Manual promotion
```

### 3. Dashboard Panel
- Location: Below breakdowns, above recent trades
- Shows: Variant | Mutation | Trades | Shadow PnL | Flip Rate | Degradation | Score | Status
- Color-coded: Green (strong), Yellow (borderline), Red (weak)

### 4. CSV Persistence (`variant_nursery.csv`)
Append-only log of all babies and their metrics. Full audit trail.

---

## How It Works

### Step 1: Spawn Babies
```bash
curl -X POST http://localhost:5000/api/nursery/spawn
```
Creates 10 babies from parent Mean Reversion strategy. Each mutates 1 parameter:
- baby_001: entry_threshold adjusted ±5%
- baby_002: exit_threshold adjusted ±5%
- baby_003: holding_time adjusted ±10%
- baby_004: confirmation_rules toggled
- baby_005: stop_loss_sensitivity adjusted ±5%
- baby_006: target_profit_sensitivity adjusted ±5%
- baby_007-010: Repeat cycle for diversity

### Step 2: Concurrent Execution
- Main Mean Reversion continues (paper + shadow)
- Each baby trades independently (paper + shadow)
- Isolated execution states (NO main arena interference)
- Separate CSV file (NO contamination)

### Step 3: Score by Fitness
Shadow-first priority:
1. **shadow_pnl** (maximize) - Realistic execution
2. **sign_flip_rate** (minimize) - Paper wins → shadow losses
3. **degradation** (minimize) - Execution cost gap
4. **trade_count** (threshold) - Minimum 20 trades
5. **win_rate** (tiebreaker)

### Step 4: Review & Promote
```bash
curl http://localhost:5000/api/nursery/leaderboard
```
Review top candidate (highest score).

Decision options:
- **PROMOTE** → Baby becomes new parent (Phase 32+)
- **RETIRE** → Stop testing this variant
- **CONTINUE** → Wait for more data

```bash
curl -X POST http://localhost:5000/api/nursery/promote/baby_001
```

---

## Fitness Scoring

### Score Calculation
```
if trade_count < 20:
    score = -999 (disqualified)
else:
    score_pnl = min(max(shadow_pnl / 10, 0), 100)
    penalty_flips = sign_flip_rate * 0.5
    penalty_deg = degradation_pct * 0.2
    score = score_pnl - penalty_flips - penalty_deg
```

### Color Coding
- **GREEN** (score > 70): Strong candidate - Consider promoting
- **YELLOW** (score 40-70): Borderline - Continue testing  
- **RED** (score < 40): Weak - Consider retiring

---

## Dashboard Integration

### Where It Appears
```
┌─────────────────────────────────────────┐
│ Main Dashboard                          │
│ ┌─ KPI Cards ──────────────────────────┐│
│ │ Paper | Shadow | Delta | Win Rate ... ││
│ └──────────────────────────────────────┘│
│ ┌─ Equity Chart ───────────────────────┐│
│ │ Paper vs Shadow vs Backtest          ││
│ └──────────────────────────────────────┘│
│ ┌─ Trade Breakdowns ───────────────────┐│
│ │ By Asset | By Signal | By Regime ... ││
│ └──────────────────────────────────────┘│
│ ┌─ VARIANT NURSERY ────────────────────┐│  ← NEW!
│ │ Status: active | Babies: 10/10       ││
│ │ [Leaderboard table with 10 babies]   ││
│ └──────────────────────────────────────┘│
│ ┌─ Recent Trades ──────────────────────┐│
│ │ Time | Asset | Signal | PnL ...      ││
│ └──────────────────────────────────────┘│
└─────────────────────────────────────────┘
```

---

## API Reference

### Spawn Nursery
```
POST /api/nursery/spawn

Response:
{
  "status": "spawned",
  "run_id": "2026-04-16-13-45-00",
  "count": 10,
  "babies": [
    {"variant_id": "baby_001", "mutation_type": "entry_threshold"},
    ...
  ]
}
```

### Get Leaderboard
```
GET /api/nursery/leaderboard

Response:
[
  {
    "variant_id": "baby_001",
    "mutation_type": "entry_threshold",
    "trades": 42,
    "shadow_pnl": 1876.45,
    "flip_rate": 18.5,
    "degradation": 12.8,
    "score": 67.3,
    "status": "active"
  },
  ...
]
```

### Finalize & Score
```
POST /api/nursery/finalize

Response:
{
  "status": "finalized",
  "leaderboard": [...]  // Ranked by score
}
```

### Promote Baby (Manual)
```
POST /api/nursery/promote/baby_001

Response:
{
  "status": "promoted",
  "variant_id": "baby_001"
}
```

---

## Key Features

✓ **Uses EXISTING mutation engine** - No new frameworks
✓ **Shadow-first scoring** - Realistic execution prioritized
✓ **Concurrent execution** - 10 babies + main strategy simultaneously
✓ **Isolated execution states** - Zero main arena interference
✓ **Manual promotion** - D.J. makes the decision
✓ **Full audit trail** - Append-only CSV, all metrics preserved
✓ **Compact dashboard** - Single screenshot, color-coded
✓ **API support** - Full CRUD for nursery operations

---

## Files Created/Modified

### New Files
- `evolution_engine.py` - Mutation + scoring engine
- `variant_nursery.py` - Nursery management
- `variant_nursery.csv` - Append-only records
- `test_phase31.py` - Test suite (all passing)
- `PHASE31_IMPLEMENTATION.md` - Full documentation
- `PHASE31_OUTPUT.md` - Deliverables checklist
- `PHASE31_SUMMARY.txt` - Executive summary

### Modified Files
- `moltmarket_dashboard.py` - 4 new API endpoints
- `templates/dashboard.html` - Added nursery panel
- `static/dashboard.css` - Added nursery styling
- `static/dashboard.js` - Added nursery functions
- `dashboard_data_layer.py` - Added nursery reference

---

## Test Results

All tests passing:
```
[PHASE 31] Evolution engine test: ✓ PASSED
[PHASE 31] Nursery system test: ✓ PASSED
[PHASE 31] Fitness scoring test: ✓ PASSED
```

---

## Next Phase (Phase 32+)

Future enhancements:
- Auto-spawn nursery at intervals
- Multi-generation evolution (baby → parent → new babies)
- Comparison dashboard (baby vs parent)
- Detail view (individual equity curves)
- Promotion workflow UI

---

## Summary

PHASE 31 adds an evolution system to MOLTmarket:

✓ Spawn 10 baby variants automatically
✓ Run them concurrently with main strategy
✓ Score by shadow-first fitness metric
✓ Display in compact dashboard panel
✓ Manual promotion workflow
✓ Full data persistence & audit trail
✓ Zero main arena interference
✓ Production ready

Ready for live concurrent evolution with manual promotion decisions.

---

**File:** PHASE31_QUICK_START.md  
**Status:** ✓ PRODUCTION READY  
**Last Updated:** 2026-04-16 13:20 MST
