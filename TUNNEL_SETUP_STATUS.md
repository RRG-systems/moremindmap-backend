# Public Tunnel Setup Status

**Date:** Tue Apr 28, 2026 09:35 MST  
**Status:** Server running, tunnel pending ngrok auth  

---

## Current State

### ✅ Server Running

**Localhost:**
```
http://127.0.0.1:3000
```

**Startup verification:**
```
RRG Intent Engine running on http://127.0.0.1:3000
CSV: /Users/rrg/rrg/shannon_cooper_150.csv
Logging to: /Users/rrg/rrg/logs/rrg-openai.log
Telnyx SMS: ✓ Configured
Webhook Signature Verification: ✓ ON
LDEBRAINV1: ✓ Ready
Webhook endpoint: POST /webhook/telnyx
```

**Status:** ✅ RUNNING (process: neat-cove)

### ⏳ Public Tunnel (ngrok)

**Status:** NOT AUTHENTICATED YET

**Error:**
```
ERROR: authentication failed: Usage of ngrok requires a verified account and authtoken.
Sign up for an account: https://dashboard.ngrok.com/signup
Install your authtoken: https://dashboard.ngrok.com/get-started/your-authtoken
```

---

## Next Steps to Get Public URL

### Step 1: Create ngrok Account (Free)

Go to: https://dashboard.ngrok.com/signup

- Sign up with email or GitHub
- Verify email
- Create account

### Step 2: Get Auth Token

After signup, go to: https://dashboard.ngrok.com/get-started/your-authtoken

- Copy your personal auth token (looks like: `2_XXXX_XXXX...`)

### Step 3: Install Auth Token

Run (substitute YOUR_TOKEN):
```bash
ngrok config add-authtoken YOUR_TOKEN
```

### Step 4: Start Tunnel

Once auth token is installed:
```bash
ngrok http 3000
```

**Output will show:**
```
Forwarding                    https://xxx-yyy-zzz.ngrok.io -> http://127.0.0.1:3000
Web Interface                 http://127.0.0.1:4040
```

### Step 5: Public Webhook URL for Telnyx

**Format:**
```
https://xxx-yyy-zzz.ngrok.io/webhook/telnyx
```

Replace `xxx-yyy-zzz` with the subdomain from ngrok output.

---

## What We Have Ready

| Component | Status | Details |
|-----------|--------|---------|
| **Server** | ✅ Running | localhost:3000, signature verification ON |
| **LDEBRAINV1** | ✅ Ready | Processing messages, signal detection working |
| **Webhook endpoint** | ✅ Ready | POST /webhook/telnyx |
| **Signature verification** | ✅ Locked | Ed25519, TELNYX_PUBLIC_KEY loaded |
| **Env vars** | ✅ Set | TELNYX_API_KEY, PROFILE_ID, PUBLIC_KEY all present |
| **ngrok** | ✅ Installed | Waiting for auth token |
| **Public URL** | ⏳ Pending | After ngrok auth |

---

## Final Webhook URL (Template)

Once ngrok is authenticated and running, you'll get a URL like:

```
https://abc-123-def.ngrok.io/webhook/telnyx
```

**Paste this into Telnyx dashboard:**
- Go to Messaging → Profiles → Your Profile
- Webhook URL field: `https://abc-123-def.ngrok.io/webhook/telnyx`
- Method: POST
- Save

---

## No Live SMS Yet

⛔ Do not test sending SMS until:
1. ✅ ngrok tunnel is authenticated and running
2. ✅ Telnyx dashboard webhook URL is updated
3. ✅ You explicitly approve each test

Current safeguards:
- Server ready: ✅
- Signature verification: ✅ ON
- Logging: ✅ All webhooks logged
- SMS sending: Locked until approved

---

**Next action:** Provide ngrok auth token, configure tunnel, obtain public URL.
