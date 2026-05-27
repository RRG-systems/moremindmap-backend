# FRONTIER INFERENCE RESTORATION — QUICK REFERENCE

**Date:** 2026-05-26 23:58 MST  
**Mission:** Restore behavioral intelligence layer (pressure mechanics, contradictions, causal chains)  
**Status:** READY FOR IMPLEMENTATION

---

## THE PROBLEM (1 SENTENCE)

The orchestrator that calls 25 inference modules was bypassed during Vercel emergency; all profiles now generate as shallow templates instead of rich behavioral intelligence.

---

## THE PROOF

### David Berg (FRONTIER WORK)
- MM-20260523-mqlev9c9
- Generated with full 25-step orchestrator
- Rich contradictions, stress patterns, organizational effects
- Behavioral depth: **HOLY SHIT** level

### Billybob (CURRENT WORK)
- mm-20260526-yj004cpt
- Generated with template-only buildFullCanonical()
- Empty contradictions, no stress patterns, no effects
- Behavioral depth: **TEMPLATE-FILLED** level

---

## THE SOLUTION (2 STEPS)

### Step 1: Restore the Orchestrator File
```bash
cp api/engine/canonical/canonicalProfileGenerator-FULL-BACKUP-1779598150.js \
   api/engine/canonical/canonicalProfileGenerator.js
```

**Why:** The full frontier code exists in backup. Just restore it.

### Step 2: Update Execution Call in executeCanonicalGeneration.js

**Replace this:**
```javascript
const canonical_profile = buildFullCanonical(job.profileInput, job.job_id)
```

**With this:**
```javascript
import { generateCanonicalProfile } from './canonicalProfileGenerator.js'

let canonical_profile
try {
  canonical_profile = await generateCanonicalProfile(job.profileInput, {
    profile_id,
    model: 'canonical-v2-frontier-restored'
  })
} catch (err) {
  console.error('[CANONICAL-GENERATION] Frontier failed, fallback:', err.message)
  canonical_profile = buildFullCanonical(job.profileInput, job.job_id)
  canonical_profile.profile_id = profile_id
}
```

**Why:** Call frontier first, graceful fallback if needed.

---

## WHAT GETS RESTORED

### Inference Modules (All 25, All Present in Repo)
- ✅ inferVectorScores — Dimension ranking
- ✅ inferBehavioralPatterns — Operating system
- ✅ inferContradictions — Tension mapping
- ✅ inferStressPatterns — Pressure response
- ✅ inferCommunicationStyle — Communication friction
- ✅ inferLeadershipArchitecture — Decision patterns
- ✅ inferBehavioralConsequences — Behavior → org impact
- ✅ inferOrganizationalEffects — Team/culture effects
- ✅ inferHiddenCosts — Long-term costs
- ✅ inferFutureTrajectory — 2yr/5yr prediction
- ✅ inferCausalChains — Causality grounding
- ... (14 more)

### Profile Fields Restored
| Field | Current | After Restore |
|-------|---------|----------------|
| contradictions | [] | [2-3 evidence-grounded tensions] |
| stress_patterns | {} | {amplified_dimension, lost_dimensions, response} |
| behavioral_consequences | undefined | [6-8 consequence chains] |
| organizational_effects | undefined | [team/culture effects] |
| hidden_costs | undefined | [long-term costs] |
| causal_chains | undefined | [causality traces] |
| evidence_map | undefined | [source grounding] |
| narrative_profile | generic | RICH with behavioral specificity |

---

## VERIFICATION (3 TESTS)

### Test 1: New Profile Generation
```
Submit new assessment → Get profile ID
```

### Test 2: Check Contradictions
```
GET vault profile → Verify contradictions field NOT empty
Expected: 2-3 tensions like "freedom vs growth ambition"
```

### Test 3: Check Inference Fields
```
Verify stress_patterns.amplified_dimension is set
Verify behavioral_consequences exists
Verify causal_chains exists
```

---

## ROLLBACK (IF NEEDED)

If Vercel ESM errors appear (unlikely, issue resolved since backup):
```bash
# Revert to current stub
git checkout api/engine/canonical/canonicalProfileGenerator.js
git checkout api/engine/canonical/executeCanonicalGeneration.js
```

---

## FILES TO MODIFY (2 TOTAL)

1. **api/engine/canonical/canonicalProfileGenerator.js**
   - Action: Restore from backup
   - Lines affected: ~400 (entire file)

2. **api/engine/canonical/executeCanonicalGeneration.js**
   - Action: Update one function call
   - Lines affected: 1-10 (import + try-catch wrapper)

---

## RISKS & MITIGATIONS

| Risk | Probability | Mitigation |
|------|-------------|-----------|
| Vercel ESM error | Very Low | Try-catch fallback to buildFullCanonical |
| Module import fail | Very Low | All modules verified present in repo |
| Performance impact | Low | Can be measured; inferences parallelizable |
| Vault schema issues | None | Renderer gracefully ignores unknown fields |

---

## TIMELINE

| Phase | Time |
|-------|------|
| File restoration | 1 min |
| Code update + import fix | 5 min |
| Deploy to Vercel | 3 min |
| Test new profile generation | 5 min |
| Verification (compare profiles) | 5 min |
| **TOTAL** | **19 min** |

---

## SUCCESS CRITERIA

✅ New profile contains contradictions  
✅ New profile contains stress_patterns  
✅ New profile contains behavioral_consequences  
✅ Narrative is RICHER than Billybob  
✅ No Vercel compilation errors  
✅ David Berg profile SAME quality (verify unchanged)  

---

## ONE-LINER SUMMARY

**Restore the 25-inference orchestrator from backup and wire it back into executeCanonicalGeneration with a try-catch fallback. Profiles will regain behavioral depth, causal chains, contradiction analysis, and pressure mechanics.**

---

Ready to execute. Report locked 2026-05-26 23:58 MST.
