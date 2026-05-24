# Smoke Test: V3 Narrative Rendering (2026-05-23 21:00 MST)

## Test Objective
Verify end-to-end assessment flow and V3 narrative section rendering in production.

## Test Environment
- URL: https://moremindmap.com
- Date: 2026-05-23 21:00 MST
- Commits: 4938ebc (cache invalidation), 74e358b (diagnostics), 202f566 (cache unwrap)

## Test Steps

### Step 1: Submit New Assessment
- Go to https://moremindmap.com
- Click "Start Here" → "Build Your MORE MindMap Profile"
- Fill organizational context (company name, role, etc.)
- Fill contextual signals
- Answer all 28 questions from the intake form
- Enter test name and email
- Submit assessment

**Verify:**
- ✅ Assessment submits without error
- ✅ New profile ID is generated (format: MM-YYYYMMDD-RANDOMPART or mm-YYYYMMDD-RANDOMPART)
- ✅ Profile ID is displayed on success page
- ✅ No console errors during submission

### Step 2: Store Profile ID
- **CRITICAL:** Save the profile ID generated (will use to verify persistence)
- Example format: `MM-20260523-abc123` or `mm-20260523-xyz789`

### Step 3: Navigate to Profile Retrieval
- Click "View Profile" button on success page OR
- Go back to home page → "Build Your MORE MindMap Profile" → Scroll to "Enter Profile ID"
- Enter the profile ID from Step 2

**Verify:**
- ✅ Profile is retrieved successfully
- ✅ No 404 or retrieval errors

### Step 4: Verify Web Profile Render
- Once profile loads, verify the header renders correctly
- Check: Person name, Profile ID box, DNA signature

**Verify:**
- ✅ Header renders
- ✅ Profile ID box shows the ID from Step 2
- ✅ DNA signature shows (first 4 dimensions)

### Step 5: Check All 7 V3 Narrative Sections
Scroll through and verify each section has CONTENT (not blank):

1. **Profile DNA**
   - Should have operating model description (~100 words)
   - Check: NOT blank, has text like "Moves with directional conviction"

2. **Executive Summary**
   - Should have compressed briefing (~150 words)
   - Check: NOT blank, short sentences, concrete observation

3. **Communication Style**
   - Should have team experience description (~250 words)
   - Check: NOT blank, meeting behavior details

4. **Hidden Contradictions**
   - Should have 3 contradictions (~220 words total)
   - Check: NOT blank, each contradiction named and grounded

5. **Strategic Ceiling**
   - Should have 1x/2x/5x/10x analysis (~200 words)
   - Check: NOT blank, scaling states described

6. **Coaching Leverage**
   - Should have 3-4 numbered tactics (~200 words)
   - Check: NOT blank, numbered list format

7. **Recommended Next Step**
   - Should have specific action/audit (~150 words)
   - Check: NOT blank, testable/measurable

**Critical Verify for Each:**
- ✅ Section title visible
- ✅ Body text present (not "(placeholder)" or empty)
- ✅ Text is readable and substantial (>50 chars)
- ✅ No "[Scenario would be injected]" stubs showing

### Step 6: Check Footer Metadata
Scroll to bottom of profile, check footer shows:
```
Assessment Date: 2026-05-23
Profile Type: Behavioral Profile
Confidence: High
V3 Source: [gpt55 or fallback_local]
Fallback: [true or false]
```

**Verify:**
- ✅ V3 Source is NOT "unknown"
- ✅ Source is either "gpt55" or "fallback_local"
- ✅ If fallback_local, all sections still have content
- ✅ Fallback is false (preferred) or true with full content (acceptable)

### Step 7: Check Browser Console
Open DevTools (F12 → Console):

**Look for these diagnostic logs:**
```
[V3 RENDER COMPLETE]
[V3 CACHE HIT] or [V3 CACHE MISS]
[WebProfileReport] V3 narrative rendered for...
```

**NOT looking for:**
- ❌ Errors about narrative.coachingLeverage undefined
- ❌ 404 on /api/moremindmap/narrative-v3
- ❌ "Missing required fields" in NARRATIVE-V3 logs
- ❌ Red error messages

**Acceptable:**
- Warnings about optional features
- "fallback_local" render source (as long as content renders)
- Cache miss on first load

### Step 8: Verify No Fatal Errors
- ✅ No unhandled JavaScript errors in console
- ✅ Page is fully interactive
- ✅ No broken layouts or missing sections
- ✅ Text is readable (not cut off or hidden)

## Success Criteria

### Must-Haves (Blocking)
1. ✅ Assessment submits successfully
2. ✅ Profile ID generated
3. ✅ Profile retrieves by ID
4. ✅ All 7 sections have visible content
5. ✅ No blank sections (coachingLeverage and recommendedNextStep must have text)
6. ✅ No fatal console errors
7. ✅ V3 Source is not "unknown"

### Should-Haves (Quality)
1. V3 Source is "gpt55" (not fallback_local) - indicates GPT rendering
2. Fallback: false (preferred, but fallback_local is acceptable if content renders)
3. All sections feel coherent and context-aware
4. Text reads naturally (no obvious placeholders)

### Nice-to-Haves
1. Generation time < 5 seconds
2. No cache hits on first assessment (fresh build)
3. Consistent styling across all sections

## Failure Criteria

STOP if you encounter:
- ❌ Assessment submission fails
- ❌ Profile ID not generated
- ❌ Profile retrieval returns 404
- ❌ Any section is completely blank (e.g., coachingLeverage shows nothing)
- ❌ JavaScript error in console preventing interaction
- ❌ V3 Source is "unknown" AND sections are blank

## Expected Output

After successful test, document:
- **Test Status:** PASS / FAIL
- **Profile ID Generated:** [exact ID]
- **Sections Populated:** 7/7
- **V3 Source:** [gpt55 or fallback_local]
- **Fallback Used:** [true/false]
- **Console Errors:** [none / description]
- **Notes:** [any observations]

## Test Execution

**Tester:** Rocky (automated)
**Date:** 2026-05-23 21:00 MST
**Duration:** ~5 minutes per test

---

## NEXT ACTION

Once this test passes, ready for:
1. User demos (visual ascension)
2. Performance optimization (if needed)
3. Production monitoring setup
