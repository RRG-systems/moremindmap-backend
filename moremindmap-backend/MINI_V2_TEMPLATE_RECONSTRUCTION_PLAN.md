# Mini V2 Template Reconstruction Plan

## Current Confirmed State

The MOREMindMap repository now has governance and recovery docs pushed to GitHub.

Confirmed:
- Git root: /Users/rrg/.openclaw/workspace
- Project folder: moremindmap-backend/
- Source-of-truth doc exists: moremindmap-backend/SOURCE_OF_TRUTH.md
- Project memory exists: moremindmap-backend/README_PROJECT_STATE.md
- Recovery TODO exists: moremindmap-backend/RECOVERY_TODO.md
- Audit tool exists and correctly reports NO MINI V2 TEMPLATES FOUND
- Surviving engine files copied:
 - moremindmap-backend/engine/questionMap.js
 - moremindmap-backend/engine/dimensionMap.js

## Missing Assets

The following must be rebuilt or restored:

- moremindmap-backend/templates/mini-v2/*.html
- moremindmap-backend/engine/scoreAssessment.js
- moremindmap-backend/engine/wiring/v3-injection-orchestrator.js
- moremindmap-backend/engine/wiring/validatePageInjection.js
- moremindmap-backend/engine/generateMiniV2HTML.js
- PDF renderer / Puppeteer utility
- Locked HTML artifact
- Production delivery flow

## Available Assets

Available:
- questionMap.js
- dimensionMap.js
- README_PROJECT_STATE.md
- SOURCE_OF_TRUTH.md
- RECOVERY_TODO.md
- User-saved locked 10-page PDF / visual reference

## Rebuild Strategy

### Phase 1 — Rebuild 10-Page Template

Create a clean Mini V2 template system based on the locked visual reference.

Pages:
1. Cover / Profile Signature
2. Behavioral Operating System Map
3. Executive Summary
4. Operating Pattern
5. Decision Architecture
6. Communication Style
7. System Under Strain
8. Operating Environment Fit
9. Facilitator Notes
10. Full Profile Unlocks + Operating DNA

Each page should have:
- stable page wrapper
- print-safe dimensions
- consistent footer
- explicit placeholder fields
- no hidden external dependencies

### Phase 2 — Rebuild Scoring

Recreate `scoreAssessment.js` from:
- `questionMap.js`
- `dimensionMap.js`

Output must include:
- raw scores
- normalized percentages
- ranked dimensions
- primary
- secondary
- suppressed
- invalid flag
- written responses

### Phase 3 — Rebuild Injection

Create:
- `engine/wiring/v3-injection-orchestrator.js`
- `engine/wiring/validatePageInjection.js`

Goal:
- deterministic field coverage first
- no AI yet
- all template placeholders supplied
- no undefined/null leakage

### Phase 4 — HTML/PDF Generation

Create:
- `engine/generateMiniV2HTML.js`
- PDF render utility

Success:
- HTML generated
- PDF generated
- visual match to locked PDF reference
- no clipping
- Page 10 DNA visible
- footer stable

### Phase 5 — AI Interpreter Layer

Only after deterministic system works.

Purpose:
Analyze HOW users answer, especially written responses:
- Q2
- Q6
- Q10
- Q15
- Q20
- Q24

AI should produce constrained page-level fields, not uncontrolled long essays.

### Phase 6 — Production Flow

Wire:
- Stripe
- Formspree
- email PDF copy
- download path
- frontend handoff
- promo code logic

## Governance Rules

- No empty success files.
- No destructive cleanup.
- No deleting contamination yet.
- No adding AI before deterministic render works.
- Commit and push every durable checkpoint.
- Verify with raw Git/file proof.
- Preserve first, classify second, move/copy third.
