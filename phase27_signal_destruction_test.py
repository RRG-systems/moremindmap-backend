#!/usr/bin/env python3
"""
PHASE 27: SIGNAL DESTRUCTION TEST
Aggressively test whether Phase 26 signals survive out-of-sample conditions
and adversarial environments. Determine if signals are REAL, CONDITIONAL, or FRAGILE.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# DATA LOADING & SPLITTING
# ============================================================================

def load_multi_asset_data():
    """Load BTC and ETH hourly data"""
    assets = {}
    
    for asset in ['BTC', 'ETH']:
        df = pd.read_csv(f'/Users/rrg/.openclaw/workspace/crypto_phase_x_{asset}_hourly.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # Calculate features
        df['returns'] = df['close'].pct_change()
        df['returns_bps'] = df['returns'] * 10000
        df['high_low'] = (df['high'] - df['low']) / df['close']
        
        # Volatility
        df['vol_5'] = df['returns'].rolling(5).std()
        df['vol_10'] = df['returns'].rolling(10).std()
        df['vol_20'] = df['returns'].rolling(20).std()
        df['realized_vol'] = df['returns'].rolling(20).std()
        
        # Moving averages
        df['ma_5'] = df['close'].rolling(5).mean()
        df['ma_10'] = df['close'].rolling(10).mean()
        df['ma_20'] = df['close'].rolling(20).mean()
        
        # Time features
        df['hour'] = df['timestamp'].dt.hour
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        
        assets[asset] = df.dropna()
    
    return assets

def split_data_in_sample_out_of_sample(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Split data: first 50% = in-sample (Phase 26), second 50% = out-of-sample (Phase 27)"""
    split_idx = len(df) // 2
    return df.iloc[:split_idx].reset_index(drop=True), df.iloc[split_idx:].reset_index(drop=True)

def identify_regimes(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """Identify market regimes"""
    vol_threshold_high = df['realized_vol'].quantile(0.75)
    vol_threshold_low = df['realized_vol'].quantile(0.25)
    
    # Detect trend: simple slope of 20-period MA
    df['trend'] = df['ma_20'].diff(20)
    trend_threshold = df['trend'].std()
    
    regimes = {}
    regimes['high_vol'] = df[df['realized_vol'] > vol_threshold_high].reset_index(drop=True)
    regimes['low_vol'] = df[df['realized_vol'] < vol_threshold_low].reset_index(drop=True)
    regimes['trending'] = df[df['trend'] > trend_threshold].reset_index(drop=True)
    regimes['ranging'] = df[abs(df['trend']) <= trend_threshold].reset_index(drop=True)
    
    return regimes

# ============================================================================
# TRADE EXECUTION & RECORDING
# ============================================================================

@dataclass
class Trade:
    entry_idx: int
    exit_idx: int
    entry_price: float
    exit_price: float
    direction: int
    win: bool
    pnl_bps: float
    duration_ticks: int
    signal_family: str
    signal_variant: str
    cost_bps: int

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
        signal_variant=signal_variant,
        cost_bps=cost_bps
    )

# ============================================================================
# SIGNAL IMPLEMENTATIONS (FROM PHASE 26)
# ============================================================================

def test_weekend_bias(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """Weekend Bias signal - exact parameters from Phase 26"""
    trades = []
    
    for i in range(1, len(df) - 1):
        is_weekend = df['day_of_week'].iloc[i] >= 5
        weekend_bias = df[df['day_of_week'] >= 5]['returns'].mean()
        
        if is_weekend:
            direction = 1 if weekend_bias > 0 else -1
            curr_price = df['close'].iloc[i]
            
            # Exit target: ±2%
            for j in range(i+1, min(i+50, len(df))):
                exit_price = df['close'].iloc[j]
                ret_pct = (exit_price - curr_price) / curr_price * direction
                
                if ret_pct >= 0.02 or ret_pct <= -0.02:
                    trade = record_trade(i, j, curr_price, exit_price, direction, cost_bps,
                                       'TimeBased', 'TB_Weekend')
                    trades.append(trade)
                    break
    
    return trades

def test_mean_reversion_20tick_03pct(df: pd.DataFrame, cost_bps: int = 10) -> List[Trade]:
    """Mean Reversion 20-tick, 0.3% fade - exact parameters from Phase 26"""
    trades = []
    
    for i in range(20, len(df) - 1):
        ma20 = df['close'].iloc[i-20:i].mean()
        curr_price = df['close'].iloc[i]
        dev_pct = (curr_price - ma20) / ma20
        
        if abs(dev_pct) > 0.003:  # >0.3% deviation
            direction = -1 if dev_pct > 0 else 1  # Fade the move
            
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
# ANALYTICS
# ============================================================================

def compute_statistics(trades: List[Trade]) -> Dict:
    """Compute comprehensive statistics"""
    if len(trades) == 0:
        return {
            'trades': 0,
            'win_rate_pct': 0,
            'avg_pnl_bps': 0,
            'std_dev_bps': 0,
            'median_pnl_bps': 0,
            'max_win_bps': 0,
            'max_loss_bps': 0,
            'max_consecutive_losses': 0,
            'sharpe_ratio': 0,
            'max_drawdown_bps': 0,
            'profit_factor': 0,
        }
    
    pnls = [t.pnl_bps for t in trades]
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p <= 0]
    
    # Max consecutive losses
    max_consecutive = 0
    current_consecutive = 0
    for t in trades:
        if t.win:
            current_consecutive = 0
        else:
            current_consecutive += 1
            max_consecutive = max(max_consecutive, current_consecutive)
    
    # Cumulative PnL for drawdown
    cumulative = np.cumsum(pnls)
    running_max = np.maximum.accumulate(cumulative)
    drawdown = running_max - cumulative
    max_drawdown = np.max(drawdown) if len(drawdown) > 0 else 0
    
    # Sharpe (annualized, assuming hourly = 8760 hours/year)
    sharpe = 0
    if len(pnls) > 1:
        daily_pnl_std = np.std(pnls)
        if daily_pnl_std > 0:
            sharpe = (np.mean(pnls) / daily_pnl_std) * np.sqrt(252)  # Annualized
    
    # Profit factor
    profit_factor = 0
    if losses:
        profit_factor = sum(wins) / abs(sum(losses)) if sum(losses) != 0 else 0
    
    return {
        'trades': len(trades),
        'win_rate_pct': (sum(1 for t in trades if t.win) / len(trades) * 100) if len(trades) > 0 else 0,
        'avg_pnl_bps': np.mean(pnls),
        'std_dev_bps': np.std(pnls),
        'median_pnl_bps': np.median(pnls),
        'max_win_bps': np.max(pnls) if pnls else 0,
        'max_loss_bps': np.min(pnls) if pnls else 0,
        'max_consecutive_losses': max_consecutive,
        'sharpe_ratio': sharpe,
        'max_drawdown_bps': max_drawdown,
        'profit_factor': profit_factor,
    }

def compare_performance(in_sample_stats: Dict, out_of_sample_stats: Dict) -> Dict:
    """Compare in-sample vs out-of-sample performance"""
    degradation = {}
    
    if in_sample_stats['avg_pnl_bps'] > 0:
        edge_degradation_pct = (1 - out_of_sample_stats['avg_pnl_bps'] / in_sample_stats['avg_pnl_bps']) * 100
    else:
        edge_degradation_pct = -999  # Undefined
    
    degradation['edge_degradation_pct'] = edge_degradation_pct
    degradation['is_acceptable'] = edge_degradation_pct < 30  # <30% loss acceptable
    degradation['is_catastrophic'] = edge_degradation_pct > 50  # >50% loss = catastrophic
    
    return degradation

# ============================================================================
# STEP 1: OUT-OF-SAMPLE TEST
# ============================================================================

def step1_out_of_sample_test(assets: Dict):
    """Test signals on new time period (second 50% of data)"""
    print("\n" + "="*80)
    print("STEP 1: OUT-OF-SAMPLE TEST")
    print("="*80)
    
    results = {}
    
    for asset in ['BTC', 'ETH']:
        print(f"\n--- Asset: {asset} ---")
        df_full = assets[asset]
        df_insample, df_oosample = split_data_in_sample_out_of_sample(df_full)
        
        print(f"In-sample: {len(df_insample)} candles | {df_insample['timestamp'].min()} to {df_insample['timestamp'].max()}")
        print(f"Out-of-sample: {len(df_oosample)} candles | {df_oosample['timestamp'].min()} to {df_oosample['timestamp'].max()}")
        
        results[asset] = {}
        
        # Test Weekend Bias
        print(f"\nWeekend Bias:")
        trades_insample = test_weekend_bias(df_insample, cost_bps=10)
        trades_oosample = test_weekend_bias(df_oosample, cost_bps=10)
        
        stats_insample = compute_statistics(trades_insample)
        stats_oosample = compute_statistics(trades_oosample)
        degradation = compare_performance(stats_insample, stats_oosample)
        
        print(f"  In-sample: {stats_insample['trades']} trades, {stats_insample['avg_pnl_bps']:.1f} bps/trade, WR {stats_insample['win_rate_pct']:.1f}%")
        print(f"  Out-of-sample: {stats_oosample['trades']} trades, {stats_oosample['avg_pnl_bps']:.1f} bps/trade, WR {stats_oosample['win_rate_pct']:.1f}%")
        print(f"  Edge degradation: {degradation['edge_degradation_pct']:.1f}%")
        
        results[asset]['weekend_bias'] = {
            'in_sample': stats_insample,
            'out_of_sample': stats_oosample,
            'degradation': degradation,
            'trades_insample': len(trades_insample),
            'trades_oosample': len(trades_oosample),
            'survives': len(trades_oosample) >= 50 and stats_oosample['avg_pnl_bps'] > 0
        }
        
        # Test Mean Reversion
        print(f"\nMean Reversion (20-tick, 0.3%):")
        trades_insample = test_mean_reversion_20tick_03pct(df_insample, cost_bps=10)
        trades_oosample = test_mean_reversion_20tick_03pct(df_oosample, cost_bps=10)
        
        stats_insample = compute_statistics(trades_insample)
        stats_oosample = compute_statistics(trades_oosample)
        degradation = compare_performance(stats_insample, stats_oosample)
        
        print(f"  In-sample: {stats_insample['trades']} trades, {stats_insample['avg_pnl_bps']:.1f} bps/trade, WR {stats_insample['win_rate_pct']:.1f}%")
        print(f"  Out-of-sample: {stats_oosample['trades']} trades, {stats_oosample['avg_pnl_bps']:.1f} bps/trade, WR {stats_oosample['win_rate_pct']:.1f}%")
        print(f"  Edge degradation: {degradation['edge_degradation_pct']:.1f}%")
        
        results[asset]['mean_reversion'] = {
            'in_sample': stats_insample,
            'out_of_sample': stats_oosample,
            'degradation': degradation,
            'trades_insample': len(trades_insample),
            'trades_oosample': len(trades_oosample),
            'survives': len(trades_oosample) >= 50 and stats_oosample['avg_pnl_bps'] > 0
        }
    
    return results

# ============================================================================
# STEP 2: CROSS-ASSET TEST
# ============================================================================

def step2_cross_asset_test(assets: Dict):
    """Test signals across assets"""
    print("\n" + "="*80)
    print("STEP 2: CROSS-ASSET TEST")
    print("="*80)
    
    results = {}
    
    for signal_name, test_func in [('weekend_bias', test_weekend_bias), 
                                     ('mean_reversion', test_mean_reversion_20tick_03pct)]:
        print(f"\n--- Signal: {signal_name} ---")
        results[signal_name] = {}
        
        for asset in ['BTC', 'ETH']:
            df_full = assets[asset]
            df_insample, df_oosample = split_data_in_sample_out_of_sample(df_full)
            
            trades = test_func(df_oosample, cost_bps=10)
            stats = compute_statistics(trades)
            
            print(f"{asset}: {stats['trades']} trades, {stats['avg_pnl_bps']:.1f} bps, WR {stats['win_rate_pct']:.1f}%")
            
            results[signal_name][asset] = {
                'trades': stats['trades'],
                'avg_pnl_bps': stats['avg_pnl_bps'],
                'win_rate_pct': stats['win_rate_pct'],
                'std_dev_bps': stats['std_dev_bps'],
                'degrades': stats['avg_pnl_bps'] < 20,  # Threshold for significant degradation
            }
    
    return results

# ============================================================================
# STEP 3: REGIME SPLIT TEST
# ============================================================================

def step3_regime_split_test(assets: Dict):
    """Test signals under different market regimes"""
    print("\n" + "="*80)
    print("STEP 3: REGIME SPLIT TEST")
    print("="*80)
    
    results = {}
    
    for asset in ['BTC']:  # Focus on BTC for regime analysis
        print(f"\n--- Asset: {asset} ---")
        df_full = assets[asset]
        df_insample, df_oosample = split_data_in_sample_out_of_sample(df_full)
        
        regimes = identify_regimes(df_oosample)
        
        results[asset] = {}
        
        for regime_name, regime_df in regimes.items():
            print(f"\n{regime_name.upper()} (n={len(regime_df)}):")
            
            # Weekend Bias
            trades_wb = test_weekend_bias(regime_df, cost_bps=10)
            stats_wb = compute_statistics(trades_wb)
            print(f"  Weekend Bias: {stats_wb['trades']} trades, {stats_wb['avg_pnl_bps']:.1f} bps, WR {stats_wb['win_rate_pct']:.1f}%")
            
            # Mean Reversion
            trades_mr = test_mean_reversion_20tick_03pct(regime_df, cost_bps=10)
            stats_mr = compute_statistics(trades_mr)
            print(f"  Mean Reversion: {stats_mr['trades']} trades, {stats_mr['avg_pnl_bps']:.1f} bps, WR {stats_mr['win_rate_pct']:.1f}%")
            
            results[asset][regime_name] = {
                'weekend_bias': {
                    'trades': stats_wb['trades'],
                    'avg_pnl_bps': stats_wb['avg_pnl_bps'],
                    'win_rate_pct': stats_wb['win_rate_pct'],
                },
                'mean_reversion': {
                    'trades': stats_mr['trades'],
                    'avg_pnl_bps': stats_mr['avg_pnl_bps'],
                    'win_rate_pct': stats_mr['win_rate_pct'],
                }
            }
    
    return results

# ============================================================================
# STEP 4: COST STRESS TEST
# ============================================================================

def step4_cost_stress_test(assets: Dict):
    """Test robustness to higher execution costs"""
    print("\n" + "="*80)
    print("STEP 4: COST STRESS TEST")
    print("="*80)
    
    results = {}
    cost_scenarios = [
        (10, 'baseline'),
        (15, '+50% cost'),
        (20, '+100% cost')
    ]
    
    for signal_name, test_func in [('weekend_bias', test_weekend_bias),
                                     ('mean_reversion', test_mean_reversion_20tick_03pct)]:
        print(f"\n--- Signal: {signal_name} ---")
        results[signal_name] = {}
        
        df_full = assets['BTC']
        df_insample, df_oosample = split_data_in_sample_out_of_sample(df_full)
        
        for cost_bps, scenario_name in cost_scenarios:
            trades = test_func(df_oosample, cost_bps=cost_bps)
            stats = compute_statistics(trades)
            
            print(f"{scenario_name} ({cost_bps} bps): {stats['trades']} trades, {stats['avg_pnl_bps']:.1f} bps, WR {stats['win_rate_pct']:.1f}%")
            
            results[signal_name][scenario_name] = {
                'cost_bps': cost_bps,
                'trades': stats['trades'],
                'avg_pnl_bps': stats['avg_pnl_bps'],
                'win_rate_pct': stats['win_rate_pct'],
                'survives': stats['avg_pnl_bps'] > 0,
            }
    
    return results

# ============================================================================
# STEP 5: PERFORMANCE STABILITY METRICS
# ============================================================================

def step5_performance_stability_metrics(assets: Dict):
    """Measure consistency and stability"""
    print("\n" + "="*80)
    print("STEP 5: PERFORMANCE STABILITY METRICS")
    print("="*80)
    
    results = {}
    
    df_full = assets['BTC']
    df_insample, df_oosample = split_data_in_sample_out_of_sample(df_full)
    
    for signal_name, test_func in [('weekend_bias', test_weekend_bias),
                                     ('mean_reversion', test_mean_reversion_20tick_03pct)]:
        print(f"\n--- Signal: {signal_name} ---")
        
        trades = test_func(df_oosample, cost_bps=10)
        stats = compute_statistics(trades)
        
        print(f"Total trades: {stats['trades']}")
        print(f"Win rate: {stats['win_rate_pct']:.1f}%")
        print(f"Avg PnL: {stats['avg_pnl_bps']:.1f} bps")
        print(f"Std dev: {stats['std_dev_bps']:.1f} bps")
        print(f"Sharpe ratio: {stats['sharpe_ratio']:.2f}")
        print(f"Max drawdown: {stats['max_drawdown_bps']:.1f} bps")
        print(f"Max consecutive losses: {stats['max_consecutive_losses']}")
        print(f"Profit factor: {stats['profit_factor']:.2f}")
        
        # Time slice consistency
        if stats['trades'] > 30:
            third = len(trades) // 3
            early_trades = trades[:third]
            mid_trades = trades[third:2*third]
            late_trades = trades[2*third:]
            
            early_stats = compute_statistics(early_trades)
            mid_stats = compute_statistics(mid_trades)
            late_stats = compute_statistics(late_trades)
            
            print(f"Early ({len(early_trades)} trades): {early_stats['avg_pnl_bps']:.1f} bps")
            print(f"Mid ({len(mid_trades)} trades): {mid_stats['avg_pnl_bps']:.1f} bps")
            print(f"Late ({len(late_trades)} trades): {late_stats['avg_pnl_bps']:.1f} bps")
            
            results[signal_name] = {
                'overall': stats,
                'early': early_stats,
                'mid': mid_stats,
                'late': late_stats,
                'consistency': {
                    'early_pnl': early_stats['avg_pnl_bps'],
                    'mid_pnl': mid_stats['avg_pnl_bps'],
                    'late_pnl': late_stats['avg_pnl_bps'],
                }
            }
        else:
            results[signal_name] = {'overall': stats}
    
    return results

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    print("\n" + "="*80)
    print("PHASE 27: SIGNAL DESTRUCTION TEST")
    print("="*80)
    print("Purpose: Aggressively test whether Phase 26 signals survive")
    print("out-of-sample conditions and adversarial environments.")
    
    # Load data
    print("\n[Loading data...]")
    assets = load_multi_asset_data()
    
    # Execute all tests
    print("\n[Executing destruction tests...]")
    
    results_step1 = step1_out_of_sample_test(assets)
    results_step2 = step2_cross_asset_test(assets)
    results_step3 = step3_regime_split_test(assets)
    results_step4 = step4_cost_stress_test(assets)
    results_step5 = step5_performance_stability_metrics(assets)
    
    # ========================================================================
    # ANALYSIS & VERDICTS
    # ========================================================================
    
    print("\n" + "="*80)
    print("ANALYSIS & VERDICTS")
    print("="*80)
    
    # QUESTION 1: Out-of-sample survival
    print("\n[QUESTION 1] Do both signals survive out-of-sample?\n")
    
    weekend_bias_survives = results_step1['BTC']['weekend_bias']['survives']
    mean_reversion_survives = results_step1['BTC']['mean_reversion']['survives']
    
    print(f"Weekend Bias (BTC out-of-sample):")
    wb_oos = results_step1['BTC']['weekend_bias']['out_of_sample']
    print(f"  Trades: {wb_oos['trades']} | Avg PnL: {wb_oos['avg_pnl_bps']:.1f} bps | WR: {wb_oos['win_rate_pct']:.1f}%")
    print(f"  Survives (>50 trades, >0 PnL): {weekend_bias_survives}")
    
    print(f"\nMean Reversion (BTC out-of-sample):")
    mr_oos = results_step1['BTC']['mean_reversion']['out_of_sample']
    print(f"  Trades: {mr_oos['trades']} | Avg PnL: {mr_oos['avg_pnl_bps']:.1f} bps | WR: {mr_oos['win_rate_pct']:.1f}%")
    print(f"  Survives (>50 trades, >0 PnL): {mean_reversion_survives}")
    
    # Edge degradation
    print(f"\nEdge Degradation:")
    wb_degrad = results_step1['BTC']['weekend_bias']['degradation']['edge_degradation_pct']
    mr_degrad = results_step1['BTC']['mean_reversion']['degradation']['edge_degradation_pct']
    print(f"  Weekend Bias: {wb_degrad:.1f}% {'(ACCEPTABLE <30%)' if wb_degrad < 30 else '(CATASTROPHIC >50%)' if wb_degrad > 50 else '(MARGINAL)'}")
    print(f"  Mean Reversion: {mr_degrad:.1f}% {'(ACCEPTABLE <30%)' if mr_degrad < 30 else '(CATASTROPHIC >50%)' if mr_degrad > 50 else '(MARGINAL)'}")
    
    # QUESTION 2: Stability across regimes & assets
    print("\n[QUESTION 2] Which signal is more stable across regimes & assets?\n")
    
    print(f"Weekend Bias - Cross-asset:")
    for asset, data in results_step2['weekend_bias'].items():
        print(f"  {asset}: {data['avg_pnl_bps']:.1f} bps {'(DEGRADES)' if data['degrades'] else '(HOLDS)'}")
    
    print(f"\nMean Reversion - Cross-asset:")
    for asset, data in results_step2['mean_reversion'].items():
        print(f"  {asset}: {data['avg_pnl_bps']:.1f} bps {'(DEGRADES)' if data['degrades'] else '(HOLDS)'}")
    
    print(f"\nWeekend Bias - Regime performance (BTC):")
    for regime, data in results_step3['BTC'].items():
        wb_pnl = data['weekend_bias']['avg_pnl_bps']
        print(f"  {regime}: {wb_pnl:.1f} bps")
    
    print(f"\nMean Reversion - Regime performance (BTC):")
    for regime, data in results_step3['BTC'].items():
        mr_pnl = data['mean_reversion']['avg_pnl_bps']
        print(f"  {regime}: {mr_pnl:.1f} bps")
    
    # QUESTION 3: Cost stress resilience
    print("\n[QUESTION 3] Does edge survive under cost stress?\n")
    
    print(f"Weekend Bias:")
    for scenario, data in results_step4['weekend_bias'].items():
        print(f"  {scenario}: {data['avg_pnl_bps']:.1f} bps {'(SURVIVES)' if data['survives'] else '(FAILS)'}")
    
    print(f"\nMean Reversion:")
    for scenario, data in results_step4['mean_reversion'].items():
        print(f"  {scenario}: {data['avg_pnl_bps']:.1f} bps {'(SURVIVES)' if data['survives'] else '(FAILS)'}")
    
    # QUESTION 4: Deployment readiness
    print("\n[QUESTION 4] Deployment readiness scoring\n")
    
    def compute_readiness(signal_name: str):
        score = 0
        issues = []
        
        # Out-of-sample survival (30 pts)
        if results_step1['BTC'][signal_name]['survives']:
            score += 20
        else:
            issues.append("Failed out-of-sample survival")
        
        if abs(results_step1['BTC'][signal_name]['degradation']['edge_degradation_pct']) < 30:
            score += 10
        else:
            issues.append("Excessive edge degradation (>30%)")
        
        # Cross-asset stability (20 pts)
        cross_asset = results_step2[signal_name]
        stable = sum(1 for d in cross_asset.values() if not d['degrades']) / len(cross_asset) > 0.5
        score += 10 if stable else 0
        if not stable:
            issues.append("Unstable across assets")
        
        # Regime stability (20 pts)
        regimes = results_step3['BTC']
        regime_consistent = True
        for regime, data in regimes.items():
            if signal_name == 'weekend_bias':
                pnl = data['weekend_bias']['avg_pnl_bps']
            else:
                pnl = data['mean_reversion']['avg_pnl_bps']
            
            if pnl < 0:
                regime_consistent = False
        
        score += 10 if regime_consistent else 0
        if not regime_consistent:
            issues.append("Negative PnL in some regimes")
        
        # Cost stress (20 pts)
        cost_stress = results_step4[signal_name]
        all_cost_survive = all(d['survives'] for d in cost_stress.values())
        score += 20 if all_cost_survive else 10
        if not all_cost_survive:
            issues.append("Fails under high-cost scenarios")
        
        # Stability metrics (10 pts)
        if signal_name in results_step5:
            stability_data = results_step5[signal_name]
            sharpe = stability_data.get('overall', {}).get('sharpe_ratio', 0)
            max_dd = stability_data.get('overall', {}).get('max_drawdown_bps', 999)
            if sharpe > 1.0 and max_dd < 100:
                score += 10
            else:
                issues.append("Poor stability metrics")
        
        return score, issues
    
    wb_readiness, wb_issues = compute_readiness('weekend_bias')
    mr_readiness, mr_issues = compute_readiness('mean_reversion')
    
    print(f"Weekend Bias: {wb_readiness}%")
    if wb_issues:
        for issue in wb_issues:
            print(f"  ⚠ {issue}")
    else:
        print(f"  ✓ All checks passed")
    
    print(f"\nMean Reversion: {mr_readiness}%")
    if mr_issues:
        for issue in mr_issues:
            print(f"  ⚠ {issue}")
    else:
        print(f"  ✓ All checks passed")
    
    # FINAL VERDICTS
    print("\n" + "="*80)
    print("FINAL VERDICTS")
    print("="*80)
    
    def verdict_for_signal(signal_name: str, readiness: int):
        if readiness >= 80:
            return "REAL"
        elif readiness >= 50:
            return "CONDITIONAL"
        else:
            return "FRAGILE"
    
    wb_verdict = verdict_for_signal('weekend_bias', wb_readiness)
    mr_verdict = verdict_for_signal('mean_reversion', mr_readiness)
    
    print(f"\nWeekend Bias: {wb_verdict} (readiness: {wb_readiness}%)")
    print(f"Mean Reversion: {mr_verdict} (readiness: {mr_readiness}%)")
    
    print(f"\nRecommendation:")
    if wb_readiness >= 50 or mr_readiness >= 50:
        print(f"  Deploy {[s for s, r in [('Weekend Bias', wb_readiness), ('Mean Reversion', mr_readiness)] if r >= 50]}")
        print(f"  Treat as {'CONDITIONAL' if max(wb_readiness, mr_readiness) < 80 else 'REAL'} - monitor actively")
    else:
        print(f"  Both signals fail destruction test. Return to Phase 26 and reconsider.")
    
    # ========================================================================
    # SAVE RESULTS
    # ========================================================================
    
    output = {
        'phase': 27,
        'title': 'Signal Destruction Test',
        'timestamp': datetime.now().isoformat(),
        'step1_out_of_sample': {k: {kk: (v.tolist() if isinstance(v, np.ndarray) else (dict(v) if hasattr(v, '__dict__') else v) 
                                           if not isinstance(v, (int, float, str, bool, list, dict)) else v) 
                                     for kk, v in vv.items()} 
                                for k, vv in results_step1.items()},
        'step2_cross_asset': results_step2,
        'step3_regime_split': results_step3,
        'step4_cost_stress': results_step4,
        'verdicts': {
            'weekend_bias': {
                'verdict': wb_verdict,
                'readiness_pct': wb_readiness,
                'issues': wb_issues
            },
            'mean_reversion': {
                'verdict': mr_verdict,
                'readiness_pct': mr_readiness,
                'issues': mr_issues
            }
        },
        'recommendation': 'Deploy conditional' if max(wb_readiness, mr_readiness) >= 50 else 'Reject both signals'
    }
    
    with open('/Users/rrg/.openclaw/workspace/phase27_results.json', 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\n[Results saved to: phase27_results.json]")
    
    return output

if __name__ == '__main__':
    results = main()
