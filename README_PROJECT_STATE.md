# README_PROJECT_STATE.md — MORE MindMap May 2026 (CHECKPOINT)

**Last Checkpoint:** 2026-05-25 10:43 MST  
**Overall Status:** ✅ LIVE PIPELINE — Questions 25-28 Updated  

---

## What's Shipping Now

### 1. Profile Generation Pipeline ✅ (Scoring Verified)
- Assessment submission: HTTP 200 → job_id
- Async job polling: Real-time progress updates
- Canonical profile generation: Profile ID created with REAL dimension scores
- WebProfileReport rendering: 2-page behavioral profile with authentic scores
- Manual retrieval: Get profile by ID anytime (vault-backed)

**Live Test:** Profile MM-20260524-rf2xqct1 (2026-05-23 22:42 MST)  
**Verified:** Scores differentiate by assessment answers (not hardcoded 5s)

### 2. Report Structure ✅
**Page 1:**
- Profile DNA
- Executive Summary
- Behavioral Dimensions (with real dimension scores)
- Communication Style / Operating Pattern

**Page 2:**
- Hidden Contradictions
- System Under Strain
- Strategic Ceiling
- Coaching Leverage
- Recommended Next Step

**Footers:** Page markers + metadata tracking + V3 source

### 3. Data Persistence ✅
- Job storage: Redis (async job state with real profileInput)
- Profile vault: Redis (long-term retrieval with real scores)
- Scoring: Calculated by buildProfileInput, stored in profileInput.dimension_scores
- Fallback: Neutral 2.5 (not inflated 5) if missing

### 4. Scoring Integrity ✅ (JUST FIXED)
- Real dimension scores extracted from assessment answers
- buildProfileInput calculates scores; executeCanonicalGeneration uses them
- Profile differentiation preserved (no collapse to all 5s)
- Behavioral authenticity restored

---

## Current Phase: Visual Ascension Pass 2

**Status:** Ready to begin (no blockers)  
**What's done:**
- Two-page layout structure complete
- Section positioning defined
- Page breaks configured
- All 7 narrative sections working with real data

**What's pending:**
- Typography and styling
- Color hierarchy
- Visual hierarchy refinement
- Design review checkpoint

---

## Session Recovery Summary

| Issue | Caused By | Fixed By | Commit |
|-------|-----------|----------|--------|
| Vercel cold-start failure | Syntax errors in vault modules | Corrected object assignment + quotes | d06b88f |
| Profiles not retrievable | No vault save in canonical generation | Added dynamic vault save | 6e2b78e |
| Scores hardcoded to 5 | buildMinimalCanonical ignored profileInput | Extract real scores from profileInput | 116b4de |

**All fixed. No workarounds. Clean architecture.**

---

## Architecture Decisions (Locked)

### Profile Format: mm-YYYYMMDD-XXXXXXXX
- Lowercase standard (new profiles)
- Fallback support for MM-* legacy profiles
- Date-based organization
- Redis key: `vault:profile:{id}`

### Scoring Pipeline
```
Assessment answers → buildProfileInput.buildDimensionScores()
  ↓
Job.profileInput.dimension_scores (real values stored)
  ↓
executeCanonicalGeneration extracts scores
  ↓
canonical_profile.vector_scores (authentic, not hardcoded)
  ↓
WebProfileReport renders with real score context
```

### Canonical Structure (Verified)
```javascript
{
  profile_id: 'mm-YYYYMMDD-XXXXXXXX',
  metadata: {
    assessment_version: 'mini-v2',
    generated_at: ISO timestamp,
    job_id,
    generation_mode: 'emergency_inline'
  },
  vector_scores: { vector, signal, fidelity, velocity, leverage, flex, framework, horizon },
  ranked_dimensions: [ sorted by real score, not hardcoded ],
  narrative_profile: {
    profileDNA,
    executiveSummary,
    operatingPattern,
    decisionArchitecture,
    communicationStyle,
    systemUnderStrain,
    hiddenContradictions,
    strategicCeiling,
    coachingLeverage,
    recommendedNextStep
  },
  ... (30+ additional fields)
}
```

### Two Rendering Paths (NOW UNIFIED)
Before: Assessment path vs. Manual retrieval path (different)  
After: Both use WebProfileReport with real scores (same)

---

## Test Profiles (Both Verified Working)

| Profile | Type | Scores | Status |
|---------|------|--------|--------|
| MM-20260524-rf2xqct1 | Live assessment | Real (sanity fixed) | ✅ Verified |
| MM-20260523-mqlev9c9 | Fallback test | Flat (old fallback) | ✅ Verified |

Both retrieve and render correctly.

---

## Deployment Status

**Branch:** main  
**Latest commits:**
- ec3b959 (memory checkpoint)
- 116b4de (scoring sanity fix)
- a8e5884 (recovery timeline)
- 2f97e5a (docs preservation)
- 6e2b78e (vault integration)
- d06b88f (syntax fixes)

**All pushed to origin/main.**

---

## Frontend Integration Points

### Endpoints
- `POST /api/moremindmap/mini-profile-v2` - Submit assessment
- `GET /api/moremindmap/mini-profile-v2-status?job_id=X` - Poll status
- `GET /api/moremindmap/retrieve-profile?id=X` - Get profile
- `POST /api/moremindmap/narrative-v3` - Generate narrative via GPT

### Component: WebProfileReport
- Loads profile by ID (with real scores)
- Calls narrative-v3 for each section
- Renders 2-page layout
- Displays authentic dimension scores

### Flow
```
Assessment Form
  ↓
Submit → job_id
  ↓
Poll status (job_id)
  ↓ (when complete)
Load WebProfileReport (profile_id with real scores)
  ↓
Render 2-page report
```

---

## Support Notes

### If Profile Scores Look Wrong
- Check if using new profile ID (MM-20260524-rf2xqct1 or later)
- Old profile (MM-20260523-mqlev9c9) has flat scores (before fix)
- New profiles should show differentiated scores

### If Retrieval Fails
1. Verify profile ID format: mm-YYYYMMDD-XXXXXXXX
2. Check Redis: `KEYS vault:profile:*`
3. Manual key lookup: `GET vault:profile:{id}`

### If WebProfileReport Doesn't Render
1. Verify narrative-v3 endpoint is responsive
2. Check canonical_profile has all 7 narrative_profile fields
3. Verify profile_id matches expected format

---

## What NOT to Change

- ✅ DO NOT: Touch mini-v2 pipeline (working perfectly)
- ✅ DO NOT: Change narrative-v3 GPT integration (working)
- ✅ DO NOT: Modify WebProfileReport rendering (verified)
- ✅ DO NOT: Alter scoring logic (just fixed)
- ⏳ DO: Proceed with visual design refinement
- ⏳ DO: Monitor real score differentiation in next assessments

---

## Next Milestones

### Immediate (This Week)
- Visual design refinement (styling + typography)
- Design review checkpoint
- Implementation of approved designs

### Near-term (Next Week)
- Monitor real score quality
- Gather user feedback on authenticity
- Plan for future scoring refinements

### Future
- Historical profile comparison
- Advanced personalization
- Export/sharing features
- Integration pipelines

---

**Status:** Production live, scoring sanity verified, rollback-safe.  
**Next:** Visual Ascension Pass 2 (styling).  
**Blocked on:** Nothing.

---

For detailed technical info, see:
- SOURCE_OF_TRUTH.md — Infrastructure verification
- CURRENT_RECOVERY_STATE.md — Recovery timeline and decisions
- MINI_V2_VISUAL_GAP_REPORT.md — (Now outdated—scoring is fixed)

---

# NARRATIVE ARCHITECTURE SNAPSHOT (2026-05-25)

## Section Inventory (7 Live + 0 Omitted)

**Currently Rendering:**
- profileDNA (GPT)
- executiveSummary (GPT)
- communicationStyle (GPT)
- hiddenContradictions (GPT)
- systemUnderStrain (GPT)
- strategicCeiling (GPT)
- coachingLeverage (GPT)
- recommendedNextStep (GPT)

**Omitted from Render (exist in dossier):**
- operatingPattern (fallback only)
- decisionArchitecture (calculated, not narrated)
- Full pressure mechanics (only pressure_manifestation surfaces)
- Scaling readiness (role_fit_analysis exists but not narrated)
- Risk profile (hidden_risk_patterns exist but not rendered)

## Intelligence Embedded in Dossier (Not Surfaced)

**Dossier fields that populate but don't render:**
- stall_patterns (avoidance, frustrations, coping)
- contradictions (array of {type, cost, resolution_attempted})
- stress_patterns (how each dimension shifts under load)
- communication_style (clarity, directness, listening)
- leadership_readiness (delegation, team development)
- role_fit_analysis (current fit, ceiling reason)
- future_growth_constraints (internal, external, timeline)
- coaching_leverage_points (array of specific interventions)
- hidden_risk_patterns (unvoiced concerns)
- execution_identity (speed, quality, risk, decision style)

**Evidence chains mapped but not narrated:**
- delegation_resistance (Q24→Q26→Q28)
- relational_friction (Q7, Q26, Q28)
- execution_vs_strategy_gap (Q23→Q24→Q25)
- leadership_ceiling (business_reality × systems_accountability)
- communication_authenticity (Q25 intent vs Q2 behavior)

## Compression Impact

Average section: **~135 words** (950 total ÷ 7)  
Target range: **150-250 words per section**  
Loss: **~20-30% from full capability**

Most loss in:
1. hiddenContradictions (multiple contradictions compress heavily)
2. systemUnderStrain (pressure mechanics for all 8 dimensions not unpacked)
3. strategicCeiling (multiple constraint types collapse to one)

## Future Components Ready for Extraction

**Tier 1 (from dossier, no new calc):**
- All 8 dimensions under pressure (instead of just primary/secondary)
- Constraint type (belief/skill/environment/time)
- Scaling timeline to ceiling
- How others experience you (first impression + misunderstandings)
- Relational blind spots

**Tier 2 (evidence reconstruction):**
- Delegation resistance (3-question chain unpacked)
- Relational friction (pattern across 3+ questions)
- Execution-strategy gap (coherence analysis)
- Leadership ceiling (capacity assessment)

**Tier 3 (scenario-based):**
- Five futures (best/probable/pressure/breakdown/transformation cases)
- The One Move (single highest-leverage intervention)
- Resistance pattern (what will pull back)
- Cost of inaction

---

**Architecture Status:** Audit complete. No redesign. Infrastructure holds. Ready for expansion planning.

---

# EXTRACTION LAYER BUILD CHECKLIST (2026-05-25)

## Phase 1: Core Extraction Functions (Tier 1-2 Components)

**File:** `api/engine/canonical/extractIntelligence.js`

- [ ] extractOperatingSystem() - Components 1-5
  - [ ] Primary driver extraction
  - [ ] Secondary stabilizer extraction
  - [ ] Opposing patterns extraction
  - [ ] Core tradeoff extraction
  - [ ] All vector scores mapping

- [ ] extractWorldExperience() - Components 6-10
  - [ ] Perception filter (signal score → what noticed first)
  - [ ] Information processing speed (velocity + fidelity)
  - [ ] Decision formation path (vector + framework)
  - [ ] Time horizon bias (horizon score)
  - [ ] Risk calibration (flex + vector)

- [ ] extractPressureMechanics() - Components 21-25
  - [ ] Primary system under load
  - [ ] Secondary system override logic
  - [ ] All 8 dimensions under pressure
  - [ ] Breaking point identification
  - [ ] Recovery trajectory estimation

## Phase 2: Relational & Evidence Extraction (Tier 2-3 Components)

- [ ] extractOthersExperience() - Components 11-15
  - [ ] First impression signature (primary → external perception)
  - [ ] Communication clarity vs brevity (fidelity + velocity)
  - [ ] Listening pattern (signal + flex vs vector)
  - [ ] Trust-building speed (signal × flex)
  - [ ] Misunderstanding pattern (Q25 evidence)

- [ ] extractKnowingOthers() - Components 16-20
  - [ ] People-reading capacity (signal + attention)
  - [ ] Relational blind spots (contradictions + Q7)
  - [ ] Delegation readiness (Q26→Q28 evidence chain)
  - [ ] Team development orientation
  - [ ] Boundary style (framework + vector)

- [ ] extractContradictions() - Component 26
  - [ ] Unpack contradictions array
  - [ ] Know vs Apply gap extraction
  - [ ] Emotional cost identification
  - [ ] Resolution attempts tracking
  - [ ] Evidence chain (Q23→Q24→Q25)

## Phase 3: Organizational & Strategic Extraction (Tier 3-4 Components)

- [ ] extractTeamConsequences() - Components 27-29
  - [ ] How operator affects teams (primary + relational patterns)
  - [ ] Friction points with other types (opposing patterns)
  - [ ] Optimal team composition inference

- [ ] extractScalingConstraint() - Component 30
  - [ ] Capacity ceiling identification (Q26 × Q28)
  - [ ] Constraint type classification (belief/skill/environment/time)
  - [ ] Timeline to ceiling estimation
  - [ ] Required shift identification
  - [ ] Expansion pathway definition

- [ ] extractFacilitatorNotes() - Systemic Architecture
  - [ ] Compatible environments (execution_identity → environment design)
  - [ ] Communication structures (reduce friction)
  - [ ] Accountability architectures (match operating style)
  - [ ] Team compositions (balance weaknesses)
  - [ ] Workflow matches (speed preference alignment)

## Phase 4: Trajectory & Intervention Extraction (Tier 4-5 Components)

- [ ] extractFiveFutures() - Scenario Simulation
  - [ ] Best case scenario (optimized, no constraints)
  - [ ] Probable case (current trajectory + current constraints)
  - [ ] Pressure case (2x demand, systems under load)
  - [ ] Breakdown case (primary system fails)
  - [ ] Transformation case (different role/environment)

- [ ] extractOneMove() - Intervention Logic
  - [ ] Highest-leverage move identification
  - [ ] Unlock mechanism inference
  - [ ] Resistance pattern identification
  - [ ] Timeline to impact (3mo/6mo/12mo)
  - [ ] Success signal definition
  - [ ] Cost of inaction inference

## Phase 5: Helper Functions & Utilities

- [ ] identifyCapacityCeiling(q26, q28, roleFit)
- [ ] classifyConstraint(ceiling, growthConstraints)
- [ ] estimateTimelineToCeiling(growthRate, ceiling)
- [ ] identifyRequiredShift(constraintType, constraints)
- [ ] inferUnlockMechanism(leveragePoint, constraint)
- [ ] identifyResistancePattern(leverage, contradictions, stress)
- [ ] defineSuccessMetric(leveragePoint, mechanism)
- [ ] inferCostOfInaction(riskPatterns, constraint)
- [ ] simulateBestCase(currentState)
- [ ] simulateProbableCase(currentState, constraints)
- [ ] simulatePressureCase(currentState, stressPatterns)
- [ ] simulateBreakdownCase(currentState, stressPatterns)
- [ ] simulateTransformationCase(currentState, roleFit)
- [ ] inferTeamEffect(primary, secondary, delegationPattern)
- [ ] inferFrictionPoints(opposing, relationalPattern)
- [ ] inferOptimalTeam(primary, frictionPoints)
- [ ] extractMisunderstandingEvidence(q25, commStyle)

## Phase 6: Dossier Gap Population

**Required before full extraction:**

- [ ] Populate future_growth_constraints
  - [ ] Extract from Q26 (business reality size, growth trajectory)
  - [ ] Extract from Q28 (systems readiness, fragility points)
  - [ ] Calculate internal vs external constraints
  - [ ] Estimate timeline to hit constraints

- [ ] Populate hidden_risk_patterns
  - [ ] Identify from contradictions (unresolved tensions)
  - [ ] Identify from pressure analysis (breaking points)
  - [ ] Identify from evidence chains (unvoiced concerns)
  - [ ] Calculate likelihood and impact

- [ ] Populate execution_identity
  - [ ] Extract from Q23 (what separates high performers)
  - [ ] Extract from Q24 (stall patterns, frustrations)
  - [ ] Extract decision style patterns
  - [ ] Calculate speed/quality/risk preferences

- [ ] Populate role_fit_analysis
  - [ ] Calculate current role fit score
  - [ ] Identify ceiling reasons
  - [ ] Identify alternative roles with higher fit
  - [ ] Map dimension requirements per role type

- [ ] Populate leadership_architecture
  - [ ] Extract from Q26 (leadership questions)
  - [ ] Extract delegation patterns
  - [ ] Extract team development orientation
  - [ ] Extract accountability style

## Phase 7: Integration & Testing

- [ ] Add extractBehavioralIntelligence() call to executeCanonicalGeneration.js
- [ ] Store extracted intelligence in canonical_profile.behavioral_intelligence
- [ ] Test extraction on MM-20260524-rf2xqct1 (live profile)
- [ ] Verify confidence tier labeling
- [ ] Verify causal chain propagation
- [ ] Test extraction on MM-20260523-mqlev9c9 (benchmark profile)
- [ ] Compare extraction quality across profiles

## Phase 8: API Exposure (Optional)

- [ ] Create /api/moremindmap/extract-intelligence endpoint
- [ ] Accept profile_id parameter
- [ ] Return extracted intelligence JSON
- [ ] Add to retrieve-profile response (optional field)

## Phase 9: Documentation

- [ ] Update SOURCE_OF_TRUTH.md with extraction status
- [ ] Document extraction logic per domain
- [ ] Document confidence tier mapping
- [ ] Document causal propagation chains
- [ ] Document dossier field requirements

---

**Status:** Architecture complete. Implementation ready. Zero rendering changes required.

---

# INSERTION POINT VERIFICATION & IMPLEMENTATION SEQUENCE (2026-05-25)

## Recommended Insertion Point: BACKEND (executeCanonicalGeneration)

**File:** `api/engine/canonical/executeCanonicalGeneration.js`  
**Line:** ~73 (after buildMinimalCanonical, before vault save)

### Current Code (Line 65-80):
```javascript
const canonical_profile = buildMinimalCanonical(job.profileInput || {}, job.job_id)
canonical_profile.profile_id = profile_id
canonical_profile.metadata.profile_id = profile_id

canonical_diagnostics.generation_success = true
canonical_diagnostics.generation_time_ms = Date.now() - startTime
canonical_diagnostics.success = true
canonical_diagnostics.profile_id = profile_id
canonical_diagnostics.profile_signature = '5_8'

// Save to vault
const { saveCanonicalProfile } = await import('./vault/saveCanonicalProfile.js')
await saveCanonicalProfile(profile_id, canonical_profile)
```

### Proposed Insertion:
```javascript
const canonical_profile = buildMinimalCanonical(job.profileInput || {}, job.job_id)
canonical_profile.profile_id = profile_id
canonical_profile.metadata.profile_id = profile_id

// ⭐ NEW: Extract behavioral intelligence
const { extractBehavioralIntelligence } = await import('./extractIntelligence.js')
try {
  const behavioral_intelligence = extractBehavioralIntelligence(canonical_profile)
  canonical_profile.behavioral_intelligence = behavioral_intelligence
  trace.push('behavioral_intelligence_extracted')
} catch (extractError) {
  console.warn('[CANONICAL] Intelligence extraction failed:', extractError)
  trace.push('behavioral_intelligence_extraction_failed')
  // Continue without extraction (non-blocking)
}

canonical_diagnostics.generation_success = true
// ... rest unchanged
```

**Impact:**
- +50-200ms to canonical generation (acceptable)
- +5-10KB to vault storage per profile (acceptable)
- Zero impact on rendering (new field ignored)
- Non-blocking (continues on extraction error)

---

## Phase-by-Phase Implementation (6 Weeks)

### Week 1: Core Extraction (Tier 1)
**Goal:** Extract high-confidence components (no dossier gaps needed)

- [ ] Day 1-2: Create extractIntelligence.js skeleton
  - [ ] File: api/engine/canonical/extractIntelligence.js
  - [ ] Entry function: extractBehavioralIntelligence()
  - [ ] Return structure: { domains: {}, confidence_tiers: {}, extraction_timestamp }

- [ ] Day 3: Implement extractOperatingSystem()
  - [ ] Extract primary_driver, secondary_stabilizer, opposing_patterns
  - [ ] Extract core_tradeoff from dimension_tradeoffs[0]
  - [ ] Test on MM-20260524-rf2xqct1

- [ ] Day 4: Implement extractWorldExperience()
  - [ ] Perception filter (signal score)
  - [ ] Decision formation (vector + framework)
  - [ ] Time horizon (horizon score)
  - [ ] Risk calibration (flex + vector)
  - [ ] Test on both profiles

- [ ] Day 5: Implement extractPressureMechanics()
  - [ ] Primary under load (pressure_manifestation)
  - [ ] Secondary override (when/how)
  - [ ] Breaking point estimation
  - [ ] Recovery trajectory
  - [ ] Test on both profiles

- [ ] Week 1 Milestone: Core extraction working, stored in vault

### Week 2: Evidence Chain Extraction (Tier 2-3)
**Goal:** Reconstruct evidence chains from dossier + questions

- [ ] Day 1: Implement extractOthersExperience()
  - [ ] First impression (primary → external perception)
  - [ ] Communication clarity (fidelity + velocity)
  - [ ] Listening pattern (signal vs vector)
  - [ ] Trust-building speed (signal × flex)
  - [ ] Test on both profiles

- [ ] Day 2-3: Implement extractKnowingOthers()
  - [ ] People-reading capacity (signal + attention_direction)
  - [ ] Relational blind spots (contradictions + Q7)
  - [ ] Delegation readiness (inferEvidenceMap.delegation_resistance)
  - [ ] Team development orientation (leadership_readiness)
  - [ ] Boundary style (framework + vector)
  - [ ] Test on both profiles

- [ ] Day 4: Implement extractContradictions()
  - [ ] Unpack contradictions array
  - [ ] Know vs Apply gap extraction
  - [ ] Emotional cost identification
  - [ ] Resolution attempts
  - [ ] Evidence chain (Q23→Q24→Q25)
  - [ ] Test on both profiles

- [ ] Day 5: Integration test
  - [ ] Verify extraction on new assessment
  - [ ] Verify vault save includes all domains
  - [ ] Verify retrieve-profile returns extraction
  - [ ] Verify renderer ignores new field

- [ ] Week 2 Milestone: Evidence chains extracting, quality verified

### Week 3: Dossier Gap Population
**Goal:** Populate missing dossier fields for Tier 3-4 extraction

- [ ] Day 1-2: Populate future_growth_constraints
  - [ ] Extract from Q26 (business_operating_reality)
  - [ ] Extract from Q28 (systems_accountability)
  - [ ] Calculate internal vs external constraints
  - [ ] Estimate timeline to hit constraints
  - [ ] Add to buildProfileInput or executeCanonicalGeneration
  - [ ] Test on new assessment

- [ ] Day 2-3: Populate hidden_risk_patterns
  - [ ] Identify from contradictions (unresolved tensions)
  - [ ] Identify from pressure analysis (breaking points)
  - [ ] Identify from evidence chains (unvoiced concerns)
  - [ ] Calculate likelihood and impact
  - [ ] Add to buildProfileInput or inferEvidenceMap
  - [ ] Test on new assessment

- [ ] Day 4: Populate execution_identity
  - [ ] Extract from Q23 (high performer separation)
  - [ ] Extract from Q24 (stall patterns, frustrations)
  - [ ] Extract decision style patterns
  - [ ] Calculate speed/quality/risk preferences
  - [ ] Add to buildProfileInput
  - [ ] Test on new assessment

- [ ] Day 5: Populate role_fit_analysis + leadership_architecture
  - [ ] Calculate current role fit score
  - [ ] Identify ceiling reasons
  - [ ] Identify alternative roles with higher fit
  - [ ] Map dimension requirements per role type
  - [ ] Extract from Q26 (leadership questions)
  - [ ] Add to buildProfileInput or executeCanonicalGeneration
  - [ ] Test on new assessment

- [ ] Week 3 Milestone: All dossier gaps populated, ready for Tier 3-4

### Week 4: Organizational & Trajectory Extraction (Tier 3-5)
**Goal:** Extract organizational consequences and trajectory simulation

- [ ] Day 1: Implement extractTeamConsequences()
  - [ ] How operator affects teams (primary + relational patterns)
  - [ ] Friction points with other types (opposing patterns)
  - [ ] Optimal team composition inference
  - [ ] Test on multiple profiles

- [ ] Day 2: Implement extractScalingConstraint()
  - [ ] Capacity ceiling identification (Q26 × Q28)
  - [ ] Constraint type classification (belief/skill/environment/time)
  - [ ] Timeline to ceiling estimation
  - [ ] Required shift identification
  - [ ] Expansion pathway definition
  - [ ] Test on multiple profiles

- [ ] Day 3: Implement extractFacilitatorNotes()
  - [ ] Compatible environments (execution_identity → environment design)
  - [ ] Communication structures (reduce friction)
  - [ ] Accountability architectures (match operating style)
  - [ ] Team compositions (balance weaknesses)
  - [ ] Workflow matches (speed preference alignment)
  - [ ] Test on multiple profiles

- [ ] Day 4: Implement extractFiveFutures()
  - [ ] Best case scenario (optimized, no constraints)
  - [ ] Probable case (current trajectory + constraints)
  - [ ] Pressure case (2x demand, systems under load)
  - [ ] Breakdown case (primary system fails)
  - [ ] Transformation case (different role/environment)
  - [ ] Test on multiple profiles

- [ ] Day 5: Implement extractOneMove()
  - [ ] Highest-leverage move identification
  - [ ] Unlock mechanism inference
  - [ ] Resistance pattern identification
  - [ ] Timeline to impact (3mo/6mo/12mo)
  - [ ] Success signal definition
  - [ ] Cost of inaction inference
  - [ ] Test on multiple profiles

- [ ] Week 4 Milestone: Full extraction pipeline complete (11 domains, 30 components)

### Week 5: Quality & Integration
**Goal:** Validate extraction quality, expose via API

- [ ] Day 1: Quality validation
  - [ ] Confidence tier labeling correct
  - [ ] Causal propagation logic working
  - [ ] Evidence chains traceable
  - [ ] No extraction failures on diverse profiles

- [ ] Day 2: API endpoint
  - [ ] Create /api/moremindmap/extract-intelligence?profile_id=...
  - [ ] Returns behavioral_intelligence JSON
  - [ ] Cache extraction results (Redis, 1 hour TTL)
  - [ ] Test on multiple profiles

- [ ] Day 3: Documentation
  - [ ] Update SOURCE_OF_TRUTH.md (extraction status)
  - [ ] Document extraction logic per domain
  - [ ] Document confidence tier mapping
  - [ ] Document causal propagation chains

- [ ] Day 4: Regression testing
  - [ ] Test on MM-20260524-rf2xqct1 (live production)
  - [ ] Test on MM-20260523-mqlev9c9 (legacy benchmark)
  - [ ] Verify backward compatibility (renderer unchanged)
  - [ ] Verify profile retrieval unchanged

- [ ] Day 5: Production deployment
  - [ ] Deploy to Vercel
  - [ ] Monitor extraction performance
  - [ ] Monitor vault storage usage
  - [ ] Monitor extraction errors

- [ ] Week 5 Milestone: Production-ready extraction, API live

### Week 6: Enhancement (Optional)
**Goal:** Use extracted intelligence to improve existing narrative

- [ ] Day 1-2: Enhance GPT prompts
  - [ ] Pass extracted intelligence to buildExecutiveSummaryPrompt
  - [ ] Pass to buildStrategicCeilingPrompt
  - [ ] Pass to buildCoachingLeveragePrompt
  - [ ] Test narrative quality improvement

- [ ] Day 3-4: Frontend display (optional)
  - [ ] Build component to display extracted intelligence
  - [ ] Progressive disclosure UI (tabs/expandable)
  - [ ] OR: Tooltip/hover details on existing sections

- [ ] Day 5: Future planning
  - [ ] Plan new renderer design (if needed)
  - [ ] Plan section expansion strategy
  - [ ] Plan multi-page architecture (if needed)

- [ ] Week 6 Milestone: Extraction enhancing existing narrative, roadmap for future

---

## Rollback Plan

If extraction causes issues:

1. **Immediate Rollback:**
   - Remove extractBehavioralIntelligence call from executeCanonicalGeneration
   - Deploy
   - Profiles generated after rollback: no behavioral_intelligence field
   - Profiles generated before rollback: still have field (ignored by renderer)

2. **Partial Rollback:**
   - Wrap extraction in try-catch (already done)
   - If extraction fails: log warning, continue without extraction
   - Non-blocking failure mode

3. **Data Rollback:**
   - Existing profiles in vault: unchanged
   - New profiles: no behavioral_intelligence field
   - No data migration needed

---

**Implementation Sequence Complete. Insertion point verified. Rollback plan documented. Ready for Week 1 start.**
