#!/usr/bin/env python3
"""
PHASE 22 - Market Lifecycle Detection System
============================================

Build system to classify markets by lifecycle stage.
Detect which markets are worth trading BEFORE applying strategy.
WHERE to trade before HOW to trade.

System:
1. Feature extraction (spread, volume, age, liquidity, volatility)
2. Rule-based classification (EMERGING / MID / MATURE)
3. Viability backtest by stage
4. Answers 4 key questions about lifecycle edge
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
from collections import defaultdict
import sys

# Data source: Variant A trades and snapshots
DATA_PATH = Path("/Users/rrg/polymarket_bot_variant_a")
TRADES_CSV = DATA_PATH / "trades_log.csv"


def load_and_prepare_data():
    """Load trade data which contains market info."""
    print("[LOAD] Reading trade data...")
    
    # Read with error handling for inconsistent columns
    trades_df = pd.read_csv(TRADES_CSV, on_bad_lines='skip', engine='python')
    
    # Convert timestamps safely
    def safe_datetime(col):
        return pd.to_datetime(col, errors='coerce', utc=True)
    
    trades_df['timestamp'] = safe_datetime(trades_df['timestamp'])
    
    # Drop rows with invalid timestamps
    trades_df = trades_df.dropna(subset=['timestamp'])
    
    print(f"  Loaded: {len(trades_df)} trades")
    print(f"  Markets: {trades_df['question'].nunique()} unique questions")
    print(f"  Time range: {trades_df['timestamp'].min()} to {trades_df['timestamp'].max()}")
    
    return trades_df


def extract_market_features(trades_df):
    """
    Extract features for each market from trade data:
    - Spread width (current, avg)
    - Trade frequency
    - Volume (total, 24h equivalent)
    - Age (days)
    - Price levels (bid/ask)
    - Price stability
    """
    print("\n[FEATURES] Extracting market features...")
    
    market_features = {}
    
    # Get time range
    min_time = trades_df['timestamp'].min()
    max_time = trades_df['timestamp'].max()
    total_days = (max_time - min_time).days + 1
    
    # Group by market (question)
    for question in trades_df['question'].unique():
        if not isinstance(question, str):
            continue
        
        market_trades = trades_df[trades_df['question'] == question].copy()
        market_trades = market_trades.sort_values('timestamp')
        
        if len(market_trades) < 2:
            continue
        
        # Timing features
        first_time = market_trades['timestamp'].min()
        last_time = market_trades['timestamp'].max()
        market_age_hours = (last_time - first_time).total_seconds() / 3600
        market_age_days = market_age_hours / 24
        
        # Spread features (convert to basis points)
        spreads = pd.to_numeric(market_trades['spread'], errors='coerce').dropna().values
        if len(spreads) > 0:
            current_spread = spreads[-1]
            avg_spread = spreads.mean()
            spread_volatility = spreads.std() if len(spreads) > 1 else 0
        else:
            current_spread = avg_spread = spread_volatility = 0
        
        # Volume features
        volumes = pd.to_numeric(market_trades['volume_24h'], errors='coerce').dropna().values
        if len(volumes) > 0:
            avg_volume_24h = volumes.mean()
            current_volume_24h = volumes[-1]
        else:
            avg_volume_24h = current_volume_24h = 0
        
        # Trade frequency (trades per hour)
        trade_count = len(market_trades)
        trade_frequency = trade_count / max(market_age_hours, 0.1)
        
        # Liquidity proxy from 'liquidity' column if available
        liquidity = pd.to_numeric(market_trades['liquidity'], errors='coerce').dropna().values
        current_liquidity = liquidity[-1] if len(liquidity) > 0 else 0
        
        # Bid/ask spread in basis points
        spread_bps_vals = spreads * 10000
        
        # Confidence signal distribution
        confidence_counts = market_trades['confidence'].value_counts()
        high_confidence_pct = 100 * confidence_counts.get('HIGH', 0) / len(market_trades) if len(market_trades) > 0 else 0
        
        # Activity trend (activity_score from trades)
        activity = pd.to_numeric(market_trades['activity_score'], errors='coerce').dropna().values
        avg_activity = activity.mean() if len(activity) > 0 else 0
        
        market_features[question] = {
            'age_days': market_age_days,
            'age_hours': market_age_hours,
            'current_spread_bps': current_spread * 10000 if current_spread > 0 else 0,
            'avg_spread_bps': avg_spread * 10000 if avg_spread > 0 else 0,
            'spread_volatility': spread_volatility,
            'current_volume_24h': current_volume_24h,
            'avg_volume_24h': avg_volume_24h,
            'trade_frequency': trade_frequency,
            'trade_count': trade_count,
            'current_liquidity': current_liquidity,
            'high_confidence_pct': high_confidence_pct,
            'avg_activity': avg_activity,
            'min_timestamp': first_time,
            'max_timestamp': last_time,
        }
    
    print(f"  Extracted features for {len(market_features)} markets")
    return market_features


def classify_lifecycle(market_features):
    """
    Classify each market into lifecycle stage using rule-based logic.
    
    EMERGING:
    - Spread > 200 bps OR high spread
    - Trade frequency < 10 trades/hour (low activity)
    - Age < 7 days (young market)
    - Volume low (bottom quartile)
    
    MID:
    - Spread 50-200 bps (moderate)
    - Trade frequency 10-50 trades/hour
    - Age 7-30 days (maturing)
    - Volume moderate (middle quartiles)
    
    MATURE:
    - Spread < 50 bps (tight)
    - Trade frequency > 50 trades/hour
    - Age > 30 days (established)
    - Volume high (top quartile)
    """
    print("\n[CLASSIFY] Running rule-based lifecycle classification...")
    
    # Calculate quartiles for volume
    volumes = [f['avg_volume_24h'] for f in market_features.values()]
    vol_q1 = np.percentile(volumes, 25) if volumes else 0
    vol_q3 = np.percentile(volumes, 75) if volumes else 0
    
    # Calculate quartiles for spreads
    spreads = [f['avg_spread_bps'] for f in market_features.values()]
    spread_q3 = np.percentile(spreads, 75) if spreads else 100
    
    classifications = {}
    stage_distribution = defaultdict(int)
    
    for question, features in market_features.items():
        spread = features['avg_spread_bps']
        trade_freq = features['trade_frequency']
        age = features['age_days']
        volume = features['avg_volume_24h']
        confidence = features['high_confidence_pct']
        
        # Rule-based classification with scoring
        emerging_score = 0
        mature_score = 0
        mid_score = 0
        
        # Age signals
        if age < 7:
            emerging_score += 3
        elif age > 30:
            mature_score += 3
        elif 7 <= age <= 30:
            mid_score += 3
        
        # Spread signals
        if spread > 200:
            emerging_score += 3
        elif spread < 50:
            mature_score += 3
        elif 50 <= spread <= 200:
            mid_score += 2
        
        # Trade frequency signals
        if trade_freq < 10:
            emerging_score += 2
        elif trade_freq > 50:
            mature_score += 2
        elif 10 <= trade_freq <= 50:
            mid_score += 2
        
        # Volume signals
        if volume <= vol_q1:
            emerging_score += 2
        elif volume >= vol_q3:
            mature_score += 2
        else:
            mid_score += 2
        
        # Confidence signal (emerging markets may have more uncertainty)
        if confidence < 30:
            emerging_score += 1
        elif confidence > 70:
            mature_score += 1
        
        # Decide stage
        scores = {'EMERGING': emerging_score, 'MID': mid_score, 'MATURE': mature_score}
        stage = max(scores, key=scores.get)
        
        classifications[question] = {
            'stage': stage,
            'features': features,
            'scores': scores,
        }
        stage_distribution[stage] += 1
    
    for stage in ['EMERGING', 'MID', 'MATURE']:
        count = stage_distribution[stage]
        pct = 100 * count / len(classifications) if classifications else 0
        print(f"  {stage}: {count} markets ({pct:.1f}%)")
    
    return classifications


def test_viability_by_stage(trades_df, classifications):
    """
    Test viability of each stage:
    - Win rate (% of profitable outcomes)
    - Average spread capture
    - Consistency metrics
    - Compute viability score (0-100) per market
    """
    print("\n[VIABILITY] Testing stage-by-stage trading viability...")
    
    stage_viability = {
        'EMERGING': [],
        'MID': [],
        'MATURE': [],
    }
    
    # For each market with trades, compute viability score
    for question, classification in classifications.items():
        market_trades = trades_df[trades_df['question'] == question]
        if len(market_trades) == 0:
            continue
        
        stage = classification['stage']
        features = classification['features']
        
        # Calculate per-trade viability
        viability_scores = []
        win_count = 0
        loss_count = 0
        flat_count = 0
        
        for idx, trade in market_trades.iterrows():
            score = 50  # baseline
            
            # Spread capture potential
            spread_bps = pd.to_numeric(trade.get('spread', 0), errors='coerce') * 10000
            if spread_bps > 200:
                score += 15
            elif spread_bps > 100:
                score += 10
            elif spread_bps < 50:
                score -= 5
            
            # Outcome signals
            outcome = trade.get('outcome', 'FLAT')
            if outcome == 'WIN':
                score += 25
                win_count += 1
            elif outcome == 'LOSS':
                score -= 20
                loss_count += 1
            else:
                score += 5
                flat_count += 1
            
            # Confidence boost
            confidence = trade.get('confidence', 'MEDIUM')
            if confidence == 'HIGH':
                score += 8
            elif confidence == 'LOW':
                score -= 5
            
            # Volume/liquidity (easier execution in mature)
            volume_24h = pd.to_numeric(trade.get('volume_24h', 0), errors='coerce')
            if volume_24h > 100000:
                score += 8
            elif volume_24h < 10000:
                score -= 3
            
            score = max(0, min(100, score))
            viability_scores.append(score)
        
        # Aggregate
        avg_viability = np.mean(viability_scores) if viability_scores else 50
        win_rate = 100 * win_count / len(market_trades) if len(market_trades) > 0 else 0
        
        stage_viability[stage].append({
            'question': question,
            'viability_score': avg_viability,
            'win_rate': win_rate,
            'trade_count': len(market_trades),
            'win_count': win_count,
            'loss_count': loss_count,
            'flat_count': flat_count,
            'avg_spread_bps': features['avg_spread_bps'],
            'volume_24h': features['avg_volume_24h'],
            'age_days': features['age_days'],
        })
    
    # Compute stage statistics
    stage_stats = {}
    for stage in ['EMERGING', 'MID', 'MATURE']:
        trades_list = stage_viability[stage]
        if trades_list:
            viability_scores = [t['viability_score'] for t in trades_list]
            win_rates = [t['win_rate'] for t in trades_list]
            
            stage_stats[stage] = {
                'count': len(trades_list),
                'avg_viability_score': np.mean(viability_scores),
                'std_viability_score': np.std(viability_scores),
                'avg_win_rate': np.mean(win_rates),
                'total_trades': sum(t['trade_count'] for t in trades_list),
                'total_wins': sum(t['win_count'] for t in trades_list),
                'avg_spread_bps': np.mean([t['avg_spread_bps'] for t in trades_list]),
                'avg_volume_24h': np.mean([t['volume_24h'] for t in trades_list]),
            }
    
    return stage_viability, stage_stats


def answer_key_questions(classifications, trades_df, stage_viability, stage_stats):
    """Answer the 4 key questions about lifecycle edge."""
    print("\n[QUESTIONS] Answering 4 key questions...")
    
    total_markets = len(classifications)
    emerging_count = sum(1 for c in classifications.values() if c['stage'] == 'EMERGING')
    mid_count = sum(1 for c in classifications.values() if c['stage'] == 'MID')
    mature_count = sum(1 for c in classifications.values() if c['stage'] == 'MATURE')
    
    # Q1: Detection accuracy
    print("\n  Q1: Can we reliably detect emerging markets early?")
    emerging_pct = 100 * emerging_count / total_markets if total_markets > 0 else 0
    print(f"    - {emerging_count}/{total_markets} markets classified as EMERGING ({emerging_pct:.1f}%)")
    print(f"    - EMERGING criteria: high spread, low frequency, young age, low volume")
    
    # False positive check: emerging markets with tight spreads
    false_positives = sum(1 for c in classifications.values() 
                         if c['stage'] == 'EMERGING' and c['features']['avg_spread_bps'] < 50)
    fp_rate = 100 * false_positives / emerging_count if emerging_count > 0 else 0
    print(f"    - False positive rate (tight spread but EMERGING): {fp_rate:.1f}%")
    print(f"    - Detection reliability: GOOD" if fp_rate < 20 else "    - Detection reliability: POOR")
    
    # Q2: Lifecycle duration
    print("\n  Q2: How long do inefficiencies persist?")
    avg_ages = {
        'EMERGING': np.mean([c['features']['age_days'] for c in classifications.values() if c['stage'] == 'EMERGING']) if emerging_count > 0 else 0,
        'MID': np.mean([c['features']['age_days'] for c in classifications.values() if c['stage'] == 'MID']) if mid_count > 0 else 0,
        'MATURE': np.mean([c['features']['age_days'] for c in classifications.values() if c['stage'] == 'MATURE']) if mature_count > 0 else 0,
    }
    print(f"    - Average age EMERGING: {avg_ages['EMERGING']:.2f} days")
    print(f"    - Average age MID: {avg_ages['MID']:.2f} days")
    print(f"    - Average age MATURE: {avg_ages['MATURE']:.2f} days")
    
    # Spread compression
    avg_spreads = {
        'EMERGING': np.mean([c['features']['avg_spread_bps'] for c in classifications.values() if c['stage'] == 'EMERGING']) if emerging_count > 0 else 0,
        'MID': np.mean([c['features']['avg_spread_bps'] for c in classifications.values() if c['stage'] == 'MID']) if mid_count > 0 else 0,
        'MATURE': np.mean([c['features']['avg_spread_bps'] for c in classifications.values() if c['stage'] == 'MATURE']) if mature_count > 0 else 0,
    }
    print(f"    - Average spread EMERGING: {avg_spreads['EMERGING']:.1f} bps")
    print(f"    - Average spread MID: {avg_spreads['MID']:.1f} bps")
    print(f"    - Average spread MATURE: {avg_spreads['MATURE']:.1f} bps")
    
    # Q3: Opportunity set
    print("\n  Q3: What % of markets are tradable at any given time?")
    tradable_pct = 100 * (emerging_count + mid_count) / total_markets if total_markets > 0 else 0
    print(f"    - Tradable (EMERGING + MID): {emerging_count + mid_count}/{total_markets} ({tradable_pct:.1f}%)")
    print(f"    - EMERGING: {emerging_count} ({100*emerging_count/total_markets:.1f}%)")
    print(f"    - MID: {mid_count} ({100*mid_count/total_markets:.1f}%)")
    print(f"    - MATURE (limited opportunity): {mature_count} ({100*mature_count/total_markets:.1f}%)")
    
    # Q4: System value
    print("\n  Q4: Does lifecycle detection outperform blind trading?")
    
    for stage in ['EMERGING', 'MID', 'MATURE']:
        if stage in stage_stats and stage_stats[stage]['count'] > 0:
            stats = stage_stats[stage]
            print(f"\n    {stage} Stage:")
            print(f"      - Markets: {stats['count']}")
            print(f"      - Total trades: {stats['total_trades']}")
            print(f"      - Viability score: {stats['avg_viability_score']:.1f}/100")
            print(f"      - Win rate: {stats['avg_win_rate']:.1f}%")
            print(f"      - Avg spread: {stats['avg_spread_bps']:.0f} bps")
            print(f"      - Avg volume: {stats['avg_volume_24h']:.0f}")
    
    return {
        'q1_detection_accuracy': {
            'emerging_pct': emerging_pct,
            'false_positive_rate': fp_rate,
        },
        'q2_lifecycle_duration': {
            'avg_age_emerging_days': avg_ages['EMERGING'],
            'avg_age_mid_days': avg_ages['MID'],
            'avg_age_mature_days': avg_ages['MATURE'],
            'avg_spread_emerging': avg_spreads['EMERGING'],
            'avg_spread_mid': avg_spreads['MID'],
            'avg_spread_mature': avg_spreads['MATURE'],
        },
        'q3_opportunity_set': {
            'total_markets': total_markets,
            'emerging_count': emerging_count,
            'mid_count': mid_count,
            'mature_count': mature_count,
            'tradable_pct': tradable_pct,
        },
        'q4_system_value': stage_stats,
    }


def generate_output_table(classifications, stage_viability):
    """Generate results table."""
    print("\n[OUTPUT] Generating results table...")
    
    results = []
    for question, classification in sorted(classifications.items()):
        features = classification['features']
        stage = classification['stage']
        
        # Find viability for this market
        viability_trades = [s for s in stage_viability.get(stage, []) 
                           if s.get('question') == question]
        viability_score = viability_trades[0]['viability_score'] if viability_trades else 0
        
        # Recommendation
        if viability_score >= 70:
            rec = "STRONG BUY"
        elif viability_score >= 60:
            rec = "BUY"
        elif viability_score >= 50:
            rec = "WATCH"
        else:
            rec = "SKIP"
        
        results.append({
            'Market': question[:45],
            'Stage': stage,
            'Spread (bps)': f"{features['avg_spread_bps']:.0f}",
            'Age (days)': f"{features['age_days']:.1f}",
            'Trade Freq': f"{features['trade_frequency']:.1f}",
            'Volume (24h)': f"{features['avg_volume_24h']:.0f}",
            'Viability': f"{viability_score:.0f}",
            'Rec': rec,
        })
    
    results_df = pd.DataFrame(results)
    print("\n" + results_df.to_string(index=False))
    
    return results_df


def main():
    print("=" * 80)
    print("PHASE 22 - MARKET LIFECYCLE DETECTION SYSTEM")
    print("=" * 80)
    
    # Step 1: Load data
    trades_df = load_and_prepare_data()
    
    # Step 2: Feature extraction
    market_features = extract_market_features(trades_df)
    
    # Step 3: Lifecycle classification
    classifications = classify_lifecycle(market_features)
    
    # Step 4: Viability backtest
    stage_viability, stage_stats = test_viability_by_stage(trades_df, classifications)
    
    # Step 5: Answer key questions
    answers = answer_key_questions(classifications, trades_df, stage_viability, stage_stats)
    
    # Step 6: Generate output table
    output_table = generate_output_table(classifications, stage_viability)
    
    # Summary verdict
    print("\n" + "=" * 80)
    print("VERDICT: Does market lifecycle classification create real edge?")
    print("=" * 80)
    
    emerging_stats = answers['q4_system_value'].get('EMERGING', {})
    mid_stats = answers['q4_system_value'].get('MID', {})
    mature_stats = answers['q4_system_value'].get('MATURE', {})
    
    emerging_viability = emerging_stats.get('avg_viability_score', 0) if emerging_stats else 0
    mid_viability = mid_stats.get('avg_viability_score', 0) if mid_stats else 0
    mature_viability = mature_stats.get('avg_viability_score', 0) if mature_stats else 0
    
    viable_scores = [s for s in [emerging_viability, mid_viability, mature_viability] if s > 0]
    avg_viability = np.mean(viable_scores) if viable_scores else 0
    
    print(f"\nAverage Viability Score by Stage:")
    if emerging_stats:
        print(f"  EMERGING: {emerging_viability:.1f}/100 (n={emerging_stats['count']} markets)")
    if mid_stats:
        print(f"  MID: {mid_viability:.1f}/100 (n={mid_stats['count']} markets)")
    if mature_stats:
        print(f"  MATURE: {mature_viability:.1f}/100 (n={mature_stats['count']} markets)")
    print(f"  Overall Average: {avg_viability:.1f}/100")
    
    # Verdict
    print(f"\n{'=' * 80}")
    if avg_viability > 65:
        print("✓✓ LIFECYCLE DETECTION CREATES STRONG EDGE")
        print(f"  - High viability scores across stages indicate real trading opportunity")
        print(f"  - {answers['q3_opportunity_set']['tradable_pct']:.0f}% of markets are in EMERGING/MID (high alpha zones)")
        print(f"  - Recommendation: PRIORITIZE lifecycle-based market selection")
        print(f"  - Focus on EMERGING ({emerging_viability:.0f}) and MID ({mid_viability:.0f}) stages")
    elif avg_viability > 55:
        print("✓ LIFECYCLE DETECTION CREATES MARGINAL EDGE")
        print(f"  - Viability score {avg_viability:.0f} suggests modest advantage")
        print(f"  - Combine lifecycle classification with other alpha sources")
        print(f"  - Use as portfolio filter, not primary strategy")
    else:
        print("✗ LIFECYCLE DETECTION INSUFFICIENT EDGE")
        print(f"  - Viability score {avg_viability:.0f} too low for standalone approach")
        print(f"  - Consider alternative market selection methods")
        print(f"  - May still provide risk management value")
    
    print(f"\n{'=' * 80}")
    
    # Detailed recommendations
    print("\nDETAILED RECOMMENDATIONS FOR D.J.:")
    print("1. MARKET SELECTION STRATEGY:")
    print(f"   - Focus on EMERGING/MID markets ({answers['q3_opportunity_set']['tradable_pct']:.0f}% of universe)")
    print(f"   - Avoid MATURE markets unless other signals present")
    
    print("\n2. LIFECYCLE MONITORING:")
    emerging_spread = answers['q2_lifecycle_duration'].get('avg_spread_emerging', 0)
    mature_spread = answers['q2_lifecycle_duration'].get('avg_spread_mature', 0)
    print(f"   - Track spread compression: {emerging_spread:.0f} → {mature_spread:.0f} bps")
    print(f"   - Monitor age-to-stage transitions for timing entries/exits")
    
    print("\n3. STAGE-SPECIFIC TACTICS:")
    if emerging_viability > 0:
        print(f"   - EMERGING: High spread capture ({emerging_stats.get('avg_spread_bps', 0):.0f} bps avg)")
        print(f"     Win rate: {emerging_stats.get('avg_win_rate', 0):.1f}%")
    if mid_viability > 0:
        print(f"   - MID: Balanced risk/reward ({mid_stats.get('avg_spread_bps', 0):.0f} bps avg)")
        print(f"     Win rate: {mid_stats.get('avg_win_rate', 0):.1f}%")
    
    print("\n4. NEXT STEPS:")
    print("   - Implement real-time lifecycle detection in trading system")
    print("   - Add position sizing based on stage (higher risk in EMERGING)")
    print("   - Set stage-specific stop losses and profit targets")
    
    # Save results to JSON
    output_json = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'summary': {
            'total_markets': len(classifications),
            'overall_viability': avg_viability,
            'verdict': 'STRONG_EDGE' if avg_viability > 65 else ('MARGINAL_EDGE' if avg_viability > 55 else 'INSUFFICIENT'),
        },
        'distribution': {
            'EMERGING': answers['q3_opportunity_set']['emerging_count'],
            'MID': answers['q3_opportunity_set']['mid_count'],
            'MATURE': answers['q3_opportunity_set']['mature_count'],
        },
        'answers': answers,
    }
    
    output_path = Path("/Users/rrg/.openclaw/workspace/PHASE22_results.json")
    with open(output_path, 'w') as f:
        json.dump(output_json, f, indent=2, default=str)
    
    print(f"\n[SAVED] Results to {output_path}")
    
    # Also save CSV table
    output_csv = Path("/Users/rrg/.openclaw/workspace/PHASE22_markets_table.csv")
    output_table.to_csv(output_csv, index=False)
    print(f"[SAVED] Markets table to {output_csv}")


if __name__ == '__main__':
    main()
