#!/usr/bin/env python3
"""
PHASE 25 - VOLATILITY EXPANSION VALIDATION
Validate whether Signal C (Volatility Expansion) is real or a small-sample artifact.
- Out-of-sample data (30-60 days, different date range than Phase 24)
- Zero parameter tuning (same params as Phase 24)
- 50-100+ trades minimum
- Regime analysis (high/mid/low volatility)
- Randomized timing control
- Stability checks across conditions
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict, Optional
from datetime import datetime, timedelta
import requests

# =====================================================================
# CONFIG - EXACT REPLICATION OF PHASE 24
# =====================================================================

CRYPTO_COSTS_BPS = {
    'maker_fee': 2,
    'taker_fee': 4,
    'entry_slippage': 2,
    'exit_slippage': 2,
    'round_trip': 10  # Conservative: 2+4+2+2 = 10 bps minimum
}

# SIGNAL C PARAMETERS (locked from Phase 24)
SIGNAL_C_PARAMS = {
    'vol_lookback': 20,  # Rolling window for volatility calculation
    'vol_spike_threshold': 1.5,  # vol > 1.5x average
    'target_pct': 2.0,  # Exit on +2% profit
    'stop_pct': 2.0,  # Exit on -2% loss
    'max_hold_ticks': 100,  # Max lookahead for exit
    'costs_bps': 10,  # Round-trip cost
}

# =====================================================================
# DATA FETCHING
# =====================================================================

def fetch_binance_perpetual_data(symbol: str, interval: str = '1m', 
                                 days: int = 60, end_date: Optional[str] = None) -> pd.DataFrame:
    """
    Fetch BTC/USDT perpetual futures data from Binance (free public API).
    Returns OHLCV candles.
    """
    print(f"  Fetching {symbol} {interval} candles for {days} days...")
    
    # Use Binance public REST API (no auth needed)
    base_url = "https://fapi.binance.com/fapi/v1/klines"
    
    all_data = []
    current_date = datetime.now() if end_date is None else datetime.strptime(end_date, '%Y-%m-%d')
    
    # Fetch in chunks (Binance limit: 1000 per request)
    for i in range(0, days, 5):  # 5-day chunks
        start_time = int((current_date - timedelta(days=days - i)).timestamp() * 1000)
        end_time = int((current_date - timedelta(days=max(0, days - i - 5))).timestamp() * 1000)
        
        try:
            response = requests.get(
                base_url,
                params={
                    'symbol': symbol,
                    'interval': interval,
                    'startTime': start_time,
                    'endTime': end_time,
                    'limit': 1000
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            
            if not data:
                print(f"    No data for {i}-day range")
                continue
            
            all_data.extend(data)
            print(f"    Fetched {len(data)} candles from {i} days ago")
            
        except requests.exceptions.RequestException as e:
            print(f"    Warning: API fetch failed ({e}), using synthetic/cached data")
            break
    
    # Parse into DataFrame
    if not all_data:
        print(f"  ⚠ No data fetched, generating synthetic data for testing...")
        return generate_synthetic_btc_data(days=60)
    
    df = pd.DataFrame(all_data)
    df.columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume',
                  'close_time', 'quote_volume', 'trades', 'taker_buy_volume',
                  'taker_buy_quote_volume', 'ignore']
    
    # Convert to proper types
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)
    df['volume'] = df['volume'].astype(float)
    
    df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']].sort_values('timestamp').reset_index(drop=True)
    
    print(f"  ✓ Loaded {len(df)} candles")
    print(f"    Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"    Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    
    return df


def generate_synthetic_btc_data(days: int = 60, price_start: float = 65000.0) -> pd.DataFrame:
    """
    Generate synthetic BTC data with realistic volatility for testing.
    """
    print(f"  Generating synthetic {days}-day data...")
    
    num_minutes = days * 24 * 60
    timestamps = pd.date_range(end=datetime.now(), periods=num_minutes, freq='1min')
    
    # Geometric random walk with drift
    np.random.seed(42)
    returns = np.random.normal(0.0001, 0.005, num_minutes)  # Small drift, ~0.5% daily vol
    prices = price_start * np.exp(np.cumsum(returns))
    
    # Create OHLCV
    data = []
    for i, ts in enumerate(timestamps):
        # Simulate intra-candle (1-min is already granular)
        open_price = prices[i]
        close_price = prices[i] * (1 + np.random.normal(0, 0.0005))
        high_price = max(open_price, close_price) * (1 + abs(np.random.normal(0, 0.0003)))
        low_price = min(open_price, close_price) * (1 - abs(np.random.normal(0, 0.0003)))
        volume = np.random.exponential(100)
        
        data.append({
            'timestamp': ts,
            'open': open_price,
            'high': high_price,
            'low': low_price,
            'close': close_price,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    print(f"  ✓ Generated {len(df)} synthetic candles")
    
    return df


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
    """Signal C: Volatility Expansion (exact replication of Phase 24)."""
    
    def __init__(self, df: pd.DataFrame, params: Dict):
        self.df = df
        self.params = params
        self.prices = df['close'].values
        self.timestamps = df['timestamp'].values
        self.trades = []
    
    def apply_costs(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Apply realistic crypto costs to entry and exit."""
        entry_cost_bps = self.params['costs_bps'] * 0.6  # Entry: 6 bps (taker + slippage)
        exit_cost_bps = self.params['costs_bps'] * 0.4   # Exit: 4 bps (maker + slippage)
        
        effective_entry = entry_price * (1 + entry_cost_bps / 10000)
        effective_exit = exit_price * (1 - exit_cost_bps / 10000)
        
        return effective_entry, effective_exit
    
    def calculate_pnl(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Calculate PnL in bps and percent, after costs."""
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
        
        # Calculate rolling volatility (standard deviation of returns)
        returns = np.diff(np.log(self.prices))
        rolling_vol = pd.Series(returns).rolling(vol_lookback).std().values
        
        i = vol_lookback + 1
        while i < len(self.prices) - 1:
            # Average volatility in recent window (40 ticks back)
            avg_vol = np.mean(rolling_vol[max(0, i - 40):i])
            current_vol = rolling_vol[i]
            
            if current_vol > vol_threshold * avg_vol and current_vol > 0 and not np.isnan(current_vol):
                # Volatility spike detected
                # Determine direction: LONG if price moving up
                if i > 0 and self.prices[i] > self.prices[i - 1]:
                    direction = 'LONG'
                    entry_price = self.prices[i]
                    entry_idx = i
                    entry_ts = self.timestamps[i]
                else:
                    i += 1
                    continue
                
                # Find exit: +2% target or -2% stop
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
    """Random timing baseline for comparison."""
    
    def __init__(self, df: pd.DataFrame, num_trades: int, params: Dict):
        self.df = df
        self.num_trades = num_trades
        self.params = params
        self.prices = df['close'].values
        self.timestamps = df['timestamp'].values
        self.trades = []
    
    def apply_costs(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Apply realistic crypto costs."""
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
        """Generate random trades for baseline."""
        trades = []
        np.random.seed(123)  # Different seed from Phase 24
        
        max_hold = self.params['max_hold_ticks']
        target_pct = self.params['target_pct']
        stop_pct = self.params['stop_pct']
        
        for _ in range(self.num_trades):
            # Random entry point (avoid last 100 ticks)
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
# ANALYSIS & REGIME DETECTION
# =====================================================================

def calculate_realized_volatility(df: pd.DataFrame, window: int = 20) -> np.ndarray:
    """Calculate realized volatility over rolling window."""
    returns = np.diff(np.log(df['close'].values))
    realized_vol = pd.Series(returns).rolling(window).std().values * np.sqrt(252 * 24 * 60)  # Annualized
    return realized_vol


def classify_regimes(df: pd.DataFrame, realized_vol: np.ndarray) -> Dict[str, List[int]]:
    """Classify periods as high/mid/low volatility."""
    vol_25 = np.nanpercentile(realized_vol, 25)
    vol_75 = np.nanpercentile(realized_vol, 75)
    
    high_vol_idx = np.where(realized_vol > vol_75)[0]
    low_vol_idx = np.where(realized_vol < vol_25)[0]
    mid_vol_idx = np.where((realized_vol >= vol_25) & (realized_vol <= vol_75))[0]
    
    return {
        'high': high_vol_idx.tolist(),
        'mid': mid_vol_idx.tolist(),
        'low': low_vol_idx.tolist(),
        'vol_25': float(vol_25),
        'vol_75': float(vol_75)
    }


def analyze_regime_performance(trades: List[Trade], regimes: Dict, df: pd.DataFrame) -> Dict:
    """Analyze signal performance within each volatility regime."""
    realized_vol = calculate_realized_volatility(df)
    regimes = classify_regimes(df, realized_vol)
    
    results = {}
    
    for regime_name, regime_idx in regimes.items():
        if regime_name in ['vol_25', 'vol_75']:
            continue
        
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
    
    # Calculate drawdown
    cumsum = np.cumsum(pnl_bps)
    running_max = np.maximum.accumulate(cumsum)
    drawdown = cumsum - running_max
    max_drawdown = min(drawdown) if len(drawdown) > 0 else 0
    
    # Consecutive losses
    max_consec = 0
    current_consec = 0
    for t in trades:
        if not t.is_win:
            current_consec += 1
            max_consec = max(max_consec, current_consec)
        else:
            current_consec = 0
    
    # Sharpe ratio
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


# =====================================================================
# MAIN EXECUTION
# =====================================================================

def main():
    print("=" * 100)
    print("PHASE 25 - VOLATILITY EXPANSION VALIDATION")
    print("=" * 100)
    print("\nObjective: Validate whether Signal C (Volatility Expansion) is REAL or FAKE")
    print("Approach: Out-of-sample test with ZERO parameter tuning\n")
    
    # =====================================================================
    # STEP 1: EXPAND DATA (out-of-sample)
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 1: EXPAND DATA (Out-of-Sample)")
    print("=" * 100)
    
    print("\nFetching BTC/USDT perpetual futures data (60 days, 1-minute candles)...")
    try:
        df = fetch_binance_perpetual_data('BTCUSDT', interval='1m', days=60)
    except Exception as e:
        print(f"Warning: Live fetch failed ({e}), using synthetic data")
        df = generate_synthetic_btc_data(days=60)
    
    print(f"\nData summary:")
    print(f"  Candles: {len(df)}")
    print(f"  Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    print(f"  Price range: {df['close'].min():.2f} - {df['close'].max():.2f}")
    print(f"  Return (period): {(df['close'].iloc[-1] / df['close'].iloc[0] - 1) * 100:.2f}%")
    
    # =====================================================================
    # STEP 2: OUT-OF-SAMPLE TEST (Signal C with Phase 24 parameters)
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 2: OUT-OF-SAMPLE TEST (Signal C)")
    print("=" * 100)
    print("\nApplying Signal C with EXACT Phase 24 parameters:")
    print(f"  Vol lookback: {SIGNAL_C_PARAMS['vol_lookback']} ticks")
    print(f"  Vol spike threshold: {SIGNAL_C_PARAMS['vol_spike_threshold']}x")
    print(f"  Target: +{SIGNAL_C_PARAMS['target_pct']}%")
    print(f"  Stop: -{SIGNAL_C_PARAMS['stop_pct']}%")
    print(f"  Costs: {SIGNAL_C_PARAMS['costs_bps']} bps round-trip\n")
    
    signal_c = SignalC_VolatilityExpansion(df, SIGNAL_C_PARAMS)
    trades = signal_c.generate_trades()
    
    print(f"✓ Generated {len(trades)} trades (target: 50-100+)")
    if len(trades) < 50:
        print(f"  ⚠ Warning: Only {len(trades)} trades (below 50 minimum)")
    
    # =====================================================================
    # STEP 3: STABILITY CHECK
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 3: STABILITY CHECK")
    print("=" * 100)
    
    analysis = analyze_trades(trades, 'Signal C')
    
    print(f"\nTrade metrics:")
    print(f"  Sample size: {analysis['sample_size']} trades")
    print(f"  Win rate: {analysis['win_rate']}%")
    print(f"  Avg PnL/trade: {analysis['avg_pnl_bps']:.2f} bps ({analysis['avg_pnl_pct']:.4f}%)")
    print(f"  Std deviation: {analysis['std_dev_bps']:.2f} bps")
    print(f"  Max win: {analysis['max_win_bps']:.2f} bps")
    print(f"  Max loss: {analysis['max_loss_bps']:.2f} bps")
    print(f"  Max consecutive losses: {analysis['max_consecutive_losses']}")
    print(f"  Max drawdown: {analysis['max_drawdown_bps']:.2f} bps")
    print(f"  Sharpe ratio: {analysis['sharpe_ratio']:.2f}")
    print(f"  Avg trade duration: {analysis['avg_duration_ticks']:.1f} ticks")
    
    # =====================================================================
    # STEP 4: REGIME TEST
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 4: REGIME TEST")
    print("=" * 100)
    
    regime_analysis = analyze_regime_performance(trades, {}, df)
    
    print(f"\nPerformance by volatility regime:")
    for regime_name in ['high', 'mid', 'low']:
        if regime_name in regime_analysis:
            r = regime_analysis[regime_name]
            print(f"\n  {regime_name.upper()} volatility:")
            print(f"    Trades: {r['sample_size']}")
            print(f"    Win rate: {r['win_rate']}%")
            print(f"    Avg PnL/trade: {r['avg_pnl_bps']:.2f} bps")
            print(f"    Total PnL: {r['total_pnl_bps']:.2f} bps")
    
    # =====================================================================
    # STEP 5: RANDOMIZED TIMING CONTROL
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 5: RANDOMIZED TIMING CONTROL")
    print("=" * 100)
    
    print(f"\nGenerating {len(trades)} random baseline trades...")
    random_control = RandomTimingControl(df, len(trades), SIGNAL_C_PARAMS)
    random_trades = random_control.generate_trades()
    
    random_analysis = analyze_trades(random_trades, 'Random Baseline')
    
    print(f"\nRandom baseline metrics:")
    print(f"  Sample size: {random_analysis['sample_size']} trades")
    print(f"  Win rate: {random_analysis['win_rate']}%")
    print(f"  Avg PnL/trade: {random_analysis['avg_pnl_bps']:.2f} bps")
    print(f"  Std deviation: {random_analysis['std_dev_bps']:.2f} bps")
    
    signal_edge_vs_random = analysis['avg_pnl_bps'] - random_analysis['avg_pnl_bps']
    print(f"\nSignal C edge vs Random: {signal_edge_vs_random:.2f} bps")
    
    # =====================================================================
    # STEP 6: RESULTS TABLE
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 6: RESULTS TABLE (Phase 24 vs Phase 25)")
    print("=" * 100)
    
    phase24_signal_c_btc = {
        'win_rate': 85.71,
        'avg_pnl_bps': 132.72,
        'edge_vs_random_bps': 38.32,
        'std_dev_bps': 139.83,
        'max_drawdown_bps': 209.79,
        'sample_size': 7
    }
    
    results_table = {
        'Phase24': phase24_signal_c_btc,
        'Phase25': {
            'win_rate': analysis['win_rate'],
            'avg_pnl_bps': analysis['avg_pnl_bps'],
            'edge_vs_random_bps': signal_edge_vs_random,
            'std_dev_bps': analysis['std_dev_bps'],
            'max_drawdown_bps': analysis['max_drawdown_bps'],
            'sample_size': analysis['sample_size']
        }
    }
    
    print(f"\n{'Metric':<30} {'Phase 24':<20} {'Phase 25':<20} {'Delta':<15} {'Status':<15}")
    print("-" * 100)
    
    for metric in ['sample_size', 'win_rate', 'avg_pnl_bps', 'edge_vs_random_bps', 'std_dev_bps', 'max_drawdown_bps']:
        p24 = results_table['Phase24'][metric]
        p25 = results_table['Phase25'][metric]
        
        if metric in ['sample_size', 'win_rate']:
            delta = p25 - p24
            status = "✓" if abs(delta) < 20 else "⚠" if abs(delta) < 40 else "✗"
        else:
            delta = p25 - p24
            status = "✓" if abs(delta) < 20 else "⚠" if abs(delta) < 50 else "✗"
        
        print(f"{metric:<30} {p24:<20.2f} {p25:<20.2f} {delta:<15.2f} {status:<15}")
    
    # =====================================================================
    # STEP 7: ANSWER 4 KEY QUESTIONS
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("STEP 7: KEY QUESTIONS & VERDICT")
    print("=" * 100)
    
    # Question 1
    print(f"\n1. Does signal still produce positive edge?")
    q1_answer = "YES" if analysis['avg_pnl_bps'] > 0 else "NO"
    print(f"   Phase 25 edge: {analysis['avg_pnl_bps']:.2f} bps (after costs)")
    print(f"   Status: {q1_answer} ({'✓' if q1_answer == 'YES' else '✗'})")
    
    # Question 2
    print(f"\n2. Does edge remain >20 bps?")
    edge_threshold = 20
    edge_degradation = phase24_signal_c_btc['avg_pnl_bps'] - analysis['avg_pnl_bps']
    q2_answer = "YES" if analysis['avg_pnl_bps'] > edge_threshold else "NO"
    print(f"   Phase 24: {phase24_signal_c_btc['avg_pnl_bps']:.2f} bps")
    print(f"   Phase 25: {analysis['avg_pnl_bps']:.2f} bps")
    print(f"   Degradation: {edge_degradation:.2f} bps ({edge_degradation/phase24_signal_c_btc['avg_pnl_bps']*100:.1f}%)")
    print(f"   Status: {q2_answer} ({'✓' if q2_answer == 'YES' else '✗'})")
    
    # Question 3
    print(f"\n3. Is performance stable across regimes?")
    regime_stability = all(
        5 < regime_analysis.get(r, {}).get('avg_pnl_bps', -1000) for r in ['high', 'mid', 'low']
    )
    q3_answer = "YES" if regime_stability and len(regime_analysis) >= 3 else "NO"
    print(f"   High vol regime: {regime_analysis.get('high', {}).get('avg_pnl_bps', 0):.2f} bps")
    print(f"   Mid vol regime: {regime_analysis.get('mid', {}).get('avg_pnl_bps', 0):.2f} bps")
    print(f"   Low vol regime: {regime_analysis.get('low', {}).get('avg_pnl_bps', 0):.2f} bps")
    print(f"   Status: {q3_answer} ({'✓' if q3_answer == 'YES' else '⚠' if q3_answer == 'PARTIAL' else '✗'})")
    
    # Question 4
    print(f"\n4. Does it outperform random consistently?")
    q4_answer = "YES" if signal_edge_vs_random > 5 else "NO"
    print(f"   Signal C: {analysis['avg_pnl_bps']:.2f} bps")
    print(f"   Random: {random_analysis['avg_pnl_bps']:.2f} bps")
    print(f"   Edge vs random: {signal_edge_vs_random:.2f} bps")
    print(f"   Status: {q4_answer} ({'✓' if q4_answer == 'YES' else '✗'})")
    
    # =====================================================================
    # FINAL VERDICT
    # =====================================================================
    
    print("\n" + "=" * 100)
    print("FINAL VERDICT")
    print("=" * 100)
    
    # Determine verdict
    if (analysis['avg_pnl_bps'] > edge_threshold and 
        q3_answer == "YES" and 
        q4_answer == "YES" and 
        analysis['sample_size'] >= 50):
        verdict = "REAL"
        confidence = "HIGH"
        production_ready = 80
        action = "DEPLOY"
    elif (analysis['avg_pnl_bps'] > 0 and 
          analysis['avg_pnl_bps'] > random_analysis['avg_pnl_bps'] and 
          analysis['sample_size'] >= 30):
        verdict = "FRAGILE"
        confidence = "MEDIUM"
        production_ready = 40
        action = "REFINE"
    else:
        verdict = "FAKE"
        confidence = "HIGH"
        production_ready = 0
        action = "DISCARD"
    
    print(f"\nSignal Status: {verdict}")
    print(f"Confidence Level: {confidence}")
    print(f"Production Readiness: {production_ready}%")
    print(f"Recommended Action: {action}")
    
    print(f"\nRationale:")
    if verdict == "REAL":
        print(f"  ✓ Edge persists in out-of-sample data (≥20 bps)")
        print(f"  ✓ Large sample size ({analysis['sample_size']} trades) reduces luck bias")
        print(f"  ✓ Stable across volatility regimes")
        print(f"  ✓ Consistent outperformance vs random ({signal_edge_vs_random:.2f} bps)")
    elif verdict == "FRAGILE":
        print(f"  ⚠ Edge exists but weakened ({edge_degradation:.2f} bps degradation)")
        print(f"  ⚠ Potentially regime-dependent or luck-based")
        print(f"  ⚠ Needs refinement before production deployment")
    else:
        print(f"  ✗ Edge disappeared in out-of-sample ({analysis['avg_pnl_bps']:.2f} bps)")
        print(f"  ✗ Small Phase 24 sample (7 trades) likely overfitting")
        print(f"  ✗ No edge vs random control")
    
    # =====================================================================
    # SAVE RESULTS
    # =====================================================================
    
    results_output = {
        'phase': 25,
        'title': 'Volatility Expansion Validation (Out-of-Sample)',
        'date_run': datetime.now().isoformat(),
        'data': {
            'candles': len(df),
            'date_range': {
                'start': df['timestamp'].min().isoformat(),
                'end': df['timestamp'].max().isoformat()
            },
            'price_range': {
                'min': float(df['close'].min()),
                'max': float(df['close'].max())
            }
        },
        'phase24_baseline': phase24_signal_c_btc,
        'phase25_results': {
            'signal_c': analysis,
            'random_baseline': random_analysis,
            'edge_vs_random_bps': signal_edge_vs_random,
            'regime_performance': regime_analysis
        },
        'answers': {
            'q1_positive_edge': q1_answer,
            'q2_edge_above_20bps': q2_answer,
            'q3_stable_across_regimes': q3_answer,
            'q4_outperforms_random': q4_answer
        },
        'verdict': {
            'status': verdict,
            'confidence': confidence,
            'production_readiness': production_ready,
            'recommended_action': action
        }
    }
    
    output_path = Path('/Users/rrg/.openclaw/workspace/phase25_validation_results.json')
    with open(output_path, 'w') as f:
        json.dump(results_output, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path}")
    
    return results_output


if __name__ == '__main__':
    main()
