# LDEBRAINV1 BUILD PLAN — EXECUTION SUMMARY

**Date:** Tue Apr 28, 2026 08:48 MST  
**Status:** ✅ SETUP COMPLETE — Ready for Testing  
**Goal:** Build LDEBRAINV1 to usable test version, connect Telnyx, validate with Pam & Heather before touching Shannon batch

---

## What's Been Done (Steps 1-6)

### ✅ Step 1: Protect Existing Work
- Backed up `server.js` → `server.js.backup`
- Backed up `.env` → `.env.backup`
- Backed up `shannon_cooper_150.csv` → `shannon_cooper_150.csv.backup`
- Current backend confirmed functional

### ✅ Step 2: Host Shannon Video
- Created `/Users/rrg/RRGconnect-site/shannon-update.html` (hidden page)
- Copied video to `/Users/rrg/RRGconnect-site/shannon-update.mp4` (8.5MB)
- **URL:** https://rrgconnect.com/shannon-update.html (not in nav, private link only)
- Link ready for testing on phone

### ✅ Step 3: Add Test Contacts
- Updated `shannon_cooper_150.csv` with Pam + Heather
- Both marked as `contact_type=test` and `status=active`
- Phone numbers hardcoded for testing (not real):
  - Pam: 602-555-1234
  - Heather: 602-555-9876

### ✅ Step 4: Telnyx Integration
- **File:** `server.js` (enhanced with Telnyx functions)
- **Functions added:**
  - `sendSmsViaTelnyx(toNumber, message)` — Send SMS via Telnyx API
  - `alertToTeam(phone, leadName, signals, message)` — Alert Darren + D.J.
- **Webhook:** `/webhook/telnyx` — Receives inbound SMS, processes with LDEBRAINV1
- **API endpoints:**
  - `POST /api/send-sms` — Send test SMS
  - `POST /api/test-ldebrainv1` — Dry test LDEBRAINV1 response

### ✅ Step 5: LDEBRAINV1 Engine
- **File:** `ldebrainv1.js` (10.8KB)
- **Features:**
  - Safety rules: STOP (opt-out), HELP, wrong number, complaints
  - Signal detection: buy, sell, refi, rates, referral, home value
  - Alert levels: hot (immediate escalate), warm (send + log), lukewarm, cold
  - Conversation history maintained per contact
  - Logging: conversations → `ldebrainv1-conversations.jsonl`, alerts → `ldebrainv1-alerts.jsonl`
- **Response generation:** Uses OpenAI with conversation context
- **Guardrails:**
  - Max 150 tokens per response (text-friendly)
  - Temperature 0.7 (natural but not too random)
  - One soft question at a time

### ✅ Step 6: Dry Test Suite
- **File:** `test-ldebrainv1.js`
- **9 test cases:**
  1. Cold: "Not really" → cold / send
  2. Opt-out: "STOP" → stop / action=stop
  3. Warm: "Maybe if rates came down" → warm / send
  4. Hot: "My daughter may buy" → hot / escalate
  5. Wrong number: "Who is this?" → stop / action=stop
  6. Complaint: "Stop texting me" → critical / escalate + stop
  7. Help: "Help?" → info / send
  8. Lukewarm: "We may sell next year" → lukewarm / send
  9. Referral: "Know someone looking to buy" → warm / send

---

## What's Ready to Test (Steps 7-10)

### Step 7: Dry Test LDEBRAINV1 (Next Action)
```bash
cd /Users/rrg/rrg
npm install  # if needed
node test-ldebrainv1.js
```

**Expected output:** 9/9 tests pass, logs written to `logs/ldebrainv1-*.jsonl`

### Step 8: Send Controlled Live Test (Requires Telnyx Setup)
Once Telnyx API key + messaging profile ID are added to `.env`:

1. Test endpoint: `curl -X POST http://localhost:3000/api/send-sms -H "Content-Type: application/json" -d '{"to":"+16025551234","message":"Test message"}'`
2. Verify SMS received on test phone
3. Reply with test message (e.g., "Not really")
4. Verify inbound webhook received and processed
5. Check `logs/rrg-openai.log` for LDEBRAINV1 response

### Step 9: Text Pam
Once Telnyx is live:
1. Send: "Hi Pam, Shannon here. Quick update on home options in Tempe area. Check this out: https://rrgconnect.com/shannon-update.html"
2. Verify: Natural reply flow
3. Verify: LDEBRAINV1 detects any signals
4. Verify: If warm/hot signal appears, Darren + D.J. get alerted

### Step 10: Text Heather
Same as Pam, review logs/alerts, then decide if Shannon Batch 1 (real 150 contacts) is ready

---

## Files Changed/Created

| File | Status | Purpose |
|------|--------|---------|
| `server.js` | ✏️ Enhanced | Added Telnyx + LDEBRAINV1 integration |
| `.env` | ✏️ Updated | Added Telnyx credentials (placeholders) |
| `ldebrainv1.js` | 🆕 Created | Core conversation engine |
| `test-ldebrainv1.js` | 🆕 Created | Dry test suite |
| `shannon_cooper_150.csv` | ✏️ Updated | Test contacts (Pam, Heather) |
| `shannon-update.html` | 🆕 Created | Hidden video page |
| `shannon-update.mp4` | 📋 Copied | Video asset (8.5MB) |

**Backups:**
- `server.js.backup`
- `.env.backup`
- `shannon_cooper_150.csv.backup`

---

## Configuration Required

Before live testing, fill in `.env`:

```env
# Telnyx (get from dashboard.telnyx.com)
TELNYX_API_KEY=<your-api-key>
TELNYX_MESSAGING_PROFILE_ID=<your-profile-id>
TELNYX_FROM_NUMBER=+1602XXXXXXX  # Your Telnyx number

# Alert recipients (already set)
DARREN_PHONE=6268313336
DJ_PHONE=9517416964
```

---

## Safety Rules Built-In

1. **STOP keyword** → Immediate opt-out, no future SMS
2. **HELP keyword** → Send help response, continue conversation
3. **Wrong number** → Mark and stop
4. **Complaints/anger** → Escalate to internal team, stop conversation
5. **Signal detected** → Alert Darren + D.J., but continue if warm (not hot)
6. **Hot signal** (buy/sell/refi confirmed) → Immediate escalate, suggest human call
7. **Daily call cap** → 50 calls max, 2 sec throttle between calls

---

## Logging

All activity logged to `logs/`:
- `rrg-openai.log` — Main activity (SMS sent/received, errors)
- `ldebrainv1-conversations.jsonl` — Each conversation turn
- `ldebrainv1-alerts.jsonl` — All alerts (opt-out, signals, complaints, errors)
- `daily-state.json` — Rate limiting state

---

## Next Actions (In Order)

1. **Today (Tue):**
   - Run dry test suite: `node test-ldebrainv1.js`
   - Verify all 9 tests pass
   - Review log output

2. **After Telnyx Credentials Obtained:**
   - Update `.env` with API key + profile ID
   - Send test SMS via curl
   - Verify inbound webhook working
   - Send to Pam (test contact)

3. **After Pam Test Succeeds:**
   - Send to Heather (test contact)
   - Review all logs + alerts
   - Validate response quality

4. **Go Live:**
   - Import real Shannon contacts (150 batch)
   - Send first wave (10-20 contacts)
   - Monitor logs closely
   - Iterate based on Darren's feedback

---

## Key Design Decisions

- **One soft question per turn** — Mimic natural conversation, not interrogation
- **Restore context** — LDEBRAINV1 mentions Shannon + why we're reaching out
- **Signal detection via keywords** — Deterministic, not NLP (faster, more reliable)
- **Conversation history in logs** — Allows playback + learning
- **Escalate on hot signals** — Don't push further, handoff to Darren
- **Darren + D.J. alerts** — Dual notification (redundancy)
- **No database yet** — All state in CSV + logs (can migrate later)

---

**Updated:** Tue Apr 28 08:58 MST  
**Ready to execute Step 7 (dry test)**
