// simRunner.v2.js - JSON output, 10 personas, clean
// node simRunner.v2.js

import { QUESTION_MAP } from './questionMap.js';
import { DIMENSIONS } from './dimensionMap.js';

function scoreResponse(answers) {
  const rawScores = {};
  DIMENSIONS.forEach(d => rawScores[d] = 0);

  QUESTION_MAP.set_1.v1.forEach((q, idx) => {
    if (q.type === 'mc' && answers[idx]) {
      const option = answers[idx];
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
  const secondary = ranked[1];
  const invalid = Object.values(rawScores).every(s => s === 0);

  return { rawScores, normalizedScores, ranked, primary, secondary, invalid };
}

const SIMS = [
  // 1. Founder Operator
  {
    persona: 'Founder Operator',
    answers: Array(24).fill('A'),  // Aggressive/action bias
    expected: 'high vector/velocity/leverage, low signal/flex'
  },
  {
    persona: 'Diplomat Leader',
    answers: ['B','B','B','A','C','B','C','B','C','B','C','D','B','C','B','B','C','D','B','B','B','B','C','B'],  // Relational/flex
    expected: 'high signal/leverage/flex, mod horizon/framework'
  },
  {
    persona: 'Rigid Executor',
    answers: ['B','C','C','D','B','D','A','D','D','C','D','C','B','D','D','D','A','D','A','C','C','D','B','C'],  // Precision/structure
    expected: 'high fidelity/framework/vector, low flex/signal'
  },
  {
    persona: 'Reactive Firefighter',
    answers: ['A','D','A','C','A','A','B','A','A','D','A','A','A','B','A','A','E','A','B','D','A','A','A','D'],  // Speed/action
    expected: 'high velocity/vector, low horizon/framework/fidelity'
  },
  {
    persona: 'Detached Strategist',
    answers: ['E','B','E','E','E','E','E','D','B','E','E','E','D','D','E','D','D','E','D','B','E','E','E','E'],  // Long-view/precise
    expected: 'high horizon/fidelity/framework, low velocity/signal'
  },
  {
    persona: 'Charismatic Improviser',
    answers: ['D','C','B','C','D','C','B','C','E','D','E','B','C','E','D','E','D','C','E','C','B','C','E','D'],  // Leverage/speed/adapt
    expected: 'high leverage/velocity/flex, mod signal, low fidelity/framework'
  },
  {
    persona: 'Anxious Planner',
    answers: ['B','A','C','D','B','D','A','E','D','C','D','C','B','D','D','D','A','D','A','A','C','D','B','A'],  // Structure/precise
    expected: 'high framework/fidelity, mod signal, low velocity/flex/vector'
  },
  {
    persona: 'Consensus Builder',
    answers: ['B','A','B','A','C','B','C','B','C','B','C','D','B','C','B','B','C','D','B','A','B','B','C','B'],  // Relational/influence/adapt
    expected: 'high signal/leverage/flex, low vector, mod framework/horizon'
  },
  {
    persona: 'Detached Analyst',
    answers: ['B','B','C','D','B','D','A','D','D','C','D','C','B','D','D','D','A','D','A','B','C','D','B','C'],  // Precise/long-view
    expected: 'high fidelity/horizon, mod framework, low signal/leverage/velocity'
  },
  {
    persona: 'Burned-Out High Performer',
    answers: ['A','A','A','B','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A','A'],  // High past vector/velocity but friction
    expected: 'high vector/fidelity/velocity, low flex/signal/horizon'
  }
];

const results = SIMS.map(sim => ({
  persona: sim.persona,
  ...scoreResponse(sim.answers),
  interpretation: getInterpretation(scoreResponse(sim.answers)),  // Placeholder
  feelsRight: 'YES',  // Manual for now
  distortion: 'None'
}));

console.log(JSON.stringify(results, null, 2));
