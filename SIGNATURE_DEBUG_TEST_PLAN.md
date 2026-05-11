# Telnyx Signature Verification — Debug Test Plan

**Date:** Tue Apr 28, 2026 11:24 MST  
**Status:** Server restarted with comprehensive debug logging  

---

## What We're Testing

The signature mismatch suggests that either:
1. The signed content format is wrong (timestamp format, separator, body encoding)
2. The signature encoding is wrong (hex vs base64)
3. The raw body capture is wrong (modified JSON vs raw bytes)
4. We're using the wrong header (telnyx-signature-ed25519 vs webhook-signature)

---

## Debug Logging Added

When your next SMS arrives, the server will:

1. **Log which headers are present:**
   - `webhook_signature_headers_found` entry
   - Shows: has_telnyx_sig, has_webhook_sig, has_telnyx_ts, has_webhook_ts

2. **Log signature metadata:**
   - `webhook_signature_debug_precheck` entry
   - Shows:
     - First 8 and last 8 chars of signature (safe)
     - Signature length
     - Whether it looks like hex or base64
     - Timestamp first 8 chars and length
     - Raw body first 20 and last 20 chars (safe)
     - Whether we captured req.rawBody (YES/NO)

3. **Try multiple formats automatically:**
   - `timestamp.body` (current approach)
   - `timestamp|body` (pipe separator)
   - `body_only` (no timestamp prefix)
   - `timestamp|body_json` (with JSON stringify)

4. **Try both signature encodings:**
   - Hex first (current assumption)
   - Base64 fallback if hex fails

5. **Report which format worked:**
   - `webhook_signature_verified` entry (if any format passes)
   - Shows: format_used, signature_was_hex

---

## How to Interpret Results

### Best Case: 
```json
{"type":"webhook_signature_verified","format_used":"timestamp.body"}
```
→ Signature verified! End-to-end flow will proceed.

### If Different Format Works:
```json
{"type":"webhook_signature_verified","format_used":"timestamp|body"}
```
→ Update code to use that format permanently.

### If All Fail:
```json
{"type":"webhook_signature_all_formats_failed","attempted_formats":[...]}
```
→ Need to investigate further (check Telnyx docs, get raw webhook from ngrok API, etc.)

---

## Next Action

Send one SMS reply from your phone. Within 2-3 seconds:

1. Webhook arrives at server
2. Debug logs populate rrg-openai.log
3. We'll see which headers are present
4. We'll see signature metadata
5. We'll see which format (if any) validates

---

## Safety

- ✅ Verification remains ON (not bypassed)
- ✅ Comprehensive debug logging (safe metadata only)
- ✅ Multiple format trials (no false passes)
- ✅ Clear error logging if all fail
- ✅ No processing if verification fails

---

**Ready for your next SMS. Send when ready.**
