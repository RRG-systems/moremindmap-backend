# BEFORE vs AFTER: Architecture Comparison

## CURRENT STATE (Patchwork, Fragile)

```
┌─────────────────────────────────────────────────────────────────┐
│ 24 QUESTION ASSESSMENT                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ scoreAssessment() — Raw Scores                                  │
│ (vector: 40, velocity: 15, fidelity: 20, ...)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ generatePremiumMiniProfileV2() — Structured Data               │
│ (codes, narratives, systemMap, environments)                   │
└────────────────────────┬────────────────────────────────────────┘
                         │
              ┌──────────┴──────────┐
              │                     │
              ▼                     ▼
    ┌──────────────────┐   ┌──────────────────┐
    │ htmlRendererV5   │   │ page2Integrated  │
    │ (Frontend)       │   │ Renderer         │
    │                  │   │ (Backend)        │
    └────────┬─────────┘   └────────┬─────────┘
             │                     │
             │  Generates HTML     │
             │  dynamically        │  Strips old
             │  (layout control)   │  page, injects
             │                     │  SVG, inserts
             │                     │  environment
             │                     │
             └──────────┬──────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │ Fragmented HTML Output   │
            │ (Page structure varies)  │
            │ (SVG position fragile)   │
            │ (Test data mixed with    │
            │  real narratives)        │
            └──────────────────────────┘
                        │
                        ▼
            ┌──────────────────────────┐
            │ Report (inconsistent)    │
            │ 🚨 V8/Fd4 might be      │
            │   hardcoded in sample   │
            └──────────────────────────┘

PROBLEMS:
  ❌ HTML generation scattered across 2 files
  ❌ Layout decisions made by code (page wrapping, section timing)
  ❌ SVG insertion is fragile (regex-based)
  ❌ Environment section integration point fragile
  ❌ Test signatures can leak to production
  ❌ Multiple page structure generators (hard to debug)
  ❌ Sample narratives mixed with real AI content
```

---

## AFTER STATE (Template-First, Solid)

```
┌─────────────────────────────────────────────────────────────────┐
│ 24 QUESTION ASSESSMENT                                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ scoreAssessment() — Raw Scores                                  │
│ (vector: 40, velocity: 15, fidelity: 20, ...)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ generatePremiumMiniProfileV2() — Structured JSON               │
│ {                                                               │
│   signature: "V8 • Fd4 • F4...",                              │
│   sections: { executiveSummary: "Your behavioral...", ... },  │
│   svgData: { primary, secondary, opposingA, opposingB, ... }, │
│   environments: { traction, conditional, friction }           │
│ }                                                               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ VALIDATION LAYER (NEW)                                           │
│ - Verify assessmentId valid                                     │
│ - Reject if signature is hardcoded test value (V8/Fd4/F4...)   │
│ - Require all narrative sections present                         │
│ - Check JSON structure complete                                 │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ MASTER TEMPLATE (LOCKED, NEW)                                    │
│ /templates/mini-profile-v2-master.html                          │
│                                                                  │
│ <div class="page cover">                                        │
│   <div class="signature">{{ SIGNATURE }}</div>                  │
│ </div>                                                          │
│                                                                  │
│ <div class="page system-map">                                  │
│   {{ SVG_PAGE_2 }}                                             │
│ </div>                                                          │
│                                                                  │
│ <div class="page executive-summary">                           │
│   {{ SECTIONS_EXECUTIVE_SUMMARY }}                             │
│ </div>                                                          │
│                                                                  │
│ <!-- 11 more fixed sections -->                                │
│                                                                  │
│ ✅ NO LAYOUT LOGIC                                             │
│ ✅ FIXED STRUCTURE                                             │
│ ✅ ONLY PLACEHOLDERS                                           │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│ INJECTOR (NEW)                                                   │
│ /engine/miniProfileV2Injector.js                                │
│                                                                  │
│ function inject(template, jsonData) {                           │
│   html = template                                               │
│   html = html.replace('{{ SIGNATURE }}', jsonData.signature)   │
│   html = html.replace(                                         │
│     '{{ SECTIONS_EXECUTIVE_SUMMARY }}',                        │
│     jsonData.sections.executiveSummary                         │
│   )                                                             │
│   // ... replace all placeholders                              │
│   return html  // DONE                                         │
│ }                                                               │
└────────────────────────┬──────────────────────────────────────────┘
                         │
                         ▼
            ┌──────────────────────────────────┐
            │ Final HTML                       │
            │ ✅ Fixed structure (14 pages)    │
            │ ✅ Signature consistent          │
            │ ✅ SVG in right place            │
            │ ✅ Environment section correct   │
            │ ✅ Real AI-generated content     │
            │ ✅ Traced to assessment ID       │
            └──────────────────────────────────┘
                         │
                         ▼
            ┌──────────────────────────────────┐
            │ Report (predictable, solid)      │
            │ ✅ No hardcoded test data        │
            │ ✅ Always 14 pages               │
            │ ✅ Data provenance tracked       │
            └──────────────────────────────────┘

BENEFITS:
  ✅ Single template = single source of truth for structure
  ✅ Template is locked (non-code file)
  ✅ AI provides JSON (no layout control)
  ✅ Injector is mechanical (no logic, just replacement)
  ✅ Validation layer prevents test data in production
  ✅ Page structure predictable (always 14)
  ✅ SVG insertion = template placeholder (not fragile regex)
  ✅ Environment section = template placeholder (not string replacement)
  ✅ Adding new section = add placeholder to template (clear process)
  ✅ Debugging = look at template + JSON (clear separation)
```

---

## KEY DIFFERENCES

### Structure Definition

| Aspect | BEFORE | AFTER |
|--------|--------|-------|
| Where defined? | Scattered across 6 files | Single template file |
| Page order | Implicit in renderer logic | Explicit in template |
| Section headers | Generated by code | Fixed in template |
| Page count | Varies (content-dependent) | Fixed (14 always) |
| New section added | Modify 3 files | Add placeholder to template |

### Content Flow

| Aspect | BEFORE | AFTER |
|--------|--------|-------|
| AI output | HTML (page-aware) | JSON (structure-agnostic) |
| Layout decisions | Made by renderer | Pre-locked in template |
| SVG insertion | Dynamic regex stripping | Template placeholder |
| Environment section | String replacement | Template placeholder |
| Page breaking | Runtime logic | CSS in template |

### Data Safety

| Aspect | BEFORE | AFTER |
|--------|--------|-------|
| Test data | Can leak to production | Rejected by validation |
| Signature provenance | Not tracked | Tied to assessment ID |
| Hardcoded samples | V8/Fd4 in test fixtures | Smoke test catches it |
| Report audit trail | None | Assessment source logged |

### Debugging

| Aspect | BEFORE | AFTER |
|--------|--------|-------|
| "Where does signature appear?" | Search 6 files | Look at template |
| "Why is page 2 missing?" | Debug regex stripping | Check template has SVG placeholder |
| "Why are sections out of order?" | Trace renderer code | Check template order |
| "Is content hardcoded?" | Grep for sample values | Validation layer rejects it |

---

## TRANSITION PATH

```
STAGE 1: Build template (parallel to current system)
├─ No code changes
├─ Create master.html with all structure locked
└─ Verify with manual content replacement

STAGE 2: Build injector (parallel to current system)
├─ New file, no modifications to existing
├─ Test independently with mock JSON
└─ Verify all placeholders replaced

STAGE 3: Wire injector (replace current system)
├─ Gradual: Route new requests to injector
├─ A/B test: Injector vs old renderer output
├─ Rollback possible if issues
└─ Deprecate old renderers once validated

STAGE 4: Validation layer (lock down data)
├─ Add assessment source tracking
├─ Reject hardcoded signatures
└─ Enable audit trail

STAGE 5: Cleanup (remove old code)
├─ Delete deprecated renderer files
├─ Document new architecture
└─ Done

RISK AT EACH STAGE:
1️⃣  LOW (read-only)
2️⃣  LOW (isolated new file)
3️⃣  MEDIUM (but mitigated with A/B testing)
4️⃣  LOW (validation layer)
5️⃣  NONE (cleanup)
```

---

## CONCRETE EXAMPLE

### BEFORE (Fragile)

```javascript
// Frontend renderer generates:
const html = generateCoverPageV1(profile)
            + generateOperatingSystemMapPageV1(profile)
            + generateNarrativePagesV1(narratives)
            + generateWorksheetPrompts(narratives)

// Backend then:
let html = htmlFromFrontend
html = stripLegacyPage2(html)  // 🚨 Fragile regex
html = embedSvgPage2(html, svgContent)  // 🚨 Insertion point fragile
html = insertEnvironmentSection(html, envSection)  // 🚨 String replacement

// Result: V8/Fd4 test signature can appear in output
```

### AFTER (Solid)

```javascript
// Data preparation:
const jsonData = await generatePremiumMiniProfileV2(scores)
validateAssessmentSource(jsonData)  // 🛡️ Reject test data

// Template rendering:
const template = await fs.readFile('/templates/mini-profile-v2-master.html')
const html = inject(template, jsonData)  // Pure string replacement

// Result: V8/Fd4 in test fixtures CANNOT reach production (validation rejects it)
```

---

**This comparison shows:** Patchwork system (fragile, scattered logic) → Template-first system (locked structure, mechanical replacement)

The gain: **Predictability, auditability, and data safety.**
