# MOREMINDMAP PAGE 2 DNA + BODY WRAPPER FIXES

**Task:** Fix two critical issues with Mini Profile V2 report generation.

---

## ISSUE 1: PAGE 2 DNA SOURCE IS WRONG ✓ DIAGNOSED

### Problem
- **Cover shows:** V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1 ✅
- **Page 2 currently shows:** Fd1 / H1 / S1 / Fx1 ❌

### Root Cause
**Frontend signature is correct, backend Page 2 is using fresh normalized scores instead of the same scores used for the cover.**

**Trace:**
1. Frontend (`htmlRendererV5-PassA-Fixed.js`, line ~369 in `generateCoverPageV1()`)
   - Calls `generateSignatureCodes(scores)` from `profile.aiRefinedScores`
   - Creates codes object with all 8 dimensions normalized 1-9
   - **Hardcoded example shows:** `V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1`
   - This is the source of truth

2. Backend (`page2IntegratedRenderer.js`, line ~48 in `generateV1MiniProfileHTML()`)
   - Receives `v2Output` from dual-stage pipeline
   - Calls `buildSystemMapData(v2Output.scoring?.normalizedScores || {})`
   - ❌ Problem: This uses fresh normalized scores, NOT the same ones frontend used
   - Result: Primary, Secondary, Opposing ranks are computed from different data

### Solution: Wire the Same Signature Object

**Backend page2IntegratedRenderer.js:**
- Don't recalculate from fresh scores
- Instead: Extract the final 8-part signature codes from frontend's renderPayload
- Or: Pass the finalized codes object from v2Output through the pipeline

**Two approaches:**

**Approach A (Recommended): Add codes field to v2Output**
- In `generatePremiumMiniProfileV2.js` (backend), the orchestrator already computes codes
- Add codes to output: `output.codes` ← already exists! (line ~152)
- In `page2IntegratedRenderer.js`, use: `v2Output.codes` instead of recalculating

**Approach B: Have frontend pass codes**
- Frontend already has codes from `generateSignatureCodes()`
- Pass to backend via renderPayload
- Backend uses renderPayload.codes instead of recalculating

### Implementation: Approach A (Codes Already Exist in v2Output)

**File: `/Users/rrg/moremindmap-backend/utils/page2IntegratedRenderer.js`**

**Change line ~48:**
```javascript
// BEFORE: Recalculating from fresh scores
const systemMapData = buildSystemMapData(v2Output.scoring?.normalizedScores || {})

// AFTER: Use codes already computed in v2Output
const systemMapData = buildSystemMapDataFromCodes(v2Output.codes || {}, v2Output.scoring?.normalizedScores || {})
```

**Add new function:** `buildSystemMapDataFromCodes()`
```javascript
function buildSystemMapDataFromCodes(codesObj, normalizedScores) {
  // codesObj is already the final 8-part signature codes from generatePremiumMiniProfileV2
  // Format: { vector: {code: "V", normalized: 8}, fidelity: {code: "Fd", normalized: 4}, ... }
  
  const dims = ["vector", "velocity", "fidelity", "framework", "leverage", "horizon", "signal", "flex"]
  const scores = {}
  
  dims.forEach(dim => {
    scores[dim] = normalizedScores[dim] || 0
  })

  // Sort by normalized score (using codes[dim].normalized)
  const sorted = [...dims].sort((a, b) => (codesObj[b]?.normalized || 0) - (codesObj[a]?.normalized || 0))

  // Extract Primary, Secondary, Opposing using SAME codes as frontend
  const primaryDim = sorted[0]
  const secondaryDim = sorted[1]
  const opposingADim = sorted[6]
  const opposingBDim = sorted[7]

  const primaryNorm = codesObj[primaryDim]?.normalized || 0
  const secondaryNorm = codesObj[secondaryDim]?.normalized || 0
  const opposingANorm = codesObj[opposingADim]?.normalized || 0
  const opposingBNorm = codesObj[opposingBDim]?.normalized || 0

  // Return systemMapData using EXACT same values as frontend's signature codes
  return {
    primary: {
      code: `${codesObj[primaryDim]?.code || "V"}${primaryNorm}`,
      name: capitalizeKey(primaryDim),
      description: getDimensionDescription(primaryDim),
    },
    secondary: {
      code: `${codesObj[secondaryDim]?.code || "F"}${secondaryNorm}`,
      name: capitalizeKey(secondaryDim),
      description: getDimensionDescription(secondaryDim),
    },
    opposingA: {
      code: `${codesObj[opposingADim]?.code || "S"}${opposingANorm}`,
      name: capitalizeKey(opposingADim),
      description: getDimensionDescription(opposingADim),
      tension: `${capitalizeKey(primaryDim)} > ${capitalizeKey(opposingADim)}`,
    },
    opposingB: {
      code: `${codesObj[opposingBDim]?.code || "Fx"}${opposingBNorm}`,
      name: capitalizeKey(opposingBDim),
      description: getDimensionDescription(opposingBDim),
      tension: `${capitalizeKey(primaryDim)} > ${capitalizeKey(opposingBDim)}`,
    },
    coreEngine: `${capitalizeKey(primaryDim)}-driven operating system prioritizing...`,
    systemTension: "Creates reliability. Reduces relational responsiveness under pressure.",
  }
}
```

---

## ISSUE 2: EXECUTIVE SUMMARY PAGE WIDTH BROKEN ✓ DIAGNOSED

### Problem
- After SVG Page 2 insertion, Executive Summary (Page 3) text runs edge-to-edge
- Missing proper page wrapper/margins/container

### Root Cause
**`stripLegacyPage2()` removed old HTML map container, but didn't restore proper `<div class="page">` wrapper for Executive Summary section.**

### Solution: Restore Page Container After SVG

**File: `/Users/rrg/moremindmap-backend/utils/page2IntegratedRenderer.js`**

**Function: `embedSvgPage2()`**

After SVG is embedded, wrap Executive Summary and all body pages in proper `.page` container.

**Implementation:**

```javascript
function embedSvgPage2(html, svgContent) {
  // Wrap SVG with page styling
  const svgPage = `
<div class="page" style="page-break-after: always; margin: 0; padding: 0.75in; width: 8.5in; height: auto; min-height: 11in;">
${svgContent}
</div>
  `.trim()

  // Find first page close
  const firstPageCloseRegex = /<div class="page">[^]*?<\/div>\s*<\/div>/i
  const firstPageMatch = html.match(firstPageCloseRegex)
  
  if (firstPageMatch) {
    const firstPageEndIndex = html.indexOf(firstPageMatch[0]) + firstPageMatch[0].length
    const beforeSvg = html.substring(0, firstPageEndIndex)
    const afterSvg = html.substring(firstPageEndIndex)
    
    // Add SVG after Page 1
    html = beforeSvg + "\n\n" + svgPage + "\n\n" + afterSvg
    console.log("[PAGE2-WRAP] SVG inserted after Page 1")
  }

  // CRITICAL: Restore page containers for body text
  // Find all sections after SVG and wrap in proper <div class="page">
  html = restorePageContainers(html)

  return html
}

function restorePageContainers(html) {
  // Executive Summary through Facilitator Notes should be wrapped in <div class="page">
  // Pattern: Find <h2>Executive Summary</h2> and wrap following content
  
  const sectionTitles = [
    "Executive Summary",
    "Operating Pattern",
    "Decision Architecture",
    "Communication Style",
    "Under Pressure",
    "Blind Spots",
    "Friction Points",
    "Growth Edge",
    "Facilitator Notes",
    "Recommended Next Step"
  ]

  sectionTitles.forEach(title => {
    const regex = new RegExp(`(<h2>${title}<\\/h2>)([^]*?)(?=<h2>|$)`, 'i')
    
    html = html.replace(regex, (match, h2, content, offset) => {
      // Check if already wrapped
      const beforeMatch = html.substring(Math.max(0, offset - 100))
      if (beforeMatch.includes('<div class="page">')) {
        return match // Already wrapped
      }

      // Wrap section in page container with proper styling
      return `
<div class="page" style="width: 8.5in; height: auto; min-height: 11in; padding: 0.75in; margin: 0 auto 0.5in; page-break-after: always; page-break-inside: avoid;">
  <div class="header">
    <div class="logo">MORE <span class="logo-accent">MINDMAP</span></div>
    ${h2}
  </div>
  <div class="content" style="padding: 0.5in 0;">
${content.trim()}
  </div>
  <div class="footer">Page [num]</div>
</div>
      `.trim()
    })
  })

  return html
}
```

---

## Test Profile (Expected Output)

**Input:** 8D scores yielding: V8, Fd4, F4, Vl3, L3, H2, S1, Fx1

**Cover signature:** ✅ V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1

**Page 2 must show:**
- Primary: V8 / Vector
- Secondary: Fd4 / Fidelity (or F4 / Framework if tie-break priority)
- Opposing A: S1 / Signal
- Opposing B: Fx1 / Flex

**Page 3+ (Executive Summary onwards):**
- Proper `<div class="page">` wrappers
- Centered content
- Correct margins/padding
- No edge-to-edge text
- Print-safe page breaks

---

## Files to Modify

1. **`/Users/rrg/moremindmap-backend/utils/page2IntegratedRenderer.js`**
   - Modify `generateV1MiniProfileHTML()` line 48
   - Add `buildSystemMapDataFromCodes()` function
   - Modify `embedSvgPage2()` to restore page containers
   - Add `restorePageContainers()` function

2. **`/Users/rrg/moremindmap-backend/engine/generatePremiumMiniProfileV2.js`**
   - Verify `codes` object is included in output (should be line ~152)
   - Log output for verification

---

## Validation Steps

1. Generate test report locally
2. Verify cover signature matches Page 2 system map codes
3. Verify Executive Summary has proper margins
4. Verify no Fd1/H1 unless they're in actual signature
5. Screenshot all three sections
6. Verify SVG Page 2 appears exactly once

---

**Status:** Fixes ready to implement  
**Estimated time:** 45 minutes  
**Complexity:** Medium (careful signature object flow, page wrapper restoration)
