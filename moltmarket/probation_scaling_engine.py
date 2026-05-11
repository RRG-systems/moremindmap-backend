#!/usr/bin/env python3
"""
PHASE 4.8: PROBATION + SCALING ENGINE

Controlled capital deployment after restart.

Principle: Earn risk. Do not assume it.

Every bot starts at 1% allocation.
Only scales if stability holds.
Cuts or reverts immediately on degradation.
"""

from datetime import datetime
from typing import Dict, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum


class AllocationState(Enum):
    """Allocation lifecycle states"""
    FLAT = 0  # No allocation
    PROBATION = 1  # Initial 1% monitoring
    ACTIVE = 2  # Scaled beyond probation
    DEGRADING = 3  # Under monitoring for degradation
    STOPPED = 4  # Hard stop, 0% allocation


@dataclass
class AllocationConfig:
    """Allocation configuration"""
    initial_allocation_pct: float = 1.0
    max_allocation_pct: float = 5.0
    
    # Probation
    probation_min_cycles: int = 5
    probation_min_trades: int = 20
    
    # Scaling
    scale_interval_cycles: int = 3  # Cycles between scale increments
    scale_increment_pct: float = 1.0  # Increment per scale up
    
    # Degradation detection
    degradation_drawdown_threshold: float = 3.0  # % drawdown to trigger scale down
    degradation_drift_threshold: float = -0.3  # Avg P&L per trade
    
    # Scale down
    scale_down_reduction_factor: float = 0.5  # Cut allocation in half


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
    
    # Scaling tracking
    last_scale_cycle: int = 0
    scale_ups_total: int = 0
    scale_downs_total: int = 0
    
    # Degradation
    consecutive_degradation_detections: int = 0
    
    # Metrics
    timestamp_started: str = ""
    timestamp_last_update: str = ""
    
    def to_dict(self):
        return asdict(self)


class ProbationScalingEngine:
    """
    PHASE 4.8: Probation + Scaling

    Controls capital deployment with probation monitoring.
    """
    
    def __init__(self, config: Optional[AllocationConfig] = None):
        self.config = config or AllocationConfig()
        
        # Track all bots' allocation states
        self.bot_allocations: Dict[str, BotAllocationState] = {}
        
        # Logs
        self.events = []
    
    def start_bot_probation(self, bot_id: str, cycle_num: int) -> BotAllocationState:
        """
        PART 1: Start new bot at 1% allocation (PROBATION)
        """
        state = BotAllocationState(
            bot_id=bot_id,
            state=AllocationState.PROBATION,
            current_allocation_pct=self.config.initial_allocation_pct,
            probation_start_cycle=cycle_num,
            probation_cycles_elapsed=0,
            probation_trades_count=0,
            timestamp_started=datetime.utcnow().isoformat(),
            timestamp_last_update=datetime.utcnow().isoformat(),
        )
        
        self.bot_allocations[bot_id] = state
        
        log_msg = f"[BRAIN] PROBATION START — {bot_id} at {self.config.initial_allocation_pct}% allocation"
        print(f"\n{log_msg}")
        self.events.append((cycle_num, 'PROBATION_START', bot_id))
        
        return state
    
    def record_probation_trade(self, bot_id: str):
        """Record trade during probation"""
        if bot_id in self.bot_allocations:
            self.bot_allocations[bot_id].probation_trades_count += 1
    
    def check_probation_status(self, 
                              bot_id: str, 
                              cycle_num: int,
                              recent_drawdown_pct: float = 0.0,
                              recent_drift: float = 0.0) -> Tuple[bool, str]:
        """
        PART 2: Check if probation is passed or failed
        
        Returns: (probation_passed, reason)
        """
        if bot_id not in self.bot_allocations:
            return False, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        
        if alloc.state != AllocationState.PROBATION:
            return False, "not_in_probation"
        
        # Update cycle count
        alloc.probation_cycles_elapsed = cycle_num - alloc.probation_start_cycle
        alloc.timestamp_last_update = datetime.utcnow().isoformat()
        
        # Check for early degradation
        if recent_drawdown_pct > self.config.degradation_drawdown_threshold:
            print(f"[BRAIN] PROBATION FAILED — {bot_id} (drawdown: {recent_drawdown_pct:.1f}%)")
            self.events.append((cycle_num, 'PROBATION_FAILED_DRAWDOWN', bot_id))
            return False, f"degradation_drawdown ({recent_drawdown_pct:.1f}%)"
        
        if recent_drift < self.config.degradation_drift_threshold:
            print(f"[BRAIN] PROBATION FAILED — {bot_id} (negative drift: {recent_drift:.3f})")
            self.events.append((cycle_num, 'PROBATION_FAILED_DRIFT', bot_id))
            return False, f"degradation_drift ({recent_drift:.3f})"
        
        # Check if probation window completed
        min_cycles_met = alloc.probation_cycles_elapsed >= self.config.probation_min_cycles
        min_trades_met = alloc.probation_trades_count >= self.config.probation_min_trades
        
        if not (min_cycles_met and min_trades_met):
            return False, "probation_incomplete"
        
        # Probation passed
        print(f"[BRAIN] PROBATION PASSED — {bot_id}")
        print(f"        Cycles: {alloc.probation_cycles_elapsed}, Trades: {alloc.probation_trades_count}")
        
        alloc.state = AllocationState.ACTIVE
        alloc.last_scale_cycle = cycle_num
        self.events.append((cycle_num, 'PROBATION_PASSED', bot_id))
        
        return True, "probation_completed"
    
    def scale_up(self, bot_id: str, cycle_num: int) -> Tuple[float, str]:
        """
        PART 3: Scale up after probation or continued stability
        
        Returns: (new_allocation_pct, reason)
        """
        if bot_id not in self.bot_allocations:
            return 0.0, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        
        if alloc.state not in [AllocationState.PROBATION, AllocationState.ACTIVE]:
            return alloc.current_allocation_pct, "invalid_state_for_scaling"
        
        # Check if enough cycles since last scale
        cycles_since_last = cycle_num - alloc.last_scale_cycle
        if cycles_since_last < self.config.scale_interval_cycles:
            return alloc.current_allocation_pct, "too_soon_to_scale"
        
        # Calculate new allocation
        new_allocation = alloc.current_allocation_pct + self.config.scale_increment_pct
        
        # Respect max cap
        if new_allocation > self.config.max_allocation_pct:
            new_allocation = self.config.max_allocation_pct
        
        if new_allocation == alloc.current_allocation_pct:
            return new_allocation, "already_at_max"
        
        # Apply scale up
        old_allocation = alloc.current_allocation_pct
        alloc.current_allocation_pct = new_allocation
        alloc.last_scale_cycle = cycle_num
        alloc.scale_ups_total += 1
        alloc.timestamp_last_update = datetime.utcnow().isoformat()
        
        print(f"[BRAIN] SCALE UP — {bot_id} from {old_allocation:.1f}% → {new_allocation:.1f}%")
        self.events.append((cycle_num, 'SCALE_UP', f"{bot_id} {old_allocation:.1f}% → {new_allocation:.1f}%"))
        
        return new_allocation, "scaled_up"
    
    def scale_down(self, bot_id: str, cycle_num: int, reason: str = "") -> Tuple[float, str]:
        """
        PART 4: Scale down due to degradation
        
        Returns: (new_allocation_pct, reason)
        """
        if bot_id not in self.bot_allocations:
            return 0.0, "bot_not_found"
        
        alloc = self.bot_allocations[bot_id]
        
        old_allocation = alloc.current_allocation_pct
        
        # Cut allocation in half
        new_allocation = old_allocation * self.config.scale_down_reduction_factor
        
        # Floor at 0
        if new_allocation < 0.1:
            new_allocation = 0.0
        
        alloc.current_allocation_pct = new_allocation
        alloc.scale_downs_total += 1
        alloc.consecutive_degradation_detections += 1
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
        """Get current allocation for bot"""
        if bot_id not in self.bot_allocations:
            return 0.0
        return self.bot_allocations[bot_id].current_allocation_pct
    
    def reset_allocation_on_flat(self, bot_id: str, cycle_num: int):
        """PART 6: Reset allocation when bot goes FLAT"""
        if bot_id in self.bot_allocations:
            alloc = self.bot_allocations[bot_id]
            alloc.current_allocation_pct = 0.0
            alloc.state = AllocationState.FLAT
            alloc.consecutive_degradation_detections = 0
            
            print(f"[BRAIN] ALLOCATION RESET — {bot_id} (returning to FLAT)")
            self.events.append((cycle_num, 'ALLOCATION_RESET', bot_id))
    
    def get_all_allocations(self) -> Dict[str, float]:
        """Get all current allocations"""
        return {bot_id: alloc.current_allocation_pct 
                for bot_id, alloc in self.bot_allocations.items()}
    
    def get_allocation_state(self, bot_id: str) -> Optional[BotAllocationState]:
        """Get full allocation state for bot"""
        return self.bot_allocations.get(bot_id)
    
    def print_summary(self, cycle_num: int = 0):
        """Print allocation summary"""
        print(f"\n[ALLOCATIONS] Cycle {cycle_num}")
        print("-" * 60)
        
        for bot_id, alloc in self.bot_allocations.items():
            print(f"  {bot_id:12s} | {alloc.state.name:10s} | {alloc.current_allocation_pct:5.1f}% | "
                  f"UPs: {alloc.scale_ups_total} | DOWNs: {alloc.scale_downs_total}")
        
        print("-" * 60)


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 4.8: PROBATION + SCALING ENGINE — Tests")
    print("="*80)
    
    config = AllocationConfig(
        probation_min_cycles=3,
        probation_min_trades=10,
        scale_interval_cycles=2,
    )
    engine = ProbationScalingEngine(config)
    
    # Test 1: Start bot at 1%
    print("\nTest 1: Start bot at 1% probation")
    print("-"*80)
    state = engine.start_bot_probation("bot_001", cycle_num=1)
    assert state.current_allocation_pct == 1.0
    assert state.state == AllocationState.PROBATION
    print("✅ PASS\n")
    
    # Test 2: Record trades during probation
    print("Test 2: Record trades during probation")
    print("-"*80)
    for i in range(10):
        engine.record_probation_trade("bot_001")
    assert engine.bot_allocations["bot_001"].probation_trades_count == 10
    print("✅ PASS\n")
    
    # Test 3: Check probation not yet passed
    print("Test 3: Check probation incomplete")
    print("-"*80)
    passed, reason = engine.check_probation_status("bot_001", cycle_num=2)
    assert not passed
    assert reason == "probation_incomplete"
    print("✅ PASS\n")
    
    # Test 4: Complete probation
    print("Test 4: Complete probation at cycle 4")
    print("-"*80)
    for i in range(10):  # Total 20 trades
        engine.record_probation_trade("bot_001")
    passed, reason = engine.check_probation_status("bot_001", cycle_num=4, 
                                                   recent_drawdown_pct=1.0, 
                                                   recent_drift=0.1)
    assert passed
    assert engine.bot_allocations["bot_001"].state == AllocationState.ACTIVE
    print("✅ PASS\n")
    
    # Test 5: Scale up after probation
    print("Test 5: Scale up after probation")
    print("-"*80)
    new_alloc, reason = engine.scale_up("bot_001", cycle_num=7)
    assert new_alloc == 2.0
    assert engine.bot_allocations["bot_001"].scale_ups_total == 1
    print("✅ PASS\n")
    
    # Test 6: Scale down on degradation
    print("Test 6: Scale down on degradation")
    print("-"*80)
    new_alloc, reason = engine.scale_down("bot_001", cycle_num=8, reason="instability")
    assert new_alloc == 1.0  # 2.0 * 0.5
    assert engine.bot_allocations["bot_001"].scale_downs_total == 1
    print("✅ PASS\n")
    
    # Test 7: Reset allocation on FLAT
    print("Test 7: Reset allocation on FLAT")
    print("-"*80)
    engine.reset_allocation_on_flat("bot_001", cycle_num=9)
    assert engine.get_allocation("bot_001") == 0.0
    assert engine.bot_allocations["bot_001"].state == AllocationState.FLAT
    print("✅ PASS\n")
    
    # Test 8: Probation fails on drawdown
    print("Test 8: Probation fails on excessive drawdown")
    print("-"*80)
    state2 = engine.start_bot_probation("bot_002", cycle_num=10)
    for i in range(10):
        engine.record_probation_trade("bot_002")
    passed, reason = engine.check_probation_status("bot_002", cycle_num=13,
                                                   recent_drawdown_pct=5.0)  # Exceed threshold
    assert not passed
    assert "drawdown" in reason
    print("✅ PASS\n")
    
    print("="*80)
    print("✅ ALL PROBATION + SCALING TESTS PASSED")
    print("="*80 + "\n")
