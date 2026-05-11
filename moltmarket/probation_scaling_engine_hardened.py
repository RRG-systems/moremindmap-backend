#!/usr/bin/env python3
"""
PHASE 4.8 HARDENING: PROBATION VISIBILITY + CONSTRAINTS

- Structured logging for probation lifecycle (queryable by THINK)
- Dual constraint: both MIN_CYCLES AND MIN_TRADES must be met
- No shortcuts, no lucky bursts
- Full diagnostic trail
"""

from datetime import datetime
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass, asdict
from enum import Enum
import json


class AllocationState(Enum):
    """Allocation lifecycle states"""
    FLAT = 0
    PROBATION = 1
    ACTIVE = 2
    DEGRADING = 3
    STOPPED = 4


class ProbationLogType(Enum):
    """Structured probation log types"""
    PROBATION_START = "PROBATION_START"
    PROBATION_STATUS = "PROBATION_STATUS"
    PROBATION_PASS = "PROBATION_PASS"
    PROBATION_FAIL = "PROBATION_FAIL"


@dataclass
class ProbationLog:
    """Structured probation log entry"""
    log_type: str
    bot_id: str
    timestamp: str
    cycle_num: int
    
    # Common fields
    current_allocation_pct: float = 0.0
    
    # For START
    reason: str = ""
    
    # For STATUS
    cycles_elapsed: int = 0
    trades_count: int = 0
    avg_pnl_per_trade: float = 0.0
    drawdown_pct: float = 0.0
    
    # For PASS/FAIL
    total_cycles: int = 0
    total_trades: int = 0
    final_drawdown: float = 0.0
    final_stability: float = 0.0
    failure_reason: str = ""
    
    def to_dict(self):
        return {k: (v.value if isinstance(v, Enum) else v) 
                for k, v in asdict(self).items()}
    
    def to_json(self):
        return json.dumps(self.to_dict())


@dataclass
class AllocationConfig:
    """Allocation configuration with hardened constraints"""
    initial_allocation_pct: float = 1.0
    max_allocation_pct: float = 5.0
    
    # PROBATION CONSTRAINTS (BOTH must be met)
    probation_min_cycles: int = 5  # Minimum time window
    probation_min_trades: int = 50  # Minimum sample size
    
    # Scaling
    scale_interval_cycles: int = 3
    scale_increment_pct: float = 1.0
    
    # Degradation detection
    degradation_drawdown_threshold: float = 3.0
    degradation_drift_threshold: float = -0.3
    
    # Scale down
    scale_down_reduction_factor: float = 0.5


@dataclass
class BotAllocationState:
    """State for a single bot's allocation"""
    bot_id: str
    state: AllocationState
    current_allocation_pct: float
    
    # Probation tracking
    probation_start_cycle: Optional[int] = None
    probation_cycles_elapsed: int = 0
    probation_trades_count: int = 0
    probation_start_time: str = ""
    
    # Scaling tracking
    last_scale_cycle: int = 0
    scale_ups_total: int = 0
    scale_downs_total: int = 0
    
    # Metrics
    timestamp_started: str = ""
    timestamp_last_update: str = ""
    
    def to_dict(self):
        return asdict(self)


class ProbationScalingEngineHardened:
    """
    PHASE 4.8 HARDENED: Probation with visibility + constraints
    """
    
    def __init__(self, config: Optional[AllocationConfig] = None):
        self.config = config or AllocationConfig()
        self.bot_allocations: Dict[str, BotAllocationState] = {}
        
        # Structured logs (queryable by THINK)
        self.probation_logs: List[ProbationLog] = []
        self.events = []
    
    def _log_probation(self, log_entry: ProbationLog):
        """Record structured probation log"""
        self.probation_logs.append(log_entry)
        print(f"[LOG] {log_entry.log_type}: {log_entry.to_json()}")
    
    def start_bot_probation(self, bot_id: str, cycle_num: int, reason: str = "restart") -> BotAllocationState:
        """
        PART 1: Start bot probation with full logging
        """
        now = datetime.utcnow().isoformat()
        
        state = BotAllocationState(
            bot_id=bot_id,
            state=AllocationState.PROBATION,
            current_allocation_pct=self.config.initial_allocation_pct,
            probation_start_cycle=cycle_num,
            probation_cycles_elapsed=0,
            probation_trades_count=0,
            probation_start_time=now,
            timestamp_started=now,
            timestamp_last_update=now,
        )
        
        self.bot_allocations[bot_id] = state
        
        # PART 1a: Log PROBATION_START
        log_entry = ProbationLog(
            log_type=ProbationLogType.PROBATION_START.value,
            bot_id=bot_id,
            timestamp=now,
            cycle_num=cycle_num,
            current_allocation_pct=self.config.initial_allocation_pct,
            reason=reason,
        )
        self._log_probation(log_entry)
        
        print(f"\n[BRAIN] PROBATION START — {bot_id} at {self.config.initial_allocation_pct}% allocation ({reason})")
        print(f"        Constraints: {self.config.probation_min_cycles} cycles + {self.config.probation_min_trades} trades")
        self.events.append((cycle_num, 'PROBATION_START', bot_id))
        
        return state
    
    def record_probation_trade(self, bot_id: str):
        """Record trade during probation"""
        if bot_id in self.bot_allocations:
            self.bot_allocations[bot_id].probation_trades_count += 1
    
    def get_probation_status(self, bot_id: str, cycle_num: int) -> Tuple[int, int, bool, bool]:
        """
        Get current probation status
        
        Returns: (cycles_elapsed, trades_count, cycles_met, trades_met)
        """
        if bot_id not in self.bot_allocations:
            return 0, 0, False, False
        
        alloc = self.bot_allocations[bot_id]
        cycles_elapsed = cycle_num - alloc.probation_start_cycle
        trades_count = alloc.probation_trades_count
        
        cycles_met = cycles_elapsed >= self.config.probation_min_cycles
        trades_met = trades_count >= self.config.probation_min_trades
        
        return cycles_elapsed, trades_count, cycles_met, trades_met
    
    def check_probation_status(self,
                              bot_id: str,
                              cycle_num: int,
                              recent_drawdown_pct: float = 0.0,
                              recent_drift: float = 0.0) -> Tuple[bool, str]:
        """
        PART 2: Check if probation passes (BOTH constraints required)
        
        Returns: (probation_passed, reason)
        """
        if bot_id not in self.bot_allocations:
            return False, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        now = datetime.utcnow().isoformat()
        
        if alloc.state != AllocationState.PROBATION:
            return False, "not_in_probation"
        
        # Get current status
        cycles_elapsed, trades_count, cycles_met, trades_met = self.get_probation_status(bot_id, cycle_num)
        alloc.probation_cycles_elapsed = cycles_elapsed
        alloc.timestamp_last_update = now
        
        # PART 1b: Log PROBATION_STATUS (optional but preferred)
        log_status = ProbationLog(
            log_type=ProbationLogType.PROBATION_STATUS.value,
            bot_id=bot_id,
            timestamp=now,
            cycle_num=cycle_num,
            current_allocation_pct=alloc.current_allocation_pct,
            cycles_elapsed=cycles_elapsed,
            trades_count=trades_count,
            drawdown_pct=recent_drawdown_pct,
        )
        self._log_probation(log_status)
        
        # Check for early degradation
        if recent_drawdown_pct > self.config.degradation_drawdown_threshold:
            log_fail = ProbationLog(
                log_type=ProbationLogType.PROBATION_FAIL.value,
                bot_id=bot_id,
                timestamp=now,
                cycle_num=cycle_num,
                total_cycles=cycles_elapsed,
                total_trades=trades_count,
                final_drawdown=recent_drawdown_pct,
                failure_reason=f"drawdown_breach ({recent_drawdown_pct:.1f}%)",
            )
            self._log_probation(log_fail)
            
            print(f"\n[BRAIN] PROBATION FAILED — {bot_id}")
            print(f"        Reason: drawdown {recent_drawdown_pct:.1f}% exceeds {self.config.degradation_drawdown_threshold}%")
            self.events.append((cycle_num, 'PROBATION_FAILED_DRAWDOWN', bot_id))
            return False, f"degradation_drawdown ({recent_drawdown_pct:.1f}%)"
        
        if recent_drift < self.config.degradation_drift_threshold:
            log_fail = ProbationLog(
                log_type=ProbationLogType.PROBATION_FAIL.value,
                bot_id=bot_id,
                timestamp=now,
                cycle_num=cycle_num,
                total_cycles=cycles_elapsed,
                total_trades=trades_count,
                final_stability=recent_drift,
                failure_reason=f"negative_drift ({recent_drift:.3f})",
            )
            self._log_probation(log_fail)
            
            print(f"\n[BRAIN] PROBATION FAILED — {bot_id}")
            print(f"        Reason: negative drift {recent_drift:.3f}")
            self.events.append((cycle_num, 'PROBATION_FAILED_DRIFT', bot_id))
            return False, f"degradation_drift ({recent_drift:.3f})"
        
        # PART 2: BOTH constraints must be met
        if not cycles_met:
            return False, f"insufficient_cycles ({cycles_elapsed}/{self.config.probation_min_cycles})"
        
        if not trades_met:
            return False, f"insufficient_trades ({trades_count}/{self.config.probation_min_trades})"
        
        # Probation passed
        log_pass = ProbationLog(
            log_type=ProbationLogType.PROBATION_PASS.value,
            bot_id=bot_id,
            timestamp=now,
            cycle_num=cycle_num,
            total_cycles=cycles_elapsed,
            total_trades=trades_count,
            final_drawdown=recent_drawdown_pct,
            final_stability=recent_drift,
        )
        self._log_probation(log_pass)
        
        print(f"\n[BRAIN] PROBATION PASSED — {bot_id}")
        print(f"        Cycles: {cycles_elapsed}/{self.config.probation_min_cycles} ✓")
        print(f"        Trades: {trades_count}/{self.config.probation_min_trades} ✓")
        print(f"        Drawdown: {recent_drawdown_pct:.1f}% (threshold: {self.config.degradation_drawdown_threshold}%)")
        
        alloc.state = AllocationState.ACTIVE
        alloc.last_scale_cycle = cycle_num
        self.events.append((cycle_num, 'PROBATION_PASSED', bot_id))
        
        return True, "probation_completed"
    
    def scale_up(self, bot_id: str, cycle_num: int) -> Tuple[float, str]:
        """Scale up after probation"""
        if bot_id not in self.bot_allocations:
            return 0.0, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        
        if alloc.state not in [AllocationState.PROBATION, AllocationState.ACTIVE]:
            return alloc.current_allocation_pct, "invalid_state_for_scaling"
        
        # Check enough cycles since last scale
        cycles_since_last = cycle_num - alloc.last_scale_cycle
        if cycles_since_last < self.config.scale_interval_cycles:
            return alloc.current_allocation_pct, "too_soon_to_scale"
        
        # Calculate new allocation
        new_allocation = alloc.current_allocation_pct + self.config.scale_increment_pct
        if new_allocation > self.config.max_allocation_pct:
            new_allocation = self.config.max_allocation_pct
        
        if new_allocation == alloc.current_allocation_pct:
            return new_allocation, "already_at_max"
        
        old_allocation = alloc.current_allocation_pct
        alloc.current_allocation_pct = new_allocation
        alloc.last_scale_cycle = cycle_num
        alloc.scale_ups_total += 1
        alloc.timestamp_last_update = datetime.utcnow().isoformat()
        
        print(f"[BRAIN] SCALE UP — {bot_id} from {old_allocation:.1f}% → {new_allocation:.1f}%")
        self.events.append((cycle_num, 'SCALE_UP', f"{bot_id} {old_allocation:.1f}% → {new_allocation:.1f}%"))
        
        return new_allocation, "scaled_up"
    
    def scale_down(self, bot_id: str, cycle_num: int, reason: str = "") -> Tuple[float, str]:
        """Scale down on degradation"""
        if bot_id not in self.bot_allocations:
            return 0.0, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        old_allocation = alloc.current_allocation_pct
        new_allocation = old_allocation * self.config.scale_down_reduction_factor
        
        if new_allocation < 0.1:
            new_allocation = 0.0
        
        alloc.current_allocation_pct = new_allocation
        alloc.scale_downs_total += 1
        alloc.last_scale_cycle = cycle_num
        alloc.timestamp_last_update = datetime.utcnow().isoformat()
        
        print(f"[BRAIN] SCALE DOWN — {bot_id} from {old_allocation:.1f}% → {new_allocation:.1f}% ({reason})")
        self.events.append((cycle_num, 'SCALE_DOWN', f"{bot_id} {old_allocation:.1f}% → {new_allocation:.1f}%"))
        
        if new_allocation == 0.0:
            alloc.state = AllocationState.STOPPED
            print(f"[BRAIN] ALLOCATION STOPPED — {bot_id} (allocation: 0%)")
            self.events.append((cycle_num, 'ALLOCATION_STOPPED', bot_id))
        
        return new_allocation, "scaled_down"
    
    def get_allocation(self, bot_id: str) -> float:
        """Get current allocation"""
        if bot_id not in self.bot_allocations:
            return 0.0
        return self.bot_allocations[bot_id].current_allocation_pct
    
    def reset_allocation_on_flat(self, bot_id: str, cycle_num: int):
        """Reset when bot goes FLAT"""
        if bot_id in self.bot_allocations:
            alloc = self.bot_allocations[bot_id]
            alloc.current_allocation_pct = 0.0
            alloc.state = AllocationState.FLAT
            
            print(f"[BRAIN] ALLOCATION RESET — {bot_id} (returning to FLAT)")
            self.events.append((cycle_num, 'ALLOCATION_RESET', bot_id))
    
    def query_probation_logs(self, bot_id: Optional[str] = None, log_type: Optional[str] = None) -> List[ProbationLog]:
        """
        Query probation logs (for THINK integration)
        
        Args:
            bot_id: Filter by bot_id (optional)
            log_type: Filter by log type (optional)
        
        Returns:
            List of matching probation logs
        """
        results = self.probation_logs
        
        if bot_id:
            results = [log for log in results if log.bot_id == bot_id]
        
        if log_type:
            results = [log for log in results if log.log_type == log_type]
        
        return results
    
    def get_probation_summary(self, bot_id: str) -> Optional[Dict]:
        """Get probation summary for bot"""
        pass_logs = self.query_probation_logs(bot_id, ProbationLogType.PROBATION_PASS.value)
        fail_logs = self.query_probation_logs(bot_id, ProbationLogType.PROBATION_FAIL.value)
        
        if not pass_logs and not fail_logs:
            return None
        
        return {
            'bot_id': bot_id,
            'probation_passed': len(pass_logs) > 0,
            'probation_failed': len(fail_logs) > 0,
            'pass_details': pass_logs[-1].to_dict() if pass_logs else None,
            'fail_details': fail_logs[-1].to_dict() if fail_logs else None,
        }


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 4.8 HARDENING: Probation Visibility + Constraints")
    print("="*80)
    
    config = AllocationConfig(
        probation_min_cycles=3,
        probation_min_trades=20,  # Requires 20 trades
        scale_interval_cycles=1,
    )
    engine = ProbationScalingEngineHardened(config)
    
    # Test 1: Fast burst (should FAIL)
    print("\nTest 1: Fast burst — high trades, low cycles (MUST FAIL)")
    print("-"*80)
    engine.start_bot_probation("bot_burst", cycle_num=1)
    
    # Record 50 trades in 1 cycle
    for i in range(50):
        engine.record_probation_trade("bot_burst")
    
    # Check probation (only 1 cycle passed)
    passed, reason = engine.check_probation_status("bot_burst", cycle_num=2, recent_drawdown_pct=0.5)
    assert not passed, f"Expected FAIL, got PASS"
    assert "insufficient_cycles" in reason
    print(f"✅ PASS: Burst blocked ({reason})\n")
    
    # Test 2: Slow stable (should PASS)
    print("Test 2: Slow stable — sufficient cycles + trades (MUST PASS)")
    print("-"*80)
    engine.start_bot_probation("bot_stable", cycle_num=10)
    
    # Record 20 trades over 3 cycles (minimum)
    for i in range(20):
        engine.record_probation_trade("bot_stable")
    
    passed, reason = engine.check_probation_status("bot_stable", cycle_num=13, recent_drawdown_pct=0.5)
    assert passed, f"Expected PASS, got FAIL: {reason}"
    print(f"✅ PASS: Stable bot passed ({reason})\n")
    
    # Test 3: Degradation during probation (should FAIL)
    print("Test 3: Degradation during probation (MUST FAIL)")
    print("-"*80)
    engine.start_bot_probation("bot_degrade", cycle_num=20)
    
    for i in range(20):
        engine.record_probation_trade("bot_degrade")
    
    passed, reason = engine.check_probation_status("bot_degrade", cycle_num=23, recent_drawdown_pct=5.0)
    assert not passed
    assert "drawdown" in reason
    print(f"✅ PASS: Degradation detected ({reason})\n")
    
    # Test 4: Log query (for THINK)
    print("Test 4: Query probation logs")
    print("-"*80)
    all_logs = engine.query_probation_logs()
    pass_logs = engine.query_probation_logs(log_type=ProbationLogType.PROBATION_PASS.value)
    
    print(f"Total logs: {len(all_logs)}")
    print(f"Pass logs: {len(pass_logs)}")
    assert len(pass_logs) == 1
    print(f"✅ PASS: Logs queryable\n")
    
    # Test 5: Summary
    print("Test 5: Get probation summary")
    print("-"*80)
    summary = engine.get_probation_summary("bot_stable")
    assert summary is not None
    assert summary['probation_passed']
    print(f"✅ PASS: Summary available\n")
    
    print("="*80)
    print("✅ ALL HARDENING TESTS PASSED")
    print("="*80 + "\n")
