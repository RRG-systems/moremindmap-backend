# PAGE 2 SVG TEMPLATE SYSTEM ARCHITECTURE

**Status:** ✅ PRODUCTION READY  
**Date:** Mon 2026-05-04 16:46 MST

---

## OVERVIEW

Page 2 (Behavioral Operating System Map) has been converted from HTML/CSS layout to a fixed SVG template system.

**Why:** HTML/CSS layouts drift during render/print. SVG is pixel-stable and print-stable.

**Result:** Instrument-grade visual asset that produces identical output every time.

---

## SYSTEM COMPONENTS

### 1. SVG Template (`/templates/page2_master.svg`)

**Size:** 7.0 KB  
**Dimensions:** 816 × 1056 (standard letter format)  
**Format:** XML with embedded styles

**Contents:**
- Header (MORE MINDMAP, title, subtitle, breadcrumb)
- Layout divider
- Orbit ring (structural boundary)
- 4 connector lines (primary, secondary, opposing A, opposing B)
- 5 nodes (primary, secondary, opposingA, opposingB, center engine)
- Diagnostic text blocks (3 sides + bottom)
- Tension labels (2)
- System tension box with legend
- Footer

**Template Markers:** 27 `{{PLACEHOLDER}}` markers for dynamic injection

**Layout Control:** Pure SVG (no HTML, no flex, no grid)

---

### 2. Injection Engine (`/utils/page2SvgEngine.js`)

**Function:** `renderPage2Svg(systemMapData)`

**Input:**
```javascript
{
  primary: { code, name, description },
  secondary: { code, name, description },
  opposingA: { code, name, description, tension },
  opposingB: { code, name, description, tension },
  coreEngine: string,
  systemTension: string
}
```

**Process:**
1. Load template as string
2. Prepare data (escape XML, word-wrap text)
3. Replace 27 placeholders with dynamic values
4. Return completed SVG string

**Text Handling:**
- XML escaping: `&`, `<`, `>`, `"`, `'` → safe entities
- Word wrapping: Break on spaces, max 35-50 chars per line
- Multiline support: Up to 3 lines per description

**Performance:** Instant (sub-millisecond)

---

### 3. Integrated Renderer (`/utils/page2IntegratedRenderer.js`)

**Function:** `generateV1MiniProfileHTML(v2Output)`

**Process:**
1. Extract scores and narrative from V2 pipeline
2. Generate frontend HTML (pages 1, 3+)
3. Build system map data from profile
4. Render Page 2 SVG via injection engine
5. Embed SVG into HTML report
6. Return complete HTML file

**Data Flow:**
```
v2Output (Stage A + B) 
  → Frontend HTML (Pages 1, 3+)
  → System Map Data (codes, names, diagnostics)
  → SVG Render (template + injection)
  → HTML Embedding (page-break styling)
  → Final Report HTML
```

---

### 4. Adapter (`/utils/htmlRendererAdapter.js`)

**Main Entry Point:** `generateHTMLFromV2Output(v2Output)`

Routes to integrated renderer.

Used by: `/engine/generatePremiumMiniProfileV2.js` job handler

---

## DATA MAPPING

### Profile → System Map

Profile scores (0-100) are normalized and mapped to system map:

```javascript
scores = {
  fidelity: 72,    // 0-100
  horizon: 48,
  signal: 15,
  flex: 12
}

// Normalize to 1-9 scale
normalized = {
  fidelity: 7,     // 70-79 range → 7
  horizon: 5,      // 40-49 range → 5
  signal: 2,       // 10-19 range → 2
  flex: 1          // 10-19 range → 1
}

// Create codes
code_fidelity = "Fd" + "7" = "Fd7"
code_horizon = "H" + "5" = "H5"
code_signal = "S" + "2" = "S2"
code_flex = "Fx" + "1" = "Fx1"

// Map to system roles
primary = fidelity (highest)
secondary = horizon (second highest)
opposingA = signal (lowest)
opposingB = flex (second lowest)
```

### Template Placeholders

| Placeholder | Source | Notes |
|------------|--------|-------|
| `{{PRIMARY_CODE}}` | `code_fidelity` | e.g., "Fd7" |
| `{{PRIMARY_NAME}}` | Capitalized dim | "Fidelity" |
| `{{PRIMARY_DESC_1-3}}` | diagnostic text, wrapped | 3 lines, ~35 chars max |
| `{{SECONDARY_CODE}}` | `code_horizon` | "H5" |
| `{{SECONDARY_NAME}}` | "Horizon" | |
| `{{SECONDARY_DESC_1-3}}` | diagnostic text | |
| `{{OPPOSING_A_CODE}}` | `code_signal` | "S2" |
| `{{OPPOSING_A_NAME}}` | "Signal" | |
| `{{OPPOSING_A_DESC_1-3}}` | diagnostic text | |
| `{{TENSION_A_1-2}}` | "Precision > Relational Awareness", wrapped | |
| `{{OPPOSING_B_CODE}}` | `code_flex` | "Fx1" |
| `{{OPPOSING_B_NAME}}` | "Flex" | |
| `{{OPPOSING_B_DESC_1-3}}` | diagnostic text | |
| `{{TENSION_B}}` | "Precision > Adaptability" | Single line |
| `{{CORE_LINE_1-2}}` | Core engine text, wrapped | ~30 chars max |
| `{{SYSTEM_TENSION_1-2}}` | System tension text, wrapped | ~55 chars max |

---

## LAYOUT SPECIFICATION

### Coordinate System (SVG viewBox: 0 0 816 1056)

**Vertical Zones:**
- 0-125: Header + divider
- 160-900: Diagram (nodes, connectors, diagnostics)
- 950-1020: System tension box
- 1045+: Footer

**Horizontal Center:** 408 (816/2)

**Nodes (Diagram Zone):**
- Primary (top): cx=408, cy=230, r=50
- Secondary (right): cx=680, cy=530, r=45
- Opposing A (left): cx=135, cy=530, r=45
- Opposing B (bottom): cx=408, cy=830, r=45
- Center Engine: cx=408, cy=530, r=65

**Orbit Ring:**
- Center: cx=408, cy=530
- Radius: 140
- Stroke: #6b7280, 2.5px, dashed, opacity 0.9

**Connectors (SVG lines):**
- Top→Center: x1=408 y1=230 → x2=408 y2=370
- Right→Center: x1=525 y1=530 → x2=680 y2=530
- Left→Center: x1=290 y1=530 → x2=135 y2=530
- Bottom→Center: x1=408 y1=690 → x2=408 y2=830

**Descriptions (Text Blocks):**
- Primary: x=760, y=210/227/244 (top-right)
- Secondary: x=745, y=460/477/494 (right side)
- Opposing A: x=71, y=460/477/494, text-anchor=end (left side, right-aligned)
- Opposing B: x=480, y=770/787/804 (bottom)

**Tensions:**
- Left: x=240, y=505/522/539 (2 lines)
- Bottom: x=408, y=745 (1 line)

---

## VISUAL CHARACTERISTICS

### Colors
- Navy: #0f172a (primary, center border, text)
- Gold: #b8860b (labels, accents, left border of tension box)
- Blue: #2c5aa0 (secondary node)
- Light Gray: #d1d5db (opposing nodes)
- Dark Gray: #6b7280 (orbit ring)
- Connector Gray: #374151
- Tension Gray: #1f2937
- Background: white, #fafafa (tension box)
- Divider: #0f172a, 2.5px

### Typography
- Font: Inter (fallback: Arial, sans-serif)
- Header logo: 11px, 700 weight, gold, letter-spacing 1.5
- Title: 28px, 700 weight, navy
- Subtitle: 11px, 666
- Node codes: 15px (primary), 14px (others), 700, white (or navy for opposing)
- Node labels: 8px, 800, gold, uppercase, letter-spacing 1.2
- Node names: 13px, 700, navy
- Descriptions: 10px, 444
- Tensions: 8px, 700, #1f2937
- Center label: 8px, 700, gold, uppercase
- Center text: 11px, 800, navy
- System tension title: 9px, 800, gold, uppercase
- System tension text: 9px, 333
- Footer: 9px, 999, letter-spacing 0.5

---

## INTEGRATION POINTS

### Upstream (Unchanged)
- `generatePremiumMiniProfileV2.js` — Stage A/B pipeline, produces v2Output
- `htmlRendererV5-PassA-Fixed.js` — Frontend HTML (pages 1, 3+)

### Entry Point
- `htmlRendererAdapter.js` — Called by job handler with v2Output
- Routes to `page2IntegratedRenderer.js`

### Output
- Complete HTML file with embedded SVG Page 2
- Single page break before Page 2 SVG
- SVG renders one full letter page

---

## CONSTRAINTS & RULES

✅ **Pixel Stability:** All coordinates absolute (SVG, no flow)  
✅ **Print Stability:** One-page fit, standard letter dimensions  
✅ **Text Safety:** XML escaping on all dynamic text  
✅ **No Score Leaks:** Only profile-derived diagnostic text injected  
✅ **No Placeholders:** 100% replacement verification  
✅ **No Layout Drift:** SVG geometry locked, not responsive  
✅ **Performance:** Instant render (no recalc)  
✅ **Unchanged Upstream:** Stage A, Stage B, frontend HTML untouched  

---

## DEPLOYMENT CHECKLIST

- [x] SVG template created and locked
- [x] Injection engine tested
- [x] Integrated renderer tested
- [x] Final report generated and verified
- [x] No placeholders remaining
- [x] No score leaks
- [x] One-page fit confirmed
- [x] Visual match to reference verified

**Status:** ✅ READY FOR PRODUCTION

---

## TESTING REPORT

**Final Test:** 2026-05-04T23:46:24Z

**Report File:** `mini-profile-v2-svg-page2-2026-05-04T23-46-24-718Z.html`

**Generation Stats:**
- Stage A: 6.1s
- Stage B: 117.4s
- SVG Render: Instant
- **Total:** 123.5s

**Content:**
- Narrative: 3,959 words
- "may" count: 0 ✅
- Score leaks: 0 ✅

**Verification:**
- SVG embedded: ✅
- Placeholders remaining: 0 ✅
- Page break styling: ✅
- File size: 43.1 KB

---

## NEXT PHASES

### Phase 2B: Frontend Integration
- Wire form submission to V2 endpoint
- Add job status polling
- Add download/share UI
- Use same SVG Page 2 system

### Phase 3: Production Infrastructure
- Bull/Redis for job queue
- Rate limiting (1 report/user/hour)
- Report archival (7-day cleanup)
- Same SVG Page 2 system

---

**Architecture Locked**

All components tested and verified. System ready for deployment.
