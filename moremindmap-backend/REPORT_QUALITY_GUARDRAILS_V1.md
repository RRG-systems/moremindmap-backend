# Report Quality Guardrails V1
**Created:** Tue May 12, 2026 21:58 MST  
**Purpose:** Runtime validator for report_content.json before template injection  
**Philosophy:** Block generic DISC/AVA sludge. Only specific behavioral profiles pass.

---

# Quality Philosophy

The validator ensures:
"Is this profile specific enough to belong to one human?"

**PASS:** Forensic, behavioral, tension-aware, evidence-based
**WARN:** Generic phrasing, weak evidence, low density
**FAIL:** Banned language, placeholders, missing structure, horoscope energy

---

# 1. REQUIRED PAGE KEY VALIDATION

**Required 10 page keys:**
```
page01_cover
page02_operating_system_map
page03_executive_summary
page04_operating_pattern
page05_decision_architecture
page06_communication_style
page07_system_under_strain
page08_operating_environment_fit
page09_facilitator_notes
page10_full_profile_unlocks
```

**FAIL if any missing.**

---

# 2. REQUIRED FIELD VALIDATION

Each page must have minimum required fields (from REPORT_CONTENT_SCHEMA_V1.md).

Example Page 1 minimum:
```
profile_signature_interpretation
profile_code_string
vector_code/label/explanation (8 dimensions total)
core_edge_narrative
confidence_level
profile_type
```

**FAIL if critical field missing.**
**WARN if secondary field missing.**

---

# 3. EMPTY/NULL FIELD DETECTION

**FAIL if:**
- >20% fields are null/undefined/empty string
- Critical fields are empty

**WARN if:**
- 10-20% fields empty
- Non-critical fields empty

---

# 4. PLACEHOLDER LANGUAGE DETECTION

**FAIL on phrases:**
- "lorem ipsum"
- "placeholder"
- "example text"
- "insert here"
- "TODO"
- "TBD"
- "sample"
- "mock content"
- "generated text"
- "[MOCK]"

---

# 5. BANNED PHRASE DETECTION (30+ terms)

**FAIL on ANY:**
```
"natural leader", "strong communicator", "values authenticity", "works well with others",
"balances structure and flexibility", "results-oriented", "team player", "growth mindset",
"unlock your potential", "passionate about", "visionary leader", "detail-oriented",
"strategic thinker", "big picture", "thinks outside the box", "takes ownership",
"proactive approach", "high standards", "empathetic", "resilient", "innovative",
"collaborative spirit", "driven individual", "executive presence", "people person"
```

**Genericity Score:** (banned phrases found) / total words * 100

---

# 6. GENERICITY SCORING

**Weak phrase weight (0.5 points each):**
```
"may benefit from", "tends to", "can be helpful", "prefers to", "likely to",
"values collaboration", "appreciates structure", "enjoys", "seeks to", "aims to"
```

**Genericity Score thresholds:**
- 0.0-1.0: PASS
- 1.0-2.0: WARN
- >2.0: FAIL

---

# 7. REPEATED SENTENCE-PATTERN DETECTION

**Check sentence openings:**
```
"You are", "This person", "They tend to", "The profile shows"
```

**WARN if >30% sentences start with same 3 patterns.**
**FAIL if >50%.**

---

# 8. EVIDENCE ANCHORING CHECKS

**Required evidence language (bonus points):**
```
"written response", "answer pattern", "under pressure", "score pattern",
"contradiction", "tradeoff", "operational consequence", "dimension conflict",
"Q2 shows", "Q24 reveals", "MC answers indicate"
```

**Evidence Anchor Score:** (evidence phrases) / total words * 100

**PASS:** >= 0.5%
**WARN:** 0.2-0.5%
**FAIL:** <0.2%

---

# 9. WRITTEN-RESPONSE INTEGRATION CHECKS

**Must reference written responses in:**
- Page 6 (communication, Q2)
- Page 7 (strain, Q15/Q24)
- Page 9 (facilitator, all Q)

**WARN if missing in these pages.**
**FAIL if missing in all 3.**

---

# 10. CONTRADICTION/TENSION PRESENCE CHECKS

**Must contain tension language somewhere:**
```
"tradeoff", "tension", "contradiction", "but", "however", "cost of", "friction",
"blind spot", "hidden cost", "under strain", "escalation"
```

**Contradiction Signal Score:** (tension phrases) / total words * 100

**PASS:** >= 0.8%
**WARN:** 0.3-0.8%
**FAIL:** <0.3%

---

# 11. BEHAVIORAL SPECIFICITY CHECKS

**Behavioral language bonus:**
```
"enters with", "moves toward", "defaults to", "responds with", "prefers to",
"under time pressure", "when stressed", "team experiences as", "discovers late"
```

**Specificity Score:** (behavioral phrases) / total words * 100

**PASS:** >= 1.2%
**WARN:** 0.5-1.2%
**FAIL:** <0.5%

---

# 12. SECTION LENGTH CHECKS

**Minimum lengths (words):**
```
page01_core_edge_narrative: 60
page02_system_tension_summary: 80
page03_summary_text: 120
page04_operating_pattern_body_1: 50
[... per schema]
```

**FAIL if critical sections too short.**
**WARN if secondary sections short.**

---

# 13. TONE VIOLATIONS

**Therapy-speak banned:**
```
"inner self", "your authentic", "unlock your", "embrace your", "journey of"
```

**Corporate fluff banned:**
```
"executive presence", "leadership potential", "high performer", "key contributor"
```

---

# 14. MOCK-OUTPUT LABELING RULES

**Mock output MUST contain:**
```
"generation_mode": "mock"
```

**Cannot pass as "gpt" output.**

---

# 15. FAIL/WARN/PASS THRESHOLDS

**FINAL QUALITY SCORE** (0-100):

**PASS (85-100):**
- All 10 pages present
- No banned/placeholder phrases
- Genericity score <= 1.0
- Evidence anchor >= 0.5%
- Contradiction signal >= 0.8%
- Specificity score >= 1.2%
- No critical sections empty

**WARN (60-84):**
- Weak phrasing found
- Some repetition
- Low density in secondary sections
- Minor evidence gaps

**FAIL (<60):**
- Missing page/section
- Banned phrases found
- Placeholder language
- High genericity
- Low evidence anchoring
- No tension/contradiction language

---

# VALIDATION FLOW

1. **Structural validation** (pages, fields)
2. **Content validation** (empty, placeholder)
3. **Genericity scan** (banned phrases)
4. **Density scoring** (evidence, specificity, tension)
5. **Pattern detection** (repetition, weak language)
6. **Final score calculation**
7. **Status assignment**

---

**END OF FILE: REPORT_QUALITY_GUARDRAILS_V1.md**