# Webhook Debug Test Plan — Comprehensive Logging

**Date:** Tue Apr 28, 2026 11:36 MST  
**Server restarted:** With comprehensive debug logging at each step  
**Status:** Ready for final diagnostic test

---

## Debug Logging Added

### Post-Verification Flow
- `webhook_post_verification` — Confirms signature verified, proceeding
- `webhook_body_check` — Logs req.body structure and data presence
- `webhook_events_extracted` — Logs events array length and type

### Event Processing
- `webhook_event_check` — For each event: index, type, is_message_received flag
- `webhook_event_skipped` — If event type != message.received, reason logged
- `webhook_message_received_entered` — Branch entered for message.received events
- `webhook_parsed_fields` — Phone number, text length extracted

### Lead Lookup & LDEBRAINV1
- `webhook_lead_lookup_start` — Before lookup
- `webhook_lead_lookup_result` — After lookup: found?, name, ID
- `webhook_ldebrainv1_calling` — Before LDEBRAINV1 call
- `webhook_ldebrainv1_result` — After LDEBRAINV1: action, has_message, alert_level, should_stop
- `inbound_sms` — Full entry (original behavior)

### Actions
- `webhook_action_check` — Should send SMS? Should alert?
- `webhook_sending_sms` — Before SMS sent
- `webhook_sms_sent` — After SMS sent successfully
- `webhook_sending_alert` — Before alert sent
- `webhook_alert_sent` — After alert sent successfully

### Errors & Completion
- `webhook_exception` — Any exception: error_message, stack snippet, text length
- `webhook_handler_complete` — Final: events processed count

---

## Expected Trace (Success Path)

```
webhook_post_verification → verified_proceeding
webhook_body_check → req_body_exists, req_body_data_exists, data_length
webhook_events_extracted → events_array_length (should be 1+)
webhook_event_check → event_index 0, type "message.received"
webhook_message_received_entered
webhook_parsed_fields → from_number, text_length
webhook_lead_lookup_start
webhook_lead_lookup_result → lead_found
webhook_ldebrainv1_calling
webhook_ldebrainv1_result → action, alert_level
inbound_sms → FULL ENTRY
webhook_action_check → should_send_sms/should_alert
webhook_sending_sms (if action=send)
webhook_sms_sent (if action=send)
webhook_handler_complete → events_processed 1
```

---

## What We're Looking For

1. **Does req.body?.data exist?**
   - If NO → body not being parsed correctly
   - If YES → parsing OK

2. **Are there events in the array?**
   - If length = 0 → no events, handler exits early
   - If length > 0 → events present

3. **What is the event type?**
   - If "message.received" → correct, enters branch
   - If something else → skipped, never processed

4. **Does webhook_message_received_entered appear?**
   - If YES → branch entered, LDEBRAINV1 should run
   - If NO → event type mismatch

5. **Does webhook_ldebrainv1_calling appear?**
   - If YES → LDEBRAINV1 called successfully
   - If NO → exception before LDEBRAINV1

6. **Does webhook_ldebrainv1_result appear?**
   - If YES → LDEBRAINV1 completed, result logged
   - If NO → exception during LDEBRAINV1

7. **Does inbound_sms appear?**
   - If YES → main logging works
   - If NO → exception between LDEBRAINV1 and logging

8. **Do webhook_sending_sms/webhook_alert_sent appear?**
   - If YES → actions executed
   - If NO → no actions triggered

---

## Next Action

**D.J.: Send one fresh SMS reply.**

Logs will capture complete flow with all debug entries. We'll see exactly where the processing stops or what goes wrong.

---

**Status:** Debug infrastructure ready. Awaiting test SMS.
