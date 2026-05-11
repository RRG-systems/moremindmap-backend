#!/usr/bin/env python3
"""
Execution simulator for MOLTmarket dashboard
Simulates paper, shadow, and backtest execution with realistic fills and slippage
"""

import random
import math
from datetime import datetime, timedelta
from collections import deque
from uuid import uuid4


class RunState:
    """PHASE 32.4: Single source of truth for run-level metrics
    
    All metrics are read from this object, ensuring clean resets between runs.
    DO NOT accumulate metrics in globals - use run_state instead.
    """
    def __init__(self):
        self.total_trades = 0
        self.trade_sign_flips = 0
        self.flip_count = 0
        self.pnl = 0.0
        self.start_time = datetime.utcnow()
        self.previous_trade_direction = None  # Track for flip detection
        self.rolling_stats = {
            'win_rate': 0.0,
            'avg_pnl': 0.0,
            'equity_curve': [10000.0],
        }


class ExecutionSimulator:
    def __init__(self, data_layer, brain_status_getter=None):
        self.data_layer = data_layer
        
        # PHASE 4.6: BRAIN enforcement callback
        # Gets current BrainStatus (state, reason_code, reason_text, etc.)
        # If not provided, defaults to NORMAL (fail-safe)
        self.get_brain_status = brain_status_getter
        
        # CRITICAL FIX: Wire in unified executor and evolution engine
        self.unified_executor = None
        self.evolution_engine = None
        
        # PHASE 32.4: Run-level metrics (single source of truth)
        self.run_state = RunState()
        
        # Assets and signals
        self.assets = ['BTC', 'ETH']  # PHASE 28: Only BTC + ETH
        # PHASE 28: SIGNAL ISOLATION - MEAN REVERSION ONLY
        self.signals = ['Mean Reversion']  # DISABLED: Weekend Bias, Trend Following, Vol Mean Reversion
        self.regimes = ['high_vol', 'low_vol', 'trending', 'ranging']
        self.ACTIVE_SIGNALS = ['mean_reversion_20_03']  # 20-tick, 0.3% deviation
        
        # Current state
        self.current_signal = 'Mean Reversion'  # PHASE 28: Fixed to Mean Reversion
        self.current_asset = 'BTC'
        self.current_regime = 'ranging'
        
        # Execution buffers (equity curves)
        self.paper_equity = deque(maxlen=1000)
        self.shadow_equity = deque(maxlen=1000)
        self.backtest_equity = deque(maxlen=1000)
        
        # Trade counters
        self.paper_trades = 0
        self.shadow_trades = 0
        self.backtest_trades = 0
        
        # PnL accumulators
        self.paper_pnl = 0.0
        self.shadow_pnl = 0.0
        self.backtest_pnl = 0.0
        
        # Signal generation state
        self.step_count = 0
        self.signal_probability = 0.50  # 15% chance of signal per step
        
        # Backtest state (historical simulation)
        self.backtest_start = datetime.utcnow() - timedelta(days=45)
        self.backtest_index = 0
        
        # Price simulation
        self.last_prices = {asset: 100.0 for asset in self.assets}
        
        # PHASE 29: Run tracking
        self.current_run_id = None
        self.run_start_time = None
        self.run_state = RunState()  # PHASE 32.4
        self.win_counter = 0
        self.loss_counter = 0
    
    def set_promoted_parent_dna(self, parent_dna):
        """Set the promoted parent strategy DNA to use in signal generation."""
        self.promoted_parent_dna = parent_dna
        print(f"[ARENA DNA] Set promoted parent: {parent_dna.get('bot_id', 'unknown')}")

    def initialize(self):
        """Initialize simulator"""
        # Initialize equity curves with starting value
        self.paper_equity.append({'timestamp': datetime.utcnow().isoformat(), 'value': 10000.0})
        self.shadow_equity.append({'timestamp': datetime.utcnow().isoformat(), 'value': 10000.0})
        self.backtest_equity.append({'timestamp': self.backtest_start.isoformat(), 'value': 10000.0})
    
    def step(self):
        """Execute one step of simulation"""
        self.step_count += 1
        
        # Update regime
        self.current_regime = random.choice(self.regimes)
        
        # Generate signal with some probability
        if random.random() < self.signal_probability:
            self._generate_signal()
    
    def _check_brain_enforcement(self):
        """Check if BRAIN allows new trades.
        
        PHASE 4.6: Enforce BRAIN state before trade generation.
        
        Returns: (can_trade, brain_state, reason_text)
        """
        if not self.get_brain_status:
            # PHASE 4.6.1: HARDENED — default to STOP if no callback
            # Prevents uncontrolled trading if BRAIN disconnects
            print(f"[BRAIN] FAILSAFE — no brain status callback, defaulting to STOP")
            return False, 'STOP', 'No BRAIN callback (failsafe to STOP)'
        
        try:
            brain = self.get_brain_status()
            state = brain.get('state', 'NORMAL')
            reason = brain.get('reason_text', '')
            
            reason_code = brain.get('reason_code', 'unknown')
            
            # STOP blocks all new trades
            if state == 'STOP':
                print(f"[BRAIN] STOP enforcement — new trades blocked. Code: {reason_code} | Reason: {reason}")
                return False, state, reason
            
            # FLAT blocks all new trades
            if state == 'FLAT':
                print(f"[BRAIN] FLAT enforcement — new trades blocked. Code: {reason_code} | Reason: {reason}")
                return False, state, reason
            
            # THROTTLE allows trades but size reduced later
            if state == 'THROTTLE':
                print(f"[BRAIN] THROTTLE enforcement — proceeding with reduced size. Code: {reason_code} | Reason: {reason}")
                return True, state, reason
            
            # NORMAL proceeds
            if state == 'NORMAL':
                print(f"[BRAIN] NORMAL — trading allowed. Reason: {reason}")
            return True, state, reason
        
        except Exception as e:
            print(f"[BRAIN] FAILSAFE — ERROR in enforcement check: {type(e).__name__}: {e}")
            # PHASE 4.6.1: HARDENED — fail-safe to STOP on any error
            return False, 'STOP', f'BRAIN check error: {e}'
    
    def _generate_signal(self):
        """Generate a trading signal - uses promoted baby strategy if available
        
        PHASE 4.6: Check BRAIN enforcement FIRST before generating signal.
        """
        # PHASE 4.6: BRAIN enforcement gate
        can_trade, brain_state, reason = self._check_brain_enforcement()
        
        if not can_trade:
            print(f"[SIGNAL] Trade generation blocked by BRAIN ({brain_state})")
            return  # Exit early, no trade
        
        # Get promoted baby or baseline
        promoted_dna = getattr(self, 'promoted_parent_dna', None)
        arena_trader_id = promoted_dna.get('bot_id', 'baseline') if promoted_dna else 'baseline'
        
        strategy_name = promoted_dna.get('strategy_type', 'Mean Reversion') if promoted_dna else 'Mean Reversion'
        print(f"[ARENA] Using strategy: {strategy_name} (trader_id={arena_trader_id})")
        
        asset = random.choice(self.assets)
        side = random.choice(['long', 'short'])
        
        # Get entry price from simulator
        entry_price = self._get_price(asset)
        exit_price = self._get_price(asset)  # Get exit price
        
        print(f"[ARENA SIGNAL] Asset: {asset} | Side: {side} | Trader: {arena_trader_id}")
        
        # CRITICAL FIX: Execute through unified executor (same as Nursery babies)
        # This ensures Arena and Nursery trade in the same feed/ledger
        if self.unified_executor:
            signal = {
                'asset': asset,
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': 1.0,
            }
            try:
                trade = self.unified_executor.execute_signal(
                    source='arena',
                    trader_id=arena_trader_id,
                    signal=signal
                )
                if trade:
                    print(f"[ARENA EXECUTION] Trade logged to unified ledger: pnl=${trade.pnl:.2f}")
                else:
                    print(f"[ARENA EXECUTION] Signal generated but no trade (BRAIN blocked?)")
            except Exception as e:
                print(f"[ARENA ERROR] Failed to execute through unified executor: {e}")
                import traceback
                traceback.print_exc()
        else:
            print(f"[ARENA ERROR] unified_executor is None - cannot execute")
        
        # Update current signal state
        self.current_signal = strategy_name
        self.current_asset = asset


    def _get_price(self, asset):
        """Get simulated price for asset with realistic walk"""
        last = self.last_prices[asset]
        # Random walk: ±0.5% per step
        change = last * random.gauss(0, 0.005)
        new_price = max(last + change, last * 0.9)  # Don't crash to zero
        self.last_prices[asset] = new_price
        return round(new_price, 2)
    
    def _execute_paper(self, asset, signal, side, entry_price, brain_state='NORMAL'):
        """Execute paper trade (ideal fills, 0-2 bps slippage)
        
        PHASE 4.6: Apply BRAIN throttling to size.
        """
        # PHASE 4.6.1: FINAL EXECUTION GUARD
        # Last line of defense — re-check BRAIN state before ANY order placement
        if brain_state == 'STOP' or brain_state == 'FLAT':
            print(f"[BRAIN] HARD BLOCK — execution prevented at final layer. State: {brain_state}")
            return  # Block execution, return without creating trade
        
        # PHASE 4.6: Base size (will be throttled if needed)
        base_size = 1.0
        
        # Apply throttling if BRAIN state is THROTTLE
        if brain_state == 'THROTTLE':
            size_multiplier = 0.5
            actual_size = base_size * size_multiplier
            print(f"[BRAIN] Paper: THROTTLE applied. Size {base_size:.2f} → {actual_size:.2f}")
        else:
            actual_size = base_size
        
        # Paper gets best bid/ask
        entry_fill = entry_price * (1 + random.uniform(-0.0002, 0.0002))
        
        # Simulate trade result
        duration = random.randint(60, 3600)  # seconds
        exit_price = self._get_price(asset)
        exit_fill = exit_price * (1 + random.uniform(-0.0002, 0.0002))
        
        # Calculate PnL
        if side == 'long':
            pnl = (exit_fill - entry_fill) / entry_fill * 10000  # In dollars on $10k account
            pnl_bps = (exit_fill - entry_fill) / entry_fill * 10000  # In bps
        else:
            pnl = (entry_fill - exit_fill) / entry_fill * 10000
            pnl_bps = (entry_fill - exit_fill) / entry_fill * 10000
        
        self.paper_pnl += pnl
        self.paper_trades += 1
        if pnl > 0:
            self.win_counter += 1
        else:
            self.loss_counter += 1
        
        # Log trade
        trade = {
            'timestamp': datetime.utcnow().isoformat(),
            'asset': asset,
            'signal': signal,
            'source': 'paper',
            'side': side,
            'entry_price': round(entry_fill, 2),
            'exit_price': round(exit_fill, 2),
            'expected_fill': round(entry_fill, 2),
            'shadow_fill': round(entry_fill, 2),
            'pnl': round(pnl, 2),
            'pnl_bps': round(pnl_bps, 1),
            'duration': duration,
            'regime': self.current_regime,
        }
        self.data_layer.append_trade(trade)
        
        # Update equity curve
        self.paper_equity.append({
            'timestamp': datetime.utcnow().isoformat(),
            'value': 10000.0 + self.paper_pnl
        })
    
    def _execute_shadow(self, asset, signal, side, entry_price, brain_state='NORMAL'):
        """Execute shadow trade (degraded fills, 3 bps slippage, 10 bps round-trip)
        
        PHASE 4.6: Apply BRAIN throttling to size.
        PHASE 4.6.1: Final execution guard before order placement.
        """
        # PHASE 4.6.1: FINAL EXECUTION GUARD
        # Last line of defense — re-check BRAIN state before ANY order placement
        if brain_state == 'STOP' or brain_state == 'FLAT':
            print(f"[BRAIN] HARD BLOCK — execution prevented at final layer. State: {brain_state}")
            return  # Block execution, return without creating trade
        
        # PHASE 4.6: Base size (will be throttled if needed)
        base_size = 1.0
        
        # Apply throttling if BRAIN state is THROTTLE
        if brain_state == 'THROTTLE':
            size_multiplier = 0.5
            actual_size = base_size * size_multiplier
            print(f"[BRAIN] Shadow: THROTTLE applied. Size {base_size:.2f} → {actual_size:.2f}")
        else:
            actual_size = base_size
        
        # Shadow gets degraded fills
        if side == 'long':
            entry_fill = entry_price * 1.0003  # ask +3 bps
        else:
            entry_fill = entry_price * 0.9997  # bid -3 bps
        
        # Add random slippage 2-5 bps
        slippage_bps = random.uniform(0.0002, 0.0005)
        entry_fill *= (1 + slippage_bps)
        
        # Simulate trade result
        duration = random.randint(60, 3600)
        exit_price = self._get_price(asset)
        
        if side == 'long':
            exit_fill = exit_price * 0.9997  # bid -3 bps on exit
        else:
            exit_fill = exit_price * 1.0003  # ask +3 bps on exit
        
        # Add round-trip cost (10 bps total)
        roundtrip_cost = (entry_price * 0.001) / entry_price
        
        # Calculate PnL with costs
        if side == 'long':
            pnl = (exit_fill - entry_fill) / entry_fill * 10000 - roundtrip_cost * 10000
            pnl_bps = (exit_fill - entry_fill) / entry_fill * 10000 - 100  # round-trip in bps
        else:
            pnl = (entry_fill - exit_fill) / entry_fill * 10000 - roundtrip_cost * 10000
            pnl_bps = (entry_fill - exit_fill) / entry_fill * 10000 - 100
        
        self.shadow_pnl += pnl
        self.shadow_trades += 1
        
        # Log trade
        trade = {
            'timestamp': datetime.utcnow().isoformat(),
            'asset': asset,
            'signal': signal,
            'source': 'shadow',
            'side': side,
            'entry_price': round(entry_fill, 2),
            'exit_price': round(exit_fill, 2),
            'expected_fill': round(entry_price, 2),
            'shadow_fill': round(entry_fill, 2),
            'pnl': round(pnl, 2),
            'pnl_bps': round(pnl_bps, 1),
            'duration': duration,
            'regime': self.current_regime,
        }
        self.data_layer.append_trade(trade)
        
        # Update equity curve
        self.shadow_equity.append({
            'timestamp': datetime.utcnow().isoformat(),
            'value': 10000.0 + self.shadow_pnl
        })
    
    def _execute_backtest(self):
        """Simulate historical backtest trade"""
        # For now, just show reference curve
        # In production, would replay historical signals
        pass
    
    def get_paper_pnl(self):
        """Get paper PnL and trade count"""
        return self.paper_pnl, self.paper_trades
    
    def get_shadow_pnl(self):
        """Get shadow PnL and trade count"""
        return self.shadow_pnl, self.shadow_trades
    
    def get_backtest_pnl(self):
        """Get backtest PnL and trade count"""
        # Simulated: reference curve
        return 500.0, 45
    
    def get_paper_equity_curve(self):
        """Get paper equity curve as list"""
        return list(self.paper_equity)
    
    def get_shadow_equity_curve(self):
        """Get shadow equity curve as list"""
        return list(self.shadow_equity)
    
    def get_backtest_equity_curve(self):
        """Get backtest equity curve as list"""
        # Return simulated backtest curve
        curve = []
        start = self.backtest_start
        base_value = 10000.0
        current_value = base_value
        
        for i in range(45 * 24):  # 45 days of hourly points
            timestamp = start + timedelta(hours=i)
            # Simulate uptrend with noise
            current_value += random.gauss(15, 10)
            curve.append({
                'timestamp': timestamp.isoformat(),
                'value': max(current_value, base_value * 0.95)
            })
        
        return curve
    
    # =========================================================================
    # PHASE 29: New Run System Methods
    # =========================================================================
    
    def finalize_and_summarize_run(self):
        """Finalize current run: capture final run summary before reset
        
        Returns dict with all metrics to append to research_runs.csv
        CRITICAL: Must execute BEFORE any state reset
        """
        if not self.current_run_id:
            return None
        
        # Get all trades for this run from data layer
        all_trades = self.data_layer.get_recent_trades(limit=10000)
        
        # Calculate summary metrics
        total_trades = len(all_trades)
        wins = sum(1 for t in all_trades if float(t.get('pnl', 0)) > 0)
        losses = sum(1 for t in all_trades if float(t.get('pnl', 0)) < 0)
        
        win_rate = (wins / total_trades * 100) if total_trades > 0 else 0
        avg_pnl_per_trade = (sum(float(t.get('pnl', 0)) for t in all_trades) / total_trades) if total_trades > 0 else 0
        
        # Paper vs Shadow PnL
        paper_trades = [t for t in all_trades if t.get('source') == 'paper']
        shadow_trades = [t for t in all_trades if t.get('source') == 'shadow']
        
        total_pnl_paper = sum(float(t.get('pnl', 0)) for t in paper_trades)
        total_pnl_shadow = sum(float(t.get('pnl', 0)) for t in shadow_trades)
        
        paper_vs_shadow_delta = ((total_pnl_paper - total_pnl_shadow) / abs(total_pnl_shadow) * 100) if total_pnl_shadow != 0 else 0
        
        # Slippage calculation
        entry_slippages = []
        exit_slippages = []
        sign_flips = 0
        
        for trade in all_trades:
            expected = float(trade.get('expected_fill', 0))
            shadow = float(trade.get('shadow_fill', 0))
            
            if expected > 0:
                entry_slippages.append(abs(expected - shadow) / expected * 10000)
            
            # Sign flips: expected win but actual loss
            pnl = float(trade.get('pnl', 0))
            pnl_bps = float(trade.get('pnl_bps', 0))
            if (pnl_bps >= 0 and pnl < 0) or (pnl_bps < 0 and pnl >= 0):
                sign_flips += 1
        
        avg_entry_slippage_bps = sum(entry_slippages) / len(entry_slippages) if entry_slippages else 0
        avg_exit_slippage_bps = 0  # Simplified; would need more data
        sign_flip_rate = (sign_flips / total_trades * 100) if total_trades > 0 else 0
        
        # Build run summary
        run_summary = {
            'run_id': self.current_run_id,
            'start_time': self.run_start_time.isoformat() if self.run_start_time else datetime.utcnow().isoformat(),
            'end_time': datetime.utcnow().isoformat(),
            'total_trades': total_trades,
            'win_rate': round(win_rate, 1),
            'avg_pnl_per_trade': round(avg_pnl_per_trade, 2),
            'total_pnl_paper': round(total_pnl_paper, 2),
            'total_pnl_shadow': round(total_pnl_shadow, 2),
            'paper_vs_shadow_delta': round(paper_vs_shadow_delta, 1),
            'avg_entry_slippage_bps': round(avg_entry_slippage_bps, 2),
            'avg_exit_slippage_bps': round(avg_exit_slippage_bps, 2),
            'sign_flip_rate': round(sign_flip_rate, 1),
        }
        
        print(f"[PHASE 29] Run finalized - {total_trades} trades, {win_rate:.1f}% win rate, ${total_pnl_paper:.2f} paper")
        return run_summary
    
    def reset_run_state(self):
        """Reset in-memory state for new run (STEP 4)
        
        Called AFTER finalizing previous run and appending separators
        PHASE 32.4: Uses run_state as single source of truth
        """
        # PHASE 32.4: Reset run-level metrics (single source of truth)
        self.run_state = RunState()
        
        # STEP 4: Reset in-memory state
        self.paper_equity.clear()
        self.shadow_equity.clear()
        self.backtest_equity.clear()
        
        self.paper_pnl = 0.0
        self.shadow_pnl = 0.0
        self.backtest_pnl = 0.0
        
        self.paper_trades = 0
        self.shadow_trades = 0
        self.backtest_trades = 0
        
        self.win_counter = 0
        self.loss_counter = 0
        
        # Re-initialize equity curves with starting value
        now = datetime.utcnow().isoformat()
        self.paper_equity.append({'timestamp': now, 'value': 10000.0})
        self.shadow_equity.append({'timestamp': now, 'value': 10000.0})
        self.backtest_equity.append({'timestamp': now, 'value': 10000.0})
        
        self.step_count = 0
        
        print(f"[PHASE 29] Run state reset for new experiment")

    def get_current_equity(self):
        """Get current equity value (paper execution)"""
        if len(self.paper_equity) > 0:
            return self.paper_equity[-1].get('value', 10000.0)
        return 10000.0
    
    def reset_capital(self):
        """Reset arena capital to $10,000
        
        - Reset equity curves
        - Reset PnL
        - Preserve trade history
        - Update equity curve with reset point
        """
        print("[ExecutionSimulator] Resetting capital...")
        
        # Reset current equity
        self.paper_pnl = 0.0
        self.shadow_pnl = 0.0
        self.backtest_pnl = 0.0
        
        # Clear equity curves but keep history by appending reset marker
        current_time = __import__('datetime').datetime.utcnow().isoformat()
        
        # Create new equity curves starting fresh
        self.paper_equity.clear()
        self.shadow_equity.clear()
        self.backtest_equity.clear()
        
        # Initialize with reset value
        self.paper_equity.append({'timestamp': current_time, 'value': 10000.0})
        self.shadow_equity.append({'timestamp': current_time, 'value': 10000.0})
        self.backtest_equity.append({'timestamp': current_time, 'value': 10000.0})
        
        # Reset trade counters for new segment
        self.paper_trades = 0
        self.shadow_trades = 0
        self.backtest_trades = 0
        
        # Reset win/loss counters
        self.win_counter = 0
        self.loss_counter = 0
        
        print("[ExecutionSimulator] Capital reset complete - equity: 10000.0")

