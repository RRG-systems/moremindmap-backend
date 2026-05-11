# D.J. Live Test — Failure Diagnosis & Fix

**Date:** Tue Apr 28, 2026 13:51 MST  
**Test Message:** "We love our home."  
**Status:** 🔴 **FAILURE — MISFIRED ON HOME SENTIMENT**

---

## The Problem

D.J. replied: **"We love our home."**

LDEBRAINV1 classified as:
- Signal: **buy** (WRONG)
- Alert level: **hot** (WRONG)
- Action: **escalate** (WRONG)
- Tier 1 alert fired: **YES** (WRONG)
- SMS response sent: **NO** (correct for escalate, but escalate shouldn't have happened)

---

## Root Causes Found

### 1. "home" in buySignals (Line 41)

**Current code:**
```javascript
this.buySignals = [
  "buy", "purchasing", "looking for", "interested in", "house",
  "home", "property", "market", "price", "down payment", "mortgage",
];
```

**Problem:** "home" is too broad. "We love our home" matches, triggering buy signal.

**Should be:** Remove "home" from buySignals. Use only intent words (buy, purchasing, looking, interested, down payment, mortgage, house, property).

### 2. No Home Satisfaction Signal

**Missing:** Positive sentiment about current home ("love", "happy", "settled", "happy with")

**Should be:** Add home_satisfaction signal for "love", "happy", "great", "wonderful", "settled"

### 3. Home Context Not Distinguished

**Missing logic:** "home" + positive sentiment = staying put / home satisfaction, NOT buy

**Should be:** Add semantic differentiation:
- "buy a home" = buy signal
- "home" alone = neutral (needs context)
- "love our home" = home satisfaction
- "our home" = current home context (anti-buy)

### 4. Alert Fired on False Positive

**Problem:** hot signal (from wrong buy detection) triggered alert to Darren + D.J.

**Should be:** Alerts should only fire on REAL signals, not false positives from keyword matching

---

## Exact Log Evidence

**Inbound SMS (20:46:37.807Z):**
```json
{
  "from": "+16268313336",
  "message": "We love our home.",
  "lead_name": "D.J. Test",
  "lead_id": "DJ001"
}
```

**LDEBRAINV1 Result (20:46:39.035Z):**
```json
{
  "action": "escalate",  // WRONG - should be "send"
  "message": "Thanks for getting back to us. Feel free to reply with any questions.",  // WRONG - generic fallback
  "alertLevel": "hot",  // WRONG - should be "cold" or "warm"
  "shouldStop": false,
  "signals": [
    {
      "type": "buy",  // WRONG - should NOT have buy signal
      "confidence": 0.8
    }
  ],
  "confidenceScore": 0.3  // Low confidence contradicts high alert level
}
```

**Webhook Action Check (20:46:39.035Z):**
```json
{
  "should_send_sms": false,  // Correct (escalate=no SMS)
  "should_alert": true  // WRONG - alert fired
}
```

**Alert Sent (20:46:39.035Z):**
```
webhook_sending_alert to Darren + D.J.
```

**No SMS Response:** Because action was "escalate", no SMS sent to D.J. ✅ (correct behavior for escalate, but escalate shouldn't have happened)

---

## Correct Interpretation

**Input:** "We love our home."

**Correct signals:**
- home_satisfaction: true
- staying_put_sentiment: true
- buy_signal: false
- sell_signal: false
- refi_signal: false (no rate/payment/cash mentions)

**Correct alert level:** cold (no concern, positive sentiment)

**Correct action:** send (respond conversationally)

**Correct response:** "That's great to hear. Are you mostly planning to stay put this year?"

**Tier 1 alert:** NO (cold/home satisfaction should not alert)

---

## Fix Required

### Fix #1: Remove "home" from buySignals

**Current:**
```javascript
this.buySignals = [
  "buy", "purchasing", "looking for", "interested in", "house",
  "home", "property", "market", "price", "down payment", "mortgage",
];
```

**Fixed:**
```javascript
this.buySignals = [
  "buy", "purchasing", "looking for", "interested in", "house",
  "property", "market", "down payment", "mortgage",
  // Removed: "home" (too generic, creates false positives)
];
```

### Fix #2: Add Home Satisfaction Signal

**New signal keywords:**
```javascript
this.homeSatisfactionSignals = [
  "love", "happy", "great", "wonderful", "settled",
  "comfortable", "satisfied", "perfect", "ideal",
  "beautiful", "amazing"
];
```

### Fix #3: Add Home Satisfaction Detection

**In detectSignals():**
```javascript
// Check for positive home sentiment BEFORE buy/sell signals
if (this.hasSignal(text, this.homeSatisfactionSignals) && (text.includes("home") || text.includes("house") || text.includes("place"))) {
  signals.push({ type: "home_satisfaction", confidence: 0.8 });
  // Don't check buy/sell if positive home sentiment + home context
  return signals;  // Early return to prevent false buy signal
}
```

### Fix #4: Home Satisfaction Response Template

**New template:**
```javascript
home_satisfaction_opening: "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?"
```

### Fix #5: Ensure Alert Doesn't Fire on Home Satisfaction

**In tier1-alert-routing.js:**
```javascript
// home_satisfaction should NOT trigger alert
const NO_ALERT_SIGNALS = ["home_satisfaction", "help", "info"];
```

---

## Test Case: "We love our home"

**After fix:**
- Signals detected: home_satisfaction
- Alert level: cold
- Action: send
- Response: "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?"
- Tier 1 alert: NO
- SMS sent: YES

---

## Summary of Changes

| Issue | Root Cause | Fix |
|---|---|---|
| "home" → buy signal | "home" in buySignals | Remove "home" from buySignals |
| No home satisfaction | Missing signal type | Add homeSatisfactionSignals array + detection |
| False hot alert | Any buy signal triggers hot | Check home satisfaction FIRST |
| Response not sent | Escalate on false signal | False signal won't trigger escalate |
| No SMS back | Escalate action | Escalate won't happen (false signal fixed) |

---

## Implementation Checklist

- [ ] Remove "home" from buySignals
- [ ] Add homeSatisfactionSignals array
- [ ] Add home_satisfaction detection in detectSignals()
- [ ] Add home_satisfaction response template
- [ ] Update NO_ALERT_TRIGGERS to include home_satisfaction
- [ ] Add dry test: "We love our home" (expect: cold, no alert, soft follow-up)
- [ ] Verify logs show: no buy signal, home_satisfaction signal, send action, SMS sent
- [ ] Live test with D.J. again after fix

---

**Status:** 🔴 MISFIRED — DIAGNOSIS COMPLETE — AWAITING FIX IMPLEMENTATION
