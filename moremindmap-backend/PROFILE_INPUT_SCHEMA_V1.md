# Profile Input Schema V1
**Created:** Tue May 12, 2026 21:33 MST  
**Purpose:** Canonical normalized interpreter payload structure  
**Philosophy:** Clean intelligence object. GPT receives forensic data, not raw chaos.

---

# Overview

The profile input object is the SINGLE SOURCE OF TRUTH for all future GPT generation.

It normalizes and structures:
- 24 assessment answers
- Deterministic dimension scores
- Written response extraction
- Language signal analysis
- Contradiction detection
- Pressure indicators
- Behavioral flags

GPT consumes this ONE object to generate all 95 report fields.

---

# Root Structure

```json
{
  "metadata": {...},
  "raw_answers": {...},
  "dimension_scores": {...},
  "top_systems": {...},
  "written_responses": {...},
  "language_signals": {...},
  "contradictions": {...},
  "pressure_analysis": {...},
  "profile_flags": {...},
  "confidence_engine": {...}
}
```

---

# SECTION 1: ROOT METADATA

```json
"metadata": {
  "assessment_id": "unique identifier",
  "generated_at": "ISO-8601 timestamp",
  "profile_version": "mini-v2",
  "question_set_version": "set_1_v1",
  "question_count": 24,
  "written_response_count": 6,
  "multiple_choice_count": 18,
  "confidence_score": 0.0-1.0,
  "assessment_duration_seconds": integer,
  "completion_date": "ISO-8601",
  "data_quality": "high|moderate|low"
}
```

**quality_score reasoning:**
- HIGH: All written responses detailed, MC answered, contradictions minimal
- MODERATE: Some written responses brief, some contradictions detected
- LOW: Minimal written responses, significant contradictions, defensive language

---

# SECTION 2: RAW ANSWERS

```json
"raw_answers": {
  "q1": {
    "question_id": 1,
    "question_type": "mc",
    "question_text": "...",
    "answer_choice": "A",
    "answer_text": "...",
    "normalized_dimensions": {
      "vector": 3,
      "signal": 1,
      "fidelity": 2,
      ...
    }
  },
  "q2": {
    "question_id": 2,
    "question_type": "written",
    "question_text": "...",
    "answer_text": "[full written response]",
    "character_count": integer,
    "word_count": integer,
    "sentence_count": integer
  },
  ... q3-q24 following same pattern
}
```

**normalized_dimensions for MC:**
- Maps choice (A/B/C/D/E) to dimension scores
- Uses questionMap.js scoring rules
- Extracted automatically from QUESTION_MAP

---

# SECTION 3: DIMENSION SCORES

```json
"dimension_scores": {
  "vector": {
    "raw_score": 0.0-4.0,
    "normalized_percent": 0-100,
    "rank": 1-8,
    "confidence": 0.5-1.0,
    "contributing_answers": [1, 5, 9, 13, 17, 21],
    "label": "Command (Vector)",
    "description": "Tendency to move toward clear direction; command bias"
  },
  "signal": {
    "raw_score": 0.0-4.0,
    "normalized_percent": 0-100,
    "rank": 1-8,
    "confidence": 0.5-1.0,
    "contributing_answers": [2, 6, 10, 14, 18, 22],
    "label": "Relational Awareness (Signal)",
    "description": "Tendency to read room dynamics; relational calibration"
  },
  "fidelity": {...},
  "velocity": {...},
  "leverage": {...},
  "flex": {...},
  "framework": {...},
  "horizon": {...}
}
```

**confidence scoring:**
- HIGH (0.8-1.0): Multiple questions agree, written responses confirm, no contradiction
- MODERATE (0.6-0.8): Some agreement, minor contradictions
- LOW (0.5-0.6): Weak signal, contradictions present, defensive language

---

# SECTION 4: TOP SYSTEMS

Automatically derived from dimension scores. NOT static labels.

```json
"top_systems": {
  "primary_driver": {
    "dimension": "vector",
    "score": 3.5,
    "rank": 1,
    "description": "Command and decisiveness",
    "operating_manifestation": "Enters situations with direction already forming...",
    "pressure_manifestation": "Under strain, decision speed increases, relational awareness decreases"
  },
  "secondary_stabilizer": {
    "dimension": "fidelity",
    "score": 2.8,
    "rank": 2,
    "description": "Precision and detail-orientation",
    "operating_manifestation": "Catches errors others miss...",
    "pressure_manifestation": "Under strain, precision preference increases; can create micro-delays"
  },
  "opposing_pattern_1": {
    "dimension": "signal",
    "score": 1.2,
    "rank": 8,
    "description": "Low relational awareness",
    "operating_manifestation": "Misses subtle room dynamics...",
    "pressure_manifestation": "Under strain, relational blindness increases; silent resistance accumulates"
  },
  "opposing_pattern_2": {
    "dimension": "flex",
    "score": 1.5,
    "rank": 7,
    "description": "Low adaptability",
    "operating_manifestation": "Prefers familiar patterns...",
    "pressure_manifestation": "Under strain, rigidity increases; resistance to iteration"
  },
  "dimension_tradeoffs": [
    {
      "dimensions": ["vector", "signal"],
      "tradeoff": "Command creates unread resistance. Speed suppresses relational calibration.",
      "cost": "Decisions move fast but miss stakeholder stakes"
    },
    {
      "dimensions": ["fidelity", "velocity"],
      "tradeoff": "Precision takes time. Speed reduces detail.",
      "cost": "Time pressure forces choice between accuracy and deadline"
    }
  ],
  "dimension_synergies": [
    {
      "dimensions": ["vector", "fidelity"],
      "synergy": "Command + precision = decisive with rigor",
      "benefit": "Clear decisions with evidence behind them"
    }
  ]
}
```

---

# SECTION 5: WRITTEN RESPONSE LAYER

```json
"written_responses": {
  "q2_communication": {
    "question_id": 2,
    "question_text": "Describe a recent situation where someone misunderstood your intentions...",
    "response_text": "[full response]",
    "metadata": {
      "word_count": integer,
      "character_count": integer,
      "sentence_count": integer,
      "paragraph_count": integer
    },
    "extraction_signals": {
      "blame_mentions": integer,
      "ownership_mentions": integer,
      "abstraction_level": 1-5,
      "emotional_tone": "neutral|defensive|reflective|analytical",
      "certainty_level": 1-5,
      "narrative_density": 1-5
    }
  },
  "q6_leverage": {...},
  "q10_decision": {...},
  "q15_strain": {...},
  "q20_environment": {...},
  "q24_complexity": {...}
}
```

---

# SECTION 6: LANGUAGE SIGNALS

Extracted from all 6 written responses.

```json
"language_signals": {
  "blame_pattern": {
    "total_blame_mentions": integer,
    "total_ownership_mentions": integer,
    "blame_ratio": 0.0-1.0,
    "ownership_ratio": 0.0-1.0,
    "interpretation": "Blame-external|Balanced|Ownership-internal",
    "confidence": 0.5-1.0,
    "evidence": [{"quote": "...", "type": "blame"}]
  },
  "abstraction_level": {
    "average_abstraction": 1-5,
    "range": [min, max],
    "pattern": "Concrete-narrative|Mixed|Abstract-systems",
    "interpretation": "Grounds in specific moments vs sees patterns vs intellectualizes",
    "evidence": [{"quote": "...", "level": 3}]
  },
  "emotional_compression": {
    "emotional_mentions": integer,
    "defensive_language": integer,
    "reflective_language": integer,
    "emotional_tone": "High|Moderate|Low",
    "interpretation": "Expresses emotions openly|Manages emotions|Intellectualizes",
    "evidence": [{"quote": "...", "type": "defensive"}]
  },
  "certainty_level": {
    "hedging_language": integer,
    "assertive_language": integer,
    "uncertainty_ratio": 0.0-1.0,
    "pattern": "High-certainty|Moderate|High-uncertainty",
    "interpretation": "States clearly OR questions themselves"
  },
  "defensiveness": {
    "defensive_phrases": integer,
    "justification_phrases": integer,
    "defensiveness_score": 0-10,
    "interpretation": "Not-defensive|Somewhat-defensive|Highly-defensive",
    "signals": ["shouldn't have", "wasn't my job", "miscommunication"],
    "evidence": [{"quote": "..."}]
  },
  "sentence_complexity": {
    "average_sentence_length": integer,
    "complex_sentences_percent": 0-100,
    "pattern": "Simple|Mixed|Complex",
    "interpretation": "Unintegrated (stress)|Normal|Highly-integrated (overthinking)"
  },
  "narrative_density": {
    "information_density": 1-5,
    "reflection_depth": 1-5,
    "pattern": "Minimal|Moderate|Dense",
    "interpretation": "Didn't reflect|Normal reflection|Deep exploration"
  },
  "control_orientation": {
    "control_language": integer,
    "surrender_language": integer,
    "control_ratio": 0.0-1.0,
    "pattern": "High-control|Balanced|Low-control",
    "interpretation": "Sees self as agent OR patient"
  }
}
```

---

# SECTION 7: CONTRADICTIONS

```json
"contradictions": {
  "mc_vs_written": [
    {
      "contradiction_id": "mc_written_01",
      "type": "MC_vs_Written",
      "mc_question": 1,
      "mc_answer": "A",
      "mc_dimension_scores": {"vector": 3, "signal": 1},
      "written_question": 2,
      "written_evidence": "Describes decision-making as collaborative and input-seeking",
      "contradiction": "MC shows high vector (command). Written shows collaborative pattern.",
      "interpretation": "Gap between aspiration (collaboration) and default (command)",
      "severity": "high|moderate|low",
      "confidence": 0.5-1.0
    }
  ],
  "score_vs_behavior": [
    {
      "contradiction_id": "score_behavior_01",
      "type": "Score_vs_Behavior",
      "dimension": "signal",
      "score": 1.2,
      "written_evidence": "Describes reading room dynamics well",
      "contradiction": "Low signal score contradicted by written description",
      "interpretation": "They're aware low signal creates problems; they're trying to compensate",
      "severity": "moderate",
      "confidence": 0.7
    }
  ],
  "identity_vs_consequence": [
    {
      "contradiction_id": "identity_consequence_01",
      "type": "Identity_vs_Consequence",
      "stated_identity": "I'm collaborative",
      "behavioral_consequence": "People are surprised by decisions",
      "contradiction": "See themselves as collaborative; others experience as unilateral",
      "interpretation": "Low relational awareness of impact. Unaware of perception gap.",
      "severity": "high",
      "confidence": 0.85
    }
  ],
  "competing_high_scores": [
    {
      "contradiction_id": "competing_high_01",
      "type": "Competing_High_Scores",
      "dimensions": ["vector", "signal", "fidelity"],
      "scores": [3.5, 3.2, 3.1],
      "contradiction": "Can't maximize all three under pressure",
      "interpretation": "Experiencing paradox-strain; something has to give",
      "severity": "moderate",
      "confidence": 0.9
    }
  ],
  "explanation_complexity_mismatch": [
    {
      "contradiction_id": "complexity_mismatch_01",
      "type": "Explanation_Complexity",
      "framework_score": 3.5,
      "written_explanation": "Simple, straightforward",
      "contradiction": "High structure score but simple written explanation",
      "interpretation": "What complexity are they avoiding?",
      "severity": "low",
      "confidence": 0.6
    }
  ],
  "total_contradictions": integer,
  "contradiction_severity_summary": "high|moderate|low",
  "contradiction_penalty_on_confidence": -0.0 to -0.3
}
```

---

# SECTION 8: PRESSURE ANALYSIS

```json
"pressure_analysis": {
  "immediate_stress_response": {
    "source": "Q15 written response",
    "pattern_type": "Tighter+Faster|Slower+Deeper|Withdrawal+Rigidity|Acceleration+Delegation",
    "description": "What happens first when stressed",
    "evidence": "...",
    "mechanism": "ambiguity feels unsafe; control via X",
    "works_for": ["crisis execution", "command clarity"],
    "fails_for": ["political problems", "iteration"],
    "people_experience": "How others perceive this response"
  },
  "sustained_stress_response": {
    "source": "Q24 written response",
    "pattern_type": "Tighter+Faster|Slower+Deeper|Withdrawal+Rigidity|Acceleration+Delegation",
    "description": "What happens after sustained strain",
    "evidence": "...",
    "escalation_vs_adaptation": "Do they adapt or escalate?"
  },
  "stress_response_chain": {
    "phase_1": "immediate_stress_response",
    "phase_2": "sustained_stress_response",
    "breakpoint": "Where does the response break? (if at all)",
    "interpretation": "2-phase response: Phase 1 = try to manage, Phase 2 = shift to control/escape"
  },
  "escalation_pattern": {
    "first_escalation": "What happens first",
    "second_escalation": "What happens next",
    "hidden_cost": "What breaks under sustained strain",
    "blind_spots_under_strain": ["What they miss", "What they can't see"]
  },
  "control_mechanisms": {
    "primary": "How they try to regain control (structure|speed|delegation|connection)",
    "secondary": "What they do if primary fails",
    "breaking_point": "When control mechanisms fail entirely"
  },
  "pressure_indicators": [
    "high_rigidity_under_strain",
    "over_control_risk",
    "communication_shutdown",
    "relational_withdrawal",
    "speed_escalation",
    "detail_perfectionism_under_pressure"
  ]
}
```

---

# SECTION 9: PROFILE FLAGS

Derived behavioral risk indicators and operating characteristics.

```json
"profile_flags": {
  "high_rigidity": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["low flex score", "repeated 'familiar patterns' in written"],
    "operational_consequence": "Struggles with novel situations, iteration cycles"
  },
  "over_control_risk": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high framework", "high vector", "low flex"],
    "operational_consequence": "Tightens structure under stress; can feel suffocating"
  },
  "nuance_suppression": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high velocity", "low fidelity", "abstract written responses"],
    "operational_consequence": "Misses important details; moves fast over precision"
  },
  "speed_bias": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high velocity", "low framework", "movement preference in written"],
    "operational_consequence": "Prefers action over planning; can miss consequences"
  },
  "collaboration_instability": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high vector", "low signal", "collaboration aspiration vs unilateral behavior"],
    "operational_consequence": "Says collaborative; acts unilateral. Stakeholder friction."
  },
  "hidden_burnout_risk": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["contradictions", "defensive language", "compensation patterns"],
    "operational_consequence": "Maintaining compensatory behavior; sustainability risk"
  },
  "communication_compression": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high velocity", "low signal", "brief written responses"],
    "operational_consequence": "Explains decisions poorly; people feel left behind"
  },
  "relational_blindness": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["low signal", "unread resistance in written"],
    "operational_consequence": "Misses stakeholder stakes; discovers misalignment late"
  },
  "perfectionism_friction": {
    "flag": boolean,
    "severity": 0-10,
    "evidence": ["high fidelity", "time-pressure stress response", "precision non-negotiable"],
    "operational_consequence": "Creates delays; team frustration with standards"
  }
}
```

---

# SECTION 10: CONFIDENCE ENGINE

```json
"confidence_engine": {
  "overall_confidence": 0.0-1.0,
  "confidence_rationale": "Based on data quality, consistency, written depth, contradiction severity",
  "section_confidence": {
    "dimension_scores": 0.0-1.0,
    "written_responses": 0.0-1.0,
    "pressure_analysis": 0.0-1.0,
    "contradictions": 0.0-1.0,
    "language_signals": 0.0-1.0
  },
  "data_quality_factors": {
    "written_response_depth": 0-10,
    "defensive_language_penalty": -0.0 to -0.2,
    "contradiction_penalty": -0.0 to -0.3,
    "consistency_bonus": +0.0 to +0.1,
    "pattern_repetition_bonus": +0.0 to +0.1
  },
  "weak_inference_zones": [
    {"zone": "section_name", "reason": "insufficient_data|defensive_language|contradiction"}
  ],
  "strong_inference_zones": [
    {"zone": "section_name", "reason": "pattern_repeats_across_3_sources|high_consistency"}
  ]
}
```

---

# Complete Schema Summary

**Total Root Sections:** 10
1. metadata
2. raw_answers
3. dimension_scores
4. top_systems
5. written_responses
6. language_signals
7. contradictions
8. pressure_analysis
9. profile_flags
10. confidence_engine

**Total Data Points:** ~200+ individual fields

**GPT Consumption Path:**
```
profile_input.json
  ↓
[Load into GPT context]
  ↓
[GPT iterates through 95 fields]
  ↓
[GPT consumes relevant sections for each field]
  ↓
[GPT generates field output]
  ↓
[Template injection]
  ↓
[10-page PDF report]
```

**Key Principle:** GPT receives FORENSIC DATA, not chaos. Clean. Structured. Intelligent.

---

**END OF FILE: PROFILE_INPUT_SCHEMA_V1.md**