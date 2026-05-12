# CURRENT RECOVERY STATE

Last verified: May 11, 2026 15:46 MST

## Repository

Repo:
`https://github.com/RRG-systems/moremindmap-backend.git`

Git root:
`/Users/rrg/.openclaw/workspace`

Project folder:
`moremindmap-backend/`

Branch:
`main`

Current baseline commit:
`ce80ac0` — complete mini v2 html generation baseline

## Recovery Status

Recovery infrastructure is complete.

GitHub is now the source of truth.

## Verified Working Baseline

The Mini V2 HTML generation pipeline now works.

Test:
`node moremindmap-backend/engine/testGenerateMiniV2HTML.js`

Passing result:
- 10 pages generated
- 0 remaining placeholders
- HTML output generated
- ES module imports resolved

## Locked Reference Artifact

Canonical locked PDF reference is preserved at:

`moremindmap-backend/LOCKED_ARTIFACTS/mini-profile-v2-locked-reference/LOCKED 10 pages MORE MindMap - Mini Profile V2.pdf`

Mirror copy:

`moremindmap-backend/reference/mini-profile-v2-locked-reference/LOCKED 10 pages MORE MindMap - Mini Profile V2.pdf`

SHA256:
`25656674884e34a02329c136891b9657aff447d0b30323662e2efef98ae205ec`

## Working Files

Engine:
- `moremindmap-backend/engine/questionMap.js`
- `moremindmap-backend/engine/dimensionMap.js`
- `moremindmap-backend/engine/scoreAssessment.js`
- `moremindmap-backend/engine/generateMiniV2HTML.js`
- `moremindmap-backend/engine/testGenerateMiniV2HTML.js`

Templates:
- `moremindmap-backend/templates/mini-v2/page01-cover.html`
- `moremindmap-backend/templates/mini-v2/page02-operating-system-map.html`
- `moremindmap-backend/templates/mini-v2/page03-executive-summary.html`
- `moremindmap-backend/templates/mini-v2/page04-operating-pattern.html`
- `moremindmap-backend/templates/mini-v2/page05-decision-architecture.html`
- `moremindmap-backend/templates/mini-v2/page06-communication-style.html`
- `moremindmap-backend/templates/mini-v2/page07-system-under-strain.html`
- `moremindmap-backend/templates/mini-v2/page08-operating-environment-fit.html`
- `moremindmap-backend/templates/mini-v2/page09-facilitator-notes.html`
- `moremindmap-backend/templates/mini-v2/page10-full-profile-unlocks-dna.html`

Governance:
- `moremindmap-backend/SOURCE_OF_TRUTH.md`
- `moremindmap-backend/README_PROJECT_STATE.md`
- `moremindmap-backend/RECOVERY_TODO.md`
- `moremindmap-backend/MINI_V2_TEMPLATE_RECONSTRUCTION_PLAN.md`
- `moremindmap-backend/VERCEL_DEPLOYMENT_STATUS.md`

## Current Phase

Recovery is complete.

Next phase:
Visual template refinement against locked PDF reference.

## Next Engineering Sequence

1. Generate current HTML output.
2. Save output artifact.
3. Compare current HTML visually against locked PDF.
4. Refine templates toward locked PDF structure:
 - typography
 - spacing
 - page hierarchy
 - cards/sections
 - footer consistency
 - Page 2 operating map
 - Page 10 DNA section
5. Wire real scoring data into placeholders.
6. Rebuild page injection layer.
7. Add PDF rendering.
8. Add AI interpreter layer.
9. Restore Stripe/Formspree/email/download production flow.

## Do Not Do

- Do not return to stale reports mentioning HEAD `1bd0b55`.
- Do not claim locked artifact is missing.
- Do not start PDF rendering before visual HTML refinement.
- Do not clean contaminated files yet.
- Do not modify production deployment until render pipeline is stable.

## Product Naming / Pricing Note

"Mini V2" is an internal engineering label only.

Do not assume the public-facing product should be called "Mini."

Likely public-facing naming options:
- MORE MindMap Profile
- Behavioral Operating Profile
- Personal Operating Profile
- Strategic Operating Profile

Pricing is TBD. The 10-page output may justify positioning above the original mini-profile price point. Do not hard-code final pricing or public product name until approved.
