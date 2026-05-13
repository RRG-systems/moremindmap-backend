# Report Content Schema V1
**Created:** Tue May 12, 2026 21:47 MST  
**Purpose:** Final AI-generated content object for 10-page Mini V2 report  
**Input:** profile_input.json  
**Output:** report_content.json → template injection → PDF

---

# Root Structure

```json
{
  "metadata": {...},
  "page01_cover": {...},
  "page02_operating_system_map": {...},
  "page03_executive_summary": {...},
  "page04_operating_pattern": {...},
  "page05_decision_architecture": {...},
  "page06_communication_style": {...},
  "page07_system_under_strain": {...},
  "page08_operating_environment_fit": {...},
  "page09_facilitator_notes": {...},
  "page10_full_profile_unlocks": {...},
  "generation_metadata": {...}
}
```

---

# METADATA

```json
"metadata": {
  "profile_version": "mini-v2",
  "generation_date": "ISO-8601",
  "model_used": "gpt-5.5",
  "genericity_score": 0.0-1.0,
  "contradiction_count": integer,
  "written_response_integration": 0-6,
  "quality_flags": ["high_diagnostic", "no_genericity", "tension_aware"]
}
```

---

# PAGE 01 — COVER / IDENTITY

```json
"page01_cover": {
  "profile_signature_interpretation": "AI_GENERATED_PARAGRAPH (80-120 words)",
  "profile_code_string": "DERIVED_LABEL (e.g. V3S2F4V3L2H1F2)",
  "vector_code": "DERIVED_LABEL (V3)",
  "vector_label": "Command (Vector)",
  "vector_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "fidelity_code": "DERIVED_LABEL (F2)",
  "fidelity_label": "Precision (Fidelity)",
  "fidelity_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "framework_code": "DERIVED_LABEL",
  "framework_label": "Structure (Framework)",
  "framework_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "velocity_code": "DERIVED_LABEL",
  "velocity_label": "Tempo (Velocity)",
  "velocity_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "leverage_code": "DERIVED_LABEL",
  "leverage_label": "Influence (Leverage)",
  "leverage_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "horizon_code": "DERIVED_LABEL",
  "horizon_label": "Perspective (Horizon)",
  "horizon_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "signal_code": "DERIVED_LABEL",
  "signal_label": "Relational Awareness (Signal)",
  "signal_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "flex_code": "DERIVED_LABEL",
  "flex_label": "Adaptability (Flex)",
  "flex_explanation": "AI_GENERATED_PARAGRAPH (25 words)",
  "core_edge_icon": "DERIVED_LABEL",
  "core_edge_narrative": "AI_GENERATED_PARAGRAPH (60-90 words)",
  "confidence_level": "DETERMINISTIC_SCORE",
  "profile_type": "DERIVED_LABEL"
}
```

**Source Inputs:** dimension_scores, written_responses.q2, written_responses.q24  
**Quality Rules:** No generic praise. Must reference specific behavioral tensions.  
**Fallback:** If low confidence, use shorter explanations.

---

# PAGE 02 — BEHAVIORAL OPERATING SYSTEM MAP

```json
"page02_operating_system_map": {
  "system_tension_warning": "SYSTEM_WARNING (40 words)",
  "core_engine_heading": "DERIVED_LABEL",
  "core_engine_summary": "AI_GENERATED_PARAGRAPH (50 words)",
  "primary_driver_name": "DERIVED_LABEL",
  "primary_driver_icon": "DERIVED_LABEL",
  "primary_driver_bullet_1": "AI_GENERATED_BULLETS (15 words)",
  "primary_driver_bullet_2": "AI_GENERATED_BULLETS (15 words)",
  "primary_driver_bullet_3": "AI_GENERATED_BULLETS (15 words)",
  "primary_driver_bullet_4": "AI_GENERATED_BULLETS (15 words)",
  "secondary_stabilizer_name": "DERIVED_LABEL",
  "secondary_stabilizer_icon": "DERIVED_LABEL",
  "secondary_stabilizer_bullet_1": "AI_GENERATED_BULLETS (15 words)",
  "secondary_stabilizer_bullet_2": "AI_GENERATED_BULLETS (15 words)",
  "secondary_stabilizer_bullet_3": "AI_GENERATED_BULLETS (15 words)",
  "secondary_stabilizer_bullet_4": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_1_name": "DERIVED_LABEL",
  "opposing_pattern_1_icon": "DERIVED_LABEL",
  "opposing_pattern_1_bullet_1": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_1_bullet_2": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_1_bullet_3": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_1_bullet_4": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_2_name": "DERIVED_LABEL",
  "opposing_pattern_2_icon": "DERIVED_LABEL",
  "opposing_pattern_2_bullet_1": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_2_bullet_2": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_2_bullet_3": "AI_GENERATED_BULLETS (15 words)",
  "opposing_pattern_2_bullet_4": "AI_GENERATED_BULLETS (15 words)",
  "system_tension_summary": "AI_GENERATED_PARAGRAPH (100 words)",
  "legend_primary_driver_text": "DERIVED_LABEL",
  "legend_secondary_stabilizer_text": "DERIVED_LABEL",
  "legend_opposing_patterns_text": "DERIVED_LABEL"
}
```

**Source Inputs:** top_systems, dimension_scores, contradictions  
**Quality Rules:** Each bullet must be unique behavioral manifestation. No trait lists.  
**Fallback:** Use deterministic node names if low confidence.

---

# PAGE 03 — EXECUTIVE SUMMARY

```json
"page03_executive_summary": {
  "summary_text": "AI_GENERATED_PARAGRAPH (150 words)",
  "leadership_heading": "MIXED_SCORE_AND_AI",
  "leadership_body": "AI_GENERATED_PARAGRAPH (60 words)",
  "development_heading": "MIXED_SCORE_AND_AI",
  "development_body": "AI_GENERATED_PARAGRAPH (60 words)",
  "priority_heading": "DEVELOPMENT_PRIORITY",
  "priority_body": "AI_GENERATED_PARAGRAPH (60 words)"
}
```

**Source Inputs:** dimension_scores, top_systems, contradictions, profile_flags  
**Quality Rules:** High-level synthesis. Must connect dots between systems.  
**Fallback:** Focus on top 3 dimensions only.

---

# PAGE 04 — OPERATING PATTERN

```json
"page04_operating_pattern": {
  "operating_pattern_body_1": "AI_GENERATED_PARAGRAPH (60 words)",
  "operating_pattern_body_2": "AI_GENERATED_PARAGRAPH (60 words)",
  "operating_pattern_body_3": "AI_GENERATED_PARAGRAPH (60 words)",
  "operating_pattern_body_4": "AI_GENERATED_PARAGRAPH (60 words)",
  "strongest_default_heading": "DERIVED_LABEL",
  "strongest_default_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "likely_blind_spot_heading": "DERIVED_LABEL",
  "likely_blind_spot_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "highest_value_adjustment_heading": "DEVELOPMENT_PRIORITY",
  "highest_value_adjustment_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "development_priority_heading": "DEVELOPMENT_PRIORITY",
  "development_priority_body": "AI_GENERATED_PARAGRAPH (100 words)"
}
```

**Source Inputs:** top_systems, profile_flags, contradictions  
**Quality Rules:** Operational description of natural operating mode.  
**Fallback:** Focus on primary + secondary systems.

---

# PAGE 05 — DECISION ARCHITECTURE

```json
"page05_decision_architecture": {
  "decision_architecture_narrative_1": "AI_GENERATED_PARAGRAPH (100 words)",
  "decision_architecture_narrative_2": "AI_GENERATED_PARAGRAPH (100 words)",
  "decision_trait_1_heading": "DERIVED_LABEL",
  "decision_trait_1_value": "DETERMINISTIC_SCORE (%)",
  "decision_trait_2_heading": "DERIVED_LABEL",
  "decision_trait_2_value": "DETERMINISTIC_SCORE (%)",
  "advantage_heading": "DERIVED_LABEL",
  "advantage_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "failure_heading": "DERIVED_LABEL",
  "failure_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "upgrade_heading": "DEVELOPMENT_PRIORITY",
  "upgrade_body": "AI_GENERATED_PARAGRAPH (80 words)"
}
```

**Source Inputs:** dimension_scores.fidelity/velocity/framework, written_responses.q10  
**Quality Rules:** Decision mechanism under different conditions.  
**Fallback:** Use score-derived traits.

---

# PAGE 06 — COMMUNICATION STYLE

```json
"page06_communication_style": {
  "signal_matrix_explanation": "AI_GENERATED_PARAGRAPH (100 words)",
  "others_experience_1_heading": "DERIVED_LABEL",
  "others_experience_1_body": "AI_GENERATED_PARAGRAPH (60 words)",
  "others_experience_2_heading": "DERIVED_LABEL",
  "others_experience_2_body": "AI_GENERATED_PARAGRAPH (60 words)",
  "others_experience_3_heading": "DERIVED_LABEL",
  "others_experience_3_body": "AI_GENERATED_PARAGRAPH (60 words)",
  "communication_advantage_heading": "DERIVED_LABEL",
  "communication_advantage_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "communication_friction_heading": "DERIVED_LABEL",
  "communication_friction_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "communication_upgrade_heading": "DEVELOPMENT_PRIORITY",
  "communication_upgrade_body": "AI_GENERATED_PARAGRAPH (80 words)"
}
```

**Source Inputs:** dimension_scores.signal/flex, written_responses.q2  
**Quality Rules:** How others experience this person's communication. Q2 heavy.  
**Fallback:** Use signal score + language signals.

---

# PAGE 07 — SYSTEM UNDER STRAIN

```json
"page07_system_under_strain": {
  "pressure_response_explanation": "AI_GENERATED_PARAGRAPH (100 words)",
  "escalation_chain_explanation": "AI_GENERATED_PARAGRAPH (100 words)",
  "blind_spot_field_explanation": "AI_GENERATED_PARAGRAPH (80 words)",
  "friction_patterns_explanation": "AI_GENERATED_PARAGRAPH (100 words)",
  "recalibration_priorities_explanation": "DEVELOPMENT_PRIORITY (100 words)"
}
```

**Source Inputs:** pressure_analysis, written_responses.q15/q24, profile_flags  
**Quality Rules:** Pressure response mechanism. Q15/Q24 heavy.  
**Fallback:** Use pressure_analysis patterns.

---

# PAGE 08 — OPERATING ENVIRONMENT FIT

```json
"page08_operating_environment_fit": {
  "high_traction_environments_body": "AI_GENERATED_PARAGRAPH (100 words)",
  "high_traction_card_heading": "DERIVED_LABEL",
  "high_traction_card_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "conditional_fit_environments_body": "AI_GENERATED_PARAGRAPH (100 words)",
  "conditional_fit_card_heading": "DERIVED_LABEL",
  "conditional_fit_card_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "high_friction_environments_body": "AI_GENERATED_PARAGRAPH (100 words)",
  "high_friction_card_heading": "DERIVED_LABEL",
  "high_friction_card_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "horizon_shift_heading": "DEVELOPMENT_PRIORITY",
  "horizon_shift_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "adapt_shift_heading": "DEVELOPMENT_PRIORITY",
  "adapt_shift_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "input_shift_heading": "DEVELOPMENT_PRIORITY",
  "input_shift_body": "AI_GENERATED_PARAGRAPH (80 words)"
}
```

**Source Inputs:** dimension_scores, profile_flags, written_responses.q20  
**Quality Rules:** Where this operating system thrives vs struggles.  
**Fallback:** Use top_systems + low dimensions.

---

# PAGE 09 — FACILITATOR NOTES

```json
"page09_facilitator_notes": {
  "facilitator_interpretation_body": "FACILITATOR_NOTE (150 words)",
  "coaching_intervention_body": "FACILITATOR_NOTE (150 words)",
  "development_edges_body": "FACILITATOR_NOTE (150 words)",
  "coaching_questions_body": "FACILITATOR_NOTE (150 words)"
}
```

**Source Inputs:** All data, all written responses, contradictions  
**Quality Rules:** Coach-to-coach. How to work WITH this person. All Q heavy.  
**Fallback:** Use confidence_engine + profile_flags.

---

# PAGE 10 — FULL PROFILE UNLOCKS / OPERATING DNA

```json
"page10_full_profile_unlocks": {
  "operating_dna_subtitle": "DERIVED_LABEL",
  "unlock_area_1_heading": "DERIVED_LABEL",
  "unlock_area_1_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "unlock_area_2_heading": "DERIVED_LABEL",
  "unlock_area_2_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "advanced_system_1_heading": "DERIVED_LABEL",
  "advanced_system_1_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "advanced_system_2_heading": "DERIVED_LABEL",
  "advanced_system_2_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "core_force_heading": "DERIVED_LABEL",
  "core_force_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "hidden_cost_heading": "DERIVED_LABEL",
  "hidden_cost_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "next_evolution_heading": "DEVELOPMENT_PRIORITY",
  "next_evolution_body": "AI_GENERATED_PARAGRAPH (80 words)",
  "why_this_matters_body": "AI_GENERATED_PARAGRAPH (100 words)"
}
```

**Source Inputs:** All data, contradictions, profile_flags  
**Quality Rules:** Evolution edge. Hidden costs.  
**Fallback:** Use top_systems + profile_flags.

---

# GENERATION METADATA

```json
"generation_metadata": {
  "genericity_score": 0.0-1.0,
  "banned_phrases_detected": ["natural leader", "strong communicator"],
  "contradiction_count": integer,
  "written_integration_count": 0-6,
  "quality_flags": ["high_diagnostic", "tension_aware", "no_genericity"],
  "generation_mode": "gpt-5.5|mock|deterministic",
  "model_used": "gpt-5.5",
  "temperature": 0.3,
  "max_tokens": integer,
  "validation_passed": boolean
}
```

---

# QUALITY GUARDRAILS

## Runtime Checks

1. **All 10 page keys present:** Throw error if missing
2. **Genericity scan:** Flag banned phrases (30+ prohibited terms)
3. **Contradiction count:** Must acknowledge contradictions if present
4. **Written integration:** Must reference written responses in Pages 6,7,9
5. **Tension awareness:** Must name at least one tradeoff per page
6. **No repetition:** Check for repeated phrases across pages

## Fallback Behavior

**Low Confidence:** Use shorter, more deterministic content
**High Genericity:** Regenerate with stricter guardrails
**Missing Data:** Use profile_flags + dimension_scores only

---

**END OF FILE: REPORT_CONTENT_SCHEMA_V1.md**