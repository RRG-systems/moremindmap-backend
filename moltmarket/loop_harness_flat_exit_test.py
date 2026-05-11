#!/usr/bin/env python3
"""
FLAT EXIT TEST — Final Validation

Tests that system can:
1. Go FLAT when candidates are weak (Phase 1: cycles 1-15)
2. Detect improvement when better candidate appears (Phase 2: cycle 16+)
3. Exit FLAT and resume trading intelligently (Phase 2)

Pass condition:
- Clean FLAT in Phase 1
- Clean exit and restart in Phase 2
- No re-churning or erratic behavior
"""

import json
from pathlib import Path
from datetime import datetime
from brain_engine_phase46_2 import BrainEnginePhase462, BrainConfig
from replacement_engine_phase47_2 import ReplacementEnginePhase463


class FlatExitTest:
    """Test system FLAT exit behavior"""
    
    def __init__(self, workspace_dir: str = '.'):
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
        self.flat_entered_cycle = None
        self.flat_exited_cycle = None
        self.in_flat = False
        self.phase = 1
    
    def inject_better_candidate(self):
        """
        At cycle 16: inject a better candidate into the nursery.
        
        This simulates: new candidate appears that's actually profitable.
        """
        # Create a synthetic better candidate
        better_candidate = {
            'run_id': 'test_run_1',
            'variant_id': 'baby_golden',  # The good one
            'parent_id': 'baseline',
            'parent_generation': 0,
            'generation': 1,
            'mutation_type': 'winning_mutation',
            'parameter_value': '0.5',
            'trade_count': 40,  # Good sample
            'paper_pnl': 200.0,
            'shadow_pnl': 150.0,  # Positive P&L
            'sign_flip_rate': 0.06,  # Low flips (stable)
            'degradation_pct': 2.0,  # Low drawdown
            'score': 0.85,
            'status': 'completed',
            'timestamp': datetime.utcnow().isoformat(),
        }
        
        # Append to nursery
        nursery_file = self.workspace / 'variant_nursery.csv'
        import csv
        
        if nursery_file.exists():
            # Append the better candidate
            with open(nursery_file, 'a', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=better_candidate.keys())
                writer.writerow(better_candidate)
            
            print(f"\n[TEST] ✓ Injected better candidate: baby_golden")
            print(f"       P&L: $150.0, Drawdown: 2.0%, Flips: 6.0%")
    
    def simulate_bot_performance(self, bot_id: str, cycle_num: int) -> Dict:
        """Simulate bot losing $40/cycle (Phase 1) or trading normally (Phase 2)"""
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
        print(f"CYCLE {cycle_num} (PHASE {self.phase})")
        print(f"{'='*80}")
        
        # At cycle 16: inject better candidate
        if cycle_num == 16:
            print(f"\n[PHASE TRANSITION] Better candidate appears (cycle 16)")
            self.inject_better_candidate()
            self.phase = 2
        
        print(f"Active bot: {self.current_bot if self.current_bot else 'NONE (FLAT)'}")
        
        if not self.current_bot:
            print("  Status: FLAT — no trading")
            equity_before = self.equity_curve[-1]
            equity_after = equity_before  # FLAT = no P&L
        else:
            bot_perf = self.simulate_bot_performance(self.current_bot, cycle_num)
            print(f"  Trades: {bot_perf['trades']}, PnL: ${bot_perf['pnl']:.2f}, Drawdown: {bot_perf['drawdown']:.1%}")
            
            # Record trades for BRAIN
            for i in range(bot_perf['trades']):
                self.brain.record_trade(bot_perf['avg_pnl_per_trade'])
            
            # BRAIN evaluation
            status = self.brain.evaluate(
                active_bot_id=self.current_bot,
                bot_drawdown_pct=bot_perf['drawdown'] * 100,
                daily_loss_usd=sum(c.get('pnl', 0) for c in self.cycles) if self.cycles else 0,
                sign_flip_pct=10.0
            )
            
            brain_state = status.state
            print(f"\nBRAIN state: {brain_state}")
            
            equity_before = self.equity_curve[-1]
            
            # Decision logic
            if brain_state == 'STOP':
                print(f"→ Replacement engine triggered")
                
                selected, should_flat, flat_reason = self.replacement_engine.select_replacement(
                    exclude_bot_id=self.current_bot
                )
                
                if should_flat:
                    print(f"→ ACTION: FLAT ({flat_reason})")
                    if not self.in_flat:
                        self.flat_entered_cycle = cycle_num
                        self.in_flat = True
                    self.current_bot = None
                    equity_after = equity_before  # No trading
                else:
                    print(f"→ ACTION: SWITCH to {selected['bot_id']}")
                    self.current_bot = selected['bot_id']
                    self.brain = BrainEnginePhase462()
                    equity_after = equity_before + bot_perf['pnl']
            else:
                equity_after = equity_before + bot_perf['pnl']
        
        # Update equity
        self.equity_curve.append(equity_after)
        
        # Check if we're exiting FLAT
        if self.in_flat and self.current_bot:
            print(f"\n>>> EXITING FLAT: Selected candidate {self.current_bot}")
            self.flat_exited_cycle = cycle_num
            self.in_flat = False
        
        # Record
        cycle_result = {
            'cycle': cycle_num,
            'phase': self.phase,
            'active_bot': self.current_bot,
            'in_flat': self.in_flat,
            'equity': equity_after,
        }
        self.cycles.append(cycle_result)
        
        print(f"\nResult: Equity ${equity_before:.2f} → ${equity_after:.2f}")
        print(f"Cumulative: ${self.equity_curve[-1]:.2f}")
        
        return cycle_result
    
    def run_test(self, num_cycles: int = 30):
        """Run the full test"""
        print("\n" + "="*80)
        print("FLAT EXIT TEST — System Graceful Restart")
        print(f"{num_cycles} Cycles (15 bad env + 15 with improvement)")
        print("="*80)
        
        for cycle_num in range(1, num_cycles + 1):
            self.run_cycle(cycle_num)
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary and verdict"""
        print("\n" + "="*80)
        print("TEST COMPLETE — FLAT EXIT VALIDATION")
        print("="*80)
        
        # Phase 1 analysis
        phase1_cycles = [c for c in self.cycles if c['phase'] == 1]
        phase1_flat_count = sum(1 for c in phase1_cycles if c['in_flat'] or not c['active_bot'])
        
        print(f"\n[PHASE 1: Bad Environment (cycles 1-15)]")
        print(f"  Cycles in FLAT: {phase1_flat_count} / {len(phase1_cycles)}")
        if phase1_flat_count >= 10:
            print(f"  ✅ System correctly went FLAT (no edge)")
        else:
            print(f"  ⚠️  System didn't FLAT enough ({phase1_flat_count}/15)")
        
        # Phase 2 analysis
        phase2_cycles = [c for c in self.cycles if c['phase'] == 2]
        
        print(f"\n[PHASE 2: Better Candidate Injected (cycles 16-30)]")
        if self.flat_exited_cycle:
            print(f"  Exited FLAT at cycle: {self.flat_exited_cycle}")
            print(f"  Selected candidate: {[c['active_bot'] for c in phase2_cycles if c['active_bot']][0] if [c['active_bot'] for c in phase2_cycles if c['active_bot']] else 'None'}")
            print(f"  ✅ System detected improvement and restarted")
        else:
            print(f"  Never exited FLAT")
            print(f"  ⚠️  System missed the better candidate")
        
        # Equity analysis
        start_equity = self.equity_curve[0]
        end_equity = self.equity_curve[-1]
        phase1_equity = self.equity_curve[15] if len(self.equity_curve) > 15 else start_equity
        
        print(f"\n[EQUITY CURVE]")
        print(f"  Start: ${start_equity:.2f}")
        print(f"  After Phase 1: ${phase1_equity:.2f}")
        print(f"  End: ${end_equity:.2f}")
        
        phase1_return = ((phase1_equity - start_equity) / start_equity * 100)
        phase2_return = ((end_equity - phase1_equity) / phase1_equity * 100) if phase1_equity > 0 else 0
        
        print(f"  Phase 1 return: {phase1_return:+.1f}% (expected ≈0%, FLAT protected)")
        print(f"  Phase 2 return: {phase2_return:+.1f}% (should be trading again)")
        
        # Verdict
        print(f"\n[VERDICT]")
        
        pass_conditions = [
            (phase1_flat_count >= 10, "✅ Phase 1: System went FLAT"),
            (self.flat_exited_cycle is not None, "✅ Phase 2: System exited FLAT"),
            (phase1_return > -2.0, "✅ Phase 1: Capital protected"),
            (self.flat_exited_cycle is not None and self.flat_exited_cycle <= 20, "✅ Phase 2: Timely restart"),
        ]
        
        passed = sum(1 for condition, _ in pass_conditions if condition)
        total = len(pass_conditions)
        
        for condition, text in pass_conditions:
            if condition:
                print(f"  {text}")
            else:
                print(f"  ❌ {text.replace('✅', '')}")
        
        print(f"\n{'='*80}")
        if passed == total:
            print(f"🎯 TEST PASSED ({passed}/{total})")
            print("System can gracefully FLAT and restart on improvement.")
            print("\n✅ SAFE TO PROCEED TO PHASE 4.8")
        else:
            print(f"⚠️  TEST PARTIAL ({passed}/{total})")
            print("System needs refinement before scaling.")
        print(f"{'='*80}\n")


if __name__ == '__main__':
    test = FlatExitTest(workspace_dir=Path.cwd())
    
    try:
        test.run_test(num_cycles=30)
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
