#!/usr/bin/env python3
"""
PHASE 26: Disciplined Signal Discovery
Strict filtering, 50+ trade minimum, statistical stability test
No parameter tuning, no optimization
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from dataclasses import dataclass
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA LOADING
# ============================================================================

def load_btc_data():
    """Load BTC hourly data"""
    df = pd.read_csv('/Users/rrg/.openclaw/workspace/crypto_phase_x_BTC_hourly.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    
    # Calculate additional features
    df['returns'] = df['close'].pct_change()
    df['returns_bps'] = df['returns'] * 10000
    df['high_low'] = (df['high'] - df['low']) / df['close']
    
    # Volatility (rolling)
    df['vol_5'] = df['returns'].rolling(5).std()
    df['vol_10'] = df['returns'].rolling(10).std()
    df['vol_20'] = df['returns'].rolling(20).std()
    
    # Price momentum
    df['mom_3'] = (df['close'] - df['close'].shift(3)) / df['close'].shift(3)
    df['mom_5'] = (df['close'] - df['close'].shift(5)) / df['close'].shift(5)
    df['mom_10'] = (df['close'] - df['close'].shift(10)) / df['close'].shift(10)
    
    # Mean levels
    df['ma_5'] = df['close'].rolling(5).mean()
    df['ma_10'] = df['close'].rolling(10).mean()
    df['ma_20'] = df['close'].rolling(20).mean()
    
    # Buy/Sell pressure (mock: volume * direction)
    df['vol_direction'] = np.where(df['close'] > df['open'], df['volume'], -df['volume'])
    
    # Time features
    df['hour'] = df['timestamp'].dt.hour
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    
    return df.dropna()

# ============================================================================
# TRADE RECORDING
# ============================================================================

@dataclass
class Trade:
    entry_idx: int
    exit_idx: int
    entry_price: float
    exit_price: float
    direction: int  # 1 for long, -1 for short
    win: bool
    pnl_bps: float
    duration_ticks: int
    signal_family: str
    signal_variant: str

def record_trade(entry_idx: int, exit_idx: int, entry_price: float, exit_price: float,
                 direction: int, cost_bps: int, signal_family: str, signal_variant: str) -> Trade:
    """Record a trade with costs"""
    gross_return_bps = direction * (exit_price - entry_price) / entry_price * 10000
    net_pnl_bps = gross_return_bps - cost_bps
    win = net_pnl_bps > 0
    duration = exit_idx - entry_idx
    
    return Trade(
        entry_idx=entry_idx,
        exit_idx=exit_idx,
        entry_price=entry_price,
        exit_price=exit_price,
        direction=direction,
        win=win,
        pnl_bps=net_pnl_bps,
        duration_ticks=duration,
        signal_family=signal_family,
        signal_variant=signal_variant
    )

# ============================================================================
# FAMILY 1: MEAN REVERSION
# ============================================================================

def test_mean_reversion(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """
    Family 1: Mean reversion signals
    - 5-tick MA, fade 1-tick deviations
    - 10-tick MA, fade 0.5% deviations
    - 20-tick MA, fade 0.3% deviations
    """
    trades = []
    
    # Variant 1: 5-tick MA, fade 1-tick deviation
    for i in range(5, len(df) - 1):
        ma5 = df['close'].iloc[i-5:i].mean()
        curr_price = df['close'].iloc[i]
        dev_pct = (curr_price - ma5) / ma5
        
        if abs(dev_pct) > 0.01:  # >1% deviation
            direction = -1 if dev_pct > 0 else 1  # Fade the move
            
            # Exit at target/stop
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:  # ±2% target/stop
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'MeanReversion', 'MR_5tick_1pct')
                    trades.append(trade)
                    break
    
    # Variant 2: 10-tick MA, fade 0.5% deviation
    for i in range(10, len(df) - 1):
        ma10 = df['close'].iloc[i-10:i].mean()
        curr_price = df['close'].iloc[i]
        dev_pct = (curr_price - ma10) / ma10
        
        if abs(dev_pct) > 0.005:  # >0.5% deviation
            direction = -1 if dev_pct > 0 else 1
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'MeanReversion', 'MR_10tick_05pct')
                    trades.append(trade)
                    break
    
    # Variant 3: 20-tick MA, fade 0.3% deviation
    for i in range(20, len(df) - 1):
        ma20 = df['close'].iloc[i-20:i].mean()
        curr_price = df['close'].iloc[i]
        dev_pct = (curr_price - ma20) / ma20
        
        if abs(dev_pct) > 0.003:  # >0.3% deviation
            direction = -1 if dev_pct > 0 else 1
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'MeanReversion', 'MR_20tick_03pct')
                    trades.append(trade)
                    break
    
    return trades

# ============================================================================
# FAMILY 2: MOMENTUM CONTINUATION
# ============================================================================

def test_momentum(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """
    Family 2: Momentum continuation
    - 3-tick momentum (fast)
    - 5-tick momentum (medium)
    - 10-tick momentum (slow)
    """
    trades = []
    
    # Variant 1: 3-tick momentum
    for i in range(3, len(df) - 1):
        mom3 = (df['close'].iloc[i] - df['close'].iloc[i-3]) / df['close'].iloc[i-3]
        direction = 1 if mom3 > 0.001 else (-1 if mom3 < -0.001 else 0)
        
        if direction != 0:
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'Momentum', 'MOM_3tick')
                    trades.append(trade)
                    break
    
    # Variant 2: 5-tick momentum
    for i in range(5, len(df) - 1):
        mom5 = (df['close'].iloc[i] - df['close'].iloc[i-5]) / df['close'].iloc[i-5]
        direction = 1 if mom5 > 0.0015 else (-1 if mom5 < -0.0015 else 0)
        
        if direction != 0:
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'Momentum', 'MOM_5tick')
                    trades.append(trade)
                    break
    
    # Variant 3: 10-tick momentum
    for i in range(10, len(df) - 1):
        mom10 = (df['close'].iloc[i] - df['close'].iloc[i-10]) / df['close'].iloc[i-10]
        direction = 1 if mom10 > 0.002 else (-1 if mom10 < -0.002 else 0)
        
        if direction != 0:
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'Momentum', 'MOM_10tick')
                    trades.append(trade)
                    break
    
    return trades

# ============================================================================
# FAMILY 3: VOLATILITY-BASED ENTRIES
# ============================================================================

def test_volatility(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """
    Family 3: Volatility-based entries
    - Entry on vol > 1.0× baseline
    - Entry on vol > 1.5× baseline
    - Entry on vol > 2.0× baseline
    """
    trades = []
    
    # Baseline vol = 20-tick rolling std
    baseline_vol_multiplier = 1
    
    for vol_threshold, variant_name in [(1.0, 'VOL_1x'), (1.5, 'VOL_1.5x'), (2.0, 'VOL_2x')]:
        for i in range(20, len(df) - 1):
            current_vol = df['vol_20'].iloc[i]
            baseline_vol = df['vol_20'].iloc[max(0, i-20):i].mean()
            
            if baseline_vol > 0 and current_vol > baseline_vol * vol_threshold:
                # Direction = breakout direction (close > open)
                direction = 1 if df['close'].iloc[i] > df['open'].iloc[i] else -1
                curr_price = df['close'].iloc[i]
                
                for j in range(i+1, min(i+50, len(df))):
                    exit_price = df['close'].iloc[j]
                    ret_pct = (exit_price - curr_price) / curr_price * direction
                    
                    if ret_pct >= 0.02 or ret_pct <= -0.02:
                        trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                           'Volatility', variant_name)
                        trades.append(trade)
                        break
    
    return trades

# ============================================================================
# FAMILY 4: ORDER-FLOW PROXIES
# ============================================================================

def test_order_flow(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """
    Family 4: Order-flow proxies
    - Buy imbalance (close > open, high volume)
    - Sell imbalance (close < open, high volume)
    - Volume surge detection
    """
    trades = []
    
    # Variant 1: Buy imbalance (close > open)
    for i in range(1, len(df) - 1):
        if df['close'].iloc[i] > df['open'].iloc[i]:
            curr_volume = df['volume'].iloc[i]
            avg_volume = df['volume'].iloc[max(0, i-10):i].mean()
            
            if curr_volume > avg_volume * 1.2:  # Volume surge
                direction = 1
                curr_price = df['close'].iloc[i]
                
                for j in range(i+1, min(i+50, len(df))):
                    exit_price = df['close'].iloc[j]
                    ret_pct = (exit_price - curr_price) / curr_price
                    
                    if ret_pct >= 0.02 or ret_pct <= -0.02:
                        trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                           'OrderFlow', 'OF_BuyImbalance')
                        trades.append(trade)
                        break
    
    # Variant 2: Sell imbalance (close < open)
    for i in range(1, len(df) - 1):
        if df['close'].iloc[i] < df['open'].iloc[i]:
            curr_volume = df['volume'].iloc[i]
            avg_volume = df['volume'].iloc[max(0, i-10):i].mean()
            
            if curr_volume > avg_volume * 1.2:
                direction = -1
                curr_price = df['close'].iloc[i]
                
                for j in range(i+1, min(i+50, len(df))):
                    exit_price = df['close'].iloc[j]
                    ret_pct = (exit_price - curr_price) / curr_price * direction
                    
                    if ret_pct >= 0.02 or ret_pct <= -0.02:
                        trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                           'OrderFlow', 'OF_SellImbalance')
                        trades.append(trade)
                        break
    
    # Variant 3: Volume surge (any direction)
    for i in range(10, len(df) - 1):
        curr_volume = df['volume'].iloc[i]
        avg_volume = df['volume'].iloc[i-10:i].mean()
        
        if curr_volume > avg_volume * 1.5:
            direction = 1 if df['close'].iloc[i] > df['close'].iloc[i-1] else -1
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'OrderFlow', 'OF_VolSurge')
                    trades.append(trade)
                    break
    
    return trades

# ============================================================================
# FAMILY 5: TIME-BASED PATTERNS
# ============================================================================

def test_time_patterns(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """
    Family 5: Time-based patterns
    - 24-hour time-of-day bias
    - Morning effect (first 4 hours UTC)
    - Evening effect (last 4 hours UTC)
    - Weekend vs weekday
    """
    trades = []
    
    # Variant 1: Morning effect (UTC 0-4)
    for i in range(1, len(df) - 1):
        if df['hour'].iloc[i] in [0, 1, 2, 3]:
            morning_bias = df[df['hour'].isin([0,1,2,3])]['returns'].mean()
            direction = 1 if morning_bias > 0 else -1
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'TimeBased', 'TB_Morning')
                    trades.append(trade)
                    break
    
    # Variant 2: Evening effect (UTC 20-23)
    for i in range(1, len(df) - 1):
        if df['hour'].iloc[i] in [20, 21, 22, 23]:
            evening_bias = df[df['hour'].isin([20,21,22,23])]['returns'].mean()
            direction = 1 if evening_bias > 0 else -1
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'TimeBased', 'TB_Evening')
                    trades.append(trade)
                    break
    
    # Variant 3: Weekend effect
    for i in range(1, len(df) - 1):
        is_weekend = df['day_of_week'].iloc[i] >= 5
        weekend_bias = df[df['day_of_week'] >= 5]['returns'].mean()
        
        if is_weekend:
            direction = 1 if weekend_bias > 0 else -1
            curr_price = df['close'].iloc[i]
            
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'TimeBased', 'TB_Weekend')
                    trades.append(trade)
                    break
    
    return trades

# ============================================================================
# RANDOM BASELINE
# ============================================================================

def test_random_baseline(df: pd.DataFrame, cost_bps: int = 10, num_trades: int = 100) -> List[Trade]:
    """Generate random baseline trades"""
    trades = []
    np.random.seed(42)
    
    for _ in range(num_trades):
        entry_idx = np.random.randint(1, len(df) - 51)
        direction = np.random.choice([-1, 1])
        curr_price = df['close'].iloc[entry_idx]
        
        for j in range(entry_idx + 1, min(entry_idx + 50, len(df))):
            exit_price = df['close'].iloc[j]
            ret_pct = (exit_price - curr_price) / curr_price * direction
            
            if ret_pct >= 0.02 or ret_pct <= -0.02:
                trade = record_trade(entry_idx, j, curr_price, exit_price, direction, cost_bps,
                                   'Random', 'RANDOM_BASELINE')
                trades.append(trade)
                break
    
    return trades

# ============================================================================
# FILTERING & STATISTICS
# ============================================================================

def compute_statistics(trades: List[Trade]) -> Dict:
    """Compute statistics for a trade list"""
    if len(trades) == 0:
        return {
            'trades': 0,
            'win_rate': 0,
            'avg_pnl_bps': 0,
            'std_dev': 0,
            'passes_filters': False
        }
    
    pnls = [t.pnl_bps for t in trades]
    wins = sum(1 for t in trades if t.win)
    
    return {
        'trades': len(trades),
        'win_rate': (wins / len(trades) * 100) if len(trades) > 0 else 0,
        'avg_pnl_bps': np.mean(pnls),
        'std_dev': np.std(pnls),
        'median_pnl_bps': np.median(pnls),
        'max_win_bps': np.max(pnls),
        'max_loss_bps': np.min(pnls)
    }

def check_filtering_criteria(trades: List[Trade], random_baseline_stats: Dict) -> Tuple[bool, str]:
    """
    Check if trades pass ALL filtering criteria:
    1. Minimum 50 trades
    2. Win rate > 50%
    3. Net PnL/trade > 0 bps
    4. Edge vs random > 0
    5. Consistency across time slices
    6. Std dev reasonable relative to edge
    """
    
    if len(trades) < 50:
        return False, f"FAIL: Only {len(trades)} trades (need 50+)"
    
    stats = compute_statistics(trades)
    
    if stats['win_rate'] <= 50:
        return False, f"FAIL: Win rate {stats['win_rate']:.1f}% <= 50%"
    
    if stats['avg_pnl_bps'] <= 0:
        return False, f"FAIL: Avg PnL {stats['avg_pnl_bps']:.1f} bps <= 0"
    
    edge_vs_random = stats['avg_pnl_bps'] - random_baseline_stats['avg_pnl_bps']
    if edge_vs_random <= 0:
        return False, f"FAIL: Edge vs random {edge_vs_random:.1f} bps <= 0"
    
    # Check consistency across time slices
    third = len(trades) // 3
    if third > 10:
        early = trades[:third]
        mid = trades[third:2*third]
        late = trades[2*third:]
        
        early_pnl = np.mean([t.pnl_bps for t in early]) if early else 0
        mid_pnl = np.mean([t.pnl_bps for t in mid]) if mid else 0
        late_pnl = np.mean([t.pnl_bps for t in late]) if late else 0
        
        # Check consistency: don't want all edge in one slice
        pnls = [p for p in [early_pnl, mid_pnl, late_pnl] if p is not None]
        if pnls:
            max_slice = max(pnls)
            min_slice = min(pnls)
            consistency_ratio = max_slice / min_slice if min_slice != 0 else float('inf')
            
            if consistency_ratio > 5:  # One slice >5x another = concentrated
                return False, f"FAIL: Concentrated in time slices (ratio {consistency_ratio:.1f})"
    
    # Std dev check: should be <5x the edge size
    if stats['std_dev'] > stats['avg_pnl_bps'] * 5:
        return False, f"FAIL: High volatility (std {stats['std_dev']:.1f} > 5× edge {stats['avg_pnl_bps']:.1f})"
    
    return True, "PASS: All criteria met"

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("=" * 80)
    print("PHASE 26: DISCIPLINED SIGNAL DISCOVERY")
    print("=" * 80)
    
    # Load data
    print("\n[1] Loading BTC data...")
    df = load_btc_data()
    print(f"    Loaded {len(df)} hourly candles")
    print(f"    Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Generate random baseline
    print("\n[2] Generating random baseline (100 trades)...")
    random_trades = test_random_baseline(df, cost_bps=10, num_trades=100)
    random_stats = compute_statistics(random_trades)
    print(f"    Random baseline: {len(random_trades)} trades, "
          f"{random_stats['avg_pnl_bps']:.1f} bps/trade, "
          f"WR {random_stats['win_rate']:.1f}%")
    
    # Test all signal families
    print("\n[3] Testing signal families...")
    
    families = {
        'MeanReversion': test_mean_reversion,
        'Momentum': test_momentum,
        'Volatility': test_volatility,
        'OrderFlow': test_order_flow,
        'TimeBased': test_time_patterns
    }
    
    all_results = []
    
    for family_name, test_func in families.items():
        print(f"\n    Testing {family_name}...")
        trades = test_func(df, cost_bps=10)
        stats = compute_statistics(trades)
        passes, reason = check_filtering_criteria(trades, random_stats)
        
        print(f"      Generated {len(trades)} trades")
        if len(trades) > 0:
            print(f"      Avg PnL: {stats['avg_pnl_bps']:.1f} bps/trade, WR: {stats['win_rate']:.1f}%")
            edge_vs_random = stats['avg_pnl_bps'] - random_stats['avg_pnl_bps']
            print(f"      Edge vs random: {edge_vs_random:.1f} bps")
            print(f"      Result: {reason}")
        
        # Group by variant and report
        variants = {}
        for trade in trades:
            variant = trade.signal_variant
            if variant not in variants:
                variants[variant] = []
            variants[variant].append(trade)
        
        for variant, var_trades in variants.items():
            var_stats = compute_statistics(var_trades)
            var_passes, var_reason = check_filtering_criteria(var_trades, random_stats)
            
            edge_vs_random = var_stats['avg_pnl_bps'] - random_stats['avg_pnl_bps']
            
            result = {
                'signal': f"{family_name}_{variant}",
                'family': family_name,
                'variant': variant,
                'trades': var_stats['trades'],
                'win_rate_pct': var_stats['win_rate'],
                'avg_pnl_bps': var_stats['avg_pnl_bps'],
                'edge_vs_random_bps': edge_vs_random,
                'std_dev_bps': var_stats['std_dev'],
                'passes_filters': var_passes,
                'reason': var_reason
            }
            all_results.append(result)
    
    # ========================================================================
    # SUMMARY & ANSWERS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("RESULTS TABLE - ALL SIGNALS")
    print("=" * 80)
    
    # Sort by edge (highest first)
    all_results.sort(key=lambda x: x['edge_vs_random_bps'], reverse=True)
    
    passing = [r for r in all_results if r['passes_filters']]
    failing = [r for r in all_results if not r['passes_filters']]
    
    print(f"\n*** PASSING SIGNALS: {len(passing)} ***\n")
    if passing:
        for r in passing:
            print(f"Signal: {r['signal']}")
            print(f"  Trades: {r['trades']} | WR: {r['win_rate_pct']:.1f}% | "
                  f"PnL: {r['avg_pnl_bps']:.1f} bps | Edge vs random: {r['edge_vs_random_bps']:.1f} bps")
            print()
    else:
        print("(none)\n")
    
    print(f"*** FAILING SIGNALS: {len(failing)} ***\n")
    for r in failing[:10]:  # Top 10 failures
        print(f"Signal: {r['signal']}")
        print(f"  Trades: {r['trades']} | WR: {r['win_rate_pct']:.1f}% | "
              f"PnL: {r['avg_pnl_bps']:.1f} bps | {r['reason']}")
        print()
    
    # ========================================================================
    # FOUR KEY QUESTIONS
    # ========================================================================
    
    print("\n" + "=" * 80)
    print("FOUR KEY QUESTIONS")
    print("=" * 80)
    
    q1_pass_count = len(passing)
    q1_fail_count = len(failing)
    
    print(f"\n1. Did any signal survive stricter criteria?")
    print(f"   ANSWER: {'YES' if q1_pass_count > 0 else 'NO'}")
    print(f"   - Passing signals: {q1_pass_count}")
    print(f"   - Failing signals: {q1_fail_count}")
    if failing:
        fail_reasons = {}
        for r in failing:
            reason = r['reason'].split(':')[0]
            fail_reasons[reason] = fail_reasons.get(reason, 0) + 1
        print(f"   - Top failure reasons:")
        for reason, count in sorted(fail_reasons.items(), key=lambda x: -x[1]):
            print(f"     • {reason}: {count} signals")
    
    family_samples = {}
    for r in all_results:
        fam = r['family']
        if fam not in family_samples:
            family_samples[fam] = []
        family_samples[fam].append(r['trades'])
    
    best_family = max(family_samples.items(), key=lambda x: sum(x[1]))
    
    print(f"\n2. Which signal family shows most promise?")
    print(f"   ANSWER: {best_family[0]}")
    print(f"   - Total trades generated: {sum(best_family[1])}")
    print(f"   - Variants: {len(best_family[1])}")
    for fam, samples in sorted(family_samples.items(), key=lambda x: -sum(x[1])):
        print(f"   • {fam}: {sum(samples)} total trades, {len(samples)} variants")
    
    best_signal = max(all_results, key=lambda x: x['edge_vs_random_bps'])
    
    print(f"\n3. Are edges improving or still marginal?")
    print(f"   Phase 24 baseline (C_VolExpansion BTC): +38.3 bps (7 trades)")
    print(f"   Phase 25 result (C_VolExpansion): +56.6 bps (3 trades) - FAILED CRITERIA")
    print(f"   Phase 26 best signal: {best_signal['signal']}")
    print(f"   - Edge: {best_signal['edge_vs_random_bps']:.1f} bps")
    print(f"   - Trades: {best_signal['trades']}")
    print(f"   - Win rate: {best_signal['win_rate_pct']:.1f}%")
    if best_signal['edge_vs_random_bps'] > 38.3:
        print(f"   - STATUS: Edge IMPROVING (>{38.3} bps)")
    elif best_signal['edge_vs_random_bps'] > 20:
        print(f"   - STATUS: Edge MODERATE (>20 bps threshold)")
    else:
        print(f"   - STATUS: Edge MARGINAL (<20 bps)")
    
    print(f"\n4. Is further search justified?")
    if passing:
        print(f"   ANSWER: YES - REFINE & VALIDATE")
        print(f"   - {len(passing)} signal(s) passed strict criteria")
        print(f"   - Recommendation: Conduct extended validation on {len(passing)} best signal(s)")
        print(f"   - Focus: Confirm edge stability over longer period")
    else:
        print(f"   ANSWER: UNCERTAIN - EXPLORE ALTERNATIVES")
        print(f"   - No signals passed ALL strict criteria")
        print(f"   - Best partial: {best_signal['signal']} ({best_signal['edge_vs_random_bps']:.1f} bps, {best_signal['trades']} trades)")
        print(f"   - Recommendation: Consider parameter relaxation or alternative signal families")
    
    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    
    output = {
        'phase': 26,
        'title': 'Disciplined Signal Discovery - Strict Filtering',
        'timestamp': datetime.now().isoformat(),
        'data_summary': {
            'candles': len(df),
            'date_start': str(df['timestamp'].min()),
            'date_end': str(df['timestamp'].max())
        },
        'random_baseline': {
            'trades': random_stats['trades'],
            'avg_pnl_bps': random_stats['avg_pnl_bps'],
            'win_rate_pct': random_stats['win_rate'],
            'std_dev_bps': random_stats['std_dev']
        },
        'all_signals_tested': all_results,
        'passing_signals': passing,
        'failing_signals': failing,
        'summary': {
            'total_signals_tested': len(all_results),
            'signals_passing': len(passing),
            'signals_failing': len(failing),
            'best_signal': best_signal,
            'best_family': best_family[0]
        },
        'answers': {
            'q1_signals_surviving_stricter': q1_pass_count,
            'q2_best_family': best_family[0],
            'q3_best_edge_bps': best_signal['edge_vs_random_bps'],
            'q4_justify_further': 'YES' if passing else 'UNCERTAIN'
        }
    }
    
    with open('/Users/rrg/.openclaw/workspace/phase26_results.json', 'w') as f:
        json.dump(output, f, indent=2)
    
    print("\n" + "=" * 80)
    print(f"Results saved to: phase26_results.json")
    print("=" * 80)
    
    return output

if __name__ == '__main__':
    results = main()
