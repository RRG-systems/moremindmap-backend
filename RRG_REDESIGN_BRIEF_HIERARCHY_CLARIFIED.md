# RRG REDESIGN BRIEF — HIERARCHY CLARIFIED

**Date:** Mon Apr 27, 2026 10:52 MST  
**Revision:** Design Direction Clarified (RRG = Parent Platform)  
**Status:** ✅ READY FOR EXECUTION (pending final approval on specific choices)

---

## HIERARCHY CLARIFICATION

**RRG = Parent Platform / Authority Layer**
- The infrastructure company
- The managed recovery operating system
- Broader, more commanding, more institutional
- The system that powers the tools

**MoreMindMap = Child Diagnostic Module**
- Entry point tool
- Diagnostic assessment
- Will live inside RRG ecosystem
- More specialized, narrower focus

**Design Relationship:**
```
RRG (Parent Infrastructure Platform)
  ├── MoreMindMap (Diagnostic Entry Point)
  ├── (Future) Other tools/modules
  └── Sales/Recovery Infrastructure
```

---

## DESIGN DIRECTION — USE MM AS REFERENCE, NOT TEMPLATE

### Keep (From MoreMindMap Aesthetic)
- ✅ Black/near-black premium dark aesthetic
- ✅ Clean sans-serif typography (no serif)
- ✅ Glassy cards with subtle borders (white/10 opacity)
- ✅ Backdrop blur on containers (glass morphism)
- ✅ Subtle wave/line motion in background
- ✅ Thin, restrained borders
- ✅ Strong spacing and breathing room
- ✅ Restrained visual language (less is more)
- ✅ Enterprise/institutional feel

### Change (Make RRG More Authoritative)
- ❌ Remove all orange accent color (no color identity clinging)
- ❌ Remove serif fonts completely (Playfair Display gone)
- ❌ Make background animation more structured/commanding
  - MM has simple subtle wave
  - RRG should have more layered, infrastructure-like animation
  - Consider: Multi-layer waves OR subtle grid/lattice underneath
  - Goal: Feels like the system backbone
- ❌ Section spacing: More commanding, less playful
  - Keep padding but make it feel more authoritative
  - Darker section backgrounds (less alternation, more cohesive black)
  - Result: Feels like one unified platform, not multiple sections
- ❌ Buttons: More authoritative
  - Primary CTA: White text on dark background (not white bg + black text)
  - Or: Subtle accent color for RRG (not orange, maybe light gray or soft blue)
  - Goal: Feels like controlled, institutional action, not soft/approachable

---

## SPECIFIC DESIGN CHANGES

### 1. Background Animation
**MM Style:** Simple subtle single-layer wave animation  
**RRG Style (Parent Platform):** Structured, more commanding
- **Option A (Recommended):** Multi-layer waves (2-3 layers at different speeds) = infrastructure depth
- **Option B:** Subtle grid/lattice overlay + single wave = technical infrastructure feel
- **Option C:** Layered lines with slight pulsing = data flow visualization
- **Guidance:** Keep it sophisticated, not busy. Avoid looking like a tech startup cliché.

### 2. Section Backgrounds
**Current:** Alternating charcoal/slate (creates segmentation)  
**New:** Unified black with subtle depth
- Remove strong section color alternation
- Use black throughout (maybe white/3 subtle backdrop for specific sections)
- Result: Feels like one platform, not disconnected sections

### 3. Typography
**Current:** Serif (Playfair Display) headings  
**New:** All sans-serif, clean and modern
- Headings: Sans-serif, larger and more commanding
- Body: Sans-serif (Inter or system font)
- Goal: Modern, institutional, no warmth (pure business)

### 4. Cards & Glass Morphism
**Current:** Solid slate background with orange hover border  
**New:** Dark glass effect with white borders (like MM)
- Background: `bg-white/5` (dark glass)
- Border: `border-white/10` (thin, subtle)
- Backdrop filter: `backdrop-blur-md` (glass effect)
- Hover: Subtle border brightening (`border-white/20` or soft glow)
- Result: Premium, sophisticated, institutional

### 5. Buttons & CTAs
**Current:** Orange background, white text  
**New (Option 1 - Recommended):** Inverted for authority
- Primary CTA: White text on dark/transparent background (like MM's secondary)
- Secondary CTA: Bordered style (white/15 border, white text)
- OR
- Primary CTA: Subtle accent color (soft gray or light tone, not orange)
- Result: Controlled, institutional, authoritative

**Guidance:** Avoid bright colors. RRG is the serious infrastructure platform, not the friendly diagnostic tool.

### 6. Accent Color Strategy
**Current:** Orange (#C2410C) used extensively  
**New:** No accent color OR single institutional accent
- Option A: No accent color (pure black/white/gray) = most institutional
- Option B: Single light gray accent (#E5E7EB or similar) = softer but still institutional
- Option C: Single dark blue accent (#3B82F6 or navy) = tech/infrastructure feel
- **Recommendation:** Option A (no accent) or Option B (light gray for button highlights)

### 7. Logo & Branding
**Current:** Orange circle with "R"  
**New:** Neutral/white branding
- Logo circle: White or light gray (not orange)
- Font weight: Keep bold for presence
- Result: Clean, institutional

### 8. Navigation
**Current:** Fixed top, charcoal bg, orange hover  
**New:** Clean, minimal, white/neutral
- Background: Black with subtle border bottom (white/10)
- Text: White, hover → white/70 (no color change)
- Remove orange entirely

### 9. Borders & Dividers
**Current:** Orange underlines on section headers, orange hover borders  
**New:** White/neutral thin borders
- Section header underline: Remove or use white/15 thin line (optional)
- Card borders: white/10
- Button borders: white/15
- Result: Restrained, institutional

### 10. Spacing & Layout
**Keep as-is:**
- Section padding (py-24)
- Grid layouts
- Responsive breakpoints
- All structural elements

---

## DESIGN INTENT

**MM (Diagnostic Entry Point):**
- Feels like: "Take this assessment, get clarity"
- Tone: Friendly, premium, but entry-level
- Purpose: Route people to the right path

**RRG (Parent Platform):**
- Feels like: "We are the infrastructure that powers recovery"
- Tone: Authoritative, institutional, serious
- Purpose: Establish trust, convey scale, show capability
- Visual signal: "This is the system behind the tools"

---

## IMPLEMENTATION CHECKLIST

### Phase 1: Base Colors & Typography
- [ ] Remove Playfair Display import
- [ ] Set all text to sans-serif
- [ ] Change background to pure black (`#000`)
- [ ] Update Tailwind config: Remove orange color, remove custom colors

### Phase 2: Buttons & CTAs
- [ ] Primary CTA: White text, dark/transparent bg (or light gray accent)
- [ ] Secondary CTA: Bordered style (white/15 border)
- [ ] Remove all orange button styling

### Phase 3: Cards & Glass Morphism
- [ ] Apply `bg-white/5` to all card containers
- [ ] Apply `backdrop-blur-md` to all cards
- [ ] Change all borders to `border-white/10`
- [ ] Update hover states (border-white/20, no color change)

### Phase 4: Navigation & Branding
- [ ] Update logo: White circle instead of orange
- [ ] Update nav: White text, white/10 border-bottom
- [ ] Remove orange hover colors from nav links

### Phase 5: Background Animation
- [ ] Choose animation style (multi-layer waves OR grid/lattice)
- [ ] Implement animated background (SVG or CSS)
- [ ] Position behind main content, subtle and sophisticated

### Phase 6: Section Styling
- [ ] Remove strong section background alternation
- [ ] Unify to black background throughout
- [ ] Optional: Use subtle white/3 or white/5 for visual separation
- [ ] Update all section classes

### Phase 7: Testing & Validation
- [ ] Desktop visual review (full width)
- [ ] Tablet responsive check
- [ ] Mobile responsive check
- [ ] Link verification (all nav, CTA, footer links working)
- [ ] Form functionality (contact form submits)
- [ ] No broken images or styling

### Phase 8: Deploy
- [ ] Commit changes to git
- [ ] Push to main branch
- [ ] Verify GitHub Pages deployment (should auto-deploy)
- [ ] Test live site

---

## QUESTIONS FOR D.J. / FINAL APPROVAL

Before execution, clarify these 3 choices:

**1. Background Animation Style:**
- Option A: Multi-layer waves (2-3 overlapping waves at different speeds) = infrastructure depth
- Option B: Subtle grid/lattice overlay + single wave = technical/data feel
- Option C: Pulsing lines = data flow visualization
- Option D: None (pure black, no animation) = maximum institutional

**Recommendation:** Option A (multi-layer waves)

**2. Button Style (Primary CTA):**
- Option A: White text on transparent/dark bg (like MM's secondary style) = most institutional
- Option B: White text on dark bg with subtle shadow = softer institutional
- Option C: Light gray accent color (#E5E7EB) bg with black text = slight visual interest
- Option D: Keep orange but desaturate = compromise

**Recommendation:** Option A (white text, transparent/dark bg)

**3. Accent Color:**
- Option A: No accent color (pure black/white/gray) = most authoritative
- Option B: Single light gray accent (#E5E7EB) = minimal visual identity
- Option C: Single institutional blue (#3B82F6) = tech/infrastructure signal

**Recommendation:** Option A (no accent)

---

## SUCCESS CRITERIA

- ✅ RRGconnect.com feels like parent infrastructure platform
- ✅ Visually related to MoreMindMap (shares aesthetic language)
- ✅ But feels broader, more commanding, more institutional
- ✅ Pure black/white/gray premium aesthetic
- ✅ No orange color
- ✅ No serif fonts
- ✅ Glass morphism cards with white borders
- ✅ Structured background animation (or none)
- ✅ All RRG content preserved (copy, links, structure, forms)
- ✅ Mobile responsive intact
- ✅ No broken links
- ✅ Deployed successfully to GitHub Pages

---

## NEXT STEP

**D.J. approves the 3 questions above** → **Rocky executes full redesign** → **Deploy to GitHub Pages**

**Estimated execution time:** 45 min - 1 hour  
**Estimated testing time:** 15 min  

---

**Document:** `/Users/rrg/.openclaw/workspace/RRG_REDESIGN_BRIEF_HIERARCHY_CLARIFIED.md`  
**Status:** Awaiting final approval on 3 design choices
