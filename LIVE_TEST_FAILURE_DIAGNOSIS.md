# Live Test Failure Diagnosis

**Date:** Tue Apr 28, 2026 14:21 MST / 21:19 UTC  
**Message:** "We love our home"  
**Status:** 🔴 **CRITICAL FAILURE - STALE PROCESS**

---

## Evidence from Live Webhook (21:19:12.807Z)

### Exact LDEBRAINV1 Result Returned:

```json
{
  "action": "escalate",
  "message": "Thanks for getting back to us. Feel free to reply with any questions.",
  "alertLevel": "hot",
  "shouldStop": false,
  "signals": [
    {"type": "buy", "confidence": 0.8}
  ],
  "confidenceScore": 0.3
}
```

### Expected LDEBRAINV1 Result:

```json
{
  "action": "send",
  "message": "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?",
  "alertLevel": "cold",
  "shouldStop": false,
  "signals": [
    {"type": "home_satisfaction", "confidence": 0.8}
  ]
}
```

---

## Root Cause Analysis

### Problem #1: Signals Wrong

**Live:** `[{"type": "buy", "confidence": 0.8}]`  
**Expected:** `[{"type": "home_satisfaction", "confidence": 0.8}]`

**Issue:** LDEBRAINV1 is still detecting "home" as a buy signal, not home_satisfaction.

### Problem #2: Alert Level Wrong

**Live:** `hot`  
**Expected:** `cold`

**Issue:** Buy signal at 0.8 confidence → hot alert (because neutral signals not filtered from getAlertLevel)

### Problem #3: Action Wrong

**Live:** `escalate`  
**Expected:** `send`

**Issue:** Still returning conditional escalate instead of always "send"

### Problem #4: Message Generic Fallback

**Live:** "Thanks for getting back to us..."  
**Expected:** "That's wonderful to hear. Are you mostly planning to stay put..."

**Issue:** No home_satisfaction response route triggered (because signal not detected)

---

## Why Live Doesn't Match Dry Tests

### Dry Test (earlier today):
- ✅ home_satisfaction detected correctly
- ✅ cold alert level
- ✅ "wonderful" response
- ✅ NO alert fired

### Live Webhook (just now):
- ❌ buy detected (WRONG)
- ❌ hot alert level (WRONG)
- ❌ Generic response (WRONG)
- ❌ Alert fired (WRONG)

**Why the difference?** The live webhook is using OLD code, not the fixes I applied.

---

## Process Status Check

### Current Process:

```
PID:     33294
Started: 12:03 PM (21:19 UTC in 24-hour format, but incorrect)
Command: node server.js
```

**Problem:** This process started BEFORE I restarted the server. It's the OLD nohup process still running old code.

### What Happened:

1. I killed old process: `pkill -f "node /Users/rrg/rrg/server.js"` ✓
2. Started new process: `nohup node server.js > /tmp/server.log 2>&1 &` ✓
3. But: The OLD process from earlier (12:03 PM local time) is STILL RUNNING
4. The NEW process I started is NOT running

**The new server never started or crashed immediately.**

---

## Why Fixes Didn't Apply

The live webhook path uses the OLD server process, which:
- ✅ Has old ldebrainv1.js (no home_satisfaction detection)
- ✅ Has old alert level logic (neutral signals included)
- ✅ Has old action logic (conditional escalate)
- ✅ Has no tier1-alert filtering

When I fixed ldebrainv1.js and tier1-alert-routing.js, the OLD process didn't reload them (Node.js requires restart to load new module files).

---

## 13 Diagnosis Questions Answered

### 1. What did LDEBRAINV1 return for live "we love our home"?

```json
{
  "action": "escalate",
  "alertLevel": "hot",
  "signals": [{"type": "buy", "confidence": 0.8}]
}
```

### 2. What exact signals object was returned?

```json
[{"type": "buy", "confidence": 0.8}]
```

### 3. What exact alert_level was returned?

`"hot"`

### 4. What exact action was returned?

`"escalate"`

### 5. Which function decided to fire Tier 1 alert?

`shouldSendTier1Alert()` in tier1-alert-routing.js (evaluated alert_level === "hot")

### 6. What condition evaluated true?

`alertLevel === "hot"` in tier1-alert-routing.js

### 7. Did tier1-alert-routing.js receive home_satisfaction/staying_put but still alert?

No - because LDEBRAINV1 never detected home_satisfaction signal (returned buy instead).

### 8. Did old code or cached process run instead of updated code?

**YES - OLD CACHED PROCESS.**

### 9. Was server actually restarted after latest code changes?

**NO.** The OLD process (PID 33294) is still running. My restart didn't work because the new process crashed or didn't start.

### 10. Did the live path use the same LDEBRAINV1 file as the dry tests?

No. Live used OLD in-memory module from OLD process. Dry tests used NEW module loaded fresh.

### 11. Why was no SMS response sent?

Because action="escalate", which triggers alert but skips SMS send in webhook handler.

### 12. Did alert logic return early before sendSms?

Yes. Line in server.js:
```javascript
if (result.action === "send" && result.message) {
  await sendSmsViaTelnyx(...);  // NOT executed because action="escalate"
}
```

### 13. Was sendSms attempted and failed, or never called?

**Never called.** The webhook sees action="escalate" and skips the SMS send block entirely.

---

## Confirmation: The Real Problem

**The live server process is 1+ hours old, still running cached old LDEBRAINV1 module.**

When I:
1. Modified ldebrainv1.js (added home satisfaction)
2. Modified tier1-alert-routing.js (filtered home_satisfaction from alerts)
3. Modified ldebrainv1.js again (fixed alert level calculation)
4. Modified ldebrainv1.js again (fixed action to always "send")

The OLD running process NEVER reloaded these changes. It's still using the in-memory JavaScript modules from startup.

---

## Fix Required

**Forcefully kill ALL node processes and restart completely fresh:**

```bash
killall -9 node  # Force kill all node processes
sleep 2
cd /Users/rrg/rrg
node server.js   # Run in foreground OR use nohup properly
```

---

## Post-Fix Validation

After fresh restart:
1. Run dry test again (verify it still works)
2. Run simulated webhook test locally
3. Verify "we love our home" → home_satisfaction, no alert, SMS response
4. Then approve D.J. live retest

---

**Status:** 🔴 **STALE PROCESS CONFIRMED - RESTART NEEDED**
