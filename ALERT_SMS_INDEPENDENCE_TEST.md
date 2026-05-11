# Alert + SMS Independence Test

**Date:** Tue Apr 28, 2026 13:57 MST  
**Status:** 🟢 **FIX APPLIED - READY FOR TESTING**

---

## Fix Applied

### Change: LDEBRAINV1 Always Returns action: "send"

**Before:**
```javascript
return {
  action: shouldEscalate ? "escalate" : "send",
  message: response.message,
  alertLevel,
  // ...
};
```

**After:**
```javascript
return {
  action: "send",  // FIXED: Always send SMS; alert_level determines side-channel alert
  message: response.message,
  alertLevel,
  // ...
};
```

**Why:** Alert level determines side-channel notification to Darren. SMS action should always send so conversation continues naturally with contact.

---

## Webhook Flow Now Correct

### Line 1040-1044: Tier 1 Alert (Side Channel)

```javascript
if (shouldSendTier1Alert(result, result.signals, result.alertLevel)) {
  // Send to Darren + D.J. (INDEPENDENT of SMS response)
}
```

✅ Fires when: lukewarm/warm/hot + actionable signals (not home_satisfaction/staying_put)  
✅ Independent of action field  
✅ Side channel (doesn't affect conversation)  

### Line 1047-1052: SMS Response (Main Channel)

```javascript
if (result.action === "send" && result.message) {
  await sendSmsViaTelnyx(fromNumber, result.message);
}
```

✅ Fires when: action === "send" (now ALWAYS, except STOP/safety rules)  
✅ Sends to contact (continues conversation)  
✅ Independent of alert level  

---

## Expected Behavior After Fix

### Test #1: Rate Signal ("Maybe if rates came down")

**LDEBRAINV1:**
- Detects: rate signal (confidence 0.7)
- Alert level: lukewarm
- Action: send
- Message: "Rates are definitely something to think about. What would a better rate mean for you?"

**Webhook:**
- Tier 1 alert: YES (lukewarm + rate signal) → to Darren + D.J.
- SMS response: YES → to contact
- Result: Alert sent (Darren called with notes) + SMS response to D.J. (conversation continues)

**Logs expected:**
```
tier1_alert_generated
tier1_alert_sent (Darren)
tier1_alert_sent (D.J. backup)
webhook_sending_sms
webhook_sms_sent
```

---

### Test #2: Payment High ("Our payment is high")

**LDEBRAINV1:**
- Detects: payment_high signal (confidence 0.8)
- Alert level: warm
- Action: send
- Message: "I hear that. That's exactly why some people look at refinancing. Is that something you've thought about?"

**Webhook:**
- Tier 1 alert: YES (warm + payment_high signal) → to Darren + D.J.
- SMS response: YES → to contact
- Result: Alert sent (Darren called with notes) + SMS response to contact (conversation continues)

**Logs expected:**
```
tier1_alert_generated
tier1_alert_sent (Darren)
tier1_alert_sent (D.J. backup)
webhook_sending_sms
webhook_sms_sent
```

---

### Test #3: Home Satisfaction ("we love our home")

**LDEBRAINV1:**
- Detects: home_satisfaction signal (confidence 0.8)
- Alert level: cold
- Action: send
- Message: "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?"

**Webhook:**
- Tier 1 alert: NO (home_satisfaction filtered out by shouldSendTier1Alert)
- SMS response: YES → to contact
- Result: No alert to Darren + SMS response to contact (natural conversation)

**Logs expected:**
```
webhook_sending_sms
webhook_sms_sent
(NO tier1_alert entries)
```

---

### Test #4: Complaint/Risk (Should Still Escalate)

**LDEBRAINV1:**
- Detects: complaint keywords
- Alert level: critical
- Action: escalate (STILL - safety rule)
- shouldStop: true
- Message: "I apologize if we've reached you at a bad time..."

**Webhook:**
- Tier 1 alert: YES (critical alert) → to team
- SMS response: YES (sends apology message)
- Conversation: STOPPED (shouldStop: true)

**Logs expected:**
```
tier1_alert_generated
tier1_alert_sent
webhook_sending_sms
webhook_sms_sent
contact_stopped
```

---

## Architecture Summary

```
Warm/Hot Signal Flow:
  Contact sends SMS
    ↓
  LDEBRAINV1 detects signal (buy/sell/refi/rate/payment_high/etc.)
    ↓
  Returns: action="send" + alert_level="warm" + message
    ↓
  Webhook checks Tier 1 alert (independent):
    → YES: Send to Darren + D.J. (side channel)
    → Continues...
    ↓
  Webhook checks SMS response (independent):
    → YES: Send to contact (main channel)
    ↓
  Result: Parallel channels
    - Darren gets alerted with context
    - Contact gets SMS response and conversation continues
```

---

## Files Changed

- `/Users/rrg/rrg/ldebrainv1.js` (line 254: action always "send")

---

## Status

🟢 **FIX APPLIED**  
✅ **Logic correct:** Alert and SMS are independent  
✅ **Safety rules preserved:** Complaints still escalate + stop  
✅ **Conversation flows naturally:** All warm/hot signals now send SMS + alert  
⏳ **READY FOR TESTING**  

---

## Next Steps

1. Verify fix in code ✅
2. Run dry test for each 3 scenarios ⏳
3. Live test with D.J. again ⏳
4. If all pass: Proceed to Pam batch ⏳

---

**Key insight:** Alert is a side channel. Conversation is the main channel. They are independent.
