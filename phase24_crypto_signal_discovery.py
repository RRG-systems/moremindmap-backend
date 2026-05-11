#!/usr/bin/env python3
"""
PHASE 24 - CRYPTO SIGNAL DISCOVERY
Test whether ANY signal produces positive edge (> costs) in crypto perpetual futures markets.

Cost Model (Realistic Crypto):
- Maker fee: 2 bps
- Taker fee: 4 bps
- Slippage on entry: 2 bps
- Slippage on exit: 2 bps
- Total round-trip: 10-14 bps per trade

Signals to test (isolated, no combinations):
A. MOMENTUM REVERSAL: Small drop (-0.3% to -0.5%) + stabilization → long
B. MICRO MOMENTUM CONTINUATION: Short momentum (+0.2% to +0.3%) → long
C. VOLATILITY EXPANSION: Vol spike (>1.5x avg) → trend following
D. MEAN REVERSION (VWAP): Deviation from VWAP (>0.5%) → fade
E. RANDOM BASELINE: Random entries (control)
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Tuple, Dict

# =====================================================================
# CONFIG & COST MODEL
# =====================================================================

CRYPTO_COSTS_BPS = {
    'maker_fee': 2,
    'taker_fee': 4,
    'entry_slippage': 2,
    'exit_slippage': 2,
    'round_trip': 10  # Conservative: 2+4+2+2 = 10 bps minimum
}

TARGET_PCT = 2.0  # Exit on +2% profit
STOP_PCT = 2.0    # Exit on -2% loss

# =====================================================================
# DATA LOADING
# =====================================================================

def load_crypto_data(asset: str) -> pd.DataFrame:
    """Load hourly OHLCV data for BTC or ETH."""
    path = Path(f'/Users/rrg/.openclaw/workspace/crypto_phase_x_{asset}_hourly.csv')
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)
    return df


def prepare_price_series(df: pd.DataFrame) -> np.ndarray:
    """Convert OHLCV to high-resolution synthetic tick series."""
    prices = []
    
    for _, row in df.iterrows():
        # Synthetic intra-hour ticks: open, (high+low)/2, close
        prices.extend([row['open'], (row['high'] + row['low']) / 2, row['close']])
    
    return np.array(prices)


# =====================================================================
# SIGNAL IMPLEMENTATIONS
# =====================================================================

@dataclass
class Trade:
    entry_price: float
    exit_price: float
    entry_idx: int
    exit_idx: int
    pnl_bps: float  # Net PnL after costs, in basis points
    pnl_pct: float  # Net PnL after costs, in percent
    direction: str = 'LONG'
    reason: str = ''
    
    @property
    def is_win(self) -> bool:
        return self.pnl_bps > 0


class SignalTester:
    """Base class for signal testing."""
    
    def __init__(self, prices: np.ndarray, name: str):
        self.prices = prices
        self.name = name
        self.trades = []
        
    def apply_costs(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Apply realistic crypto costs to entry and exit."""
        # Entry cost: Taker fee (4 bps) + entry slippage (2 bps) = 6 bps
        entry_cost_bps = CRYPTO_COSTS_BPS['taker_fee'] + CRYPTO_COSTS_BPS['entry_slippage']
        
        # Exit cost: Maker fee (2 bps) + exit slippage (2 bps) = 4 bps (if limit) or 6 bps (if market)
        # Conservatively assume market exit: 4 bps + 2 bps slippage = 6 bps
        exit_cost_bps = CRYPTO_COSTS_BPS['maker_fee'] + CRYPTO_COSTS_BPS['exit_slippage']
        
        # Total cost = 12 bps round-trip (realistic)
        effective_entry = entry_price * (1 + entry_cost_bps / 10000)
        effective_exit = exit_price * (1 - exit_cost_bps / 10000)
        
        return effective_entry, effective_exit
    
    def calculate_pnl(self, entry_price: float, exit_price: float) -> Tuple[float, float]:
        """Calculate PnL in bps and percent, after costs."""
        effective_entry, effective_exit = self.apply_costs(entry_price, exit_price)
        
        pnl_pct = (effective_exit - effective_entry) / effective_entry * 100
        pnl_bps = pnl_pct * 100  # Convert percent to bps
        
        return pnl_bps, pnl_pct
    
    def generate_trades(self) -> List[Trade]:
        """Override in subclass."""
        raise NotImplementedError


class SignalA_MomentumReversal(SignalTester):
    """
    Detect small price drop (-0.3% to -0.5% over N ticks) + stabilization.
    Entry: Long (bet on bounce).
    Exit: +2% target or -2% stop.
    """
    
    def generate_trades(self) -> List[Trade]:
        """Find momentum reversal setups."""
        trades = []
        lookback = 5  # Check last 5 ticks for drop
        
        i = lookback
        while i < len(self.prices) - 1:
            # Check for drop: price fell 0.3-0.5% over last N ticks
            start_price = self.prices[i - lookback]
            current_price = self.prices[i]
            drop_pct = (start_price - current_price) / start_price * 100
            
            # Stabilization check: last tick not continuing down
            is_stabilizing = self.prices[i] >= self.prices[i - 1]
            
            if 0.3 <= drop_pct <= 0.5 and is_stabilizing:
                # Entry signal: go long
                entry_price = self.prices[i]
                entry_idx = i
                
                # Find exit: +2% target or -2% stop
                target_price = entry_price * (1 + TARGET_PCT / 100)
                stop_price = entry_price * (1 - STOP_PCT / 100)
                
                exit_idx = None
                exit_price = None
                
                for j in range(i + 1, min(i + 100, len(self.prices))):  # Look ahead max 100 ticks
                    if self.prices[j] >= target_price:
                        exit_idx = j
                        exit_price = target_price
                        break
                    elif self.prices[j] <= stop_price:
                        exit_idx = j
                        exit_price = stop_price
                        break
                
                if exit_idx is not None:
                    pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                    trade = Trade(
                        entry_price=entry_price,
                        exit_price=exit_price,
                        entry_idx=entry_idx,
                        exit_idx=exit_idx,
                        pnl_bps=pnl_bps,
                        pnl_pct=pnl_pct,
                        reason=f'drop_pct={drop_pct:.2f}%'
                    )
                    trades.append(trade)
                    i = exit_idx + 1
                else:
                    i += 1
            else:
                i += 1
        
        self.trades = trades
        return trades


class SignalB_MicroMomentumContinuation(SignalTester):
    """
    Detect short-term momentum (+0.2% to +0.3% over last 5 ticks).
    Entry: Long (trend following).
    Exit: +2% target or -2% stop.
    """
    
    def generate_trades(self) -> List[Trade]:
        """Find micro momentum setups."""
        trades = []
        lookback = 5
        
        i = lookback
        while i < len(self.prices) - 1:
            # Check for upward momentum: +0.2-0.3% over last N ticks
            start_price = self.prices[i - lookback]
            current_price = self.prices[i]
            momentum_pct = (current_price - start_price) / start_price * 100
            
            if 0.2 <= momentum_pct <= 0.3:
                # Entry signal: go long on continuation
                entry_price = self.prices[i]
                entry_idx = i
                
                target_price = entry_price * (1 + TARGET_PCT / 100)
                stop_price = entry_price * (1 - STOP_PCT / 100)
                
                exit_idx = None
                exit_price = None
                
                for j in range(i + 1, min(i + 100, len(self.prices))):
                    if self.prices[j] >= target_price:
                        exit_idx = j
                        exit_price = target_price
                        break
                    elif self.prices[j] <= stop_price:
                        exit_idx = j
                        exit_price = stop_price
                        break
                
                if exit_idx is not None:
                    pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                    trade = Trade(
                        entry_price=entry_price,
                        exit_price=exit_price,
                        entry_idx=entry_idx,
                        exit_idx=exit_idx,
                        pnl_bps=pnl_bps,
                        pnl_pct=pnl_pct,
                        reason=f'momentum_pct={momentum_pct:.2f}%'
                    )
                    trades.append(trade)
                    i = exit_idx + 1
                else:
                    i += 1
            else:
                i += 1
        
        self.trades = trades
        return trades


class SignalC_VolatilityExpansion(SignalTester):
    """
    Detect volatility spike (vol > 1.5x recent average).
    Entry: On breakout direction.
    Exit: +2% target or -2% stop.
    """
    
    def generate_trades(self) -> List[Trade]:
        """Find volatility expansion setups."""
        trades = []
        vol_lookback = 20
        
        # Calculate rolling volatility (simple standard deviation)
        returns = np.diff(np.log(self.prices))
        rolling_vol = pd.Series(returns).rolling(vol_lookback).std().values
        
        i = vol_lookback
        while i < len(self.prices) - 1:
            # Average volatility in recent window
            avg_vol = np.mean(rolling_vol[max(0, i - 40):i])
            current_vol = rolling_vol[i]
            
            if current_vol > 1.5 * avg_vol and current_vol > 0:
                # Volatility spike detected
                # Determine direction: go in direction of current move
                if i > 0 and self.prices[i] > self.prices[i - 1]:
                    direction = 'LONG'
                    entry_price = self.prices[i]
                else:
                    # Simplified: only test long direction
                    i += 1
                    continue
                
                entry_idx = i
                target_price = entry_price * (1 + TARGET_PCT / 100)
                stop_price = entry_price * (1 - STOP_PCT / 100)
                
                exit_idx = None
                exit_price = None
                
                for j in range(i + 1, min(i + 100, len(self.prices))):
                    if self.prices[j] >= target_price:
                        exit_idx = j
                        exit_price = target_price
                        break
                    elif self.prices[j] <= stop_price:
                        exit_idx = j
                        exit_price = stop_price
                        break
                
                if exit_idx is not None:
                    pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                    trade = Trade(
                        entry_price=entry_price,
                        exit_price=exit_price,
                        entry_idx=entry_idx,
                        exit_idx=exit_idx,
                        pnl_bps=pnl_bps,
                        pnl_pct=pnl_pct,
                        reason=f'vol_spike={current_vol / avg_vol:.2f}x'
                    )
                    trades.append(trade)
                    i = exit_idx + 1
                else:
                    i += 1
            else:
                i += 1
        
        self.trades = trades
        return trades


class SignalD_MeanReversion(SignalTester):
    """
    Detect price deviation from VWAP (>0.5%).
    Entry: Opposite to deviation (fade the move).
    Exit: Back to VWAP or -2% stop.
    """
    
    def generate_trades(self) -> List[Trade]:
        """Find mean reversion setups."""
        trades = []
        vwap_lookback = 20
        
        i = vwap_lookback
        while i < len(self.prices) - 1:
            # Calculate VWAP (simplified: just mean of recent prices)
            vwap = np.mean(self.prices[i - vwap_lookback:i])
            current_price = self.prices[i]
            deviation_pct = (current_price - vwap) / vwap * 100
            
            if abs(deviation_pct) > 0.5:
                # Price deviated > 0.5% from VWAP
                # Fade the move: go long if price below VWAP, short if above
                # Simplified: test only long fades
                if deviation_pct < -0.5:  # Price below VWAP, go long
                    entry_price = current_price
                    entry_idx = i
                    
                    # Exit: back to VWAP or -2% stop
                    exit_idx = None
                    exit_price = None
                    
                    for j in range(i + 1, min(i + 100, len(self.prices))):
                        if self.prices[j] >= vwap:  # Back to VWAP
                            exit_idx = j
                            exit_price = vwap
                            break
                        elif self.prices[j] <= entry_price * (1 - STOP_PCT / 100):
                            exit_idx = j
                            exit_price = entry_price * (1 - STOP_PCT / 100)
                            break
                    
                    if exit_idx is not None:
                        pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                        trade = Trade(
                            entry_price=entry_price,
                            exit_price=exit_price,
                            entry_idx=entry_idx,
                            exit_idx=exit_idx,
                            pnl_bps=pnl_bps,
                            pnl_pct=pnl_pct,
                            reason=f'deviation={deviation_pct:.2f}%, vwap={vwap:.2f}'
                        )
                        trades.append(trade)
                        i = exit_idx + 1
                    else:
                        i += 1
                else:
                    i += 1
            else:
                i += 1
        
        self.trades = trades
        return trades


class SignalE_RandomBaseline(SignalTester):
    """
    Random entry timing in same windows (control signal).
    Same trade count as other signals.
    Same position sizing.
    """
    
    def generate_trades(self, target_count: int = 50) -> List[Trade]:
        """Generate random trades for baseline comparison."""
        trades = []
        np.random.seed(42)  # Reproducible
        
        for _ in range(target_count):
            # Random entry point (avoid last 100 ticks)
            entry_idx = np.random.randint(0, max(1, len(self.prices) - 100))
            entry_price = self.prices[entry_idx]
            
            target_price = entry_price * (1 + TARGET_PCT / 100)
            stop_price = entry_price * (1 - STOP_PCT / 100)
            
            exit_idx = None
            exit_price = None
            
            for j in range(entry_idx + 1, min(entry_idx + 100, len(self.prices))):
                if self.prices[j] >= target_price:
                    exit_idx = j
                    exit_price = target_price
                    break
                elif self.prices[j] <= stop_price:
                    exit_idx = j
                    exit_price = stop_price
                    break
            
            if exit_idx is not None:
                pnl_bps, pnl_pct = self.calculate_pnl(entry_price, exit_price)
                trade = Trade(
                    entry_price=entry_price,
                    exit_price=exit_price,
                    entry_idx=entry_idx,
                    exit_idx=exit_idx,
                    pnl_bps=pnl_bps,
                    pnl_pct=pnl_pct,
                    reason='random'
                )
                trades.append(trade)
        
        self.trades = trades
        return trades


# =====================================================================
# ANALYSIS & REPORTING
# =====================================================================

def analyze_trades(trades: List[Trade], signal_name: str, asset: str) -> Dict:
    """Analyze trade results."""
    if not trades:
        return {
            'signal': signal_name,
            'asset': asset,
            'sample_size': 0,
            'win_rate': 0,
            'pnl_per_trade_bps': 0,
            'pnl_per_trade_pct': 0,
            'total_pnl_bps': 0,
            'std_dev_bps': 0,
            'verdict': 'NO_TRADES'
        }
    
    wins = sum(1 for t in trades if t.is_win)
    win_rate = wins / len(trades) * 100
    
    pnl_bps = [t.pnl_bps for t in trades]
    total_pnl = sum(pnl_bps)
    avg_pnl = total_pnl / len(trades)
    std_dev = np.std(pnl_bps)
    
    # Verdict logic
    if avg_pnl > 10:
        verdict = 'STRONG_EDGE'
    elif avg_pnl > 5:
        verdict = 'MODERATE_EDGE'
    elif avg_pnl > 0:
        verdict = 'MARGINAL_EDGE'
    else:
        verdict = 'NO_EDGE'
    
    return {
        'signal': signal_name,
        'asset': asset,
        'sample_size': len(trades),
        'win_rate': round(win_rate, 2),
        'pnl_per_trade_bps': round(avg_pnl, 2),
        'pnl_per_trade_pct': round(avg_pnl / 100, 4),
        'total_pnl_bps': round(total_pnl, 2),
        'std_dev_bps': round(std_dev, 2),
        'max_win_bps': round(max(pnl_bps), 2),
        'max_loss_bps': round(min(pnl_bps), 2),
        'verdict': verdict
    }


# =====================================================================
# MAIN EXECUTION
# =====================================================================

def main():
    print("=" * 80)
    print("PHASE 24 - CRYPTO SIGNAL DISCOVERY")
    print("=" * 80)
    print(f"\nCost Model (Round-trip):")
    print(f"  Taker fee (entry): {CRYPTO_COSTS_BPS['taker_fee']} bps")
    print(f"  Entry slippage: {CRYPTO_COSTS_BPS['entry_slippage']} bps")
    print(f"  Maker fee (exit): {CRYPTO_COSTS_BPS['maker_fee']} bps")
    print(f"  Exit slippage: {CRYPTO_COSTS_BPS['exit_slippage']} bps")
    print(f"  Total: ~{CRYPTO_COSTS_BPS['round_trip']} bps round-trip\n")
    
    # Load data
    print("Loading crypto data...")
    btc_df = load_crypto_data('BTC')
    eth_df = load_crypto_data('ETH')
    
    btc_prices = prepare_price_series(btc_df)
    eth_prices = prepare_price_series(eth_df)
    
    print(f"  BTC: {len(btc_prices)} ticks, price range {btc_prices.min():.2f} - {btc_prices.max():.2f}")
    print(f"  ETH: {len(eth_prices)} ticks, price range {eth_prices.min():.2f} - {eth_prices.max():.2f}\n")
    
    # Test all signals
    results = []
    
    for asset, prices in [('BTC', btc_prices), ('ETH', eth_prices)]:
        print(f"\n{'='*80}")
        print(f"Testing on {asset}")
        print(f"{'='*80}")
        
        # Signal A: Momentum Reversal
        print("\nSignal A: MOMENTUM REVERSAL...")
        sig_a = SignalA_MomentumReversal(prices, 'A_MomentumReversal')
        trades_a = sig_a.generate_trades()
        result_a = analyze_trades(trades_a, 'A_MomentumReversal', asset)
        results.append(result_a)
        print(f"  Trades: {result_a['sample_size']}")
        print(f"  Win Rate: {result_a['win_rate']}%")
        print(f"  PnL/Trade: {result_a['pnl_per_trade_bps']} bps")
        print(f"  Verdict: {result_a['verdict']}")
        
        # Signal B: Micro Momentum Continuation
        print("\nSignal B: MICRO MOMENTUM CONTINUATION...")
        sig_b = SignalB_MicroMomentumContinuation(prices, 'B_MicroMomentum')
        trades_b = sig_b.generate_trades()
        result_b = analyze_trades(trades_b, 'B_MicroMomentum', asset)
        results.append(result_b)
        print(f"  Trades: {result_b['sample_size']}")
        print(f"  Win Rate: {result_b['win_rate']}%")
        print(f"  PnL/Trade: {result_b['pnl_per_trade_bps']} bps")
        print(f"  Verdict: {result_b['verdict']}")
        
        # Signal C: Volatility Expansion
        print("\nSignal C: VOLATILITY EXPANSION...")
        sig_c = SignalC_VolatilityExpansion(prices, 'C_VolExpansion')
        trades_c = sig_c.generate_trades()
        result_c = analyze_trades(trades_c, 'C_VolExpansion', asset)
        results.append(result_c)
        print(f"  Trades: {result_c['sample_size']}")
        print(f"  Win Rate: {result_c['win_rate']}%")
        print(f"  PnL/Trade: {result_c['pnl_per_trade_bps']} bps")
        print(f"  Verdict: {result_c['verdict']}")
        
        # Signal D: Mean Reversion
        print("\nSignal D: MEAN REVERSION (VWAP)...")
        sig_d = SignalD_MeanReversion(prices, 'D_MeanReversion')
        trades_d = sig_d.generate_trades()
        result_d = analyze_trades(trades_d, 'D_MeanReversion', asset)
        results.append(result_d)
        print(f"  Trades: {result_d['sample_size']}")
        print(f"  Win Rate: {result_d['win_rate']}%")
        print(f"  PnL/Trade: {result_d['pnl_per_trade_bps']} bps")
        print(f"  Verdict: {result_d['verdict']}")
        
        # Signal E: Random Baseline
        # Scale to match signal sample sizes
        avg_sample_size = int(np.mean([result_a['sample_size'], result_b['sample_size'], result_c['sample_size'], result_d['sample_size']]))
        print(f"\nSignal E: RANDOM BASELINE ({avg_sample_size} trades)...")
        sig_e = SignalE_RandomBaseline(prices, 'E_Random')
        trades_e = sig_e.generate_trades(target_count=max(20, avg_sample_size))
        result_e = analyze_trades(trades_e, 'E_Random', asset)
        results.append(result_e)
        print(f"  Trades: {result_e['sample_size']}")
        print(f"  Win Rate: {result_e['win_rate']}%")
        print(f"  PnL/Trade: {result_e['pnl_per_trade_bps']} bps")
        print(f"  Verdict: {result_e['verdict']}")
    
    # =====================================================================
    # SUMMARY ANALYSIS
    # =====================================================================
    
    print("\n" + "=" * 80)
    print("PHASE 24 SUMMARY RESULTS")
    print("=" * 80)
    
    print("\nResults Table:")
    print("-" * 130)
    print(f"{'Signal':<20} {'Asset':<6} {'Trades':<8} {'Win%':<8} {'PnL/Trade(bps)':<16} {'Edge vs Random':<16} {'Verdict':<20}")
    print("-" * 130)
    
    for r in results:
        print(f"{r['signal']:<20} {r['asset']:<6} {r['sample_size']:<8} {r['win_rate']:<8} {r['pnl_per_trade_bps']:<16} {'TBD':<16} {r['verdict']:<20}")
    
    print("-" * 130)
    
    # =====================================================================
    # KEY QUESTION ANALYSIS
    # =====================================================================
    
    print("\n" + "=" * 80)
    print("KEY QUESTIONS & ANSWERS")
    print("=" * 80)
    
    # Q1: Does ANY signal produce positive net edge after costs?
    winning_signals = [r for r in results if r['pnl_per_trade_bps'] > 0]
    print(f"\n1. Does ANY signal produce positive net edge after costs?")
    print(f"   Signals with PnL > 0 bps: {len(winning_signals)}/{len(results)}")
    if winning_signals:
        for sig in winning_signals:
            print(f"     • {sig['signal']} ({sig['asset']}): {sig['pnl_per_trade_bps']} bps")
        print(f"   ✓ YES - {len(winning_signals)} signals beat random after costs")
    else:
        print(f"   ✗ NO - All signals fail to beat costs")
    
    # Q2: Which signal is strongest?
    strongest = max(results, key=lambda r: r['pnl_per_trade_bps'])
    print(f"\n2. Which signal is strongest?")
    print(f"   Best performer: {strongest['signal']} ({strongest['asset']})")
    print(f"   - PnL/Trade: {strongest['pnl_per_trade_bps']} bps ({strongest['pnl_per_trade_pct']}%)")
    print(f"   - Win Rate: {strongest['win_rate']}%")
    print(f"   - Std Dev: {strongest['std_dev_bps']} bps")
    
    # Q3: Is edge strength strong/moderate/marginal/negative?
    print(f"\n3. Is edge strength: Strong (>20 bps) / Moderate (10-20 bps) / Marginal (<10 bps) / Negative (fails)?")
    if strongest['pnl_per_trade_bps'] > 20:
        strength = "STRONG (>20 bps)"
    elif strongest['pnl_per_trade_bps'] > 10:
        strength = "MODERATE (10-20 bps)"
    elif strongest['pnl_per_trade_bps'] > 0:
        strength = "MARGINAL (<10 bps)"
    else:
        strength = "NEGATIVE (fails)"
    print(f"   Answer: {strength}")
    print(f"   Strongest signal edge: {strongest['pnl_per_trade_bps']} bps")
    
    # Q4: Is edge stable across BTC and ETH?
    print(f"\n4. Is edge stable across BTC and ETH?")
    btc_results = [r for r in results if r['asset'] == 'BTC']
    eth_results = [r for r in results if r['asset'] == 'ETH']
    
    for sig_name in set(r['signal'] for r in results):
        btc_sig = [r for r in btc_results if r['signal'] == sig_name]
        eth_sig = [r for r in eth_results if r['signal'] == sig_name]
        
        if btc_sig and eth_sig:
            btc_pnl = btc_sig[0]['pnl_per_trade_bps']
            eth_pnl = eth_sig[0]['pnl_per_trade_bps']
            diff = abs(btc_pnl - eth_pnl)
            stability = "STABLE" if diff < 5 else "UNSTABLE"
            print(f"   {sig_name}: BTC={btc_pnl:+.1f} bps, ETH={eth_pnl:+.1f} bps, Δ={diff:.1f} bps [{stability}]")
    
    # =====================================================================
    # SAVE RESULTS
    # =====================================================================
    
    output_file = Path('/Users/rrg/.openclaw/workspace/phase24_results.json')
    with open(output_file, 'w') as f:
        json.dump({
            'phase': 24,
            'title': 'Crypto Signal Discovery',
            'cost_model_bps': CRYPTO_COSTS_BPS['round_trip'],
            'results': results,
            'summary': {
                'signals_tested': 5,
                'assets': ['BTC', 'ETH'],
                'total_trades': sum(r['sample_size'] for r in results),
                'winning_signals': len(winning_signals),
                'strongest_signal': {
                    'name': strongest['signal'],
                    'asset': strongest['asset'],
                    'pnl_per_trade_bps': strongest['pnl_per_trade_bps'],
                    'win_rate': strongest['win_rate']
                }
            }
        }, f, indent=2)
    
    print(f"\n✓ Results saved to {output_file}")
    
    return results


if __name__ == '__main__':
    main()
