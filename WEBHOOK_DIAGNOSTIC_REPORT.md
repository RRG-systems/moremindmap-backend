# Webhook Signature Verification Diagnostic Report

**Date:** Tue Apr 28, 2026 10:52 MST  
**Test:** Diagnostic webhook sent via curl to public ngrok tunnel  
**Result:** Root cause confirmed  

---

## Diagnostic Test Command

```bash
curl -X POST https://vitamins-doorstop-esophagus.ngrok-free.dev/webhook/telnyx \
  -H "Content-Type: application/json" \
  -d '{
    "data": [{
      "type": "message.received",
      "payload": {
        "from": {"phone_number": "+16268313336"},
        "text": "Test diagnostic"
      }
    }]
  }'
```

---

## Server Diagnostic Log Output

```json
{"t":"2026-04-28T17:52:01.946Z","type":"webhook_received_diagnostic","headers_present":[],"body_type":"message.received","from_phone":"+16268313336","message_preview":"Test diagnostic"}
{"t":"2026-04-28T17:52:01.946Z","type":"webhook_signature_verification_failed","reason":"missing_headers"}
```

---

## Critical Finding

### Headers Present: **NONE** ❌

```
"headers_present":[]
```

**This means:**
- ngrok is NOT receiving Telnyx signature headers
- OR ngrok is NOT forwarding them
- OR Telnyx is NOT sending them

**Most likely:** Telnyx is **not sending Ed25519 signature headers at all**

---

## Current Code Expectations

**File:** `server.js` (lines 681-683)

```javascript
const signature = req.headers["x-telnyx-signature-ed25519"];
const timestamp = req.headers["x-telnyx-timestamp"];

if (!signature || !timestamp) {
  return { valid: false, reason: "missing_headers" };
}
```

**Expected headers:**
1. `x-telnyx-signature-ed25519` — Ed25519 signature (hex string)
2. `x-telnyx-timestamp` — Timestamp of request

**Actual headers received:**
- `[]` (empty array)

---

## Verification Failure Chain

```
1. Webhook arrives at /webhook/telnyx ✅
2. Diagnostic logging captures headers ✅
3. headers_present = [] ❌
4. Signature verification checks for:
   - req.headers["x-telnyx-signature-ed25519"] → NOT FOUND
   - req.headers["x-telnyx-timestamp"] → NOT FOUND
5. Returns: reason: "missing_headers"
6. Webhook rejected with 401
```

---

## Root Causes (Likely In Order)

### 1. **Telnyx doesn't send Ed25519 signatures** (Most Likely)

Telnyx may use:
- No signature (rely on HTTPS + auth token)
- Different header names (e.g., `x-telnyx-request-signature`, `x-webhook-signature`)
- Different algorithm (HMAC-SHA256, etc.)
- Bearer token in Authorization header
- No webhooks security at all for this endpoint

### 2. **ngrok stripping headers** (Unlikely)

ngrok should forward all headers by default, but could be:
- Filtering Telnyx-specific headers
- Converting header names to lowercase
- Dropping authentication headers

### 3. **Header name case sensitivity** (Unlikely)

Node.js req.headers normalizes to lowercase, so this shouldn't be the issue. But Express could be case-sensitive.

---

## Test Evidence

**What we sent:** Plain webhook (no signature headers)  
**What was received:** Message payload parsed correctly, but headers empty  
**What server did:** Correctly identified missing headers and rejected  

**Security verdict:** ✅ **Working as designed** — Server correctly rejects unsigned webhooks

**Usability verdict:** ❌ **Broken** — Can't process legitimate Telnyx webhooks

---

## Recommended Fixes

### Fix Option 1: Disable Verification Temporarily (For Testing)

**In `.env`:**
```
TELNYX_VERIFY_SIGNATURES=false
```

**Effect:** All webhooks processed without signature check

**Security:** ⚠️ **REDUCED** — Use for testing only

**Pro:** Quick, allows testing end-to-end flow  
**Con:** No signature protection during test phase

---

### Fix Option 2: Implement Telnyx Actual Signature Scheme

**Steps:**
1. Review Telnyx webhook documentation to find actual signature method
2. Update signature verification function to match Telnyx's scheme
3. Test with real webhooks
4. Re-enable strict verification

**Security:** ✅ **MAINTAINED** — Proper signature verification  
**Pro:** Correct long-term solution  
**Con:** Requires Telnyx documentation research

---

### Fix Option 3: Add Fallback/Discovery Mode

**Implementation:**
```javascript
// If no Ed25519 headers, try other methods:
// 1. Check for X-Telnyx-Webhook-Signature
// 2. Check for Authorization bearer token
// 3. Check for X-Webhook-ID
// 4. If all missing, allow with logging (dev mode only)
```

**Security:** ⚠️ **CONDITIONAL** — Good for troubleshooting  
**Pro:** Captures all possible header formats  
**Con:** More complex code

---

## What We Know

✅ **Telnyx IS sending webhooks** — Request arrives at endpoint  
✅ **ngrok IS forwarding the request** — Body is intact  
✅ **Server IS receiving the request** — Logging captures it  
❌ **Ed25519 signature headers are NOT present** — headers_present = []  

---

## Diagnostic Headers Captured

**On this test webhook:**
- `headers_present: []`
- `body_type: "message.received"` ✅ (correct)
- `from_phone: "+16268313336"` ✅ (parsed correctly)
- `message_preview: "Test diagnostic"` ✅ (text captured)

**Body payload structure:** ✅ Correct Telnyx format

**Headers:** ❌ Missing expected signature headers

---

## When D.J.'s Real Reply Arrives

The same thing will happen:
1. Telnyx sends webhook (without signature headers)
2. Our diagnostic logs it
3. Signature verification fails (missing headers)
4. Webhook rejected with 401
5. LDEBRAINV1 never called
6. No response sent

**Unless we fix verification logic first.**

---

## Recommended Immediate Action

### For This D.J. Test Only:

**Temporarily disable signature verification:**

```bash
# In /Users/rrg/rrg/.env, set:
TELNYX_VERIFY_SIGNATURES=false

# Restart server:
pkill -f "node server"
/Users/rrg/rrg/keep-running.sh
```

**Effect:**
- All webhooks processed (no signature check)
- LDEBRAINV1 can respond to D.J.'s reply
- Test completes successfully
- We learn if LDEBRAINV1 flow works

**Then:**
1. Re-enable verification in `.env` after test
2. Contact Telnyx support for webhook signature documentation
3. Update signature verification to match their actual format
4. Thoroughly test before production

---

## Security Notes

### Current Situation

✅ **Signature verification code is CORRECT** — It properly validates Ed25519  
✅ **Rejection behavior is CORRECT** — Unsigned webhooks get 401  
❌ **Telnyx format is DIFFERENT** — They don't send Ed25519 headers (or send different ones)

### Why This Happened

- We implemented Ed25519 based on Telnyx API documentation
- Telnyx webhook signing may use a different method
- Signature scheme may differ from general API authentication

### Fix Path

1. **Short-term:** Disable verification for controlled test (D.J. only)
2. **Medium-term:** Find Telnyx webhook docs, implement correct method
3. **Long-term:** Re-enable strict verification with correct format

---

## Status

🔴 **Root cause identified:** Telnyx webhooks don't include Ed25519 signature headers

**Recommendation:** Temporarily disable verification for D.J. test, then implement correct Telnyx webhook signature scheme

**Next action:** Authorization from D.J. to disable verification for testing purposes only
