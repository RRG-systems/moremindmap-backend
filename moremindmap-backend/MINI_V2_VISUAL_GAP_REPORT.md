# Mini V2 Visual Gap Report

Last updated: May 12, 2026

## Executive Summary

The current generated HTML baseline is structurally functional but visually skeletal. It proves the generator, placeholder system, and 10-page output path work, but it does not yet resemble the locked Mini V2 PDF reference.

The locked PDF is the canonical visual and product target. It contains a premium 10-page behavioral operating profile with strong typography, modular report sections, detailed interpretive copy, structured cards, page-level hierarchy, a distinctive Page 2 Behavioral Operating System Map, and a Page 10 Full Profile / Operating DNA close.

The current generated baseline should be treated only as a technical baseline, not as product design.

## Overall Gap Severity

Severity: HIGH

Reason:
- Current HTML uses skeletal placeholder copy.
- Current templates lack the locked PDF's visual hierarchy.
- Page 2 map is only a placeholder.
- Page 10 DNA section is only a placeholder.
- Pages 3–9 lack dense report structure, multi-column layouts, cards, metric bands, and facilitator formatting.
- Footer/header system is not yet matched to locked reference.

## Page-by-Page Gap Table

| Page | Locked PDF Purpose | Current HTML State | Missing Visual Structure | Missing Content Blocks | Template File | Priority |
|---|---|---|---|---|---|---|
| 1 | Cover / Behavioral Operating Profile identity and signature | Basic generated report shell | Large cover title, background arcs, profile signature card, core edge card, metadata boxes | Profile signature, core edge narrative, assessment date, confidence, profile type | page01-cover.html | Critical |
| 2 | Behavioral Operating System Map | Placeholder map text | Central operating architecture map, core engine, driver/stabilizer/opposing pattern nodes, tension lines, system tension box | Vector/Fidelity/Signal/Flex nodes, profile codes, tension language | page02-operating-system-map.html | Critical |
| 3 | Executive Summary | Basic summary placeholder | Premium report header, long-form summary, 3-card leadership/development/priority section, footer | Executive summary body, primary leadership signal, development opportunity, priority statement | page03-executive-summary.html | High |
| 4 | Operating Pattern | Basic placeholder | Long-form operating pattern body, 3-card summary row, development priority band | strongest default, likely blind spot, highest value adjustment | page04-operating-pattern.html | High |
| 5 | Decision Architecture | Basic placeholder | Two-column narrative/metrics layout, decision trait rows with percentages, 3-card advantage/failure/upgrade section | closure speed, evidence threshold, consensus dependence, strategic reopen rate, decision priority | page05-decision-architecture.html | High |
| 6 | Communication Style | Basic placeholder | Dense multi-section communication page, signal matrix, others-experience cards, advantage/friction/upgrade cards | transmission pattern, directness, receptivity, emotional filtering, pressure intensification | page06-communication-style.html | High |
| 7 | System Under Strain | Basic placeholder | Pressure response grid, escalation chain, blind spot field, friction patterns, recalibration priorities | pressure behaviors, risk signals, blind spots, friction loop, recalibration items | page07-system-under-strain.html | Critical |
| 8 | Operating Environment Fit | Basic placeholder | Three environment columns, environmental insight, primary development shift cards | high-traction, conditional-fit, high-friction environments, horizon/adapt/input shifts | page08-operating-environment-fit.html | High |
| 9 | Facilitator Notes | Basic placeholder | Dense facilitator interpretation layer, coaching intervention points, development edges, coaching questions | system architecture, tensions, intervention points, maturity progression | page09-facilitator-notes.html | Medium |
| 10 | Full Profile Unlocks + Operating DNA | Basic placeholder | Strategic expansion grid, advanced systems grid, operating DNA three-card close, why-this-matters band | unlock areas, advanced systems, core force, hidden cost, next evolution | page10-full-profile-unlocks-dna.html | Critical |

## Recommended Reconstruction Order

1. Shared CSS / page shell
2. Page 1 cover
3. Page 2 Behavioral Operating System Map
4. Page 10 Full Profile Unlocks + Operating DNA
5. Page 3 Executive Summary
6. Page 4 Operating Pattern
7. Page 5 Decision Architecture
8. Page 6 Communication Style
9. Page 7 System Under Strain
10. Page 8 Operating Environment Fit
11. Page 9 Facilitator Notes

Reason:
- Shared CSS prevents repeated page-level chaos.
- Page 1, Page 2, and Page 10 define perceived product value.
- Pages 3–9 then follow the established system.

## Shared CSS System Needed

Create reusable design primitives before heavy page work:

### Typography
- Premium sans-serif stack.
- Large bold title style.
- Compact eyebrow labels.
- Strong section headings.
- Dense but readable paragraph style.
- Small uppercase labels for cards and metrics.

### Page Shell
- 8.5 x 11 print-safe page frame.
- Consistent margins.
- Top report identifier.
- Bottom footer with assessment date, confidence, profile type, page number.
- Controlled page breaks.

### Card System
- Light bordered cards.
- Dark signature card for Page 1.
- Modular 3-card and 4-card rows.
- Accent-left rule cards.
- Compact metric rows.

### Grid System
- Two-column narrative/metrics layouts.
- Three-column environment grids.
- Responsive enough for browser preview but optimized for print/PDF.

### Color System
- Dark charcoal primary.
- Warm gold/orange accent.
- Light gray panels.
- Muted rule lines.
- Optional red/yellow/purple accents for Page 7/10 sections only if controlled.

### Visual Motifs
- Subtle background arcs on cover.
- Operating system map nodes and tension lines on Page 2.
- Structured bands and cards rather than loose paragraphs.

## Placeholder Expansion Plan

Current placeholder set is too small for the locked report structure.

Each page should receive page-specific placeholders for:
- title
- subtitle
- section labels
- long-form narrative body
- card headings
- card body copy
- metric labels
- metric values
- footer metadata

Priority placeholder expansion:
1. Page 1 signature and core edge
2. Page 2 operating map node content
3. Page 10 DNA cards
4. Pages 3–8 body/card sections
5. Page 9 facilitator notes

## Do-Not-Do Rules

- Do not install PDF tooling until HTML visual structure is closer to locked reference.
- Do not rewrite scoring while doing visual refinement.
- Do not rename public product labels inside code yet; Mini V2 remains internal engineering label.
- Do not delete or overwrite the locked PDF.
- Do not attempt all 10 pages in one uncontrolled patch.
- Do not weaken placeholder validation.
- Do not remove the 10-page structure.
- Do not move to production delivery until generated HTML is visually acceptable.

## Next Immediate Action

Start with shared CSS/page shell and Page 1 cover reconstruction.

Target file:
`moremindmap-backend/templates/mini-v2/page01-cover.html`

Supporting file:
`moremindmap-backend/engine/generateMiniV2HTML.js`

Goal:
Make Page 1 visually resemble the locked PDF cover enough to establish the report's premium identity while preserving successful generation and 0-placeholder validation.
