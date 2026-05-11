# MOREMindMap Mini Profile V2 — 3-Phase Stabilization (EXECUTIVE BRIEF)

**Current State:** Patchwork dynamic rendering (fragile, test data risk)  
**Target State:** Template-first assembly (locked structure, AI content only)  
**Status:** ANALYSIS COMPLETE — Ready for approval before coding

---

## 3 PHASES AT A GLANCE

### PHASE 1: DESIGN TEMPLATE
**What:** Create single locked HTML template with ALL page structure fixed  
**Input:** Current working report HTML  
**Output:** `/templates/mini-profile-v2-master.html` with `{{ PLACEHOLDER }}` markers  
**Time:** 2-3 hours  
**Risk:** LOW  
**Why:** Eliminates dynamic page structure sprawl across multiple renderers

### PHASE 2: CONTENT INJECTION  
**What:** Build injector that replaces placeholders with AI-generated JSON content  
**Input:** Structured JSON from generatePremiumMiniProfileV2.js  
**Output:** Final HTML (template + placeholders filled)  
**Time:** 1-2 hours  
**Risk:** LOW  
**Why:** Separates content generation from page layout (AI ≠ layout control)

### PHASE 3: DATA POPULATION LOCK
**What:** Enforce strict validation — NO hardcoded test data reaches production  
**Input:** Assessment ID + 24-question responses  
**Output:** Report with audit trail (provenance: which assessment generated it)  
**Time:** 1-2 hours  
**Risk:** LOW  
**Why:** Current risk: V8/Fd4 test profile could ship as real customer data

---

## CURRENT RISKS (Why This Matters)

| Risk | Cause | Impact |
|------|-------|--------|
| **Multiple HTML generators** | Backend calls frontend renderer + has own logic | Signature appears inconsistently, test data leaks |
| **SVG insertion fragile** | Regex-based stripping + dynamic injection | Page 2 disappears or appears twice |
| **Environment section timing** | String replacement integration point | Section missing or duplicated |
| **Page structure varies** | Dynamic rendering based on content length | Reports become 15 pages instead of 14 |
| **Hardcoded test data** | V8/Fd4/F4 in test fixtures | Sample profile ships to real customers |
| **Renderer file sprawl** | Logic scattered across 6+ files | Hard to understand how report built, impossible to debug |

---

## SAFEST IMPLEMENTATION ORDER

```
Stage 1: Design Template (2-3h, LOW risk)
  └─> Stage 2: Create Injector (1-2h, LOW risk)
      └─> Stage 3: Wire Injector (2-3h, MEDIUM risk, but mitigated)
          └─> Stage 4: Validation (1-2h, LOW risk)
              └─> Stage 5: Cleanup & Docs (1h, NONE)

TOTAL: 7-11 hours | Can deploy incrementally at each stage
```

**Key:** Each stage has clear deliverable. Stages 1-2 can verify independently before full wire-up.

---

## FILES INVOLVED (No coding yet)

### Will Create (New)
- `/templates/mini-profile-v2-master.html` — Master template with locked structure
- `/engine/miniProfileV2Injector.js` — Placeholder → JSON injection logic

### Will Modify (Thin layer)
- `/routes/miniProfileV2Routes.js` — Add validation + call new injector
- `/engine/auditV2Reports.js` — Track report provenance

### Will Deprecate (Keep for now, remove later)
- `/utils/page2IntegratedRenderer.js` (370 lines) — Old renderer
- `/utils/htmlRendererAdapter.js` — Old router
- `/utils/page2SvgEngine.js` — Old SVG injector (consolidated into template)

### Won't Touch (Stays the same)
- ✅ Signature scoring logic
- ✅ SVG template visual design
- ✅ Stage A/B AI pipeline
- ✅ Operating Environment Fit matching
- ✅ CSS/typography/colors

---

## CORE PRINCIPLE

**Before:** "AI decides everything — structure, layout, when to break pages, where to insert sections"  
**After:** "AI provides CONTENT ONLY. Template defines STRUCTURE. Injector does mechanical replacement."

Result: No more fragile dynamic rendering. No more test data leaks. One place to understand the entire report structure.

---

## WHAT THIS LOCKS

✅ **Page count** — Always 14 pages (fixed sections in fixed order)  
✅ **Section order** — Cover → Page 2 → Executive Summary → ... → Facilitator Notes  
✅ **Page layout** — No responsive sizing, no text wrapping that changes page count  
✅ **Signature consistency** — V8/Fd4/F4 appears on BOTH cover AND Page 2 (same source)  
✅ **Data provenance** — Every report traceable to original 24-question assessment  
✅ **No sample data** — Hardcoded test signatures rejected at validation layer  

---

## DECISION POINTS (Before Coding)

1. **Section count:** Are all 14 sections mandatory? Or is "Reflection / Full Profile Unlocks" optional?
2. **Narrative targets:** Should each section have word-count limits? Or fixed-height containers?
3. **Page count tolerance:** Exactly 14 pages or acceptable range (13-15)?
4. **Audit trail:** How strict on provenance tracking? (Log everything? Reject reports without ID?)
5. **Rollout:** Deploy Stage 1 template (read-only) while building Stages 2-3? Or wait for full system?

---

## RISK MITIGATION STRATEGY

| Risk | Mitigation |
|------|-----------|
| **Template complexity** | Start with copy of working report; systematically replace sections |
| **Placeholder collisions** | Use unique prefixes (e.g., `{{ SECTION_EXECUTIVE_SUMMARY }}` not `{{ TEXT }}`) |
| **JSON format mismatch** | generatePremiumMiniProfileV2 already outputs structured JSON; injector just normalizes it |
| **Regression in existing features** | Keep old renderers running in parallel during Stage 3; A/B test output |
| **Hardcoded sample data** | Smoke test suite that FAILS if V8/Fd4 found in production output |
| **Missing placeholders** | Validation that scans output for unreplaced `{{ PLACEHOLDER }}` strings |

---

## MEASURABLE OUTCOMES

When all 5 stages complete:

✅ One template file defines 100% of report structure  
✅ AI provides JSON, never HTML  
✅ Every report tied to source assessment (audit trail)  
✅ Sample signatures rejected by validation  
✅ Page count predictable (always 14)  
✅ Signature on cover matches signature on Page 2  
✅ Adding new section = add placeholder to template, nothing else  
✅ Debugging = check template, not scatter through 6 files  

---

## NEXT STEPS

1. **D.J. reviews** this plan (5 min read)
2. **D.J. answers decision points** (5 questions above)
3. **Rocky codes** Stage 1 (template design)
4. **Team verifies** Stage 1 before proceeding to Stage 2

**No files modified until approval.**

---

**Document:** `/Users/rrg/.openclaw/workspace/3PHASE_EXECUTIVE_SUMMARY.md`  
**Full Plan:** `/Users/rrg/.openclaw/workspace/MOREMINDMAP_3PHASE_STABILIZATION_PLAN.md`  
**Status:** ✅ READY FOR DECISION

**Time to code:** Awaiting approval + decision point answers
