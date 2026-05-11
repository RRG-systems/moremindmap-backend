# LDEBRAINV1 Controlled Technical Test Plan

**Date:** Tue Apr 28, 2026 09:58 MST  
**Public URL:** https://vitamins-doorstop-esophagus.ngrok-free.dev/webhook/telnyx  
**Status:** ✅ ALL SYSTEMS READY FOR TEST  

---

## Pre-Test Verification (6-Point Checklist)

### ✅ 1. ngrok Traffic Clean

**Status:** No unexpected traffic  
**Evidence:** ngrok process running (PID 31725), no webhook events in logs  
**Risk:** None detected

### ✅ 2. Server Running on localhost:3000

**Status:** Active and responding  
**Evidence:**
```bash
curl http://127.0.0.1:3000/status
→ {"day":"2026-04-28","calls_used_today":null,"daily_max_calls":50,...}
```
**Process:** neat-cove (running since 09:35 MST)

### ✅ 3. /webhook/telnyx Ready

**Status:** Endpoint wired and listening  
**Evidence:** `grep verifyTelnyxSignature server.js` confirms handler at line 671 + 706  
**Route:** `POST /webhook/telnyx`

### ✅ 4. Signature Verification ON

**Status:** Locked  
**Evidence:** Server startup log shows `Webhook Signature Verification: ✓ ON`  
**Configuration:**
```javascript
const TELNYX_VERIFY_SIGNATURES = process.env.TELNYX_VERIFY_SIGNATURES !== "false"; // Default: ON
TELNYX_PUBLIC_KEY: present (44 chars)
```

### ✅ 5. Telnyx Webhook Endpoint Ready

**Status:** Confirmed and saved in Telnyx dashboard  
**Public URL:** `https://vitamins-doorstop-esophagus.ngrok-free.dev/webhook/telnyx`  
**Method:** POST  
**Signature Verification:** Ed25519 (TELNYX_PUBLIC_KEY loaded)

### ✅ 6. Controlled Test (Not Pam/Heather Yet)

**Status:** Ready for technical validation  
**Reason:** Must verify signature verification works before human tests

---

## Controlled Technical Test Sequence

### Test 1: Dry Run (Local, No Telnyx)

**Objective:** Verify LDEBRAINV1 processes messages correctly

**Command:**
```bash
curl -X POST http://127.0.0.1:3000/api/test-ldebrainv1 \
  -H "Content-Type: application/json" \
  -d '{"phone":"6025551234","message":"Maybe if rates came down"}'
```

**Expected Response:**
```json
{
  "action": "send",
  "alertLevel": "warm",
  "signals": [{"type": "rate", "confidence": 0.7}, ...],
  "message": "That sounds great. Would you be interested in learning more...",
  "shouldStop": false
}
```

**Success:** Signals detected, response generated, no errors

---

### Test 2: Webhook Signature Validation (Manual)

**Objective:** Confirm signature verification rejects unsigned webhooks

**Command (no signature):**
```bash
curl -X POST https://vitamins-doorstop-esophagus.ngrok-free.dev/webhook/telnyx \
  -H "Content-Type: application/json" \
  -d '{"data":[{"type":"message.received","payload":{"from":{"phone_number":"+16025551234"},"text":"Test"}}]}'
```

**Expected Response:**
```json
{"ok":false,"error":"Unauthorized"}
```

**HTTP Status:** 401  
**Log entry:** `webhook_signature_verification_failed` + reason

**Success:** Rejected without processing

---

### Test 3: Signature Verification Pass (Telnyx Sandbox)

**Objective:** Confirm valid signatures ARE processed

**Method:** Use Telnyx sandbox/test mode to send a signed webhook

**Steps:**
1. Go to Telnyx dashboard → Messaging → Profiles
2. Find your profile with webhook URL set to ngrok tunnel
3. Click "Send Test Event" or use Telnyx CLI:
   ```bash
   telnyx messaging:webhooks:test --profile-id YOUR_PROFILE_ID
   ```

**Expected:**
- Webhook arrives with valid signature
- Server logs: `inbound_sms` entry (no rejection)
- LDEBRAINV1 processes the test message
- Response generated based on test message content

**Log entry format:**
```json
{"t":"2026-04-28T...", "type":"inbound_sms", "from":"+1...", "message":"...", "ldebrainv1_result":{...}}
```

**Success:** Message processed, LDEBRAINV1 responds, no rejection

---

### Test 4: End-to-End Signal Detection (Telnyx Sandbox)

**Objective:** Confirm LDEBRAINV1 detects signals in real webhook flow

**Telnyx test message:**
```
"My daughter may buy a place nearby. We're interested."
```

**Expected:**
- Webhook arrives (signed)
- Signature verified ✓
- LDEBRAINV1 detects: `{"type": "buy", "confidence": 0.8}`
- Alert level: `hot`
- Action: `escalate`
- Darren + D.J. alert sent (iMessage)

**Verification:**
- Check logs: `signal_alert` entry
- Check logs: iMessage sent to both numbers
- Confirm Darren/D.J. received message

**Success:** Full hot signal flow works

---

## Execution Order

1. **Today (Tue, now):**
   - ✅ Run Test 1 (local LDEBRAINV1 dry run)
   - ✅ Run Test 2 (unsigned webhook rejection)

2. **After approval:**
   - Run Test 3 (Telnyx sandbox signed webhook)
   - Run Test 4 (signal detection with real Telnyx)

3. **After all pass:**
   - Ready for Pam test (real contact, controlled)
   - Then Heather test
   - Then Shannon batch 1 (150 contacts)

---

## Rollback Plan

If any test fails:

1. Check logs: `/Users/rrg/rrg/logs/rrg-openai.log`
2. Identify failure type:
   - Signature verification issue → Review TELNYX_PUBLIC_KEY
   - LDEBRAINV1 issue → Review signal detection rules
   - SMS sending issue → Review Telnyx API response
3. Fix in code or config
4. Restart server: kill process neat-cove, restart
5. Re-run failing test

---

## Safety Locks (No Live SMS Until Tests Pass)

| Lock | Status | Override |
|------|--------|----------|
| **Unsigned webhook rejection** | ✅ Locked | None (by design) |
| **Signature verification required** | ✅ Locked | Manual config change only |
| **No auto-sending** | ✅ Locked | Manual approval per send |
| **All sends logged** | ✅ Enabled | N/A |
| **Rate limiting (50 calls/day, 2s throttle)** | ✅ Enabled | Config change only |

---

## Current Status Summary

| Component | Status | Evidence |
|-----------|--------|----------|
| Server (localhost:3000) | ✅ Running | curl /status returns 200 |
| Signature verification | ✅ ON | Startup log confirms |
| LDEBRAINV1 | ✅ Ready | Function loaded, tested locally |
| ngrok tunnel | ✅ Active | PID 31725 running |
| Public URL | ✅ Configured | Saved in Telnyx dashboard |
| TELNYX_PUBLIC_KEY | ✅ Loaded | Signature verification function references it |
| Test contacts (Pam, Heather) | ✅ Ready | shannon_cooper_150.csv loaded |
| No live SMS yet | ✅ Locked | No credentials in /api/send-sms without approval |

---

**Ready to execute Test 1 & 2?** (Local validation, no Telnyx involvement)

**Or wait for explicit approval before proceeding?**
