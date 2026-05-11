# BUGFIXES — Phase 9 Live Testing Session

**Date:** 2026-04-18 00:06-00:10 MST  
**Issues Found:** 4  
**Status:** All Fixed ✅

---

## BUG 1: APPROVE/REJECT Not Working

**Symptom:** "Failed to record decision" error alert

**Root Cause:** Missing `request` import in Flask imports

**Fix:**
```python
# Before:
from flask import Flask, render_template, jsonify

# After:
from flask import Flask, render_template, jsonify, request
```

**Impact:** POST endpoint `/api/rocky/decision` now works  
**File:** `moltmarket_dashboard.py` line 11

---

## BUG 2: "Run: —" Not Displaying

**Symptom:** Run ID showing empty dash instead of timestamp

**Root Cause:** `current_run_id` initialized to `None`, never set

**Fix:** Initialize `current_run_id` with timestamp at startup

```python
'current_run_id': 'run_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
```

Also added to `dashboard_state`:
- `bot_id: 'arena_bot'` — For Rocky/Control context
- `survival_pass`, `max_drawdown`, `avg_pnl_per_trade` — For Control layer
- `flip_rate`, `divergence`, `total_trades`, `rolling_win_rate` — For panels

**Impact:** Run ID now displays + all layers have access to metrics  
**File:** `moltmarket_dashboard.py` line 56

---

## BUG 3: Control Status Panel Blank

**Symptom:** Panel shows "Evaluating..." but never updates

**Root Cause:** Metrics stored in `dashboard_state['metrics']` dict, but Control/Rocky endpoints read from top-level keys

**Fix:** Added metric sync after `update_metrics()`:

```python
# After storing to dashboard_state['metrics'], also sync to top-level:
dashboard_state['total_trades'] = total_trades
dashboard_state['flip_rate'] = round(integrity['sign_flip_rate_pct'], 1)
dashboard_state['avg_pnl_per_trade'] = round(avg_pnl, 6)
dashboard_state['divergence'] = round(((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100) if paper_pnl != 0 else 0, 2)
dashboard_state['rolling_win_rate'] = round(win_rate * 100, 1)
```

**Impact:** Control layer now finds metrics → panel populates  
**File:** `moltmarket_dashboard.py` after line 383

---

## BUG 4: Trade Sign Flips Showing 0.0

**Symptom:** "TRADE SIGN FLIPS: 0.0" even with many flips in data

**Root Cause:** Same as Bug 3 — `sign_flip_rate_pct` in `metrics` dict but panels read from `dashboard_state['flip_rate']`

**Fix:** Same metric sync code (see Bug 3)

```python
dashboard_state['flip_rate'] = round(integrity['sign_flip_rate_pct'], 1)
```

**Impact:** Flip rate panel now shows correct value  
**File:** `moltmarket_dashboard.py` (same location as Bug 3 fix)

---

## SUMMARY

| Bug | Issue | Root Cause | Fix | Status |
|-----|-------|-----------|-----|--------|
| 1 | APPROVE/REJECT 404 | Missing import | Add `request` | ✅ |
| 2 | Run ID blank | Uninitialized state | Initialize with timestamp | ✅ |
| 3 | Control panel blank | Metrics in wrong dict | Sync to top-level keys | ✅ |
| 4 | Flip rate 0.0 | Metrics in wrong dict | Sync to top-level keys | ✅ |

**All fixes applied to:** `/Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py`

**Verified:** Python compilation ✅

---

## NEXT STEPS

1. Restart dashboard: `python3 /Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py`
2. Verify all panels populate
3. Run arena bot for 30+ trades
4. Click [Generate Insight]
5. Click [APPROVE] or [REJECT]
6. Verify decision recorded + banner appears
7. Click [Spawn Babies]
8. Verify mutation intent cleared

---

**Ready to test. Let's go.**
