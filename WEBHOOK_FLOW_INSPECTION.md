# Webhook Flow Inspection — Alert vs SMS Response

**Date:** Tue Apr 28, 2026 13:57 MST  
**Status:** 🔴 **CRITICAL ISSUE FOUND**

---

## Current Webhook Flow (Lines 1030-1080)

```
1. LDEBRAINV1 processes inbound SMS (generates result)
2. Check: should_send_sms?
3. IF Tier 1 alert should fire:
   → Send alert to Darren
   → Send alert to D.J.
4. IF result.action === "send" AND result.message:
   → Send SMS response to contact
5. IF result.action === "escalate" OR result.alertLevel === "hot":
   → Call alertToTeam() [duplicate alert code?]
6. IF result.shouldStop:
   → Mark lead as stopped
```

---

## Problems Found

### Problem #1: Double Alert Logic

**Lines 1040-1044 (Tier 1 alert):**
```javascript
if (shouldSendTier1Alert(result, result.signals, result.alertLevel)) {
  // Send alerts to Darren + D.J.
}
```

**Lines 1053-1058 (Escalate alert):**
```javascript
if (result.action === "escalate" || result.alertLevel === "hot") {
  await alertToTeam(fromNumber, leadName, result.signals || [], inboundText);
  // Another alert sent?
}
```

**Issue:** Two separate alert code paths. Are we double-alerting?

---

### Problem #2: Response Skipped on Escalate

**Lines 1047-1052:**
```javascript
if (result.action === "send" && result.message) {
  // Send SMS response
}
```

**The issue:** Response only sends if `action === "send"`.

But LDEBRAINV1 might return `action: "escalate"` when it detects a warm signal!

**Result:** Alert fires, but NO SMS response sent to contact (WRONG).

---

### Problem #3: Escalate Blocks Response

**Current logic:**
- If LDEBRAINV1 returns `action: "escalate"` (for warm/hot signals):
  - Alert fires ✅
  - Response SMS is skipped ❌ (action !== "send")
  - Contact gets NO response from Shannon's team

**Expected:**
- If LDEBRAINV1 detects warm/hot signal:
  - Alert fires ✅ (side channel to Darren)
  - Response SMS is sent ✅ (conversation continues)
  - Contact gets natural reply

---

### Problem #4: LDEBRAINV1 Returns Escalate on Hot

**From LDEBRAINV1 logic:**
```javascript
if (signals.some(s => s.type === "buy" || s.type === "sell")) {
  // ...
  return { action: "escalate", ... };
}
```

When LDEBRAINV1 detects buy/sell/refi/rate signals, it returns `action: "escalate"`.

But the webhook treats `escalate` as "don't respond, just alert".

**This breaks the conversation flow.**

---

## What Should Happen

### Scenario 1: Warm Signal (e.g., "Maybe if rates came down")

**LDEBRAINV1 detects:** rate signal, alert_level: warm  
**Should return:** action: "send", message: "...", alert_level: "warm"

**Webhook should:**
1. Send Tier 1 alert to Darren (side channel) ✅
2. Send SMS response to D.J. ✅
3. Keep conversation open ✅
4. Continue responding to future messages ✅

**Current behavior:**
- If LDEBRAINV1 returns `action: "escalate"` → SMS response skipped ❌

---

### Scenario 2: Cold Signal (e.g., "Thanks")

**LDEBRAINV1 detects:** no signals, alert_level: cold  
**Should return:** action: "send", message: "...", alert_level: "cold"

**Webhook should:**
1. No Tier 1 alert ✅
2. Send SMS response ✅
3. Keep conversation open ✅

**Current behavior:** Works correctly ✅

---

### Scenario 3: Home Satisfaction (e.g., "we love our home")

**LDEBRAINV1 detects:** home_satisfaction signal, alert_level: cold  
**Should return:** action: "send", message: "...", alert_level: "cold"

**Webhook should:**
1. No Tier 1 alert (home_satisfaction filtered) ✅
2. Send SMS response ✅
3. Response: "That's wonderful to hear. Are you mostly planning to stay put..."
4. Keep conversation open ✅

**Current behavior:** Will work IF home_satisfaction is correctly filtered from alerts

---

## Critical Fix Needed

### Change #1: LDEBRAINV1 Should Always Return action: "send"

**Current:**
```javascript
if (signals.some(s => s.type === "buy" || s.type === "sell")) {
  return { action: "escalate", ... };
}
```

**Should be:**
```javascript
if (signals.some(s => s.type === "buy" || s.type === "sell")) {
  return { action: "send", message: "...", alert_level: "hot", ... };
}
```

**Rationale:** `action: "escalate"` should NOT exist. Alert level determines side-channel alert. Action should always be "send" (unless STOP/safety rule).

---

### Change #2: Webhook Always Sends SMS If action: "send"

**Current (correct):**
```javascript
if (result.action === "send" && result.message) {
  await sendSmsViaTelnyx(fromNumber, result.message);
}
```

**This is correct.** Keep it.

---

### Change #3: Alert Logic Independent of Action

**Current:**
```javascript
if (shouldSendTier1Alert(result, result.signals, result.alertLevel)) {
  // Send alert (side channel)
}

if (result.action === "send" && result.message) {
  // Send SMS response
}
```

**This is correct.** Alert and response are independent.

---

### Change #4: Remove Duplicate alertToTeam()

**Lines 1053-1058 seem redundant.** Should be removed or clarified:
```javascript
if (result.action === "escalate" || result.alertLevel === "hot") {
  await alertToTeam(...);  // ← What is this?
}
```

**Is this:**
- A backup alert mechanism?
- Legacy code?
- Dead code?

---

## Summary of Required Fixes

| Issue | Current | Should Be | Status |
|---|---|---|---|
| LDEBRAINV1 returns `action: "escalate"` on hot signals | ❌ Breaks response | Always return `action: "send"` + alert_level | 🔴 NEEDS FIX |
| Webhook skips response when action !== "send" | ❌ No SMS to contact | Always send SMS if action="send" | ⏳ (works if LDEBRAINV1 fixed) |
| Double alert logic (Tier 1 + alertToTeam) | ❌ Unclear | Keep Tier 1, remove/clarify alertToTeam | 🔴 NEEDS REVIEW |
| Alert fires independently of response | ✅ Correct | Keep as is | ✅ GOOD |
| Home satisfaction alerts | ❌ (with old code) | Tier 1 filters it out | ⏳ (tier1 fix applied) |

---

## Test Cases Needed

### Test #1: "Maybe if rates came down"

**Expected flow:**
1. LDEBRAINV1 detects: rate signal, alert_level: warm
2. LDEBRAINV1 returns: action: "send", message: "Rates are definitely...", alert_level: "warm"
3. Webhook sends Tier 1 alert to Darren
4. Webhook sends SMS response to contact
5. Logs show: `tier1_alert_sent` + `webhook_sms_sent` (both)

---

### Test #2: "Our payment is high"

**Expected flow:**
1. LDEBRAINV1 detects: payment_high signal, alert_level: warm
2. LDEBRAINV1 returns: action: "send", message: "I hear that. That's exactly...", alert_level: "warm"
3. Webhook sends Tier 1 alert to Darren
4. Webhook sends SMS response to contact
5. Logs show: `tier1_alert_sent` + `webhook_sms_sent` (both)

---

### Test #3: "we love our home"

**Expected flow:**
1. LDEBRAINV1 detects: home_satisfaction signal, alert_level: cold
2. LDEBRAINV1 returns: action: "send", message: "That's wonderful to hear...", alert_level: "cold"
3. Webhook does NOT send Tier 1 alert (home_satisfaction filtered)
4. Webhook sends SMS response to contact
5. Logs show: NO `tier1_alert_sent`, YES `webhook_sms_sent`

---

## Status

🔴 **CRITICAL:** LDEBRAINV1 returns `action: "escalate"` on hot signals, which breaks response flow  
⏳ **NEEDS FIX:** Change LDEBRAINV1 to always return `action: "send"` + alert_level  
⏳ **NEEDS REVIEW:** Double alert logic (Tier 1 vs alertToTeam)  
✅ **READY:** Webhook response logic is correct (once LDEBRAINV1 is fixed)  

---

**Next action:** Fix LDEBRAINV1 to return action: "send" (not "escalate") + alert_level, then test all 3 scenarios.
