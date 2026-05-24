# MINI_V2_VISUAL_GAP_REPORT.md — Dimension Scoring Issue

**Report Date:** 2026-05-23 22:42 MST  
**Status:** Known issue, non-blocking, deferred  
**Impact:** Scoring quality (not infrastructure)  

---

## The Issue

All dimension scores are suspiciously flat and high:

```javascript
vector_scores: {
  vector: 5,
  signal: 5,
  fidelity: 5,
  velocity: 5,
  leverage: 5,
  flex: 5,
  framework: 5,
  horizon: 8
}
```

**Expected:** Varied scores across 1-10 scale (or 1-8)  
**Actual:** All 5, except horizon at 8  
**Result:** No profile differentiation

---

## Why This Happened

**executeCanonicalGeneration** uses emergency fallback canonical:

```javascript
function buildMinimalCanonical(profileInput, jobId) {
  return {
    vector_scores: {
      vector: 5, signal: 5, fidelity: 5, velocity: 5,
      leverage: 5, flex: 5, framework: 5, horizon: 8
    },
    // ... rest of structure
  }
}
```

This is intentional—emergency mode prioritizes **pipeline viability** over **scoring accuracy**.

---

## Why It's Not Blocking

1. **Infrastructure works end-to-end** ✅
   - Profiles generate successfully
   - Retrieval works
   - Rendering works

2. **All narrative sections populate** ✅
   - profileDNA, executiveSummary, etc.
   - Users see complete reports
   - No missing fields

3. **Separate from visual design** ✅
   - Layout and styling work independently
   - Dimension scores don't affect page structure
   - Visual checkpoint can proceed

4. **Acceptable for demo phase** ✅
   - Users can see full report structure
   - Feedback gathering works
   - Scoring refinement is next iteration

---

## What Needs to Fix This

### Phase 1: Understand Current Scoring
- [ ] Review how dimension scores were originally calculated
- [ ] Find the canonical scoring logic (before fallback)
- [ ] Document the scoring algorithm

### Phase 2: Implement Real Scoring
- [ ] Restore dimension calculation from assessment answers
- [ ] Implement trait propagation logic
- [ ] Add anti-repetition scoring constraints
- [ ] Test differentiation across profiles

### Phase 3: Validate
- [ ] Run multiple assessments
- [ ] Verify varied scores across profiles
- [ ] Check score distribution
- [ ] Confirm narrative depth matches scores

---

## Current Fallback Text (Also Placeholder)

All narrative sections use emergency fallback:

```javascript
narrative_profile: {
  profileDNA: 'Emergency inline profile',
  executiveSummary: 'Assessment processed',
  operatingPattern: 'Standard',
  decisionArchitecture: 'Moderate',
  communicationStyle: 'Direct',
  systemUnderStrain: 'Adaptive',
  hiddenContradictions: 'None identified',
  strategicCeiling: 'Unknown',
  coachingLeverage: 'Development focus needed',
  recommendedNextStep: 'Next phase evaluation'
}
```

**When this gets better:** Phase 2 (Narrative Enrichment) after visual checkpoint

---

## Deferral Rationale

### Why Not Fix Now?
1. Scoring logic is complex and separate from rendering
2. Requires deep understanding of original algorithm
3. Risk of breaking working pipeline
4. Lower priority than visual design checkpoint

### Why Defer?
1. Visual design is blocking user experience
2. Scoring refinement doesn't help demo phase
3. Infrastructure is proven solid—focus on UX next
4. Scoring can be incremental improvement

### Go/No-Go for Demo?
**YES, proceed with visual checkpoint.**
- Pipeline works ✅
- Users see full reports ✅
- Scoring is known placeholder ✅
- Won't impact design feedback ✅

---

## Future Work (After Visual Checkpoint)

1. **Scoring Refinement Phase**
   - Restore real dimension calculation
   - Implement evidence-based scoring
   - Add trait propagation

2. **Narrative Enrichment Phase**
   - Replace placeholder text
   - Add personalization from answers
   - Implement anti-repetition rules

3. **Quality Validation**
   - Profile differentiation testing
   - Score accuracy benchmarking
   - Narrative specificity scoring

---

## Files to Review (For Future Scoring Work)

- `api/engine/canonical/canonicalProfileGenerator.js` — Original logic (before fallback)
- `api/engine/canonical/inferBehavioralPatterns.js` — Pattern recognition
- `api/engine/canonical/inferContradictions.js` — Contradiction detection
- `api/engine/canonical/inferEvidenceMap.js` — Evidence aggregation
- `src/lib/buildNarrativeV3.js` — Frontend narrative builder (if present)

---

## Monitoring

**What to watch:**
- User feedback on profile relevance
- Whether flat scores cause confusion
- Profile differentiation complaints

**Signals to act on:**
- If users say "all profiles look the same"
- If feedback is "too generic"
- If visual design is complete and scoring remains issue

---

## Summary

| Aspect | Status | Timing |
|--------|--------|--------|
| Infrastructure | ✅ Live | Now |
| Rendering | ✅ Working | Now |
| Layout | ✅ Complete (Pass 1) | Now |
| Styling | 🔵 In progress | Visual checkpoint |
| Scoring | 🟡 Fallback placeholder | After visual checkpoint |
| Narratives | 🟡 Fallback placeholder | After visual checkpoint |

**Proceed with confidence.** Visual design can move forward independently.

---

**Issue logged:** MINI_V2_VISUAL_GAP_REPORT.md  
**Priority:** P3 (non-blocking)  
**Assigned to:** Scoring refinement phase  
**Unblocks:** Visual design checkpoint ✅
