# MOREMindMap Source of Truth

## Canonical Git Root

The Git repository root is:

/Users/rrg/.openclaw/workspace

## Project Folder

The MOREMindMap backend project folder is currently:

moremindmap-backend/

This folder is not a nested Git repository. It does not have its own .git directory.

Therefore all Git-tracked MOREMindMap backend paths must be referenced from the Git root with:

moremindmap-backend/

Example:

moremindmap-backend/README_PROJECT_STATE.md

NOT:

README_PROJECT_STATE.md

## Canonical GitHub Remote

Expected remote:

https://github.com/RRG-systems/moremindmap-backend.git

## Required Startup Check

Before every session, run from the Git root:

pwd
git remote -v
git branch --show-current
git status --short
git log --oneline -5
ls -lh moremindmap-backend/README_PROJECT_STATE.md

## May 12, 2026 Travel Checkpoint — Local Engine Complete / Live Beta Wiring Next

**Current HEAD:** `5a66f7f`

**Status:** Local generation pipeline COMPLETE. Live website wiring NEXT.

### ✅ COMPLETED: Steps 1-6 Local Pipeline

**Step 1:** Visual V1 Locked
- All 10 pages accepted as V1
- Page 1: Profile Signature + YOUR PROFILE DNA decoder + Core Edge (LOCKED)
- Page 2: Behavioral Operating System Map with radial circles (LOCKED)
- No further visual redesign unless explicitly reopened

**Step 2:** AI Content Schema
- AI_CONTENT_SCHEMA_V1.md created (12K, 404 lines)
- 95 dynamic fields mapped across 10 pages

**Step 3:** Canonical Profile Input Pipeline
- PROFILE_INPUT_SCHEMA_V1.md created (16K, 301 lines)
- engine/buildProfileInput.js created (19K, 452 lines)
- examples/profile_input_example.json created
- 24-question set verified (Q2, Q6, Q10, Q15, Q20, Q24 = written)

**Step 4:** GPT-5.5 Report Generation Brain
- REPORT_CONTENT_SCHEMA_V1.md created (13K, 358 lines)
- engine/generateReportContent.js created (7.6K, 214 lines)
- prompts/moremindmapMiniV2Prompt.js created (2.7K, 86 lines)
- examples/report_content_example.json generated
- Mock mode functional (OPENAI_MODEL || "gpt-5.5")

**Step 5:** Quality Guardrails
- REPORT_QUALITY_GUARDRAILS_V1.md created (5.8K, 271 lines)
- engine/validateReportContent.js created (6.8K, 164 lines)
- examples/report_quality_report.json generated
- Quality score: 92/100, Genericity: 0.0

**Step 6:** Template Injection Engine
- engine/injectReportContent.js created (6.6K, 174 lines)
- generated/mini_v2_full_report.html generated
- generated/mini_v2_full_report_snapshot.json created
- 10 pages rendered, 95 fields injected, 0 placeholders, 100% coverage

### Current Pipeline Flow

```
Raw Assessment (24 Q + 6 written)
  ↓ buildProfileInput.js
profile_input.json (forensic intelligence)
  ↓ generateReportContent.js + GPT-5.5
report_content.json (95 AI fields)
  ↓ validateReportContent.js
quality report (anti-genericity)
  ↓ injectReportContent.js
generated/mini_v2_full_report.html
```

### ⚠️ IMPORTANT: Live Website NOT Assumed Wired

**DO NOT ASSUME:**
- FATHOMFREE currently triggers new 24-question flow
- Submit endpoint calls new pipeline
- Frontend renders 24 questions
- Backend generates populated 10-page output

**NEXT TASK: Live-Flow Audit**

### Travel Beta Goal (Controlled Beta, NOT Full Production)

**Goal during travel:**
```
FATHOMFREE code
  ↓
new 24-question Mini assessment
  ↓
submit
  ↓
backend pipeline (buildProfileInput → generateReportContent → inject)
  ↓
populated 10-page HTML or PDF
  ↓
Darren / Heather / Pam test and provide feedback
```

**Confidence Levels:**
- Controlled beta: 75-85%
- Full polished production while traveling: 45-60%

**If PDF annoying:** HTML report link acceptable for initial tester feedback.

### Next Steps (Mobile/Travel Context)

1. **Live-Flow Audit** (FIRST PRIORITY)
   - What does FATHOMFREE currently unlock?
   - Which question file does live Mini use?
   - Does frontend render new 24 questions?
   - What endpoint receives Mini submission?
   - Does that endpoint call new pipeline?
   - Where does output go? (HTML? Email? Download? Lost?)
   - Which repo/path is live frontend using?
   - What hosting environment serves backend?

2. **Wire Frontend to 24-Question Set**
   - Confirm questionMap.js loads in frontend
   - Confirm FATHOMFREE bypasses payment for Mini

3. **Wire Submit Endpoint to New Pipeline**
   - Connect submit → buildProfileInput → generateReportContent → inject

4. **Generate HTML Report After Submit**
   - Add Puppeteer PDF if feasible (optional for beta)

5. **Add Download/Email Delivery**

6. **Have Testers Run**
   - Darren, Heather, Pam
   - Inspect AI quality

7. **ONLY THEN:** Move toward Stripe/public production

### Files NOT To Touch During Travel

- ❌ Page 1 or Page 2 layout/geometry
- ❌ CSS redesign
- ❌ questionMap.js (24-question set locked)
- ❌ dimensionMap.js
- ❌ Scoring engine
- ❌ Visual template redesign

### Travel Operating Plan

**Context:** User traveling for son's college graduation in Colorado. Working remotely via Telegram.

**Priority:** Controlled beta wiring for tester feedback. NOT full production polish.

**Key Constraint:** Mobile/remote workflow. Minimize complex multi-file changes.
