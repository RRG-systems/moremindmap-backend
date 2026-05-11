# D.J. Live Test Result — "we love our home"

**Date:** Tue Apr 28, 2026 14:18 MST  
**Test Input:** "we love our home"  
**Status:** AWAITING WEBHOOK

---

## Evidence Required (Will Update on Webhook Arrival)

### 1. Webhook Timestamp
- Expected: When D.J. sends SMS
- Actual: [AWAITING]

### 2. Signature Verification
- Expected: ✅ PASS
- Actual: [AWAITING]
- Details: Ed25519, header: telnyx-signature-ed25519

### 3. Inbound SMS Parsed
- Phone: +16268313336
- Message: "we love our home"
- Lead: D.J. Test (DJ001)
- Expected: ✅ PARSED
- Actual: [AWAITING]

### 4. Signals Detected
- Expected: home_satisfaction (NOT buy)
- Buy signal: false
- Sell signal: false
- Refi signal: false
- Actual: [AWAITING]

### 5. Alert Level
- Expected: cold
- Actual: [AWAITING]

### 6. Tier 1 Alert Decision
- Expected: NO (home_satisfaction filtered)
- Actual: [AWAITING]

### 7. SMS Response
- Expected: YES
- Response text: "That's wonderful to hear. Are you mostly planning to stay put this year?"
- Actual: [AWAITING]

### 8. Telnyx Message ID
- Expected: Valid UUID
- Actual: [AWAITING]

### 9. Errors
- Expected: None
- Actual: [AWAITING]

### 10. Duplicate Sends
- Expected: None
- Actual: [AWAITING]

---

## Log Evidence (Will Be Populated)

### webhook_received
```
[AWAITING]
```

### webhook_signature_verified
```
[AWAITING]
```

### webhook_parsed_fields
```
[AWAITING]
```

### webhook_ldebrainv1_result
```
[AWAITING]
```

### inbound_sms
```
[AWAITING]
```

### tier1_alert_decision
```
[AWAITING]
```

### webhook_sms_sent
```
[AWAITING]
```

### webhook_handler_complete
```
[AWAITING]
```

---

## Pass/Fail Criteria

| Check | Expected | Result |
|---|---|---|
| Webhook received | ✅ YES | [AWAITING] |
| Signature verified | ✅ YES | [AWAITING] |
| home_satisfaction detected | ✅ YES | [AWAITING] |
| buy signal | ❌ NO | [AWAITING] |
| Tier 1 alert fired | ❌ NO | [AWAITING] |
| SMS response sent | ✅ YES | [AWAITING] |
| Response contains "wonderful" | ✅ YES | [AWAITING] |
| No duplicate sends | ✅ YES | [AWAITING] |
| No errors | ✅ YES | [AWAITING] |

---

**Status:** AWAITING WEBHOOK

Will update with exact evidence once D.J. sends test reply.
