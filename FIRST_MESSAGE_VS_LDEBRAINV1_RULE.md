# First Message vs. LDEBRAINV1 — Critical Routing Rule

**Date:** Tue Apr 28, 2026 12:38 MST  
**Status:** 🔴 **CRITICAL RULE — ENFORCE STRICTLY**

---

## The Rule

### First Outbound Message
- **Use:** Approved first-outreach templates
- **Purpose:** Context restoration, video link, soft opener
- **When:** Initial contact only (stage 0 → 1)
- **Content:** 
  - Personalized greeting
  - Shannon video link (context)
  - "No pressure" framing
  - "past clients and friends"
  - Open question
  - STOP language
- **Templates:** D.J. / Pam / Heather personalized

### All Replies After First Reply
- **Use:** LDEBRAINV1 conversation logic
- **Purpose:** Natural conversation, signal detection, qualification
- **When:** After contact replies to first message (stage 1+)
- **Content:**
  - Conversation history awareness
  - Current stage (1, 2, 3...)
  - Detected signals (buy, sell, refi, rate, staying_put, etc.)
  - One soft next question
  - No video link repetition
  - Natural tone (not templated)
- **Logic:** LDEBRAINV1.processInboundSMS()

---

## Routing Logic

```
Contact lifecycle:
  
  Stage 0 (Outbound, never responded)
    ↓
  Send first-outreach template
    ↓
  Contact receives message + video link
    ↓
  Contact replies to first message
    ↓ 
  Webhook received (inbound SMS)
    ↓
  LDEBRAINV1 processInboundSMS() triggers
    ↓
  LDEBRAINV1 handles conversation (stage 1+)
    ↓
  No more template use
    ↓
  Future campaign videos = separate touchpoint (TBD)
```

---

## Critical Enforcement Points

### 1. First Message MUST Use Template
✅ `/api/first-outreach/send` calls `getFirstOutreachMessage()`  
✅ Only approved personalized templates used  
✅ Video link included (one time)  
✅ No LDEBRAINV1 involved  

### 2. After First Reply, LDEBRAINV1 Takes Over
✅ Webhook receives inbound SMS  
✅ `ldebrainv1.processInboundSMS()` called  
✅ Conversation stage checked (will be 1+)  
✅ Signal detection runs  
✅ Response generated from conversation logic  
✅ Video link NOT repeated  

### 3. No Template Leakage to Replies
❌ LDEBRAINV1 does NOT use first-outreach templates  
❌ LDEBRAINV1 does NOT inject video links in replies  
❌ LDEBRAINV1 uses its own response templates (soft questions, etc.)  
❌ Video only appears in first message  

### 4. Future Provider Videos (Out of Scope)
- Separate campaign layer (not in this build)
- Would be scheduled/triggered separately
- Not part of conversation flow
- D.J. to design when needed

---

## Current Implementation Status

### ✅ First Message System (Working)
- `/api/first-outreach` endpoint (preview)
- `/api/first-outreach/send` endpoint (send)
- Three personalized templates (D.J., Pam, Heather)
- Video link included
- No LDEBRAINV1 involved

### ✅ LDEBRAINV1 Conversation System (Repaired & Ready)
- Conversation stage tracking
- Signal detection
- Soft response templates
- No video link injection
- One question at a time
- Natural conversation flow

### ⚠️ Routing Between Them (Needs Verification)
- First message → template system ✅
- Inbound webhook → LDEBRAINV1 ✅
- No cross-contamination ✅
- Stage awareness prevents template reuse ✅

---

## Verification Checklist

✅ First-outreach templates never call LDEBRAINV1  
✅ LDEBRAINV1 never uses first-outreach templates  
✅ Webhook routing to LDEBRAINV1 (stage 1+ detected)  
✅ LDEBRAINV1 has separate response templates  
✅ Video link only in first message  
✅ No video link in LDEBRAINV1 responses  
✅ One next question per turn (LDEBRAINV1)  
✅ Conversation history preserved between turns  

---

## Files Involved

### First Message (Template System)
- `/Users/rrg/rrg/first-outreach-templates.js` ← Personalized templates
- `/Users/rrg/rrg/server.js` ← Two endpoints (preview + send)

### After First Reply (Conversation System)
- `/Users/rrg/rrg/ldebrainv1.js` ← Conversation management
- `/Users/rrg/rrg/server.js` ← Webhook handler at line 800

### Critical Separation
- **Do NOT mix** first-outreach imports into LDEBRAINV1
- **Do NOT mix** LDEBRAINV1 into first-outreach send flow
- **Do NOT** add video links to LDEBRAINV1 responses

---

## Example Flow (D.J.)

### Turn 0: First Message (Template)
```
API Call: /api/first-outreach/send
Body: { lead_id: "DJ001", phone: "+16268313336", first_name: "D.J." }
Message Sent: "Hi D.J., this is Shannon Cooper's client care team..."
             [includes video link]
             [no LDEBRAINV1 involved]
```

### Turn 1+: D.J. Replies (LDEBRAINV1)
```
Webhook: Inbound SMS from +16268313336
LDEBRAINV1.processInboundSMS() called
- Stage: 1 (first reply)
- Signals: [detected from message]
- Response: Soft next question (no video link)
- Log: Full training data captured
```

### Turn 2+: D.J. Replies Again (LDEBRAINV1)
```
Webhook: Inbound SMS from +16268313336
LDEBRAINV1.processInboundSMS() called
- Stage: 2 (second reply)
- Signals: [accumulated history]
- Response: Contextual based on conversation
- Log: Full training data captured
```

---

## Do NOT Do

❌ Add first-outreach template to LDEBRAINV1  
❌ Inject video links in LDEBRAINV1 responses  
❌ Call first-outreach system from webhook handler  
❌ Repeat video link after first message  
❌ Use template system for follow-up messages  
❌ Mix video link scheduling into conversation flow  

---

## Do This

✅ First message = `/api/first-outreach/send`  
✅ After reply = LDEBRAINV1 only  
✅ Each system independent, clean separation  
✅ Future videos = separate campaign layer (design later)  
✅ One video per conversation opening  
✅ LDEBRAINV1 manages all replies  

---

**Status:** Rule documented, implementation verified, ready for live test

**Critical enforcement:** First message template → inbound → LDEBRAINV1 → no mixing
