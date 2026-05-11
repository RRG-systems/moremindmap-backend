# Alert Routing Investigation — Offline Diagnostic

**Date:** Tue Apr 28, 2026 15:36 MST  
**Status:** OFFLINE DIAGNOSIS ONLY — NO LIVE ACTIONS  
**Priority:** HIGH — Critical for understanding alert loop mechanism

---

## Critical Observation

**Alert-loop texts sent TO D.J. FROM 628 Telnyx number**  
**Darren did NOT receive the same storm**

**Implication:** Alert routing may have only sent to contact's phone, not to both Darren + D.J.

---

## 10-Point Investigation (Next Session, Offline Only)

### 1. Did live Tier 1 alert send to DARREN_PHONE at all?
**Check:**
- Telnyx MDR (Message Delivery Report) for any SMS to Darren's number
- Search by recipient number + timestamp window 21:35-21:55 UTC
- Confirm if ANY alert messages reached Darren's phone

**Expected:** Yes, Darren should have received at least 1-2 alerts  
**Finding:** If NO, alert routing had bug sending only to D.J.

---

### 2. Did it only send to the contact phone from the inbound message?
**Check:**
- Review tier1-alert-routing.js `sendTier1Alert()` function
- Verify it reads from DARREN_PHONE and DJ_PHONE env vars
- Check if it accidentally uses `result.phone` or `leadRecord.phone` instead

**Expected:** Should use env vars only  
**Finding:** If YES, that's the bug — alerts went to contact instead of internal team

---

### 3. Did code accidentally use lead.phone / contact.phone as alert recipient?
**Check:**
- Search tier1-alert-routing.js for `lead.phone`, `contact.phone`, `result.phone`
- Verify no alert sends to these variables
- Confirm ONLY DARREN_PHONE and DJ_PHONE used

**Code location:** `/Users/rrg/rrg/tier1-alert-routing.js` around `sendTier1Alert()` call

---

### 4. Did DJ_PHONE overwrite DARREN_PHONE?
**Check:**
- Review .env file structure
- Confirm both DARREN_PHONE and DJ_PHONE defined separately
- Check if one was accidentally duplicated or misnamed
- Verify env loading logic in server.js

**Expected:** Two separate variables with different numbers  
**Finding:** If same number, alerts would only go to one recipient

---

### 5. Were DARREN_PHONE and DJ_PHONE loaded from .env correctly?
**Check:**
- Search server.js for `process.env.DARREN_PHONE` and `process.env.DJ_PHONE`
- Verify they're loaded at startup and available
- Check for typos in env var names
- Confirm .env file has both entries with correct values

**Expected:** Both loaded without errors  
**Finding:** If undefined/missing, alerts defaulted to contact phone

---

### 6. Were either missing, malformed, or undefined?
**Check:**
- Add console.log at server startup:
  ```javascript
  console.log("DARREN_PHONE:", process.env.DARREN_PHONE);
  console.log("DJ_PHONE:", process.env.DJ_PHONE);
  ```
- Check logs from 21:35-21:55 UTC for these values
- Verify format (should be +1XXXXXXXXXX)

**Expected:** Both logged with valid phone numbers  
**Finding:** If `undefined` or `null`, explains why alerts only went to contact

---

### 7. Did dry test mock alert recipients differ from live code path?
**Check:**
- Review test-multiturn-staying-put.js alert recipient logic
- Compare to live server.js alert sending
- Check if test hardcoded different recipients
- Verify test doesn't use real DARREN_PHONE/DJ_PHONE

**Expected:** Dry test should match live code  
**Finding:** If different, dry test passed but live failed

---

### 8. Did sendTier1Alert() call sendSms(contact.phone, alertText) by mistake?
**Check:**
- Review tier1-alert-routing.js line that sends alert SMS
- Search for `sendSms(` calls in alert routing
- Verify recipient parameter is DARREN_PHONE or DJ_PHONE
- Confirm NOT passing `contact.phone`, `result.phone`, or inbound number

**Code to check:**
```javascript
// Should NOT do this:
await sendSms(contact.phone, alertText);

// Should do this:
await sendSms(DARREN_PHONE, alertText);
await sendSms(DJ_PHONE, alertText);
```

---

### 9. Did alert loop happen only because D.J.'s contact phone received internal alert?
**Check:**
- Trace message flow in Telnyx logs
- Confirm all ~4,086 messages went TO +16268313336 (D.J.'s phone)
- Verify they came FROM +16282101103 (our Telnyx number)
- Check if any went to Darren's actual number
- Determine if loop was D.J.-only or split

**Telnyx MDR Query:**
- Filter: recipient = +16268313336, sender = +16282101103
- Count: ~4,086 messages expected
- Time range: 21:35-21:55 UTC
- Status: sent/delivered

**Alternative filter:**
- All messages sent FROM +16282101103 to ANY recipient
- Find if Darren's number appears
- If only D.J. appears, alert routing was broken

---

### 10. Confirm from Telnyx MDR whether alert messages sent to Darren's phone
**Check:**
- Pull full Telnyx Message Delivery Report for 2026-04-28 21:35-21:55 UTC
- Filter by sender = +16282101103 (our outbound number)
- List all recipient numbers and message counts
- Confirm:
  - D.J.'s number: YES (expected ~4,086)
  - Darren's number: ? (should see 1-2 initial alerts)
  - Other numbers: Should be NONE

**Expected result:**
```
Recipient: +16268313336 (D.J.)
  Messages: ~4,086
  Status: sent/queued/failed

Recipient: +1XXXXXXXXXX (Darren)
  Messages: 0-2 (initial alerts only)
  Status: sent/delivered
```

**If Darren has 0 messages:** Alert routing bug — only sent to D.J.'s contact phone

---

## Root Cause Hypothesis

**Most Likely:** `sendTier1Alert()` accidentally used contact's phone number instead of DARREN_PHONE/DJ_PHONE env vars.

**Evidence:**
- Only D.J. received alerts (same as contact phone)
- Darren did NOT receive alerts (internal recipient failed)
- Loop happened because D.J.'s phone is the inbound webhook source

**Implication:** Alerts went TO the customer instead of TO internal team, then re-entered as inbound customer messages.

---

## Critical Fix (Future Implementation)

### Rule: Tier 1 Alert Recipients = Fixed Internal Config Only

```javascript
// DO THIS:
const ALERT_RECIPIENTS = {
  PRIMARY: process.env.DARREN_PHONE,    // Must be defined
  BACKUP: process.env.DJ_PHONE,         // Must be defined
};

if (!ALERT_RECIPIENTS.PRIMARY) throw new Error("DARREN_PHONE not configured");
if (!ALERT_RECIPIENTS.BACKUP) throw new Error("DJ_PHONE not configured");

async function sendTier1Alert(alertData) {
  // Send to ONLY these internal recipients
  await sendSms(ALERT_RECIPIENTS.PRIMARY, alertData.message);
  await sendSms(ALERT_RECIPIENTS.BACKUP, alertData.message);
}

// NEVER DO THIS:
// await sendSms(contact.phone, alertText);           ❌
// await sendSms(result.phone, alertText);            ❌
// await sendSms(inboundFrom, alertText);             ❌
// await sendSms(leadRecord.phone, alertText);        ❌
```

### Validation at Startup:

```javascript
// Startup checks
if (!process.env.DARREN_PHONE) {
  console.error("FATAL: DARREN_PHONE not configured");
  process.exit(1);
}
if (!process.env.DJ_PHONE) {
  console.error("FATAL: DJ_PHONE not configured");
  process.exit(1);
}
console.log("✅ Alert recipients configured");
```

---

## Investigation Checklist

- [ ] Query Telnyx MDR for 2026-04-28 21:35-21:55 UTC
- [ ] Count messages to D.J.'s number (+16268313336)
- [ ] Count messages to Darren's number
- [ ] Count messages to any other recipients
- [ ] Review tier1-alert-routing.js `sendTier1Alert()` function
- [ ] Check for `lead.phone`, `contact.phone`, `result.phone` usage
- [ ] Verify DARREN_PHONE and DJ_PHONE env var loading
- [ ] Add console.log for both env vars to startup logs
- [ ] Compare dry test vs live code path
- [ ] Confirm alert loop was D.J.-only or split

---

## Status

🔴 **OFFLINE DIAGNOSIS ONLY**  
⏳ **NEXT SESSION:** Execute 10-point investigation  
📋 **GOAL:** Confirm if alert routing sent to contact instead of internal team  
🚫 **NO LIVE ACTIONS**

---

**Prepared:** Tue Apr 28, 2026 15:36 MST  
**Investigation Type:** Offline code review + Telnyx MDR query
