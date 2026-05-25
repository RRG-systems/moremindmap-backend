# README_PROJECT_STATE.md — MORE MindMap May 2026 (CHECKPOINT)

**Last Checkpoint:** 2026-05-25 10:43 MST  
**Overall Status:** ✅ LIVE PIPELINE — Questions 25-28 Updated  

---

## What's Shipping Now

### 1. Profile Generation Pipeline ✅ (Scoring Verified)
- Assessment submission: HTTP 200 → job_id
- Async job polling: Real-time progress updates
- Canonical profile generation: Profile ID created with REAL dimension scores
- WebProfileReport rendering: 2-page behavioral profile with authentic scores
- Manual retrieval: Get profile by ID anytime (vault-backed)

**Live Test:** Profile MM-20260524-rf2xqct1 (2026-05-23 22:42 MST)  
**Verified:** Scores differentiate by assessment answers (not hardcoded 5s)

### 2. Report Structure ✅
**Page 1:**
- Profile DNA
- Executive Summary
- Behavioral Dimensions (with real dimension scores)
- Communication Style / Operating Pattern

**Page 2:**
- Hidden Contradictions
- System Under Strain
- Strategic Ceiling
- Coaching Leverage
- Recommended Next Step

**Footers:** Page markers + metadata tracking + V3 source

### 3. Data Persistence ✅
- Job storage: Redis (async job state with real profileInput)
- Profile vault: Redis (long-term retrieval with real scores)
- Scoring: Calculated by buildProfileInput, stored in profileInput.dimension_scores
- Fallback: Neutral 2.5 (not inflated 5) if missing

### 4. Scoring Integrity ✅ (JUST FIXED)
- Real dimension scores extracted from assessment answers
- buildProfileInput calculates scores; executeCanonicalGeneration uses them
- Profile differentiation preserved (no collapse to all 5s)
- Behavioral authenticity restored

---

## Current Phase: Visual Ascension Pass 2

**Status:** Ready to begin (no blockers)  
**What's done:**
- Two-page layout structure complete
- Section positioning defined
- Page breaks configured
- All 7 narrative sections working with real data

**What's pending:**
- Typography and styling
- Color hierarchy
- Visual hierarchy refinement
- Design review checkpoint

---

## Session Recovery Summary

| Issue | Caused By | Fixed By | Commit |
|-------|-----------|----------|--------|
| Vercel cold-start failure | Syntax errors in vault modules | Corrected object assignment + quotes | d06b88f |
| Profiles not retrievable | No vault save in canonical generation | Added dynamic vault save | 6e2b78e |
| Scores hardcoded to 5 | buildMinimalCanonical ignored profileInput | Extract real scores from profileInput | 116b4de |

**All fixed. No workarounds. Clean architecture.**

---

## Architecture Decisions (Locked)

### Profile Format: mm-YYYYMMDD-XXXXXXXX
- Lowercase standard (new profiles)
- Fallback support for MM-* legacy profiles
- Date-based organization
- Redis key: `vault:profile:{id}`

### Scoring Pipeline
```
Assessment answers → buildProfileInput.buildDimensionScores()
  ↓
Job.profileInput.dimension_scores (real values stored)
  ↓
executeCanonicalGeneration extracts scores
  ↓
canonical_profile.vector_scores (authentic, not hardcoded)
  ↓
WebProfileReport renders with real score context
```

### Canonical Structure (Verified)
```javascript
{
  profile_id: 'mm-YYYYMMDD-XXXXXXXX',
  metadata: {
    assessment_version: 'mini-v2',
    generated_at: ISO timestamp,
    job_id,
    generation_mode: 'emergency_inline'
  },
  vector_scores: { vector, signal, fidelity, velocity, leverage, flex, framework, horizon },
  ranked_dimensions: [ sorted by real score, not hardcoded ],
  narrative_profile: {
    profileDNA,
    executiveSummary,
    operatingPattern,
    decisionArchitecture,
    communicationStyle,
    systemUnderStrain,
    hiddenContradictions,
    strategicCeiling,
    coachingLeverage,
    recommendedNextStep
  },
  ... (30+ additional fields)
}
```

### Two Rendering Paths (NOW UNIFIED)
Before: Assessment path vs. Manual retrieval path (different)  
After: Both use WebProfileReport with real scores (same)

---

## Test Profiles (Both Verified Working)

| Profile | Type | Scores | Status |
|---------|------|--------|--------|
| MM-20260524-rf2xqct1 | Live assessment | Real (sanity fixed) | ✅ Verified |
| MM-20260523-mqlev9c9 | Fallback test | Flat (old fallback) | ✅ Verified |

Both retrieve and render correctly.

---

## Deployment Status

**Branch:** main  
**Latest commits:**
- ec3b959 (memory checkpoint)
- 116b4de (scoring sanity fix)
- a8e5884 (recovery timeline)
- 2f97e5a (docs preservation)
- 6e2b78e (vault integration)
- d06b88f (syntax fixes)

**All pushed to origin/main.**

---

## Frontend Integration Points

### Endpoints
- `POST /api/moremindmap/mini-profile-v2` - Submit assessment
- `GET /api/moremindmap/mini-profile-v2-status?job_id=X` - Poll status
- `GET /api/moremindmap/retrieve-profile?id=X` - Get profile
- `POST /api/moremindmap/narrative-v3` - Generate narrative via GPT

### Component: WebProfileReport
- Loads profile by ID (with real scores)
- Calls narrative-v3 for each section
- Renders 2-page layout
- Displays authentic dimension scores

### Flow
```
Assessment Form
  ↓
Submit → job_id
  ↓
Poll status (job_id)
  ↓ (when complete)
Load WebProfileReport (profile_id with real scores)
  ↓
Render 2-page report
```

---

## Support Notes

### If Profile Scores Look Wrong
- Check if using new profile ID (MM-20260524-rf2xqct1 or later)
- Old profile (MM-20260523-mqlev9c9) has flat scores (before fix)
- New profiles should show differentiated scores

### If Retrieval Fails
1. Verify profile ID format: mm-YYYYMMDD-XXXXXXXX
2. Check Redis: `KEYS vault:profile:*`
3. Manual key lookup: `GET vault:profile:{id}`

### If WebProfileReport Doesn't Render
1. Verify narrative-v3 endpoint is responsive
2. Check canonical_profile has all 7 narrative_profile fields
3. Verify profile_id matches expected format

---

## What NOT to Change

- ✅ DO NOT: Touch mini-v2 pipeline (working perfectly)
- ✅ DO NOT: Change narrative-v3 GPT integration (working)
- ✅ DO NOT: Modify WebProfileReport rendering (verified)
- ✅ DO NOT: Alter scoring logic (just fixed)
- ⏳ DO: Proceed with visual design refinement
- ⏳ DO: Monitor real score differentiation in next assessments

---

## Next Milestones

### Immediate (This Week)
- Visual design refinement (styling + typography)
- Design review checkpoint
- Implementation of approved designs

### Near-term (Next Week)
- Monitor real score quality
- Gather user feedback on authenticity
- Plan for future scoring refinements

### Future
- Historical profile comparison
- Advanced personalization
- Export/sharing features
- Integration pipelines

---

**Status:** Production live, scoring sanity verified, rollback-safe.  
**Next:** Visual Ascension Pass 2 (styling).  
**Blocked on:** Nothing.

---

For detailed technical info, see:
- SOURCE_OF_TRUTH.md — Infrastructure verification
- CURRENT_RECOVERY_STATE.md — Recovery timeline and decisions
- MINI_V2_VISUAL_GAP_REPORT.md — (Now outdated—scoring is fixed)
