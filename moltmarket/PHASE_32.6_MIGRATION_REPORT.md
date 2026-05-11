# PHASE 32.6: PORT MIGRATION + PERSISTENT CONFIG (LOCK TO 5050)

**Status: ✓ COMPLETE**

## Objective
Move entire MOLTmarket system off port 5000 (conflicts with macOS AirTunes) and permanently standardize on port 5050.

## Changes Made

### 1. **moltmarket_dashboard.py**
- **Added PORT constant** (line 24):
  ```python
  # PHASE 32.6: Port Configuration
  # Port 5000 is reserved by macOS AirTunes — DO NOT USE
  PORT = 5050
  ```
- **Updated app.run()** (line 927):
  ```python
  # Before:  app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
  # After:   app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)
  ```
- **Updated startup message** (line 897):
  ```python
  # Before:  print("🎯 Dashboard: http://localhost:5000")
  # After:   print(f"🎯 Dashboard: http://127.0.0.1:{PORT}")
  ```

### 2. **test_promotion_endpoint.py**
- **Added PORT constant** (line 23):
  ```python
  PORT = 5050
  BASE_URL = f"http://127.0.0.1:{PORT}"
  ```
- **Before:** `BASE_URL = "http://localhost:5000"`
- **After:** `BASE_URL = f"http://127.0.0.1:{PORT}"`
- **Updated docstring** to reference port 5050

### 3. **test_reset_fix.py**
- **Added PORT constant** (line 23):
  ```python
  PORT = 5050
  BASE_URL = f"http://127.0.0.1:{PORT}"
  ```
- **Before:** `BASE_URL = "http://localhost:5000"`
- **After:** `BASE_URL = f"http://127.0.0.1:{PORT}"`

## Verification Results

### Port Binding
✅ Server successfully binds to `http://127.0.0.1:5050`
- No conflicts with AirTunes (macOS port 5000)
- Confirmed via Flask startup: "Running on http://127.0.0.1:5050"

### Codebase Scan
✅ **Zero hardcoded references to port 5000** in production code
- Verified across: `*.py`, `*.js`, `*.html` files
- All references now use `PORT` constant
- Only comments mention 5000 (AirTunes warning)

### Frontend Configuration
✅ **Dashboard.js uses relative API paths**
- No absolute URLs hardcoded
- All API calls use `/api/...` pattern
- Auto-adapts to any port

### Critical Routes Verified
✅ All 15 Flask routes properly registered:
- `/api/metrics` → 200 OK, valid JSON
- `/api/trades` → 200 OK, valid JSON
- `/api/equity-curves` → 200 OK, valid JSON
- `/api/breakdowns` → 200 OK, valid JSON
- `/api/nursery/spawn` → registered
- `/api/nursery/leaderboard` → registered
- `/api/nursery/promote/<variant_id>` → registered
- `/api/nursery/status` → registered
- `/api/health` → registered
- And 6 more utility routes

### Metrics Reset Validation
✅ Metrics reset correctly on new run:
- total_trades resets to 0
- trade_sign_flips resets to 0
- avg_pnl resets to 0
- slippage resets to 0

### Dashboard Browser Access
✅ Opens at: `http://127.0.0.1:5050`
✅ Live metrics display working
✅ New Run button triggers reset
✅ Metrics increment with trades

## Configuration Lock

### Permanent Port Assignment
```python
# Top of moltmarket_dashboard.py (line 24)
PORT = 5050  # Port 5000 is reserved by macOS AirTunes — DO NOT USE
```

### All Future References Use Constant
All future code must:
1. Import/reference `PORT` constant
2. Use `f"http://127.0.0.1:{PORT}"` for URLs
3. Never hardcode 5050 directly (use constant for future flexibility)

### Documentation Lock
All startup messages now clearly show:
```
🎯 Dashboard: http://127.0.0.1:5050
```

## Success Criteria - ALL MET ✓

| Criterion | Status | Evidence |
|-----------|--------|----------|
| Server runs on 5050 | ✅ | Flask confirmation + lsof verification |
| No use of port 5000 | ✅ | Full codebase scan (0 results) |
| curl returns 200 | ✅ | All 4 endpoints tested |
| Dashboard works live | ✅ | Browser access verified |
| Metrics reset correctly | ✅ | New Run → metrics = 0 |
| No AirTunes interference | ✅ | Port 5050 is free (5000 was conflict) |
| PORT constant in config | ✅ | Line 24 of moltmarket_dashboard.py |

## Files Modified
1. ✅ `/Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py`
2. ✅ `/Users/rrg/.openclaw/workspace/moltmarket/test_promotion_endpoint.py`
3. ✅ `/Users/rrg/.openclaw/workspace/moltmarket/test_reset_fix.py`

## Test Files Created (for verification)
- `verify_port.py` - Verify PORT constant and routes
- `run_tests.py` - Automated endpoint testing
- `start_dashboard.sh` - Simple startup script
- `PHASE_32.6_MIGRATION_REPORT.md` - This report

## Migration Path

### To Run Dashboard
```bash
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 moltmarket_dashboard.py
# Server runs on: http://127.0.0.1:5050
```

### To Run Tests
```bash
python3 test_promotion_endpoint.py --status
# Connects to: http://127.0.0.1:5050
```

### To Verify Configuration
```bash
grep "^PORT = " moltmarket_dashboard.py
# Output: PORT = 5050
```

## Notes

### AirTunes Conflict Resolution
- **Problem:** macOS reserves port 5000 for AirTunes/iTunes
- **Solution:** Moved to port 5050 (adjacent, unused)
- **Why not port 5001?** 5050 is a safer choice (less likely to conflict)

### Future-Proofing
The `PORT` constant approach allows:
1. Environment variable override (future)
2. Config file override (future)
3. Documentation clarity (current)
4. Zero hardcoding (current)

## Deployment Checklist

- [x] Update moltmarket_dashboard.py
- [x] Update test files
- [x] Scan for remaining 5000 references
- [x] Verify Flask routes
- [x] Test all 4 critical endpoints
- [x] Verify dashboard browser access
- [x] Verify metrics reset
- [x] Document configuration
- [x] Create verification report
- [x] Lock to PORT constant

**PHASE 32.6 COMPLETE - READY FOR PRODUCTION**
