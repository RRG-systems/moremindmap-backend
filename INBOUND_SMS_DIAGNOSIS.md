# Inbound SMS Diagnosis Report

**Date:** Tue Apr 28, 2026 10:40 MST  
**Issue:** D.J. replied but no response was sent  
**Root Cause:** Signature verification rejecting Telnyx webhooks  

---

## Timeline

| Time | Event |
|------|-------|
| 17:19:38 | SMS sent to D.J. (messageId: 40319dd5-1a84-4cf8-81b2-c20430e34bf6) |
| ~17:30 | D.J. replies: "yeah our oldest son is graduating from college" |
| 17:37:38 | Signature verification fails (reason: missing_headers) |
| 17:37:38 | Signature verification fails again (reason: missing_headers) |
| ~17:40 | No response sent to D.J. |

---

## What We Know

✅ **Outbound SMS:** Working (D.J. received it)  
❌ **Inbound webhook:** Arriving but failing signature verification  
❌ **Signature verification:** Rejecting with "missing_headers"  
❌ **LDEBRAINV1:** Never called (rejected at verification)  
❌ **Response:** Never sent  

---

## Root Cause Analysis

**The webhook is arriving, but Telnyx signature headers are NOT present:**

```json
{"t":"2026-04-28T17:37:38.454Z","type":"webhook_signature_verification_failed","reason":"missing_headers"}
```

This means one of three things:

1. **Telnyx not sending headers** — Webhook arrives without `X-Telnyx-Signature-Ed25519` and `X-Telnyx-Timestamp`
2. **ngrok not forwarding headers** — Headers exist at Telnyx but ngrok drops them
3. **Express not receiving headers** — Headers exist at ngrok but req.headers doesn't have them

---

## Current Signature Verification Code

```javascript
const signature = req.headers["x-telnyx-signature-ed25519"];
const timestamp = req.headers["x-telnyx-timestamp"];

if (!signature || !timestamp) {
  return { valid: false, reason: "missing_headers" };
}
```

---

## The Problem

**Signature verification is too strict. If headers are missing, the webhook is rejected and never logged as `inbound_sms`.**

This means:
1. Webhook arrives at `/webhook/telnyx`
2. Signature verification fails (missing headers)
3. Return 401 (no processing)
4. **No log entry** (so we don't know what the message was)
5. D.J. gets no reply

---

## Solution

We need to:

1. **Add diagnostic logging** to see what headers ARE arriving
2. **Check Telnyx documentation** — Do they actually send Ed25519 signatures?
3. **Relax verification temporarily** — Log the message even if verification fails
4. **Or disable verification for now** — Use `TELNYX_VERIFY_SIGNATURES=false` to test end-to-end flow
5. **Re-enable after validation**

---

## Immediate Fix (Option A): Diagnostic Logging

Add this before signature check to see what's arriving:

```javascript
app.post("/webhook/telnyx", async (req, res) => {
  // DIAGNOSTIC: Log all headers
  appendLog({
    t: isoNow(),
    type: "webhook_received",
    headers: Object.keys(req.headers).filter(h => h.includes("telnyx") || h.includes("sig") || h.includes("time")),
    body_size: (req.rawBody || "").length,
    body_preview: (req.rawBody || "").substring(0, 100),
  });
  
  // Continue with signature verification...
});
```

---

## Immediate Fix (Option B): Temporarily Disable Verification

Set in `.env`:
```
TELNYX_VERIFY_SIGNATURES=false
```

Then messages will be processed and we can see if LDEBRAINV1 is working.

**Use for testing only** — Re-enable before production.

---

## Immediate Fix (Option C): Add Fallback Logging

Even if signature fails, log the webhook so we can see what Telnyx is sending:

```javascript
if (!verification.valid) {
  // Log the attempt even though it failed
  appendLog({
    t: isoNow(),
    type: "webhook_received",
    reason: verification.reason,
    from: req.body?.data?.[0]?.payload?.from?.phone_number,
    message: req.body?.data?.[0]?.payload?.text,
  });
  return res.status(401).json({ ok: false, error: "Unauthorized" });
}
```

---

## Questions to Answer

1. **Is Telnyx actually sending Ed25519 signatures?**
   - Check Telnyx documentation
   - Or check Telnyx dashboard webhook settings

2. **Are the headers being forwarded by ngrok?**
   - ngrok should forward all headers by default
   - But need to verify

3. **What headers IS Telnyx sending?**
   - Need diagnostic logging to see

---

## Recommended Action Path

### Step 1: Add Diagnostic Logging

Modify server.js to log what headers are arriving, then restart.

### Step 2: D.J. Replies Again (or test with Telnyx sandbox)

Send another message so we can see what Telnyx actually sends.

### Step 3: Review Logs

Check what headers are present, verify signature, adjust accordingly.

### Step 4: Fix Verification

Once we know what Telnyx sends, update verification logic.

### Step 5: Re-enable Strict Verification

Lock signature verification back ON with correct logic.

---

## Hypothesis

Most likely scenario: **Telnyx webhook doesn't include Ed25519 signature headers.** Instead, it may use:
- HTTP Basic Auth
- Bearer token
- Simple API key verification
- Webhook signing via different headers (e.g., `X-Webhook-Signature`, `X-Telnyx-Webhook-Signature`)

The `TELNYX_PUBLIC_KEY` we have may be for **different purposes** (not webhook verification).

---

## Next Steps

1. **Add diagnostic logging** to see what headers Telnyx sends
2. **Check Telnyx webhook documentation** for signature format
3. **Update signature verification** to match Telnyx's actual format
4. **Test end-to-end** with corrected verification
5. **Re-lock security** with proper verification

---

**Status:** Identified root cause — Signature verification rejecting incoming webhooks (missing headers)

**Action:** Implement diagnostic logging or temporarily disable verification to validate webhook flow
