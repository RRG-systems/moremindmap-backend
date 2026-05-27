# SOURCE_OF_TRUTH.md — Project State (2026-05-26 17:39 MST)

**Last Updated:** 2026-05-26 17:39 MST  
**Commit:** 008ac85 (ORCHESTRATION PARITY COMPLETE)

---

## CURRENT STABLE WINS ✅

### Architectural Foundation
- ✅ FATHOMFREE pathway and Profile ID pathway are now unified
- ✅ FATHOMFREE no longer renders directly from job payload
- ✅ FATHOMFREE now routes through same validateProfileId / retrieve-profile pathway as manual profile ID lookup
- ✅ Divergence between FATHOMFREE and Profile ID render path is **FIXED** (commit 008ac85)

### Data Pipeline
- ✅ Canonical dossier saves successfully
- ✅ Vault retrieval works
- ✅ intake_answers are saved in dossier
- ✅ frontier orchestrator restored (25 inference modules)
- ✅ Model label: `canonical-v2-frontier-restored` is active

### Rendering & Interpretation
- ✅ WebProfileReport renders
- ✅ unifiedInterpreter exists and is wired
- ✅ narrative-v3 endpoint works
- ✅ GPT-5.5 JSON issue fixed by requiring "as JSON" in prompts
- ✅ No emergency_inline success path should be used

---

## KNOWN REMAINING ISSUES ⚠️

### Semantic/Engine Refinement (DO NOT TOUCH YET)
- ⚠️ Five Futures is still generic and should be upgraded first
- ⚠️ One Move is generic and should be upgraded second
- ⚠️ Contradiction Engine needs later refinement
- ⚠️ Scaling Constraint Engine needs later refinement
- ⚠️ Team Dynamics Engine needs later refinement
- ⚠️ Intelligent downstream engines need tuning

### Display & Consistency Issues (DO NOT TOUCH YET)
- ⚠️ Scoring/display audit needed: top DNA grid and big three cards may pull from different semantic buckets and look inconsistent
- ⚠️ Interpreter currently overuses anxiety/avoidance language across profiles; needs state-vs-trait separation later
- ⚠️ Section engines still contain legacy archetype language in places

### RED LINE — DO NOT TOUCH THESE
- 🛑 Do NOT touch renderer (layout/design)
- 🛑 Do NOT touch vault (storage/retrieval)
- 🛑 Do NOT touch canonical generation pipeline
- 🛑 Do NOT touch FATHOMFREE orchestration
- 🛑 Do NOT touch scoring system (deterministic, working)
- Until memory is saved and future task is explicit

---

## CRITICAL COMMITS (This Session)

| Commit | What | Why |
|--------|------|-----|
| 1f46b6b | intake_answers to vault | Written answers flowing to GPT |
| 537db0a | intake_answers through frontend | GPT context integration |
| 75a4bb6 | OpenAI schema fix (as JSON) | HTTP 400 error resolution |
| 89a02d0 | Unified interpreter brain pass | Single shared interpretation artifact |
| 7050568 | Evidence dominance reweighting | All 7 sections prioritize truth over archetype |
| 3f58b65 | ReferenceError fix | Typo in deriveFutureIfSupportAdded |
| 59ee5e5 | Retry loop on canonical fetch | Timing race condition handling |
| 008ac85 | FATHOMFREE validateProfileId pathway | Orchestration parity complete |

---

## RECENT TEST PROFILES

| Profile | ID | Status | Notes |
|---------|----|----|-------|
| David Berg | MM-20260523-mqlev9c9 | ✅ | Vector-dominant, command/momentum |
| Billybob Depressed3 | mm-20260526-fqxptt3n | ✅ | Stuck/fearful/avoidant, unified interpreter match |
| Pamela Perez | mm-20260526-r8362esx | ✅ | Orchestration parity test case |
| Jonny TOUGHCEO / Blackrock | mm-20260527-kgppxg8e | ✅ | Additional validation |

---

## NEXT PRIORITY (In Order)

### Phase 1: Engine Refinement
1. **Upgrade Futures Engine** (Five Futures: move from generic to specific)
2. **Upgrade One Move Engine** (specific actionable unblock, not generic advice)
3. **Then Contradiction Engine** (deep contradiction analysis)
4. **Then Scaling Constraint Engine** (where does this person hit the ceiling?)
5. **Then Team Dynamics Engine** (how do they show up with others?)

### Phase 2: Polish & Validation
6. **Scoring/display audit** (top DNA grid + big three cards consistency)

---

## DOWNSTREAM ENRICHMENT DOCTRINE (LOCKED) 🔒

**Status:** CANONICAL. DO NOT DEVIATE.

### Prime Directive

The MOREMindMap system now has THREE ingress paths:

1. Stripe-paid assessment
2. Promo-code/FATHOMFREE assessment
3. Profile-ID retrieval

**These MUST NEVER become separate intelligence systems.**

### Ingress Layer Responsibilities (ONLY)

Ingress layers are **ONLY allowed to:**
- authorize
- validate
- retrieve
- normalize
- route
- fetch canonical artifacts

Ingress layers are **NOT allowed to:**
- score
- enrich
- interpret
- generate futures
- generate One Move
- mutate narrative logic
- render differently
- inject profile-specific intelligence

### ALL Intelligence Generation Lives Downstream

**ALL intelligence generation must occur ONLY downstream of canonical dossier generation.**

Canonical architecture is now locked as:

```
INGRESS LAYER (normalize, validate, route only)
  ↓
CANONICAL DOSSIER (stable, immutable from ingress)
  ↓
SHARED DOWNSTREAM ENRICHMENT PIPELINE
  ├─ Unified Interpreter (ONE shared artifact)
  ├─ Futures Engine
  ├─ One Move Engine
  ├─ Contradiction Engine
  ├─ Pressure Mechanics Engine
  ├─ Team Experience Engine
  ├─ Scaling Constraint Engine
  ├─ Facilitator Intelligence Layer
  ├─ Organizational Role Mapping Layer
  └─ Comparative Scoring Infrastructure
  ↓
LOCKED PROFILE OBJECT
  ↓
RENDERER (layout/design, consumption only)
```

### Orchestration Parity Rule

**ALL future enrichments must:**
- occur downstream
- operate on canonical dossier
- remain renderer-compatible
- preserve orchestration parity
- preserve byte-equivalent rendering across all ingress paths

### Current Architecture (VALIDATED)

```
FATHOMFREE Assessment Completion:
  ↓
Job completes, returns canonical_profile_id
  ↓
Frontend: setProfileId() + call validateProfileId()
  ↓
validateProfileId(): Fetch /api/moremindmap/retrieve-profile?id=...
  ↓
Vault returns: canonical_dossier (with intake_answers + frontier outputs + interpreted fields)
  ↓
setResult({ version: "web", canonical_dossier, ... })
setSubmitted(true), setProcessing(false)
  ↓
Component renders: <WebProfileReport canonical={canonical_dossier} />
  ↓
buildNarrativeV3():
  - Calls unifiedInterpreter() → one shared interpretation artifact
  - All 7 sections read from unified artifact (not independent reinvention)
  - narrative-v3 endpoint renders JSON sections with GPT-5.5
  ↓
Render output: Full 5-card futures + 7 report sections + scaling + one move
```

**Key Win:** FATHOMFREE and manual Profile ID lookup use IDENTICAL pathway. Output is byte-equivalent. This is the template all future enrichments must follow.

---

## MODEL ATTRIBUTION

**Generation Mode:** `canonical-v2-frontier-restored`  
**Model:** OpenAI GPT-5.5 (narrative-v3 sections)  
**Interpretation:** unifiedInterpreter.js (unified artifact pipeline)  
**Scoring:** Deterministic (25 MC/ranking/written questions → normalized_dimensions)

---

## DEPLOYMENT STATUS

**Live on Vercel:** ✅ (commit 008ac85)  
**No manual deployment needed:** Services auto-deploy on push to main  
**Monitoring:** Check narrative-v3 endpoint for any 400/500 errors (schema fixed, should be 200)

---

## HEALTH CHECK

```
✅ Canonical saves to vault
✅ Retrieval returns full dossier
✅ Unified interpreter reads entire dossier
✅ Narrative-v3 renders without errors
✅ WebProfileReport displays correctly
✅ FATHOMFREE completion matches Profile ID load
✅ No emergency fallbacks in active use
✅ Frontier orchestrator (25 modules) operational
```

**Result:** Stable foundation for engine refinement.
