# MINI_V2_VISUAL_GAP_REPORT.md — Issue Status (2026-05-26)

**Report Date:** 2026-05-26 17:39 MST  
**Status:** ✅ RESOLVED  
**Resolution Type:** Orchestration Parity (not format upgrade)

---

## ORIGINAL ISSUE

**Problem:** FATHOMFREE assessment completion rendered using mini-v2 HTML template instead of full WebProfileReport.

**Symptoms:**
- FATHOMFREE output: 5-page mini profile (old template)
- Profile ID output: Full V3 report (new template)
- Same profile → different visual presentation
- User confusion and consistency issues

**Root Cause:** FATHOMFREE was rendering from job payload directly, using a different rendering flow than manual Profile ID lookup.

---

## RESOLUTION (Commit 008ac85)

### What Was Changed
FATHOMFREE completion flow now routes through exact same `validateProfileId()` pathway as manual Profile ID lookup:

**Before:**
```javascript
// Direct rendering attempt
const canonicalRes = await fetch(...)
setResult({ version: "web", canonical_dossier: data, ... })
// Sometimes succeeded, sometimes fell back to mini-v2 HTML
```

**After:**
```javascript
// Route through validateProfileId() pathway
setProfileId(canonical_profile_id)
const data = await fetch(/api/moremindmap/retrieve-profile?id=...)
setResult({ 
  version: "web",
  canonical_dossier: data.canonical_dossier,
  behavioral_intelligence_v1: data.behavioral_intelligence_v1,
  profile_id: data.profile_id,
  retrieved_at: data.retrieved_at
})
setSubmitted(true)
setProcessing(false)
```

### Impact
- ✅ No more mini-v2 fallback rendering
- ✅ Both pathways use WebProfileReport
- ✅ Both render full narrative sections
- ✅ Both display Five Futures (5 cards)
- ✅ Both show scaling section
- ✅ Both include one move

---

## VISUAL COMPARISON

### FATHOMFREE Output (After Fix)

```
┌─────────────────────────────────────────┐
│  Full WebProfileReport                  │
├─────────────────────────────────────────┤
│  EXECUTIVE SUMMARY                      │
│  [Full interpretation, not placeholder] │
├─────────────────────────────────────────┤
│  FIVE FUTURES                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐│
│  │ Card 1   │ │ Card 2   │ │ Card 3   ││
│  └──────────┘ └──────────┘ └──────────┘│
│  ┌──────────┐ ┌──────────┐             │
│  │ Card 4   │ │ Card 5   │             │
│  └──────────┘ └──────────┘             │
├─────────────────────────────────────────┤
│  COMMUNICATION STYLE                    │
│  [Full section, not truncated]          │
├─────────────────────────────────────────┤
│  HIDDEN CONTRADICTIONS                  │
│  [Full section, not truncated]          │
├─────────────────────────────────────────┤
│  STRATEGIC CEILING                      │
│  [Full section, not truncated]          │
├─────────────────────────────────────────┤
│  ONE MOVE                               │
│  [Specific unblock + mechanism]         │
└─────────────────────────────────────────┘
```

### Manual Profile ID Output (Unchanged)

```
[Same as above]
```

### Result
✅ **Identical Visual Presentation**

---

## TEST CASE: Pamela Perez (mm-20260526-r8362esx)

### Before Fix
| Aspect | FATHOMFREE | Manual Profile ID | Match |
|--------|------------|-------------------|-------|
| Futures | 1 placeholder block | 5 cards | ❌ |
| Sections | Partially expanded | Fully expanded | ❌ |
| Layout | Mini-v2 hybrid | Full WebProfileReport | ❌ |
| Enrichment | Basic | Full V3 | ❌ |

### After Fix
| Aspect | FATHOMFREE | Manual Profile ID | Match |
|--------|------------|-------------------|-------|
| Futures | 5 cards | 5 cards | ✅ |
| Sections | Fully expanded | Fully expanded | ✅ |
| Layout | Full WebProfileReport | Full WebProfileReport | ✅ |
| Enrichment | Full V3 | Full V3 | ✅ |

---

## MINI_V2 HTML FALLBACK STATUS

**Current Status:** ✅ Fallback preserved but not active  
**Use Case:** Error recovery only (if canonical fetch fails even in validateProfileId pathway)  
**Expected Frequency:** <1% (should never happen in normal operation)

**Note:** Mini-v2 template is NOT deprecated. It's kept as graceful degradation in case of system issues. But normal operation uses WebProfileReport exclusively.

---

## FORWARD COMPATIBILITY

**No Breaking Changes:**
- ✅ Profile ID manual lookup unchanged
- ✅ WebProfileReport component unchanged
- ✅ Vault retrieval unchanged
- ✅ Scoring/canonical generation unchanged

**Only Changed:**
- FATHOMFREE completion flow (now uses validateProfileId pathway)

**Result:** Safe to deploy. No rollback risk.

---

## REMAINING MINOR ISSUES (Not Blocking)

These are content issues, not rendering issues:

| Issue | Component | Priority | Note |
|-------|-----------|----------|------|
| Generic Five Futures | Futures Engine | Next session | Needs profile-specific tuning |
| Generic One Move | One Move Engine | Next session | Needs specific unblock logic |
| Placeholder text in places | Section engines | Later | Legacy archetype language |
| State-vs-trait overlap | Unified interpreter | Later | Language polishing |
| Display scoring audit | Rendering | Later | Visual consistency check |

**These do NOT affect orchestration parity. They're content quality improvements.**

---

## DOCTRINE LOCKED: No More Ingress-Specific Rendering

**This issue is RESOLVED because of the DOWNSTREAM ENRICHMENT DOCTRINE.**

Future enrichments will NEVER create divergence because:
1. Ingress layers route to common vault fetch
2. All rendering happens downstream of canonical
3. Both pathways produce identical output by design
4. Before ANY future work, trace both pathways to verify

**Status:** ✅ CLOSED (commit 008ac85)  
**Prevention:** Doctrine locks this issue permanently.

---

**For Future Development:** When adding new enrichment engines (Futures upgrade, One Move upgrade, etc.), remember: they must live downstream and attach to canonical, not ingress. Both ingress paths must remain identical. Always test BOTH pathways.
