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
  const completeData = {
    title: scoredData.headline || "Mini V2 Profile Analysis",
    subtitle: "Generated Report",
    description: "This is a mock profile report generated for testing purposes.",
    footer: "© MOREMindMap 2026 - Test Run",
    operating_system_map_placeholder: "Operating System Map visualization placeholder",
    summary_text: "This executive summary summarizes the key findings from the behavioral analysis.",
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

  const pageCount = (htmlContent.match(/class="mmm-page page\d+"/g) || []).length;
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
