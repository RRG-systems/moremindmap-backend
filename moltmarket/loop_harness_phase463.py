#!/usr/bin/env python3
"""
LOOP HARNESS v3 — Phase 4.6.3 Churn Prevention Integration

Tests that system:
1. Detects degradation early
2. Attempts limited replacements
3. Goes FLAT when all candidates identical
4. Stops churning
"""

import json
from pathlib import Path
from datetime import datetime
from brain_engine_phase46_2 import BrainEnginePhase462, BrainConfig
from replacement_engine_phase47_2 import ReplacementEnginePhase463


class LoopHarnessPhase463:
    """Loop harness with churn prevention"""
    
    def __init__(self, num_cycles: int = 30, workspace_dir: str = '.'):
        self.num_cycles = num_cycles
        self.workspace = Path(workspace_dir)
        self.replacement_engine = ReplacementEnginePhase463(workspace_dir)
        
        brain_config = BrainConfig(
            throttle_drawdown_pct=5.0,
            stop_drawdown_pct=8.0,
            slow_bleed_window_size=10,
            slow_bleed_avg_pnl_threshold=-0.5,
        )
        self.brain = BrainEnginePhase462(brain_config)
        
        self.cycles = []
        self.equity_curve = [10000.0]
        self.current_bot = 'baseline'
        self.flat_count = 0
        self.replace_count = 0
        self.throttle_count = 0
        self.stop_count = 0
        self.churn_prevented = False
    
    def simulate_bot_performance(self, bot_id: str, cycle_num: int) -> Dict:
        """Simulate bot losing $40/cycle"""
        pnl = -40.0
        trades = 20
        win_rate = 0.45
        drawdown = min(0.06, 0.002 * cycle_num)
        
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
        
        print(f"Active bot: {self.current_bot}")
        bot_perf = self.simulate_bot_performance(self.current_bot, cycle_num)
        print(f"  Trades: {bot_perf['trades']}, PnL: ${bot_perf['pnl']:.2f}, Drawdown: {bot_perf['drawdown']:.1%}")
        
        # Record trades for BRAIN
        for i in range(bot_perf['trades']):
            self.brain.record_trade(bot_perf['avg_pnl_per_trade'])
        
        # BRAIN evaluation
        status = self.brain.evaluate(
            active_bot_id=self.current_bot,
            bot_drawdown_pct=bot_perf['drawdown'] * 100,
            daily_loss_usd=sum(c['pnl'] for c in self.cycles) if self.cycles else 0,
            sign_flip_pct=10.0
        )
        
        brain_state = status.state
        reason = status.reason_code
        print(f"\nBRAIN state: {brain_state} ({reason})")
        
        if brain_state == 'THROTTLE':
            self.throttle_count += 1
        elif brain_state == 'STOP':
            self.stop_count += 1
        
        # Equity update
        equity_before = self.equity_curve[-1]
        equity_after = equity_before + bot_perf['pnl']
        
        # Decision logic
        action = None
        
        if brain_state in ['STOP', 'THROTTLE']:
            if brain_state == 'STOP':
                print(f"→ Replacement engine triggered")
                
                # Try replacement (with churn prevention)
                selected, should_flat, flat_reason = self.replacement_engine.select_replacement(
                    exclude_bot_id=self.current_bot
                )
                
                if should_flat:
                    if 'CHURN' in flat_reason or 'Low diversity' in flat_reason:
                        print(f"→ ACTION: FLAT ({flat_reason})")
                        self.churn_prevented = True
                    else:
                        print(f"→ ACTION: FLAT ({flat_reason})")
                    
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
            else:
                print(f"→ ACTION: THROTTLE")
                action = 'THROTTLE'
        else:
            print(f"→ ACTION: CONTINUE")
            action = 'CONTINUE'
        
        # Update equity
        self.equity_curve.append(equity_after)
        
        # Record
        cycle_result = {
            'cycle': cycle_num,
            'active_bot': self.current_bot,
            'brain_state': brain_state,
            'action': action,
            'pnl': bot_perf['pnl'],
            'equity': equity_after,
        }
        self.cycles.append(cycle_result)
        
        print(f"\nResult: Equity ${equity_before:.2f} → ${equity_after:.2f}")
        print(f"Cumulative: ${self.equity_curve[-1]:.2f}")
        
        return cycle_result
    
    def run_harness(self):
        """Run all cycles"""
        print("\n" + "="*80)
        print(f"LOOP HARNESS v3 — Phase 4.6.3 Churn Prevention")
        print(f"{self.num_cycles} Cycles")
        print("="*80)
        
        for cycle_num in range(1, self.num_cycles + 1):
            self.run_cycle(cycle_num)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "="*80)
        print("HARNESS TEST COMPLETE")
        print("="*80)
        
        total_cycles = len(self.cycles)
        
        print(f"\n[CYCLE STATISTICS]")
        print(f"  Total cycles: {total_cycles}")
        print(f"  THROTTLE: {self.throttle_count}")
        print(f"  STOP: {self.stop_count}")
        print(f"  Replacements: {self.replace_count}")
        print(f"  FLAT: {self.flat_count}")
        
        # Equity
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
        
        if self.throttle_count == 0 and self.stop_count == 0:
            print("❌ BRAIN never triggered")
        else:
            print(f"✅ BRAIN triggered: {self.throttle_count + self.stop_count} events")
        
        if self.churn_prevented:
            print(f"✅ CHURN PREVENTED: System went FLAT instead of cycling")
        
        if self.replace_count <= 2:
            print(f"✅ Limited replacements: {self.replace_count} (goal: ≤2)")
        else:
            print(f"⚠️  Replacements: {self.replace_count} (high)")
        
        if self.flat_count >= 1:
            print(f"✅ FLAT triggered: {self.flat_count} time(s)")
        
        print("\n" + "="*80 + "\n")


if __name__ == '__main__':
    harness = LoopHarnessPhase463(num_cycles=30, workspace_dir=Path.cwd())
    
    try:
        harness.run_harness()
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
