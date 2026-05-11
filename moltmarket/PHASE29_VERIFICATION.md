# PHASE 29 - Quick Verification Guide

## Files Modified

### Backend (Python)
- [x] `moltmarket_dashboard.py` - Reset endpoint + run_id tracking
- [x] `dashboard_execution.py` - Run finalization + state reset
- [x] `dashboard_data_layer.py` - CSV migration + separator markers

### Frontend (HTML/CSS/JS)
- [x] `templates/dashboard.html` - New Run button + run ID display
- [x] `static/dashboard.css` - Button styling + run ID display styling
- [x] `static/dashboard.js` - Reset handler + click listener

## Key Features Implemented

### 1. Run ID System
```python
run_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
# Example: "2026-04-16-12-32-45"
```
- ✓ Timestamp-based
- ✓ Globally unique
- ✓ Chronologically sortable

### 2. Run Finalization (Before Reset)
```python
run_summary = finalize_and_summarize_run()
# Captures:
# - total_trades, win_rate, avg_pnl_per_trade
# - total_pnl_paper, total_pnl_shadow
# - paper_vs_shadow_delta, avg_entry_slippage_bps
# - avg_exit_slippage_bps, sign_flip_rate
```

### 3. State Reset (After Finalization)
```python
simulator.reset_run_state()
# Clears:
# - paper_equity, shadow_equity, backtest_equity
# - paper_pnl, shadow_pnl, backtest_pnl
# - All trade counters
# Re-initializes: $10,000 starting value
```

### 4. Run Separators (Clear Boundaries)
```csv
run_id, timestamp, asset, ...
2026-04-16-12-00-00, 2026-04-16T12:30:00, ..., (last real trade)
2026-04-16-12-00-00, 2026-04-16T12:30:05, RUN_SEPARATOR, ...
2026-04-16-12-32-45, 2026-04-16T12:32:45, ..., (first new trade)
```

### 5. Data Migration (Automatic)
```python
_migrate_legacy_data()
# Runs on first DataLayer.initialize()
# Adds run_id column to existing CSVs
# Backfills with run_id="phase_28_run"
```

## CSV Structure - After PHASE 29

### research_trades.csv
```
run_id, timestamp, asset, signal, source, side, entry_price, exit_price, ...
```
✓ run_id in EVERY row
✓ RUN_SEPARATOR markers for boundaries
✓ Never deleted, only appended

### research_runs.csv
```
run_id, start_time, end_time, total_trades, win_rate, avg_pnl_per_trade, ...
```
✓ One row per finalized run
✓ Complete metrics snapshot
✓ Append-only archive

### signal_health.csv
```
run_id, timestamp, asset, signal, rolling_20_edge, ...
```
✓ run_id in EVERY row
✓ RUN_SEPARATOR markers

### execution_quality.csv
```
run_id, timestamp, asset, signal, expected_entry, shadow_entry, ...
```
✓ run_id in EVERY row
✓ RUN_SEPARATOR markers

## Frontend UI

### New Run Button
- Location: Top right, next to status indicator
- Style: Amber/orange gradient (caution)
- Tooltip: "Start new experiment run (preserves all historical data)"
- Behavior: Click → Confirmation → Reset → New run_id

### Run ID Display
- Location: Below header section
- Format: "Run: 2026-04-16-12-32-45"
- Updates: On page load + on reset
- Always visible

## API Endpoint

### POST /api/reset

**Request:**
```
POST /api/reset
```

**Response (Success):**
```json
{
  "status": "reset_complete",
  "new_run_id": "2026-04-16-12-32-45",
  "previous_run_summary": {
    "run_id": "2026-04-16-12-00-00",
    "total_trades": 68,
    "win_rate": 71.4,
    "total_pnl_paper": 2456.78,
    "total_pnl_shadow": 2145.23,
    "paper_vs_shadow_delta": 14.5,
    "avg_entry_slippage_bps": 2.1,
    "avg_exit_slippage_bps": 1.8,
    "sign_flip_rate": 20.6
  }
}
```

**Response (Error):**
```json
{
  "status": "error",
  "message": "Error description"
}
```

## Testing Checklist

- [ ] Start dashboard
- [ ] Generate 30-60 seconds of trades
- [ ] Verify run_id displays correctly
- [ ] Click New Run button
- [ ] Confirm dialog appears
- [ ] Confirm the reset
- [ ] Dashboard clears (charts empty)
- [ ] KPI cards show 0/0/0%
- [ ] New run_id displayed
- [ ] Check CSV files - historical data preserved
- [ ] Verify RUN_SEPARATOR markers in CSVs
- [ ] Repeat test cycle 2-3 times
- [ ] Generate CSV analysis report

## Critical Invariants

✓ NO CSV files deleted
✓ EVERY row has run_id
✓ RUN_SEPARATOR marks boundaries
✓ Data accessible for analysis
✓ Runs comparable over time
✓ Zero data loss guarantee

## Example Workflow

1. Start dashboard (run_id = 2026-04-16-12-00-00)
2. Trade for 30 min (68 trades, +$2456.78)
3. Click New Run
4. Finalize: append row to research_runs.csv
5. Append separators to all CSVs
6. Reset state → new run_id
7. Start fresh (run_id = 2026-04-16-12-32-45)
8. Trade for another 30 min (52 trades, +$1823.45)
9. Click New Run again
10. Now have 2 completed runs + 1 in progress
11. Can analyze any run independently
12. Compare runs across time

## Files - Quick Reference

### Python
- `moltmarket_dashboard.py` → Reset endpoint
- `dashboard_execution.py` → finalize_and_summarize_run() + reset_run_state()
- `dashboard_data_layer.py` → append_run_summary() + append_run_separator()

### Frontend
- `templates/dashboard.html` → Button + run ID display
- `static/dashboard.css` → Styling
- `static/dashboard.js` → Event handler

### Data
- `research_trades.csv` → With run_id, separators
- `research_runs.csv` → Run summaries
- `signal_health.csv` → With run_id, separators
- `execution_quality.csv` → With run_id, separators

## Implementation Status

✓ Part 1: Frontend UI (New Run button, run ID display)
✓ Part 2: Backend reset endpoint (POST /api/reset)
✓ Part 2.5: Run finalization snapshot
✓ Part 3: CSV structure update (run_id in every row)
✓ Part 4: Persistent data layer
✓ Part 5: Frontend reset handler
✓ Part 6: Run ID display
✓ Part 7: Data migration (automatic)
✓ Part 8: Expected results
✓ Part 9: Files modified

**PHASE 29 STATUS: COMPLETE ✓**

See PHASE29_IMPLEMENTATION.md for full details.
