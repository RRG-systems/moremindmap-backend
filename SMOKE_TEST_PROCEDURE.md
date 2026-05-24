# Smoke Test Procedure: V3 Narrative Rendering (Manual)

## Overview
This is a manual browser-based smoke test to verify the full assessment → V3 narrative pipeline works end-to-end in production.

## Test Flow

### Phase 1: Submit Assessment (with FATHOMFREE promo for async pipeline)

**URL:** https://moremindmap.com/profile

**Steps:**
1. Click "Build Your MORE MindMap Profile"
2. In Intro Screen:
   - Enter Name: `Test User 2026-05-23`
   - Enter Email: `test+$(date +%s)@moremindmap.com` (or similar)
   - **CRITICAL:** Enter Promo Code: `FATHOMFREE`
   - Click "Validate Code"
   - Should show "Code validated" (or similar confirmation)
3. Click "Start Assessment"
4. Fill Page 0A (Organizational Context):
   - Company: `Test Corp`
   - Department: Select any option
   - Role Title: `Test Role`
   - Reports To: `Test Manager`
   - Industry: Select any
   - Click "Continue"
5. Fill Page 0B (Contextual Signals):
   - Answer 3-4 multi-select signals
   - Click "Continue"
6. Answer all 28 assessment questions (q1-q28):
   - Any reasonable answers work (A-E multiple choice)
   - Continue through all questions
7. Click "Submit Assessment"

**Verify at submission:**
- ✅ No JavaScript errors in console
- ✅ "Processing" screen shows
- ✅ "Building your MORE MindMap profile..." message displays

### Phase 2: Async Job Execution (Polling)

**What's happening:**
- Backend is generating canonical profile in background
- Frontend is polling `/api/moremindmap/status?job_id={jobId}` every 3 seconds
- Process: answer normalization → canonical generation → narrative rendering → HTML injection

**Expected Timeline:**
- First 2-3 polls: "Queued" or "Processing"
- Polls 3-6: "Canonical generation" or similar
- Polls 6-8: "Rendering profile" or "Building narrative"
- Poll 9-10: "Complete"

**Total time:** 3-6 minutes typical

**Verify during polling:**
- ✅ No timeout errors
- ✅ Job status updates in console (if dev tools open)
- ✅ Page doesn't freeze

### Phase 3: Profile Renders

**What you should see:**
- Mini V2 Beta report container appears
- "10-Page Behavioral Profile Report" header
- Report content (10 pages of HTML)

**CRITICAL CHECK:** Does the report have a profile ID visible?

**Look for:**
- Somewhere in the report or nearby, should see format: `mm-20260523-XXXXXXXX` or `MM-20260523-XXXXXXXX`
- May be in header, footer, or success message
- **SAVE THIS PROFILE ID** — you'll need it for Phase 4

### Phase 4: Verify Canonical Saved to Vault

From the generated profile ID (e.g., `mm-20260523-abc123`):

1. Go back to home page: https://moremindmap.com
2. Go to "Build Your MORE MindMap Profile"
3. Scroll to "Enter Profile ID" section at bottom
4. Paste the profile ID from Phase 3
5. Click "Enter Profile ID"

**Verify:**
- ✅ Profile loads successfully (no 404)
- ✅ Page shows retrieved profile report

### Phase 5: Verify V3 Narrative Rendering

Once profile is retrieved/displayed:

1. Click "Enter Profile ID" again to load as Web Profile (premium display)
   - OR look for "View Full Profile" or similar button
   - Goal: Get to the dark-theme WebProfileReport with all 7 sections

2. **Scroll through and verify all 7 V3 sections have CONTENT:**

   a) **Profile DNA**
      - Should have: "Operating Model: Moves with..." (or similar)
      - Word count: ~100 words
      - NOT blank

   b) **Executive Summary**
      - Should have: Short sentences, concrete observations
      - Word count: ~150 words
      - NOT blank

   c) **Communication Style**
      - Should have: Team experience description
      - Example phrases: "Meeting pace", "Silent processing", "Some stop speaking"
      - Word count: ~250 words
      - NOT blank

   d) **Hidden Contradictions**
      - Should have: 3 named contradictions
      - Examples: "Self-Model vs Reality", "Strategy vs Execution"
      - Word count: ~220 words total
      - NOT blank

   e) **Strategic Ceiling**
      - Should have: 1x/2x/5x/10x scale analysis
      - Examples: "Optimized", "Coordination gaps", "Personal execution impossible"
      - Word count: ~200 words
      - NOT blank

   f) **Coaching Leverage**
      - Should have: Numbered list (3-4 items)
      - Examples: "Pace as signal", "Process friction is intelligence"
      - Format: `1. [tactic]: [description]`
      - Word count: ~200 words
      - NOT blank

   g) **Recommended Next Step**
      - Should have: Specific action/audit
      - Examples: "Conduct a 'decision velocity audit'..."
      - Word count: ~150 words
      - NOT blank

3. **Check footer:**
   - Scroll to bottom
   - Look for metadata:
     ```
     Assessment Date: 2026-05-23
     Profile Type: Behavioral Profile
     Confidence: High
     V3 Source: [gpt55 or fallback_local]
     Fallback: [true or false]
     ```
   - ✅ V3 Source is NOT "unknown"
   - ✅ All 7 sections have `.body` content (non-empty)

### Phase 6: Check Browser Console

Open DevTools (F12):

**Look for these patterns:**
- `[V3 RENDER COMPLETE]` — should show all sections rendered
- `[WebProfileReport] V3 narrative rendered` — confirming React component ran
- No red error messages

**Should NOT see:**
- `narrative.coachingLeverage undefined`
- `Cannot read property 'body' of undefined`
- 404 errors on `/api/moremindmap/narrative-v3`
- "Missing required fields"

## Success Criteria

### Must-Haves (BLOCKING)

All of these must pass:

1. ✅ Assessment submits without error
2. ✅ Polling starts and completes (no timeout)
3. ✅ Mini V2 report displays with HTML content
4. ✅ **Profile ID generated and visible** (format: `mm-YYYYMMDD-XXXXXXXX`)
5. ✅ Profile retrieves successfully by ID
6. ✅ Web profile renders (dark theme, all sections visible)
7. ✅ All 7 V3 sections have visible, non-empty `.body` text
8. ✅ Coaching Leverage section has numbered list
9. ✅ Recommended Next Step section has actionable recommendation
10. ✅ V3 Source is NOT "unknown"
11. ✅ No fatal console errors (red errors blocking interaction)

### Should-Haves (QUALITY)

Nice-to-haves if time permits:

- V3 Source is "gpt55" (not fallback_local) — means GPT rendering was used
- Fallback: false (preferred)
- Generation time < 6 minutes
- All sections read naturally (no placeholders like `[...]`)
- Text is coherent across all sections

### Failure Criteria

STOP immediately if:

- ❌ Assessment submission fails or times out
- ❌ Polling never completes (stuck on "Processing" after 10+ minutes)
- ❌ No profile ID is generated or not visible
- ❌ Profile retrieval returns 404 or "not found"
- ❌ Any section is completely blank (e.g., coachingLeverage shows nothing)
- ❌ Fatal JavaScript error in console preventing navigation
- ❌ V3 Source shows "unknown" AND sections are blank

## Recording Results

After test completes, capture:

**Test Status:** PASS or FAIL

**If PASS:**
```
Profile ID Generated: [exact ID from test, e.g., mm-20260523-abc123]
Sections Populated: 7/7
V3 Source: [gpt55 or fallback_local]
Fallback Used: [true or false]
Generation Time: [minutes:seconds]
Console Errors: None
Notes: [any observations]
```

**If FAIL:**
```
Failure Point: [step where test stopped]
Error: [exact error message or description]
Profile ID Generated: [yes/no, if available]
Sections with Content: [which ones are blank]
Console Errors: [key errors preventing test]
Screenshots: [recommended]
Notes: [what went wrong]
```

## Next Steps

### If PASS:
- ✅ System is production-ready
- Ready for user demos (visual ascension)
- Schedule: User testing → Iterate → Production monitoring

### If FAIL:
- 🔧 Debug based on failure point
- Check logs: `/api/moremindmap/status?job_id={jobId}` for errors
- Check browser console for detailed error traces
- If canonical generation failed: check `/api/engine/canonical/*` logs
- If V3 rendering failed: check `/api/moremindmap/narrative-v3` logs and check for API key
- Fix and re-run smoke test

---

## Test Execution Log

**Test Date:** 2026-05-23 21:00 MST
**Tester:** [Your Name]
**Result:** [PASS / FAIL]
**Profile ID:** [if successful]
**Notes:** [any additional notes]

