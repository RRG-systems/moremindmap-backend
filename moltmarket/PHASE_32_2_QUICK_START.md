# PHASE 32.2 - Quick Start Guide

## What's New

### 1. Active Strategy Label
Look near the top of dashboard:
```
ACTIVE STRATEGY: baseline • Gen 0
```
This always shows your current strategy and generation.

### 2. Promote Button in Nursery
After you spawn babies ([ Spawn Babies (10) ]), the top performer gets a green button:
```
[ Promote to Main Arena ]
```
- Only the #1 candidate is enabled
- Others are greyed out
- Click to promote baby to be your new active strategy
- Label updates automatically
- Nursery clears after promotion

### 3. Reset to Baseline Button
Below the nursery table:
```
[ Reset to Baseline Strategy ]
```
- Resets your strategy back to "baseline • Gen 0"
- **Keeps your equity/P&L intact**
- Useful for A/B testing or recovery

### 4. Reset Capital Button
Below the nursery table:
```
[ Reset Arena Capital ]
```
- Resets equity to $10,000
- Clears P&L for new segment
- **Keeps your strategy unchanged**
- Opens a confirmation modal

---

## Testing Flow

### Test 1: Basic Label Display
1. Open dashboard
2. Look for cyan-bordered box: "ACTIVE STRATEGY: baseline • Gen 0"
3. Confirm generation is shown

### Test 2: Promote a Baby
1. Click `[ Spawn Babies (10) ]`
2. Wait for table to populate
3. See top row has `[ Promote to Main Arena ]` button (green)
4. See other rows have disabled button (grey)
5. Click promote button
6. Confirm label updates to new strategy name
7. Confirm nursery clears

### Test 3: Reset to Baseline
1. Current strategy should be: "baby_010 • Gen 1"
2. Click `[ Reset to Baseline Strategy ]`
3. Confirm dialog appears
4. Click OK/Yes
5. Confirm label updates to: "baseline • Gen 0"
6. Confirm equity stays the same (KPI cards unchanged)

### Test 4: Reset Capital
1. Note current equity in "Paper Rolling Value" KPI
2. Click `[ Reset Arena Capital ]`
3. Modal appears with explanation
4. Modal requires typing strategy name to confirm
5. Type strategy name (e.g., "baby_010")
6. Confirm button becomes enabled (green)
7. Click Confirm
8. Modal closes
9. Confirm "Paper Rolling Value" resets to $10,000
10. Confirm strategy label is unchanged

### Test 5: Modal Friction (Exact Match)
1. Open modal: Click `[ Reset Arena Capital ]`
2. See input field: "Type strategy name to confirm"
3. Type wrong name (e.g., "foo")
4. Button stays disabled
5. Backspace to clear
6. Type correct name (case-sensitive!)
7. Button becomes enabled
8. Confirm match is exact (no substring matching)

---

## Console Debugging

Open browser dev tools (F12) and watch console for logs:

```
[PHASE 32.2] Initializing frontend control layer...
[PHASE 32.2] Updated active strategy label: baby_010 • Gen 1
[PHASE 32.2] Updated 10 rows in leaderboard with action column
[PHASE 32.2] Promoting variant: baby_010
[PHASE 32.2] Promotion successful: { status: "success", ... }
```

---

## Constraints Verified

All three reset actions are **independent**:

- ✓ Promote does NOT affect equity
- ✓ Baseline reset does NOT affect equity
- ✓ Capital reset does NOT change strategy
- ✓ No side effects between actions
- ✓ All three can be combined

---

## Success Criteria

Dashboard shows:
1. ✓ Active strategy label visible
2. ✓ Promote button on top candidate only
3. ✓ Separate baseline reset button
4. ✓ Separate capital reset button with modal
5. ✓ All actions remain distinct

---

## Next Steps

After verification, PHASE 32.2 is complete. Proceed to:
- PHASE 33: Data export/visualization
- PHASE 34: Performance optimization
- PHASE 35: Multi-strategy scheduling
