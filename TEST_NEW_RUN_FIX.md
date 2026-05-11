# TEST: PHASE 32.5C - NEW RUN FRONTEND CRASH FIX

## Test Objective
Verify that:
1. No console error on New Run click
2. /api/reset endpoint called successfully
3. All metrics reset to zero immediately
4. Metrics increment correctly on new trades
5. UI fully refreshes from live state

## Pre-Test Checklist
- [ ] Dashboard is open in browser
- [ ] Open browser DevTools Console (F12)
- [ ] Have a few trades already recorded

## Test Steps

### Step 1: Observe Current State
**ACTION**: Take screenshot of current metrics
- Expected: See some trades, PNL, etc.
- Record screenshot as: `BEFORE_reset.png`

### Step 2: Click New Run Button
**ACTION**: 
1. Click "New Run" button
2. Confirm dialog
3. Watch browser console for errors

**EXPECTED**:
- No TypeError in console
- Message: "[PHASE 32.5C] Triggering full dashboard refresh after reset..."
- "New run started: YYYY-MM-DD-HH-MM-SS" notification
- NO error about null.textContent

### Step 3: Check Metrics After Reset
**ACTION**: Wait 1 second, take screenshot
**EXPECTED**: 
```
total_trades = 0
trade_sign_flips = 0
flip_rate = 0%
pnl = $0 (or $10,000.00 depending on display)
equity curve chart clears/restarts
run_id = new timestamp
```
- Record screenshot as: `AFTER_reset.png`

### Step 4: Execute 2 New Trades
**ACTION**: Place 2 quick trades manually or via API
**EXPECTED**: Metrics increment:
- total_trades = 2
- pnl = reflects new trade P&L
- equity curve updates with new data points

- Record screenshot as: `AFTER_2_trades.png`

### Step 5: Check Console
**ACTION**: Copy console log output

**EXPECTED**:
```
[PHASE 29] New Run button clicked
[PHASE 29] Reset complete: 2026-04-16-21-XX-XX
[PHASE 32.5C] Triggering full dashboard refresh after reset...
[pollDashboard] Fetching fresh metrics...
(no errors)
```

## Success Criteria
- ✅ No TypeError crash
- ✅ /api/reset called (check Network tab)
- ✅ All metrics = 0 after reset
- ✅ Metrics increment correctly on new trades
- ✅ UI fully refreshes from backend
- ✅ run_id updated with new timestamp
- ✅ Console shows no errors

## Code Changes Made

### dashboard.js (lines 553-596)

**BEFORE** (problematic):
```javascript
document.getElementById('kpi-pnl').textContent = '$0';  // NULL REFERENCE - element doesn't exist!
document.getElementById('kpi-edge').textContent = '0 bps';  // Destroys .bps-suffix span!
```

**AFTER** (fixed):
```javascript
const safeSetKPI = (id, value) => {
    const el = document.getElementById(id);
    if (el) {  // NULL GUARD
        const firstNode = el.firstChild;
        if (firstNode && firstNode.nodeType === Node.TEXT_NODE) {
            firstNode.textContent = value;  // Preserve child spans
        } else if (!el.querySelector('span')) {
            el.textContent = value;
        }
    }
};

safeSetKPI('kpi-trades', '0');  // No more null errors
// ... etc
```

**New Addition** (force refresh):
```javascript
setTimeout(() => {
    if (typeof pollDashboard === 'function') {
        pollDashboard();  // Re-fetch all metrics from backend
    }
}, 500);
```

## If Tests Fail

### Symptom: Still getting TypeError
- Check if element ID matches dashboard.html
- Run: `grep "id=" moltmarket/templates/dashboard.html | grep kpi`
- Add new elements as needed

### Symptom: Metrics don't reset to 0
- Check backend: `reset_run_state()` called?
- Check DataLayer: `reset_trades_for_new_run()` called?
- Verify /api/reset response includes success

### Symptom: UI doesn't refresh
- Check if `pollDashboard()` function exists
- Check if it's called after timeout
- Verify no errors preventing fetch

## Debugging Commands

```bash
# Check Python reset endpoint
curl -X POST http://localhost:5000/api/reset | jq .

# Check if metrics endpoint returns zeros
curl http://localhost:5000/api/metrics | jq .

# Monitor console
# F12 > Console > Filter "[PHASE"
```
