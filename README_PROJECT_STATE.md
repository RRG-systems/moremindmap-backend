# README_PROJECT_STATE.md — Quick Reference (2026-05-26)

**Latest Stable State:** 2026-05-26 17:39 MST  
**Last Commit:** 008ac85 (ORCHESTRATION PARITY COMPLETE)

---

## TL;DR: WHAT WORKS NOW ✅

- FATHOMFREE assessment completion and manual Profile ID lookup now produce **identical output**
- Both use same rendering pipeline (validateProfileId → vault retrieval → WebProfileReport)
- Five Futures renders 5 cards (not placeholders)
- All narrative sections fully expanded
- Unified interpreter wired and active
- Frontier orchestrator restored (25 inference modules)
- GPT-5.5 integration fixed
- intake_answers flowing through entire pipeline

---

## PROOF: Pamela Perez (mm-20260526-r8362esx)

**Before Fix:**
- FATHOMFREE: 1 placeholder futures block + partial sections
- Profile ID: 5 full futures cards + complete sections
- Divergence: ❌

**After Fix:**
- FATHOMFREE: 5 full futures cards + complete sections
- Profile ID: 5 full futures cards + complete sections
- Divergence: ✅ FIXED

---

## CURRENT STATE

### ✅ Operational
- Canonical generation (25-module frontier orchestrator)
- Vault storage and retrieval
- Unified interpretation (single artifact → all 7 sections)
- WebProfileReport rendering
- Narrative-v3 endpoint (GPT-5.5 JSON rendering)
- FATHOMFREE orchestration (now using validateProfileId pathway)
- Profile ID manual lookup
- Scoring system (deterministic, normalized_dimensions)

### ⚠️ Known Issues (Not Blocking, Fix Later)
- Five Futures content is generic (should be profile-specific)
- One Move content is generic (should be specific unblock)
- Contradiction Engine output could be more precise
- Scaling Constraint Engine could be more granular
- Team Dynamics Engine output could be more nuanced
- Interpreter sometimes overuses anxiety/avoidance language (needs state-vs-trait)
- Display scoring might pull from misaligned buckets (audit needed)

### 🛑 DO NOT MODIFY
- Renderer (layout/design)
- Vault (storage/retrieval logic)
- Canonical generation pipeline
- FATHOMFREE orchestration (just fixed it)
- Scoring system
- Until memory saved + explicit task

---

## RECENT TEST PROFILES

| Profile | ID | Entry Point | Status |
|---------|----|----|--------|
| David Berg | MM-20260523-mqlev9c9 | Manual Profile ID | ✅ Full render |
| Billybob | mm-20260526-fqxptt3n | Manual Profile ID | ✅ Full render |
| Pamela Perez | mm-20260526-r8362esx | FATHOMFREE + Profile ID (parity test) | ✅ Identical |
| Jonny TOUGHCEO | mm-20260527-kgppxg8e | (validation) | ✅ Full render |

---

## ARCHITECTURE (Current)

```
FATHOMFREE Assessment Entry:
  1. User submits assessment
  2. Backend processes, generates canonical, saves to vault
  3. Frontend polls until complete
  4. Frontend calls validateProfileId(canonical_profile_id)
  5. validateProfileId fetches from vault
  6. WebProfileReport renders with full narrative-v3 enrichment

Manual Profile ID Entry:
  1. User enters profile ID in URL
  2. Frontend calls validateProfileId(profile_id)
  3. validateProfileId fetches from vault
  4. WebProfileReport renders with full narrative-v3 enrichment

RESULT: Same pathway, same output, byte-equivalent
```

---

## DOWNSTREAM ENRICHMENT DOCTRINE (LOCKED) 🔒

**Architectural Law:** All future enrichments MUST live downstream of canonical generation. Ingress layers exist ONLY to authorize, validate, retrieve, normalize, and route. They do NOT score, interpret, or generate intelligence.

**Before ANY enrichment work:**
1. Trace architecture (both ingress paths)
2. Map dependencies (what data flows where)
3. Verify orchestration parity (both paths converge)
4. Analyze insertion point (downstream, not ingress)
5. Check backward compatibility (no renderer breaks)

**After every enrichment:**
- Test 2-3 profiles minimum
- Test BOTH ingress paths
- Confirm byte-equivalent output
- Confirm no regression

---

## NEXT PRIORITY (In Order)

### Immediate (Next Session)
1. **Upgrade Futures Engine** — make Five Futures specific to each profile
   - Apply doctrine (orchestration trace first, test both paths)
2. **Upgrade One Move Engine** — make it a specific mechanism, not generic advice
   - Apply same rigor as Futures

### Soon After
3. Contradiction Engine refinement
4. Scaling Constraint Engine refinement
5. Team Dynamics Engine refinement
6. Scoring/display audit

### Longer Term
- Interpreter language polishing (state-vs-trait separation)
- Performance optimization if needed

---

## DEPLOYMENT STATUS

**Current Environment:** Vercel (auto-deploy)  
**Monitoring:** Watch narrative-v3 endpoint for errors (schema fixed, should be 200)  
**Rollback:** Not needed (fix is stable)  

---

## KEY FILES

| File | Purpose | Status |
|------|---------|--------|
| src/Profile.jsx | Entry point, FATHOMFREE orchestration | ✅ Updated |
| api/moremindmap/retrieve-profile.js | Vault fetch | ✅ Working |
| src/lib/narrativeV3/unifiedInterpreter.js | Single interpretation artifact | ✅ Wired |
| src/lib/narrativeV3/buildNarrativeV3.js | Narrative building | ✅ Using unified |
| src/lib/narrativeV3/sectionPrompts.js | 7 section renderers | ✅ Evidence dominance active |
| api/engine/canonical/executeCanonicalGeneration.js | Canonical generation | ✅ Frontier restored |
| api/engine/vault/saveCanonicalProfile.js | Vault storage | ✅ Working |
| src/components/reports/WebProfileReport.jsx | Main render component | ✅ Full features |

---

## QUICK HEALTH CHECK

```bash
# Verify deployment
curl https://moremindmap.vercel.app/api/diagnostic/get-vault-profile?id=mm-20260526-r8362esx

# Should return full canonical_dossier with:
# - intake_answers
# - frontier outputs (25 modules)
# - interpreted fields
```

---

## WHAT TO REMEMBER

**This Session's Achievement:** Complete orchestration parity between FATHOMFREE assessment completion and manual Profile ID lookup. Both pathways now use identical rendering pipeline and produce byte-equivalent output.

**Stability:** High. Foundation is solid. Engine refinements can proceed safely.

**Constraint:** Do not touch renderer, vault, canonical, orchestration, or scoring until next explicit task.

**Doctrine:** All enrichment work follows downstream pattern. Trace first. Test both paths. Confirm parity.

---

**For D.J.:** You're good to proceed with Futures and One Move upgrades using the doctrine. Everything underneath is stable and consistent.
