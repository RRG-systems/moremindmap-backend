# RUNTIME TRACE: GPT COGNITION CHAIN — EXACT BREAKPOINTS FOUND

**Date:** 2026-05-28 05:40 MST  
**Profile:** David (mm-20260523-mqlev9c9)  
**Status:** ✅ ROOT CAUSE IDENTIFIED  

---

## RUNTIME CHAIN VERIFICATION TABLE

| Step | Expected | Actual | Status | Proof |
|------|----------|--------|--------|-------|
| 1. Canonical exists in Vault | ✅ Canonical profile | ✅ Retrieved from /api/moremindmap/retrieve-profile | PASS | `/tmp/david_profile.json` contains canonical_dossier |
| 2. Canonical has rescoring_gpt | ✅ rescoring_gpt object | ❌ **NULL** | **FAIL** | `jq '.canonical_dossier.canonical_profile_json.rescoring_gpt'` = null |
| 3. Canonical has rescoring_v1 | ✅ rescoring_v1 object | ❌ **NULL** | **FAIL** | `jq '.canonical_dossier.canonical_profile_json.rescoring_v1'` = null |
| 4. Admin endpoint creates rescoring_gpt | ✅ 200 OK, rescoring_gpt saved | ❌ **FUNCTION_INVOCATION_FAILED** | **FAIL** | curl -X POST admin/rescore-profile returns error |
| 5. buildNarrativeV3 receives canonical | ✅ With rescoring layers | ❌ **Without rescoring layers** | **FAIL** | Canonical only has ranked_dimensions (baseline) |
| 6. getCognitionContext extracts layer | ✅ source === 'gpt' or 'v1' | ❌ **source === 'baseline'** | **FAIL** | No GPT or V1 layers to extract |
| 7. buildProfileDNAPrompt receives cognition context | ✅ cognitionContext param | ✅ Parameter passed | PASS | Code review shows conditional pass |
| 8. buildProfileDNAPrompt uses cognition context | ✅ Uses ranked_dimensions from cognitionContext | ⚠️ **Uses baseline ranked_dimensions** | PARTIAL | Uses baseline because that's all available |
| 9. GPT prompt includes GPT context | ✅ includes behavioral topology | ❌ **Includes deterministic topology** | **FAIL** | Prompt receives baseline scorer, not GPT |
| 10. ProfileDNA rendered | ✅ Reflects behavioral patterns | ❌ **Reflects deterministic template** | **FAIL** | Narrative generated from baseline context |
| 11. DNA Summary uses rescoring_gpt.render_ready | ✅ Uses GPT render_ready | ❌ **Uses deterministic fallback** | **FAIL** | render_ready doesn't exist, falls back to hardcoded string |

---

## EXACT BREAKPOINT

**BREAKPOINT: Step #2 - rescoring_gpt Missing**

David's canonical_profile_json in Vault contains:
- ✅ ranked_dimensions (baseline scores)
- ❌ rescoring_v1 (never created)
- ❌ rescoring_gpt (never created)

**Why rescoring_gpt wasn't created:**

1. David's profile created 2026-05-23 (before GPT rescoring infrastructure built 2026-05-27)
2. Admin endpoint should backfill rescoring_gpt, but:
   - ❌ Admin endpoint fails with FUNCTION_INVOCATION_FAILED
   - ❌ No rescoring_gpt has been created

**Consequence:**

Without rescoring_gpt, entire chain falls back to baseline:
```
getCognitionContext(canonical)
  → Tries rescoring_gpt: NULL ❌
  → Tries rescoring_v1: NULL ❌
  → Falls back to ranked_dimensions (baseline) ⚠️
  
buildProfileDNAPrompt receives baseline context
  → Prompt built from deterministic scores, not behavioral cognition
  → GPT generates narrative about baseline, not psychology
  → Result: Deterministic template
```

---

## CRITICAL STRING TRACE

**Search Result:** `"Balanced multi-system topology with flexible dynamics"`

**Found in:** src/components/reports/WebProfileReport.jsx:187

**Function:** DNA Summary topology fallback

**When it executes:**
```javascript
const renderReady = canonical?.rescoring_gpt?.render_ready || canonical?.rescoring_v1?.render_ready || {};
const dominance = canonical?.rescoring_gpt?.dominance_profile || canonical?.rescoring_v1?.dominance_profile || {};

if (renderReady.profile_intensity === 'extreme') {
  return 'Concentrated directional topology...'; // ✅ Would show for David
}
if (renderReady.profile_intensity === 'high') {
  return 'Strong domain topology...'; // ✅ Would show for David
}
// ...
return 'Balanced multi-system topology with flexible dynamics.'; // ❌ FALLBACK (EXECUTES NOW)
```

**Why it executes for David NOW:**
- renderReady is {} (empty) because rescoring_gpt doesn't exist
- dominance is {} (empty) because rescoring_v1 doesn't exist
- All conditions fail
- **Falls back to hardcoded string**

**What would prevent it:**
- ✅ rescoring_gpt.render_ready.profile_intensity = 'extreme'
- ✅ rescoring_v1.render_ready.profile_intensity = 'extreme'

---

## PROOF: WHERE IS THE BREAKPOINT EXACTLY?

### Canonical Inspection

```bash
$ jq '.canonical_dossier.canonical_profile_json | {
  has_rescoring_gpt: (.rescoring_gpt != null),
  has_rescoring_v1: (.rescoring_v1 != null),
  ranked_dimensions: .ranked_dimensions | length,
  rescoring_gpt: .rescoring_gpt
}' /tmp/david_profile.json

{
  "has_rescoring_gpt": false,
  "has_rescoring_v1": false,
  "ranked_dimensions": 8,
  "rescoring_gpt": null
}
```

### Admin Endpoint Status

```bash
$ curl -X POST https://moremindmap.com/api/admin/rescore-profile \
  -H "Authorization: Bearer $SECRET" \
  -d '{"profile_id": "mm-20260523-mqlev9c9"}'

A server error has occurred
FUNCTION_INVOCATION_FAILED
sfo1::nz8db-1779946761366-35d1bfea9914
```

Admin endpoint **still failing** despite import fixes.

---

## CACHE INVESTIGATION

**Question:** Is ProfileDNA being regenerated or reused?

**Answer:** BOTH are broken:
1. buildNarrativeV3 can't regenerate (no rescoring layers to use)
2. Cached narrative doesn't exist (retrieve returns null for narrative_profile)

Retrieved narrative_profile is NULL, meaning:
- Either it was never generated
- Or Vault doesn't have it cached

**Result:** ProfileDNA will be generated fresh by buildNarrativeV3, but:
- ❌ Will be generated from baseline (no GPT context)
- ❌ Will still feel deterministic

---

## RESCORE STATUS: DOES rescoring_gpt EXIST?

**Current State:**
```
rescoring_gpt: ❌ NO
rescoring_v1: ❌ NO
ranked_dimensions: ✅ YES (baseline only)
```

**Why it wasn't created:**
1. David's profile created before rescoring infrastructure (2026-05-23 vs 2026-05-27)
2. Admin endpoint should backfill, but is FAILING

**Error Details:**
- Endpoint: /api/admin/rescore-profile
- Method: POST
- Auth: Bearer token
- Response: FUNCTION_INVOCATION_FAILED
- Indicates: Runtime error in Vercel function

---

## RENDERER STATUS: IS FINAL RENDERER USING GPT?

**Answer:** NO

**DNA Summary:**
```javascript
const topology = renderReady.profile_intensity === 'extreme'
  ? 'Concentrated directional topology...'
  : renderReady.profile_intensity === 'high'
  ? 'Strong domain topology...'
  : 'Balanced multi-system topology with flexible dynamics.' // ← EXECUTES

// Why: renderReady = {} (empty), because rescoring_gpt doesn't exist
```

**ProfileDNA:**
```javascript
narrative.profileDNA?.body || narrative.profileDNA || ''

// Is NULL, so renders from buildNarrativeV3, which has NO GPT context
```

---

## RECOMMENDED SURGICAL FIX (DO NOT IMPLEMENT YET)

**Primary Issue:** Admin endpoint broken → rescoring_gpt never created

**Fix Strategy:**
1. Debug why admin endpoint fails in production
2. Ensure gptBehavioralRescore imports work
3. Ensure rescoring_gpt created and saved to Redis
4. Re-run admin endpoint for David
5. buildNarrativeV3 will then see rescoring_gpt
6. ProfileDNA will be generated with GPT context

**Secondary Issue:** Even if admin endpoint fixed, imports might still fail

**Backup Fix:**
1. Check gptBehavioralRescore import in api/admin/rescore-profile.js
2. Check gptBehavioralRescore import in api/engine/canonical/canonicalProfileGenerator.js
3. Verify function is exported and callable
4. Add console.log traces to admin endpoint to debug runtime failure

---

## EXACT PROOF SUMMARY

| Question | Answer | Proof |
|----------|--------|-------|
| Does David's canonical have rescoring_gpt? | ❌ NO | jq query returns null |
| Can getCognitionContext find GPT layer? | ❌ NO | Falls back to baseline |
| Does buildProfileDNAPrompt use GPT context? | ❌ NO | Receives baseline context only |
| Does ProfileDNA reflect GPT topology? | ❌ NO | Generated from baseline scores |
| Does DNA Summary use rescoring_gpt? | ❌ NO | Falls back to hardcoded string |
| Why hasn't rescoring_gpt been created? | Admin endpoint fails | FUNCTION_INVOCATION_FAILED |
| Where is runtime broken? | Admin endpoint in Vercel | Cannot invoke gptBehavioralRescore |

---

## CRITICAL REALIZATION

**The GPT cognition bridge code IS correct.**

**The problem is UPSTEAM:** The rescoring_gpt data itself doesn't exist because the admin endpoint that creates it is FAILING.

Without rescoring_gpt in canonical, even correct code falls back to baseline.

**Fix requires:** Debug and repair admin endpoint, not the cognition bridge code.

---

**ROOT CAUSE: Admin endpoint unable to create rescoring_gpt. Rescoring layers missing from David's profile. GetCognitionContext falls back to baseline. Profiles render deterministically because no behavioral layer is available.**

**Next step: Debug admin endpoint runtime failure (gptBehavioralRescore invocation error in Vercel).**
