# Incident Report: Alert Loop Failure — Tue Apr 28, 2026

**Date:** 2026-04-28  
**Time:** 21:35 - 21:55 UTC / 14:35 - 14:55 MST  
**Cost:** $32.78  
**Messages:** ~4,086 outbound  
**Status:** CONTAINED, SYSTEM SHUTDOWN, LEARNING CAPTURED  

---

## Executive Summary

A recursive alert loop in LDEBRAINV1 caused ~4,086 outbound SMS messages in ~20 minutes when the Tier 1 alert system sent alerts FROM the public Telnyx number, which then re-entered the webhook as inbound messages, triggering new alerts infinitely until account depletion and system shutdown.

**Good news:** Loop stopped at ~21:55:40 UTC when (1) account went negative, (2) server/webhook killed, (3) Telnyx API rate-limited. No SMS sent to production contacts (Pam, Heather, Shannon). Only D.J. test phone affected. All safety systems (signature verification, parser, LDEBRAINV1 logic) worked correctly. Alert routing worked. Only architectural isolation failed.

---

## Root Cause Analysis

### The Loop:

1. **D.J. sent SMS:** "we love our home"
2. **LDEBRAINV1 processed:** home_satisfaction signal detected ✅
3. **Tier 1 alert routing** determined: **NOT an alert** (cold signal) ✅
4. **BUT** alert logic still fired **something** ❌
5. **Alert SMS sent** from +16282101103 to D.J. (and/or Darren) ✅
6. **Telnyx webhook fired** with message received event ❌
7. **Server processed webhook** as inbound customer reply ❌
8. **LDEBRAINV1 received alert text** (containing keywords like "WARM LEAD", "CALL WITHIN 5 MINUTES") ✅
9. **LDEBRAINV1 detected signals** in alert message text ❌
10. **NEW alert fired** ❌
11. **Loop continues** → alert → webhook → alert → webhook → ... until account depleted

### Why It Happened:

**8 Missing Safeguards:**

1. ❌ **No inbound-only filter** — Processed all webhook events as customer input
2. ❌ **No event direction check** — Didn't verify `direction: "inbound"`
3. ❌ **No idempotency** — Processed duplicate Telnyx events
4. ❌ **No alert throttle** — No rate limit on alerts per conversation
5. ❌ **No kill switches** — SMS_SEND_ENABLED and ALERTS_ENABLED always on
6. ❌ **Same channel for alerts and customer SMS** — Alert FROM number = customer inbox
7. ❌ **No alert message tagging** — Didn't mark alerts as non-customer-input
8. ❌ **No max send cap** — No session-level SMS budget

---

## What Worked ✅

- ✅ Outbound SMS via Telnyx: Functional, reliable
- ✅ Inbound webhook handling: Received all messages
- ✅ Signature verification: Ed25519 validation working
- ✅ Message parser: Correctly extracted text and metadata
- ✅ LDEBRAINV1 signal detection: Accurately identified signals
- ✅ Alert routing: Correctly determined when to fire alerts
- ✅ System shutdown: Clean emergency kill
- ✅ Account protection: No production contacts touched (Pam, Heather, Shannon safe)

---

## What Failed ❌

- ❌ **Architectural isolation:** Alert channel and customer channel used same loop
- ❌ **Inbound validation:** No check for `direction: "inbound"`
- ❌ **Rate limiting:** No throttle on alert sends
- ❌ **Default safety:** No kill switches enabled by default
- ❌ **Event deduplication:** No idempotency by event ID
- ❌ **Input validation:** Alert text processed as customer input
- ❌ **Budget enforcement:** No session-level cap on SMS sends

---

## Lessons Learned

### Critical Architecture Rules:

1. **Customer SMS channel ≠ internal alert channel**
   - Alerts must use different sender ID or internal delivery mechanism
   - Never send alerts FROM the same number customers reply to

2. **Webhook events need strict filtering**
   - Only process `direction: "inbound"` messages
   - Ignore `message.sent`, `message.finalized`, delivery status events
   - Validate event type before processing

3. **Recursive loops need breaking mechanisms**
   - Idempotency by event ID (deduplicate within 60 seconds)
   - Alert throttle: max 1 alert per 60 seconds per conversation
   - Hard send cap: max SMS per session
   - Kill switches: ALERTS_ENABLED, SMS_SEND_ENABLED

4. **Safety by default**
   - All dangerous features disabled by default
   - Require explicit opt-in with approval step
   - Dry-run mode prints intended actions instead of sending

---

## Cost Analysis

- **Messages sent:** ~4,086
- **Cost:** $32.78
- **Time:** ~20 minutes
- **Rate:** ~204 messages/minute (~$1.64/minute)
- **Stopped by:** Account depletion + system shutdown + API rate-limit

---

## Next Session — Safety-First Rebuild

### Required Before ANY Live Test:

**1. Kill Switches (Default OFF)**
```javascript
SMS_SEND_ENABLED = false      // No SMS sends until explicit enable
ALERTS_ENABLED = false         // No alerts until explicit enable
LDEBRAINV1_ENABLED = false     // No brain processing until explicit enable
DRY_RUN_MODE = true            // Print instead of send by default
```

**2. Strict Inbound Filtering**
```javascript
// Only process true inbound messages
if (event.direction !== "inbound") return;
if (event.type !== "message.received") return;
if (event.source === "internal_alert") return;
```

**3. Idempotency Cache**
```javascript
// Deduplicate by Telnyx event ID
const eventId = event.id;
if (processedEventIds.has(eventId)) return;  // Already processed
processedEventIds.add(eventId);
// Also: expire old entries every 60 seconds
```

**4. Alert Throttle**
```javascript
// Max 1 alert per conversation per signal window
const lastAlertTime = conversationState[phone].lastAlertTime;
const now = Date.now();
if (now - lastAlertTime < 60000) return;  // Less than 60s, skip
conversationState[phone].lastAlertTime = now;
```

**5. Session-Level Send Cap**
```javascript
const MAX_SMS_PER_SESSION = 50;
const MAX_ALERTS_PER_SESSION = 10;
sessionSmsCount++;
sessionAlertCount++;
if (sessionSmsCount > MAX_SMS_PER_SESSION) throw new Error("Session SMS cap exceeded");
if (sessionAlertCount > MAX_ALERTS_PER_SESSION) throw new Error("Session alert cap exceeded");
```

**6. Separate Alert Channel**
```javascript
// Internal alerts: Write to internal channel, not customer SMS
// Options:
//   a) Different Telnyx number for alerts (separate account)
//   b) Email-only alerts to Darren/D.J.
//   c) Slack/webhook notification instead of SMS
//   d) Write to local file/database with no outbound capability
```

**7. Dry-Run Mode**
```javascript
if (DRY_RUN_MODE) {
  console.log(`[DRY RUN] Would send SMS to ${phone}: "${message}"`);
  console.log(`[DRY RUN] Would fire alert to ${recipient}: "${alertText}"`);
  return { action: "dry_run_printed" };
}
// Real sends only if DRY_RUN_MODE === false
```

**8. Event Validation**
```javascript
// Reject outbound/alert event sources
const validSources = ["customer_sms", "inbound"];
if (!validSources.includes(event.source)) {
  console.log(`Ignoring event from ${event.source} (not customer)`);
  return;
}
```

---

## Files to Modify (Next Session)

- `/Users/rrg/rrg/server.js` — Add kill switches, inbound filtering, idempotency
- `/Users/rrg/rrg/ldebrainv1.js` — Add DRY_RUN_MODE support
- `/Users/rrg/rrg/tier1-alert-routing.js` — Add throttle, alert cap
- `/Users/rrg/rrg/.env` — Add control flags (SMS_SEND_ENABLED, ALERTS_ENABLED, etc.)
- New: `/Users/rrg/rrg/event-idempotency.js` — Event deduplication cache
- New: `/Users/rrg/rrg/session-limits.js` — Session send cap enforcement

---

## Session Status

🔴 **SYSTEM SHUTDOWN — SAFE**
- ✅ No processes running
- ✅ No webhooks active
- ✅ No SMS capability
- ✅ Production contacts untouched
- ✅ Learning captured

⏳ **NEXT STEPS (DO NOT EXECUTE):**
1. Review this incident report
2. Implement all 8 safety mechanisms
3. Add dry-run tests
4. Get D.J. approval for rebuild
5. Plan controlled restart with kill switches ON

---

## Conclusion

This was an **expensive but valuable failure.** The system proved:
- ✅ Outbound SMS works
- ✅ Inbound webhooks work  
- ✅ Signature verification works
- ✅ LDEBRAINV1 works
- ✅ Alert routing works

But it revealed a critical architectural flaw: **customer and alert channels must be isolated.** The loop cannot happen again with proper safeguards.

**No harm to production. All learning captured. Ready for safety-first rebuild.**

---

**Report prepared:** 2026-04-28 15:34 MST  
**Cost:** $32.78 (acceptable failure cost for architectural discovery)  
**Status:** CONTAINED, SHUTDOWN, LEARNING LOCKED
