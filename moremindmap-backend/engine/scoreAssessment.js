// moremindmap-backend/engine/scoreAssessment.js
// Recreated May 11, 2026

import { QUESTION_MAP } from './questionMap.js';
import { DIMENSIONS } from './dimensionMap.js';

// Mock functions for now, assume these are filled on real data
const getRawScores = (answers) => {
  // Placeholder: In reality, this would process answers against questionMap
  // For now, return mock scores based on answer count for simplicity
  const rawScores = {};
  DIMENSIONS.forEach(dim => rawScores[dim] = answers.length * Math.random()); // Mock scores
  return rawScores;
};

const normalizeScores = (rawScores) => {
  const normalized = {};
  for (const dim in rawScores) {
    normalized[dim] = Math.max(0, Math.min(100, rawScores[dim] / rawScores.length * 100)); // Mock normalization
  }
  return normalized;
};

const rankDimensions = (normalizedScores) => {
  // Mock ranking: sort dimensions by score descending
  const sorted = Object.entries(normalizedScores).sort(([,a],[,b]) => b-a);
  const ranked = sorted.map(([dim]) => dim);

  const primary = ranked[0] || null;
  const secondary = ranked[1] || null;
  const suppressed = ranked.slice(2).filter(dim => normalizedScores[dim] < 50); // Example suppression
  const invalid = null; // Placeholder for invalid scores

  return { ranked, primary, secondary, suppressed, invalid };
};

const getHeadline = (ranked) => {
  if (!ranked || ranked.length === 0) return "Profile Analysis";
  return `Profile: ${ranked.join('/')}`; // Simple headline
};

export const scoreAnswers = (answers) => {
  const rawScores = getRawScores(answers);
  const normalizedScores = normalizeScores(rawScores);
  const { ranked, primary, secondary, suppressed, invalid } = rankDimensions(normalizedScores);
  const headline = getHeadline(ranked);

  const writtenResponses = answers.filter(a => a.type === 'written').map(a => ({
    id: a.id,
    response: a.response // Store the actual response
  }));

  return {
    rawScores,
    normalizedScores,
    ranked,
    primary,
    secondary,
    suppressed,
    invalid,
    headline,
    writtenResponses
  };
};
