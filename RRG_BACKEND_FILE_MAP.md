# RRG BACKEND FILE MAP & BUILD READINESS

**Date:** Mon Apr 27, 2026 @ 14:55 MST  
**Status:** READY FOR APPROVAL — No edits made yet

---

## 1. PROJECT STRUCTURE

### Directory Tree (non-node_modules)

```
/Users/rrg/rrg/
├── server.js                    ← Main entry point (Express app)
├── package.json                 ← Dependencies + scripts
├── package-lock.json            ← Locked versions
├── .env                         ← Environment variables (secret, not in git)
├── shannon_cooper_150.csv       ← Lead database
└── logs/
    ├── daily-state.json         ← Daily call tracking (state machine)
    └── rrg-openai.log           ← JSONL log of all classifications
```

### Key Folders

- `/logs/` — Persisted state and audit trails
- `node_modules/` — Dependencies (dotenv, express, openai)

### Entry File

**`/Users/rrg/rrg/server.js`** (519 lines)
- Single monolithic file (intentionally simple for testing)
- All logic: CSV loading, classifying, alerting, logging
- Starts server on `localhost:3000`

### Package Scripts

```json
"scripts": {
  "test": "echo \"Error: no test specified\" && exit 1"
}
```

**No start script defined** — users run `node server.js` directly

---

## 2. EXISTING ROUTES/ENDPOINTS

### Route Inventory

| Route | Method | Purpose | Current Status |
|-------|--------|---------|-----------------|
| `/` | GET | HTML control panel UI | ✅ Working |
| `/status` | GET | Daily metrics + config | ✅ Working |
| `/reload-csv` | POST | Reload lead database | ✅ Working |
| `/classify` | POST | Main classifier endpoint | ✅ Working |

### Route Details

#### `GET /` — Control Panel UI
- **Purpose:** HTML interface for manual testing
- **Returns:** Full HTML page with form + output display
- **JavaScript:** Client-side fetch to `/classify` and `/status`
- **Used by:** Human operator via browser (localhost:3000)

#### `GET /status` — Daily Status
- **Purpose:** Check call count, config, log paths
- **Query params:** None
- **Response:** JSON
  ```json
  {
    "day": "2026-04-27",
    "calls_used_today": 5,
    "daily_max_calls": 50,
    "log_file": "/Users/rrg/rrg/logs/rrg-openai.log",
    "alert_numbers": ["6268313336", "9517416964"],
    "csv_path": "/Users/rrg/rrg/shannon_cooper_150.csv"
  }
  ```

#### `POST /reload-csv` — Reload Leads
- **Purpose:** Refresh lead database without restarting server
- **Body:** None required
- **Response:** JSON
  ```json
  {
    "ok": true,
    "loaded": 150,
    "csv_path": "/Users/rrg/rrg/shannon_cooper_150.csv"
  }
  ```

#### `POST /classify` — Classify Lead Intent
- **Purpose:** Core business logic — parse lead message, classify intent, trigger alerts
- **Body:** JSON
  ```json
  {
    "source": "Shannon Cooper Database",
    "leadId": "SC001",
    "phone": "555-123-4567",
    "message": "I'm thinking about refinancing. Can someone call me?"
  }
  ```
- **Response:** JSON (full example below)

---

## 3. CLASSIFIER LOGIC

### File Location
**`/Users/rrg/rrg/server.js`**

### Function: `buildSystemPrompt()`
- **Lines:** ~45-80 (within server.js)
- **Purpose:** Returns system prompt for GPT classifier
- **Return type:** String (multi-line prompt text)

```javascript
function buildSystemPrompt() {
  return `
You are RRG Intent Engine v0.3.

Output STRICT JSON only. No markdown. No extra keys.

Your job:
- Determine if the message indicates a "lead" (user wants a call / wants to refi / wants a human / wants next step)
- Classify: HOT / WARM / COLD / NOT_A_LEAD
- Provide urgency: Immediate / Soon / Later / Unknown
- Provide interest_type: Refinance / Purchase / Sell / Support / Other
- Produce a short notes line and a suggested opener line.

Rules:
- HOT = explicit request to talk/call/apply/quote today/now OR direct purchase intent
- WARM = interest but not ready today (thinking, exploring, questions)
- COLD = general, vague, no clear next step
- NOT_A_LEAD = spam, wrong number, hostility, nonsense

Return JSON schema:
{
  "is_lead": true|false,
  "classification": "HOT"|"WARM"|"COLD"|"NOT_A_LEAD",
  "confidence": 0.0-1.0,
  "interest_type": "Refinance"|"Purchase"|"Sell"|"Support"|"Other",
  "urgency": "Immediate"|"Soon"|"Later"|"Unknown",
  "notes": "string",
  "suggested_opener": "string"
}
`.trim();
}
```

### Function: `POST /classify` Handler
- **Lines:** ~360-490 (main async handler)
- **Input:**
  - `req.body.source` (string, e.g., "Shannon Cooper Database")
  - `req.body.leadId` (optional, string, e.g., "SC001")
  - `req.body.phone` (optional, string, e.g., "5551234567")
  - `req.body.message` (required, string, the user message)

- **Processing Flow:**
  1. Extract/normalize phone number
  2. Look up lead in CSV by leadId or phone
  3. Check rate limit (daily max + throttle)
  4. Call OpenAI with system prompt + user message
  5. Parse JSON response from GPT
  6. Build alert text
  7. Send iMessage alerts if lead + HOT/WARM
  8. Log everything to JSONL
  9. Return response JSON

- **Output Format:**
  ```json
  {
    "ok": true,
    "requestId": "rrg_1704067200000",
    "callNumberToday": 5,
    "lead_resolved": true,
    "lead": {
      "lead_id": "SC001",
      "name": "Testy McTestface",
      "phone": "(555) 123-4567",
      "city": "Tempe",
      "state": "AZ",
      "email": "testy@example.com",
      "source": "Shannon Cooper Database"
    },
    "output": {
      "is_lead": true,
      "classification": "HOT",
      "confidence": 0.95,
      "interest_type": "Refinance",
      "urgency": "Immediate",
      "notes": "Explicitly requested call today for refi.",
      "suggested_opener": "Thanks for reaching out! I'll have someone from our team call you within 15 minutes."
    },
    "alert_text": "RRG HOT LEAD (CALL <5 MIN)\nSource: Shannon Cooper Database\nLead: Testy McTestface | Phone: (555) 123-4567\n...",
    "alert": {
      "sent": 2,
      "targets": ["6268313336", "9517416964"]
    },
    "usage": {
      "prompt_tokens": 312,
      "completion_tokens": 94,
      "total_tokens": 406
    }
  }
  ```

### Model Used
- **Model:** `gpt-4o-mini` (default, configurable via `OPENAI_MODEL` env var)
- **Temperature:** 0.2 (deterministic, not creative)
- **API Key:** `process.env.OPENAI_API_KEY`

### Current Prompt Assessment
- ✅ **Strengths:**
  - Clear classification schema (HOT/WARM/COLD/NOT_A_LEAD)
  - Interest type detection (Refi/Purchase/Sell/Support/Other)
  - Urgency detection
  - Suggested opener (useful for human handoff)

- ⚠️ **Opportunities for refinement:**
  - Refi signal detection could be more nuanced (e.g., "wondering if rates are better" = WARM, not COLD)
  - Could probe more directly for homeownership status
  - Could detect multi-signal leads (e.g., "thinking of refi AND selling")

---

## 4. ALERT LOGIC

### File Location
**`/Users/rrg/rrg/server.js`**

### Function: `sendIMessage(toNumber, message)`
- **Lines:** ~180-210
- **Purpose:** Send alert via macOS Messages app (iMessage)
- **How it works:**
  1. Normalizes phone number (remove dashes, extract digits)
  2. Constructs AppleScript code string
  3. Executes via `osascript` command
  4. Returns Promise (resolve on success, reject on error)
- **Implementation:**
  ```javascript
  const script = `
    tell application "Messages"
      set targetService to 1st service whose service type = iMessage
      set targetBuddy to buddy "${num}" of targetService
      send "${String(message).replace(/"/g, '\\"')}" to targetBuddy
    end tell
  `;
  execFile("osascript", ["-e", script], (err) => {
    if (err) return reject(err);
    resolve(true);
  });
  ```

### Function: `sendAlertToAll(alertText)`
- **Lines:** ~212-227
- **Purpose:** Broadcast alert to all recipients in ALERT_NUMBERS
- **How it works:**
  1. Iterate through ALERT_NUMBERS from env var
  2. Call sendIMessage for each number
  3. Add 150ms delay between messages (so Messages app doesn't get weird)
  4. Log any errors
  5. Return count of successfully sent alerts

### Alert Recipients

**Darren (Primary):** 626-831-3336  
**D.J. (Backup):** 951-741-6964

**Method:** iMessage via AppleScript (native macOS)  
**Not SMS, not email** — iMessage only (requires Mac with Messages app)

### Alert Trigger Logic (from /classify handler)
```javascript
// Send iMessage ONLY if it's a lead and HOT/WARM
const isLead = !!parsed.is_lead;
if (isLead && (classification === "HOT" || classification === "WARM")) {
  alertResult = await sendAlertToAll(alertText);
}
```

### Alert Text Format
```
RRG HOT LEAD (CALL <5 MIN)
Source: Shannon Cooper Database
Lead: [Name] | Phone: (###) ###-####
Location: [City], [State]
Email: [Email]
Interest: [Refi/Purchase/Sell/Other]
Urgency: [Immediate/Soon/Later/Unknown]
Notes: [Classifier notes]
Suggested opener: [Suggested opener from GPT]
```

---

## 5. DATA/STORAGE LOGIC

### CSV Lead Database

**File:** `/Users/rrg/rrg/shannon_cooper_150.csv`

**Columns:**
```
lead_id, first_name, last_name, phone, email, city, state, address1, source
```

**Current Records:** 2 (Testy McTestface, Jamie Leadman) — meant to be expanded to 150

**Loading Function:** `loadLeadsCsv(filePath)`
- **Lines:** ~115-165
- **How it works:**
  1. Read file from disk
  2. Parse CSV with custom minimal parser (handles quoted fields)
  3. Build two maps: `byPhone` (normalized 10-digit) and `byId` (lead_id string)
  4. Return `{ leads: [], byPhone: Map, byId: Map }`

**Lead Lookup Function:** `lookupLead({ leadId, phone, source })`
- **Lines:** ~320-330
- **How it works:**
  1. If leadId provided, search byId map
  2. Else if phone provided, normalize and search byPhone map
  3. Return lead record or null

### JSON State File

**File:** `/Users/rrg/rrg/logs/daily-state.json`

**Purpose:** Track API call count per day (guardrail)

**Structure:**
```json
{
  "2026-02-26": {
    "calls": 5,
    "lastCallAt": 1772128978074
  }
}
```

**Functions:**
- `readState()` — Load JSON from disk (catches parse errors, returns {})
- `writeState(state)` — Write JSON to disk (overwrites)
- `recordCall()` — Increment call count for today, update lastCallAt, persist to disk

### JSONL Log File

**File:** `/Users/rrg/rrg/logs/rrg-openai.log`

**Purpose:** Audit trail of all classifications (one JSON object per line)

**Entry Format:**
```json
{
  "t": "2026-02-26T15:30:35.995Z",
  "requestId": "rrg_1704067200000",
  "source": "Shannon Cooper Database",
  "leadId": "SC001",
  "leadName": "Testy McTestface",
  "phone": "5551234567",
  "city": "Tempe",
  "state": "AZ",
  "message": "[user message]",
  "output": { ... classification JSON ... },
  "alert_sent": 2,
  "alert_targets": ["6268313336", "9517416964"],
  "usage": { "prompt_tokens": 312, "completion_tokens": 94, "total_tokens": 406 },
  "callNumberToday": 5
}
```

**Function:** `appendLog(obj)`
- **Lines:** ~70-72
- **How it works:** Append JSON-stringified object + newline to log file

### State Update Flow
```
Request → canCallOpenAI() checks limit → recordCall() increments + persists → 
  OpenAI call → Logging → Alert (if HOT/WARM)
```

---

## 6. ENVIRONMENT VARIABLES

### Required Env Vars

| Variable | Type | Default | Status | Example |
|----------|------|---------|--------|---------|
| `OPENAI_API_KEY` | string | Required | ✅ Set in .env | `sk-proj-...` |
| `OPENAI_MODEL` | string | `gpt-4o-mini` | ✅ Set in .env | `gpt-4o-mini` |
| `DAILY_MAX_CALLS` | number | 50 | ✅ Set in .env | `50` |
| `MIN_SECONDS_BETWEEN_CALLS` | number | 2 | ✅ Set in .env | `2` |
| `ALERT_NUMBERS` | string (comma-sep) | `` | ✅ Set in .env | `6268313336,9517416964` |
| `PORT` | number | 3000 | ⚠️ Not in .env | `3000` |
| `CSV_PATH` | string | `./shannon_cooper_150.csv` | ⚠️ Not in .env | `/Users/rrg/rrg/shannon_cooper_150.csv` |

### Current .env (sanitized)

```bash
OPENAI_API_KEY=sk-proj-[REDACTED]
OPENAI_MODEL=gpt-4o-mini
DAILY_MAX_CALLS=50
MIN_SECONDS_BETWEEN_CALLS=2
ALERT_NUMBERS=6268313336,9517416964
```

### Loading Mechanism
```javascript
require("dotenv").config();  // Line 1 of server.js
const MODEL = process.env.OPENAI_MODEL || "gpt-4o-mini";
const DAILY_MAX_CALLS = Number(process.env.DAILY_MAX_CALLS || 50);
const ALERT_NUMBERS = (process.env.ALERT_NUMBERS || "")
  .split(",")
  .map((s) => s.trim())
  .filter(Boolean);
```

---

## 7. TELNYX READINESS

### Current Dependency Status

**package.json (current):**
```json
{
  "dependencies": {
    "dotenv": "^17.3.1",
    "express": "^5.2.1",
    "openai": "^6.25.0"
  }
}
```

- ❌ No `telnyx` SDK
- ❌ No `axios` (would need for HTTP requests to Telnyx)
- ✅ `express` can handle webhooks natively

### Required Additions to package.json

```json
"dependencies": {
  ...existing...,
  "telnyx": "^2.x.x",
  "axios": "^1.x.x"  // optional, but easier for SMS HTTP calls
}
```

### Where to Add Send SMS Function

**New function location:** After `sendAlertToAll()` in server.js (around line 230)

```javascript
async function sendSms(toPhone, messageText) {
  // Use Telnyx SDK to send SMS
  // Return { ok: true, messageId: "..." }
}
```

### Where to Add Inbound Webhook Route

**New route location:** After `/classify` POST handler (around line 500)

```javascript
app.post("/webhook/telnyx", async (req, res) => {
  // Parse incoming Telnyx webhook
  // Extract sender phone, message text, event type
  // Log inbound message
  // Call classifier
  // Store conversation state
  // Trigger alerts if needed
  res.json({ received: true });
});
```

### Required .env Variables for Telnyx

```bash
TELNYX_API_KEY=pk_[key]
TELNYX_PUBLIC_KEY=pk_[key]
TELNYX_PHONE_NUMBER=+1[number]
TELNYX_WEBHOOK_URL=https://[public-domain]/webhook/telnyx
```

**Note:** TELNYX_WEBHOOK_URL must be public (can't be localhost:3000) — needs ngrok or Vercel deployment

---

## 8. SHANNON VIDEO HOSTING RECOMMENDATION

### Current State
- **File:** `/Users/rrg/rrg/video.mp4` (8.9 MB, local only)
- **Problem:** Can't link to local file in SMS
- **Need:** Public URL

### Option A: Recommended — Host on RRGconnect GitHub Pages
**Pros:**
- Already deployed + trusted domain
- No additional infrastructure
- Simple git commit to add file
- CDN-backed (Vercel)

**Cons:**
- Adds to GitHub repo size

**Implementation:**
1. Copy video.mp4 to `/Users/rrg/RRGconnect-site/assets/shannon-video.mp4`
2. Commit and push to GitHub
3. Access at: `https://rrgconnect.com/assets/shannon-video.mp4`
4. Link in SMS: `https://rrgconnect.com/assets/shannon-video.mp4` (68 chars)

### Option B: Alternative — Shannon Update Landing Page (HTML)
**Create:** `/Users/rrg/RRGconnect-site/shannon-update.html`
- Embedded video player
- Context message from Shannon
- CTA button (call/text to reply)
- Compliance notice

**Link in SMS:** `https://rrgconnect.com/shannon-update.html` (45 chars)

**Pros:** More branded, better UX, context

**Cons:** Extra HTML file to maintain

### Option C: YouTube (Unlisted)
**Pros:** Reliable, auto-hosted

**Cons:** Need YouTube account, sharing YouTube link (less clean), not owning the asset

### Option D: Google Drive (Shareable Link)
**Pros:** Already may have Drive setup

**Cons:** Long share URL, less professional, not SMS-friendly

---

## RECOMMENDATION: Option A (Direct File) + Option B (Landing Page)

**Best approach:** Do both:

1. **Host raw video at:** `https://rrgconnect.com/assets/shannon-video.mp4`
   - Direct link for SMS (clean, short)
   - First text can link directly to video

2. **Optional landing page at:** `https://rrgconnect.com/shannon-update.html`
   - For follow-up messages ("Check out this message from Shannon...")
   - Better context, embedded player
   - Can track views if needed

**Exact files needed:**

| File | Location | Action |
|------|----------|--------|
| `video.mp4` | `/Users/rrg/RRGconnect-site/assets/shannon-video.mp4` | Copy from `/Users/rrg/rrg/video.mp4` |
| `shannon-update.html` | `/Users/rrg/RRGconnect-site/shannon-update.html` | NEW (optional) |
| `index.html` | `/Users/rrg/RRGconnect-site/index.html` | Already deployed |

**Final SMS-safe URLs:**
- Raw video: `https://rrgconnect.com/assets/shannon-video.mp4` (68 chars)
- Landing page: `https://rrgconnect.com/shannon-update.html` (45 chars)

---

## 9. BUILD PLAN AFTER FILE MAP APPROVAL

### Phase 1: Host Shannon Video (30 mins, LOW RISK)
**Files to change:**
- Copy `/Users/rrg/rrg/video.mp4` → `/Users/rrg/RRGconnect-site/assets/shannon-video.mp4`
- Optionally create `/Users/rrg/RRGconnect-site/shannon-update.html` (landing page)

**Steps:**
1. Create `/Users/rrg/RRGconnect-site/assets/` folder
2. Copy video.mp4 to assets/
3. (Optional) Create shannon-update.html with embedded player
4. Commit: `git add assets/shannon-video.mp4 shannon-update.html`
5. Push to GitHub
6. Verify: `https://rrgconnect.com/assets/shannon-video.mp4` loads

**Risk:** Minimal — just file hosting

---

### Phase 2: Update Test Contacts in CSV (15 mins, MINIMAL RISK)
**Files to change:**
- `/Users/rrg/rrg/shannon_cooper_150.csv`

**Steps:**
1. Add rows for Pam and Heather (need confirmed phone numbers from D.J.)
2. Save CSV
3. Test CSV parsing by hitting `/reload-csv` POST endpoint

**Risk:** Minimal — just data, no code

---

### Phase 3: Add Telnyx SDK to Backend (30 mins, LOW RISK)
**Files to change:**
- `/Users/rrg/rrg/package.json`
- `/Users/rrg/rrg/.env`

**Steps:**
1. Add `"telnyx": "^2.x.x"` to dependencies
2. Run `npm install`
3. Add `TELNYX_API_KEY`, `TELNYX_PUBLIC_KEY`, `TELNYX_PHONE_NUMBER` to .env
4. Restart server (`node server.js`)
5. Verify Telnyx SDK imports work

**Risk:** Low — dependency only, no logic yet

---

### Phase 4: Implement Send SMS Function (1.5 hours, MEDIUM RISK)
**Files to change:**
- `/Users/rrg/rrg/server.js` (add sendSms function)

**Steps:**
1. Create `async function sendSms(toPhone, messageText)` using Telnyx SDK
2. Test with single SMS to test phone
3. Add error handling + logging
4. Hook into classifier (replace iMessage with SMS for production)

**Risk:** Medium — new external API call, needs testing

---

### Phase 5: Implement Inbound Webhook Handler (2 hours, MEDIUM-HIGH RISK)
**Files to change:**
- `/Users/rrg/rrg/server.js` (add POST /webhook/telnyx route)

**Steps:**
1. Create `app.post("/webhook/telnyx", ...)` endpoint
2. Parse Telnyx webhook payload (message.received, message.finalized)
3. Extract inbound message + sender phone
4. Look up lead in CSV
5. Call classifier with message
6. Log conversation state
7. Trigger alerts if needed
8. Handle STOP command (add to opt-outs)
9. Test with live inbound SMS

**Risk:** Medium-High — webhook timing, parsing, state management

---

### Phase 6: Add Conversation State Machine (2 hours, MEDIUM-HIGH RISK)
**Files to change:**
- `/Users/rrg/rrg/server.js` (new conversation table logic)
- `/Users/rrg/rrg/.env` (add DB config if using external DB)

**Steps:**
1. Create in-memory conversation store (or SQLite file)
2. Track conversation_id → [message1, message2, ...]
3. Pass full conversation history to GPT classifier
4. Implement opt-out tracking (STOP command)
5. Auto-close conversations after timeout (24-48h)
6. Test multi-turn conversations

**Risk:** Medium-High — state consistency, message ordering

---

### Phase 7: Refine Refi Detection Prompt (1 hour, LOW RISK)
**Files to change:**
- `/Users/rrg/rrg/server.js` (update buildSystemPrompt function)

**Steps:**
1. Enhance prompt with refi-specific examples
2. Add guidance for detecting subtle signals ("wondering if", "maybe", "curious")
3. Test with sample messages
4. Tune confidence thresholds for Tier 1 alert

**Risk:** Low — only prompt changes, no logic

---

### Phase 8: Full Integration Test (1-2 hours, HIGH RISK)
**Files to change:**
- None (testing phase)

**Steps:**
1. Send initial SMS from backend to Pam's phone (via `/classify` endpoint)
2. Pam replies naturally
3. Inbound webhook receives reply
4. Classifier processes it
5. Verify Tier 1 alert goes to Darren + D.J.
6. Repeat with Heather
7. Test STOP command
8. Test HELP command
9. Verify no further messages after STOP

**Risk:** High — live SMS, real users, timing issues

---

## TOTAL EFFORT & TIMELINE

| Phase | Effort | Risk | Cumulative |
|-------|--------|------|-----------|
| 1: Host Video | 30 min | Low | 30 min |
| 2: Update CSV | 15 min | Minimal | 45 min |
| 3: Telnyx SDK | 30 min | Low | 1h 15m |
| 4: Send SMS | 1.5h | Medium | 2h 45m |
| 5: Inbound Webhook | 2h | Medium-High | 4h 45m |
| 6: Conversation State | 2h | Medium-High | 6h 45m |
| 7: Refi Detection | 1h | Low | 7h 45m |
| 8: Integration Test | 1-2h | High | 8h 45m - 9h 45m |

**Total: ~9-10 hours** (can parallelize some phases)

---

## DECISION CHECKLIST FOR D.J.

Before proceeding:

- [ ] Approve this file map?
- [ ] Approve build plan (Phases 1-8)?
- [ ] Confirm Telnyx API key available?
- [ ] Confirm Pam's test phone number?
- [ ] Confirm Heather's test phone number?
- [ ] Confirm Telnyx phone number to send from?
- [ ] Ready to start Phase 1 immediately?
- [ ] Deployment target for backend? (localhost, Vercel, Heroku, etc.)

---

**File map created by:** Rocky  
**Timestamp:** 2026-04-27T21:55:00Z  
**Status:** READY FOR D.J. APPROVAL — NO EDITS YET
