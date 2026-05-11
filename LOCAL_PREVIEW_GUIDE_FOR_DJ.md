# RRG REDESIGN — LOCAL PREVIEW GUIDE FOR D.J.

**Server Status:** ✅ RUNNING  
**URL:** http://localhost:8000  
**Time:** Mon Apr 27, 2026 11:15 MST

---

## TO VIEW LOCALLY

### Quick Start
1. Open browser to: **http://localhost:8000**
2. You'll see the redesigned homepage
3. Click through sections below to inspect

### If Server Stops
To restart:
```bash
cd /Users/rrg/RRGconnect-site
python3 -m http.server 8000
```

Then open: **http://localhost:8000**

---

## WHAT TO INSPECT

### 1. HOMEPAGE DESKTOP VIEW
**URL:** http://localhost:8000

**Visual Checklist:**
- [ ] Background: Pure black (not charcoal gradient)
- [ ] Wave animation: Subtle waves in background (infrastructure-like, not decorative)
- [ ] Hero headline: Large, bold, commanding
- [ ] Logo: White circle with "R" (not orange)
- [ ] Navigation: Clean, white text, white logo
- [ ] CTA buttons: White border + transparent (not orange)
- [ ] Cards: Glass morphism effect (semi-transparent, blurred)
- [ ] Card numbers: White/gray (not orange 01, 02, 03, etc.)
- [ ] Overall feel: **Parent infrastructure platform** (vs. MoreMindMap's diagnostic tool feel)

**Key visual signals to confirm:**
- Zero orange color visible
- Glass cards with subtle white borders
- Black/white/gray only
- Institutional, serious tone
- NOT a SaaS friendly vibe

---

### 2. CONTACT PAGE DESKTOP
**URL:** http://localhost:8000/contact.html

**Visual Checklist:**
- [ ] Form container: Glass morphism (semi-transparent, blurred)
- [ ] Form title: "Contact Revenue Recovery Group" (large, clear)
- [ ] Form fields: 6 inputs visible (name, company, email, phone, inquiry type, message)
- [ ] SMS consent: Checkbox + readable text ("I agree to receive text messages from M+RE Recruiting LLC...")
- [ ] Submit button: White with hover transition
- [ ] Privacy/Terms links: Present at bottom (clickable)
- [ ] Overall: Form is prominent, usable, institutional

**Key elements to verify:**
- SMS consent text is readable and intact
- Consent checkbox is required (can't submit without checking)
- Form styling matches homepage aesthetic
- No orange anywhere on form

---

### 3. MOBILE/RESPONSIVE VIEW
**URL:** http://localhost:8000 (view in responsive mode)

**How to test:**
- Open DevTools (Cmd+Opt+I on Mac)
- Click device toggle (top left)
- Select iPhone SE or similar (375px width)
- Inspect these areas:

**Mobile Checklist:**
- [ ] Navigation: Readable, not cramped
- [ ] Hero headline: Wraps naturally, legible at 6xl
- [ ] CTA buttons: Large, tappable (not cramped)
- [ ] Cards: Stack vertically, readable
- [ ] Contact form: Single column, inputs full-width
- [ ] SMS consent checkbox: Legible, label wraps properly
- [ ] Footer: Readable, links accessible
- [ ] No horizontal scrolling
- [ ] Overall: Fully responsive

**Responsive breakpoints to test:**
- Mobile: 375px (iPhone SE)
- Tablet: 768px (iPad)
- Desktop: 1440px (full width)

---

### 4. STYLE COMPARISON TO MOREMINDMAP

**How to compare:**
1. In separate browser tab, open: https://moremindmap.com
2. Compare to local http://localhost:8000

**Visual Comparison:**

| Aspect | MoreMindMap | RRG | Parent Status |
|--------|-------------|-----|---------------|
| Background | Black | Black | Same ✅ |
| Waves | Subtle single wave | Multi-layer waves | RRG more structured ✓ |
| Typography | Sans-serif | Sans-serif | Same ✅ |
| Cards | Glass, white/10 border | Glass, white/10 border | Same ✅ |
| Accents | White/light gray | None (pure black/white/gray) | RRG more neutral ✓ |
| Buttons | White on dark | White on dark | Similar approach ✓ |
| Feel | Friendly, diagnostic entry point | Authoritative, platform-level | RRG feels larger ✓ |

**Parent platform confirmation:**
- [ ] RRG feels broader and more commanding than MoreMindMap
- [ ] RRG feels like the operating system, MoreMindMap like the tool
- [ ] RRG is institutional, not diagnostic
- [ ] RRG is colder, sharper (not friendly)
- [ ] They share aesthetic language (glass, black/white) but RRG is the parent

---

### 5. PARENT PLATFORM FEEL

**Does RRG feel like the parent infrastructure platform?**

Check these signals:

**Authority Signals:**
- [ ] Pure black/white/gray (no warmth, no color signaling)
- [ ] All sans-serif (modern, professional)
- [ ] Glass cards (transparent, trustworthy)
- [ ] Thin white borders (restrained, sophisticated)
- [ ] Large spacing (breathing room, not cramped)
- [ ] Institutional button styling (controlled, not friendly)
- [ ] Multi-layer waves (infrastructure complexity, not decoration)

**NOT a MoreMindMap clone:**
- [ ] Feels broader (not narrow diagnostic focus)
- [ ] Feels more commanding (not entry-point friendly)
- [ ] Feels colder/sharper (not warm/approachable)
- [ ] Hierarchy clear: RRG > MoreMindMap

**Verdict:** Does it feel like the parent operating system? **YES / NO**

---

## SPECIFIC AREAS TO INSPECT

### No Orange Visible
Look for any orange/warm colors:
- Logo: Should be white circle, not orange
- Buttons: Should be white/transparent, not orange
- Hover states: Should be white-based, not orange
- Section accents: Should be none or white, not orange
- Text highlights: Should be white, not orange

**Expected:** ZERO orange instances visible

### Glass Morphism
Look for this effect on cards:
- Slightly transparent background
- Blurred/frosted glass effect
- Thin white border
- Rounded corners
- Hover: Slightly brighter border

**Expected:** ALL cards should have this effect

### Wave Animation
Look at background:
- Multi-layer waves moving subtly
- Very faint (not distracting)
- Infrastructure-like motion
- Different speeds (layered effect)

**Expected:** Subtle, sophisticated, not busy

### Button Transitions
Hover over any button:
- Primary (white border): Hover → white bg + black text
- Secondary (border): Hover → brighter border + slight bg

**Expected:** Sharp, institutional transitions

---

## NAVIGATION TEST

**Test all navigation links:**

Homepage (http://localhost:8000):
- [ ] Click "Problem" → scrolls to problem section
- [ ] Click "What We Do" → scrolls to services section
- [ ] Click "How It Works" → scrolls to 4-step process
- [ ] Click "Why RRG" → scrolls to benefits
- [ ] Click "Industries" → scrolls to industries section
- [ ] Click "Get Started" → navigates to contact.html

Contact page (http://localhost:8000/contact.html):
- [ ] Click "Back to Homepage" → returns to index.html
- [ ] Click "Privacy Policy" → opens privacy-policy.html
- [ ] Click "Terms of Service" → opens terms-of-service.html
- [ ] Click "Submit" → submits form (without actually submitting, just check button responds)

**Expected:** All links work, no 404 errors

---

## FORM TEST

**Test contact form:**

1. Fill out fields:
   - Name: Test Name
   - Company: Test Company
   - Email: test@example.com
   - Phone: 555-1234
   - Inquiry Type: Select one
   - Message: Test message

2. Check SMS consent:
   - [ ] Checkbox is visible
   - [ ] Text is readable ("I agree to receive text messages from M+RE Recruiting LLC...")
   - [ ] Cannot submit without checking

3. Submit:
   - [ ] Button text: "Submit Inquiry"
   - [ ] Button is white/large/tappable
   - [ ] (Don't actually submit, just verify button responds)

**Expected:** Form layout is clear, consent is required, no submission errors

---

## APPROVAL CHECKLIST FOR D.J.

After reviewing, check these boxes:

**Visual Design:**
- [ ] Zero orange visible anywhere
- [ ] Glass morphism cards look premium
- [ ] Black/white/gray aesthetic is institutional
- [ ] Wave animation is subtle and infrastructure-like
- [ ] Overall design feels like parent platform

**Functionality:**
- [ ] All navigation links work
- [ ] All external links work (privacy, terms)
- [ ] Contact form is usable
- [ ] SMS consent text readable and required

**Responsive:**
- [ ] Mobile view is readable
- [ ] Tablet view is readable
- [ ] Desktop view is optimal
- [ ] No horizontal scrolling

**Hierarchy:**
- [ ] RRG feels like parent operating system
- [ ] RRG feels broader than MoreMindMap
- [ ] RRG is more authoritative/institutional
- [ ] Not a MoreMindMap clone

**Copy:**
- [ ] All text unchanged
- [ ] All links point to correct pages
- [ ] Legal language preserved
- [ ] No accidental edits

---

## APPROVAL STATEMENT

**If everything looks good, confirm:**

"Redesign approved for deployment."

**If adjustments needed, specify:**

"Please adjust [specific area] because [reason]. Then re-review locally."

---

## AFTER APPROVAL

**If approved:**
1. Rocky executes:
   ```bash
   cd /Users/rrg/RRGconnect-site
   git add index.html contact.html
   git commit -m "Redesign: Institutional parent platform aesthetic"
   git push origin main
   ```

2. GitHub Pages deploys automatically (1-2 min)
3. Live at https://rrgconnect.com

**If adjustments needed:**
1. Rocky makes changes locally
2. Preview again at http://localhost:8000
3. D.J. approves after re-review

---

## QUICK REFERENCE

| Page | URL | Purpose |
|------|-----|---------|
| Homepage | http://localhost:8000 | Main site, hero, sections, cards |
| Contact | http://localhost:8000/contact.html | Form, consent, legal links |
| Privacy | http://localhost:8000/privacy-policy.html | Legal page |
| Terms | http://localhost:8000/terms-of-service.html | Legal page |

---

**Server will stay running until you approve deployment.**

**To stop server:** `pkill -f 'http.server 8000'`

**Ready when you are.**
