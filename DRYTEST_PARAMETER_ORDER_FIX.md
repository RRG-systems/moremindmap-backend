# Dry Test — Parameter Order Fix

**Problem found:** Test was calling processInboundSMS with parameters in wrong order.

**Function signature:**
```javascript
async processInboundSMS(phone, inboundText, leadRecord)
```

**Test was calling:**
```javascript
brain.processInboundSMS(test.input, '+16268313336', 'DJ001', 'D.J. Test')
//                      ^ input     ^ phone        ^ leadId  ^ leadName (extra)
```

**Should call:**
```javascript
brain.processInboundSMS('+16268313336', test.input, { lead_id: 'DJ001', lead_name: 'D.J. Test' })
//                      ^ phone        ^ input     ^ leadRecord object
```

**Fix applied:** Updated dry-test-all-scenarios-fixed.js with correct parameter order.
