# MOREMINDMAP MINI PROFILE — AI UPGRADE FEASIBILITY REPORT

**Date:** Thu Apr 30, 2026 10:03 MST  
**Mission:** Inspect feasibility of OpenAI-powered interpretation + PDF generation + email delivery  
**Status:** FEASIBILITY ANALYSIS ONLY — No code changes made

---

## A. CURRENT DATA AVAILABLE AFTER SCORING

**Location:** Backend, after `scoreAssessment()` runs (scoreAssessment.js line ~70)

**Complete Data Package Ready for AI Consumption:**

```javascript
{
  // Normalized dimension scores (0-100%)
  normalizedScores: {
    velocity: 28.5,
    vector: 31.2,
    horizon: 15.3,
    leverage: 12.1,
    signal: 8.4,
    fidelity: 2.1,
    flex: 1.2,
    framework: 1.2
  },

  // Ranked dimensions (sorted by score, highest first)
  ranked: [
    { key: "vector", label: "Vector (Command)", percent: 31.2 },
    { key: "velocity", label: "Velocity (Tempo)", percent: 28.5 },
    { key: "horizon", label: "Horizon (Perspective)", percent: 15.3 },
    // ... 5 more
  ],

  // Primary drivers (top 2)
  primary: [
    { key: "vector", label: "Vector (Command)", percent: 31.2 },
    { key: "velocity", label: "Velocity (Tempo)", percent: 28.5 }
  ],

  // Secondary patterns (next 6)
  secondary: [
    { key: "horizon", label: "Horizon (Perspective)", percent: 15.3 },
    // ... more
  ],

  // Raw dimension scores (before normalization)
  rawScores: {
    velocity: 12,
    vector: 13,
    // ... all dimensions
  },

  // Written responses (if present, filtered for >10 chars)
  writtenResponses: [
    { questionId: 15, answer: "I tend to move fast..." },
    { questionId: 22, answer: "People tell me I..." }
  ],

  // Diagnostic flags
  diagnostics: {
    flatSpread: 30.0,           // spread between max and min score
    flatDistribution: false,    // true if spread < 12%
    weakWrittenCount: 0,        // number of written responses < 25 words
    contradictionScore: 0       // placeholder for future logic
  },

  invalid: false,               // true if assessment fails quality gates
  nextStep: "Proceed to OpenAI interpretation layer"
}
```

**User Metadata (from frontend, not in scoringPayload but available in req.body):**
- `answers` — raw 24 question responses
- User name and email (captured on intro screen)
- Promo/payment status (from Profile.jsx state)

**Total Available Context:**
✅ All 8 dimension scores (normalized + raw)  
✅ Primary and secondary patterns identified  
✅ Written responses (if any)  
✅ Diagnostics + quality flags  
✅ All 24 raw answers  
✅ User name/email  
✅ Payment status  

---

## B. RECOMMENDED AI INSERTION POINT

**Location:** `/server.js`, in `POST /api/moremindmap/mini-profile` endpoint

**Exact Flow:**

```javascript
// CURRENT FLOW:
1. receive { answers }
2. scoreAssessment() → scoringPayload
3. generateMiniProfile() → miniProfile (deterministic)
4. save submission
5. return response

// PROPOSED FLOW:
1. receive { answers } + user metadata
2. scoreAssessment() → scoringPayload
3. [NEW] Call OpenAI interpreter with scoringPayload + answers
4. [NEW] Get AI-generated miniProfile JSON
5. [FALLBACK] If OpenAI fails, use generateMiniProfile() (current deterministic)
6. save submission (now includes aiGenerated flag)
7. return response
```

**Insertion Code Pattern:**

```javascript
app.post("/api/moremindmap/mini-profile", async (req, res) => {
  try {
    const { answers } = req.body
    // ... validation ...

    // Score assessment
    const scoringPayload = scoreAssessment("set_1", responses)

    // [NEW] Generate AI interpretation
    let miniProfile
    let aiGenerated = false
    try {
      miniProfile = await generateAiMiniProfile(scoringPayload, answers)
      aiGenerated = true
    } catch (aiError) {
      console.warn("[AI FALLBACK]", aiError.message)
      // Fall back to deterministic generation
      miniProfile = generateMiniProfile(scoringPayload, writtenResponses)
    }

    // Save submission (with flag)
    await saveSubmission("moremindmap-mini-profile", {
      answers,
      scoringPayload,
      miniProfile,
      aiGenerated  // Track which method was used
    })

    // Return response
    res.json({ success: true, ... })
  } catch (error) { ... }
})
```

**Why This Location:**
- ✅ All data is ready and validated
- ✅ Before response sent to frontend
- ✅ Can fail gracefully with fallback
- ✅ Easy to track which profiles used AI vs deterministic
- ✅ All user metadata available in request scope

---

## C. RECOMMENDED OPENAI JSON STRUCTURE

**File:** `/engine/openAiMiniProfileInterpreter.js` (new file)

**Function:** `generateAiMiniProfile(scoringPayload, rawAnswers)`

**OpenAI Prompt Structure:**

```javascript
const systemPrompt = `You are the interpretation engine for MORE MindMap, 
a behavioral profiling system. You receive scored assessment data and produce 
a sharp, specific personality interpretation.

Return ONLY valid JSON. No markdown, no code fences.

Focus on:
- How this person actually moves through decisions and pressure
- Specific behavioral patterns (not generic archetypes)
- Real strengths and real costs (tradeoffs)
- What they should know about their operating style
- Practical implications for work/leadership
- One clear recommended next step

Be specific, sharp, and useful. Avoid corporate-speak.`

const userMessage = JSON.stringify({
  normalizedScores,    // All 8 dimensions with percentages
  ranked,              // Ranked by strength
  primary,             // Top 2
  secondary,           // Next 6
  rawAnswers,          // All 24 question responses
  writtenResponses     // Any written answers
})

// Then call OpenAI with specific JSON structure requirement
```

**Recommended JSON Output Structure:**

```json
{
  "executiveSummary": "1-2 paragraphs describing who this person is and how they operate",
  
  "operatingPattern": "How they typically move through situations — what's their default mode",
  
  "decisionPattern": "How they actually make decisions — speed, information gathering, confidence",
  
  "communicationStyle": "How they talk, write, listen — what's their natural mode",
  
  "underPressure": "How they behave when stakes are high, time is short, clarity is low",
  
  "blindSpots": "Areas where their strengths create predictable weaknesses",
  
  "frictionPoints": "Where they typically create friction with teams/systems/processes",
  
  "growthEdge": "One area of genuine growth potential (not a weakness, but a next level)",
  
  "recommendedNextStep": "One specific, actionable practice or shift to consider",
  
  "facilitatorNotes": "Notes for a coach/advisor on how to work with this person"
}
```

**Why This Structure:**
- ✅ Matches 5-page report layout (1 section per page + cover)
- ✅ Each section is 2-4 paragraphs of sharp content
- ✅ AI can generate independently without template dependency
- ✅ Frontend can render directly to MiniProfileReport
- ✅ Easy to compare AI vs deterministic output
- ✅ Facilitator notes useful for real coaching integration later

---

## D. RECOMMENDED PDF GENERATION METHOD

**Analysis of Current Stack & Options:**

### Option 1: Puppeteer (Recommended)
**Pros:**
- ✅ Industry standard for HTML → PDF
- ✅ Full browser rendering (CSS, layout perfect)
- ✅ Can render React output directly
- ✅ Headless Chrome under the hood (reliable)
- ✅ Easy error handling and fallbacks
- ✅ Handles complex layouts, fonts, styling

**Cons:**
- ❌ Memory intensive (launches headless Chrome)
- ❌ Slower than html-pdf (~5-15s per PDF)
- ❌ Requires Chrome/Chromium binary

**Cost:** Free  
**Install:** `npm install puppeteer`

### Option 2: React PDF (Not Recommended for this use case)
**Pros:**
- ✅ Lightweight
- ✅ React-native PDF generation
- ✅ No external binaries

**Cons:**
- ❌ Limited styling (no full CSS support)
- ❌ Doesn't render complex React components well
- ❌ Layout control is limited
- ❌ Not suitable for "professional 5-page report" goal

### Option 3: html-pdf (Not Recommended)
**Pros:**
- ✅ Lightweight
- ✅ Fast

**Cons:**
- ❌ PhantomJS no longer maintained
- ❌ CSS support is spotty
- ❌ Not suitable for complex layouts

### Option 4: Playwright (Also Viable)
**Pros:**
- ✅ Similar to Puppeteer (also Chromium-based)
- ✅ Cross-browser (Chrome, Firefox, Safari)
- ✅ Good for complex rendering

**Cons:**
- ❌ Slightly heavier than Puppeteer
- ❌ Overkill for this use case

---

### **RECOMMENDED: Puppeteer Server-Side Generation**

**Architecture:**

```javascript
// In POST /api/moremindmap/mini-profile endpoint:

// 1. Generate profile data (AI or fallback)
const miniProfile = await generateAiMiniProfile(...)

// 2. Generate PDF server-side
const pdfBuffer = await generateProfilePdf(
  miniProfile,
  userName,
  scoringPayload
)

// 3. Return PDF data OR store + email

```

**Implementation Pattern:**

```javascript
import puppeteer from 'puppeteer'

async function generateProfilePdf(miniProfile, userName, scoringPayload) {
  const browser = await puppeteer.launch({
    headless: true,
    args: ['--no-sandbox']  // For containerized environments
  })
  
  try {
    const page = await browser.newPage()
    
    // Generate HTML from miniProfile data
    const htmlContent = renderProfileHtml(miniProfile, userName, scoringPayload)
    
    // Set HTML content
    await page.setContent(htmlContent, { waitUntil: 'networkidle0' })
    
    // Generate PDF
    const pdf = await page.pdf({
      format: 'A4',
      margin: { top: '1cm', bottom: '1cm', left: '1cm', right: '1cm' },
      printBackground: true  // Include background colors
    })
    
    return pdf  // Buffer
  } finally {
    await browser.close()
  }
}
```

**Why Puppeteer Over Current Browser Print:**
- ✅ Automatic PDF generation (no user action needed)
- ✅ Consistent output (all users get same formatting)
- ✅ Can be emailed immediately
- ✅ Professional PDF (not screenshot quality)
- ✅ Solves "user must print to PDF" requirement

---

## E. RECOMMENDED EMAIL DELIVERY METHOD

**Analysis of Email Options:**

### Option 1: Resend (Recommended)
**Pros:**
- ✅ Modern, API-first email service
- ✅ Excellent for transactional emails
- ✅ PDF attachment support built-in
- ✅ Good deliverability
- ✅ Simple API
- ✅ Free tier available

**Cost:** Free up to 100/day; then $20/month for 10k/month  
**Install:** `npm install resend`  
**Setup:** Get API key from resend.com

### Option 2: SendGrid
**Pros:**
- ✅ Reliable, established
- ✅ Good for transactional
- ✅ Attachment support

**Cons:**
- ❌ More complex API
- ❌ Pricier ($20+ baseline)

### Option 3: Nodemailer + SMTP (Not Recommended)
**Pros:**
- ✅ No dependency (built-in Node)

**Cons:**
- ❌ Requires SMTP credentials (Gmail, Mailgun, etc.)
- ❌ Configuration more complex
- ❌ Deliverability less reliable

---

### **RECOMMENDED: Resend**

**Why:**
- ✅ API-first, simple to use
- ✅ Automatic attachment handling
- ✅ Excellent for transactional emails
- ✅ Good free tier
- ✅ Darren likely already familiar with modern tools

**Implementation Pattern:**

```javascript
import { Resend } from 'resend'

const resend = new Resend(process.env.RESEND_API_KEY)

async function emailProfile(clientEmail, darrenEmail, pdfBuffer, userName) {
  try {
    await resend.emails.send({
      from: process.env.FROM_EMAIL,  // e.g., "profiles@moremindmap.com"
      to: [clientEmail, darrenEmail],
      subject: `Your MORE MindMap Profile – ${userName}`,
      html: renderEmailHtml(userName),  // Nice HTML email body
      attachments: [
        {
          filename: `MindMap_${userName.replace(/\s/g, '_')}.pdf`,
          content: pdfBuffer
        }
      ]
    })
  } catch (error) {
    console.error("[EMAIL ERROR]", error)
    throw error
  }
}
```

---

## F. ENVIRONMENT VARIABLES REQUIRED

**To add to `/Users/rrg/moremindmap/.env`:**

```bash
# OpenAI (already exists, but verify)
OPENAI_API_KEY=sk-proj-...

# Resend Email
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=profiles@moremindmap.com

# Recipients
DARREN_EMAIL=darren@moremindmap.com

# PDF Options (optional)
PDF_DEBUG=false  # Set to true to save PDFs locally for testing
PDF_STORAGE_PATH=/tmp/moremindmap-pdfs

# Feature flags (optional)
SEND_EMAIL_ON_COMPLETION=true
USE_AI_INTERPRETATION=true
```

**Current .env Status:**
- ✅ OPENAI_API_KEY exists (verified)
- ❌ RESEND_API_KEY not present (needs to be added)
- ❌ FROM_EMAIL not present (needs to be added)
- ❌ DARREN_EMAIL not present (needs to be added)

---

## G. EXACT FILES TO CREATE/MODIFY

### **NEW FILES TO CREATE:**

| File | Purpose | Size | Complexity |
|------|---------|------|------------|
| `engine/openAiMiniProfileInterpreter.js` | OpenAI API integration | ~150 lines | Medium |
| `engine/pdfGenerator.js` | Puppeteer PDF generation | ~100 lines | Medium |
| `utils/emailService.js` | Resend email integration | ~80 lines | Low |
| `utils/htmlRenderer.js` | HTML template for PDF + email | ~200 lines | High |

### **FILES TO MODIFY:**

| File | Changes | Impact | Lines |
|------|---------|--------|-------|
| `server.js` | Insert AI call + PDF generation + email | Medium | +40-60 |
| `package.json` | Add dependencies (puppeteer, resend) | None | +2 |
| `.env` | Add 3 new environment variables | None | +3 |
| `.gitignore` | Ignore PDF temp files | None | +1 |

### **FILES TO REVIEW (No changes):**

- `src/Profile.jsx` — Frontend handles response same way
- `src/components/reports/MiniProfileReport.jsx` — Already renders miniProfile JSON
- `engine/miniProfileGenerator.js` — Kept as fallback

---

## H. DETAILED FILE MODIFICATION MAP

### **1. server.js**

**Location:** Line ~250 (inside `POST /api/moremindmap/mini-profile` endpoint)

**Change Type:** Insert AI generation layer

**Before:**
```javascript
// Generate mini profile with dominance model...
const miniProfile = generateMiniProfile(scoringPayload, writtenResponses)

// Save submission
await saveSubmission("moremindmap-mini-profile", {
  answers,
  scoringPayload,
  miniProfile,
})

// Return success
res.json({
  success: true,
  scoringPayload: { ... },
  miniProfile,
  timestamp: new Date().toISOString(),
})
```

**After:**
```javascript
// [NEW] Generate AI interpretation (with fallback)
let miniProfile
let aiGenerated = false
try {
  miniProfile = await generateAiMiniProfile(
    scoringPayload,
    answers,
    { name, email }  // user metadata
  )
  aiGenerated = true
  console.log("[AI] Profile generated successfully")
} catch (aiError) {
  console.warn("[AI FALLBACK]", aiError.message)
  miniProfile = generateMiniProfile(scoringPayload, writtenResponses)
}

// [NEW] Generate PDF
let pdfBuffer = null
try {
  pdfBuffer = await generateProfilePdf(miniProfile, name, scoringPayload)
  console.log("[PDF] Generated successfully")
} catch (pdfError) {
  console.warn("[PDF ERROR]", pdfError.message)
  // Continue without PDF — don't block response
}

// [NEW] Send email
if (pdfBuffer && email) {
  try {
    await emailProfilePdf(email, darrenEmail, pdfBuffer, name)
    console.log("[EMAIL] Sent to", email, darrenEmail)
  } catch (emailError) {
    console.error("[EMAIL ERROR]", emailError.message)
    // Log but don't throw — user still gets response
  }
}

// Save submission (with flags)
await saveSubmission("moremindmap-mini-profile", {
  answers,
  scoringPayload,
  miniProfile,
  aiGenerated,
  pdfGenerated: !!pdfBuffer,
  emailSent: !!pdfBuffer  // Only true if email attempted
})

// Return success
res.json({
  success: true,
  scoringPayload: { ... },
  miniProfile,
  timestamp: new Date().toISOString(),
  processing: {
    aiGenerated,
    pdfGenerated: !!pdfBuffer,
    emailSent: !!pdfBuffer
  }
})
```

**Imports needed at top of server.js:**
```javascript
import { generateAiMiniProfile } from './engine/openAiMiniProfileInterpreter.js'
import { generateProfilePdf } from './engine/pdfGenerator.js'
import { emailProfilePdf } from './utils/emailService.js'
```

### **2. package.json**

**Add to dependencies:**
```json
"puppeteer": "^22.0.0",
"resend": "^3.0.0"
```

### **3. .env**

**Add:**
```bash
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=profiles@moremindmap.com
DARREN_EMAIL=darren@example.com
```

---

## I. RISKS & MITIGATIONS

### Risk 1: OpenAI API Failures
**Risk:** OpenAI rate limits, downtime, or errors block profile generation  
**Probability:** Medium (production systems fail ~1-5% of time)  
**Impact:** User doesn't get profile  
**Mitigation:** ✅ Fallback to deterministic `generateMiniProfile()`  
**Recommendation:** Track failures in logs; alert Darren if >5% fail rate

### Risk 2: Puppeteer Memory/Performance
**Risk:** Puppeteer consumes significant server memory per PDF  
**Probability:** High if traffic increases  
**Impact:** Server slowdowns, crashes under load  
**Mitigation:** 
- ✅ Use async queue (process PDFs sequentially if needed)
- ✅ Set Puppeteer timeout (30s max)
- ✅ Monitor memory usage
- ✅ Consider background job queue (Bull, RabbitMQ) if >10 PDFs/min

### Risk 3: Email Delivery Failures
**Risk:** Resend API fails, email not sent, user doesn't know  
**Probability:** Low (~0.5% Resend uptime SLA 99.95%)  
**Impact:** User doesn't receive PDF  
**Mitigation:**
- ✅ Don't block response on email failure
- ✅ Log all failures
- ✅ Include email status in submission record
- ✅ Darren can manually send if needed

### Risk 4: PDF Rendering Quality
**Risk:** Complex CSS/layouts don't render correctly in Puppeteer  
**Probability:** Medium (CSS differences between browser and Puppeteer)  
**Impact:** PDF looks bad, unprofessional  
**Mitigation:**
- ✅ Test PDF rendering with sample profiles
- ✅ Use simple, conservative CSS
- ✅ Avoid browser-specific features
- ✅ Have fallback: send HTML version if PDF fails

### Risk 5: Costs Scaling Up
**Risk:** OpenAI and Resend costs accumulate  
**Probability:** Low if volume stays <100/day  
**Impact:** Unexpected billing  
**Mitigation:**
- ✅ Track API calls in logs
- ✅ Set rate limits per user/day
- ✅ Monitor costs weekly
- ✅ Add feature flags to disable if needed

### Risk 6: User Data in Prompts
**Risk:** Raw assessment answers sent to OpenAI (privacy concern)  
**Probability:** Expected but worth noting  
**Impact:** Data leaves your infrastructure  
**Mitigation:**
- ✅ Review OpenAI data retention policy (they don't store by default)
- ✅ Disclose to users in privacy policy
- ✅ Option: Use Azure OpenAI for on-prem alternative

---

## J. STEP-BY-STEP BUILD SEQUENCE

### **Phase 1: Setup & Dependencies (30 min)**
1. Add `puppeteer` and `resend` to package.json
2. Run `npm install`
3. Sign up for Resend account
4. Get Resend API key
5. Add RESEND_API_KEY, FROM_EMAIL, DARREN_EMAIL to .env
6. Test Resend connectivity

### **Phase 2: OpenAI Interpreter (45 min)**
1. Create `/engine/openAiMiniProfileInterpreter.js`
2. Write `generateAiMiniProfile()` function
3. Design OpenAI prompt
4. Test with sample scoring payloads
5. Verify JSON output structure
6. Add error handling + fallback logic

### **Phase 3: PDF Generation (45 min)**
1. Create `/engine/pdfGenerator.js`
2. Create `/utils/htmlRenderer.js` (HTML template)
3. Write `generateProfilePdf()` function
4. Test Puppeteer PDF generation
5. Verify PDF quality (fonts, layout, colors)
6. Add styling to match 5-page report design
7. Add error handling

### **Phase 4: Email Integration (30 min)**
1. Create `/utils/emailService.js`
2. Write `emailProfilePdf()` function
3. Design email HTML template
4. Test email delivery to test account
5. Test email attachments
6. Add error handling

### **Phase 5: Backend Integration (30 min)**
1. Modify `server.js` POST endpoint
2. Add imports
3. Insert AI + PDF + Email calls
4. Add feature flags (optional)
5. Add logging throughout

### **Phase 6: Testing (60 min)**
1. Complete assessment → verify profile generated
2. Check PDF output (visual inspection)
3. Check email delivery (both addresses)
4. Test OpenAI failure → verify fallback works
5. Test Puppeteer failure → verify email still sends or fails gracefully
6. Test email failure → verify response still returns to user
7. Load test (submit 5 profiles rapid-fire)

### **Phase 7: Deployment (15 min)**
1. Verify .env variables in production
2. Test in staging first
3. Deploy to Vercel
4. Verify Puppeteer works in serverless environment
5. Monitor for first 24h

### **Total Estimated Time: 4-5 hours**

---

## K. ALTERNATIVE ARCHITECTURES (Worth Considering)

### Alternative A: Background Job Queue
**If:** Volume becomes >50 profiles/day  
**Use:** Bull + Redis, or RabbitMQ  
**Benefit:** PDF generation doesn't block response  
**Tradeoff:** More complex, requires Redis

### Alternative B: Hybrid HTML + PDF
**If:** Want instant HTML preview + async PDF  
**Use:** Return HTML immediately, generate PDF in background  
**Benefit:** Faster response, better UX  
**Tradeoff:** More complex state management

### Alternative C: Third-Party PDF Service
**If:** Don't want to manage Puppeteer  
**Use:** Cloud-based PDF service (e.g., HTMLtoPDF API)  
**Benefit:** Simpler, offloads complexity  
**Tradeoff:** More expensive, less control

---

## L. PRODUCTION DEPLOYMENT CONSIDERATIONS

### Vercel Serverless Constraints
**Issue:** Puppeteer has size limits in serverless  
**Solutions:**
1. Use pre-built Chromium layers (`chromium-layer`)
2. Or use `puppeteer-extra-plugin-stealth` (lighter)
3. Or switch to Playwright server (less heavy)

**Recommended:** Use official Puppeteer Vercel integration if available

### Rate Limiting
**Recommendation:** Add to server.js
```javascript
// Limit to 100 profiles/day per user
const userCallCount = new Map()
```

### Monitoring
**Add CloudWatch/Datadog tracking for:**
- OpenAI API latency (target: <5s)
- PDF generation latency (target: <10s)
- Email delivery success rate (target: >99%)
- Error rates by type

---

## M. IMPLEMENTATION CHECKLIST

**Ready to code?** Use this checklist:

- [ ] Create `/engine/openAiMiniProfileInterpreter.js`
- [ ] Create `/engine/pdfGenerator.js`
- [ ] Create `/utils/htmlRenderer.js`
- [ ] Create `/utils/emailService.js`
- [ ] Modify `server.js` (add imports + endpoint logic)
- [ ] Update `package.json`
- [ ] Update `.env` template
- [ ] Test OpenAI integration
- [ ] Test PDF rendering
- [ ] Test email delivery
- [ ] Test fallback paths
- [ ] Load test (5+ concurrent requests)
- [ ] Deploy to staging
- [ ] Deploy to production
- [ ] Monitor first 24h

---

## FEASIBILITY VERDICT

### ✅ **HIGHLY FEASIBLE**

**Why:**
1. All data already available after scoring ✅
2. OpenAI library already installed ✅
3. Clean insertion point in backend ✅
4. Excellent fallback options ✅
5. Puppeteer mature and reliable ✅
6. Resend simple to integrate ✅
7. No breaking changes to existing code ✅
8. Frontend needs NO changes ✅

**Estimated Complexity:** Medium  
**Estimated Timeline:** 4-5 hours build + testing  
**Risk Level:** Low (all critical paths have fallbacks)  

**Go/No-Go:** ✅ **GO — Proceed to implementation**

---

**Report Completed:** Thu Apr 30, 2026 10:03 MST  
**Status:** FEASIBILITY CONFIRMED — Ready for build phase  
**Next Step:** Begin Phase 1 (dependencies)
