# PHASE 1D: GPT-5.5 OUTPUT AUDIT & REFINEMENT PLAN

**Date:** Mon 2026-05-04 11:13 MST  
**Status:** INSPECTION COMPLETE — Refinements identified, no coding yet

**Report audited:**
`/Users/rrg/moremindmap-backend/temp/reports/mini-profile-v2-dual-stage-2026-05-04T18-06-39-438Z.html`

---

## EXECUTIVE SUMMARY

✅ **Output quality:** Strong, instrument-grade, well-structured  
⚠️ **Issues found:** Moderate — mostly pattern/language refinements, not structural  
✅ **Layout:** No clipping, no overflow, readable end-to-end  
✅ **Page 2:** System map working well, no changes needed  
✅ **Recommendation:** One pass of Stage B prompt refinement + linguistic polish

---

## 1. TOP 10 CONTENT ISSUES

### Issue 1: Overuse of "may" (39 occurrences)
**Location:** Throughout all 12 sections  
**Examples:**
- "The person may become..."
- "May be experienced as..."
- "may create friction..."
- "may underestimate..."

**Problem:** Creates tentative tone, reduces authority. Instrument-grade reports should state patterns with confidence, not speculation.

**Fix:** Replace ~60% of "may" with "tends to," "shows," "creates," "produces," "demonstrates," "does," "will."

**Impact:** High — this is the single biggest tone shift needed

---

### Issue 2: Secondary "may be" constructions (14 occurrences)
**Examples:**
- "may be partly true"
- "may be one of being..."
- "may be heavy..."

**Problem:** Compounds Issue 1, creates passive voice over active diagnosis.

**Fix:** Rewrite as active: "partly true" → "is often partly true"; "one of being" → "one in which they..."

**Impact:** Medium-High

---

### Issue 3: Raw score leaks (3 occurrences in HTML)
**Locations:**
- Page 2: "34/100" (Fidelity)
- Page 2: "20/100" (Horizon)
- Page 2: "5/100" (Signal/Flex)

**Problem:** Doctrine requirement violated — never show raw decimals. Should use codes (Fd7, H4, S1) only.

**Fix:** Remove all decimal scores from final rendering. Page 2 should show only codes and labels.

**Impact:** Critical (doctrine breach)

---

### Issue 4: Repetitive phrase: "the person" (appears frequently)
**Examples:**
- "The person is likely to..."
- "The person may..."
- "The person becomes..."
- "The person can..."

**Problem:** While acceptable in behavioral writing, overuse creates institutional tone. Patricia-style uses varied openers.

**Fix:** Vary sentence structure: "They...," "This system...," "The profile...," "Characterized by...," "Built to..."

**Impact:** Medium — affects prose elegance, not substance

---

### Issue 5: Vague consultant language in sections
**Location:** Facilitator Notes, Growth Edge  
**Examples:**
- "should approach this profile with respect"
- "is unlikely to land unless"
- "should not over-pathologize"

**Problem:** Generic coaching guidance. Should be specific, operationalized, tied to this pattern.

**Fix:** Replace with concrete behavioral triggers: "When the person intellectualizes pressure, notice..." / "Name three specific scenarios where..."

**Impact:** Medium

---

### Issue 6: Missing compartmentalization (Core Read → What This Creates → What This Costs → Development Lever)
**Affected sections:** All 12  
**Current structure:** Dense paragraphs without sub-structure

**Problem:** Readers can't quickly extract actionable insight. Patricia-style compartmentalizes for clarity.

**Fix:** Add internal headers or bullet structure within each section to show:
- Core pattern
- How it manifests  
- Costs when overplayed
- Specific development move

**Impact:** High (content is strong but structure could be tighter)

---

### Issue 7: Contradictions/circular reasoning
**Location:** Growth Edge section
**Text:** "The person becomes more powerful when they can say...that the team has enough information to move, enough structure to stay safe, and enough feedback to correct course."

**Problem:** Slightly abstract. What does "enough" mean operationally? Needs specificity.

**Fix:** Rewrite: "The person becomes more powerful when they can distinguish between a) need-to-know (required before moving), b) nice-to-know (can be learned in motion), and c) noise (can be ignored)."

**Impact:** Low-Medium

---

### Issue 8: Thin language in "What Full Profile Unlocks"
**Current:** Section is present but generic
**Examples:**
- "would clarify the deeper architecture"
- "would identify the finer distinctions"
- "would help distinguish"

**Problem:** Too many "woulds." Doesn't tell reader what they'd actually get.

**Fix:** Rewrite as concrete: "Full profile would identify whether your precision drive is primarily cognitive (seeking correctness), ethical (seeking integrity), or anxiety-regulating (seeking safety)."

**Impact:** Medium

---

### Issue 9: Incomplete differentiation in "Blind Spots"
**Current:** Blind spots identified, but not clearly distinguished from weaknesses

**Problem:** Blind spots are different from weaknesses. A blind spot is something you're not aware of.

**Fix:** Restructure: "What you're likely NOT seeing: [1] cost of your own analysis approach [2] valid reasons others resist structure [3] emotional impact of your directness."

**Impact:** Medium

---

### Issue 10: Missing "Default Stress Response" clarity
**Location:** Under Pressure section  
**Current:** Describes tightening, but doesn't name the specific first behaviors

**Problem:** Reader doesn't know early warning signs of their own stress response.

**Fix:** Add: "Early indicators you're under pressure: you start asking more questions, requesting additional documentation, taking back work, correcting minor deviations. This is your system re-creating coherence."

**Impact:** Medium-High

---

## 2. TOP 10 LAYOUT ISSUES

### Layout Issue 1: ✅ NO CLIPPING — Confirmed
**Status:** PASS  
All pages render fully, no text hidden, no overflow:hidden violations  
CSS: `overflow: visible` applied throughout

---

### Layout Issue 2: ✅ NO AWKWARD PAGE BREAKS — Confirmed
**Status:** PASS  
Section breaks occur naturally where content ends  
Page 2 (System Map): Standalone, clear visual  
Pages 3-12: Narrative sections flow naturally

---

### Layout Issue 3: ✅ PAGE 2 INTEGRITY — Confirmed  
**Status:** PASS — Recommend NO CHANGES  
5-circle system map displays correctly  
Circles: primary (top), secondary (right), opposing (left/bottom), center  
Tension notes clear  
Ready to stay as-is

---

### Layout Issue 4: ⚠️ Score display showing raw decimals
**Issue:** Page 2 shows "34/100", "20/100", "5/100"  
**Location:** Pattern circles, bottom of each dimension  
**Problem:** Contradicts doctrine (scores should use codes only)

**Fix:** Remove decimal scores from pattern circles. Keep only:
- Icon with code (Fd7, H4, S1)
- Pattern name
- Remove the score line

**Impact:** Critical

---

### Layout Issue 5: ✅ Font sizing appropriate
**Status:** PASS  
10.5px body text readable  
18px section headers clear  
9px footer/metadata appropriate  
8px callout text acceptable (not strained)

---

### Layout Issue 6: ✅ Signature line visible and clear
**Status:** PASS  
"V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1" renders clearly  
Monospace font works well  
Easy to scan

---

### Layout Issue 7: ✅ System Map visual hierarchy
**Status:** PASS  
Primary (dark) vs Secondary (blue) vs Opposing (gray) color distinction clear  
Center hub appropriately subtle  
Spacing good

---

### Layout Issue 8: ✅ Callout boxes (golden accents) working
**Status:** PASS  
Core Edge box on cover page readable  
Tension note on Page 2 stands out appropriately  
Visual rhythm good

---

### Layout Issue 9: ✅ No awkward line breaks in prose
**Status:** PASS  
Text wraps naturally  
No mid-word breaks  
Readability maintained across font size changes

---

### Layout Issue 10: ✅ Mobile/print readiness
**Status:** PASS  
Media queries for print mode present  
CSS handles page-break-inside: avoid  
Would print cleanly (18 pages as expected)

---

## 3. EXACT SECTIONS NEEDING REWRITE

### Priority 1 (Critical) — Rewrite for Language Tone
- ❌ **Executive Summary:** Reduce "may" density (8 occurrences in first 2 paragraphs). Increase active voice. Make opening more authoritative.
- ❌ **Operating Pattern:** "May continue refining," "may also be a tendency" → Replace with present-tense description of the pattern.
- ❌ **Growth Edge:** "Should not be confused" → "is distinct from" (remove prescriptive tone, add descriptive certainty)

### Priority 2 (High) — Compartmentalization Layer
- ❌ **All 12 sections:** Add internal structure markers (not visible in final, but informing the prose):
  - Core Read (what this is)
  - What This Creates (consequences/manifestations)
  - What This May Cost (dark side)
  - Development Lever (specific next move)

Example (Decision Architecture currently):
```
Decision-making is analytical, structured, and evidence-seeking. 
The person is unlikely to rely on impulse...
[etc.]
```

Should be structured as:
```
CORE READ: Decision-making is analytical, structured, evidence-seeking.
[Behaviors that show this...]

WHAT THIS CREATES: You catch risks others miss...
[Specifics...]

WHAT THIS COSTS: Decision latency, analysis paralysis...
[When this fails...]

DEVELOPMENT LEVER: Distinguish reversible from irreversible decisions...
[Specific practice...]
```

### Priority 3 (Medium) — Specificity Upgrades
- ⚠️ **Blind Spots:** Make explicit: "You likely don't see: [1] the opportunity cost of your analysis [2] that others' resistance to structure is intelligent, not lazy [3] the emotional weight of your directness"
- ⚠️ **Facilitator Notes:** Replace generic "approach with respect" with specific coaching moves: "Watch for intellectualization. When they say 'we need more data,' listen for: Is this a real information gap or anxiety about uncertainty?"
- ⚠️ **What Full Profile Unlocks:** Concrete: "Would tell you whether your precision is cognitive, ethical, or anxiety-driven—each requires different development."

### Priority 4 (Low-Medium) — Polish
- ⚠️ **Recommended Next Step:** Rewrite opening. Currently: "The single most valuable next action is..." → Should be more compelling: "The unlock: One weekly decision lab where you practice calibrating process intensity to consequence."

---

## 4. EXACT PROMPT CHANGES FOR STAGE B (gpt-5.5)

### Current Prompt Problem
Current prompt is good but too permissive on certain patterns. Needs constraints added.

### Recommended Changes

**ADD THIS SECTION to Stage B system prompt:**

```
LANGUAGE CONSTRAINTS:
- Minimize "may" / "might" / "could" — use fewer than 5 per section
- Replace with: tends to, shows, creates, produces, demonstrates, does, will
- Use active voice (80%+): person shows X, not X may be shown
- Vary sentence openers: Don't repeat "The person" > vary with "They," "This system," "Built to," "Characterized by"
- Write with confidence: This IS [pattern], not This MIGHT BE [pattern]

COMPARTMENTALIZATION REQUIREMENTS:
- Each section must have implicit (not explicit) four-layer structure:
  1. Core Read: What is the fundamental pattern?
  2. Manifestation: How does it show up? (behaviors, defaults, tendencies)
  3. Cost: When does this create friction? What's the shadow side?
  4. Development: What's the specific growth move?
  
Example structure (hidden but informing the prose):
"[Layer 1: Core pattern] + [Layer 2: How it manifests] + [Layer 3: Costs when overplayed] + [Layer 4: Specific developmental practice]"

SPECIFICITY CONSTRAINTS:
- Avoid vague consultant language ("may approach," "should recognize," "is unlikely to land")
- Replace with behavioral specificity: Name behaviors, triggers, patterns
- Example: Instead of "may become anxious," write "When expectations are ambiguous, you feel dysregulated and need clarity before proceeding"

SCORE CONSTRAINTS:
- NO decimal scores in narrative text (35.9/100 is forbidden)
- Use code language only: V8, Fd4, F4, etc.
- When referring to patterns: Use names or code, never raw decimals

BLIND SPOT CONSTRAINTS:
- Blind spots are distinct from weaknesses
- Frame as: "What you're likely NOT seeing: [X], [Y], [Z]"
- Make actionable: "You don't realize your precision costs $X in team latency" vs abstract "you may underestimate"

REFLECTION PROMPT CONSTRAINTS:
- Facilitator sections should end with specific questions, not generic guidance
- Example: "What concerns remain unstated in meetings?" instead of "Check whether clarity has produced commitment"
```

**ALSO MODIFY the opening directive:**

Current: "Write exactly these 12 sections as a JSON object. Each section must be 300-400 words minimum"

Add: 
```
CRITICAL REQUIREMENT: This is a behavioral INSTRUMENT, not general advice.
- Every statement should be backed by the patterns in the analyst data
- Every recommendation should be operationalized (not theoretical)
- Tone: Confident diagnosis + specific development moves
- Authority: Speak with psychological precision, not consultant hedging
- Do NOT soften with "may," "might," "could" unless truly uncertain
```

---

## 5. RENDERER CHANGES NEEDED?

### Current Status: ✅ NO RENDERER CHANGES REQUIRED

**Why:**
- CSS handles dynamic height correctly (overflow: visible applied)
- Page breaks natural, no clipping
- Signature codes render cleanly
- System map displays properly
- Score display works

### One small refinement (optional)
**Current:** Page 2 shows raw decimal scores (34/100, etc.)  
**Fix:** Hide score decimals via CSS or data prep, keep codes only

This is a **DATA/CONTENT fix**, not a renderer fix. HTML/CSS fine as-is.

---

## 6. PAGE 2 (SYSTEM MAP) — RECOMMENDATION

### ✅ **KEEP AS-IS, NO CHANGES**

**Why:**
- 5-circle behavioral map clear and visual
- Color coding (primary/secondary/opposing) effective
- Tension note helpful
- System architecture well-communicated
- Spacing and layout perfect

**One caveat:** Remove raw decimal scores from circles (34/100 → just icon + code + name). This is content, not design.

---

## 7. FINAL RECOMMENDATION FOR NEXT PASS

### Phase 1D.1: Stage B Prompt Refinement (Coding)
**Goal:** Tighten language constraints in Stage B prompt

**What to change:**
1. Add language constraints section (minimize "may," favor active voice)
2. Add compartmentalization requirement (implicit 4-layer structure)
3. Add specificity constraint (name behaviors, not abstractions)
4. Remove score decimals from output
5. Strengthen confidence/authority in tone

**Expected impact:** 
- Less hedging (may → shows)
- More specific development moves
- Cleaner language
- Same word count, higher signal density

### Phase 1D.2: Decimal Score Removal (Content/Renderer)
**Goal:** Remove raw decimals from Page 2

**What to change:**
1. In stageB output: Remove decimal scores from pattern data
2. In renderer: Don't display score percentages, only codes

**Expected impact:** Doctrine compliance, cleaner Page 2 visual

### Phase 1D.3: Retest with Refined Prompts
**Goal:** Run dual-stage pipeline again with new constraints

**Expected results:**
- ~4,067 words (same or slightly more)
- Higher specificity
- Lower "may" count
- More actionable development moves
- Compartmentalization implicit but present

### Estimated effort: 1-2 hours (prompt refinement + test run)

---

## QUALITY SCORECARD

| Dimension | Score | Notes |
|-----------|-------|-------|
| Content Depth | 8/10 | Strong, detailed, psychologically sound |
| Language Precision | 6/10 | Good but hedged (too many "may"s) |
| Tone/Authority | 7/10 | Professional but could be more direct |
| Specificity | 7/10 | Good examples, could be more actionable |
| Layout | 9/10 | Excellent, no issues |
| Completeness | 9/10 | All 12 sections present, well-balanced |
| Doctrine Compliance | 7/10 | Good, but decimal scores violated (Page 2) |
| Development Clarity | 7/10 | Growth edges present but could be more tactical |
| Overall Instrument Grade | 7.5/10 | Strong report, refinements would push to 8.5-9 |

---

## SIGN-OFF

**Audit complete. No coding yet.**

Refinements needed are:
1. ✅ Stage B prompt tightening (language, specificity, confidence)
2. ✅ Remove decimal scores from Page 2
3. ✅ Retest to verify improvements

**Status:** READY FOR PHASE 1D CODING PASS

---

**Files to review:**
- HTML: `/Users/rrg/moremindmap-backend/temp/reports/mini-profile-v2-dual-stage-2026-05-04T18-06-39-438Z.html`
- Narrative JSON: `/Users/rrg/moremindmap-backend/temp/debug/stageB-narrative.json`
- Code to refine: `/Users/rrg/moremindmap-backend/engine/stageBExecutiveWriter.js`
