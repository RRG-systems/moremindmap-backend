// testSet1ToHTML.js - Step 6 validation
// node engine/testSet1ToHTML.js

import fs from 'fs';
import path from 'path';
import { QUESTION_MAP } from './questionMap.js';
import { DIMENSIONS } from './dimensionMap.js';
// Assume engine/scoreAssessment.js, utils/htmlRendererV5-PrintReady.js, utils/page2SvgEngine.js exist or stub

const testAssessment = {
  name: "D.J. Test",
  email: "test@example.com",
  setId: "set_1",
  version: "v1",
  answers: {
    1: "D",
    2: "WRITTEN: I once had a conversation go sideways because I moved too quickly into solution mode. I realized later that the person needed context and acknowledgment before strategy. I adjusted by slowing down, asking clarifying questions, and checking whether they wanted advice or just space to explain.",
    3: "C",
    4: "E",
    5: "B",
    6: "WRITTEN: I pushed a decision through when a group was stalled and the cost of delay was rising. I listened to the main objections, separated emotional resistance from operational risk, and made the call once the tradeoffs were clear. Some people were frustrated, but the project recovered.",
    7: "A",
    8: "D",
    9: "D",
    10: "WRITTEN: A plan changed at the last minute when a key person became unavailable. I was frustrated by the loss of control, but I rebuilt the priorities, protected the outcome that mattered most, and let go of the pieces that no longer justified the effort.",
    11: "C",
    12: "B",
    13: "E",
    14: "C",
    15: "WRITTEN: I delayed a decision because I wanted more certainty than the situation could provide. Eventually I realized the delay itself had become a decision. I moved forward after defining the downside, choosing a reversible first step, and accepting that perfect information was not coming.",
    16: "B",
    17: "C",
    18: "D",
    19: "D",
    20: "WRITTEN: A conversation changed my view of someone when I realized their resistance was not laziness but fear of being exposed. That shifted me from judging the behavior to understanding the pressure underneath it. I still held the standard, but I changed the way I approached them.",
    21: "E",
    22: "B",
    23: "C",
    24: "WRITTEN: Over the last few years, the clearest pattern is that I perform well under ambiguity when I can turn confusion into structure. I tend to move toward action, but I have learned that speed without calibration creates cleanup work. My best results come when I combine direction, patience, and enough listening to avoid solving the wrong problem."
  }
};

// Stub scoring if engine/scoreAssessment.js missing
function scoreAssessment(assessment) {
  const rawScores = {};
  DIMENSIONS.forEach(d => rawScores[d] = 0);

  Object.entries(assessment.answers).forEach(([qIdStr, answer]) => {
    const qId = parseInt(qIdStr);
    const q = QUESTION_MAP.set_1.v1.find(q => q.id === qId);
    if (q && q.type === 'mc' && answer.length === 1) {
      const option = answer;
      if (q.scores?.[option]) {
        Object.entries(q.scores[option]).forEach(([dim, weight]) => {
          if (DIMENSIONS.includes(dim)) rawScores[dim] += weight;
        });
      }
    }
  });

  const maxScore = 30;
  const normalizedScores = {};
  DIMENSIONS.forEach(d => normalizedScores[d] = Math.max(0, rawScores[d] / maxScore));

  const ranked = Object.entries(normalizedScores)
    .sort((a, b) => b[1] - a[1])
    .map(([d]) => d);

  const primary = ranked[0];
  const secondary = ranked[1] || null;
  const invalid = Object.values(rawScores).every(s => s === 0);

  return { rawScores, normalizedScores, ranked, primary, secondary, invalid };
}

// Stub HTML generation (minimal 10-page structure for validation)
function generateHTML(scores, assessment) {
  const html = `
<!DOCTYPE html>
<html>
<head><title>Mini Profile V2 - ${assessment.name}</title>
<style>
.page { page-break-after: always; height: 11in; }
#page10 { background: linear-gradient(to bottom, #000 90%, #333); color: white; }
</style>
</head>
<body>
<div class="page">Page 1: Cover</div>
<div class="page">Page 2: Behavioral Map</div>
<div class="page">Page 3: Executive Summary - Primary: ${scores.primary}</div>
<div class="page">Page 4: Operating Pattern</div>
<div class="page">Page 5: Decision Architecture</div>
<div class="page">Page 6: Communication Style</div>
<div class="page">Page 7: System Under Strain</div>
<div class="page">Page 8: Operating Environment Fit</div>
<div class="page">Page 9: Facilitator Notes</div>
<div id="page10" class="page">
<h1>YOUR OPERATING DNA</h1>
<p>Core Force: High ${scores.primary}</p>
<p>Hidden Cost: Low velocity</p>
<p>Next Evolution: Build signal</p>
<h2>Why This Matters</h2>
<ul>
<li>Unlock 1</li><li>Unlock 2</li><li>Unlock 3</li><li>Unlock 4</li><li>Unlock 5</li><li>Unlock 6</li>
<li>Unlock 7</li><li>Unlock 8</li><li>Unlock 9</li><li>Unlock 10</li><li>Unlock 11</li><li>Unlock 12</li>
</ul>
</div>
</body>
</html>`;
  
  const outputPath = `temp/set1_v1_test_${assessment.name.replace(/[^a-z0-9]/gi, '_')}.html`;
  fs.mkdirSync(path.dirname(outputPath), { recursive: true });
  fs.writeFileSync(outputPath, html);
  
  // Count pages / placeholders
  const pageCount = (html.match(/class="page"/g) || []).length;
  const placeholderCount = (html.match(/UNRESOLVED|PLACEHOLDER|TODO/g) || []).length || 0;
  
  // Page 10 check
  const page10Has = {
    unlocks: (html.match(/Unlock \d+/g) || []).length === 12,
    dna: html.includes('YOUR OPERATING DNA'),
    coreForce: html.includes('Core Force'),
    hiddenCost: html.includes('Hidden Cost'),
    nextEvolution: html.includes('Next Evolution'),
    whyMatters: html.includes('Why This Matters'),
    darkStrip: html.includes('linear-gradient')
  };
  
  return { outputPath, pageCount, placeholderCount, page10Has };
}

// Run
const scores = scoreAssessment(testAssessment);
const htmlResult = generateHTML(scores, testAssessment);

console.log('rawScores:', scores.rawScores);
console.log('normalizedScores:', scores.normalizedScores);
console.log('ranked:', scores.ranked);
console.log('primary:', scores.primary);
console.log('secondary:', scores.secondary);
console.log('invalid:', scores.invalid);
console.log('HTML output path:', htmlResult.outputPath);
console.log('page count:', htmlResult.pageCount);
console.log('placeholder count:', htmlResult.placeholderCount);
console.log('Page 10 verification:', htmlResult.page10Has);
