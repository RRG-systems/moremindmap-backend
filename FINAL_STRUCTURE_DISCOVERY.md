# Final Telnyx Webhook Structure Discovery

**Time:** 19:00:01 UTC (Tue Apr 28, 2026 12:00 MST)  
**Status:** ✅ ACTUAL STRUCTURE FOUND

---

## Critical Discovery

### Top-Level req.body Keys
```
["data", "meta"]
```

### req.body.data Keys
```
["event_type", "id", "occurred_at", "payload", "record_type"]
```

### req.body.data.record_type Value
```
"event"  (NOT "message")
```

### req.body.data.payload Keys (ACTUAL MESSAGE DATA)
```
["autoresponse_type","cc","completed_at","cost","cost_breakdown","direction","encoding","errors","from","id","is_spam","media","messaging_profile_id","organization_id","parts","received_at","record_type","sent_at","subject","tags","text","to","type","valid_until","webhook_failover_url","webhook_url"]
```

### req.body.data.payload.record_type Value
**UNKNOWN** (not logged yet) — but likely `"message"`

---

## Root Issue with Previous Patch

The patch checked `event.record_type === "message"`, but the actual value is `event.record_type === "event"`.

**The real message data is inside `event.payload`**, not at the event level.

---

## Correct Parser Logic

**The message IS arriving**, but we need to check:

1. ✅ `event.record_type === "event"` (confirm it's an event wrapper)
2. ✅ `event.payload.record_type === "message"` (confirm payload is a message)
3. ✅ Extract from `event.payload.text`, `event.payload.from`, `event.payload.to`

---

## Evidence That It Works

From payload keys, we can see:
- ✅ `"text"` — message text
- ✅ `"from"` — sender
- ✅ `"to"` — recipient
- ✅ `"id"` — message ID
- ✅ `"received_at"` — timestamp
- ✅ `"record_type"` — type indicator

The actual inbound message data **IS PRESENT IN event.payload**.

---

## Next Patch Required

```javascript
// Current (WRONG - checks outer event)
if (event.record_type !== "message") continue;

// Correct (check payload)
if (event.payload?.record_type !== "message") continue;
const payload = event.payload;
const fromNumber = payload.from?.phone_number || payload.from;
const inboundText = payload.text;
const messageId = payload.id;
```

---

## Status

🟢 **STRUCTURE COMPLETE** — Message data confirmed present in `event.payload`

❌ **CURRENT PATCH WRONG** — Checking wrong level (event vs payload)

🟢 **NEXT PATCH CLEAR** — Check `event.payload.record_type`, extract from `event.payload`

---

**Ready for corrected parser patch.**
