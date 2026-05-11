# SESSION 4 BLOCKER — FOR MORNING 2026-04-22

**Status:** Two working panels need fixes + UI reorg

---

## What's Working ✅

**Backend endpoints verified:**
```bash
curl http://localhost:5050/api/brain/status
# Returns: {"state":"THROTTLE", "reason_code":"instability_warning", ...}

curl -X POST http://localhost:5050/api/think/query -H "Content-Type: application/json" -d '{"query":"why not trading"}'
# Returns: {"status":"success", "answer":"...", "confidence":1.0, ...}
```

Both endpoints are **alive and working correctly**.

---

## What's Broken ❌

### 1. BRAIN Panel JavaScript Handler
- Endpoint works → JS handler fails
- Error: `"Cannot read properties of undefined (reading 'answer')"`
- **Fix needed:** Check `static/think_brain_panel_handler.js` line ~143
  - Verify response parsing
  - May need to map `/api/brain/status` fields correctly to display

### 2. THINK Panel JavaScript Handler  
- Endpoint works → JS handler fails
- Same error pattern
- **Fix needed:** Same file, check response parsing
  - Endpoint returns: `{status, answer, confidence, patterns, adjustment}`
  - Handler may expect different field names

### 3. Panel Position
- BRAIN + THINK panels are in the middle of the page
- Should be: **directly above "Equity Curves Chart" section**
- Lines in HTML: BRAIN at 366, THINK at 374, Equity Curves at 122
- **Fix needed:** Cut BRAIN+THINK blocks and insert before line 122

---

## Quick Debug Checklist

1. **Open browser DevTools → Network tab**
2. **Send a THINK query**
3. **Look at the `/api/think/query` response**
4. **Compare response structure to what JS expects**
5. **Fix the parsing in `think_brain_panel_handler.js`**

---

## Files to Fix (Morning)

1. `static/think_brain_panel_handler.js`
   - Line ~100-150: BRAIN response parsing
   - Line ~150-200: THINK response parsing
   - Make sure field names match

2. `templates/dashboard.html`
   - Cut lines 366-420 (BRAIN + THINK panels)
   - Insert before line 122 (before Equity Curves)

---

## Expected Outcome

After fixes:
- ✅ BRAIN panel shows enforcement state (STOP/THROTTLE/NORMAL/FLAT)
- ✅ THINK panel accepts queries and shows responses
- ✅ Both panels positioned above Equity Curves chart
- ✅ Clean, uncluttered dashboard layout

---

**Time estimate:** 15-20 minutes (parsing + repositioning)

**Blocker severity:** MEDIUM (system works, UI broken, not critical)
