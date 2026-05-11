# SCORING CORRECTION — Independent Dimension Scoring

**Date:** Thu Apr 30, 2026 10:23 MST  
**Correction:** Dimension scores are independent 0-100, not a pie chart

---

## WHAT CHANGED

### ❌ OLD (Incorrect)
- All 8 dimensions must sum to 100%
- Scores normalized to fit a pie chart
- If one dimension goes up, others must go down proportionally

### ✅ NEW (Correct)
- Each dimension scored independently on 0-100 scale
- No sum requirement
- Final scores can total >100 or <100
- Primary/secondary selected by **highest individual scores**, not by percentages of a sum

---

## KEY SCORING RULES (CORRECTED)

### Score Range
```
Each dimension: 0–100 (independent)
Example:
  Vector: 72
  Velocity: 80
  Signal: 48
  Leverage: 35
  Fidelity: 22
  Flex: 18
  Framework: 15
  Horizon: 10
  ──────────
  Total: 300 (not constrained to 100%)
```

### Adjustment Cap
- Normal adjustment: ±5–12 points per dimension
- Strong evidence: ±15 points max
- Hard cap: ±20 points per dimension
- Each dimension adjusted independently (no zero-sum constraint)

### Primary/Secondary Selection
- **Primary:** Top 2 by highest individual scores (80, 72 in example above)
- **Secondary:** Next highest scores (48, 35 in example)
- **Suppressed:** Lowest scores (10, 15, 18, 22 in example)
- **Not** selected by percentage of a sum

### Evidence Requirement
- Adjustment ≥5 points requires documented reason
- Adjustment ≥10 points requires strong written evidence OR multiple answer-pattern signals
- Adjustment ≥15 points requires both written evidence AND answer contradictions
- All adjustments must remain within ±20 cap

---

## IMPLEMENTATION IMPACT

### What Stays The Same
✅ OpenAI scoring refinement layer  
✅ Language pattern analysis  
✅ Adjustment cap at ±20 points  
✅ Evidence-based refinements  
✅ Fallback to deterministic if AI fails  
✅ Confidence levels (high/medium/low)  

### What Changes
❌ Remove: "All scores must sum to 100%"  
❌ Remove: Pie-chart normalization logic  
❌ Remove: Zero-sum adjustment constraint  
✅ Add: Independent 0-100 scoring per dimension  
✅ Add: Selection logic for primary/secondary by highest scores  

---

## CORRECTED JSON STRUCTURE

```json
{
  "aiRefinedScores": {
    "Vector": 72,              // Independent 0-100
    "Velocity": 80,            // Independent 0-100
    "Signal": 48,              // Independent 0-100
    "Leverage": 35,            // Independent 0-100
    "Fidelity": 22,            // Independent 0-100
    "Flex": 18,                // Independent 0-100
    "Framework": 15,           // Independent 0-100
    "Horizon": 10              // Independent 0-100
    // Total = 300 (no constraint)
  },

  "scoreAdjustments": [
    {
      "dimension": "Vector",
      "baselineScore": 67,
      "refinedScore": 72,
      "adjustmentReason": "Concise, command-oriented answers. Ownership framing. +5 points."
    },
    {
      "dimension": "Velocity",
      "baselineScore": 75,
      "refinedScore": 80,
      "adjustmentReason": "Rapid decision-making pattern. Urgency language in written responses. +5 points."
    }
  ],

  "primaryPattern": [
    { "key": "Velocity", "score": 80 },   // Highest individual score
    { "key": "Vector", "score": 72 }      // Second highest
  ],

  "secondaryPattern": [
    { "key": "Signal", "score": 48 },     // Third highest
    { "key": "Leverage", "score": 35 }    // Fourth highest
  ],

  "suppressedPatterns": [
    { "key": "Horizon", "score": 10 },
    { "key": "Framework", "score": 15 },
    { "key": "Fidelity", "score": 22 },
    { "key": "Flex", "score": 18 }
  ],

  "confidenceLevel": "high",
  "validityFlags": ["strong_written_signal", "consistent_answer_pattern"],
  "contradictionFlags": [],

  // ... narrative sections unchanged
}
```

---

## CODE CHANGES NEEDED

### In `engine/openAiMiniProfileInterpreter.js`

**OLD (Remove):**
```javascript
function rankAndNormalizeScores(refinedScores) {
  // Old pie-chart normalization
  const total = Object.values(refinedScores).reduce((a, b) => a + b, 0)
  const normalized = Object.fromEntries(
    Object.entries(refinedScores).map(([k, v]) => [k, (v / total) * 100])
  )
  return normalized
}
```

**NEW (Replace with):**
```javascript
function rankScores(refinedScores) {
  // Independent 0-100 scoring
  // No normalization needed
  return Object.entries(refinedScores)
    .map(([key, score]) => ({ key, score }))
    .sort((a, b) => b.score - a.score)  // Sort by highest score
}
```

### Selection Logic

**OLD (Remove):**
```javascript
const primaryPattern = rankedPercentages.slice(0, 2)  // By percentage
```

**NEW (Replace with):**
```javascript
const ranked = rankScores(refinedScores)
const primaryPattern = ranked.slice(0, 2)     // By highest individual scores
const secondaryPattern = ranked.slice(2, 4)   // By next highest
const suppressedPatterns = ranked.slice(4)    // By lowest
```

---

## VALIDATION CHECKLIST

- [ ] Remove all normalization logic (no sum requirement)
- [ ] Update rankScores() to sort by highest individual scores
- [ ] Verify primary/secondary selection uses highest scores
- [ ] Verify suppressed patterns are lowest scores
- [ ] Test with sample profile where scores >100 total
- [ ] Verify adjustments stay within ±20 cap per dimension
- [ ] Verify evidence requirements still apply
- [ ] Verify fallback still works

---

## FEASIBILITY IMPACT

**Impact on timeline:** Minimal (removes complexity)  
**Impact on feasibility:** ✅ Improves (simpler logic, fewer constraints)  
**Impact on testing:** ✅ Simplifies (no normalization bugs to test)

---

**Correction Applied:** Thu Apr 30, 2026 10:23 MST  
**Status:** READY FOR IMPLEMENTATION
