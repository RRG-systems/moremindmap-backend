# MOREMINDMAP MINI PROFILE — AI UPGRADE FEASIBILITY REPORT (REVISED)
## With Behavioral Scoring Refinement Layer

**Date:** Thu Apr 30, 2026 10:20 MST  
**Revision:** Architecture amended to include AI-driven scoring calibration  
**Status:** FEASIBILITY ANALYSIS ONLY — No code changes made

---

## EXECUTIVE SUMMARY — REVISED ARCHITECTURE

**Old Understanding:** AI generates narrative interpretation of deterministic scores

**Revised Understanding:** AI performs behavioral calibration with final scoring authority

```
scoreAssessment.js (baseline mechanical scoring)
         ↓
[AI SCORING REFINEMENT LAYER] ← NEW TIER
  - Analyzes 24 answer texts for language patterns
  - Analyzes written responses for behavioral signals
  - Refines dimension scores up to ±20 points when evidence supports
  - Returns both refined scores AND narrative sections
         ↓
PDF/Report uses AI-refined scores, not baseline
```

**Key Difference:** AI doesn't just narrate the deterministic scores. AI **recalibrates the scores themselves** based on deeper behavioral evidence.

---

## A. CURRENT DATA AVAILABLE AFTER SCORING

**Same as before, but AI will now process MORE deeply:**

```javascript
{
  // Deterministic baseline (now treated as first-pass only)
  normalizedScores: { ... },      // Will be refined by AI
  ranked: [ ... ],                // Will be re-ranked by AI
  rawScores: { ... },
  
  // Raw data for AI analysis (NEW FOCUS)
  answers: {                       // All 24 selected answers
    1: "A",
    2: "B",
    // ... all 24
  },
  
  writtenResponses: [              // Analyzed for language patterns
    { questionId: 15, answer: "I tend to move fast..." },
    { questionId: 22, answer: "People tell me I..." }
  ],
  
  // Quality signals
  diagnostics: {
    flatSpread: 30.0,
    flatDistribution: false,
    weakWrittenCount: 0,
    contradictionScore: 0
  }
}
```

**What AI Will Analyze:**

✅ All 24 raw selected answers (not just scores)  
✅ Written response text for language patterns  
✅ Patterns across the entire response set  
✅ Contradictions between answer selections and written text  
✅ Evidence for language-based refinements  

---

## B. RECOMMENDED AI SCORING REFINEMENT LAYER

**Location:** `/engine/openAiMiniProfileInterpreter.js` (new file)

**Function:** `refineScoresWithAi(scoringPayload, rawAnswers, writtenResponses)`

### **AI Task: Behavioral Language Pattern Analysis**

The AI will examine:

#### **1. Answer Style Patterns**
- Short, clipped, direct answers → may increase Vector/Velocity
- Long, reflective answers → may increase Signal/Horizon
- Procedural, detailed answers → may increase Fidelity/Framework
- Adaptive, trade-off aware answers → may increase Flex
- Persuasion/positioning language → may increase Leverage

#### **2. Written Response Language Signals**
```
Language Pattern               → Dimension Signal
─────────────────────────────────────────────────
"I move fast..."              → Velocity +5-10
"I take charge..."            → Vector +5-10
"I look ahead..."             → Horizon +5-10
"I build relationships..."    → Leverage +5-10
"I read people..."            → Signal +5-10
"I pay attention to details..." → Fidelity +5-10
"I adapt/change course..."    → Flex +5-10
"I build systems..."          → Framework +5-10
```

#### **3. Meta-Behavioral Evidence**
- Short, confident responses → Vector +5, uncertainty -5
- Hedging, conditional language ("might," "could") → Flex +5, Vector -3
- Blame language → Vector +5, Signal -3
- Ownership language → Vector +5, Flex -2
- Future-oriented language → Horizon +5
- Process-oriented language → Framework +5
- People-first framing → Signal +5, Leverage +5
- Task-first framing → Velocity +5, Vector +5
- Conflict avoidance language → Signal +5, Vector -3
- Ambiguity tolerance signals → Flex +5, Framework -3

### **AI Scoring Refinement Rules**

**Rule 1: Adjustment Boundaries**
- Normal adjustment: ±5-12 points
- Strong written evidence: ±15 points max
- Never adjust >20 points unless profile flagged low-confidence or contradictory
- Cap total adjustment per dimension: ±20 points max

**Rule 2: Evidence Requirement**
- Adjustment ≥5 points requires documented reason
- Adjustment ≥10 points requires strong written evidence OR multiple answer-pattern signals
- Adjustment ≥15 points requires both written evidence AND multiple answer contradictions

**Rule 3: Preserve Baseline When Unclear**
- If written responses are thin (<50 words total), rely more on deterministic scoring
- Don't adjust on speculation
- Only adjust when evidence is clear

**Rule 4: Handle Contradictions**
- If written answers contradict selected answers, flag in facilitatorNotes
- Example: Selected "fast-moving" answers but wrote "I think carefully"
- Flag as validation question for facilitator

**Rule 5: Final Score Normalization**
- After refinements, re-normalize all 8 dimensions to 0-100%
- Ensure sum of all percentages = 100%
- Recalculate primary/secondary from refined scores

**Rule 6: Confidence Levels**
- High: Strong written signal + clear patterns + no contradictions
- Medium: Mixed signals or thin written responses
- Low: Contradictory patterns, flat distribution, or unclear signals

---

## C. REVISED OPENAI JSON OUTPUT STRUCTURE

**Includes both refined scores AND narrative interpretation**

```json
{
  "aiRefinedScores": {
    "Vector": 72,
    "Signal": 48,
    "Fidelity": 22,
    "Velocity": 80,
    "Leverage": 35,
    "Flex": 18,
    "Framework": 15,
    "Horizon": 10
  },

  "scoreAdjustments": [
    {
      "dimension": "Vector",
      "baselineScore": 67,
      "refinedScore": 72,
      "adjustmentReason": "User gave concise, command-oriented responses ('Go straight into the planning session'). Consistently selected ownership-first answers. Adjustment +5."
    },
    {
      "dimension": "Velocity",
      "baselineScore": 75,
      "refinedScore": 80,
      "adjustmentReason": "Answer pattern shows rapid decision-making. Written responses use urgency language ('move fast', 'no time'). Strong velocity signal in both. Adjustment +5."
    }
  ],

  "primaryPattern": [
    { "key": "Velocity", "label": "Velocity (Tempo)", "percent": 80 },
    { "key": "Vector", "label": "Vector (Command)", "percent": 72 }
  ],

  "secondaryPattern": [
    { "key": "Signal", "label": "Signal (Relational Awareness)", "percent": 48 },
    { "key": "Leverage", "label": "Leverage (Influence)", "percent": 35 }
  ],

  "suppressedPatterns": [
    { "key": "Flex", "label": "Flex (Adaptability)", "percent": 18 },
    { "key": "Framework", "label": "Framework (Structure)", "percent": 15 },
    { "key": "Fidelity", "label": "Fidelity (Precision)", "percent": 22 },
    { "key": "Horizon", "label": "Horizon (Perspective)", "percent": 10 }
  ],

  "confidenceLevel": "high",

  "validityFlags": [
    "strong_written_signal",
    "consistent_answer_pattern",
    "clear_primary_secondary_split"
  ],

  "contradictionFlags": [],

  "executiveSummary": "You are defined by rapid decision-making combined with clear command presence. You move fast AND take charge—a powerful combination for driving momentum and pushing through ambiguity.",

  "operatingPattern": "You move by acting first, gathering information mid-course. You don't wait for perfect clarity. You step in to lead when direction is needed.",

  "decisionPattern": "You decide quickly with 60-70% information. You trust pattern recognition. You own your decisions visibly.",

  "communicationStyle": "You communicate directly and briefly. You skip preamble. You state conclusions, not possibilities.",

  "underPressure": "You get more decisive, not less. You push harder and move faster. Your directness can tip into bulldozing.",

  "blindSpots": "You may miss important nuance in complex interpersonal situations. You can seem impatient with careful analysis.",

  "frictionPoints": "In detail work, you cut corners. With people, you can miss emotional data. Under pressure, you get intolerant of different paces.",

  "growthEdge": "Consider one extra pause before major decisions: 'What might I be missing? Who else should I hear from?' This is not slowing down—it's adding one input valve to an already-fast system.",

  "recommendedNextStep": "Practice listening for the unstated concern, not just the stated objection. This will make you more effective in complex negotiations.",

  "facilitatorNotes": "Profile shows high confidence. Answer patterns align with written response language. No contradictions detected. User is likely self-aware about their operating style. Good coaching candidate for influence/signal development."
}
```

---

## D. IMPLEMENTATION: AI SCORING REFINEMENT IN openAiMiniProfileInterpreter.js

**New Function Architecture:**

```javascript
export async function generateAiMiniProfile(
  scoringPayload,      // From scoreAssessment.js
  rawAnswers,          // All 24 selected answers
  writtenResponses,    // Any written response text
  userMetadata         // { name, email }
) {
  // STAGE 1: Analyze answer patterns
  const answerPatterns = analyzeAnswerPatterns(rawAnswers)
  
  // STAGE 2: Call OpenAI for behavioral analysis + refinement
  const aiAnalysis = await callOpenAiForScoreRefinement(
    scoringPayload,
    answerPatterns,
    writtenResponses
  )
  
  // STAGE 3: Apply AI refinements to baseline scores
  const refinedScores = applyScoreAdjustments(
    scoringPayload.normalizedScores,
    aiAnalysis.adjustments
  )
  
  // STAGE 4: Recalculate primary/secondary from refined scores
  const newRanked = rankScores(refinedScores)
  const primaryPattern = newRanked.slice(0, 2)
  const secondaryPattern = newRanked.slice(2, 4)
  const suppressedPatterns = newRanked.slice(4)
  
  // STAGE 5: Build final output with both scores + narrative
  return {
    aiRefinedScores: refinedScores,
    scoreAdjustments: aiAnalysis.adjustments,
    primaryPattern,
    secondaryPattern,
    suppressedPatterns,
    confidenceLevel: aiAnalysis.confidenceLevel,
    validityFlags: aiAnalysis.validityFlags,
    contradictionFlags: aiAnalysis.contradictionFlags,
    executiveSummary: aiAnalysis.narratives.executiveSummary,
    operatingPattern: aiAnalysis.narratives.operatingPattern,
    // ... all narrative sections
    facilitatorNotes: aiAnalysis.narratives.facilitatorNotes
  }
}
```

### **OpenAI Prompt Architecture:**

```javascript
const systemPrompt = `You are a behavioral scoring calibration engine for MORE MindMap.

Your role:
1. Analyze the raw 24 answers for language/pattern evidence
2. Analyze written responses for behavioral signals
3. Compare evidence against baseline mechanical scores
4. Refine scores where evidence supports (up to ±20 points)
5. Return BOTH refined scores AND narrative interpretation

Rules for score refinement:
- Normal adjustments: ±5-12 points
- Strong evidence adjustments: ±15 points max
- Max adjustment per dimension: ±20 points
- Only adjust if evidence supports it
- Provide reasons for adjustments ≥5 points
- Never adjust on speculation

Language patterns to look for:
- Short/clipped answers → Vector/Velocity signals
- Long/reflective answers → Signal/Horizon signals
- Procedural/detailed → Fidelity/Framework signals
- Adaptive/tradeoff-aware → Flex signals
- Persuasion/positioning → Leverage signals
- Ownership language → Vector signals
- Hedging/conditional → Flex signals
- Conflict avoidance → Signal signals
- Future-oriented → Horizon signals
- Process-oriented → Framework signals

Return ONLY valid JSON (no markdown).`

const userMessage = JSON.stringify({
  baselineScores: scoringPayload.normalizedScores,
  baselineRanked: scoringPayload.ranked,
  allAnswers: rawAnswers,
  writtenResponses: writtenResponses,
  diagnostics: scoringPayload.diagnostics,
  userResponseCount: Object.keys(rawAnswers).length
})
```

---

## E. REVISED DATA FLOW

```
┌────────────────────────────────────────────────────────────┐
│ POST /api/moremindmap/mini-profile (server.js)            │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ scoreAssessment.js (BASELINE MECHANICAL SCORING)          │
│ Returns: normalizedScores, ranked, diagnostics            │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ [NEW] generateAiMiniProfile() (BEHAVIORAL CALIBRATION)    │
│ INPUT: baseline scores + raw answers + written responses  │
│ PROCESS: Analyze language patterns, refine scores         │
│ OUTPUT: aiRefinedScores + adjustments + narratives        │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ [FALLBACK] If AI fails: use generateMiniProfile()         │
│ (existing deterministic generator)                        │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ generateProfilePdf() (uses aiRefinedScores, not baseline) │
│ emailProfilePdf()                                         │
└────────────────────────────────────────────────────────────┘
         ↓
┌────────────────────────────────────────────────────────────┐
│ Response to frontend (PDF emailed, HTML in browser)       │
│ Uses: aiRefinedScores + AI narrative sections             │
└────────────────────────────────────────────────────────────┘
```

---

## F. CHANGES TO FEASIBILITY REPORT

### **Updated: Complexity Assessment**

| Phase | Complexity | Time | Impact |
|-------|-----------|------|--------|
| OpenAI Interpreter (OLD) | Medium | 45 min | Just narrative |
| OpenAI Interpreter (REVISED) | **High** | **75 min** | **Scores + narrative** |
| PDF Generation | Medium | 45 min | Same |
| Email Integration | Low | 30 min | Same |
| Backend Wiring | Medium | 40 min | Slightly more logic |
| Testing | Medium→High | 90 min | Need to validate score refinements |
| **Total** | | **~5-6 hours** | +1 hour vs original |

### **Updated: Risk Assessment**

| Risk | Old | New | Mitigation |
|------|-----|-----|-----------|
| OpenAI fails | Medium | Medium | Fallback to deterministic scores ✅ |
| Bad score refinement | LOW | **MEDIUM** | Validate with test profiles, add guardrails ✅ |
| Contradictory refines | - | **MEDIUM** | Flag in facilitator notes, alert Darren ✅ |
| Over-adjustment | - | **MEDIUM** | Cap adjustments at ±20, require evidence ✅ |

### **New Validation Requirements**

**Before deploying, test:**
- ✅ Score refinements make sense (spot check 3-5 profiles)
- ✅ Adjustment reasons are clear and accurate
- ✅ Contradictions flagged correctly
- ✅ Fallback works if OpenAI fails
- ✅ Final scores re-normalize correctly
- ✅ Primary/secondary recalculated properly

---

## G. UPDATED FILE STRUCTURE

### **New File (More Complex):**

| File | Purpose | Lines | Complexity |
|------|---------|-------|-----------|
| `engine/openAiMiniProfileInterpreter.js` | **Score refinement + narrative** | **~300 lines** | **High** |
| `engine/pdfGenerator.js` | PDF generation | ~100 | Medium |
| `utils/emailService.js` | Email delivery | ~80 | Low |
| `utils/htmlRenderer.js` | HTML template | ~200 | Medium |

### **Modified Files:**

| File | Changes | Lines Added |
|------|---------|------------|
| `server.js` | Insert refined AI flow | +50-70 |
| `package.json` | Add dependencies | +2 |
| `.env` | Add env vars | +3 |

---

## H. BEHAVIORAL LANGUAGE ANALYSIS ENGINE (Inside openAiMiniProfileInterpreter.js)

**Pre-processing function (before AI call):**

```javascript
function analyzeAnswerPatterns(rawAnswers) {
  return {
    // Count answer style characteristics
    conciseAnswers: countAnswerType(rawAnswers, "short"),
    reflexiveAnswers: countAnswerType(rawAnswers, "long"),
    commandLanguage: countLanguage(rawAnswers, ["go", "take", "push", "drive"]),
    relationalLanguage: countLanguage(rawAnswers, ["people", "listen", "read", "understand"]),
    urgencyLanguage: countLanguage(rawAnswers, ["fast", "now", "immediate", "quick"]),
    ownershipLanguage: countLanguage(rawAnswers, ["I", "my", "I decide", "I lead"]),
    hedgingLanguage: countLanguage(rawAnswers, ["might", "could", "maybe", "possibly"]),
    futureLanguage: countLanguage(rawAnswers, ["ahead", "future", "tomorrow", "next"]),
    processLanguage: countLanguage(rawAnswers, ["system", "process", "structure", "framework"]),
    conflictAvoidance: countLanguage(rawAnswers, ["avoid", "prevent", "smooth", "ease"]),
    // ... more patterns
  }
}
```

This gets passed to OpenAI along with baseline scores for cross-validation.

---

## I. IMPLEMENTATION CHECKLIST (REVISED)

- [ ] Design OpenAI refinement prompt (with language pattern guidance)
- [ ] Create `engine/openAiMiniProfileInterpreter.js` (300 lines, high complexity)
- [ ] Build `analyzeAnswerPatterns()` function
- [ ] Implement score refinement logic (±20 cap, reason capture)
- [ ] Build score normalization function
- [ ] Implement recalculation of primary/secondary from refined scores
- [ ] Implement contradictory pattern detection
- [ ] Create `engine/pdfGenerator.js`
- [ ] Create `utils/htmlRenderer.js`
- [ ] Create `utils/emailService.js`
- [ ] Modify `server.js` with revised flow
- [ ] Add fallback: use deterministic scores if AI fails
- [ ] Test score refinements (spot check 5 profiles)
- [ ] Test fallback path (disable OpenAI, verify deterministic works)
- [ ] Test contradiction detection
- [ ] Test normalization (scores sum to 100%)
- [ ] Load test (5+ concurrent requests)
- [ ] Deploy to staging
- [ ] Verify 24h of production data
- [ ] Deploy to production

---

## J. REVISED BUILD SEQUENCE

### **Phase 1: Dependencies** (30 min)
- Add puppeteer, resend to package.json

### **Phase 2: OpenAI Scoring Refinement** (90 min) ← EXPANDED
- Design language-pattern analysis system
- Create `engine/openAiMiniProfileInterpreter.js`
- Build score adjustment logic (cap at ±20, require evidence)
- Build recalculation functions
- Test with 3-5 sample profiles
- Validate score adjustments make sense

### **Phase 3: PDF Generation** (45 min)
- Create `engine/pdfGenerator.js`
- Create `utils/htmlRenderer.js`
- Test PDF rendering

### **Phase 4: Email Integration** (30 min)
- Create `utils/emailService.js`
- Test Resend delivery

### **Phase 5: Backend Wiring** (40 min)
- Modify `server.js` with revised flow
- Wire AI refinement layer
- Add fallback logic

### **Phase 6: Testing** (90 min) ← EXPANDED
- Validate score refinements (5 test profiles)
- Test all adjustment reasons
- Test contradiction detection
- Test normalization
- Test fallback
- Load test

### **Phase 7: Deploy** (15 min)
- Staging validation
- Production deployment
- Monitor first 48h

**Total: 5.5-6 hours** (vs 4-5 original)

---

## K. CRITICAL REFINEMENT GUARDRAILS

**To prevent bad AI-driven score adjustments:**

1. **Hard Cap Rule:** No dimension adjustment >20 points ever
2. **Evidence Rule:** Adjustment ≥5 points requires documented reason
3. **Contradition Flag:** If answer patterns contradict, log in facilitatorNotes
4. **Thin Data Rule:** If written responses <50 words, cap refinements at ±8 points
5. **Recalc Rule:** Always re-normalize after adjustments (no floating point errors)
6. **Backup Rule:** If AI confidence <medium, prefer deterministic baseline
7. **Fallback Rule:** If OpenAI fails, use deterministic generator (no partial refinements)

---

## L. REVISED FEASIBILITY VERDICT

### ✅ **STILL HIGHLY FEASIBLE** (with caveats)

**Increases in Complexity:**
- More complex OpenAI prompt engineering
- More validation testing required
- Need guardrails on score adjustments
- Need confidence-level logic

**Why Still Feasible:**
- ✅ Clear algorithmic approach (language pattern analysis is well-defined)
- ✅ Strong fallback path (deterministic generator if AI fails)
- ✅ Adjustment caps prevent wild changes
- ✅ All evidence-based (not speculative)
- ✅ Darren can review score adjustments before full rollout

**Recommendation:**
- Build Phase 2 (AI Refinement) carefully
- Test thoroughly with real profiles
- Have Darren review first 10 refined profiles
- Then roll out to production

**Go/No-Go:** ✅ **GO — Proceed with caution on AI refinement**

---

**Report Completed:** Thu Apr 30, 2026 10:20 MST  
**Status:** FEASIBILITY CONFIRMED (REVISED ARCHITECTURE)  
**Next Step:** Begin Phase 1, then careful Phase 2 (scoring refinement)
