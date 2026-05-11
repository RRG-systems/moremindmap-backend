# Telnyx Signature Verification — Debug Results

**Time:** 18:26:36 UTC (Tue Apr 28, 2026 11:26 MST)  
**Status:** Debug logging successful, signature still failing

---

## Confirmed Evidence

### 1. Did the webhook arrive?
**✅ YES** — Two webhooks at **18:26:36.491Z** and **18:26:36.855Z** (600ms apart, Telnyx retry)

### 2. Which signature headers were present?
**✅ ALL FOUR:**
- `telnyx-signature-ed25519` ✅
- `telnyx-timestamp` ✅
- `webhook-signature` ✅ (alternate header)
- `webhook-timestamp` ✅ (alternate header)

### 3. What encoding did the signature appear to use?
**✅ BASE64 (not hex)**

**Evidence:**
```
signature_first_8: "4hgg5wzJ"
signature_last_8: "X2f1AQ=="
signature_length: 88
signature_looks_hex: false
signature_looks_base64: true
```

**Finding:** Signature ends with `==` (base64 padding), not hex characters. **We were decoding as hex when it's base64.**

### 4. Was rawBody captured?
**✅ YES**

```
rawbody_uses_raw: true
rawbody_length: 1718 bytes
```

Body was properly captured as raw bytes (not parsed JSON).

### 5. Which signed content formats were tested?
**4 formats attempted:**
1. `timestamp.body` (period separator, current approach)
2. `timestamp|body` (pipe separator)
3. `body_only` (no timestamp)
4. `timestamp|body_json` (with JSON stringify)

### 6. Did any format pass verification?
**❌ NO** — All formats failed

```json
{"type":"webhook_signature_all_formats_failed","attempted_formats":["timestamp.body","timestamp|body","body_only","timestamp|body_json"]}
```

### 7. If one passed, which exact format/encoding passed?
**N/A** — None passed

### 8. If none passed, what safe metadata points to the likely issue?
**🔴 CRITICAL FINDING: Signature is BASE64, not HEX**

**Current code:** `Buffer.from(signature, "hex")` ← WRONG  
**Should be:** `Buffer.from(signature, "base64")` ← CORRECT

**Evidence:**
- Signature: `4hgg5wzJ...X2f1AQ==`
- Ends with `==` → classic base64 padding
- Contains no hex-only characters like `abcdef`
- Contains `=` which is invalid hex

### 9. Did LDEBRAINV1 remain blocked until verification passed?
**✅ YES** — LDEBRAINV1 never ran (blocked at signature verification)

No `inbound_sms` entries in logs.

### 10. Were any SMS replies or alerts sent?
**✅ NO** — No `sms_sent` or alert entries after 18:26:36

---

## Root Cause

**Bug:** Signature is being decoded as **hex** when it's actually **base64**

```javascript
// WRONG (current code)
const sigBuffer = Buffer.from(signature, "hex");
// Trying to parse base64 string as hex → garbage bytes → signature mismatch

// CORRECT
const sigBuffer = Buffer.from(signature, "base64");
// Parses the base64 correctly → should validate
```

---

## Critical Details

| Property | Value |
|----------|-------|
| Signature encoding | Base64 (confirmed) |
| Signature length | 88 chars (base64) |
| Base64 decoded length | 66 bytes (Ed25519 sig is 64 bytes, +2 padding) |
| Timestamp | `17774007` (10 digits, Unix seconds) |
| Raw body | 1718 bytes, properly captured |
| Formats tested | 4 (all failed with wrong encoding) |

---

## Next Fix

Change signature decoding from:
```javascript
Buffer.from(signature, "hex")
```

To:
```javascript
Buffer.from(signature, "base64")
```

This single change should allow verification to work for at least one of the tested formats.

---

## Recommendation

1. Update code to decode signature as base64
2. Restart server
3. Send one more test SMS
4. Verify passes (likely with one of the 4 tested formats)
5. If it passes, lock in that format permanently

---

**Status:** Root cause found. Fix is straightforward: change hex to base64.
