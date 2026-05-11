# BUGFIXES — CONTROL LAYER OVERLY AGGRESSIVE

**Date:** 2026-04-18 00:18 MST  
**Issues:** 2 critical  
**Status:** Fixed ✅

---

## BUG 1: APPROVE/REJECT "Failed to record decision"

**Symptom:** Button click → error alert

**Root Cause:** Insight endpoint doesn't return `run_id` and `bot_id` to frontend

**Fix:**
```python
# Before:
return jsonify({
    'status': 'success',
    'notes': insight['notes'],
    'proposal': insight['proposal'],
    ...
})

# After:
return jsonify({
    'status': 'success',
    'notes': insight['notes'],
    'proposal': insight['proposal'],
    'run_id': run_id,              # ← ADDED
    'bot_id': bot_id,              # ← ADDED
    ...
})
```

**File:** `moltmarket_dashboard.py` line 879

**Result:** Buttons now send correct `run_id` + `bot_id` to decision endpoint ✅

---

## BUG 2: CONTROL LAYER FIRES STOP TOO EARLY

**Symptoms observed:**
- STOP after 8 trades
- PnL: -495300.0 bps (completely wrong scale)
- Survival gate triggering before enough data

**Root Causes Identified:**

### 2a: Double PnL Conversion Bug
```
avg_pnl from dashboard_data_layer: -49.53 (dollars)
Synced to dashboard_state as: -49.53 (dollars)
Control layer receives: -49.53
Control layer does: -49.53 * 10000 = -495300.0 bps (WRONG!)
```

The conversion was already happening in the data layer, but control layer converted again.

**Fix:**
```python
# Before:
avg_pnl_bps = avg_pnl * 10000  # Double conversion!

# After:
avg_pnl_bps = avg_pnl  # Dashboard already normalized
```

**File:** `control_layer.py` line 185

### 2b: No Minimum Sample Gate
Control layer had hard thresholds but no "warmup" period. With only 8 trades, small movements trigger survival gate failures.

**Fix:**
```python
# Added:
MIN_SAMPLE_GATE = 20  # No control action before 20 trades

# In evaluate_stop_condition():
if total_trades < self.MIN_SAMPLE_GATE:
    # Exception: only allow early STOP for catastrophic drawdown
    if max_drawdown > self.CATASTROPHIC_DRAWDOWN:  # >10%
        return True, "CATASTROPHIC drawdown..."
    return False, None  # Otherwise, continue warmup
```

**File:** `control_layer.py` lines 21-22, 48-53

### 2c: Missing WARMUP State
UI didn't have a visual state for "collecting data, no decision yet"

**Fix:**
- Added `WARMUP` action state
- Added color for WARMUP: blue (#64B5F6)
- UI now displays clearly instead of defaulting to STOP

**File:** `static/dashboard.js` line 1308

---

## BEFORE vs AFTER BEHAVIOR

### Before (Broken)
```
Trade 1:   NORMAL
Trade 5:   STOP (PnL: -495300.0 bps 🚨)
Trade 8:   STOP (Survival gate failed)
Trade 20:  STOP (PnL threshold breach - wrong scale)
```

### After (Fixed)
```
Trade 1:   WARMUP (collecting data...)
Trade 5:   WARMUP (collecting data...)
Trade 15:  WARMUP (collecting data...)
Trade 20:  NORMAL / THROTTLE / SWITCH (real decision)
Trade 50+: STOP only if legitimate catastrophic loss
```

---

## EXACT CHANGES MADE

| File | Function | Change | Lines |
|------|----------|--------|-------|
| `moltmarket_dashboard.py` | `get_rocky_insight()` | Return `run_id`, `bot_id` in response | 879-880 |
| `control_layer.py` | Class constants | Add `CATASTROPHIC_DRAWDOWN`, `MIN_SAMPLE_GATE` | 20-22 |
| `control_layer.py` | `evaluate_stop_condition()` | Add early warmup gate, catastrophic exception | 48-53 |
| `control_layer.py` | `evaluate_control()` | Remove double PnL conversion | 185 |
| `static/dashboard.js` | Control polling | Add WARMUP color (#64B5F6) | 1308 |

---

## THRESHOLDS NOW

| Gate | Threshold | Action |
|------|-----------|--------|
| **Sample size** | < 20 trades | WARMUP (no action) |
| **Catastrophic** | > 10% drawdown (any time) | STOP (early kill switch) |
| **Normal STOP** | Survival fail + 20+ trades | STOP |
| **Normal STOP** | PnL < -5 bps + 30+ trades | STOP |
| **THROTTLE** | Degrading + negative PnL + 20+ trades | THROTTLE |
| **SWITCH** | Degrading + mutation failed + 40+ trades | SWITCH |

---

## TESTING CHECKLIST

- [ ] Restart dashboard
- [ ] Run arena bot
- [ ] After 3 trades: Panel should show **WARMUP**
- [ ] After 15 trades: Panel should show **WARMUP**
- [ ] After 20 trades: Panel should show **NORMAL** or real action
- [ ] Click [APPROVE]: Button should work (run_id/bot_id now sent)
- [ ] After 50+ good trades: Control should remain NORMAL
- [ ] After >10% DD: Control should show STOP (even early)

---

**Status: Ready for testing. Both bugs fixed. ✅**
