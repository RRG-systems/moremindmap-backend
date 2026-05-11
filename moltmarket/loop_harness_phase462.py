#!/usr/bin/env python3
"""
LOOP HARNESS TEST v2 — Phase 4.6.2 Integration
Tests the enhanced BRAIN with slow bleed detection

Expects:
- Early THROTTLE on negative drift
- STOP on slow bleed
- Replacement engine triggered
- System doesn't bleed uncontrolled
"""

import json
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple
from replacement_engine_phase47 import ReplacementEngine
from brain_engine_phase46_2 import BrainEnginePhase462, BrainConfig


class LoopHarnessPhase462:
    """
    Enhanced loop harness with Phase 4.6.2 BRAIN integration.
    """
    
    def __init__(self, num_cycles: int = 30, workspace_dir: str = '.'):
        self.num_cycles = num_cycles
        self.workspace = Path(workspace_dir)
        self.replacement_engine = ReplacementEngine(workspace_dir)
        
        # Enhanced BRAIN
        brain_config = BrainConfig(
            throttle_drawdown_pct=5.0,   # Early warning
            stop_drawdown_pct=8.0,        # Hard stop
            slow_bleed_window_size=10,    # Faster detection
            slow_bleed_avg_pnl_threshold=-0.5,
        )
        self.brain = BrainEnginePhase462(brain_config)
        
        # Harness state
        self.cycles = []
        self.equity_curve = [10000.0]
        self.current_bot = 'baseline'
        self.flat_count = 0
        self.replace_count = 0
        self.throttle_count = 0
        self.stop_count = 0
        self.cycle_results = []
    
    def simulate_bot_performance(self, bot_id: str, cycle_num: int) -> Dict:
        """Simulate bot performance (progressive degradation)"""
        # Simulate consistent small losses (-$0.80 per cycle)
        # This should trigger slow bleed detection around cycle 8-10
        pnl = -40.0  # $40 loss per cycle (to accumulate)
        trades = 20
        win_rate = 0.45
        drawdown = min(0.06, 0.002 * cycle_num)  # Slow increase
        
        return {
            'bot_id': bot_id,
            'cycle': cycle_num,
            'trades': trades,
            'win_rate': win_rate,
            'pnl': pnl,
            'drawdown': drawdown,
            'avg_pnl_per_trade': pnl / trades,
        }
    
    def run_cycle(self, cycle_num: int) -> Dict:
        """Run one trading cycle"""
        print(f"\n{'='*80}")
        print(f"CYCLE {cycle_num}")
        print(f"{'='*80}")
        
        # Step 1: Bot performance
        print(f"\nActive bot: {self.current_bot}")
        bot_perf = self.simulate_bot_performance(self.current_bot, cycle_num)
        print(f"  Trades: {bot_perf['trades']}, Win rate: {bot_perf['win_rate']:.1%}, PnL: ${bot_perf['pnl']:.2f}, Drawdown: {bot_perf['drawdown']:.1%}")
        
        # Step 2: Record trade for BRAIN analysis
        for i in range(bot_perf['trades']):
            self.brain.record_trade(bot_perf['avg_pnl_per_trade'])
        
        # Step 3: BRAIN evaluation (PHASE 4.6.2 ENHANCED)
        status = self.brain.evaluate(
            active_bot_id=self.current_bot,
            bot_drawdown_pct=bot_perf['drawdown'] * 100,
            daily_loss_usd=sum(c['pnl'] for c in self.cycles) if self.cycles else 0,
            sign_flip_pct=10.0
        )
        
        brain_state = status.state
        reason = status.reason_code
        print(f"\nBRAIN state: {brain_state} ({reason})")
        if status.reason_text:
            print(f"  {status.reason_text}")
        
        # Track state changes
        if brain_state == 'THROTTLE':
            self.throttle_count += 1
        elif brain_state == 'STOP':
            self.stop_count += 1
        
        # Step 4: Equity update
        equity_before = self.equity_curve[-1]
        equity_after = equity_before + bot_perf['pnl']
        
        # Step 5: Decision logic
        action = None
        
        if brain_state in ['STOP', 'THROTTLE']:
            if brain_state == 'STOP':
                print(f"\n→ Replacement engine triggered (STOP)")
                
                # Try replacement
                selected, should_flat = self.replacement_engine.select_replacement(
                    exclude_bot_id=self.current_bot
                )
                
                if should_flat:
                    print(f"→ ACTION: FLAT")
                    action = 'FLAT'
                    self.flat_count += 1
                    equity_after = equity_before  # No trading
                else:
                    print(f"→ ACTION: SWITCH to {selected['bot_id']}")
                    action = 'SWITCH'
                    self.replace_count += 1
                    self.current_bot = selected['bot_id']
                    
                    # Reset BRAIN for new bot
                    self.brain = BrainEnginePhase462()
            else:  # THROTTLE
                print(f"→ ACTION: THROTTLE (reducing size)")
                action = 'THROTTLE'
        else:
            print(f"→ ACTION: CONTINUE (NORMAL)")
            action = 'CONTINUE'
        
        # Step 6: Update equity
        self.equity_curve.append(equity_after)
        
        # Step 7: Record
        cycle_result = {
            'cycle': cycle_num,
            'active_bot': self.current_bot,
            'brain_state': brain_state,
            'reason': reason,
            'action': action,
            'pnl': bot_perf['pnl'],
            'equity': equity_after,
        }
        self.cycles.append(cycle_result)
        
        print(f"\nResult:")
        print(f"  Equity: ${equity_before:.2f} → ${equity_after:.2f} ({bot_perf['pnl']:+.2f})")
        print(f"  Cumulative: ${self.equity_curve[-1]:.2f}")
        
        return cycle_result
    
    def run_harness(self):
        """Run all cycles"""
        print("\n" + "="*80)
        print(f"LOOP HARNESS v2 — Phase 4.6.2 Enhanced BRAIN")
        print(f"{self.num_cycles} Cycles")
        print("="*80)
        
        for cycle_num in range(1, self.num_cycles + 1):
            self.run_cycle(cycle_num)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("HARNESS TEST COMPLETE — SUMMARY")
        print("="*80)
        
        total_cycles = len(self.cycles)
        
        print(f"\n[CYCLE STATISTICS]")
        print(f"  Total cycles: {total_cycles}")
        print(f"  NORMAL: {total_cycles - self.throttle_count - self.stop_count - self.flat_count}")
        print(f"  THROTTLE: {self.throttle_count}")
        print(f"  STOP: {self.stop_count}")
        print(f"  FLAT: {self.flat_count}")
        print(f"  Replacements: {self.replace_count}")
        
        # Equity analysis
        start_equity = self.equity_curve[0]
        end_equity = self.equity_curve[-1]
        total_pnl = end_equity - start_equity
        return_pct = (total_pnl / start_equity * 100)
        
        print(f"\n[EQUITY CURVE]")
        print(f"  Start: ${start_equity:.2f}")
        print(f"  End: ${end_equity:.2f}")
        print(f"  Total P&L: ${total_pnl:+.2f}")
        print(f"  Return: {return_pct:+.1f}%")
        
        # Verdict
        print(f"\n[VERDICT]")
        
        # Check 1: Did BRAIN detect the bleed?
        if self.throttle_count == 0 and self.stop_count == 0:
            print("❌ BRAIN never triggered (still has the original problem)")
            return False
        
        # Check 2: Did replacements happen or FLAT?
        if self.replace_count == 0 and self.flat_count == 0:
            print("❌ No replacements or FLAT decisions")
            return False
        
        # Check 3: Did bleed reduce?
        if return_pct < -12.0:
            print(f"⚠️  Bleed still high ({return_pct:.1f}%)")
        
        if self.throttle_count > 0 or self.stop_count > 0:
            print(f"✅ BRAIN detected degradation:")
            print(f"   • THROTTLE events: {self.throttle_count}")
            print(f"   • STOP events: {self.stop_count}")
            print(f"   • Total detections: {self.throttle_count + self.stop_count}")
        
        if return_pct < -12.0:
            print(f"⚠️  System still bleeds {return_pct:.1f}% (better, but still high)")
            print(f"   Replacement or FLAT needs tuning")
        else:
            print(f"✅ Bleed controlled: {return_pct:+.1f}%")
        
        print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    harness = LoopHarnessPhase462(num_cycles=30, workspace_dir=Path.cwd())
    
    try:
        harness.run_harness()
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
