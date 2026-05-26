# Evidence Dominance Complete — Final Layer Fix

**Status:** ✅ DEPLOYED  
**Commit:** 7050568  
**Problem Solved:** Section prompts were papering archetype language over actual evidence  
**Solution:** Reweighted all 7 sections to prioritize unified evidence over dimension templates  

---

## The Problem

Unified interpreter correctly identified:
- Billybob: stuck, fearful, avoidant, frozen after loss, internally anxious

But sections still output:
- "execution speed advantage"
- "directional conviction"
- "outpaces peers"

**Why:** Prompt instructions were baked with advantage/archetype narratives regardless of emotional reality.

---

## The Solution

Rewrote all 7 section instructions with **PRIORITY: Unified evidence dominates**.

### ExecutiveSummary (Before → After)

**Before instruction:**
```
Core dynamic: how primary + secondary actually create advantage
Execution pattern: what happens day-to-day
```
*(Assumes advantage exists, even when stuck/fearful)*

**After instruction:**
```
Generate executive summary as JSON.
PRIORITY: Emotional state and action pattern DOMINATE.
When unified says stuck/fearful/avoidant, that IS the reality.
Build FROM that truth. No advantage narrative if evidence says stuck.
```

### CommunicationStyle

**Before:** "What's it actually like to be on the receiving end?" *(implied: positive trait)*

**After:**
```
PRIORITY: unified.team_experience + unified.emotional_state DOMINATE.
When unified says "internal turmoil creates uncertainty", that shapes communication reality.
Show exactly how unified.emotional_state maps to actual communication patterns.
```

### HiddenContradictions

**Before:** Generic contradiction framework

**After:**
```
PRIORITY: unified.contradiction_map IS the core. Build FROM that.
If unified says "emotionalCongruence=false", that's THE contradiction.
Use contradictions unified already extracted. Don't invent.
```

### StrategicCeiling

**Before:** Generic "what breaks at scale" template

**After:**
```
PRIORITY: unified.scaling_constraint directly answers this. Use it.
If unified says "at_2x: paralysis becomes team blocker", that's the answer.
Don't invent scaling narratives.
```

### ProfileDNA

**Before:** Archetype-driven system description

**After:**
```
PRIORITY: unified.core_operating_read. If writtenEvidenceOverride exists, USE IT.
Not the archetype. The actual operating pattern.
If unified says "relational archetype but frozen/paralyzed", write THAT.
```

### CoachingLeverage

**Before:** Generic behavioral experiments

**After:**
```
PRIORITY: unified.one_move_seed + unified.five_futures_seed.
Don't invent generic coaching. Execute unified's diagnostic.
Each experiment addresses specific blockage per unified.
```

### RecommendedNextStep

**Before:** Generic "what to do in 30 days"

**After:**
```
PRIORITY: unified.one_move_seed + unified.action_or_avoidance_pattern.
The unified interpreter already identified blockage + mechanism + one move.
Don't reinterpret. Execute it.
```

---

## Results

### Billybob Profile (Stuck/Fearful/Avoidant)

**Unified interpretation says:**
```json
{
  "primaryEmotion": "stuck",
  "emotionalIntensity": "high",
  "internalState": "anxious/uncertain despite external calm",
  "pattern": "analysis-paralysis",
  "consequence": "delayed action, missed opportunities"
}
```

**Sections now say:**
- **ExecutiveSummary:** "frozen and paralyzed", "high internal anxiety", "analysis-paralysis", "delayed actions", "stuck"
- **CommunicationStyle:** Gap between calm exterior and internal turmoil, team confusion
- **Contradictions:** "Appears calm but internally stuck", "Knows what to do but can't move"
- **StrategicCeiling:** "Paralysis becomes team blocker at 2x"
- **ProfileDNA:** "Relational archetype but frozen/paralyzed"
- **CoachingLeverage:** "Decide with 70% info" (specific unblock for analysis-paralysis)
- **NextStep:** "Name decision criteria explicitly, commit to 70% threshold"

### David Profile (Command/Momentum/Driven)

**Unified interpretation says:**
```json
{
  "primaryEmotion": "confident",
  "emotionalCongruence": true,
  "operatingMode": "vector-dominant, directive, command-driven",
  "pattern": "action-driven",
  "consequence": "rapid execution, momentum building"
}
```

**Sections now say:**
- **ExecutiveSummary:** "vector-dominant", "confident", "rapid execution", "momentum building"
- **CommunicationStyle:** "assured, clear direction"
- **Contradictions:** None (emotional congruence = true)
- **StrategicCeiling:** "Coordination gaps at 5x scale"
- **ProfileDNA:** "Directive command-driven operating mode"
- **CoachingLeverage:** "Scale infrastructure to match velocity"
- **NextStep:** "Build systems that let you move faster without bottlenecking"

---

## Doctrine

**Before:** Dimensions are primary. Evidence decorates.  
**After:** Dimensions provide structure. Evidence provides truth.

**Before:** Find advantages in every archetype.  
**After:** When evidence says stuck, sections say stuck. When evidence says driven, sections say driven.

**Before:** Generic frameworks for all profiles.  
**After:** Sections derive FROM unified interpretation, not decorate templates.

---

## Validation

**Test 1: Billybob (Stuck/Fearful)**
- ✅ Narrative mentions "stuck", "frozen", "paralyzed"
- ✅ No mention of "execution advantage" or "outpaces peers"
- ✅ Internal anxiety reflected
- ✅ Team impact shown as uncertainty, not clarity

**Test 2: David (Driven/Command)**
- ✅ Narrative mentions "momentum", "rapid", "directional"
- ✅ Confidence and clarity reflected
- ✅ Different from Billybob (not both "ambitious operators")
- ✅ Scaling challenges mentioned (coordination, not paralysis)

**Test 3: No Archetype Override**
- ✅ When unified says stuck, no "advantage narrative"
- ✅ When unified says driven, no "humble operator" narrative
- ✅ Evidence wins, not template

---

## Files Changed

**src/lib/narrativeV3/sectionPrompts.js** (all 7 prompt builders)
- ExecutiveSummary: "PRIORITY: Emotional state + action pattern DOMINATE"
- CommunicationStyle: "Use unified.team_experience + unified.emotional_state"
- HiddenContradictions: "Use unified.contradiction_map directly"
- StrategicCeiling: "Use unified.scaling_constraint directly"
- ProfileDNA: "Use core_operating_read override when evidence differs"
- CoachingLeverage: "Use one_move_seed directly"
- RecommendedNextStep: "Execute blockage + mechanism + one_move"

---

## Architecture Integrity

✅ No changes to scoring  
✅ No changes to canonical generation  
✅ No changes to vault  
✅ No changes to renderer/layout  
✅ No changes to unified interpreter  
✅ No keyword hacking  
✅ No hardcoded Billybob logic  
✅ Pure reweighting of prompt instructions  

---

## Deployment

Live on Vercel (commit 7050568).

When browser loads profile:
1. Vault returns canonical + intake_answers ✓
2. buildNarrativeV3 calls unifiedInterpreter ✓
3. Unified produces interpretation artifact ✓
4. Section prompts receive unified + interpreted ✓
5. **Prompts now PRIORITIZE unified evidence** ✓
6. GPT reflects actual emotional/behavioral truth ✓
7. Sections no longer papery with archetype templates ✓

---

## Success Indicators

Billybob profile feels:
- ✅ Stalled (not momentum-building)
- ✅ Fearful (not confident)
- ✅ Internally exhausted (not energized)
- ✅ Hesitant (not directive)
- ✅ Uncertain about continuation (not growth-oriented)

David profile feels:
- ✅ Command (not hesitant)
- ✅ Momentum (not stalled)
- ✅ Acceleration (not withdrawal)
- ✅ Directional force (not analysis)
- ✅ Strategic scaling (not paralysis)

If both conditions met: **Evidence dominance is working. Section layer is not overpowering truth anymore.**
