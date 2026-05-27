#!/usr/bin/env node

/**
 * Test script: Verify profile-specific futures generation
 * Tests 3 profiles with dramatically different operating systems
 */

import { generateProfileSpecificFutures } from './moremindmap-live/api/engine/canonical/generateProfileSpecificFutures.js';

const testProfiles = [
  {
    name: 'David / Vector-Dominant (Command)',
    canonical: {
      top_systems: {
        primary_driver: {
          dimension: 'vector',
          operating_manifestation: 'Rapid directional leadership',
          pressure_manifestation: 'Doubles down on direction'
        },
        secondary_stabilizer: {
          dimension: 'framework',
          operating_manifestation: 'Structures clarity'
        }
      },
      vector_scores: { vector: 7.2, signal: 5.1, fidelity: 4.8, framework: 6.1 },
      contradictions: [{ type: 'speed_vs_depth', severity: 'mild' }],
      hidden_risk_patterns: { relational_erosion_risk: 'Low', burnout_trajectory: 'Low' },
      future_ceiling: { primary_constraint: null },
      stall_patterns: { triggers: [] },
      intake_answers: { Q1: 'I move fast', Q2: 'Speed is my edge', Q3: 'I decide quickly' }
    }
  },
  {
    name: 'Billybob / Fidelity-Stuck (Paralysis)',
    canonical: {
      top_systems: {
        primary_driver: {
          dimension: 'fidelity',
          operating_manifestation: 'Thorough detail analysis',
          pressure_manifestation: 'Intensifies perfectionism'
        },
        secondary_stabilizer: {
          dimension: 'signal',
          operating_manifestation: 'Reads emotional tone'
        }
      },
      vector_scores: { vector: 2.1, signal: 6.8, fidelity: 7.4, framework: 4.2 },
      contradictions: [
        { type: 'stuck', severity: 'high', tension: 'Knows what to do vs paralyzed' }
      ],
      hidden_risk_patterns: { relational_erosion_risk: 'Medium', burnout_trajectory: 'High' },
      future_ceiling: { primary_constraint: 'Analysis paralysis' },
      stall_patterns: { triggers: ['decision', 'ambiguity'] },
      intake_answers: { Q1: 'I\'m stuck', Q2: 'I froze', Q3: 'Operating out of fear', Q4: 'Paralyzed by options' }
    }
  },
  {
    name: 'Pamela / Signal-Precision (Chaos Management)',
    canonical: {
      top_systems: {
        primary_driver: {
          dimension: 'signal',
          operating_manifestation: 'Reads patterns under chaos',
          pressure_manifestation: 'Intensifies monitoring'
        },
        secondary_stabilizer: {
          dimension: 'fidelity',
          operating_manifestation: 'Applies precision structures'
        }
      },
      vector_scores: { vector: 5.2, signal: 7.1, fidelity: 6.9, framework: 5.4 },
      contradictions: [
        { type: 'precision_vs_chaos', severity: 'medium', tension: 'Seeks order in inherent chaos' }
      ],
      hidden_risk_patterns: { relational_erosion_risk: 'Low', burnout_trajectory: 'Medium' },
      future_ceiling: { primary_constraint: 'Structural support limits precision' },
      stall_patterns: { triggers: ['ambiguous_goals'] },
      intake_answers: { Q1: 'I bring order', Q2: 'Chaos is constant', Q3: 'I need precision' }
    }
  }
];

console.log('='.repeat(80));
console.log('FUTURES ENGINE TEST: Profile-Specific Trajectory Simulations');
console.log('='.repeat(80));
console.log('');

testProfiles.forEach((profile, idx) => {
  console.log(`\n[${ idx + 1 }] ${profile.name}`);
  console.log('-'.repeat(80));
  
  const futures = generateProfileSpecificFutures(profile.canonical);
  
  futures.forEach((future, fidx) => {
    console.log(`\n  Future ${fidx + 1}: ${future.title}`);
    console.log(`  Likelihood: ${future.likelihood}`);
    console.log(`  Description: ${future.description.substring(0, 100)}${future.description.length > 100 ? '...' : ''}`);
  });
  
  // Extract titles for comparison
  console.log(`\n  TITLES: ${futures.map(f => `"${f.title}"`).join(', ')}`);
});

console.log('\n' + '='.repeat(80));
console.log('VALIDATION CHECKS');
console.log('='.repeat(80));

// Check 1: No generic titles repeated
const allTitles = testProfiles.flatMap(p => generateProfileSpecificFutures(p.canonical).map(f => f.title));
const uniqueTitles = new Set(allTitles);
console.log(`\n✓ Unique titles across profiles: ${uniqueTitles.size} / ${allTitles.length}`);
if (uniqueTitles.size === allTitles.length) {
  console.log('  ✅ PASS: No repeated futures across profiles');
} else {
  console.log('  ⚠️  WARNING: Some futures repeated across profiles');
}

// Check 2: No "Scaled Success" or generic titles
const genericTitles = ['Scaled Success', 'Optimized Specialty', 'Increasing Friction', 'Infrastructure Crisis', 'Successful Transition'];
const foundGeneric = allTitles.filter(t => genericTitles.includes(t));
if (foundGeneric.length === 0) {
  console.log(`✓ No generic static futures found`);
  console.log('  ✅ PASS: All futures are profile-specific');
} else {
  console.log(`⚠️  Found ${foundGeneric.length} generic futures: ${foundGeneric.join(', ')}`);
}

// Check 3: Futures mention specific operating patterns
console.log(`\n✓ Profile specificity check:`);
testProfiles.forEach((profile, idx) => {
  const futures = generateProfileSpecificFutures(profile.canonical);
  const primary_dim = profile.canonical.top_systems.primary_driver.dimension;
  const mentioned = futures.filter(f => 
    f.description.includes(primary_dim) || 
    f.description.includes(profile.canonical.top_systems.primary_driver.operating_manifestation?.substring(0, 20))
  ).length;
  console.log(`  Profile ${idx + 1} (${primary_dim}): ${mentioned}/${futures.length} mention operating pattern`);
});

console.log('\n' + '='.repeat(80));
console.log('TEST COMPLETE');
console.log('='.repeat(80));
