# ROCKY inside THINK — Full Build Plan

## Overview
Embedding ROCKY as the live diagnostic/operator intelligence inside the THINK panel.

Rocky's job:
1. Explain what's happening (BRAIN, Arena, Nursery, MOLT)
2. Keep Nursery stocked with best babies
3. Build a playbook for tightening BRAIN over time

Rocky's constraints:
- Cannot override BRAIN (BRAIN controls money)
- Cannot place trades directly
- Must report missing visibility honestly
- Must give one recommended action per query

---

## Part 1: Backend Infrastructure
- [ ] Rocky reasoning engine (full access to system state)
- [ ] Data visibility layer (what Rocky can see)
- [ ] `/api/think/query` endpoint (live handler for THINK panel)
- [ ] Context assembly (current BRAIN, Arena, Nursery, MOLT state)

## Part 2: Frontend (THINK Panel Rebuild)
- [ ] Simple conversational UI (no buttons)
- [ ] Input + message scroll area
- [ ] Live responses from Rocky backend
- [ ] Auto-scroll and formatting

## Part 3: Rocky's Core Reasoning
- [ ] System diagnosis logic
- [ ] Plain English explanations
- [ ] Evidence-based confidence scoring
- [ ] Structured response format

## Part 4: Nursery Governance
- [ ] Baby evaluation logic
- [ ] Recommendation engine (keep/respawn/import)
- [ ] Diversity tracking
- [ ] Candidate health scoring

## Part 5: BRAIN Tightening Logbook
- [ ] High-signal observation capture
- [ ] Playbook entry generation
- [ ] Categorized patterns
- [ ] Confidence scoring on observations

## Part 6: Operator Playbook Generator
- [ ] Meta-learning from Rocky's observations
- [ ] Best practices extraction
- [ ] Future system teaching docs
- [ ] Operator confusion patterns

## Part 7: Response Rules + Safety
- [ ] Tone consistency (calm, direct, serious)
- [ ] Uncertainty quantification
- [ ] Action recommendation logic
- [ ] BRAIN safety enforcement

## Part 8: UI/Panel Design
- [ ] Header: "THINK — DIAGNOSTIC ENGINE"
- [ ] Body: conversational message area
- [ ] Input: free text box
- [ ] Formatting: clean, readable

## Part 9: Validation Suite
- [ ] Query test cases (BRAIN questions, Nursery decisions, BRAIN tightening)
- [ ] Visibility checks (Rocky reports missing data)
- [ ] Action recommendation tests
- [ ] Playbook entry generation tests

## Part 10: Integration + Live Testing
- [ ] Wire Rocky into dashboard
- [ ] Test with live BRAIN/Arena/Nursery state
- [ ] Validate playbook capture
- [ ] Deploy

---

## Key Data Rocky Needs Access To

### BRAIN State
- `dashboard_state['brain_state']` → current state (NORMAL/THROTTLE/STOP/FLAT)
- `dashboard_state['brain_reason_code']` → why it's in that state
- `dashboard_state['brain_reason_text']` → explanation
- `dashboard_state['brain_enforcement']` → what's being enforced (trade blocks, throttle, etc)
- Restart history
- FLAT/STOP/THROTTLE event log

### Arena State
- `dashboard_state['metrics']` → current KPIs
- Paper/shadow equity curves
- Recent trades
- Signal health
- Execution quality (slippage)
- Current strategy ID

### Nursery State
- Active baby candidates
- Baby metrics (trades, PnL, sign flips, degradation)
- Leaderboard
- Execution states
- Candidate diversity

### MOLT State
- Recent suggestions
- Import candidates
- Idea quality assessments

### Probation/Restart History
- Restarts triggered
- Reasons for restart
- Recovery patterns
- Failed candidates

---

## Rocky's Two Primary Jobs

### Job 1: System Diagnosis
Answer questions like:
- Why are we FLAT?
- Why did BRAIN throttle?
- Is the current strategy valid?
- Are Nursery babies stronger than Arena parent?
- What's the biggest risk right now?

### Job 2: Nursery Governance
Decide:
- Should we keep current Nursery babies?
- Should we respawn from Arena parent?
- Should we import a MOLT idea?
- What's the ideal Nursery composition?

---

## Rocky's Response Format

Every response should include:
1. **Diagnosis** — what's happening (1-3 sentences)
2. **Evidence** — why I think so (specific metrics/observations)
3. **Confidence** — how sure am I (0-1.0)
4. **Recommended Action** — next step to take

Example:
```
Diagnosis: We're FLAT because Arena strategy hit a divergence threshold.

Evidence:
  - Current paper/shadow divergence: 3.2% (threshold: 3.0%)
  - Arena has 47 trades, sign flip rate: 12.1%
  - BRAIN triggered FLAT 2 minutes ago

Confidence: 0.92

Recommended Action: Wait for divergence to recover below 3.0%, or respawn Nursery from baseline.
```

---

## Playbook Entry Schema

Each high-signal observation goes into the playbook:

```json
{
  "timestamp": "2026-04-22T15:35:00Z",
  "category": "BRAIN_RULE | NURSERY_RULE | REALITY_RULE | FAILURE_PATTERN | OPERATOR_GUIDE | UX_RULE",
  "observed_pattern": "early paper profitability with severe shadow divergence",
  "why_it_matters": "indicates overfitting to historical data without real friction modeling",
  "recommended_rule": "do not trust positive paper results unless shadow stays within acceptable divergence band",
  "confidence": 0.9,
  "source": "arena | nursery | molt | brain | operator",
  "context": "...",
  "tags": ["edge_validation", "paper_shadow", "divergence"]
}
```

---

## Nursery Health Checks

Rocky should evaluate Nursery based on:
- **Diversity** — are babies too similar? (clone detection)
- **Strength** — do babies beat Arena parent? (fitness scoring)
- **Realism** — do babies survive shadow execution? (sign flip rate)
- **Completeness** — is pool populated? (avoid empty nursery)

---

## Build Order

1. **Part 1** — Rocky backend + data access layer
2. **Part 2** — THINK panel frontend (simple UI)
3. **Part 3** — Rocky core reasoning + diagnostics
4. **Part 4** — Nursery governance logic
5. **Part 5** — Playbook/logbook system
6. **Part 6** — Operator playbook generator
7. **Part 7** — Response rules + safety
8. **Part 8** — Final UI polish
9. **Part 9** — Validation tests
10. **Part 10** — Integration + live deployment

---

## Start: Part 1 - Backend Infrastructure
