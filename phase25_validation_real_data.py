#!/usr/bin/env python3
"""
PHASE 25 - VOLATILITY EXPANSION VALIDATION (Real Data)
Using out-of-sample split from existing Phase X BTC hourly data.
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple, Dict, Optional
from datetime import datetime

# =====================================================================
# CONFIG - EXACT REPLICATION OF PHASE 24
# =====================================================================

SIGNAL_C_PARAMS = {
    'vol_lookback': 20,
    'vol_spike_threshold': 1.5,
    'target_pct': 2.0,
    'stop_pct': 2.0,
    'max_hold_ticks': 100,
    'costs_bps': 10,
}

# =====================================================================
# TRADE EXECUTION
# =====================================================================

@dataclass
class Trade:
    entry_price: float
    exit_price: float
    entry_idx: int
    exit_idx: int
    entry_timestamp: Optional[datetime] = None
    exit_timestamp: Optional[datetime] = None
    pnl_bps: float = 0.0
    pnl_pct: float = 0.0
    direction: str = 'LONG'
    reason: str = ''
    vol_spike_ratio: float = 1.0
    
    @property
    def is_win(self) -> bool:
        return self.pnl_bps > 0
    
    @property
    def duration_ticks(self) -> int:
        return self.exit_idx - self.entry_idx


class SignalC_VolatilityExpansion:
    """Signal C: Volatility Expansion."""
    
    def __init__(self, df: pd.DataFrame, params: Dict):
        self.df = df
        self.params = params
        self.prices = df['close'].values
        self.timestamps = df['timestamp'].values
        self.trades = []
    
    def apply_costs(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Apply crypto costs."""
        entry_cost_bps = self.params['costs_bps'] * 0.6
        exit_cost_bps = self.params['costs_bps'] * 0.4
        
        effective_entry = entry_price * (1 + entry_cost_bps / 10000)
        effective_exit = exit_price * (1 - exit_cost_bps / 10000)
        
        return effective_entry, effective_exit
    
    def calculate_pnl(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Calculate PnL."""
        effective_entry, effective_exit = self.apply_costs(entry_price, exit_price)
        pnl_pct = (effective_exit - effective_entry) / effective_entry * 100
        pnl_bps = pnl_pct * 100
        return pnl_bps, pnl_pct
    
    def generate_trades(self) -> List[Trade]:
        """Generate trades using Signal C logic."""
        trades = []
        vol_lookback = self.params['vol_lookback']
        vol_threshold = self.params['vol_spike_threshold']
        target_pct = self.params['target_pct']
        stop_pct = self.params['stop_pct']
        max_hold = self.params['max_hold_ticks']
        
        returns = np.diff(np.log(self.prices))
        rolling_vol = pd.Series(returns).rolling(vol_lookback).std().values
        
        i = vol_lookback + 1
        while i < len(self.prices) - 1:
            avg_vol = np.mean(rolling_vol[max(0, i - 40):i])
            current_vol = rolling_vol[i]
            
            if current_vol > vol_threshold * avg_vol and current_vol > 0 and not np.isnan(current_vol):
                if i > 0 and self.prices[i] > self.prices[i - 1]:
                    entry_price = self.prices[i]
                    entry_idx = i
                    entry_ts = self.timestamps[i]
                else:
                    i += 1
                    continue
                
                target_price = entry_price * (1 + target_pct / 100)
                stop_price = entry_price * (1 - stop_pct / 100)
                
                exit_idx = None
                exit_price = None
                exit_ts = None
                
                for j in range(i + 1, min(i + max_hold + 1, len(self.prices))):
                    if self.prices[j] >= target_price:
                        exit_idx = j
                        exit_price = target_price
                        exit_ts = self.timestamps[j]
                        break
                    elif self.prices[j] <= stop_price:
                        exit_idx = j
                        exit_price = stop_price
                        exit_ts = self.timestamps[j]
                        break
                
                if exit_idx is not None:
                    pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                    trade = Trade(
                        entry_price=entry_price,
                        exit_price=exit_price,
                        entry_idx=entry_idx,
                        exit_idx=exit_idx,
                        entry_timestamp=entry_ts,
                        exit_timestamp=exit_ts,
                        pnl_bps=pnl_bps,
                        pnl_pct=pnl_pct,
                        reason=f'vol_spike={current_vol / avg_vol:.2f}x',
                        vol_spike_ratio=current_vol / avg_vol if avg_vol > 0 else 1.0
                    )
                    trades.append(trade)
                    i = exit_idx + 1
                else:
                    i += 1
            else:
                i += 1
        
        self.trades = trades
        return trades


class RandomTimingControl:
    """Random timing baseline."""
    
    def __init__(self, df: pd.DataFrame, num_trades: int, params: Dict):
        self.df = df
        self.num_trades = num_trades
        self.params = params
        self.prices = df['close'].values
        self.timestamps = df['timestamp'].values
        self.trades = []
    
    def apply_costs(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        entry_cost_bps = self.params['costs_bps'] * 0.6
        exit_cost_bps = self.params['costs_bps'] * 0.4
        effective_entry = entry_price * (1 + entry_cost_bps / 10000)
        effective_exit = exit_price * (1 - exit_cost_bps / 10000)
        return effective_entry, effective_exit
    
    def calculate_pnl(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        effective_entry, effective_exit = self.apply_costs(entry_price, exit_price)
        pnl_pct = (effective_exit - effective_entry) / effective_entry * 100
        pnl_bps = pnl_pct * 100
        return pnl_bps, pnl_pct
    
    def generate_trades(self) -> List[Trade]:
        trades = []
        np.random.seed(999)
        
        max_hold = self.params['max_hold_ticks']
        target_pct = self.params['target_pct']
        stop_pct = self.params['stop_pct']
        
        for _ in range(self.num_trades):
            entry_idx = np.random.randint(0, max(1, len(self.prices) - 100))
            entry_price = self.prices[entry_idx]
            entry_ts = self.timestamps[entry_idx]
            
            target_price = entry_price * (1 + target_pct / 100)
            stop_price = entry_price * (1 - stop_pct / 100)
            
            exit_idx = None
            exit_price = None
            exit_ts = None
            
            for j in range(entry_idx + 1, min(entry_idx + max_hold + 1, len(self.prices))):
                if self.prices[j] >= target_price:
                    exit_idx = j
                    exit_price = target_price
                    exit_ts = self.timestamps[j]
                    break
                elif self.prices[j] <= stop_price:
                    exit_idx = j
                    exit_price = stop_price
                    exit_ts = self.timestamps[j]
                    break
            
            if exit_idx is not None:
                pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                trade = Trade(
                    entry_price=entry_price,
                    exit_price=exit_price,
                    entry_idx=entry_idx,
                    exit_idx=exit_idx,
                    entry_timestamp=entry_ts,
                    exit_timestamp=exit_ts,
                    pnl_bps=pnl_bps,
                    pnl_pct=pnl_pct,
                    reason='random'
                )
                trades.append(trade)
        
        self.trades = trades
        return trades


# =====================================================================
# ANALYSIS
# =====================================================================

def analyze_trades(trades: List[Trade], name: str) -> Dict:
    """Comprehensive trade analysis."""
    if not trades:
        return {
            'name': name,
            'sample_size': 0,
            'win_rate': 0,
            'avg_pnl_bps': 0,
            'avg_pnl_pct': 0,
            'total_pnl_bps': 0,
            'std_dev_bps': 0,
            'sharpe_ratio': 0,
            'max_win_bps': 0,
            'max_loss_bps': 0,
            'max_consecutive_losses': 0,
            'max_drawdown_bps': 0,
            'avg_duration_ticks': 0
        }
    
    wins = sum(1 for t in trades if t.is_win)
    pnl_bps = [t.pnl_bps for t in trades]
    
    cumsum = np.cumsum(pnl_bps)
    running_max = np.maximum.accumulate(cumsum)
    drawdown = cumsum - running_max
    max_drawdown = min(drawdown) if len(drawdown) > 0 else 0
    
    max_consec = 0
    current_consec = 0
    for t in trades:
        if not t.is_win:
            current_consec += 1
            max_consec = max(max_consec, current_consec)
        else:
            current_consec = 0
    
    returns = np.array(pnl_bps)
    sharpe = (np.mean(returns) / np.std(returns) * np.sqrt(252)) if np.std(returns) > 0 else 0
    
    return {
        'name': name,
        'sample_size': len(trades),
        'win_rate': round(wins / len(trades) * 100, 2),
        'avg_pnl_bps': round(np.mean(pnl_bps), 2),
        'avg_pnl_pct': round(np.mean(pnl_bps) / 100, 4),
        'total_pnl_bps': round(sum(pnl_bps), 2),
        'std_dev_bps': round(np.std(pnl_bps), 2),
        'sharpe_ratio': round(sharpe, 2),
        'max_win_bps': round(max(pnl_bps), 2),
        'max_loss_bps': round(min(pnl_bps), 2),
        'max_consecutive_losses': max_consec,
        'max_drawdown_bps': round(max_drawdown, 2),
        'avg_duration_ticks': round(np.mean([t.duration_ticks for t in trades]), 1)
    }


def analyze_regime_performance(trades: List[Trade], df: pd.DataFrame) -> Dict:
    """Analyze performance by volatility regime."""
    returns = np.diff(np.log(df['close'].values))
    realized_vol = pd.Series(returns).rolling(20).std().values * np.sqrt(252 * 24 * 60)
    
    vol_25 = np.nanpercentile(realized_vol, 25)
    vol_75 = np.nanpercentile(realized_vol, 75)
    
    results = {}
    
    for regime_name, threshold in [('high', vol_75), ('mid', vol_25), ('low', -np.inf)]:
        if regime_name == 'high':
            regime_idx = np.where(realized_vol > threshold)[0]
        elif regime_name == 'mid':
            regime_idx = np.where((realized_vol >= vol_25) & (realized_vol <= vol_75))[0]
        else:
            regime_idx = np.where(realized_vol < vol_25)[0]
        
        regime_trades = [t for t in trades if t.entry_idx in regime_idx]
        
        if regime_trades:
            wins = sum(1 for t in regime_trades if t.is_win)
            pnl_bps = [t.pnl_bps for t in regime_trades]
            
            results[regime_name] = {
                'sample_size': len(regime_trades),
                'win_rate': round(wins / len(regime_trades) * 100, 2),
                'avg_pnl_bps': round(np.mean(pnl_bps), 2),
                'std_dev_bps': round(np.std(pnl_bps), 2),
                'max_win_bps': round(max(pnl_bps), 2),
                'max_loss_bps': round(min(pnl_bps), 2),
                'total_pnl_bps': round(sum(pnl_bps), 2)
            }
        else:
            results[regime_name] = {
                'sample_size': 0,
                'win_rate': 0,
                'avg_pnl_bps': 0,
                'std_dev_bps': 0,
                'max_win_bps': 0,
                'max_loss_bps': 0,
                'total_pnl_bps': 0
            }
    
    return results


# =====================================================================
# MAIN
# =====================================================================

def main():
    print("=" * 100)
    print("PHASE 25 - VOLATILITY EXPANSION VALIDATION (Real Data)")
    print("=" * 100)
    
    # Load data
    print("\nLoading real Phase X BTC hourly data...")
    df_full = pd.read_csv('/Users/rrg/.openclaw/workspace/crypto_phase_x_BTC_hourly.csv')
    df_full['timestamp'] = pd.to_datetime(df_full['timestamp'])
    
    print(f"Full dataset: {len(df_full)} candles")
    print(f"Date range: {df_full['timestamp'].min()} to {df_full['timestamp'].max()}")
    
    # SPLIT DATA: First 50% = Phase 24, Second 50% = Phase 25 (out-of-sample)
    split_idx = len(df_full) // 2
    df_phase24 = df_full.iloc[:split_idx].reset_index(drop=True)
    df_phase25 = df_full.iloc[split_idx:].reset_index(drop=True)
    
    print(f"\nData split:")
    print(f"  Phase 24 (in-sample): {df_phase24['timestamp'].min()} to {df_phase24['timestamp'].max()} ({len(df_phase24)} candles)")
    print(f"  Phase 25 (out-of-sample): {df_phase25['timestamp'].min()} to {df_phase25['timestamp'].max()} ({len(df_phase25)} candles)")
    
    # =====================================================================
    # PHASE 24 BASELINE (reproduce known results)
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("PHASE 24 BASELINE (for comparison)")
    print("=" * 100)
    
    signal_c_p24 = SignalC_VolatilityExpansion(df_phase24, SIGNAL_C_PARAMS)
    trades_p24 = signal_c_p24.generate_trades()
    analysis_p24 = analyze_trades(trades_p24, 'Signal C Phase 24')
    
    print(f"\nPhase 24 results:")
    print(f"  Trades: {analysis_p24['sample_size']}")
    print(f"  Win rate: {analysis_p24['win_rate']}%")
    print(f"  Avg PnL/trade: {analysis_p24['avg_pnl_bps']:.2f} bps")
    print(f"  Edge vs market: {analysis_p24['max_drawdown_bps']:.2f} bps (max drawdown)")
    
    # =====================================================================
    # PHASE 25 OUT-OF-SAMPLE TEST
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("PHASE 25 OUT-OF-SAMPLE TEST")
    print("=" * 100)
    print("\nApplying Signal C (ZERO parameter tuning)...")
    
    signal_c_p25 = SignalC_VolatilityExpansion(df_phase25, SIGNAL_C_PARAMS)
    trades_p25 = signal_c_p25.generate_trades()
    analysis_p25 = analyze_trades(trades_p25, 'Signal C Phase 25')
    
    print(f"\nPhase 25 results:")
    print(f"  Trades: {analysis_p25['sample_size']}")
    print(f"  Win rate: {analysis_p25['win_rate']}%")
    print(f"  Avg PnL/trade: {analysis_p25['avg_pnl_bps']:.2f} bps")
    print(f"  Std deviation: {analysis_p25['std_dev_bps']:.2f} bps")
    print(f"  Max drawdown: {analysis_p25['max_drawdown_bps']:.2f} bps")
    
    # =====================================================================
    # REGIME ANALYSIS
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("REGIME ANALYSIS (Phase 25)")
    print("=" * 100)
    
    regime_analysis = analyze_regime_performance(trades_p25, df_phase25)
    
    for regime_name in ['high', 'mid', 'low']:
        r = regime_analysis[regime_name]
        print(f"\n{regime_name.upper()} volatility:")
        print(f"  Trades: {r['sample_size']}")
        print(f"  Win rate: {r['win_rate']}%")
        print(f"  Avg PnL/trade: {r['avg_pnl_bps']:.2f} bps")
    
    # =====================================================================
    # RANDOM CONTROL
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("RANDOM TIMING CONTROL")
    print("=" * 100)
    
    random_control = RandomTimingControl(df_phase25, max(len(trades_p25), 10), SIGNAL_C_PARAMS)
    random_trades = random_control.generate_trades()
    random_analysis = analyze_trades(random_trades, 'Random Baseline')
    
    print(f"\nRandom baseline ({len(random_trades)} trades):")
    print(f"  Win rate: {random_analysis['win_rate']}%")
    print(f"  Avg PnL/trade: {random_analysis['avg_pnl_bps']:.2f} bps")
    
    edge_vs_random = analysis_p25['avg_pnl_bps'] - random_analysis['avg_pnl_bps']
    print(f"\nSignal C edge vs Random: {edge_vs_random:.2f} bps")
    
    # =====================================================================
    # RESULTS TABLE
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("RESULTS COMPARISON")
    print("=" * 100)
    
    phase24_baseline = 132.72  # From phase24_final_results.json
    phase24_edge_vs_random = 38.32
    
    print(f"\n{'Metric':<35} {'Phase 24':<20} {'Phase 25':<20} {'Delta':<20} {'Status':<15}")
    print("-" * 110)
    
    metrics = {
        'Sample Size': (analysis_p24['sample_size'], analysis_p25['sample_size']),
        'Win Rate (%)': (85.71, analysis_p25['win_rate']),
        'Avg PnL/Trade (bps)': (phase24_baseline, analysis_p25['avg_pnl_bps']),
        'Edge vs Random (bps)': (phase24_edge_vs_random, edge_vs_random),
        'Std Dev (bps)': (139.83, analysis_p25['std_dev_bps']),
        'Max Drawdown (bps)': (209.79, analysis_p25['max_drawdown_bps'])
    }
    
    for metric_name, (p24, p25) in metrics.items():
        delta = p25 - p24
        if 'Edge' in metric_name or 'Avg PnL' in metric_name:
            status = "✓" if abs(delta) < 30 else "⚠" if abs(delta) < 100 else "✗"
        else:
            status = "✓" if abs(delta) < 50 else "⚠" if abs(delta) < 100 else "✗"
        print(f"{metric_name:<35} {p24:<20.2f} {p25:<20.2f} {delta:<20.2f} {status:<15}")
    
    # =====================================================================
    # VERDICT
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("VERDICT")
    print("=" * 100)
    
    q1 = "YES" if analysis_p25['avg_pnl_bps'] > 0 else "NO"
    q2 = "YES" if analysis_p25['avg_pnl_bps'] > 20 else "NO"
    q3 = "YES" if all(regime_analysis.get(r, {}).get('avg_pnl_bps', -1000) > 0 for r in ['high', 'mid', 'low']) else "NO"
    q4 = "YES" if edge_vs_random > 5 else "NO"
    
    print(f"\n1. Does signal produce positive edge? {q1}")
    print(f"   Phase 25 edge: {analysis_p25['avg_pnl_bps']:.2f} bps")
    
    print(f"\n2. Does edge remain >20 bps? {q2}")
    print(f"   Phase 24: {phase24_baseline:.2f} bps vs Phase 25: {analysis_p25['avg_pnl_bps']:.2f} bps")
    print(f"   Degradation: {phase24_baseline - analysis_p25['avg_pnl_bps']:.2f} bps")
    
    print(f"\n3. Is performance stable across regimes? {q3}")
    for regime_name in ['high', 'mid', 'low']:
        r = regime_analysis[regime_name]
        print(f"   {regime_name}: {r['avg_pnl_bps']:.2f} bps")
    
    print(f"\n4. Does it outperform random consistently? {q4}")
    print(f"   Signal vs Random: {edge_vs_random:.2f} bps")
    
    # Determine verdict
    if q1 == "YES" and q2 == "YES" and q3 == "YES" and analysis_p25['sample_size'] >= 10:
        verdict = "REAL"
        confidence = "HIGH"
        readiness = 85
        action = "DEPLOY"
    elif q1 == "YES" and q4 == "YES" and analysis_p25['sample_size'] >= 5:
        verdict = "FRAGILE"
        confidence = "MEDIUM"
        readiness = 45
        action = "REFINE"
    else:
        verdict = "FAKE"
        confidence = "HIGH"
        readiness = 0
        action = "DISCARD"
    
    print(f"\n{'='*100}")
    print(f"Signal Status: {verdict}")
    print(f"Confidence: {confidence}")
    print(f"Production Readiness: {readiness}%")
    print(f"Action: {action}")
    
    # Save results
    results = {
        'phase': 25,
        'title': 'Volatility Expansion Validation (Out-of-Sample)',
        'date_run': datetime.now().isoformat(),
        'data_split': {
            'phase24': {
                'date_start': df_phase24['timestamp'].min().isoformat(),
                'date_end': df_phase24['timestamp'].max().isoformat(),
                'candles': len(df_phase24)
            },
            'phase25': {
                'date_start': df_phase25['timestamp'].min().isoformat(),
                'date_end': df_phase25['timestamp'].max().isoformat(),
                'candles': len(df_phase25)
            }
        },
        'results': {
            'phase24': analysis_p24,
            'phase25': analysis_p25,
            'random_baseline': random_analysis,
            'edge_vs_random_bps': edge_vs_random,
            'regime_performance': regime_analysis
        },
        'answers': {
            'q1_positive_edge': q1,
            'q2_edge_above_20bps': q2,
            'q3_stable_across_regimes': q3,
            'q4_outperforms_random': q4
        },
        'verdict': {
            'status': verdict,
            'confidence': confidence,
            'production_readiness': readiness,
            'recommended_action': action
        }
    }
    
    output_path = Path('/Users/rrg/.openclaw/workspace/phase25_final_validation.json')
    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")


if __name__ == '__main__':
    main()
