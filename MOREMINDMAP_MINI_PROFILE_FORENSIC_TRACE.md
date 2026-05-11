# MOREMINDMAP MINI PROFILE PIPELINE — FORENSIC TRACE
**Date:** Thu Apr 30, 2026 09:53 MST  
**Mission:** Trace current working pipeline from assessment completion → PDF output  
**Status:** INSPECTION ONLY — No modifications made

---

## A. PROJECT PATH

```
/Users/rrg/moremindmap/
├── src/
│   ├── App.jsx                          (Router, home page)
│   ├── Profile.jsx                      (24-question assessment UI)
│   ├── components/reports/
│   │   └── MiniProfileReport.jsx        (5-page report renderer)
│   └── lib/assessments/
│       └── moremindmap-questions.js     (Locked 24-question set)
├── engine/
│   ├── scoreAssessment.js               (Dimension scoring logic)
│   ├── miniProfileGenerator.js          (Profile assembly + content generation)
│   ├── writtenResponseInterpreter.js    (Phase 2A: written response analysis)
│   ├── dimensionMap.js                  (8 dimensions + labels)
│   └── [test files]
├── server.js                            (Express backend, API endpoints)
├── submissions/                         (JSON submission archival)
└── .env                                 (Environment config)
```

---

## B. CURRENT MINI PROFILE ROUTE

**Frontend Route:** `/profile`  
**Component:** `/src/Profile.jsx`

**Route Flow:**
1. User navigates to `/profile` → `Profile.jsx` mounts
2. IntroScreen displays (name, email, offer selection, promo validation)
3. Payment → Stripe checkout (if not FATHOMFREE promo)
4. Post-payment → redirects back to `/profile?success=true` (implicit)
5. User re-enters with assessment starting
6. QuestionScreen renders 24 questions sequentially
7. On final "Submit Assessment" button → `submitAssessment()` triggered

---

## C. ASSESSMENT SUBMISSION PIPELINE

### Frontend Submission Handler

**File:** `/src/Profile.jsx`  
**Function:** `submitAssessment()` (line ~142)

**Flow:**
```javascript
submitAssessment() {
  // 1. Transform frontend response format:
  //    { q1: "A", q2: "B", ... } 
  //    → passed as "answers" object
  
  // 2. POST to API endpoint:
  const API = import.meta.env.VITE_API_URL 
              || "https://moremindmap-backend.vercel.app"
  const endpoint = `${API}/api/moremindmap/mini-profile`
  
  // 3. Payload sent:
  //    { answers: { questionId: answer, ... } }
  
  // 4. Receives response:
  //    {
  //      success: true,
  //      scoringPayload: {...},
  //      miniProfile: {...},
  //      timestamp: "..."
  //    }
  
  // 5. Display result via MiniProfileReport component
}
```

**API URL Resolution:**
- Development: `http://localhost:4242` (if running locally)
- Production: `https://moremindmap-backend.vercel.app` (Vercel deployment)
- Environment Override: `VITE_API_URL` in `.env`

**Question Format:** 24 questions with IDs (1-24)  
**Answer Format:** Mixed (single-choice, multi-select, ranking, written)

---

## D. SCORING & PROFILE ASSEMBLY PIPELINE

### Backend Endpoint

**File:** `/server.js`  
**Endpoint:** `POST /api/moremindmap/mini-profile` (line ~235)

**Request Handler:**
```
1. Receive { answers } object
2. Validate: 24 answers required
3. Convert to scoring format:
   { questionId: int, type: string, answer: any }
4. Call scoreAssessment("set_1", responses)
5. Check for invalid flag (flat distribution, low signal)
6. Extract written responses (>10 char)
7. Call generateMiniProfile(scoringPayload, writtenResponses)
8. Save submission to /submissions/moremindmap-mini-profile_*.json
9. Return { success, scoringPayload, miniProfile, timestamp }
```

### Scoring Engine

**File:** `/engine/scoreAssessment.js`

**Logic:**
1. Loop through responses
2. Look up each question in `QUESTION_MAP`
3. Extract dimension scoring for that answer
4. Accumulate raw scores across 8 dimensions:
   - velocity (tempo/pace)
   - vector (command/direction)
   - horizon (perspective/vision)
   - leverage (influence/networks)
   - signal (relational awareness)
   - fidelity (precision/detail)
   - flex (adaptability)
   - framework (structure/process)

5. Normalize to percentages (0-100)
6. Rank dimensions by score
7. Detect diagnostic flags:
   - Flat distribution (spread < 12%) → invalid
   - Low written signal (weak written responses) → invalid
8. Return `scoringPayload`:
   ```
   {
     normalizedScores: { dimension: percent },
     ranked: [ { key, label, percent }, ... ],
     primary: [ top 2 dimensions ],
     secondary: [ next 2 dimensions ],
     diagnostics: { flags, flatness, signal },
     invalid: boolean
   }
   ```

### Profile Generator

**File:** `/engine/miniProfileGenerator.js`

**Function:** `generateMiniProfile(scoringPayload, writtenResponses)`

**Generates:**

1. **Dominance Structure**
   - Primary (top 2 dimensions)
   - Secondary (next 2)
   - Suppressed (bottom 4)

2. **Tradeoff Analysis**
   - For each dimension: advantages + costs
   - Draws from `DIMENSION_TRADEOFFS` lookup table

3. **Long-form Content Sections**
   - `what_this_means` — how to interpret the profile
   - `how_you_move` — operational behavior pattern
   - `communication_style` — how they communicate
   - `decision_pattern` — how they decide
   - `sales_behavior` — sales context interpretation
   - `leadership_snapshot` — leadership implications
   - `friction_pattern` — where they create friction
   - `recommended_next_step` — actionable insight

4. **Phase 2A: Written Response Interpretation**
   - Function: `interpretWrittenResponses(responses)`
   - Analyzes written answer content (if >10 chars)
   - Returns structured interpretation
   - Function: `generateInterpreterModifier(writtenInterpretation)`
   - Modifies primary profile based on written signals

5. **Returns miniProfile object**
   ```
   {
     primary_pattern: "string",
     secondary_pattern: "string",
     dominance_note: "string",
     dominance_structure: { primary, secondary, suppressed },
     what_this_means: "paragraph",
     how_you_move: "paragraph",
     communication_style: "paragraph",
     decision_pattern: "paragraph",
     sales_behavior: "paragraph",
     leadership_snapshot: "paragraph",
     friction_pattern: "paragraph",
     recommended_next_step: "paragraph",
     written_interpretation: { ... },      // Phase 2A
     interpreter_modifier: { ... }         // Phase 2A
   }
   ```

---

## E. OpenAI INTEGRATION

**Status:** ✅ **CURRENTLY NOT USED IN MINI PROFILE PIPELINE**

### Previous Integration (Deprecated)

**File:** `/server.js` line ~11  
**API Key:** `process.env.OPENAI_API_KEY`  
**Model:** `gpt-4o-mini`

**Endpoint:** `POST /api/interpret` (line ~85)  
**Status:** Exists but is **NOT called** by current Mini Profile flow

**Historic Flow (old code path):**
- Called OpenAI for interpretation (now replaced by hardcoded generator)
- Used prompt engineering to generate profile text
- Parsed JSON response

**Current Flow (Mini Profile):**
- NO OpenAI call
- All profile content hardcoded in `miniProfileGenerator.js`
- Deterministic content generation based on dimension scores

---

## F. PDF RENDERING PIPELINE

### Current Rendering

**File:** `/src/components/reports/MiniProfileReport.jsx`

**Rendering Method:** React component → HTML → Browser DOM

**Structure:** Fixed 5-page layout
```
PAGE 1: Cover page (name, date, primary/secondary patterns)
PAGE 2: Dimensions + dominance structure + summary
PAGE 3: Primary & secondary pattern cards
PAGE 4: How you operate (movement, communication, decisions)
PAGE 5: Real-world application (sales, leadership, friction, next steps)
[DEBUG PAGE: Full JSON payload (dev only)]
```

**CSS:** `/src/components/reports/MiniProfileReport.css`

**How User Receives PDF:**
1. Report renders in browser as full HTML page
2. User can:
   - Print to PDF using browser print dialog (Cmd+P)
   - Browser "Save as PDF" option
   - Screenshot

**PDF Generation Libraries:** ✅ **NONE CURRENTLY USED**
- jsPDF: NOT installed
- html2pdf: NOT installed
- puppeteer: NOT installed
- wkhtmltopdf: NOT installed

**Conclusion:** PDF is **browser-side only** → no automatic PDF download endpoint

---

## G. FORMSPREE INTEGRATION

**Status:** ✅ **NOT INVOLVED IN MINI PROFILE FLOW**

**Evidence:**
- No Formspree import in source files
- No Formspree references in server.js
- No Formspree config in .env

**Other Paths (Real Estate, Recovery):**
- Real Estate assessment may use Formspree (not traced)
- Mini Profile does NOT use Formspree

---

## H. EMAIL DELIVERY

**Status:** ✅ **NOT IMPLEMENTED**

**Evidence:**
- No nodemailer, SendGrid, or email library imports
- No email sending logic in server.js
- Email field captured in submission (for user reference)
- NO automatic email triggered on profile completion

**Current Email Handling:**
- User provides email on intro screen
- Email saved with submission JSON file
- NO transactional email sent

---

## I. SUBMISSION ARCHIVAL

**File Storage:** `/submissions/moremindmap-mini-profile_*.json`

**Filename Pattern:**
```
moremindmap-mini-profile_{sanitized_name}_{timestamp}.json
```

**Stored Data:**
```json
{
  "type": "moremindmap-mini-profile",
  "submittedAt": "ISO8601 timestamp",
  "answers": { q1: answer, q2: answer, ... },
  "scoringPayload": { dimensions, ranked, primary, secondary, diagnostics },
  "miniProfile": { full profile object },
}
```

**Storage Method:** Node.js `fs.writeFile()` to disk

---

## J. COMPLETION EVENT & DELIVERY

**Current Flow:**

```
1. User submits 24 answers
   ↓
2. Frontend calls /api/moremindmap/mini-profile POST
   ↓
3. Backend scores + generates profile
   ↓
4. Backend saves submission to /submissions/*.json
   ↓
5. Backend returns response with miniProfile
   ↓
6. Frontend receives response
   ↓
7. 2-second processing screen (visual delay)
   ↓
8. MiniProfileReport component renders as HTML in browser
   ↓
9. USER SEES: 5-page report in white container on black background
   ↓
10. USER OPTIONS:
    - Print to PDF (Cmd+P → Print to PDF)
    - Screenshot
    - Save as HTML (right-click)
    - View in browser
```

**No Automatic Download:** Report is NOT automatically downloaded as PDF  
**No Email Delivery:** User does NOT receive email  
**No Redirect:** User stays on report page

---

## K. EXACT FILES CONTROLLING EACH STEP

| Step | File | Function/Component | Key Logic |
|------|------|-------------------|-----------|
| 1. Display Assessment | `Profile.jsx` | `IntroScreen` | Form capture, offer selection |
| 2. Process Payment | `Profile.jsx` + `server.js` | `handleStartAssessment()` → Stripe session | Routes to Stripe OR skips to assessment if promo |
| 3. Display 24 Questions | `Profile.jsx` | `QuestionScreen` | Renders questions from `MOREMINDMAP_QUESTIONS` |
| 4. Collect Answers | `Profile.jsx` | `selectAnswer()` | Stores in `responses[questionId]` state |
| 5. Submit Answers | `Profile.jsx` | `submitAssessment()` | POST to `/api/moremindmap/mini-profile` |
| 6. Score Assessment | `server.js` + `scoreAssessment.js` | `POST /api/moremindmap/mini-profile` → `scoreAssessment()` | Dimension scoring, ranking, diagnostics |
| 7. Generate Profile | `server.js` + `miniProfileGenerator.js` | `generateMiniProfile()` | Dominance structure, tradeoffs, content |
| 8. Handle Written Responses | `miniProfileGenerator.js` + `writtenResponseInterpreter.js` | `interpretWrittenResponses()` | Phase 2A analysis |
| 9. Save Submission | `server.js` | `saveSubmission()` | Write to `/submissions/moremindmap-mini-profile_*.json` |
| 10. Return Response | `server.js` | POST response | `{ success, scoringPayload, miniProfile, timestamp }` |
| 11. Show Processing Screen | `Profile.jsx` | `ProcessingScreen` | 2-second delay with animated messages |
| 12. Render Report | `MiniProfileReport.jsx` | Component render | 5-page HTML structure with styling |
| 13. Display to User | Browser DOM | React renderer | HTML displayed in white container |
| 14. User Saves | Browser | Native print/save | User chooses: Print to PDF, screenshot, etc. |

---

## L. ENVIRONMENT CONFIGURATION

**File:** `/Users/rrg/moremindmap/.env`

**Key Variables:**
- `OPENAI_API_KEY` — (loaded but not used by mini profile pipeline)
- `STRIPE_SECRET_KEY` — For payment processing
- `SITE_URL` — Stripe redirect URL
- `VITE_API_URL` — Frontend API endpoint override

**Frontend Environment:** `import.meta.env.VITE_API_URL`  
**Backend Environment:** `process.env.*` (Node.js dotenv)

---

## M. CURRENT DATA FLOW VISUALIZATION

```
┌─────────────────────────────────────────────────────────────────┐
│                      USER BROWSER (Frontend)                    │
├─────────────────────────────────────────────────────────────────┤
│  Profile.jsx (React Component)                                  │
│  ├─ IntroScreen: Capture name, email, promo/offer              │
│  ├─ QuestionScreen: 24 questions from MOREMINDMAP_QUESTIONS    │
│  └─ submitAssessment(): POST /api/moremindmap/mini-profile     │
│                                                                 │
│  Response: { success, scoringPayload, miniProfile, timestamp } │
│  ├─ ProcessingScreen: 2-sec delay                              │
│  └─ MiniProfileReport: 5-page HTML report render               │
│                                                                 │
│  [User prints/screenshots/saves]                               │
└─────────────────────────────────────────────────────────────────┘
         ↓ POST /api/moremindmap/mini-profile ↑
         ↓ JSON: { answers }                   ↑
         ↓                                     ↑
┌─────────────────────────────────────────────────────────────────┐
│                   SERVER (Express.js)                           │
├─────────────────────────────────────────────────────────────────┤
│  server.js:PORT 4242                                            │
│  └─ POST /api/moremindmap/mini-profile                         │
│     ├─ Validate 24 answers                                     │
│     ├─ scoreAssessment.js: Score & rank dimensions             │
│     ├─ miniProfileGenerator.js: Generate long-form profile     │
│     ├─ writtenResponseInterpreter.js: Phase 2A (written resp)  │
│     ├─ saveSubmission(): Write to /submissions/*.json          │
│     └─ Return: { success, scoringPayload, miniProfile, ... }   │
└─────────────────────────────────────────────────────────────────┘
         ↑ Responses processed internally (no external calls)
         │
         ├─ dimensionMap.js: 8 dimensions + labels
         ├─ miniProfileGenerator.js: Hardcoded content templates
         └─ writtenResponseInterpreter.js: Deterministic parsing
```

---

## N. KEY INSIGHTS & CURRENT STATE

### What Works Now

✅ 24-question assessment collects answers  
✅ Stripe payment integration (promo FATHOMFREE bypasses checkout)  
✅ Scoring engine calculates dimension percentages  
✅ Mini profile generates 5-page HTML report  
✅ Submissions archived to disk  
✅ All content generated deterministically (no AI)  
✅ Written response analysis (Phase 2A) included  

### What Does NOT Happen

❌ No automatic PDF download  
❌ No email sent to user  
❌ No OpenAI call for mini profile generation  
❌ No Formspree integration  
❌ No database storage (file-based only)  
❌ No transactional email  
❌ No SMS notifications  

### Critical Control Points

1. **Assessment Logic:** 24-question set in `moremindmap-questions.js`
2. **Scoring Logic:** `scoreAssessment.js` + `dimensionMap.js`
3. **Profile Content:** `miniProfileGenerator.js` (hardcoded templates)
4. **Rendering:** `MiniProfileReport.jsx` + CSS
5. **API Endpoint:** `POST /api/moremindmap/mini-profile` in `server.js`
6. **Submission Storage:** `saveSubmission()` function in `server.js`

---

## O. PRODUCTION DEPLOYMENT

**Frontend:** Likely on Vercel (based on API URL fallback)  
**Backend:** Likely on Vercel (standard Node.js deployment)  
**Database:** None (file-based submissions only)  
**Payment:** Stripe live mode  
**Email:** None configured  

---

## INSPECTION SUMMARY

**Mission Complete:** ✅

The Mini Profile pipeline is fully traced:
- Assessment → Submission → Scoring → Profile Generation → HTML Rendering
- No OpenAI required for current pipeline
- No PDF library in use
- No email delivery
- All content deterministic and hardcoded
- Ready for inspection/redesign/optimization

**Blueprint:** Complete and forensically mapped. Proceed with redesign phase.

---

**Report Completed:** Thu Apr 30, 2026 09:53 MST  
**Inspection Status:** MAPPING COMPLETE — NO MODIFICATIONS MADE
