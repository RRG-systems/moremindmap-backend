// moremindmap-backend/engine/testGenerateMiniV2HTML.js
// Recreated May 11, 2026

import fs from 'fs/promises';
import path from 'path';
import * as generateHTMLModule from './generateMiniV2HTML.js';
import { scoreAnswers } from './scoreAssessment.js';

const mockAnswers = Array.from({ length: 24 }, (_, i) => ({
  id: `q${i + 1}`,
  type: i % 3 === 0 ? 'mc' : 'written',
  answer: i % 3 === 0 ? String.fromCharCode(65 + (i % 5)) : `Written answer ${i+1}`,
  response: i % 3 !== 0 ? `This is a mock written response for question ${i+1}.` : undefined
}));

async function runTest() {
  console.log("Starting Mini V2 HTML generation test...");

  const scoredData = scoreAnswers(mockAnswers);

  // Complete data object with ALL placeholders from MINI_V2_PLACEHOLDER_CONTRACT.json
  // NOTE: Updated to include placeholders for ALL pages and new structures.
  const completeData = {
    // General Report Placeholders (added for consistency)
    title: scoredData.headline || "Mini V2 Profile Analysis",
    subtitle: "Generated Report",
    description: "This is a mock profile report generated for testing purposes.",
    footer: "© MOREMindMap 2026 - Test Run",
    assessment_date: "May 12, 2026",
    confidence_level: "85%",
    profile_type: "Behavioral Operating Profile",

    // Page 1 Placeholders
    profile_signature_narrative: "Your behavioral signature reflects a strategic, systems-oriented operating mode with high signal clarity and decisive action orientation.",
    core_edge_narrative: "Your core edge lies in rapidly synthesizing complex information into actionable frameworks while maintaining operational velocity under constraint.",

    // Page 2 Placeholders
    page2_title: "Behavioral Operating System Map",
    page2_subtitle: "System architecture: how you prioritize, decide, and respond",
    core_engine_heading: "Strategic Systems Processor",
    core_engine_summary: "Integrates complexity into clear, actionable systems. Maintains velocity without sacrificing structural integrity.",
    primary_driver_label: "PRIMARY DRIVER",
    primary_driver_name: "Signal Clarity & Velocity",
    primary_driver_code: "V+S",
    primary_driver_icon: "⚡",
    primary_driver_side_heading: "Drives the System Forward",
    primary_driver_description: "Rapidly identifies high-value signals, prioritizes what matters most, and executes with decisive momentum.",
    secondary_stabilizer_label: "SECONDARY STABILIZER",
    secondary_stabilizer_name: "Framework Rigor",
    secondary_stabilizer_code: "F+R",
    secondary_stabilizer_icon: "⊞",
    secondary_stabilizer_side_heading: "Brings Structure & Discipline",
    secondary_stabilizer_description: "Applies analytical rigor, standards, and systems to ensure accuracy, consistency, and reliability.",
    secondary_stabilizer_subheading: "Extends Decision Horizon",
    secondary_stabilizer_subbody: "Slows to ensure quality and long-term integrity.",
    opposing_pattern_1_name: "Signal",
    opposing_pattern_1_code: "S-",
    opposing_pattern_1_icon: "⊗",
    opposing_pattern_1_heading: "Relational Awareness & Intuition",
    opposing_pattern_1_description: "Reads between the lines, senses dynamics, and adapts to human context.",
    opposing_pattern_1_lowest_capacity: "May under-leverage relational nuance or intuitive signals.",
    opposing_pattern_2_name: "Flex",
    opposing_pattern_2_code: "F-",
    opposing_pattern_2_icon: "↻",
    opposing_pattern_2_heading: "Adaptability & Fluidity",
    opposing_pattern_2_description: "Adapts to change, improvises, and shifts quickly in dynamic conditions.",
    opposing_pattern_2_lowest_capacity: "Creates friction when continuous shifting is required.",
    left_tension_label: "Driver Tension",
    right_tension_label: "Stabilizer Tension",
    bottom_tension_label: "Opposition Tension",
    system_tension_warning: "Under high ambiguity, tendency to over-index on speed may compromise depth. Monitor for premature closure on incomplete data sets.",
    system_tension_summary: "Your system is optimized for precision and structural integrity. Under ambiguity, monitor for speed bias that may limit depth and relational inputs.",
    legend_primary_driver_text: "Primary Driver",
    legend_secondary_stabilizer_text: "Secondary Stabilizer",
    legend_opposing_patterns_text: "Opposing Patterns",

    // Page 3 Placeholders
    summary_text: "This executive summary summarizes the key findings from the behavioral analysis.",
    leadership_heading: "Leadership Signal",
    leadership_body: "Focuses on how the individual leads and influences.",
    development_heading: "Development Opportunity",
    development_body: "Key areas for growth and skill enhancement.",
    priority_heading: "Strategic Priority",
    priority_body: "The most critical focus for immediate action.",
    page_number_box_3: "3",

    // Page 4 Placeholders
    operating_pattern_body_1: "This is the first paragraph of the operating pattern description, detailing inherent tendencies.",
    operating_pattern_body_2: "This paragraph focuses on how these patterns manifest in daily activities.",
    operating_pattern_body_3: "The third paragraph delves into common scenarios where these patterns are most evident.",
    operating_pattern_body_4: "The fourth paragraph discusses implications for decision-making and environment fit.",
    strongest_default_heading: "Strongest Default Pattern",
    strongest_default_body: "Highlights the most dominant and natural behavioral tendency.",
    likely_blind_spot_heading: "Likely Blind Spot",
    likely_blind_spot_body: "Identifies potential areas of unawareness stemming from the default pattern.",
    highest_value_adjustment_heading: "Highest Value Adjustment",
    highest_value_adjustment_body: "Focuses on impactful adjustments to leverage strengths and mitigate blind spots.",
    development_priority_heading: "KEY DEVELOPMENT PRIORITY",
    development_priority_body: "Primary focus for growth related to the operating pattern.",
    page_number_box_4: "4",

    // Page 5 Placeholders
    decision_architecture_narrative_1: "Detailed explanation of decision-making style, including factors like speed and reliance on external data.",
    decision_architecture_narrative_2: "Further elaboration on cognitive approaches to complex choices and risk assessment.",
    decision_trait_1_heading: "Closure Speed",
    decision_trait_1_value: "80",
    decision_trait_2_heading: "Evidence Threshold",
    decision_trait_2_value: "70",
    advantage_heading: "Decision Advantage",
    advantage_body: "The core strengths in decision-making.",
    failure_heading: "Decision Failure Point",
    failure_body: "Potential pitfalls or weaknesses in the decision process.",
    upgrade_heading: "Decision Upgrade Path",
    upgrade_body: "Areas for improvement in decision-making.",
    page_number_box_5: "5",

    // Page 6 Placeholders
    signal_matrix_explanation: "Analysis of how signals are perceived, transmitted, and interpreted.",
    others_experience_1_heading: "Transmission Pattern",
    others_experience_1_body: "How others typically experience your communication.",
    others_experience_2_heading: "Directness vs. Subtlety",
    others_experience_2_body: "Your tendency towards directness or indirect communication.",
    others_experience_3_heading: "Receptivity to Feedback",
    others_experience_3_body: "How open you are to receiving and acting on feedback.",
    communication_advantage_heading: "Communication Advantage",
    communication_advantage_body: "Strengths in conveying information effectively.",
    communication_friction_heading: "Communication Friction",
    communication_friction_body: "Potential sources of miscommunication or difficulty.",
    communication_upgrade_heading: "Communication Upgrade",
    communication_upgrade_body: "Areas to enhance communication clarity and impact.",
    page_number_box_6: "6",

    // Page 7 Placeholders
    pressure_response_explanation: "Description of how the system behaves under various forms of pressure.",
    escalation_chain_explanation: "Explanation of the typical escalation points when facing increased pressure.",
    blind_spot_field_explanation: "Identification of areas that become less apparent under strain.",
    friction_patterns_explanation: "Common patterns of friction that emerge during stressful situations.",
    recalibration_priorities_explanation: "Key areas for adjustment to maintain performance under pressure.",
    page_number_box_7: "7",

    // Page 8 Placeholders
    high_traction_environments_body: "Environments where the individual typically thrives and performs optimally.",
    high_traction_card_heading: "Optimal Fit Environment",
    high_traction_card_body: "Detailed description of the ideal environment.",
    conditional_fit_environments_body: "Environments where performance is contingent on specific factors.",
    conditional_fit_card_heading: "Conditional Fit Environment",
    conditional_fit_card_body: "Factors influencing success in moderately suitable environments.",
    high_friction_environments_body: "Environments where the individual is likely to experience significant challenges.",
    high_friction_card_heading: "High Friction Environment",
    high_friction_card_body: "Characteristics of environments that create difficulties.",
    horizon_shift_heading: "Horizon Shift Strategy",
    horizon_shift_body: "Adjusting long-term focus.",
    adapt_shift_heading: "Adaptation Shift Strategy",
    adapt_shift_body: "Adjusting to immediate situational changes.",
    input_shift_heading: "Input Shift Strategy",
    input_shift_body: "Modifying how information is received or processed.",
    page_number_box_8: "8",

    // Page 9 Placeholders
    facilitator_interpretation_body: "Guidance for facilitators on interpreting the profile results.",
    coaching_intervention_body: "Recommendations for coaching actions based on the profile.",
    development_edges_body: "Specific edges or opportunities for development.",
    coaching_questions_body: "Key questions to explore with the individual during coaching.",
    page_number_box_9: "9",

    // Page 10 Placeholders (Combined and expanded)
    operating_dna_subtitle: "Understanding your core behavioral signature and its implications.",
    unlock_area_1_heading: "Strategic Expansion Opportunity: Application of Core Strengths",
    unlock_area_1_body: "Leveraging the primary driving force for new ventures and strategic growth.",
    unlock_area_2_heading: "Strategic Expansion Opportunity: Mitigating Hidden Costs",
    unlock_area_2_body: "Addressing potential downsides or risks associated with the core force.",
    advanced_system_1_heading: "Advanced System Engagement: Next Evolution Pathways",
    advanced_system_1_body: "Exploring the projected next stage of development and adaptation.",
    advanced_system_2_heading: "Advanced System Engagement: Resilience Under Extremes",
    advanced_system_2_body: "How the system behaves in rare or extreme conditions.",
    core_force_heading: "Core Force: Your Behavioral Signature",
    core_force_body: "The fundamental driving force that shapes your actions and decisions.",
    hidden_cost_heading: "Hidden Cost: Unseen Implications",
    hidden_cost_body: "The potential unseen costs or risks associated with your core force.",
    next_evolution_heading: "Next Evolution: Future Trajectory",
    next_evolution_body: "The projected future development and adaptation of your operating style.",
    why_this_matters_body: "This section explains the significance of understanding your Operating DNA for strategic advantage and personal growth.",
    page_number_box_10: "10",

    // Fallback/general placeholders if needed
    operating_pattern_details: "Details about primary operating patterns and decision-making approaches.",
    decision_architecture_diagram: "Visual representation of decision architecture and frameworks.",
    communication_style_description: "Analysis of communication style, signal processing, and interpersonal dynamics.",
    strain_indicators: "Indicators of how the system performs under pressure, ambiguity, and constraints.",
    environment_fit_analysis: "Analysis of optimal operating environments and cultural fit considerations.",
    facilitator_notes_content: "Notes for facilitators: key observations, coaching recommendations, and development areas.",
    full_profile_unlocks: "Complete profile unlocks: advanced insights and pattern recognition.",
    operating_dna: "Operating DNA: core behavioral signature and cognitive fingerprint."
  };


  const generateHTML =
    generateHTMLModule.generateMiniV2HTML ||
    generateHTMLModule.generateHTML ||
    generateHTMLModule.default;

  if (typeof generateHTML !== 'function') {
    throw new Error(`No HTML generator export found. Available exports: ${Object.keys(generateHTMLModule).join(', ')}`);
  }

  const htmlContent = await generateHTML(completeData);

  if (!htmlContent) {
    console.error("HTML generation failed.");
    process.exit(1);
  }

  // Write baseline artifacts
  const releaseDir = path.resolve('releases/mini-v2-html-baseline');
  const referenceDir = path.resolve('reference/mini-v2-html-baseline');

  await fs.mkdir(releaseDir, { recursive: true });
  await fs.mkdir(referenceDir, { recursive: true });

  const releasePath = path.join(releaseDir, 'mini-v2-html-baseline.html');
  const referencePath = path.join(referenceDir, 'mini-v2-html-baseline.html');

  await fs.writeFile(releasePath, htmlContent, 'utf8');
  await fs.writeFile(referencePath, htmlContent, 'utf8');

  console.log(`\n✓ HTML artifact written: ${releasePath}`);
  console.log(`✓ HTML reference written: ${referencePath}`);

  // Verification
  console.log(`\n--- Verification ---`);
  console.log(`HTML generated successfully`);
  console.log(`HTML length: ${htmlContent.length} characters`);

  const leftovers = htmlContent.match(/\{\{[^}]+\}\}/g) || [];
  console.log(`Remaining placeholders: ${leftovers.length}`);
  if (leftovers.length > 0) {
    console.error(`Unfilled placeholders: ${leftovers.join(', ')}`);
  }

  const pageCount = (htmlContent.match(/class="[^"]*mmm-page[^"]*"/g) || []).length;
  console.log(`Page count: ${pageCount}`);

  if (pageCount === 10 && leftovers.length === 0) {
    console.log("\nTest PASSED: 10 pages generated with 0 remaining placeholders.");
    process.exit(0);
  } else {
    console.error(`\nTest FAILED: Expected 10 pages with 0 placeholders, but found ${pageCount} pages and ${leftovers.length} placeholders.`);
    process.exit(1);
  }
}

runTest();
