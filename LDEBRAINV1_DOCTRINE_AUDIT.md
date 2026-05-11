# LDEBRAINV1 Doctrine Audit

**Date:** Tue Apr 28, 2026 12:07 MST  
**Audit Scope:** Behavior alignment with RRG Conversion Cloud founder-guide physics  
**Status:** ⚠️ PENDING REVIEW — Issues Found

---

## 1. Current System Prompt / Behavioral Instruction

**From ldebrainv1.js line 129+:**

```
You are Shannon Cooper's recovery AI. You're reaching out to leads who may 
be interested in real estate services.

Your goals:
1. Have a natural, brief conversation (text-length responses)
2. Restore context about Shannon Cooper and why we're reaching out
3. Ask ONE soft question at a time
4. Listen for signals: buying, selling, refinancing, rates, home value, referrals
5. Be respectful of their time—keep messages short

If the person seems even slightly warm, set up a human call with Shannon.
If they're cold but not hostile, try one more opening before backing off.
If they're angry or negative, stop immediately.
```

---

## 2. Does it restore Shannon Cooper context before qualifying?

**🟡 PARTIALLY**

**What it does:**
- References "Shannon Cooper's recovery AI" in system prompt
- Says "set up a human call with Shannon" when warm

**What it DOESN'T do:**
- ❌ No contextual story about who Shannon is
- ❌ No "we met at..." / "you talked to Shannon about..."
- ❌ No history of prior conversation restoration
- ❌ Generic "real estate services" positioning

**Issue:** First message should restore context. Currently relies on OpenAI to improvise.

---

## 3. Does it ask one soft, low-pressure question at a time?

**🟡 PARTIALLY**

**What it's supposed to do:**
- System prompt says "Ask ONE soft question at a time" ✓

**What actually happens:**
- OpenAI generates response freely (temp=0.7)
- No enforcement of single-question rule
- No conversation state tracking to prevent multiple questions

**Issue:** Prompt intent is good, but no architecture enforces it.

---

## 4. Does it avoid direct buying/selling/refi/referral interrogation too early?

**🔴 NO — CRITICAL ISSUE**

**What it does:**
- Detects signals generically (line 255+)
- Routes to "hot" / "warm" based on ANY signal match

**What it DOESN'T do:**
- ❌ No conversation stage tracking (is this message 1 or 5?)
- ❌ No gradation ("Did you mention rates? That's interesting, tell me more vs. push to call")
- ❌ System prompt says "even slightly warm → set up call" (too aggressive)
- ❌ No time gating (ask open question first before closing)

**Issue:** Will push to Shannon call on first mention of "rates" or "payment" without exploration.

---

## 5. Does it treat "staying put" as a possible home-cost/refi opening?

**🔴 NO**

**What it does:**
- "Staying put" is NOT in detectSignals() at all (line 244-270)

**What it DOESN'T do:**
- ❌ No "staying put" keyword detection
- ❌ No logic: "staying put" = potential refi candidate
- ❌ No response: "That makes sense. Are you happy with your current rate/payment?"

**Issue:** Misses refi opportunity when lead volunteers "we're staying put."

---

## 6. Does it detect refi/rate/payment/equity/home-cost signals without pitching lending?

**🟡 PARTIALLY**

**What it does:**
- Detects: refi, rate, payment ✓
- Does NOT pitch lending directly ✓

**What it DOESN'T do:**
- ❌ Missing "equity" keyword
- ❌ Missing "home cost" / "mortgage" / "tax" patterns
- ❌ No contextual follow-up: "What's driving that concern about rates?"

**Issue:** Signal detection is incomplete. Generic response means no follow-up depth.

---

## 7. What exact triggers cause Tier 1 alert to Darren + D.J.?

**From ldebrainv1.js line 159:**

```javascript
if (alertLevel === "hot" || alertLevel === "warm") {
  await this.logAlert("signal_detected", ...);
}
```

**And getAlertLevel() line 272:**

```javascript
const hasHotSignal = signals.some(
  (s) => ["buy", "sell", "refi"].includes(s.type) && s.confidence >= 0.8
);

if (hasHotSignal) return "hot";           // → escalate
if (maxConfidence >= 0.75) return "warm"; // → send (NOT escalate)
```

**Alert triggers:**
- **HOT (escalate):** Any buy/sell/refi mention + confidence ≥0.8
- **WARM (send only):** Any signal ≥0.75 confidence (rate, referral, home_value)

**Issue:** WARM signals (e.g., "rates are high") are NOT escalated to Darren. Only logged. This may be intentional but unclear.

---

## 8. What does it send if the user says specific things?

### "Not really"
**Current behavior:** Generic AI response (no special handling)  
**Expected:** Soft closer, option to follow up later  
**Grade:** 🟡 Will depend on OpenAI's mood

### "We're staying put"
**Current behavior:** No detection, generic response  
**Expected:** "That's smart. Are you happy with your current mortgage/payment?"  
**Grade:** 🔴 MISS

### "Maybe if rates came down"
**Current behavior:** Triggers "rate" signal → WARM → generic response  
**Expected:** "What rate would work for you? Let me check what's available."  
**Grade:** 🟡 Detected but generic response

### "Our payment is high"
**Current behavior:** Triggers "rate" + "payment" signals → WARM or HOT depending on confidence  
**Expected:** "That's a pain. Have you looked at refinancing?"  
**Grade:** 🟡 Detected but generic response

### "My daughter may buy soon"
**Current behavior:** Triggers "buy" + "referral" signals → HOT  
**Expected:** "That's great! Would she be interested in connecting with Shannon?"  
**Grade:** 🟡 Escalated but generic response

### "We might sell next year"
**Current behavior:** Triggers "sell" signal → HOT  
**Expected:** Soft exploration  
**Grade:** 🟡 Escalated but generic response

### "Who is this?"
**Current behavior:** Treated as "wrong number" → stop  
**Expected:** Could be opening, not rejection  
**Grade:** 🔴 WRONG — "Who is this?" can mean "who am I talking to?" not "I don't know you"

### "STOP"
**Current behavior:** opt-out keyword → stop ✓  
**Expected:** Respect immediately  
**Grade:** ✅ CORRECT

---

## 9. Does it log brain_version = LDEBRAINV1?

**🔴 NO**

From logConversation() and logAlert(), no `brain_version` field present.

**Issue:** Cannot track which engine version generated the response for future training.

---

## 10. Does it log enough conversation state/signals for future LDE training?

**🟡 PARTIALLY**

**What it logs:**
- timestamp, phone, message, role
- signals array (in meta)
- confidenceScore (in meta)
- alertLevel (in alert logs)

**What it DOESN'T log:**
- ❌ Conversation stage (turn 1/5/10)
- ❌ User satisfaction / next-step outcome
- ❌ AI reasoning (why this response chosen)
- ❌ Actual response quality (was it good/bad)
- ❌ brain_version or engine ID

**Issue:** Insufficient for training future LDE versions. Needs outcome tracking.

---

## 11. What response did it generate to D.J., and was that LDEBRAINV1 or fallback logic?

**From logs (19:04:49.422Z):**

```
Message sent: "Thanks for getting back to us. Feel free to reply with any questions."
```

**Analysis:**
- D.J. message: "Actual final parser test" (neutral, no signals)
- Signals detected: [] (empty)
- alertLevel: "cold"
- Action: "send"

**Was this LDEBRAINV1 or fallback?**
- **Most likely FALLBACK** (generic response)
- Reason: No signals detected, so OpenAI probably returned generic fallback response

**Issue:** Test message had no content to work with. Not a real evaluation.

---

## 12. Are there any fallback/default replies that are too generic?

**🔴 YES — CRITICAL**

From line 146-150:

```javascript
return {
  action: "send",
  message: "Thanks for getting back to us. Feel free to reply with any questions.",
  alertLevel: "info",
  shouldStop: false,
};
```

**Problem:**
- This is the MAIN FALLBACK for OpenAI errors
- It's generic, doesn't restore context
- It's what D.J. received (likely from error handling line 240-242)

**Other fallback issues:**
- No contextual fallback based on conversation stage
- No "we'll circle back later" / "call you at X time" type responses
- No escalation ladder (try 1x, then back off)

---

## Summary: Doctrine Alignment

| Doctrine Principle | Status | Issue |
|---|---|---|
| Restore Shannon context | 🟡 Partial | Generic AI response, no story |
| One soft question | 🟡 Partial | Prompt says it, code doesn't enforce |
| No early interrogation | 🔴 NO | "Even slightly warm → call" is too aggressive |
| "Staying put" as refi signal | 🔴 NO | Not detected at all |
| Detect signals without pitching | 🟡 Partial | Missing equity/cost keywords |
| Tier 1 alerts | ✅ OK | Clear triggers logged |
| Specific response examples | 🟡 Mixed | Some handled, some generic |
| Who is this handling | 🔴 WRONG | Treats as reject, could be opening |
| Brain version logging | 🔴 NO | Missing |
| Training data sufficiency | 🟡 Partial | Missing outcome/reasoning logs |
| Response quality (D.J. test) | 🔴 WEAK | Fallback generic response |
| Fallback reply quality | 🔴 WEAK | Too generic for founder-guide physics |

---

## Blocking Issues for Production

🔴 **CRITICAL:**
1. No conversation stage tracking (will push call too early)
2. "Staying put" not detected (misses refi opens)
3. "Who is this?" treated as rejection (loses sales)
4. Generic fallback responses don't match founder-guide
5. No brain_version logging (can't improve)

🟡 **IMPORTANT:**
1. No context restoration before qualifying
2. No question-count enforcement
3. Incomplete signal detection (missing equity, costs)
4. Insufficient training data logging

---

## Recommendation

**DO NOT DEPLOY TO PAM/HEATHER YET.**

LDEBRAINV1 current implementation:
- ✅ Infrastructure works (end-to-end passing)
- ✅ Signal detection implemented
- ❌ Doctrine alignment incomplete
- ❌ Conversation physics not RRG-grade

**Required before Pam/Heather:**
1. Add conversation stage tracking
2. Fix "staying put" signal
3. Fix "who is this" handling
4. Implement contextual response templates (not just OpenAI)
5. Add brain_version logging
6. Add outcome tracking for training

**Estimated effort:** 4-6 hours of code + testing

---

**Status:** LIVE TECHNICAL FLOW ✅ → PRODUCTION READINESS ❌ PENDING DOCTRINE REVIEW
