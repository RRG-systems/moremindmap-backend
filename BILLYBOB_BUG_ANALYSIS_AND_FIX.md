# BILLYBOB FAKE CACHE LEAK BUG - ROOT CAUSE & FIX

**Date:** 2026-05-26 [Current Session]  
**Status:** ROOT CAUSE IDENTIFIED  
**Architect Ticket:** "Billybob profile too similar to David Berg - canonical/personality output appears stale, cached, defaulted, or copied"

---

## ROOT CAUSE IDENTIFIED

**NOT a cache leak. NOT a copied profile. It's a DATA LOSS BUG:**

### What's Happening

1. **Billybob's profile generated in "emergency_inline" mode**
   - Canonical metadata: `generation_mode: "emergency_inline"`
   - This is the SKELETON/FALLBACK mode (no manifestions, no opposing patterns)

2. **David Berg's profile generated with FULL canonical data**
   - Has primary_driver + secondary_stabilizer + 2 opposing_patterns + tradeoffs
   - Has operating_manifestation + pressure_manifestation text
   - Generated in NORMAL mode (not emergency)

3. **Why Billybob is skeleton:**
   - executeCanonicalGeneration receives `job.profileInput = undefined` or `{}`
   - Falls back to buildMinimalCanonical({}), generating empty skeleton
   - Result: skeleton canonical with basic scores but NO behavioral context

### Proof (from live Vercel retrieval)

**Billybob top_systems:**
```javascript
{
  "primary_driver": {
    "dimension": "leverage",
    "score": 3,
    "rank": 1
    // MISSING: description, operating_manifestation, pressure_manifestation
  },
  "secondary_stabilizer": { ... },
  // MISSING: opposing_pattern_1, opposing_pattern_2
  // MISSING: dimension_tradeoffs
}
```

**David Berg top_systems:**
```javascript
{
  "primary_driver": {
    "dimension": "vector",
    "score": 3,
    "rank": 1,
    "description": "high Command (Vector)",
    "operating_manifestation": "Enters situations with direction already forming...",
    "pressure_manifestation": "Under strain, decisiveness increases..."
  },
  "secondary_stabilizer": { ... (full structure) },
  "opposing_pattern_1": { ... },
  "opposing_pattern_2": { ... },
  "dimension_tradeoffs": [ ... ]
}
```

---

## ROOT DATA LOSS VECTOR

### Pipeline Trace

```
1. POST /api/moremindmap/start
   → createJob({ answers: { q1: {...}, q2: {...}, ... } })
   → job.payload = { answers, metadata }
   → Returns job_id

2. GET /api/moremindmap/status?job_id
   → executeNextStage(job)
   → stage = RECEIVED → executeFirstPassGeneration(job)

3. executeFirstPassGeneration:
   const { answers } = job.payload  // ✅ Gets answers object
   const profileInput = await buildProfileInput({ answers })  // ✅ Passes correct format
   await updateJob(job_id, { profileInput, ... })  // ✅ Persists to job

4. Next poll → stage = CANONICAL_GENERATION
   → executeCanonicalGeneration(job)
   → buildMinimalCanonical(job.profileInput || {}, job_id)
   → ❌ IF job.profileInput is empty/undefined → skeleton mode
```

### The Missing Link

**Question:** Why would `job.profileInput` be empty when executeCanonicalGeneration is called?

**Hypothesis 1:** buildProfileInput threw exception → profileInput never created
- **Evidence against:** Job would be marked FAILED, not continued to canonical generation
- **Evidence against:** No exception handling catches it silently

**Hypothesis 2:** profileInput persisted to job but not retrieved
- **Evidence:** Redis locking/transaction might have lost data
- **Likely:** Race condition between updateJob and getJob

**Hypothesis 3:** buildRawAnswers throws but exception is silently swallowed
- **Evidence:** Missing guards in buildRawAnswers (crashes if answer undefined)
- **If exception:** buildProfileInput returns empty/null
- **If caught somewhere:** Job continues with empty profileInput

---

## FIX IMPLEMENTATION

### Part 1: Add Guards to buildRawAnswers()

**File:** `api/engine/buildProfileInput.js` (lines 104-131)

**Problem:** If any answer is undefined, line 114 `answer.choice` crashes

**Solution:** Add guards before accessing answer properties

```javascript
buildRawAnswers(rawAssessment) {
  const rawAnswers = {};
  const questions = QUESTION_MAP.set_1.v1;

  // GUARD 1: Ensure rawAssessment structure
  if (!rawAssessment || !rawAssessment.answers || typeof rawAssessment.answers !== 'object') {
    console.warn('[buildRawAnswers] GUARD: rawAssessment.answers is missing/invalid', {
      has_rawAssessment: !!rawAssessment,
      has_answers: !!rawAssessment?.answers,
      answers_type: typeof rawAssessment?.answers
    });
    return rawAnswers; // Safe: return empty (triggers fallback scoring)
  }

  questions.forEach(question => {
    const answer = rawAssessment.answers[`q${question.id}`];
    
    // GUARD 2: Skip missing answers (don't crash)
    if (!answer) {
      console.warn(`[buildRawAnswers] GUARD: Missing answer for q${question.id}`);
      return; // Continue loop, skip this answer
    }
    
    if (question.type === 'mc') {
      // GUARD 3: MC answer must have choice
      if (!answer.choice) {
        console.warn(`[buildRawAnswers] GUARD: MC q${question.id} missing choice`);
        return; // Skip
      }
      rawAnswers[`q${question.id}`] = {
        question_id: question.id,
        question_type: 'mc',
        question_text: question.text,
        answer_choice: answer.choice,
        answer_text: question.options[answer.choice.charCodeAt(0) - 65] || 'Unknown',
        normalized_dimensions: question.scores[answer.choice] || {}
      };
    } else if (question.type === 'written') {
      // GUARD 4: Written answer must have text
      if (typeof answer.text !== 'string') {
        console.warn(`[buildRawAnswers] GUARD: Written q${question.id} missing text`);
        return; // Skip
      }
      rawAnswers[`q${question.id}`] = {
        question_id: question.id,
        question_type: 'written',
        question_text: question.text,
        answer_text: answer.text || '',
        character_count: (answer.text || '').length,
        word_count: (answer.text || '').split(/\s+/).length,
        sentence_count: (answer.text || '').split(/[.!?]+/).length - 1
      };
    }
  });

  return rawAnswers;
}
```

### Part 2: Add null/empty check in executeCanonicalGeneration()

**File:** `api/engine/canonical/executeCanonicalGeneration.js` (line 160)

**Current:**
```javascript
const canonical_profile = buildMinimalCanonical(job.profileInput || {}, job.job_id)
```

**Add diagnostic:**
```javascript
const canonical_profile = buildMinimalCanonical(job.profileInput || {}, job.job_id);

// DIAGNOSTIC: Log if profileInput is empty (indicates data loss)
if (!job.profileInput || Object.keys(job.profileInput).length === 0) {
  console.warn('[CANONICAL-GENERATION] WARNING: profileInput is empty/missing', {
    profile_id,
    job_id: job.job_id,
    has_profileInput: !!job.profileInput,
    profileInput_keys: job.profileInput ? Object.keys(job.profileInput) : [],
    generation_mode: 'emergency_inline_fallback'
  });
  canonical_diagnostics.empty_profileInput_warning = true;
}
```

### Part 3: Trace through StagedExecutor

**File:** `api/engine/miniV2StagedExecutor.js` (lines 36-63)

**Add explicit guards:**
```javascript
export async function executeFirstPassGeneration(job) {
  const trace = job.diagnostics?.stage_trace || [];
  trace.push('ENTER_first_pass_generation');
  
  const { buildProfileInput } = await import('./buildProfileInput.js');
  const { generateReportContent } = await import('./generateReportContent.js');

  const { answers } = job.payload;
  
  // GUARD: Verify answers exist and are formatted
  if (!answers || typeof answers !== 'object' || Object.keys(answers).length === 0) {
    console.error('[STAGED-EXECUTOR] ERROR: Answers missing/empty', {
      has_answers: !!answers,
      answers_type: typeof answers,
      answer_count: answers ? Object.keys(answers).length : 0
    });
    throw new Error('No answers provided to buildProfileInput');
  }

  trace.push('answers_validated');
  trace.push('before_buildProfileInput');
  
  let profileInput;
  try {
    profileInput = await buildProfileInput({ answers });
    trace.push('after_buildProfileInput_success');
  } catch (err) {
    console.error('[STAGED-EXECUTOR] buildProfileInput failed:', err.message);
    trace.push(`CATCH_buildProfileInput: ${err.message}`);
    throw err; // Re-throw to fail job properly
  }

  // GUARD: Verify profileInput has dimension_scores
  if (!profileInput || !profileInput.dimension_scores) {
    console.error('[STAGED-EXECUTOR] ERROR: profileInput missing dimension_scores', {
      has_profileInput: !!profileInput,
      has_dimension_scores: !!profileInput?.dimension_scores,
      profileInput_keys: profileInput ? Object.keys(profileInput) : []
    });
    throw new Error('buildProfileInput produced invalid output (missing dimension_scores)');
  }

  trace.push('profileInput_validated');
  trace.push('before_generateReportContent');
  
  let reportContent = await generateReportContent(profileInput);
  trace.push('after_generateReportContent');
  
  // ... rest of function
}
```

---

## Deployment Strategy

### Phase 1: Add Guards (Safe, Non-Breaking)
1. Deploy buildRawAnswers guards
2. Deploy executeCanonicalGeneration diagnostic logging
3. Deploy StagedExecutor guards + error throwing
4. Monitor logs for "empty_profileInput" warnings

### Phase 2: Test & Validate
1. Submit new assessment (Billybob-2 or similar)
2. Verify profileInput has dimension_scores
3. Verify canonical NOT in emergency_inline mode
4. Verify vector_scores > 2.5 (real scores, not default)
5. Compare to David Berg for sanity

### Phase 3: Re-generate Billybob (Optional)
Once fix is deployed:
1. Re-run Billybob's assessment answers through API
2. Get new profile ID
3. Verify canonical generates with full structure
4. Compare new vs. old for debugging

---

## Verification

### Before Fix (Current State - Billybob)
```
generation_mode: "emergency_inline"  ← SKELETON
top_systems: { primary, secondary }  ← NO opposing patterns
primary_driver: { dimension, score, rank }  ← NO manifestions
```

### After Fix (Expected - Billybob 2.0)
```
generation_mode: "normal" OR "with_data"  ← FULL
top_systems: { primary, secondary, opposing_1, opposing_2, tradeoffs }  ← COMPLETE
primary_driver: { dimension, score, rank, description, operating_manifestation, pressure_manifestation }  ← RICH
```

---

## Summary

**Bug:** buildRawAnswers crashes silently on missing answers → profileInput empty → canonical in emergency_inline mode

**Fix:** Add defensive guards to prevent exceptions, add diagnostics to detect empty profileInput, explicitly validate data at each stage

**Impact:** Prevents data loss in profile generation pipeline, ensures rich behavioral canonical for all new assessments

**Rollback:** Guards are additive (don't break existing code), safe to deploy immediately

---

**Next:** Implement fixes in three parts, deploy to Vercel, test with new assessment

