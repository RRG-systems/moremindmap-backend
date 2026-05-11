# Webhook Structure Issue — ROOT CAUSE FOUND

**Time:** 18:39:56 UTC (Tue Apr 28, 2026 11:40 MST)  
**Status:** 🔴 BLOCKED — Telnyx webhook structure mismatch

---

## Confirmed Evidence Chain

### 1. Did the webhook arrive?
**✅ YES** — 18:39:56.837Z

### 2. Did signature verification pass?
**✅ YES** 
```json
{"type":"webhook_signature_verified","format_used":"timestamp|body"}
```

### 3. Was req.body populated?
**✅ YES**
```json
{"type":"webhook_post_verification","status":"verified_proceeding"}
{"type":"webhook_body_check","req_body_exists":true,"req_body_data_exists":true}
```

### 4. Was the Telnyx event parsed correctly?
**❌ NO — DATA IS NOT AN ARRAY**

```json
{"type":"webhook_body_check","req_body_exists":true,"req_body_data_exists":true,"req_body_data_is_array":false}
{"type":"webhook_events_extracted","events_is_array":false}
{"type":"webhook_error_events_not_array","details":"Returning early"}
```

---

## ROOT CAUSE 🔴

**Code expects:**
```javascript
req.body.data = [...]  // Array of events
```

**Telnyx sends:**
```javascript
req.body.data = {...}  // Object (not array)
```

---

## Evidence from Raw Body

The diagnostic log shows:
```
rawbody_first_20: "{\n  \"data\": {\n    \"e"
```

This confirms `data` is an **object** (`{`), not an **array** (`[`).

---

## The Flow That Should Happen

```
webhook arrives
  ↓
signature verified ✅
  ↓
req.body parsed ✅
  ↓
req.body.data exists ✅
  ↓
req.body.data is array ❌ ← BLOCKER HERE
  ↓
(returns early, never processes messages)
```

---

## The Fix

**Change this line:**
```javascript
const events = req.body?.data || [];
if (!Array.isArray(events)) return;
```

**To handle object structure:**
```javascript
// If data is an array, use it directly
// If data is an object, wrap it or extract events from it
const events = Array.isArray(req.body?.data) 
  ? req.body.data 
  : (req.body?.data ? [req.body.data] : []);
```

OR inspect the actual Telnyx webhook structure more carefully to understand what property holds the events.

---

## What We Know About Telnyx Structure

- `req.body.data` exists ✅
- `req.body.data` is an object ✅ (not array)
- Raw body length: 1730 bytes
- First 20 chars: `"{\n  \"data\": {\n    \"e"`

The object likely has event properties/fields that need to be extracted differently.

---

## Recommendation

**Next step:** 
1. Add logging to dump the actual structure of `req.body.data`
2. See what properties it has
3. Determine correct path to extract event(s)
4. Update code to handle that structure

---

## Complete Chain Blocked

```
webhook_received_diagnostic ✅
webhook_signature_verified ✅
webhook_post_verification ✅
webhook_body_check ✅ (but data not array)
webhook_events_extracted ❌ (not array, exits)
→ NEVER REACHES:
  - webhook_message_received_entered
  - webhook_lead_lookup_start
  - webhook_ldebrainv1_calling
  - inbound_sms
  - webhook_action_check
  - webhook_sending_sms
```

**Everything blocked by data structure issue.**

---

**Status:** Root cause identified. Fix is straightforward: handle non-array data structure.
