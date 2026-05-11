# Webhook Structure Diagnostic — Investigation

**Time:** 18:49:18 UTC (Tue Apr 28, 2026 11:49 MST)  
**Status:** Data wrapping works, but event structure unclear

---

## Progress Made

### ✅ Webhook arrived
- 18:49:18.713Z
- Signature verified (timestamp|body format)
- req.body.data exists and was properly wrapped

### ✅ Data wrapping works
```json
{"type":"webhook_events_extracted","events_array_length":1,"events_is_array":true,"was_wrapped":true}
```

**This confirms:** `req.body.data` (object) was successfully wrapped into array with 1 element.

### ❌ Event type is undefined
```json
{"type":"webhook_event_check","event_index":0,"event_type":"undefined","is_message_received":false}
```

**Problem:** When we wrap `req.body.data`, the wrapped element doesn't have a `.type` property.

---

## What We Know About Telnyx Structure

**Raw body first 20 chars:** `"{\n  \"data\": {\n    \"e"`

This shows `data` is an object starting with another property (looks like `"events"` perhaps?).

**Hypothesis:** The actual structure might be:
```json
{
  "data": {
    "events": [...]  // Array of actual events
    // or
    "message": {...}  // Single message object
  }
}
```

NOT:
```json
{
  "data": [...]  // Array directly
}
```

---

## Added Diagnostic Logging

When next webhook arrives, we'll log:
```json
{
  "type": "webhook_event_structure",
  "event_keys": ["...list of properties..."],
  "event_type": "undefined",
  "has_payload": true/false,
  "has_data": true/false,
  "has_events": true/false
}
```

This will show us exactly what properties the wrapped object has.

---

## Likely Scenarios

### Scenario A: data.events
```javascript
req.body.data = {
  events: [
    { type: "message.received", payload: {...} }
  ]
}
```
→ Need to extract: `req.body.data.events` instead of `req.body.data`

### Scenario B: data is wrapper
```javascript
req.body.data = {
  type: "message.received",
  payload: {...}
}
```
→ Current wrapping is wrong, should use `req.body.data` directly as event

### Scenario C: Different structure
→ Logs will reveal it

---

## Next Action

**D.J.: Send one more test SMS.**

With the structure logging, we'll see exactly what properties are in the wrapped object, and can fix accordingly.

---

**Status:** Data wrapping works. Event extraction needs refinement based on actual structure.
