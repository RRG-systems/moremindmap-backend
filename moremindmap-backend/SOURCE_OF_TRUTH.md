# MOREMindMap Source of Truth

## Canonical Git Root

The Git repository root is:

/Users/rrg/.openclaw/workspace

## Project Folder

The MOREMindMap backend project folder is currently:

moremindmap-backend/

This folder is not a nested Git repository. It does not have its own .git directory.

Therefore all Git-tracked MOREMindMap backend paths must be referenced from the Git root with:

moremindmap-backend/

Example:

moremindmap-backend/README_PROJECT_STATE.md

NOT:

README_PROJECT_STATE.md

## Canonical GitHub Remote

Expected remote:

https://github.com/RRG-systems/moremindmap-backend.git

## Required Startup Check

Before every session, run from the Git root:

pwd
git remote -v
git branch --show-current
git status --short
git log --oneline -5
ls -lh moremindmap-backend/README_PROJECT_STATE.md

## May 12, 2026 Evening Checkpoint — Page 2 Annotation Problem / Next Design Direction

**Current HEAD before commit:** `274eced`

**Current Artifact Path:**
`moremindmap-backend/releases/mini-v2-html-baseline/mini-v2-html-baseline.html`

**Current Known Working Status:**
- HTML generation pipeline: Stable
- Test passes: 0 placeholders, 10 pages
- Circle geometry: Approved
- Center circle: Good
- Four outer circles: Geometrically aligned
- System Tension Warning box overlap with top circle: Approved

**Current Page 2 Visual Assessment:**
- Circle system successful
- Annotation box placement unsuccessful
- External text boxes repeatedly drift off-page, overlap circles, or become unreadable
- Multiple positioning attempts failed
- Connector lines create additional problems

**Failed Annotation-Box Approach:**
External annotation boxes positioned outside the four outer circles have not achieved acceptable readability and layout balance after multiple iterations.

**Proposed Next Experiment:**
Replace external annotation boxes with self-contained enlarged outer circles:
- Remove four external annotation text boxes
- Slightly enlarge four outer circles (e.g., 110px → 130-140px diameter)
- Keep center circle unchanged
- Keep top warning overlap if visually useful
- Place concise 1-2 sentence descriptors INSIDE each outer circle
- Structure: role label + name/code + icon + descriptor
- Makes each circle self-contained

**Page 1 Lock:**
Add YOUR PROFILE DNA decoder box on Page 1 Cover between the Profile Signature black bar and Core Edge section.

Purpose:
- Explain the profile code string (e.g., V8 • Fd4 • F4 • Vl3 • L3 • H2 • S1 • Fx1)
- Interpret all eight vector codes as integrated operating architecture
- Tone: proprietary diagnostic behavioral-systems language
- NOT motivational fluff or generic personality praise

**Launch Strategy:**
1. Finish Page 2 (key visual page)
2. Add YOUR PROFILE DNA decoder to Page 1
3. Wire AI content generation for full report
4. Get production deployment working
5. Upgrade remaining pages over time

**Next Recommended Steps:**
1. Reopen fresh session
2. Pull latest main
3. Read SOURCE_OF_TRUTH.md, CURRENT_RECOVERY_STATE.md, README_PROJECT_STATE.md, MINI_V2_VISUAL_GAP_REPORT.md
4. Confirm artifact opens correctly
5. Decide: external annotations vs. self-contained enlarged circles
6. If self-contained approach: remove external boxes, enlarge circles, add internal descriptors
7. Add Page 1 YOUR PROFILE DNA decoder box
8. Shift to AI content wiring
