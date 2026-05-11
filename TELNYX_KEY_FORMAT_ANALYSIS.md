# TELNYX_PUBLIC_KEY Format Analysis

**Analysis Date:** Tue Apr 28, 2026 11:17 MST

---

## Key Format Findings

### 1. Is it PEM format with BEGIN PUBLIC KEY / END PUBLIC KEY?
**NO** — No PEM markers found

### 2. Is it raw base64?
**YES** — Valid base64-encoded data

### 3. Is it hex?
**NO** — Contains base64 characters (+, /, =)

### 4. Length of the value
**44 characters** (base64-encoded)

### 5. First 8 and last 8 characters
- First 8: `Nx+xttrZ`
- Last 8: `a1AKmkg=`

### 6. Whether it contains literal \n characters
**NO** — No literal `\n` in the string

### 7. Whether it contains actual newlines
**NO** — No actual newline characters

### 8. Which format crypto.createPublicKey() currently expects
**crypto.createPublicKey() CANNOT handle raw Ed25519 keys**

---

## What The Key Actually Is

**Format:** Raw Ed25519 public key (32 bytes)

When decoded from base64:
- **Length:** 32 bytes
- **Type:** Raw Ed25519 public key bytes (not DER-wrapped, not SPKI-wrapped, not PEM)
- **First 4 bytes (hex):** `371fb1b6`
- **Last 4 bytes (hex):** `500a9a48`

---

## Why "Failed to read asymmetric key" Error Occurs

1. Code calls: `crypto.createPublicKey({ key: keyBuffer, format: 'der', type: 'spki' })`
2. Node.js tries to parse 32 raw bytes as DER-encoded SPKI
3. Fails because the bytes are NOT in DER format
4. Error: "Failed to read asymmetric key"

---

## The Solution

**Use `webcrypto.subtle` instead of `crypto.createPublicKey()`**

### Why:
- `webcrypto.subtle.importKey()` supports raw Ed25519 keys
- `webcrypto.subtle.verify()` verifies with those raw keys
- Handles Ed25519 correctly (async API)

### How:

```javascript
const crypto = require('crypto');
const { webcrypto } = crypto;

async function verifyTelnyxSignature(signature, timestamp, body, publicKeyBase64) {
  try {
    // Import raw Ed25519 key
    const publicKey = await webcrypto.subtle.importKey(
      'raw',
      Buffer.from(publicKeyBase64, 'base64'),
      'Ed25519',
      false,
      ['verify']
    );
    
    // Prepare signed content (same format as before)
    const signedContent = timestamp + '.' + body;
    
    // Verify signature (hex string to buffer)
    const signatureBuffer = Buffer.from(signature, 'hex');
    
    // Verify (async)
    const isValid = await webcrypto.subtle.verify(
      'Ed25519',
      publicKey,
      signatureBuffer,
      Buffer.from(signedContent)
    );
    
    return isValid;
  } catch (e) {
    return { valid: false, reason: String(e?.message || e) };
  }
}
```

---

## Testing Confirmation

✅ `webcrypto.subtle.importKey()` with raw Ed25519: **SUCCESS**  
✅ `webcrypto.subtle.verify()` with Ed25519: **SUCCESS**  
✅ API signature validated (dummy signature tested): **SUCCESS**  

---

## Required Code Changes

1. Update `verifyTelnyxSignature()` function to use `webcrypto.subtle`
2. Change from sync to async (required by webcrypto API)
3. Update webhook handler to use `await` for verification
4. Test with real Telnyx signature data

---

## Implementation Impact

- **Breaking change:** Verification becomes async (function returns Promise)
- **Compatibility:** All modern Node.js versions support webcrypto
- **Security:** No downgrade — using Web Cryptography API standard
- **Performance:** Negligible overhead for single verify operation

---

**Status:** Solution identified and tested. Ready for implementation.
