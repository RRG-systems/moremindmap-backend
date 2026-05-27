#!/usr/bin/env node

/**
 * DIAGNOSTIC: Billybob Fake vs David Berg Cache Leak
 * 
 * Purpose: Retrieve both profiles, compare canonical structures
 * Goal: Identify if Billybob got David Berg's data or fallback/stale data
 */

const fs = require('fs');
const path = require('path');

// Import vault accessor (assuming Redis connection available)
const { retrieveFromVault } = require('./api/engine/vault/vaultManager');

async function diagnoseBillybobBug() {
  console.log('='.repeat(80));
  console.log('DIAGNOSTIC: Billybob Fake vs David Berg Cache Leak');
  console.log('='.repeat(80));
  console.log();

  const billybobId = 'mm-20260526-d8k0lw33'; // Billybob Fake
  const davidId = 'MM-20260523-mqlev9c9';    // David Berg

  try {
    // 1. RETRIEVE BOTH PROFILES
    console.log(`[1/6] Retrieving Billybob profile: ${billybobId}`);
    const billybobProfile = await retrieveFromVault(billybobId);
    if (!billybobProfile) {
      console.error(`❌ Billybob profile NOT FOUND in vault: ${billybobId}`);
      return;
    }
    console.log('✅ Billybob profile retrieved');
    console.log();

    console.log(`[2/6] Retrieving David Berg profile: ${davidId}`);
    const davidProfile = await retrieveFromVault(davidId);
    if (!davidProfile) {
      console.error(`❌ David Berg profile NOT FOUND in vault: ${davidId}`);
      return;
    }
    console.log('✅ David Berg profile retrieved');
    console.log();

    // 2. COMPARE CRITICAL FIELDS
    console.log('[3/6] COMPARING CRITICAL FIELDS');
    console.log('-'.repeat(80));

    const comparisonFields = [
      'profile_id',
      ['vector_scores', 'vector'],
      ['vector_scores', 'signal'],
      ['vector_scores', 'fidelity'],
      ['vector_scores', 'velocity'],
      ['top_systems', 'primary_driver', 'dimension'],
      ['top_systems', 'primary_driver', 'operating_manifestation'],
      ['top_systems', 'secondary_stabilizer', 'dimension'],
      'metadata'
    ];

    console.log('\nFIELD COMPARISON:');
    console.log(`{"field": "value_billybob", "value_david", "match"}`);

    let fieldMatches = 0;
    let fieldMismatches = 0;

    comparisonFields.forEach(field => {
      let billybobVal, davidVal;

      if (Array.isArray(field)) {
        billybobVal = field.reduce((obj, key) => obj?.[key], billybobProfile);
        davidVal = field.reduce((obj, key) => obj?.[key], davidProfile);
        field = field.join('.');
      } else {
        billybobVal = billybobProfile[field];
        davidVal = davidProfile[field];
      }

      const match = JSON.stringify(billybobVal) === JSON.stringify(davidVal);
      const status = match ? '❌ MATCH' : '✅ DIFF';

      console.log(`  ${field}: "${billybobVal}" vs "${davidVal}" ${status}`);

      if (match) {
        fieldMatches++;
      } else {
        fieldMismatches++;
      }
    });

    console.log();
    console.log(`FIELD MATCH SUMMARY: ${fieldMatches} matches, ${fieldMismatches} differences`);
    console.log();

    // 3. CHECK FOR CACHE-LEAK INDICATORS
    console.log('[4/6] CHECKING CACHE-LEAK INDICATORS');
    console.log('-'.repeat(80));

    // 3a. Check if Billybob got David's profile_id
    if (billybobProfile.profile_id === davidProfile.profile_id) {
      console.log('🚨 CACHE LEAK #1: Billybob has David\'s profile_id!');
      console.log(`   Billybob ID: ${billybobProfile.profile_id}`);
      console.log(`   David ID: ${davidProfile.profile_id}`);
    } else {
      console.log('✅ Profile IDs are different (not copied)');
    }
    console.log();

    // 3b. Check if all scores identical
    const billybobScores = billybobProfile.vector_scores;
    const davidScores = davidProfile.vector_scores;
    const allScoresMatch = Object.keys(billybobScores).every(
      key => billybobScores[key] === davidScores[key]
    );
    if (allScoresMatch) {
      console.log('🚨 CACHE LEAK #2: Billybob has IDENTICAL scores to David!');
      console.log(`   Scores: ${JSON.stringify(billybobScores)}`);
    } else {
      console.log('✅ Scores are different (not copied)');
    }
    console.log();

    // 3c. Check if primary/secondary dimensions identical
    const billybobPrimary = billybobProfile.top_systems.primary_driver.dimension;
    const davidPrimary = davidProfile.top_systems.primary_driver.dimension;
    if (billybobPrimary === davidPrimary) {
      console.log('🚨 CACHE LEAK #3: Billybob has SAME primary dimension as David!');
      console.log(`   Billybob primary: ${billybobPrimary}`);
      console.log(`   David primary: ${davidPrimary}`);
    } else {
      console.log('✅ Primary dimensions are different (not copied)');
    }
    console.log();

    // 3d. Check narrative sections for exact copy
    const billybobDNA = billybobProfile.narrative_profile?.profileDNA?.body;
    const davidDNA = davidProfile.narrative_profile?.profileDNA?.body;
    if (billybobDNA === davidDNA) {
      console.log('🚨 CACHE LEAK #4: Billybob has SAME profileDNA narrative as David!');
      console.log(`   Narrative: "${billybobDNA?.substring(0, 100)}..."`);
    } else if (billybobDNA && davidDNA) {
      const similarity = calculateSimilarity(billybobDNA, davidDNA);
      console.log(`✅ Narratives are different (similarity: ${(similarity * 100).toFixed(1)}%)`);
      if (similarity > 0.8) {
        console.log('   ⚠️ WARNING: High similarity detected (>80%), possible partial reuse');
      }
    }
    console.log();

    // 4. TRACE CANONICAL GENERATION
    console.log('[5/6] CANONICAL GENERATION METADATA');
    console.log('-'.repeat(80));
    console.log('\nBILLYBOB METADATA:');
    console.log(JSON.stringify(billybobProfile.metadata, null, 2).substring(0, 500));
    console.log('\nDAVID METADATA:');
    console.log(JSON.stringify(davidProfile.metadata, null, 2).substring(0, 500));
    console.log();

    // 5. DEEP DIVE: Check for default/fallback indicators
    console.log('[6/6] DEFAULT/FALLBACK DETECTION');
    console.log('-'.repeat(80));

    const checkDefaultIndicators = (profile, name) => {
      const indicators = [];

      // Check if all scores are 2.5 (neutral default)
      if (Object.values(profile.vector_scores).every(v => v === 2.5)) {
        indicators.push('🚨 All scores are 2.5 (neutral default fallback)');
      }

      // Check if profileInput exists and is populated
      if (!profile.profileInput) {
        indicators.push('⚠️ No profileInput in profile (generation may be incomplete)');
      } else if (!profile.profileInput.dimension_scores) {
        indicators.push('⚠️ profileInput.dimension_scores missing (scoring data not preserved)');
      }

      // Check if narrative sections are placeholders
      if (profile.narrative_profile?.profileDNA?.body === 'Emergency inline') {
        indicators.push('🚨 profileDNA is placeholder text (generation incomplete)');
      }

      // Check if metadata generation_mode is 'fallback'
      if (profile.metadata?.generation_mode === 'fallback') {
        indicators.push('⚠️ Profile was generated in fallback mode');
      }

      if (indicators.length === 0) {
        indicators.push('✅ No default/fallback indicators detected');
      }

      console.log(`\n${name}:`);
      indicators.forEach(i => console.log(`  ${i}`));
    };

    checkDefaultIndicators(billybobProfile, 'BILLYBOB');
    checkDefaultIndicators(davidProfile, 'DAVID BERG');
    console.log();

    // SUMMARY
    console.log('='.repeat(80));
    console.log('DIAGNOSTIC SUMMARY');
    console.log('='.repeat(80));
    console.log();

    const issues = [];
    if (billybobProfile.profile_id === davidProfile.profile_id) {
      issues.push('❌ CRITICAL: Billybob has David\'s profile_id');
    }
    if (allScoresMatch) {
      issues.push('❌ CRITICAL: Billybob has identical scores to David');
    }
    if (billybobPrimary === davidPrimary) {
      issues.push('❌ CRITICAL: Billybob has same primary dimension as David');
    }
    if (billybobDNA === davidDNA) {
      issues.push('❌ CRITICAL: Billybob has same narrative as David');
    }

    if (issues.length === 0) {
      console.log('✅ NO CRITICAL CACHE LEAKS DETECTED');
      console.log();
      console.log('NEXT STEPS:');
      console.log('1. Check if Billybob profile ID is correct (mm-20260526-d8k0lw33)');
      console.log('2. Review the submitted assessment answers for Billybob');
      console.log('3. Trace through buildProfileInput → executeCanonicalGeneration');
      console.log('4. Compare Billybob\'s profileInput.dimension_scores to rendered vector_scores');
      console.log('5. Check localStorage/sessionStorage for cache pollution');
    } else {
      console.log('ISSUES FOUND:');
      issues.forEach(issue => console.log(`  ${issue}`));
      console.log();
      console.log('ROOT CAUSE POSSIBILITIES:');
      console.log('1. Cache key using static key instead of profileId');
      console.log('2. profileId null/undefined during canonical generation');
      console.log('3. localStorage/sessionStorage reuse between profiles');
      console.log('4. Default profile template returned instead of real data');
      console.log('5. Vault save using wrong key (David\'s key instead of Billybob\'s)');
    }

    console.log();
    console.log('='.repeat(80));

  } catch (err) {
    console.error('ERROR:', err.message);
    console.error(err.stack);
  }
}

// Helper: Calculate string similarity (Levenshtein-inspired)
function calculateSimilarity(str1, str2) {
  const longer = str1.length > str2.length ? str1 : str2;
  const shorter = str1.length > str2.length ? str2 : str1;

  if (longer.length === 0) return 1.0;

  const editDistance = getEditDistance(longer, shorter);
  return (longer.length - editDistance) / longer.length;
}

function getEditDistance(s1, s2) {
  const costs = [];
  for (let i = 0; i <= s1.length; i++) {
    let lastValue = i;
    for (let j = 0; j <= s2.length; j++) {
      if (i === 0) {
        costs[j] = j;
      } else if (j > 0) {
        let newValue = costs[j - 1];
        if (s1.charAt(i - 1) !== s2.charAt(j - 1)) {
          newValue = Math.min(Math.min(newValue, lastValue), costs[j]) + 1;
        }
        costs[j - 1] = lastValue;
        lastValue = newValue;
      }
    }
    if (i > 0) costs[s2.length] = lastValue;
  }
  return costs[s2.length];
}

// Run
diagnoseBillybobBug();
