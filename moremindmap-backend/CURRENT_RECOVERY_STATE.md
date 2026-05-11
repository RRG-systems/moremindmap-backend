# CURRENT RECOVERY STATE
Last verified: May 11, 2026 13:53 MST

## Repository
Git root:
`/Users/rrg/.openclaw/workspace`

Project folder:
`moremindmap-backend/`

Remote:
`https://github.com/RRG-systems/moremindmap-backend.git`

Current branch:
`main`

## Verified Current State

### Locked Artifact
Verified present in GitHub and local repo:

`moremindmap-backend/LOCKED_ARTIFACTS/mini-profile-v2-locked-reference/LOCKED 10 pages MORE MindMap - Mini Profile V2.pdf`

Mirror copy:
`moremindmap-backend/reference/mini-profile-v2-locked-reference/`

This PDF is now the canonical visual reconstruction target.

### Governance Files Present
- SOURCE_OF_TRUTH.md
- README_PROJECT_STATE.md
- RECOVERY_TODO.md
- MINI_V2_TEMPLATE_RECONSTRUCTION_PLAN.md
- VERCEL_DEPLOYMENT_STATUS.md

### Templates
10 Mini V2 skeleton templates exist in:

`moremindmap-backend/templates/mini-v2/`

### Engine Files Present
- questionMap.js
- dimensionMap.js
- scoreAssessment.js
- generateMiniV2HTML.js
- testGenerateMiniV2HTML.js

### Current Known Blocker
`generateMiniV2HTML.js`

Issue:
ES module / __dirname handling prevents HTML generation test from succeeding.

Primary active task:
Fix Mini V2 HTML generation pipeline.

### Current Priority Order
1. Fix generateMiniV2HTML.js
2. Run testGenerateMiniV2HTML.js successfully
3. Restore placeholder injection pipeline
4. Compare generated HTML to locked PDF reference
5. Restore PDF rendering
6. Restore production pipeline

## Important Rule
Do NOT trust stale reports mentioning:
- HEAD 1bd0b55
- "no locked artifacts found"
- "audit files empty"

Those reports are outdated and superseded.

## Startup Procedure For Future Sessions

Always begin with:

1. Read SOURCE_OF_TRUTH.md
2. Read CURRENT_RECOVERY_STATE.md
3. Run:
 - git fetch origin main
 - git checkout main
 - git pull origin main
4. Verify locked PDF exists
5. Continue only from verified current state

