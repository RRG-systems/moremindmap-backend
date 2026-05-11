# PHASE 31: BABY VARIANT NURSERY (CONCURRENT EVOLUTION, LOCKED TO ENGINE)

## Overview

PHASE 31 implements a concurrent evolution system for MOLTmarket strategy optimization. The system spawns 10 baby variants of the parent Mean Reversion strategy, runs them concurrently using EXISTING execution layers (paper + shadow), scores them using a shadow-first fitness hierarchy, and provides a dashboard panel for manual promotion decisions.

**CRITICAL CONSTRAINT:** ALL BABIES USE EXISTING EVOLUTION ENGINE. No new mutation framework. No new execution layers. Reuse everything.

---

## Architecture

### Core Components

#### 1. **EvolutionEngine** (`evolution_engine.py`)
Central system for strategy mutation and fitness scoring.

**Key Methods:**
- `mutate_one_dimension(variant, dimension, intensity=0.05)` - Mutate single parameter
- `spawn_baby_variants(parent_strategy, count=10)` - Create N babies from parent
- `score_variant(variant_id)` - Calculate fitness score
- `get_nursery_leaderboard()` - Rank all babies by score

**Mutation Dimensions (single per baby):**
1. `entry_threshold` - Entry signal threshold (±5-10%)
2. `exit_threshold` - Profit target threshold (±5-10%)
3. `holding_time` - Max trade duration in seconds (±10-20%)
4. `confirmation_rules` - Toggle confirmation tick requirement (0 or 1)
5. `stop_loss_sensitivity` - Stop loss multiplier (±5%)
6. `target_profit_sensitivity` - Target profit multiplier (±5%)

#### 2. **VariantNursery** (`variant_nursery.py`)
Manages spawning, scoring, persistence, and promotion workflow.

**Key Methods:**
- `spawn_babies(run_id, count=10)` - Spawn babies for this run
- `finalize_and_score_babies(run_id)` - Score all babies and persist
- `promote_baby(variant_id)` - Manual promotion (status → 'promoted')
- `retire_baby(variant_id)` - Retire baby (status → 'retired')
- `get_candidate_for_promotion()` - Get top baby for review

**CSV Persistence:** `variant_nursery.csv` (append-only)
```
run_id, variant_id, parent_id, generation, mutation_type, parameter_value,
trade_count, paper_pnl, shadow_pnl, sign_flip_rate, degradation_pct,
score, status, timestamp
```

#### 3. **Execution Layer Integration**
Babies execute using EXISTING layers:
- **Paper Layer:** Ideal fills (0-2 bps slippage)
- **Shadow Layer:** Degraded fills (2-5 bps slippage + 10 bps round-trip)
- Each baby gets isolated execution state (no main arena interference)

---

## Fitness Scoring Hierarchy (SHADOW-FIRST)

**Priority 1: shadow_pnl (Maximize)**
- Metric: Total PnL from shadow execution
- Normalized to 0-100 scale (assume $1000 max realistic PnL)
- Base score: `score_pnl = min(max(shadow_pnl / 10, 0), 100)`

**Priority 2: sign_flip_rate (Minimize)**
- Metric: % of paper wins that become shadow losses
- Penalty: Each 1% flip rate = -0.5 points
- `penalty_flips = sign_flip_rate * 0.5`

**Priority 3: paper_vs_shadow_degradation (Minimize)**
- Metric: `(paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100`
- Penalty: Each 1% degradation = -0.2 points
- `penalty_degradation = degradation_pct * 0.2`

**Priority 4: trade_count (Minimum Threshold)**
- Requirement: >= 20 trades (sufficient sample)
- Below threshold → Score = -999 (disqualified)

**Priority 5: win_rate (Optional, Lower Weight)**
- Target: >= 50% winning trades
- Used as tiebreaker only

**Composite Score Calculation:**
```
if trade_count < 20:
    return -999  # Disqualified

score_pnl = min(max(shadow_pnl / 10, 0), 100)
penalty_flips = sign_flip_rate * 0.5
penalty_degradation = degradation_pct * 0.2

final_score = score_pnl - penalty_flips - penalty_degradation
```

---

## Dashboard Panel (Variant Nursery)

### Location
Below the breakdowns section, above recent trades table.

### Layout (Compact, Single Screenshot)
```
┌─ Variant Nursery (Concurrent Evolution) ────────────────┐
│ Status: active | Babies: 10/10 | Top: baby_001 (85.3)   │
├─ Leaderboard (Sorted by Score, Descending) ─────────────┤
│ Variant  | Mutation  | Trades | Shadow PnL | Flip | Deg | Score | Status │
├──────────┼───────────┼────────┼────────────┼──────┼─────┼───────┼────────┤
│ baby_001 │ entry_... │   42   │   $1876.45 │ 18.5 │12.8 │  67.3 │ active │
│ baby_002 │ exit_...  │   38   │   $1650.22 │ 22.1 │15.3 │  61.1 │ active │
│ baby_003 │ holding.. │   35   │   $1200.15 │ 25.0 │20.5 │  48.7 │ active │
│ ...      │ ...       │  ...   │   ...      │ ...  │ ... │  ...  │ ...    │
└─ ────────┴───────────┴────────┴────────────┴──────┴─────┴───────┴────────┘

Color Coding:
✓ Green (score > 70): Strong candidate
⊙ Yellow (score 40-70): Borderline
✗ Red (score < 40): Weak
```

### HTML Structure
```html
<div class="nursery-panel">
    <h2>Variant Nursery (Concurrent Evolution)</h2>
    <div class="nursery-info">
        <span>Status: <span id="nursery-status">idle</span></span>
        <span>Babies: <span id="nursery-count">0</span>/10</span>
        <span>Top Candidate: <span id="top-candidate">—</span></span>
    </div>
    <table class="nursery-leaderboard">
        <thead>
            <tr>
                <th>Variant</th>
                <th>Mutation</th>
                <th>Trades</th>
                <th>Shadow PnL</th>
                <th>Flip Rate</th>
                <th>Degradation</th>
                <th>Score</th>
                <th>Status</th>
            </tr>
        </thead>
        <tbody id="nursery-body">
            <!-- Populated by JS -->
        </tbody>
    </table>
</div>
```

### CSS Styling
```css
.nursery-panel {
    background: #1a1a1a;
    border: 1px solid #333;
    border-radius: 6px;
    padding: 12px;
    margin: 16px 0;
}

.nursery-leaderboard tr.strong { background: rgba(34, 197, 94, 0.1); }  /* Green */
.nursery-leaderboard tr.borderline { background: rgba(234, 179, 8, 0.1); } /* Yellow */
.nursery-leaderboard tr.weak { background: rgba(239, 68, 68, 0.1); }    /* Red */
```

---

## Promotion Workflow (MANUAL, NO AUTO-PROMOTION)

### Step 1: Identify Top Candidate
```
Nursery leaderboard shows top-ranked baby
Status: "candidate_winner" in CSV
```

### Step 2: Manual Review
```
D.J. inspects:
- Equity curve (paper vs shadow)
- Trade log (entry/exit quality)
- Regime performance (high vol, low vol, trending)
- Sign flip rate (execution reliability)
- Degradation (gap between paper and shadow)
```

### Step 3: Decision
Three options:

**Option A: Promote**
```
POST /api/nursery/promote/baby_001
→ Status: "promoted"
→ Baby becomes new parent strategy (next phase)
```

**Option B: Retire**
```
Status: "retired" 
→ Baby is removed from competition
→ Continue testing other babies
```

**Option C: Continue Testing**
```
Status: "active"
→ Allow more trading data to accumulate
→ Re-score when sample size sufficient
```

### Promotion Persistence
```csv
run_id,variant_id,parent_id,generation,mutation_type,parameter_value,
trade_count,paper_pnl,shadow_pnl,sign_flip_rate,degradation_pct,score,
status,timestamp

run_001,baby_001,parent_mean_rev,1,entry_threshold,0.0032,42,2150.34,
1876.45,18.5,12.8,67.3,promoted,2026-04-16-13:45:00
```

---

## Separation: Main Arena vs Nursery

### Main Arena (Protected)
- Parent strategy continues (Mean Reversion)
- Feeds `/api/equity-curves` (paper, shadow, backtest)
- Feeds `research_trades.csv`
- KPI cards show main metrics only
- NO baby curves mixed in

### Nursery (Isolated)
- 10 babies run concurrently
- Each baby has isolated execution state
- No interference with main trades
- Separate CSV: `variant_nursery.csv`
- Nursery panel below dashboard (not embedded in main charts)

### Data Files
```
Main Arena:
  research_trades.csv (paper/shadow/backtest)
  research_runs.csv
  signal_health.csv
  execution_quality.csv

Nursery:
  variant_nursery.csv (append-only, full audit trail)
```

---

## API Endpoints

### 1. Spawn Babies
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

### 2. Get Leaderboard
```
GET /api/nursery/leaderboard

Response: [
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

### 3. Finalize & Score
```
POST /api/nursery/finalize

Response:
{
  "status": "finalized",
  "leaderboard": [...]  // Sorted by score
}
```

### 4. Promote Baby (Manual)
```
POST /api/nursery/promote/baby_001

Response:
{
  "status": "promoted",
  "variant_id": "baby_001"
}
```

---

## Example Execution Flow

### Phase 31A: Spawn Babies
```
1. Click "Spawn Nursery" button (future UI)
2. POST /api/nursery/spawn
3. Evolution engine creates 10 babies:
   - baby_001: entry_threshold mutated ±5%
   - baby_002: exit_threshold mutated ±5%
   - baby_003: holding_time mutated ±10%
   - ...
   - baby_010: target_profit_sensitivity mutated ±5%
4. Each baby initialized with execution state
5. Leaderboard updated on dashboard
```

### Phase 31B: Concurrent Execution
```
1. Main Mean Reversion continues (paper + shadow)
2. 10 babies execute simultaneously (paper + shadow each)
3. Each baby trades independently on market data
4. Trades recorded to variant_nursery.csv
5. Metrics accumulated per baby
```

### Phase 31C: Score & Finalize
```
1. POST /api/nursery/finalize
2. Score each baby:
   - Shadow PnL (priority 1)
   - Sign flip rate (priority 2)
   - Degradation (priority 3)
   - Trade count (threshold)
   - Win rate (tiebreaker)
3. Rank by composite score
4. Mark top baby as "candidate_winner"
5. Persist to CSV
```

### Phase 31D: Manual Promotion
```
1. D.J. reviews leaderboard
2. Inspects top candidate (baby_001)
3. Reviews metrics:
   - Score: 67.3 (strong)
   - Shadow PnL: $1876.45 (profitable)
   - Flip rate: 18.5% (acceptable)
   - Degradation: 12.8% (reasonable execution cost)
4. Decision: PROMOTE
5. POST /api/nursery/promote/baby_001
6. Status → "promoted" in CSV
7. (Future phase) Baby becomes new parent for next nursery
```

---

## CSV Schema: variant_nursery.csv

**Append-Only Design** (no updates, full audit trail)

```csv
run_id,variant_id,parent_id,generation,mutation_type,parameter_value,
trade_count,paper_pnl,shadow_pnl,sign_flip_rate,degradation_pct,score,
status,timestamp

run_001,baby_001,parent_mean_rev,1,entry_threshold,0.0032,42,
2150.34,1876.45,18.5,12.8,67.3,active,2026-04-16-13:20:00

run_001,baby_002,parent_mean_rev,1,exit_threshold,0.0019,38,
1950.22,1650.22,22.1,15.3,61.1,active,2026-04-16-13:20:00

run_001,baby_003,parent_mean_rev,1,holding_time,330,35,
1300.15,1200.15,25.0,20.5,48.7,active,2026-04-16-13:20:00
```

**Fields:**
- `run_id`: Experiment run identifier (links to research_runs.csv)
- `variant_id`: Baby identifier (baby_001 - baby_010)
- `parent_id`: Reference to parent strategy
- `generation`: Generation number (1 for first nursery)
- `mutation_type`: Dimension mutated (entry_threshold, etc.)
- `parameter_value`: Actual mutated value
- `trade_count`: Total trades executed (paper + shadow)
- `paper_pnl`: Paper layer total PnL
- `shadow_pnl`: Shadow layer total PnL
- `sign_flip_rate`: % of paper wins → shadow losses
- `degradation_pct`: (paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100
- `score`: Composite fitness score
- `status`: active | candidate_winner | promoted | retired
- `timestamp`: When evaluated

---

## DO NOT (Critical Constraints)

- ✗ Do NOT create new mutation framework (use existing)
- ✗ Do NOT randomize parameters outside system
- ✗ Do NOT clutter main dashboard with baby curves
- ✗ Do NOT optimize for paper-only results
- ✗ Do NOT auto-promote without review
- ✗ Do NOT interfere with main arena execution
- ✗ Do NOT mix baby trades with main trades in research_trades.csv
- ✗ Do NOT delete historical CSV data

---

## Files Created/Modified

### New Files
1. `evolution_engine.py` - Mutation + scoring engine
2. `variant_nursery.py` - Nursery management
3. `variant_nursery.csv` - Append-only nursery records

### Modified Files
1. `moltmarket_dashboard.py` - Added nursery endpoints
2. `templates/dashboard.html` - Added nursery panel
3. `static/dashboard.css` - Added nursery styling
4. `static/dashboard.js` - Added nursery update logic
5. `dashboard_data_layer.py` - Added nursery_file reference

---

## Testing

### Manual Test Sequence
```bash
# 1. Start dashboard
python moltmarket_dashboard.py

# 2. In another terminal, test nursery spawn
curl -X POST http://localhost:5000/api/nursery/spawn

# 3. Verify babies created in memory
curl http://localhost:5000/api/nursery/leaderboard

# 4. Simulate some trading (dashboard runs automatically)

# 5. Finalize babies
curl -X POST http://localhost:5000/api/nursery/finalize

# 6. Check leaderboard (should show scores)
curl http://localhost:5000/api/nursery/leaderboard

# 7. Promote top baby
curl -X POST http://localhost:5000/api/nursery/promote/baby_001

# 8. Verify CSV was created
cat variant_nursery.csv
```

---

## Next Phase (Phase 32)

- [ ] Auto-spawn nursery at regular intervals
- [ ] Optional detail view (equity curves per baby)
- [ ] Compare baby vs parent performance
- [ ] Implement multi-generation evolution
- [ ] Baby → Parent transition logic

---

## Summary

PHASE 31 extends MOLTmarket's evolution system using EXISTING mutation engine and execution layers. The baby variant nursery:

✓ Spawns 10 babies (single dimension mutations)
✓ Runs concurrently (isolated execution states)
✓ Scores with shadow-first priority
✓ Displays in compact dashboard panel
✓ Enables manual promotion workflow
✓ Persists all data (append-only CSV)
✓ Protects main arena (zero interference)

**Focus:** Evolution framework locked to engine. Nursery display. Shadow-first scoring. Manual promotion.
