# CURRENT RECOVERY STATE

Last verified: May 12, 2026 12:31 MST

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
`44fcc98` — scale mini v2 anchor page visual composition

Previous checkpoints:
- `ce80ac0` — complete mini v2 html generation baseline (Baby1)
- `7eb9b64` — add page 1 and page 2 placeholder data, regenerate artifact
- `916aa2d` — strip jinja template comments from generated html
- `44fcc98` — scale mini v2 anchor page visual composition (Baby2)

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

## Current Phase - Baby2 Checkpoint

Infrastructure recovery complete.
Baseline HTML generation stable.
Anchor page scale & composition upgraded.

### Baby2 Known Strengths
- HTML pipeline stable and regenerating correctly
- Placeholder system: 0 unfilled placeholders
- Page validation: explicit pages.length check (10 pages)
- Template comment stripping: Jinja {# #} comments removed from output
- Shared CSS system established with premium styling
- Anchor pages (1, 2, 4) structurally upgraded with larger scale
- Generated artifact fresh and current (timestamp May 12 12:31)
- Page 1: premium cover identity, dark signature card, bordered core edge
- Page 2: map nodes (core engine, driver, stabilizer, opposing), tension system
- Page 4: gold vertical accent, navy divider, three-card row, development banner

### Baby2 Known Weaknesses
- Typography still web-like, not print-premium
- Page composition/spacing still compressed compared to locked reference
- Page 2 map positioning/layout needs major refinement (nodes overlap, tension lines crude)
- Footer system functional but not matching locked reference style
- Pages 3, 5-10 still skeletal/unrefined
- No PDF rendering yet
- No real scoring data wired
- No production deployment

### Next Phase
Page-by-page visual refinement against locked PDF reference.
Priority: Pages 1, 2, 4 closer to locked targets, then Pages 3, 5-10.

## Next Engineering Sequence

Baby2 → Baby3:
1. Refine Page 2 map layout (fix node positioning, improve tension visualization)
2. Refine Page 1 cover (closer to locked reference premium identity)
3. Refine Page 4 pattern (closer to locked reference cards/spacing)
4. Refine Pages 3, 5-10 sequentially against locked reference
5. Wire real scoring data into placeholders
6. Add PDF rendering (Puppeteer or equivalent)
7. Add AI interpreter layer
8. Restore Stripe/Formspree/email/download production flow
9. Deploy to production

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

## May 12, 2026 Evening Checkpoint — Page 2 Annotation Problem / Next Design Direction

**Session Context:** Evening checkpoint before family time. Preserving exact project state.

**Current HEAD:** `274eced` (fix page 2 annotation readability)

**Page 2 Status:**
- Circle geometry: ✅ Approved and locked
- Center circle: ✅ Good, unchanged
- Four outer circles: ✅ Geometrically aligned at equal radial distance
- System Tension Warning overlap with top circle: ✅ Approved, keep
- External annotation boxes: ❌ Failed after multiple attempts

**The Annotation Box Problem:**
Multiple attempts to position external text boxes beside circles have failed:
- Boxes drift off-page
- Boxes overlap circles
- Boxes become unreadable
- Connector lines add complexity without clarity
- Layout balance not achieved

**Current Artifact:**
- Path: `moremindmap-backend/releases/mini-v2-html-baseline/mini-v2-html-baseline.html`
- Size: 37K
- Timestamp: May 12, 2026 14:55
- Test status: Passing (0 placeholders, 10 pages)

**Proposed Next Design Direction:**
Abandon external annotation boxes. Instead:
1. Remove four external text boxes
2. Slightly enlarge four outer circles (110px → 130-140px)
3. Keep center circle size unchanged
4. Add concise 1-2 sentence descriptor text INSIDE each outer circle
5. Circle structure: role label + name + icon + descriptor
6. Makes circles self-contained and solves annotation placement problem

**Page 1 Enhancement Lock:**
Add YOUR PROFILE DNA decoder box to Page 1 Cover:
- Position: Between Profile Signature black bar and Core Edge section
- Purpose: Explain the 8-vector profile code (V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1)
- Tone: Proprietary diagnostic behavioral-systems language
- NOT motivational copy
- Decoder interprets integrated operating architecture

**Revised Launch Sequence:**
1. Resolve Page 2 annotation issue (likely via self-contained circles)
2. Add Page 1 YOUR PROFILE DNA decoder
3. Wire AI content generation to templates
4. Connect to production deployment pipeline
5. Iteratively upgrade Pages 3-10

**Critical Next Session Actions:**
1. Pull latest main
2. Read all checkpoint documentation files
3. Verify artifact still opens and renders
4. Make design decision: external boxes vs. self-contained circles
5. Implement chosen direction
6. Move to Page 1 DNA decoder
7. Shift focus to AI wiring
