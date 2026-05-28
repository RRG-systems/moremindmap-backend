# SOURCE_OF_TRUTH.md — Project State (2026-05-28 23:24 MST)

**Last Updated:** 2026-05-28 23:24 MST  
**Session Focus:** GPT Cognition Bridge Implementation & Deployment Trace  
**Build Status:** ✅ PASSING (488ms)  
**Production Status:** ⏳ AWAITING DEPLOYMENT  

---

## CURRENT ARCHITECTURE

### Three-Layer Rescoring (Doctrine-Based)

```
Layer 1: Baseline Scores (Q1-Q28)
  ↓ [IMMUTABLE, SACRED]
Layer 2: Deterministic Rescoring (rescoring_v1)
  └─ Threshold gravity, compensatory suppression, flatness preservation
  ↓ [ALWAYS AVAILABLE]
Layer 3: GPT Behavioral Cognition (rescoring_gpt)
  └─ Psychological interpretation of patterns
  ↓ [OPTIONAL, DOWNSTREAM ONLY]
Renderer: Fallback chain (GPT → V1 → baseline)
```

### What's Working ✅

**Baseline Scoring:**
- ✅ Q1-Q28 assessment generation
- ✅ ranked_dimensions creation
- ✅ Baseline immutable (sacred)

**Deterministic Rescoring (V2):**
- ✅ rescoreDimensions engine (V2 with threshold gravity)
- ✅ dominance_profile generation
- ✅ render_ready calculation
- ✅ All downstream, baseline untouched

**GPT Behavioral Cognition Layer:**
- ✅ gptBehavioralRescore engine (450 lines)
- ✅ Reads full canonical context
- ✅ Applies behavioral psychology
- ✅ Validates GPT output
- ✅ Stores in canonical.rescoring_gpt

**Integration Points:**
- ✅ canonicalProfileGenerator triggers rescoring (V1 then GPT)
- ✅ getCognitionContext extracts best layer
- ✅ buildNarrativeV3 uses cognition context for profileDNA
- ✅ WebProfileReport has fallback chain

**Admin Infrastructure:**
- ✅ POST /api/admin/rescore-profile endpoint built
- ✅ Backfill support for old profiles
- ✅ Non-destructive (only updates rescoring fields)
- ✅ Idempotent (safe to call multiple times)

---

## CURRENT UNRESOLVED STATE

### Deployment Not Live

**Commits Exist, Not Deployed:**
- e5b7637: Admin endpoint generates rescoring_v1 for old profiles
- 670a795: Fix rescoreDimensions import (named export)
- 38362fd: DNA Summary reads correct canonical path
- 836fcde: All rescoring_gpt reads use correct path
- 95f7767: Documentation complete

**Proof:**
- Source: WebProfileReport.jsx has `canonicalProfile` extraction (8x)
- Production bundle: Does NOT contain `canonicalProfile`
- Admin endpoint: Still fails with FUNCTION_INVOCATION_FAILED

### Why DNA Summary Still Shows Fallback

**Root Cause Chain:**
1. Admin endpoint not deployed → rescoring_gpt never created
2. Renderer not deployed → can't read correct canonical path anyway
3. Result: Falls back to hardcoded "Balanced multi-system topology..."

**For David:**
```
Current state:
- rescoring_gpt = null (never created)
- DNA Summary reads canonical?.rescoring_gpt (wrong path in old code)
- renderReady = {} (empty)
- Falls back to hardcoded string

After deployment:
- Admin rescore creates rescoring_gpt ✅
- Renderer reads canonical.canonical_profile_json.rescoring_gpt ✅
- renderReady = { profile_intensity: 'extreme' } ✅
- Shows: "Concentrated directional topology..." ✅
```

---

## DOCTRINE MAINTAINED

✅ Baseline never modified (sacred, immutable)  
✅ Deterministic layer always available (V1 independent of GPT)  
✅ All intelligence downstream (no core scoring changes)  
✅ Ingress unchanged (FATHOMFREE, Profile ID flow identical)  
✅ Orchestration preserved (canonical generation structure same)  
✅ Fallback chains complete (3-level, any layer can fail)  
✅ No breaking changes (all additive)  
✅ Reversible (env flags control execution)  

---

## CRITICAL COMMITS (This Extended Session)

| Commit | What | Layer | Status |
|--------|------|-------|--------|
| 2b3f415 | GPT rescoring engine (450 lines) | Layer 3 | ✅ Built |
| 504fd0d | Integration + docs | Layer 3 | ✅ Built |
| c90fd5c | Flag enabled in production | Layer 3 | ✅ Committed |
| c22933d | Admin endpoint complete | Infrastructure | ✅ Built |
| e5b7637 | Admin V1 generation for old profiles | Infrastructure | Committed, NOT deployed |
| 670a795 | rescoreDimensions import fix | Infrastructure | Committed, NOT deployed |
| 38362fd | DNA Summary canonical path fix | Renderer | Committed, NOT deployed |
| 836fcde | All rescoring_gpt reads fixed | Renderer | Committed, NOT deployed |
| 95f7767 | Documentation complete | Docs | ✅ Committed |
| 798d315 | Deployment trace | Docs | ✅ Committed |

---

## TEST PROFILES

| Profile | ID | rescoring_gpt | rescoring_v1 | Status |
|---------|-------|---|---|---------|
| David Berg | mm-20260523-mqlev9c9 | ❌ null | ❌ null | Pre-deployment |
| Pamela Perez | mm-20260526-r8362esx | ❌ null | ❌ null | Pre-deployment |
| Jonny CEO | mm-20260527-kgppxg8e | ❌ null | ❌ null | Pre-deployment |

---

## NEXT STEPS (IN ORDER)

1. **Vercel Deployment** (external dependency)
   - Commits on GitHub
   - Awaiting Vercel rebuild/deploy
   - ETA: Auto or manual trigger

2. **Admin Rescore Test** (after deployment)
   - POST /api/admin/rescore-profile
   - Target: David, Pamela, Jonny
   - Verify: rescoring_gpt created

3. **Profile Render Verification** (after rescore)
   - Retrieve each profile with nocache=true
   - Check DNA Summary topology
   - Verify: Shows "Concentrated..." not "Balanced..."

4. **Narrative Enrichment Phase 4** (future, not this session)
   - Narrative Regeneration
   - Future Trajectory Refinement
   - One Move Upgrade
   - Contradiction Engine Update

---

## RED LINES (DO NOT TOUCH)

🛑 Baseline scoring (Q1-Q28, ranked_dimensions)  
🛑 Renderer layout/design  
🛑 Vault storage/retrieval  
🛑 FATHOMFREE orchestration  
🛑 Ingress flows (Profile ID, Stripe, etc.)  
🛑 Five Futures (until Phase 4)  
🛑 Executive Summary (until Phase 4)  
🛑 Contradictions (until Phase 4)  

---

**STATE: Production code ready, deployment pending, runtime architecture complete.**
