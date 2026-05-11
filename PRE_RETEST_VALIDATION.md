# Pre-Retest Validation Checklist

**Date:** Tue Apr 28, 2026 14:16 MST  
**Campaign:** DJ_CONFIRMATION_TEST_LDEBRAINV1  
**Status:** 🟢 **ALL CHECKS PASS**

---

## 1. ✅ Server Restarted

**Action:** Killed old process, started new server  
**Command:** `cd /Users/rrg/rrg && nohup node server.js > /tmp/server.log 2>&1 &`  
**Result:** Server started successfully

---

## 2. ✅ Server Running

**Check:** Process verification  
**Log output:**
```
[dotenv@17.3.1] injecting env (12) from .env
Loaded 3 leads from CSV: /Users/rrg/rrg/shannon_cooper_150.csv
RRG Intent Engine running on http://127.0.0.1:3000
CSV: /Users/rrg/rrg/shannon_cooper_150.csv
Logging to: /Users/rrg/rrg/logs/rrg-openai.log
```

**Status:** ✅ RUNNING

---

## 3. ✅ Signature Verification ON

**Check:** Log confirms verification enabled  
**Log output:**
```
Webhook Signature Verification: ✓ ON
```

**Verification method:** Ed25519 signature verification  
**Status:** ✅ ENABLED (not bypassed)

---

## 4. ✅ LDEBRAINV1 Ready

**Check:** Engine loaded and ready  
**Log output:**
```
LDEBRAINV1: ✓ Ready
```

**Status:** ✅ READY

**Code changes loaded:**
- ✅ Home satisfaction signal detection
- ✅ Alert level calculation (neutral signals excluded)
- ✅ Action always "send" (not "escalate")
- ✅ Tier 1 alert + SMS independence

---

## 5. ✅ D.J. State Reset (if needed)

**Previous:** D.J. had stage 3 (multi-turn conversation)  
**Current:** Fresh dry test ran against same phone  
**Decision:** Can run fresh test OR reset state if needed

**D.J. phone:** +16268313336  
**D.J. lead_id:** DJ001  
**State file:** `/Users/rrg/rrg/logs/ldebrainv1-state.jsonl`

**Action:** Fresh test can proceed (state will increment normally)

---

## 6. ✅ Webhook Endpoint Ready

**Log output:**
```
Webhook endpoint: POST /webhook/telnyx
```

**URL:** `https://vitamins-doorstop-esophagus.ngrok-free.dev/webhook/telnyx`  
**Status:** ✅ READY

---

## 7. ✅ ngrok Tunnel Confirmed

**Tunnel URL:** `https://vitamins-doorstop-esophagus.ngrok-free.dev`  
**Status:** ✅ ACTIVE

---

## 8. ✅ Telnyx SMS Configured

**Log output:**
```
Telnyx SMS: ✓ Configured
```

**From number:** +16282101103  
**API key:** Configured in .env  
**Status:** ✅ READY

---

## 9. ✅ Leads Loaded

**Log output:**
```
Loaded 3 leads from CSV: /Users/rrg/rrg/shannon_cooper_150.csv
```

**Leads in CSV:**
- D.J. (DJ001, +16268313336) ✅
- Pam (PAM001, +16025551234) — NOT texting yet
- Heather (HEA001, +16025559876) — NOT texting yet

**Protection:** Only D.J. will be texted in this test

---

## 10. ✅ Logging Ready

**Log location:** `/Users/rrg/rrg/logs/rrg-openai.log`  
**Status:** ✅ Ready to capture all events

---

## Pre-Retest Summary

| Component | Status | Notes |
|---|---|---|
| Server | ✅ RUNNING | Process active, logs flowing |
| Signature verification | ✅ ON | Ed25519, not bypassed |
| LDEBRAINV1 | ✅ READY | All fixes loaded |
| Webhook | ✅ READY | /webhook/telnyx listening |
| ngrok tunnel | ✅ ACTIVE | https://vitamins-doorstop-esophagus.ngrok-free.dev |
| Telnyx SMS | ✅ CONFIGURED | API ready |
| Leads | ✅ LOADED | D.J. protected, Pam/Heather protected |
| Logging | ✅ READY | rrg-openai.log ready |

---

## Ready for D.J. Live Retest ✅

**All validations pass. Awaiting D.J. approval to proceed with:**
1. Send D.J. new first-outreach SMS (or continue from previous)
2. D.J. replies
3. Webhook processes reply
4. Validate:
   - Signals detected correctly
   - Tier 1 alert (if warm/hot signal)
   - SMS response sent
   - Alert + SMS independent

---

**Status:** 🟢 **PRE-RETEST VALIDATION COMPLETE**

**Awaiting:** D.J. approval to send/retest

**Note:** Do not text Pam, Heather, or Shannon contacts.
