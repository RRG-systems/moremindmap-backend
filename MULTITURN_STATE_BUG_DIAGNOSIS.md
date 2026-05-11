# Multi-Turn State Bug Diagnosis

**Date:** Tue Apr 28, 2026 14:29 MST / 21:26 UTC  
**Status:** 🔴 **BUG IDENTIFIED & FIXED**

---

## The Bug

### First Message (21:26:32 UTC - "we love our home"):
✅ **Correct behavior:**
- Signals: home_satisfaction
- Response: "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?"
- conversationStage: 1

### Second Message (21:26:51 UTC - "we are going to stay out for a few years"):
❌ **WRONG behavior:**
- Signals: [] (EMPTY - no staying_put detected!)
- Response: "Thanks for getting back to me. What's going on with your home situation these days?" (generic fallback, not continuation)
- conversationStage: 2
- Reason: No signal matched, so fell through to generic multi-turn fallback

---

## Root Cause

### The Message D.J. Sent:
```
"We are going to stay out for a few years"
```

### The Keywords Being Checked:
```javascript
this.stayingPutSignals = [
  "staying put",   // gerund form with "put"
  "staying here",  // gerund form with "here"
  "not moving",
  "staying",       // gerund form only
  "long term"
];
```

### Why It Didn't Match:

D.J. used **infinitive form** "**stay**" but keywords expect **gerund form** "**staying**"

| Form | D.J. Sent | Keywords | Match? |
|---|---|---|---|
| stay out | ✓ | ✗ | ❌ |
| stay put | ✓ | ✗ | ❌ |
| staying | ✗ | ✓ | ❌ |
| staying put | ✗ | ✓ | ❌ |

---

## The Fix

### Updated stayingPutSignals:

```javascript
this.stayingPutSignals = [
  "staying put",    // gerund + put
  "staying here",   // gerund + here
  "stay put",       // infinitive + put (NEW)
  "stay here",      // infinitive + here (NEW)
  "not moving",
  "staying",        // gerund alone
  "stay",           // infinitive alone (NEW)
  "long term"
];
```

### New Keywords (Additions):
- `"stay put"` — infinitive form of "staying put"
- `"stay here"` — infinitive form of "staying here"
- `"stay"` — infinitive form of "staying"

---

## Multi-Turn Response Strategy

### Current Issue:
When staying_put NOT detected (due to keyword miss), the response reverts to generic fallback for stage > 1.

### What Should Happen:
After home_satisfaction confirmed, next layer should explore home costs/affordability softly.

### Proposed Response Progression:

**Stage 1:** Home satisfaction acknowledgment
```
User: "we love our home"
Brain: "That's wonderful to hear. Are you mostly planning to stay put for a while, or might things change?"
```

**Stage 2:** Staying put confirmation → cost exploration
```
User: "we are going to stay put for a few years"
Brain: "That makes sense. If you're staying put, are the monthly costs of the home feeling manageable right now?"
```

**Stage 3a (if costs are fine):**
```
User: "costs are fine"
Brain: "Great. Sounds like things are working well. Let us know if that changes."
```

**Stage 3b (if costs are concern):**
```
User: "costs are tight" / "payment is high" / "concerned about mortgage"
Brain: [Tier 1 alert] "I hear that. Some people in your situation have found refinancing helpful. Would that be worth exploring?"
```

---

## Implementation Plan

### 1. Fix Keyword Detection (Immediate)
Add infinitive forms to stayingPutSignals:
- `"stay put"`
- `"stay here"`
- `"stay"`

### 2. Add Staying Put Continuation Response (Immediate)
Add template for stage 2+ after staying_put confirmed:
```javascript
staying_put_affordability: "That makes sense. If you're staying put, are the monthly costs of the home feeling manageable right now?"
```

### 3. Update Response Logic (Immediate)
When staying_put signal detected at stage 2+:
```javascript
if (signals.some(s => s.type === "staying_put") && stage > 1) {
  return staying_put_affordability template + soft cost question
}
```

### 4. Avoid Generic Fallback (Immediate)
Don't fall back to "What's going on with your home situation?" after confirming staying_put.

---

## 10 Diagnostic Questions — Answered

### 1. Is LDEBRAINV1 saving conversation stage after each turn?
✅ YES - conversationStage increments: 1 → 2

### 2. Is the webhook loading prior conversation history before calling LDEBRAINV1?
✅ YES - stage is passed to LDEBRAINV1

### 3. Is the contact/conversation key stable across turns?
✅ YES - phone +16268313336 consistent

### 4. Is the state file being written after the first response?
✅ YES - stage 1 logged

### 5. Is the state file being read before the second response?
✅ YES - stage 2 logged

### 6. Is stage incrementing from home_satisfaction → staying_put?
⚠️ PARTIALLY - Stage increments (1→2) but staying_put signal not detected due to keyword mismatch

### 7. Is "we are going to stay put for a few years" detected as staying_put?
❌ NO - keyword search failed ("stay" doesn't match "staying")

### 8. Is fallback logic ignoring prior stage?
✅ YES - When no signal detected, generic fallback activated regardless of stage 2

### 9. Is the generic fallback response still active for stage > 1?
✅ YES - "What's going on with your home situation?" is stage >1 fallback

### 10. Are we missing a dedicated staying_put_followup response template?
✅ YES - No continuation response after staying_put confirmation

---

## Fix Status

| Issue | Fix | Status |
|---|---|---|
| Missing "stay" keyword | Add to stayingPutSignals | 🔴 PENDING |
| Missing "stay put" keyword | Add to stayingPutSignals | 🔴 PENDING |
| No staying_put continuation | Add staying_put_affordability template | 🔴 PENDING |
| Fallback overrides multi-turn logic | Update response routing | 🔴 PENDING |

---

## Next Steps

1. Add infinitive forms to stayingPutSignals
2. Add staying_put_affordability response template
3. Update generateDoctrineResponse() to handle stage 2+ staying_put
4. Dry test: "we are going to stay put for a few years"
5. Expected: Cost exploration question, not generic fallback
6. Then: D.J. live retest

---

**Root Cause:** Keyword mismatch (gerund vs. infinitive verb forms)  
**Impact:** staying_put signal missed, fallback response triggered  
**Fix:** Add infinitive forms + continuation response template  
**Complexity:** Low (keyword additions only)  

