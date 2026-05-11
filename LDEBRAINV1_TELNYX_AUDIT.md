# LDEBRAINV1 / Telnyx Integration Audit

**Date:** Tue Apr 28, 2026 09:13 MST  
**Auditor:** Rocky  
**Status:** Ready for credential injection  

---

## Question 1: Required Telnyx Environment Variables

**Answer:** The code requires exactly **3 Telnyx variables:**

```
TELNYX_API_KEY              (required for auth)
TELNYX_MESSAGING_PROFILE_ID (required for sending)
TELNYX_FROM_NUMBER          (required, used in outbound messages)
```

**Optional (has defaults):**
```
TELNYX_WEBHOOK_URL          (defaults to http://localhost:3000/webhook/telnyx)
```

**Source:** `server.js` lines 28-31

---

## Question 2: Webhook Signature Verification

**Answer:** ❌ **NOT IMPLEMENTED**

The webhook handler at `/webhook/telnyx` (line 650) does NOT verify Telnyx webhook signatures.

**Current behavior:**
- Receives POST to `/webhook/telnyx`
- Immediately returns `200 OK` (line 651)
- Processes all events without signature check
- No `TELNYX_PUBLIC_KEY` used anywhere

**Risk:** Any caller can POST fake events to this endpoint.

**Recommendation:** Before going live with real SMS, implement signature verification:
- Add `TELNYX_PUBLIC_KEY` to `.env`
- Verify `X-Telnyx-Signature-Ed25519` header on inbound webhooks
- Use Telnyx's public key to validate payload authenticity

---

## Question 3: Webhook Signature Verification Implementation

**Answer:** ❌ **NOT IMPLEMENTED** (confirmed in Question 2)

`TELNYX_PUBLIC_KEY` is **NOT** referenced anywhere in the code.

---

## Question 4: Outbound SMS Sending

**Answer:** Uses **both**, but correctly:

```javascript
const body = {
  to: toNumber,
  from: TELNYX_FROM_NUMBER,           // ← TELNYX_FROM_NUMBER (your Telnyx number)
  text: message,
  messaging_profile_id: TELNYX_MESSAGING_PROFILE_ID,  // ← TELNYX_MESSAGING_PROFILE_ID
};
```

**Source:** `server.js` lines 576-581

**How it works:**
- `to`: Recipient phone number (passed as argument)
- `from`: Your Telnyx sender number (TELNYX_FROM_NUMBER env var)
- `messaging_profile_id`: Telnyx profile ID (TELNYX_MESSAGING_PROFILE_ID env var)
- `text`: The message body

---

## Question 5: Exact .env Variable Names

**All variable names as written in code:**

```
TELNYX_API_KEY
TELNYX_MESSAGING_PROFILE_ID
TELNYX_FROM_NUMBER
TELNYX_WEBHOOK_URL
DARREN_PHONE
DJ_PHONE
OPENAI_API_KEY
OPENAI_MODEL
DAILY_MAX_CALLS
MIN_SECONDS_BETWEEN_CALLS
ALERT_NUMBERS
CSV_PATH
```

**Source:** `server.js` lines 14-34

---

## Question 6: No Live SMS Without Approval

**✅ CONFIRMED**

Current code has these safeguards:

1. **sendSmsViaTelnyx** (line 571):
   - Checks if `TELNYX_API_KEY || TELNYX_MESSAGING_PROFILE_ID` are empty
   - Returns `{ ok: false, error: "Telnyx not configured" }` if missing
   - Logs all outbound attempts to `logs/rrg-openai.log`

2. **Webhook handler** (line 650):
   - Only responds to `message.received` events (inbound SMS)
   - Does NOT auto-generate outbound unless configured

3. **Manual control**:
   - `POST /api/send-sms` requires explicit call (won't fire without curl/request)
   - Inbound webhooks require Telnyx to be configured
   - No cron jobs or automatic sending

**Current state: SAFE** — No SMS can send until credentials are added to `.env`

---

## Exact .env Template (Placeholder Values Only)

```env
# OpenAI
OPENAI_API_KEY=sk-proj-YOUR_OPENAI_KEY_HERE
OPENAI_MODEL=gpt-4o-mini
DAILY_MAX_CALLS=50
MIN_SECONDS_BETWEEN_CALLS=2

# Telnyx SMS
TELNYX_API_KEY=KEY1234567890abcdef
TELNYX_MESSAGING_PROFILE_ID=12345678-abcd-ef01-2345-6789abcdef01
TELNYX_FROM_NUMBER=+16025551234
TELNYX_WEBHOOK_URL=http://localhost:3000/webhook/telnyx

# Alert Recipients (iMessage)
DARREN_PHONE=6268313336
DJ_PHONE=9517416964
ALERT_NUMBERS=6268313336,9517416964

# CSV & Logging
CSV_PATH=./shannon_cooper_150.csv
```

---

## Critical Gaps (Before Live Deployment)

| Gap | Status | Action Required |
|-----|--------|-----------------|
| Webhook signature verification | ❌ Missing | Add before production |
| Rate limiting | ✅ Present | Guarded by DAILY_MAX_CALLS + MIN_SECONDS_BETWEEN_CALLS |
| Opt-out persistence | ⚠️ Partial | Logged to file, not database |
| Error handling | ✅ Present | Try/catch on all API calls |
| Logging | ✅ Present | JSONL logs to `logs/` directory |

---

## Testing Checklist (Before Real SMS)

- [ ] All `.env` variables filled in (Telnyx credentials from dashboard)
- [ ] Server starts: `node server.js` (check for "Telnyx: ✓ Configured" in logs)
- [ ] Test endpoint works: `curl -X POST http://localhost:3000/api/test-ldebrainv1 -d '{"phone":"6025551234","message":"Not really"}'`
- [ ] No actual SMS sent until explicitly approved
- [ ] Telnyx webhook URL configured in Telnyx dashboard pointing to your server
- [ ] First outbound SMS sent ONLY after D.J. approval

---

**Status:** ✅ Code is safe to configure. Awaiting your approval to add Telnyx credentials.
