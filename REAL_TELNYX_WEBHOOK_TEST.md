# Real Telnyx Webhook Capture — Instructions

**Status:** Ready to capture  
**Duration:** Up to 120 seconds  

---

## What's Running

✅ ngrok tunnel: Active (vitamins-doorstop-esophagus.ngrok-free.dev)  
✅ Server: Running with diagnostic logging  
✅ Capture script: Monitoring ngrok API for incoming webhooks  

---

## Trigger a Real Telnyx Webhook (Choose One)

### Option 1: D.J. Replies via Phone (Preferred)

**Action:**
1. From your phone, reply to the SMS from +1 628-210-1103
2. Send any message (e.g., "Thanks for the update")
3. Telnyx will route it to our webhook

**Timing:** Usually arrives within 1-5 seconds

### Option 2: Telnyx Dashboard Test Event

**If available:**
1. Go to Telnyx dashboard → Messaging → Webhooks
2. Find the webhook URL (should be our ngrok URL)
3. Click "Send Test Event" or "Trigger Test"
4. Select `message.received` event type if prompted

**Note:** Test event may differ from real SMS event

---

## What We're Capturing

When the webhook arrives, the capture script will log:

1. **Full HTTP headers** including:
   - `telnyx-signature-ed25519` (if present)
   - `telnyx-timestamp` (if present)
   - `x-telnyx-signature-ed25519` (if present)
   - Any other authentication/signature headers

2. **Request method:** POST

3. **Request URI:** /webhook/telnyx

4. **Full JSON payload:** The message details

5. **Timestamp:** When received

---

## Expected Outcomes

### If Telnyx Sends Ed25519 Headers

**We'll see:**
```json
{
  "request": {
    "headers": {
      "telnyx-signature-ed25519": ["...hex string..."],
      "telnyx-timestamp": ["...number..."],
      ...
    }
  }
}
```

**Then:**
- Signature verification should PASS
- LDEBRAINV1 processes the message
- Response is sent back to D.J.
- Problem solved ✅

### If Telnyx Does NOT Send Signature Headers

**We'll see:**
```json
{
  "request": {
    "headers": {
      // No telnyx-signature-ed25519
      // No telnyx-timestamp
      // Other headers present
      ...
    }
  }
}
```

**Then:**
- Real Telnyx webhooks also lack headers
- Issue is not curl vs. Telnyx
- Need to research Telnyx webhook security method
- May require disabling verification or updating to different scheme

---

## After Webhook Arrives

The capture script will:
1. ✅ Display full header list
2. ✅ Show payload structure
3. ✅ Save to console

Then Rocky will:
1. Compare headers to what code expects
2. Identify what's missing or different
3. Recommend fix

---

## Do NOT

❌ Don't text Pam, Heather, or Shannon contacts  
❌ Don't disable signature verification yet  
❌ Don't assume curl results = Telnyx behavior  

---

## Timeline

- **Now:** Capture script monitoring (120 second timeout)
- **Next:** Send real webhook (D.J. reply or Telnyx test)
- **~1-5 sec after:** Webhook captured
- **After:** Full header analysis

---

**Ready when you send the real webhook.**
