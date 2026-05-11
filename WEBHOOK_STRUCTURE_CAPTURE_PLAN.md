# Webhook Structure Capture Plan

**Date:** Tue Apr 28, 2026 11:52 MST  
**Server:** Restarted with comprehensive structure logging  
**Goal:** Capture exact Telnyx webhook structure without sensitive data

---

## Logging Deployed

### Top-Level Structure
- `webhook_toplevel_structure` entry will log:
  - `req_body_keys` — all keys at root level
  - `req_body_data_type` — is it object, array, string?
  - `req_body_data_keys` — all keys in req.body.data
  - Presence checks: `has_type`, `has_payload`, `has_event_type`, `has_events`, `has_attributes`, `has_record_type`, `has_id`

### Nested Structure
- `webhook_payload_structure` — if data.payload exists, log its keys
- `webhook_attributes_structure` — if data.attributes exists, log its keys
- `webhook_event_structure` — original logging showing wrapped event properties

---

## What We'll Extract (Safe Metadata Only)

1. ✅ Key names (property paths)
2. ✅ Data types (object, string, number, array)
3. ✅ Existence flags (has_X, true/false)
4. ❌ No phone numbers
5. ❌ No message text
6. ❌ No Telnyx IDs (will be reported as "present" only)

---

## Expected Output

```json
{
  "type": "webhook_toplevel_structure",
  "req_body_keys": ["data"],
  "req_body_data_type": "object",
  "req_body_data_keys": ["type", "id", "payload", "timestamp", ...],
  "req_body_data_has_type": true/false,
  "req_body_data_has_payload": true,
  "req_body_data_has_events": false,
  "..."
}
```

Then (if payload exists):
```json
{
  "type": "webhook_payload_structure",
  "payload_keys": ["from", "to", "text", "received_at", ...]
}
```

---

## Analysis Process

Once we see the structure:
1. Identify where `type` / `record_type` / `event_type` field is
2. Identify where `from` / `to` / `text` fields are
3. Determine correct extraction path
4. Update code to use that path instead of wrong assumptions

---

## Next Action

**D.J.: Send one fresh SMS reply.**

Server will capture:
- Top-level keys
- Data structure
- Payload structure (if nested)
- Attributes structure (if present)
- All property names (safe metadata)

---

**Ready to capture. Awaiting your SMS.**
