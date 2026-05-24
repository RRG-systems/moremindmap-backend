# EXACT WIRING INSTRUCTIONS: V3 Integration into WebProfileReport

**Date:** 2026-05-23 17:52 MST  
**Objective:** Wire V3 buildNarrativeV3 into React component  
**Files:** 1 (WebProfileReport.jsx)  
**Lines:** 2 critical, 1 optional async wrapper  
**Time:** ~5 minutes  

---

## CURRENT STATE (BROKEN)

**File:** `src/components/reports/WebProfileReport.jsx`

```javascript
// Line 10 (CURRENT - WRONG)
import { expandNarrative } from '../../lib/narrativeExpander.js';

// Line 26 (CURRENT - WRONG)
const narrative = expandNarrative(canonical);
```

Result: Uses V2 deterministic renderer (no GPT).

---

## REQUIRED CHANGES

### Change #1: Import V3 Engine

**Location:** `src/components/reports/WebProfileReport.jsx`, Line 1-15

**BEFORE:**
```javascript
import { useState, useMemo, useEffect } from "react"
import MiniProfileReport from "./components/reports/MiniProfileReport.jsx";
import WebProfileReport from "./components/reports/WebProfileReport.jsx";
import Page0A_OrganizationalContext from "./components/Page0A_OrganizationalContext.jsx";
import Page0B_ContextualSignals from "./components/Page0B_ContextualSignals.jsx";
import MOREMINDMAP_QUESTIONS from "./lib/assessments/moremindmap-questions";
import { expandNarrative } from '../../lib/narrativeExpander.js';  // <-- LINE 10
```

**AFTER:**
```javascript
import { useState, useMemo, useEffect } from "react"
import MiniProfileReport from "./components/reports/MiniProfileReport.jsx";
import WebProfileReport from "./components/reports/WebProfileReport.jsx";
import Page0A_OrganizationalContext from "./components/Page0A_OrganizationalContext.jsx";
import Page0B_ContextualSignals from "./components/Page0B_ContextualSignals.jsx";
import MOREMINDMAP_QUESTIONS from "./lib/assessments/moremindmap-questions";
import { buildNarrativeV3 } from '../../lib/narrativeV3/buildNarrativeV3.js';  // <-- LINE 10 (CHANGED)
```

**Exact Edit:**
```
OLD: import { expandNarrative } from '../../lib/narrativeExpander.js';
NEW: import { buildNarrativeV3 } from '../../lib/narrativeV3/buildNarrativeV3.js';
```

---

### Change #2: Call V3 Engine

**Location:** `src/components/reports/WebProfileReport.jsx`, Line 23-30 (approximate)

**BEFORE:**
```javascript
export default function WebProfileReport({ canonical, profileId }) {
  if (!canonical) {
    return <div className="web-report-error">Unable to load profile data</div>
  }

  const data = canonical.canonical_profile_json || canonical;
  const personName = canonical.person_name || 'Assessment Subject';
  const company = canonical.company_name || '';
  const profileType = data.inferred_patterns?.profile_type || 'Behavioral Profile';
  const vectorScores = data.vector_scores || {};
  const topSystems = data.top_systems || {};
  const ranked = data.ranked_dimensions || [];

  // Expand narratives from canonical fields
  const narrative = expandNarrative(canonical);  // <-- LINE ~26 (WRONG)
```

**AFTER:**
```javascript
export default function WebProfileReport({ canonical, profileId }) {
  if (!canonical) {
    return <div className="web-report-error">Unable to load profile data</div>
  }

  const data = canonical.canonical_profile_json || canonical;
  const personName = canonical.person_name || 'Assessment Subject';
  const company = canonical.company_name || '';
  const profileType = data.inferred_patterns?.profile_type || 'Behavioral Profile';
  const vectorScores = data.vector_scores || {};
  const topSystems = data.top_systems || {};
  const ranked = data.ranked_dimensions || [];

  // V3 narrative rendering (with fallback to local rendering if GPT unavailable)
  const [narrative, setNarrative] = useState(null);
  const [narrativeLoading, setNarrativeLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const v3Narrative = await buildNarrativeV3(canonical, true, profileId);
        setNarrative(v3Narrative);
      } catch (err) {
        console.error('[WebProfileReport] V3 rendering failed:', err);
        setNarrative(null);
      } finally {
        setNarrativeLoading(false);
      }
    })();
  }, [canonical, profileId]);

  // Handle loading state
  if (narrativeLoading || !narrative) {
    return <div className="web-report-loading">Loading profile narrative...</div>;
  }
```

**Exact Edit:**
```
OLD: const narrative = expandNarrative(canonical);

NEW: 
  const [narrative, setNarrative] = useState(null);
  const [narrativeLoading, setNarrativeLoading] = useState(true);

  useEffect(() => {
    (async () => {
      try {
        const v3Narrative = await buildNarrativeV3(canonical, true, profileId);
        setNarrative(v3Narrative);
      } catch (err) {
        console.error('[WebProfileReport] V3 rendering failed:', err);
        setNarrative(null);
      } finally {
        setNarrativeLoading(false);
      }
    })();
  }, [canonical, profileId]);

  if (narrativeLoading || !narrative) {
    return <div className="web-report-loading">Loading profile narrative...</div>;
  }
```

---

### Change #3: Update Section Rendering (Conditional)

**Location:** `src/components/reports/WebProfileReport.jsx`, section renders

The section rendering should be idempotent. If narrative has different structure than V2, update selectively:

**V2 output structure:**
```javascript
narrative = {
  profileDNA: "...",
  executiveSummary: "...",
  operatingPattern: "...",
  communicationStyle: "...",
  hiddenContradictions: "...",
  strategicCeiling: "...",
}
```

**V3 output structure:**
```javascript
narrative = {
  executiveSummary: { body: "...", grounding_used: [...], key_warning: "..." },
  communicationStyle: { body: "...", grounding_used: [...], key_warning: "..." },
  hiddenContradictions: { body: "...", grounding_used: [...], key_warning: "..." },
  strategicCeiling: { body: "...", grounding_used: [...], key_warning: "..." },
}
```

**Update section renders to handle V3 structure:**

**EXAMPLE (For Executive Summary section in WebProfileReport):**

**BEFORE:**
```javascript
{/* Section 2: Executive Summary */}
<section className="narrative-section featured">
  <h2 className="section-title">Executive Summary</h2>
  <div className="narrative-text">{narrative.executiveSummary}</div>
</section>
```

**AFTER:**
```javascript
{/* Section 2: Executive Summary */}
<section className="narrative-section featured">
  <h2 className="section-title">Executive Summary</h2>
  <div className="narrative-text">
    {narrative.executiveSummary?.body || narrative.executiveSummary}
  </div>
  {narrative.executiveSummary?.key_warning && (
    <div className="key-warning">⚠️ {narrative.executiveSummary.key_warning}</div>
  )}
</section>
```

**Apply this pattern to all V3 sections:**
- executiveSummary
- communicationStyle
- hiddenContradictions
- strategicCeiling

---

## VERIFICATION CHECKLIST

After making changes:

### Local Verification

```bash
cd /Users/rrg/.openclaw/workspace/moremindmap-live

# 1. Syntax check
npm run build

# Should succeed with no errors
# ✓ built in XXXms

# 2. Dev server test
npm run dev

# Open browser: http://localhost:5173
# Enter profile: MM-20260523-mqlev9c9
# Click: Retrieve
# Expected: V3 rendering with 4 sections

# 3. Check browser console
# Look for logs: [V3 CACHE HIT] or [V3] Calling GPT-5.5 for
```

### Code Review Checklist

- [ ] Import changed from `expandNarrative` to `buildNarrativeV3`
- [ ] Function call wrapped in `useEffect` (async)
- [ ] Loading state handled
- [ ] Error handling added
- [ ] Section renders updated to handle V3 structure
- [ ] All 4 V3 sections rendering (not V2 sections)

### Production Verification

After deploying:

```bash
# Check that production build uses V3
curl https://moremindmap.com/api/moremindmap/retrieve-profile?id=MM-20260523-mqlev9c9

# Open browser: https://moremindmap.com
# Enter profile: MM-20260523-mqlev9c9
# Expected output: V3 rendering with less mechanical repetition

# If GPT API key set:
# Expected: More asymmetrical, varied language
# (true GPT texture layer)

# If no GPT API key:
# Expected: Same as local fallback (deterministic but still V3)
```

---

## CRITICAL ENVIRONMENT VARIABLE

After wiring V3, deploy and set API key:

**Vercel Dashboard:**
1. https://vercel.com/projects
2. Select: moremindmap
3. Settings → Environment Variables
4. Add: `VITE_OPENAI_API_KEY=sk-proj-...` (from OpenAI API dashboard)
5. Redeploy for env var to take effect

**Verify in Vercel logs:**
```
[V3] Calling GPT-5.5 for executiveSummary
[V3 CALL START] Section: executiveSummary
[GPT-5.5 CALL SUCCESS] Section: executiveSummary, Body length: XXX
```

---

## TIMELINE

**Stage 1: Wiring (This session)**
- [ ] Update import (1 line)
- [ ] Update function call (8 lines)
- [ ] Update section renders (apply pattern)
- [ ] Build locally ✓
- [ ] Test locally ✓

**Stage 2: Deployment (Next action)**
- [ ] Commit changes
- [ ] Push to origin/main
- [ ] Vercel auto-deploys
- [ ] Verify in production ✓

**Stage 3: Activation (Optional, recommended)**
- [ ] Get OpenAI API key
- [ ] Set VITE_OPENAI_API_KEY in Vercel
- [ ] Redeploy
- [ ] Verify GPT texture layer active ✓

---

## ROLLBACK PROCEDURE

If something breaks:

```bash
# Revert to V2
git revert <commit-hash>
git push origin main

# Vercel auto-deploys
# Production rolls back to V2
```

But this shouldn't be needed. Changes are pure additions (V3 already exists, just wiring it).

---

## EXPECTED OUTPUT BEFORE/AFTER

### BEFORE (V2 - Current)

```
Executive Summary:
"An operator who moves like a chess player analyzing board state: rapid pattern 
recognition, quick move commitment, minimal second-guessing. Strength: velocity 
and conviction. Liability: emerges under complexity. Immediate impact: executes 
faster, builds momentum, establishes direction. Medium-term: leaves precision 
details to compound into problems. Under acute stress: doubles down on speed, 
which works briefly then fails catastrophically."

[OBSERVATION: Mechanical rhythm, repeated "execution" theme, predictable structure]
```

### AFTER (V3 with GPT - Expected)

```
Executive Summary:
"Enters situations already forming direction. Couples this conviction with 
pattern reading that maintains strategic scope. The immediate effect: velocity. 
Things move faster in his orbit. Decisions compound into momentum. There's a 
cost. The missing 25% of information doesn't feel like missing information for 
three months. It just feels like bad luck when it surfaces. Month four, the 
luck runs out."

[OBSERVATION: Asymmetrical structure, micro-scenarios ("month four"), less mechanical]
```

(Exact wording depends on what GPT produces, but character is different.)

---

## EXACT FILES TO TOUCH

```
ONLY:
  src/components/reports/WebProfileReport.jsx
  - Line 10: Change import
  - Line 26: Change function call + add async wrapper
  - Section renders: Apply V3 structure pattern

ENVIRONMENT (Vercel Dashboard):
  - Add: VITE_OPENAI_API_KEY (after deploy)

DO NOT TOUCH:
  - src/lib/narrativeV3/ (already fixed)
  - .env.production (API key goes in Vercel env, not .env)
  - API routes (already working)
  - Styling (use existing CSS)
```

---

**Ready to wire. 5-minute fix. High confidence.**
