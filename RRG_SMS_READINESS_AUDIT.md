# RRG SMS / SHANNON TEST READINESS AUDIT

**Date:** Mon Apr 27, 2026 @ 14:35 MST  
**Auditor:** Rocky  
**Status:** AUDIT COMPLETE — READY FOR BUILD PHASE

---

## 1. WEBSITE

**RRGconnect Path:**
- `/Users/rrg/RRGconnect-site/`
- Static HTML + Tailwind CDN (no backend attached)

**Static or Backend:**
- Pure static site (GitHub Pages → Vercel)
- Contact form endpoint: Formspree (`https://formspree.io/f/mdawjdqq`)
- No local backend integration

**Live Deploy Method:**
- Git push to GitHub Pages → auto-deploy to Vercel
- Last deployment: Mon Apr 27 13:25 MST (commit 452a1c8)

**Current Status:**
- ✅ Live at https://rrgconnect.com
- ✅ Redesigned with signal intelligence wave background
- ✅ All copy, forms, links preserved
- ✅ Mobile responsive

---

## 2. BACKEND / API

**Backend Path Found:**
- `/Users/rrg/rrg/` (Node.js Express)

**Framework:**
- Express.js (v5.2.1)
- Node.js runtime
- dotenv for environment variables

**Existing Endpoints:**
- `GET /` — HTML control panel (web UI)
- `GET /status` — Daily call metrics and config display
- `POST /reload-csv` — Reload leads from CSV file
- `POST /classify` — Main intent classifier endpoint

**Current Webhook Status:**
- ✅ Local HTTP server running on localhost:3000 (controlled invocation only)
- ✅ iMessage alert sender via AppleScript (macOS native)
- ❌ NO Telnyx webhook configured
- ❌ NO SMS inbound listener configured
- ❌ NO SMS outbound sender configured

**Notes:**
- Server listens on 127.0.0.1:3000 only (not public)
- Designed for local/controlled testing
- iMessage alerts go to ALERT_NUMBERS via AppleScript
- Currently no production deployment method (Vercel, Render, etc.)

---

## 3. TELNYX LOGIC

**Send SMS Function:**
- ❌ NOT IMPLEMENTED
- Current: iMessage only (AppleScript)

**Inbound Webhook:**
- ❌ NOT IMPLEMENTED
- No `/inbound` or `/webhook` endpoint
- No Telnyx SDK imported

**Delivery Events:**
- ❌ NOT IMPLEMENTED
- No message.delivered handler
- No message.finalized handler

**STOP/HELP Handling:**
- ❌ NOT IMPLEMENTED

**Logging:**
- ✅ PARTIALLY IMPLEMENTED
  - JSON append to `/logs/rrg-openai.log`
  - Daily state tracking in `/logs/daily-state.json`
  - Logs include: timestamp, requestId, classification, lead data, alert status

**AI/Classifier:**
- ✅ IMPLEMENTED
  - GPT-4o-mini based intent classifier
  - System prompt detects: HOT / WARM / COLD / NOT_A_LEAD
  - Classifies: REFI / PURCHASE / SELL / SUPPORT / OTHER
  - Outputs: is_lead, classification, confidence, interest_type, urgency, notes, suggested_opener

**Human Handoff:**
- ✅ IMPLEMENTED (iMessage only)
  - Sends alert text to ALERT_NUMBERS when HOT or WARM
  - Alert format includes: classification, contact name, phone, interest type, urgency, notes, suggested opener
  - Uses AppleScript to send via Messages app

**Notes:**
- Backend is intent classification only (no SMS transport)
- Need to add Telnyx SDK to package.json
- Need to implement outbound SMS sender function
- Need to implement inbound webhook listener
- Daily call cap is working (50 calls/day, 2s throttle between calls)

---

## 4. DATABASE / STORAGE

**Storage Type:**
- CSV (shannon_cooper_150.csv)
- JSON state files (daily-state.json, rrg-openai.log)
- No SQL database (SQLite, Postgres, etc.)

**Existing Tables/Files:**

✅ **shannon_cooper_150.csv** (2 test rows currently)
```
Columns: lead_id, first_name, last_name, phone, email, city, state, address1, source
Rows: 2 (Testy McTestface, Jamie Leadman)
```

✅ **logs/daily-state.json** (call tracking)
```
Tracks: calls per day, last call timestamp, daily max cap
```

✅ **logs/rrg-openai.log** (JSONL format)
```
Each line = one classified request with full context
Includes: requestId, source, leadId, leadName, phone, city, state, message, classification, alerts sent
```

**Missing Tables/Files:**

❌ **contacts table** — Need to store:
- contact_id
- first_name, last_name
- phone_number
- test_contact (boolean)
- source
- opt_in/consent notes
- ai_enabled
- created_at
- last_contacted_at

❌ **sms_messages table** — Need to store:
- message_id
- contact_id
- direction (inbound/outbound)
- content
- status (pending/sent/delivered/failed)
- created_at
- timestamp

❌ **conversations table** — Need to store:
- conversation_id
- contact_id
- first_message_at
- last_message_at
- message_count
- status (active/closed)
- signals_detected (JSON array)

❌ **webhook_events table** — Need to store:
- event_id
- telnyx_event_id
- event_type (message.received, message.finalized, etc.)
- payload (raw JSON)
- processed (boolean)
- created_at

❌ **opt_outs table** — Need to store:
- contact_id
- opt_out_reason
- opt_out_date
- compliance_note

❌ **handoff_alerts table** — Need to store:
- alert_id
- contact_id
- alert_type (HOT/WARM/LUKEWARM)
- signal_type (REFI/BUY/SELL/REFERRAL)
- conversation_summary (text)
- recipients (JSON: [darren_phone, dj_phone])
- sent_at
- human_response_at

❌ **campaign_batches table** — Need to store:
- batch_id
- campaign_name
- status (pending/sent/in_progress/complete)
- contacts_count
- sent_count
- created_at

**Notes:**
- CSV is fine for test (150 leads)
- Need to migrate to JSON/SQLite/Supabase for production
- Logging structure is solid, expand to database tables

---

## 5. SHANNON COOPER VIDEO

**Found:** ✅ YES

**Path/URL:**
- Local file: `/Users/rrg/rrg/video.mp4` (8.9 MB)
- File type: MPEG-4 video
- Last modified: Mar 2, 2026

**Publicly Accessible:**
- ❌ NOT YET
- Currently local only (not hosted on web)

**SMS-Safe:**
- ❌ NOT YET
- Cannot link to local file in SMS
- Need to upload to public URL

**Notes:**
- **ACTION REQUIRED:** Upload video.mp4 to public CDN or hosting
  - Option A: Upload to GitHub Pages (RRGconnect-site/assets/shannon-video.mp4)
  - Option B: Upload to Vercel static storage
  - Option C: Upload to YouTube (unlisted) and share link
  - Option D: Upload to Google Drive (link shareable)
  - Option E: Upload to AWS S3 or Cloudflare (if available)
- Recommend: Host on rrgconnect.com/assets/shannon-video.mp4
- Once hosted, create short clean link: e.g., https://rrgconnect.com/assets/shannon-video.mp4
- Link must be SMS-safe (ideally <120 chars including domain)

---

## 6. EXISTING NOTIFICATION LOGIC

**Darren Alert:**
- ✅ IMPLEMENTED
  - Phone: 6268313336 (from .env ALERT_NUMBERS)
  - Method: iMessage via AppleScript
  - Trigger: When classification is HOT or WARM

**D.J. Backup Alert:**
- ✅ IMPLEMENTED
  - Phone: 9517416964 (from .env ALERT_NUMBERS)
  - Method: iMessage via AppleScript
  - Trigger: When classification is HOT or WARM

**Email/SMS Method:**
- iMessage (native macOS)
- No email integration
- No Telnyx SMS yet

**Alert Format (CURRENT):**
```
RRG HOT LEAD (CALL <5 MIN)
Source: Shannon Cooper Database
Lead: [Name] | Phone: (###) ###-####
Location: City, ST
Email: [email]
Interest: Refi/Purchase/Sell/Other
Urgency: Immediate/Soon/Later
Notes: [classifier notes]
Suggested opener: [suggested_opener]
```

**Notes:**
- Alert logic is solid
- When SMS transport added, can send same format via Telnyx
- Darren gets it first, D.J. as backup is correct

---

## 7. RISK / MISSING PIECES

### CRITICAL BLOCKERS

1. **Telnyx SMS Integration (100% MISSING)**
   - No SDK installed
   - No send_sms function
   - No inbound webhook handler
   - No Telnyx API key in .env
   - **Impact:** Cannot send or receive SMS
   - **Effort:** Medium (4-6 hours to implement)

2. **Shannon Video Not Publicly Hosted**
   - Video exists locally but not accessible from SMS
   - No URL to include in outbound message
   - **Impact:** Cannot include video link in first text
   - **Effort:** Low (20 mins to upload + test)

3. **Database Not Designed for SMS Workflows**
   - CSV works for lead lookup but not for conversations
   - No opt-out tracking
   - No conversation state machine
   - **Impact:** Can't track message threads or compliance
   - **Effort:** Medium (3-4 hours to add SQLite + tables)

### MEDIUM BLOCKERS

1. **Pam + Heather Test Contacts Not in CSV**
   - CSV only has "Testy McTestface" and "Jamie Leadman"
   - Need to add Pam and Heather phone numbers + consent records
   - **Impact:** Can't run beta test without updating CSV
   - **Effort:** Low (5 mins)

2. **No Inbound Message Parser**
   - Backend receives messages but doesn't parse conversation context
   - Each message treated as standalone, not thread
   - **Impact:** AI doesn't understand multi-turn conversation history
   - **Effort:** Medium (2-3 hours)

3. **No Refi Signal Detection Refinement**
   - Classifier looks for it but prompt isn't optimized for natural conversation discovery
   - May miss subtle refi cues
   - **Impact:** False negatives on refi interest
   - **Effort:** Low (1 hour to refine system prompt)

### LOW-RISK CLEANUP

1. **Logging could be more structured**
   - Currently JSON Lines (JSONL), works but not ideal for querying
   - Should add database tracking for easier analysis

2. **No rate limiting per contact**
   - Currently global rate limit (50/day total)
   - Should limit 2-3 messages per contact per day

3. **No conversation timeout**
   - No logic to close conversation after inactivity
   - Should auto-close after 24-48h with no reply

---

## 8. RECOMMENDED NEXT BUILD STEPS

### PHASE 1 — HOST SHANNON VIDEO (30 mins)
1. Upload video.mp4 to RRGconnect-site/assets/
2. Commit and push to GitHub Pages
3. Verify URL works: https://rrgconnect.com/assets/shannon-video.mp4
4. Create shortened reference link if needed

### PHASE 2 — ADD TEST CONTACTS (15 mins)
1. Update shannon_cooper_150.csv with:
   - Pam: first_name=Pam, phone=[verified number], source=Shannon Cooper Database, test_contact=true
   - Heather: first_name=Heather, phone=[verified number], source=Shannon Cooper Database, test_contact=true
2. Save and test CSV parsing reload

### PHASE 3 — SETUP TELNYX SMS (2-3 hours)
1. Add telnyx-node SDK to package.json
2. Add TELNYX_API_KEY and TELNYX_PHONE_NUMBER to .env
3. Implement send_sms(phone, message) function
4. Test outbound SMS to test phones
5. Implement inbound webhook handler at /webhook/telnyx
6. Test inbound message parsing

### PHASE 4 — BUILD CONVERSATION STATE (2 hours)
1. Create conversations table (JSON file or SQLite)
2. Add inbound message parser to track thread context
3. Pass conversation history to classifier (not just latest message)
4. Implement opt-out logic (STOP command)
5. Implement help logic (HELP command)

### PHASE 5 — REFINE REFI DETECTION (1 hour)
1. Enhance system prompt to probe for refi signals naturally
2. Add example conversations to classifier context
3. Test with sample messages: "rates", "payment", "mortgage", "equity", "refinance"
4. Tune confidence thresholds for Tier 1 alert trigger

### PHASE 6 — TEST BEFORE LIVE (1-2 hours)
1. Send test message to D.J.'s phone
2. Reply and verify inbound handler parses correctly
3. Check classifier detects interest signals
4. Verify Tier 1 alert goes to Darren + D.J.
5. Repeat with Heather
6. Test STOP and verify no further messages
7. Test HELP and verify response

---

## SUMMARY TABLE

| Component | Status | Ready | Notes |
|-----------|--------|-------|-------|
| **Website (RRGconnect)** | ✅ Live | Yes | Deployed, static only |
| **Backend (Intent Engine)** | ✅ Working | Yes | Localhost, GPT classifier runs |
| **Telnyx SMS** | ❌ Missing | No | Need SDK + implementation |
| **Inbound Webhook** | ❌ Missing | No | Need /webhook endpoint |
| **SMS Parser** | ❌ Missing | No | Need to add to handler |
| **Conversation State** | ❌ Missing | No | Need database tables |
| **Shannon Video** | ✅ Exists | No | Exists locally, need to host publicly |
| **Test Contacts** | ⚠️ Stub | No | Need Pam + Heather phone numbers |
| **Notifications (Darren+D.J.)** | ✅ Working | Yes | iMessage working, SMS soon |
| **Refi Detection** | ✅ Partial | Yes | Classifier works, prompt could be tuned |
| **Opt-out Logic** | ❌ Missing | No | Need STOP handler |
| **Compliance Logging** | ✅ Partial | Yes | Basic logging works, need tables |

---

## CRITICAL NEXT STEP

**D.J. DECISION REQUIRED:**

1. **Approve this audit?** (Yes / No / Modify)
2. **Proceed to PHASE 1-6 build?** (Yes / Now / Schedule for later)
3. **Telnyx API key available?** (Confirm)
4. **Test contact phone numbers ready?** (Pam + Heather confirmed)
5. **Expected timeline?** (Estimate: 8-12 hours total to go live)

---

**Audit completed by:** Rocky  
**Timestamp:** 2026-04-27T21:35:00Z  
**Status:** READY FOR BUILD APPROVAL
