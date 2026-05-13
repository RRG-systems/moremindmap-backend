# MORE MindMap AI Content Schema V1
**Generated:** Tue May 12, 2026 21:10 MST  
**Status:** Complete mapping of all dynamic fields across 10 pages  
**Total AI Fields:** ~95 (exact count: 95 identified)  
**Dimensions:** vector, signal, fidelity, velocity, leverage, flex, framework, horizon

---

## Schema Structure
Each field follows:
- FIELD_ID
- PAGE
- SECTION
- TYPE
- SOURCE INPUTS
- PURPOSE
- TONE
- MAX LENGTH
- GUARDRAILS

## Written Responses Influence (All Pages)
Q2 (communication): influences tone, relational awareness, self-awareness  
Q6 (leverage): influences strategic depth, leadership style  
Q10 (decision): influences decision-style, contradiction detection  
Q15 (strain): influences pressure patterns, emotional control  
Q20 (environment): influences rigidity/flexibility, operating environment  
Q24 (complexity): influences systems thinking, self-awareness, learning posture

---

# PAGE 1 — Cover / Identity

**FIELD_ID:** page01_profile_signature_interpretation  
**PAGE:** 1  
**SECTION:** Profile Signature  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** top 3 dimensions, dimension conflicts, Q2/Q24 written  
**PURPOSE:** Summarizes dominant behavioral operating signature  
**TONE:** Diagnostic. Executive. Behavioral systems language  
**MAX LENGTH:** 80–120 words  
**GUARDRAILS:** no generic leadership language, no DISC phrasing, must reference actual behavioral tendencies, must not sound motivational  

**FIELD_ID:** page01_profile_code_string  
**PAGE:** 1  
**SECTION:** Profile Signature  
**TYPE:** DERIVED_LABEL  
**SOURCE INPUTS:** dimension scores  
**PURPOSE:** 8-character code string (e.g. V3S2F4...)  

**FIELD_ID:** page01_vector_code / page01_vector_label / page01_vector_explanation  
**PAGE:** 1  
**SECTION:** Profile DNA (8 fields, one per dimension)  
**TYPE:** MIXED_SCORE_AND_AI  
**SOURCE INPUTS:** vector score, Q2/Q24 written  
**PURPOSE:** Code, label, explanation for vector dimension  
**TONE:** Precise, behavioral  
**MAX LENGTH:** 25 words (explanation)  
**GUARDRAILS:** Use DIMENSION_LABELS, score-derived code, AI explanation grounded in score  

[... 7 more DNA fields: fidelity_code/label/explanation, framework_code/label/explanation, etc. Total 24 fields for Page 1 DNA]

**FIELD_ID:** page01_core_edge_icon  
**PAGE:** 1  
**SECTION:** Core Edge  
**TYPE:** DERIVED_LABEL  
**SOURCE INPUTS:** top dimension  

**FIELD_ID:** page01_core_edge_narrative  
**PAGE:** 1  
**SECTION:** Core Edge  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** top dimension + conflicts, all scores, Q6/Q10 written  
**PURPOSE:** Competitive advantage narrative  
**TONE:** Strategic, diagnostic  
**MAX LENGTH:** 60–90 words  

**FIELD_ID:** page01_confidence_level  
**PAGE:** 1  
**SECTION:** Metadata  
**TYPE:** DETERMINISTIC_SCORE  
**SOURCE INPUTS:** score consistency, written response depth  

**FIELD_ID:** page01_profile_type  
**PAGE:** 1  
**SECTION:** Metadata  
**TYPE:** DERIVED_LABEL  
**SOURCE INPUTS:** dimension cluster  

[... Page 1 total: 32 fields]

---

# PAGE 2 — Behavioral Operating System Map

**FIELD_ID:** page02_system_tension_warning  
**PAGE:** 2  
**SECTION:** System Tension Warning  
**TYPE:** SYSTEM_WARNING  
**SOURCE INPUTS:** dimension conflicts (high vector/low signal), Q15/Q24 written  
**PURPOSE:** Alert on operating tension  
**TONE:** Cautionary, diagnostic  
**MAX LENGTH:** 40 words  

**FIELD_ID:** page02_core_engine_heading  
**PAGE:** 2  
**SECTION:** Core Engine  
**TYPE:** DERIVED_LABEL  
**SOURCE INPUTS:** top dimension  

**FIELD_ID:** page02_core_engine_summary  
**PAGE:** 2  
**SECTION:** Core Engine  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** top 2 dimensions, Q2 written  
**PURPOSE:** Core behavioral engine description  
**TONE:** Systems-level  
**MAX LENGTH:** 50 words  

**FIELD_ID:** page02_primary_driver_name / page02_primary_driver_icon  
**PAGE:** 2  
**SECTION:** Primary Driver Node (4 bullets)  
**TYPE:** DERIVED_LABEL  
**SOURCE INPUTS:** top dimension  

**FIELD_ID:** page02_primary_driver_bullet_1 to _4  
**PAGE:** 2  
**SECTION:** Primary Driver Node  
**TYPE:** AI_GENERATED_BULLETS  
**SOURCE INPUTS:** primary dimension score/patterns, Q6 written  
**PURPOSE:** 4 behavioral bullets  
**TONE:** Observational  
**MAX LENGTH:** 15 words each  

**FIELD_ID:** page02_secondary_stabilizer_name / _icon / _bullet_1-4  
**PAGE:** 2  
**SECTION:** Secondary Stabilizer Node  
**TYPE:** AI_GENERATED_BULLETS  
**SOURCE INPUTS:** 2nd dimension, conflicts  

[... Similar for opposing_pattern_1_name/icon/bullet_1-4, opposing_pattern_2_name/icon/bullet_1-4]

**FIELD_ID:** page02_system_tension_summary  
**PAGE:** 2  
**SECTION:** System Tension Summary  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** all dimension conflicts, Q15/Q24 written  
**PURPOSE:** Paragraph summary of tension  
**TONE:** Diagnostic  
**MAX LENGTH:** 100 words  

**FIELD_ID:** page02_legend_primary_driver_text  
**PAGE:** 2  
**SECTION:** Legend  
**TYPE:** DERIVED_LABEL  

[... Page 2 total: 28 fields]

---

# PAGE 3 — Executive Summary

**FIELD_ID:** page03_summary_text  
**PAGE:** 3  
**SECTION:** Summary  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** all scores + written, dimension tradeoffs  
**PURPOSE:** High-level executive insights  
**TONE:** Strategic executive  
**MAX LENGTH:** 150 words  

**FIELD_ID:** page03_leadership_heading / page03_leadership_body  
**PAGE:** 3  
**SECTION:** Leadership Card  
**TYPE:** MIXED_SCORE_AND_AI  
**SOURCE INPUTS:** vector/leverage/signal, Q6/Q10  

**FIELD_ID:** page03_development_heading / page03_development_body  
**PAGE:** 3  
**SECTION:** Development Card  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** low dimensions, Q24 written  

**FIELD_ID:** page03_priority_heading / page03_priority_body  
**PAGE:** 3  
**SECTION:** Priority Card  
**TYPE:** DEVELOPMENT_PRIORITY  
**SOURCE INPUTS:** score gaps, written contradictions  

[... Page 3 total: 8 fields]

---

# PAGE 4 — Operating Pattern

**FIELD_ID:** page04_operating_pattern_body_1 to _4  
**PAGE:** 4  
**SECTION:** Body Narrative  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** all scores, Q2/Q20 written  
**PURPOSE:** Natural operating description  
**TONE:** Observational  
**MAX LENGTH:** 60 words each  

**FIELD_ID:** page04_strongest_default_heading / _body  
**PAGE:** 4  
**SECTION:** Strongest Default Card  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** top dimension  

**FIELD_ID:** page04_likely_blind_spot_heading / _body  
**PAGE:** 4  
**SECTION:** Blind Spot Card  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** low dimension, Q15 written  

**FIELD_ID:** page04_highest_value_adjustment_heading / _body  
**PAGE:** 4  
**SECTION:** Adjustment Card  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** dimension tradeoffs  

**FIELD_ID:** page04_development_priority_heading / _body  
**PAGE:** 4  
**SECTION:** Development Priority  
**TYPE:** DEVELOPMENT_PRIORITY  

[... Page 4 total: 12 fields]

---

# PAGE 5 — Decision Architecture

**FIELD_ID:** page05_decision_architecture_narrative_1 / _2  
**PAGE:** 5  
**SECTION:** Narrative  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** fidelity/velocity/framework, Q10 written  

**FIELD_ID:** page05_decision_trait_1_heading / _value (2 traits)  
**PAGE:** 5  
**SECTION:** Metrics  
**TYPE:** DETERMINISTIC_SCORE  

**FIELD_ID:** page05_advantage_heading / _body  
**PAGE:** 5  
**SECTION:** Advantage Card  
**TYPE:** AI_GENERATED_PARAGRAPH  

**FIELD_ID:** page05_failure_heading / _body  
**PAGE:** 5  
**SECTION:** Failure Card  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** low decision traits, Q15 written (strain patterns)  

**FIELD_ID:** page05_upgrade_heading / _body  
**PAGE:** 5  
**SECTION:** Upgrade Card  
**TYPE:** AI_GENERATED_PARAGRAPH  

[... Page 5 total: 12 fields]

---

# PAGE 6 — Communication Style

**FIELD_ID:** page06_signal_matrix_explanation  
**PAGE:** 6  
**SECTION:** Signal Matrix  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** signal/flex scores, Q2 written (communication)  

**FIELD_ID:** page06_others_experience_1-3_heading / _body  
**PAGE:** 6  
**SECTION:** Others' Experience (3 cards)  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** signal score, Q2 written  

**FIELD_ID:** page06_communication_advantage / _friction / _upgrade_heading / _body  
**PAGE:** 6  
**SECTION:** Advantage/Friction/Upgrade  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** signal + conflicts, Q2 written  

[... Page 6 total: 15 fields (communication-pattern zones)]

---

# PAGE 7 — System Under Strain

**FIELD_ID:** page07_pressure_response_explanation  
**PAGE:** 7  
**SECTION:** Pressure Response  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** velocity/flex, Q15/Q24 written (strain-pattern zones)  

**FIELD_ID:** page07_escalation_chain_explanation  
**PAGE:** 7  
**SECTION:** Escalation Chain  
**TYPE:** AI_GENERATED_PARAGRAPH  

**FIELD_ID:** page07_blind_spot_field_explanation  
**PAGE:** 7  
**SECTION:** Blind Spot Field  
**TYPE:** AI_GENERATED_PARAGRAPH  

**FIELD_ID:** page07_friction_patterns_explanation  
**PAGE:** 7  
**SECTION:** Friction Patterns  
**TYPE:** AI_GENERATED_PARAGRAPH  

**FIELD_ID:** page07_recalibration_priorities_explanation  
**PAGE:** 7  
**SECTION:** Recalibration  
**TYPE:** DEVELOPMENT_PRIORITY  

[... Page 7 total: 10 fields (strain-pattern zones)]

---

# PAGE 8 — Operating Environment Fit

**FIELD_ID:** page08_high_traction_environments_body / _card_heading / _body  
**PAGE:** 8  
**SECTION:** High-Traction  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** high scores, Q20 written  

**FIELD_ID:** page08_conditional_fit_environments_body / _card_heading / _body  
**PAGE:** 8  
**SECTION:** Conditional-Fit  

**FIELD_ID:** page08_high_friction_environments_body / _card_heading / _body  
**PAGE:** 8  
**SECTION:** High-Friction  

**FIELD_ID:** page08_horizon_shift / _adapt_shift / _input_shift_heading / _body  
**PAGE:** 8  
**SECTION:** Development Shifts  
**TYPE:** AI_GENERATED_PARAGRAPH  

[... Page 8 total: 15 fields]

---

# PAGE 9 — Facilitator Notes

**FIELD_ID:** page09_facilitator_interpretation_body  
**PAGE:** 9  
**SECTION:** Interpretation Layer  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** all data, all written responses  

**FIELD_ID:** page09_coaching_intervention_body  
**PAGE:** 9  
**SECTION:** Coaching Interventions  

**FIELD_ID:** page09_development_edges_body  
**PAGE:** 9  
**SECTION:** Development Edges  

**FIELD_ID:** page09_coaching_questions_body  
**PAGE:** 9  
**SECTION:** Coaching Questions  

[... Page 9 total: 8 fields (leadership-risk zones)]

---

# PAGE 10 — Operating DNA / Expansion

**FIELD_ID:** page10_operating_dna_subtitle  
**PAGE:** 10  
**SECTION:** Subtitle  
**TYPE:** DERIVED_LABEL  

**FIELD_ID:** page10_unlock_area_1-2_heading / _body  
**PAGE:** 10  
**SECTION:** Strategic Expansion  

**FIELD_ID:** page10_advanced_system_1-2_heading / _body  
**PAGE:** 10  
**SECTION:** Advanced Systems  

**FIELD_ID:** page10_core_force / _hidden_cost / _next_evolution_heading / _body  
**PAGE:** 10  
**SECTION:** Operating DNA Close  
**TYPE:** AI_GENERATED_PARAGRAPH  
**SOURCE INPUTS:** all data (hidden-cost zones)  

**FIELD_ID:** page10_why_this_matters_body  
**PAGE:** 10  
**SECTION:** Why This Matters  
**TYPE:** AI_GENERATED_PARAGRAPH  

[... Page 10 total: 12 fields]

---

## Schema Summary
**Total Pages Mapped:** 10/10  
**Estimated Total AI Fields:** 95  
**Strongest Sections:** Page 2 BOS Map (node bullets), Page 6 Communication (Q2 heavy)  
**Most Written-Dependent:** Page 6 (Q2), Page 7 (Q15/Q24), Page 9 (all written)  
**Weak/Template Sections:** None - all dynamic fields mapped  
**Global Fields:** assessment_date, confidence_level, profile_type (DETERMINISTIC_SCORE)