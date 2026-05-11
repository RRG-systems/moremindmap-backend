// simRunner.js - Fake profile simulations for validation
// Run: node engine/simRunner.js

import { QUESTION_MAP, VALIDATION } from './questionMap.js';
import { DIMENSIONS } from './dimensionMap.js';

function scoreResponse(answers) {
  const rawScores = {};
  DIMENSIONS.forEach(d => rawScores[d] = 0);

  QUESTION_MAP.set_1.v1.forEach((q, idx) => {
    if (q.type === 'mc' && answers[idx]) {
      const option = answers[idx];
      if (q.scores && q.scores[option]) {
        Object.entries(q.scores[option]).forEach(([dim, weight]) => {
          if (DIMENSIONS.includes(dim)) rawScores[dim] += weight;
        });
      }
    }
  });

  // Normalize (0-1 scale, assuming max ~30 per dim)
  const normalized = {};
  const maxScore = 30;
  DIMENSIONS.forEach(d => normalized[d] = Math.max(0, rawScores[d] / maxScore));

  // Ranked
  const ranked = Object.entries(normalized)
    .sort((a, b) => b[1] - a[1])
    .map(([d]) => d);

  const primary = ranked[0];
  const secondary = ranked[1];

  const invalid = Object.values(rawScores).every(s => s === 0);

  return { rawScores, normalized, ranked, primary, secondary, invalid };
}

// Sims
const SIMS = [
  {
    name: 'Founder Operator',
    answers: ['A','A','A','B','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A']  // Bias vector/velocity
  },
  // 4 more...
];

SIMS.forEach(sim => {
  const result = scoreResponse(sim.answers);
  console.log(`\\n=== ${sim.name} ===`);
  console.log('Raw:', result.rawScores);
  console.log('Norm:', result.normalized);
  console.log('Ranked:', result.ranked);
  console.log('Primary:', result.primary, 'Secondary:', result.secondary);
  console.log('Invalid:', result.invalid);
});
