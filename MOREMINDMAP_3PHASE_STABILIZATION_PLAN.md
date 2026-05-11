# MOREMindMap Mini Profile V2 — 3-Phase Stabilization Plan

**Status:** ANALYSIS ONLY (NO CODING YET)  
**Date:** Tue May 5, 2026 09:30 MST  
**Owner:** Rocky (Architect Mode)

---

## CORE STRATEGY

**From:** Patchwork dynamic rendering (AI controls layout, code patches structure)  
**To:** Template-first assembly (Fixed shell, AI provides content only)

This eliminates the cascading fragility where a change to one renderer breaks another, where dynamic page structure is scattered across multiple files, and where sample data (V8/Fd4/etc.) risks leaking into production.

---

## 3-PHASE ARCHITECTURE

### PHASE 1 — DESIGN TEMPLATE
**Objective:** Create one locked master template that defines COMPLETE document structure.

**What It Contains:**
```
TEMPLATE: Mini Profile V2 Master Shell
├── COVER (Page 1)
│   ├── Logo / Title
│   ├── Signature Line (placeholder)
│   ├── Core Edge paragraph (placeholder)
│   └── Assessment metadata
├── PAGE 2 (SVG System Map)
│   ├── Title / Subtitle
│   ├── SVG Container (fixed dimensions)
│   │   ├── 4 DNA nodes (Primary/Secondary/Opposing A/Opposing B)
│   │   ├── Tension lines
│   │   └── System Tension box
│   └── Page footer
├── PAGES 3-14 (Body Sections)
│   ├── Executive Summary
│   ├── Operating Pattern
│   ├── Decision Architecture
│   ├── Communication Style
│   ├── Under Pressure
│   ├── Blind Spots
│   ├── Friction Points
│   ├── Growth Edge
│   ├── Operating Environment Fit (3 cards)
│   ├── Facilitator Notes
│   ├── Recommended Next Step
│   └── Reflection / Full Profile Unlocks
└── STYLING (Fixed CSS)
    ├── Page dimensions (8.5" × 11")
    ├── Padding/margins
    ├── Typography (fonts, sizes, weights)
    ├── Print-safe page breaks
    └── No layout that changes per profile
```

**Key Constraint:** NO DYNAMIC PAGE STRUCTURE
- Page count is FIXED: always 14 pages (may vary by 1-2 if Reflection is optional)
- Section headers are FIXED: always appear in same order
- Container sizing is FIXED: no responsive layout, no text wrapping causing page drift
- Typography is FIXED: sizes, line-heights, margin never change

**Deliverable:** 
- `/templates/mini-profile-v2-master.html` (single source of truth for structure)
- Print-safe, fully styled, with `{{ PLACEHOLDER }}` markers for AI content injection

---

### PHASE 2 — CONTENT INJECTION
**Objective:** AI provides ONLY structured JSON content; template receives it via placeholders.

**What Changes:**
- No HTML generation from AI
- No dynamic page creation
- No renderer deciding "how many paragraphs fit on this page"
- Instead: **Structured JSON with exact content pieces**

**Input/Output Pattern:**

```javascript
// INPUT: Scoring data from 24-question assessment
{
  vector: 40,
  velocity: 15,
  fidelity: 20,
  framework: 20,
  leverage: 15,
  horizon: 10,
  signal: 5,
  flex: 5
}

// PROCESS 1: Normalize to 8-part signature
{
  vector: 8,      // 40 → 8
  velocity: 3,    // 15 → 3
  fidelity: 4,    // 20 → 4
  framework: 4,   // 20 → 4
  leverage: 3,    // 15 → 3
  horizon: 2,     // 10 → 2
  signal: 1,      // 5 → 1
  flex: 1         // 5 → 1
}

// PROCESS 2: Stage A & B AI pipeline returns JSON (GPT-4o-mini + GPT-5.5)
{
  // COVER
  signature: "V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1",
  coreEdge: "Your fundamental competitive edge...",
  
  // PAGE 2 SVG (already done, no change)
  svgData: {
    primary: { code: "V8", name: "Vector", description: "..." },
    secondary: { code: "Fd4", name: "Fidelity", description: "..." },
    opposingA: { code: "S1", name: "Signal", description: "..." },
    opposingB: { code: "Fx1", name: "Flex", description: "..." },
    coreEngine: "Vector-driven operating system...",
    systemTension: "Creates reliability. Reduces..."
  },
  
  // BODY SECTIONS (Stage B output - already GPT-5.5)
  sections: {
    executiveSummary: "Your behavioral operating system is led by command...",
    operatingPattern: "Your default operating pattern centers on control...",
    decisionPattern: "Your decision pattern is fast, directive...",
    communicationStyle: "Your communication style is direct...",
    underPressure: "Under pressure, your system becomes more assertive...",
    blindSpots: "Your blind spots sit around adaptability...",
    frictionPoints: "Friction arises when your need for direction...",
    growthEdge: "Your growth edge is the integration of...",
    facilitatorNotes: "A coach or facilitator working with this profile...",
    recommendedNextStep: "The single most valuable next action...",
    coreEdgeExpanded: "Your fundamental competitive edge is...",
    whatFullProfileUnlocks: "A deeper profile unlocks the finer mechanics..."
  },
  
  // OPERATING ENVIRONMENT FIT (already dynamic, structured output)
  environments: {
    traction: [
      { environment: "Systems rewarding precision...", rationale: "...precision and structural control reward..." },
      // 3 more...
    ],
    conditional: [ /* 4 environments */ ],
    friction: [ /* 4 environments */ ]
  }
}

// TEMPLATE: Master shell with placeholders
<html>
  <div class="page cover">
    <div class="signature">{{ SIGNATURE }}</div>
    <div class="core-edge">{{ CORE_EDGE }}</div>
  </div>
  
  <div class="page system-map">
    {{ SVG_PAGE_2 }}
  </div>
  
  <div class="page executive-summary">
    <h2>Executive Summary</h2>
    <div>{{ SECTIONS.EXECUTIVE_SUMMARY }}</div>
  </div>
  
  <!-- etc for all sections -->
</html>

// OUTPUT: Final HTML (placeholder replacement)
```

**Key Constraint:** Template injection is ONLY text replacement
- `{{ SIGNATURE }}` → "V8 • Fd4 • F4..."
- `{{ SECTIONS.EXECUTIVE_SUMMARY }}` → GPT-5.5 output paragraph
- No conditional logic in template
- No "if field exists, show it" branching
- No optional sections

**Deliverable:**
- Update `/engine/generatePremiumMiniProfileV2.js` to return structured JSON (it already does most of this)
- Create new `/engine/miniProfileV2Injector.js` that takes JSON + template and returns final HTML
- ALL logic moves to: "Given these scores and these narratives, what is the placeholder replacement?"

---

### PHASE 3 — TRUE DATA POPULATION LOCK
**Objective:** NO hardcoded test data. Every report derives from actual 24-question assessment.

**Current Risk:**
- Test profile (V8, Fd4, F4, Vl3, L3, H2, S1, Fx1) is hardcoded in test fixtures
- Risk: Someone accidentally deploys test template with test signature
- Risk: Devs confuse test output with real data

**What Gets Locked:**
1. **Never hardcode a signature in production**
   - Every signature MUST come from scoreAssessment(responses)
   - Reject any request without valid 24-question payload
   - Return error if scores cannot be normalized to 8-part code

2. **Never hardcode narratives**
   - Every narrative section MUST come from Stage A (analyst) + Stage B (writer)
   - No default/fallback text in template
   - No demo sections
   - Reject any report if AI pipeline incomplete

3. **Audit Trail: Track Source**
   - Report object logs: `derivedFrom: "assessment_uuid"`
   - Assessment payload stored (or reference to it)
   - If report regenerated, re-verify same assessment produced it

4. **API Validation**
   - `/api/mini-profile-v2/generate` requires:
     - `assessmentId` (exists in DB)
     - `responses[]` (24 items, valid answer types)
   - Returns error if missing either
   - Refuses to use fallback/default data

**Deliverable:**
- Update `/routes/miniProfileV2Routes.js` with strict validation
- Add assessment source tracking to report object
- Add smoke test that rejects hardcoded signatures

---

## CURRENT FILES INVOLVED

### Core Orchestrators
1. **`/engine/generatePremiumMiniProfileV2.js`** (210 lines)
   - Takes 24 scores → outputs structured JSON (codes, narratives, systemMap, etc.)
   - Already structured, but needs slight refactor to separate JSON from rendering
   - **Status:** ~80% correct format already

2. **`/jobs/generateMiniReportV2Job.js`**
   - Async orchestrator that calls V2 generator
   - **Status:** Thin wrapper, mostly fine

3. **`/routes/miniProfileV2Routes.js`**
   - API endpoint handler
   - **Status:** Needs validation layer

### Renderers (Current Patchwork)
4. **`/utils/page2IntegratedRenderer.js`** (370 lines)
   - Calls frontend HTML generator
   - Injects SVG Page 2
   - Inserts Operating Environment Fit
   - **Problem:** Dynamic, multiple integration points, fragile

5. **`/utils/htmlRendererAdapter.js`**
   - Routes to frontend renderer or fallback
   - **Problem:** Multiple renderers create duplication

6. **`/utils/page2SvgEngine.js`** (100 lines)
   - SVG injection logic
   - **Status:** Good, but currently scattered

### SVG & Templates
7. **`/templates/page2_master.svg`** (260 lines)
   - SVG template with placeholders
   - **Status:** Good, just needs consistent loading

### Frontend HTML Generator (Outside Backend)
8. **`~/moremindmap/utils/htmlRendererV5-PassA-Fixed.js`** (650 lines)
   - Currently generates full HTML structure dynamically
   - Calls `generateSignatureCodes()`, `generateCoverPageV1()`, `generateOperatingSystemMapPageV1()`, etc.
   - **Problem:** This IS the source of dynamic page structure

---

## IDENTIFIED RISKS

### Risk 1: Multiple HTML Generators
**Current State:**
- Backend calls frontend's `htmlRendererV5-PassA-Fixed.js`
- Frontend also has its own rendering logic
- If signature changes, must update both places

**Risk:** Version skew, duplicate code, test data leaks

**Mitigation (Phase 1):** Consolidate to single template

---

### Risk 2: SVG Page 2 Placement
**Current State:**
- `stripLegacyPage2()` removes old page structure (assumes certain HTML)
- `embedSvgPage2()` inserts SVG (fragile regex)
- If frontend HTML structure changes, insertion breaks

**Risk:** SVG disappears or inserts in wrong location

**Mitigation (Phase 1):** SVG is fixed template section, not dynamically injected

---

### Risk 3: Operating Environment Fit Integration
**Current State:**
- Generated separately, inserted via string replacement
- If section structure changes, insertion point breaks

**Risk:** Environment section appears twice or not at all

**Mitigation (Phase 1):** Environment section is fixed template placeholder

---

### Risk 4: Narrative Word Count / Length Variability
**Current State:**
- AI outputs vary in length (3,500–4,000+ words possible)
- Page wrapping changes based on exact word count
- Hard to predict final page count

**Risk:** Report becomes 15 pages instead of 14, breaks print assumptions

**Mitigation (Phase 1):** All sections have FIXED height in template (overflow handling)

---

### Risk 5: Sample Data Hardcoding
**Current State:**
- Test fixtures contain hardcoded V8/Fd4/F4 signature
- Test narratives are thin mock content
- Risk: Someone deploys test template as production

**Risk:** Real customers get sample profile

**Mitigation (Phase 3):** Strict validation, never accept report without valid assessment source

---

### Risk 6: Renderer File Sprawl
**Current State:**
- `page2IntegratedRenderer.js` (370 lines)
- `htmlRendererAdapter.js`
- `page2SvgEngine.js`
- `htmlRendererV5-PassA-Fixed.js` (frontend, 650 lines)
- Multiple `generateX()` functions scattered

**Risk:** Hard to find where signature appears, where page structure defined, what controls layout

**Mitigation (Phase 1):** Consolidate to template + single injector

---

## IMPLEMENTATION ROADMAP (SAFEST ORDER)

### Stage 1: Design Template (Foundation)
**Goal:** Create `/templates/mini-profile-v2-master.html` with ALL section structure locked

**Steps:**
1. Copy current working report HTML structure
2. Verify all 14 pages are present and properly formatted
3. Replace dynamic content with `{{ PLACEHOLDER }}` markers
4. Lock all CSS to fixed sizes (no responsive, no wrapping)
5. Add comments marking each placeholder
6. **Create visual diagram** showing page flow and placeholders
7. **Manual review:** Verify template renders with sample placeholder text

**Time:** 2-3 hours  
**Risk:** LOW (Read-only, no logic changes)  
**Deliverable:** `/templates/mini-profile-v2-master.html`

---

### Stage 2: Create Injector (Glue Layer)
**Goal:** Build `/engine/miniProfileV2Injector.js` that takes JSON + template and returns HTML

**Steps:**
1. Read template file
2. Accept JSON from generatePremiumMiniProfileV2
3. Implement placeholder replacement:
   ```javascript
   html = html.replace('{{ SIGNATURE }}', json.signature)
   html = html.replace('{{ SECTIONS.EXECUTIVE_SUMMARY }}', json.sections.executiveSummary)
   // ... etc for all placeholders
   ```
4. Validate all placeholders replaced (no `{{ MISSING }}` in output)
5. Return final HTML
6. **No page breaking logic, no rendering decisions**

**Time:** 1-2 hours  
**Risk:** LOW (Straightforward string replacement)  
**Deliverable:** `/engine/miniProfileV2Injector.js`

---

### Stage 3: Wire Injector (Integration)
**Goal:** Replace current renderer with new template injector

**Steps:**
1. Update `/routes/miniProfileV2Routes.js`:
   - Receive 24-question responses (validate)
   - Call scoreAssessment() → raw scores
   - Call generatePremiumMiniProfileV2() → structured JSON
   - Call miniProfileV2Injector(template, json) → final HTML
   - Return HTML
2. Delete/deprecate old `page2IntegratedRenderer.js` logic
3. Test with multiple profiles to verify output
4. **Add unit tests** for placeholder injection
5. **Add integration test** that confirms no V8/Fd4/F4 hardcoding

**Time:** 2-3 hours  
**Risk:** MEDIUM (Integration point, but test coverage helps)  
**Deliverable:** Updated routes, deprecated old renderers

---

### Stage 4: Validation & Audit (Data Lock)
**Goal:** Ensure no sample data reaches production

**Steps:**
1. Add `derivedFrom` field to report object (links to assessment ID)
2. Add validation: reject reports without valid assessment source
3. Create smoke test:
   ```javascript
   // Test should FAIL if signature is hardcoded
   report = generateReport(emptyAssessment)
   assert(report.signature !== "V8 • Fd4 • F4...")
   ```
4. Add request logging: log all generated reports with source assessment
5. Create audit script to find hardcoded signatures in output
6. **Document:** "How to verify a report came from real assessment"

**Time:** 1-2 hours  
**Risk:** LOW (Validation, no rendering changes)  
**Deliverable:** Validation layer + audit tools

---

### Stage 5: Cleanup & Documentation
**Goal:** Remove old renderer code, document new system

**Steps:**
1. Delete deprecated functions from old renderer files
2. Add comments to template marking placeholder purposes
3. Create `/docs/mini-profile-v2-template-architecture.md`
4. Create `/docs/adding-new-sections.md` (how to add a new placeholder)
5. Create `/docs/debugging-v2-reports.md` (troubleshooting guide)

**Time:** 1 hour  
**Risk:** NONE (Cleanup only)  
**Deliverable:** Documentation

---

## TIMELINE SUMMARY

| Phase | Files | Time | Risk | Blocker? |
|-------|-------|------|------|----------|
| Stage 1: Design Template | `mini-profile-v2-master.html` | 2-3h | LOW | NO |
| Stage 2: Create Injector | `miniProfileV2Injector.js` | 1-2h | LOW | Stage 1 |
| Stage 3: Wire Injector | `/routes/miniProfileV2Routes.js` | 2-3h | MEDIUM | Stage 2 |
| Stage 4: Validation | `/engine/auditV2Reports.js` | 1-2h | LOW | Stage 3 |
| Stage 5: Cleanup | docs + deprecation | 1h | NONE | Stage 4 |
| **TOTAL** | **5 files** | **7-11h** | **Managed** | **None** |

---

## KEY DECISIONS (Locked)

1. **Template is FIXED source of truth** → No renderer invents page structure
2. **AI provides JSON, not HTML** → No HTML generation, no layout control
3. **All sections have FIXED placeholders** → No optional sections, no conditional rendering
4. **No hardcoded test data in production** → Strict validation, audit trail
5. **Single template file** → One place to understand report structure
6. **Placeholder replacement only** → No rendering logic in injector

---

## WHAT DOES NOT CHANGE (Guardrails)

- ✅ Signature scoring logic (Vector, Velocity, etc. normalization)
- ✅ Page 2 SVG template (fixed, just needs to inject codes)
- ✅ Stage A analyst logic (GPT-4o-mini)
- ✅ Stage B writer logic (GPT-5.5)
- ✅ Operating Environment Fit matching engine
- ✅ Current CSS/typography/colors

---

## QUESTIONS FOR D.J.

Before coding begins:

1. **Section Count Lock:** Are all 14 sections fixed? Or can "Reflection / Full Profile Unlocks" be optional?

2. **Narrative Word Count:** Should each section have a target word count (e.g., Executive Summary 200-300 words)? Or fixed-height container?

3. **Page Count:** Is exactly 14 pages the target? Or acceptable range (13-15)?

4. **Placeholder Naming:** Preference for placeholder style?
   - `{{ SIGNATURE }}`
   - `{{ signature }}`
   - `{{ section_executive_summary }}`
   - Other?

5. **Assessment Source Tracking:** How strict on audit trail?
   - Log every generated report?
   - Reject reports without assessment ID?
   - Store assessment payload in DB?

6. **Rollout:** Once Phase 1 template is locked, can we deploy just that (read-only) while building Phases 2-3? Or all-or-nothing?

---

**Status:** Analysis complete. Ready for coding once decisions confirmed.

**Next Action:** D.J. reviews, confirms constraints, approves implementation order.

**No files modified.** All changes staged for approval.

---

**Document:** `/Users/rrg/.openclaw/workspace/MOREMINDMAP_3PHASE_STABILIZATION_PLAN.md`  
**Created:** Tue May 5, 2026 09:30 MST  
**Version:** 1.0 (Analysis Only)
