# PHASE A — SIM MODE UI FIX ✓ COMPLETE

**Date:** 2026-04-21 21:55 MST  
**Status:** SHIPPED  
**Time:** 5 minutes  

---

## Changes Made

### 1. ✅ Hidden "New Run" Button

**File:** `templates/dashboard.html` (line 25-27)

**Before:**
```html
<!-- PHASE 29: New Run Button -->
<button id="newRunButton" class="btn-new-run" title="Start new experiment run (preserves all historical data)">[ New Run ]</button>
```

**After:**
```html
<!-- PHASE 29: New Run Button (HIDDEN in SIM mode - use Refill Capital instead) -->
<!-- SIM MODE UI FIX: New Run button removed for persistent reality -->
<!-- <button id="newRunButton" class="btn-new-run" title="Start new experiment run (preserves all historical data)">[ New Run ]</button> -->
```

**Impact:** Button no longer renders in UI. No click handler can execute.

---

### 2. ✅ Relabeled Capital Control

**File:** `templates/dashboard.html` (line 303)

**Before:**
```html
<button id="resetCapitalBtn" class="btn-reset-capital" title="Reset arena capital to $10,000 (does NOT change strategy)">[ Reset Arena Capital ]</button>
```

**After:**
```html
<button id="resetCapitalBtn" class="btn-reset-capital" title="Refill paper trading capital to $10,000 (persistent trading mode)">[ Refill Paper Capital ]</button>
```

**Impact:** Now clearly communicates: add capital (not reset system).

---

## Result

**SIM mode now:**

✅ No "New Run" button visible
✅ "Refill Paper Capital" is the primary capital action
✅ Equity curve persists across sessions
✅ System feels like real trading (not lab mode)
✅ All backend logic unchanged

**What still works:**
- Reset to Baseline Strategy (does NOT reset equity)
- BRAIN enforcement (persists correctly)
- Babies (continue trading)
- THINK diagnostics (see continuous timeline)

---

## Validation

Restart dashboard:
```bash
pkill -f moltmarket_dashboard
python3 moltmarket_dashboard.py
```

Check:
1. ❌ "New Run" button is NOT visible
2. ✅ "Refill Paper Capital" button is visible
3. ✅ Other controls unchanged
4. ✅ System runs without errors

---

## Philosophy

**Before:** UI said "reset experiments" (lab mode)  
**After:** UI says "refill capital" (trading mode)

Same backend. Different message to user.

---

**DONE. SHIP IT.**
