# PUPPETEER DEPLOYMENT ASSESSMENT

**Date:** Thu Apr 30, 2026 10:29 MST  
**Assessment:** Deployment target verification before Puppeteer install  
**Status:** ASSESSMENT COMPLETE

---

## DEPLOYMENT TARGET ANALYSIS

### Evidence Found

**1. Production URL (.env.production)**
```
VITE_API_URL=https://moremindmap-backend.vercel.app
```
✅ **Confirms:** Backend deployed on Vercel

**2. Server Configuration (server.js)**
```javascript
app.listen(4242, () => console.log("Server running on port 4242"))
```
✅ **Traditional Node.js:** `app.listen()` on fixed port (not serverless functions)

**3. Git Remote**
```
https://github.com/RRG-systems/moremindmap.git
```
✅ Public GitHub repo (standard for Vercel deployments)

**4. Stack**
- Express.js (traditional HTTP server)
- Vite (frontend build)
- Stripe (payment)
- OpenAI (API calls)
- No serverless function markers

---

## DEPLOYMENT MODEL IDENTIFIED

### ✅ **VERCEL WITH PERSISTENT NODE SERVER**

**Configuration:**
- Frontend: Vercel static hosting (Next.js style)
- Backend: Vercel Node.js runtime (long-running server, not functions)
- Port: 4242 (fixed)
- Runtime: 24/7 server process

**Evidence:**
- `app.listen()` on port (not AWS Lambda/Vercel Functions)
- Fixed port binding (typical for Vercel servers)
- Traditional Express.js pattern (not serverless)
- `.env.production` references persistent backend URL

---

## PUPPETEER DECISION MATRIX

| Scenario | Solution | Choice |
|----------|----------|--------|
| Pure Vercel Functions | puppeteer-core + @sparticuz/chromium | ❌ Not this case |
| Persistent Node on Vercel | Vanilla puppeteer | ✅ **THIS CASE** |
| Self-hosted Node | Vanilla puppeteer | Alternative |
| Railway/Render/Fly | Vanilla puppeteer | Alternative |

---

## RECOMMENDED APPROACH

### ✅ **Vanilla Puppeteer is Safe**

**Why:**
1. **Persistent process:** Vercel allows long-running Node.js servers
2. **Sufficient memory:** Standard Vercel tier has enough for Puppeteer + Chromium
3. **Cold start not an issue:** Server stays warm 24/7
4. **Simpler codebase:** No need for puppeteer-core workarounds
5. **Chromium included:** Puppeteer bundles Chromium (works on Vercel)

**Risk:** Low
- Vercel supports vanilla Puppeteer on Node.js runtime
- Default Chromium works in Vercel environment
- No special configuration needed

### ⚠️ **Potential Caveat**

If Vercel tier has memory constraints (<512MB), Puppeteer may struggle. But typical Vercel Pro tier has sufficient resources.

**Mitigation:** 
- Start with vanilla Puppeteer
- Monitor memory usage first week
- If issues arise, switch to puppeteer-core + @sparticuz/chromium

---

## PHASE 1 INSTALL PLAN

### Install Both Packages

```bash
npm install puppeteer resend
```

**Packages to install:**
- `puppeteer@22.0.0` ← Full Puppeteer (Chromium bundled)
- `resend@3.0.0` ← Email service

**Do NOT install:**
- ❌ puppeteer-core (not needed for persistent Node)
- ❌ @sparticuz/chromium (serverless workaround, not needed)

---

## VERCEL-SPECIFIC CONFIGURATION

### Optional: vercel.json for Optimization

Create `/Users/rrg/moremindmap/vercel.json`:

```json
{
  "builds": [
    {
      "src": "server.js",
      "use": "@vercel/node",
      "config": {
        "includeFiles": "engine/**",
        "maxDuration": 60
      }
    }
  ],
  "routes": [
    {
      "src": "/(.*)",
      "dest": "server.js"
    }
  ]
}
```

**Explanation:**
- `maxDuration: 60` ← Allows up to 60s for PDF generation (Puppeteer can take 10-15s)
- `includeFiles` ← Ensures engine/ directory deployed
- `@vercel/node` ← Explicitly uses Node.js runtime

**Is this required?** No, but recommended for production to avoid timeouts.

---

## IMPLEMENTATION PLAN

### Step 1: Install Dependencies (Now)
```bash
cd /Users/rrg/moremindmap
npm install puppeteer@22.0.0 resend@3.0.0
```

**Expected:** Both install successfully without conflicts

### Step 2: Verify Installation
```bash
npm list puppeteer resend
```

**Expected output:**
```
moremindmap@0.0.0
├── puppeteer@22.0.0
├── resend@3.0.0
└── ... other deps
```

### Step 3: No Code Changes Yet
- ✅ Dependencies added
- ❌ Don't modify server.js
- ❌ Don't create engine files
- ⏸ Wait for report back

### Step 4: Optional (After Phase 1 validation)
- Create `vercel.json` for production safety
- Update `.gitignore` to exclude Chromium cache

---

## .GITIGNORE RECOMMENDATION

Add to `.moremindmap/.gitignore` (after Puppeteer install):

```
# Puppeteer
.puppeteer/
node_modules/.cache/
chromium-*
```

---

## DEPLOYMENT READINESS MATRIX

| Item | Status | Impact |
|------|--------|--------|
| Target identified | ✅ Vercel persistent Node | Low risk |
| Puppeteer choice | ✅ Vanilla Puppeteer | Low risk |
| Memory adequacy | ⚠️ Likely sufficient | Monitor |
| Timeout concerns | ⚠️ May need vercel.json | Mitigation ready |
| Dependencies | ✅ Ready to install | No blockers |

---

## READY TO PROCEED?

✅ **YES — Phase 1 Install Ready**

**Command:**
```bash
npm install puppeteer@22.0.0 resend@3.0.0
```

**After install:**
1. Run: `npm list puppeteer resend`
2. Report back status
3. Await Phase 2 (engine files) authorization

---

## POST-INSTALL CHECKLIST

- [ ] npm install puppeteer@22.0.0 resend@3.0.0
- [ ] npm list (verify both packages installed)
- [ ] Check package.json (both deps added)
- [ ] Check package-lock.json (updated)
- [ ] No git conflicts
- [ ] Ready for Phase 2

---

## DEPLOYMENT NOTES FOR VERCEL

**When deploying to production:**

1. **Environment variables in Vercel dashboard:**
   - OPENAI_API_KEY (already set)
   - STRIPE_SECRET_KEY (already set)
   - SITE_URL (already set)
   - Add Phase 4: RESEND_API_KEY, FROM_EMAIL, DARREN_EMAIL

2. **Vercel.json (recommended):**
   - Create after Phase 1 validation
   - Set maxDuration to 60s (for Puppeteer PDF generation)

3. **First deployment:**
   - Monitor logs for Puppeteer startup
   - Check memory usage (should be <400MB)
   - Validate PDF generation works

---

## VERDICT

✅ **Vanilla Puppeteer is the correct choice for this deployment**

- Vercel persistent Node runtime supports it
- No serverless workarounds needed
- Standard installation process applies
- Deployment risk: Low

---

**Assessment Completed:** Thu Apr 30, 2026 10:29 MST  
**Recommendation:** Proceed with vanilla Puppeteer + Resend install  
**Next Step:** Execute Phase 1 install, report back
