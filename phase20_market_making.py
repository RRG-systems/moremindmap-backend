#!/usr/bin/env python3
"""
PHASE 20 - MARKET MAKING FOUNDATION

Build minimal, testable market-making loop. Capture bid/ask spreads.

Core strategy:
1. Place bid at (mid - spread_offset) and ask at (mid + spread_offset)
2. When bid fills: place offsetting ask at better price (capture spread)
3. When ask fills: place offsetting bid at better price (capture spread)
4. Track inventory, enforce caps, apply K3 regime suppression
5. Measure: spread captured, fill rate, inventory drift, PnL

Tests across 40 seeds, 200 ticks/seed, 5-10 markets per seed.
"""

import numpy as np
import pandas as pd
import json
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_SEEDS = 40
TICKS_PER_SEED = 200
MARKETS_PER_SEED = 8
MAX_INVENTORY_CAP = 5  # Max position size per market

MARKET_MAKING_PARAMS = {
    'spread_offset_bps': 30,  # Place bid/ask at mid ±30bps (60bps total width)
    'offset_improvement_bps': 10,  # Offsetting order improves by 10bps (capture spread)
    'order_fill_prob_base': 0.7,  # Base probability order gets filled
}

# Costs (realistic Polymarket)
COSTS = {
    'spread_bps': 20,
    'slippage_bps': 5,
    'taker_fee_bps': 100,  # 1% taker fee (Polymarket)
}
COST_PER_TRADE_BPS = sum(COSTS.values())

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class OrderSide(Enum):
    BID = "bid"
    ASK = "ask"

@dataclass
class Order:
    """Represents a single order."""
    order_id: int
    side: OrderSide
    price: float
    quantity: int
    tick_placed: int
    filled: bool = False
    fill_price: Optional[float] = None
    fill_tick: Optional[int] = None
    parent_order_id: Optional[int] = None  # Link to offsetting order

@dataclass
class Position:
    """Tracks inventory for a market."""
    market_id: str
    quantity: int = 0
    avg_entry_price: float = 0.0
    
    def get_mtm_value(self, current_price: float) -> float:
        if self.quantity == 0:
            return 0.0
        return self.quantity * (current_price - self.avg_entry_price)
    
    def add_position(self, qty: int, price: float):
        """Add qty at price."""
        if qty == 0:
            return
        
        new_qty = self.quantity + qty
        
        if new_qty == 0:
            self.quantity = 0
            self.avg_entry_price = 0.0
        elif (new_qty > 0 and self.quantity >= 0) or (new_qty < 0 and self.quantity <= 0):
            # Same direction: average in
            total_cost = self.quantity * self.avg_entry_price + qty * price
            self.avg_entry_price = total_cost / new_qty
            self.quantity = new_qty
        else:
            # Opposite direction: don't change avg entry
            self.quantity = new_qty
            if self.quantity == 0:
                self.avg_entry_price = 0.0

@dataclass
class MarketMakerState:
    """MM state for one market."""
    market_id: str
    ticks: List[float]
    
    active_orders: Dict[int, Order] = field(default_factory=dict)
    filled_orders: List[Order] = field(default_factory=list)
    position: Position = field(default_factory=lambda: Position(""))
    
    next_order_id: int = 0
    bid_fill_count: int = 0
    ask_fill_count: int = 0
    
    # Track round-trip spreads
    realized_pnl: float = 0.0
    round_trips: int = 0  # Number of completed bid-ask pairs
    
    # K3 tracking
    quotes_placed: int = 0
    quotes_cancelled_hostile: int = 0
    current_regime: str = "safe"
    
    def __post_init__(self):
        self.position.market_id = self.market_id

# ============================================================================
# K3 REGIME DETECTION
# ============================================================================

def detect_k3_regimes(ticks: List[float]) -> List[Tuple[int, int, str]]:
    """Detect hostile regimes (2+ consecutive down-ticks)."""
    regimes = []
    current_regime = None
    regime_start = 0
    consecutive_downs = 0
    
    for i in range(len(ticks)):
        if i == 0:
            current_regime = 'safe'
            continue
        
        price_change = ticks[i] - ticks[i-1]
        if price_change < 0:
            consecutive_downs += 1
        else:
            consecutive_downs = 0
        
        is_hostile = consecutive_downs >= 2
        
        if current_regime == 'safe' and is_hostile:
            regimes.append((regime_start, i, current_regime))
            current_regime = 'hostile'
            regime_start = i
        elif current_regime == 'hostile' and not is_hostile:
            regimes.append((regime_start, i, current_regime))
            current_regime = 'safe'
            regime_start = i
    
    if current_regime:
        regimes.append((regime_start, len(ticks), current_regime))
    
    return regimes

def get_regime_at_tick(tick_idx: int, regimes: List[Tuple[int, int, str]]) -> str:
    """Get regime at tick."""
    for start, end, regime_type in regimes:
        if start <= tick_idx < end:
            return regime_type
    return "safe"

# ============================================================================
# ORDER FILL SIMULATION
# ============================================================================

def simulate_order_fill(order: Order, mid_price: float, regime: str,
                       tick_idx: int, seed: int) -> Tuple[bool, Optional[float]]:
    """Simulate order fill."""
    np.random.seed(seed + order.order_id * 10000 + tick_idx)
    
    # Distance from mid
    if order.side == OrderSide.BID:
        distance_bps = (mid_price - order.price) / mid_price * 10000
    else:
        distance_bps = (order.price - mid_price) / mid_price * 10000
    
    # Base fill probability
    fill_prob = MARKET_MAKING_PARAMS['order_fill_prob_base']
    
    # Reduce in hostile regime
    if regime == "hostile":
        fill_prob *= 0.7
    
    # Reduce with distance from mid
    fill_prob *= (1.0 - distance_bps / 500)  # 500bps away = 0% prob
    fill_prob = np.clip(fill_prob, 0.05, 0.95)
    
    if np.random.random() < fill_prob:
        return True, order.price
    
    return False, None

# ============================================================================
# MARKET MAKING ENGINE
# ============================================================================

def run_single_market_mm(market_id: str, ticks: List[float], seed: int) -> MarketMakerState:
    """Run MM for one market."""
    mm_state = MarketMakerState(market_id=market_id, ticks=ticks)
    mm_state.position.market_id = market_id
    
    regimes = detect_k3_regimes(ticks)
    
    # Track pending bids and asks separately
    pending_bids = []  # List of (order_id, entry_price, qty)
    pending_asks = []  # List of (order_id, entry_price, qty)
    
    for tick_idx in range(1, len(ticks)):
        current_price = ticks[tick_idx]
        regime = get_regime_at_tick(tick_idx, regimes)
        mm_state.current_regime = regime
        
        # STEP 1: Process fills on existing orders
        filled_this_tick = []
        for order_id, order in list(mm_state.active_orders.items()):
            filled, fill_price = simulate_order_fill(
                order, current_price, regime, tick_idx, seed
            )
            
            if filled:
                order.filled = True
                order.fill_price = fill_price
                order.fill_tick = tick_idx
                filled_this_tick.append(order)
                mm_state.filled_orders.append(order)
                del mm_state.active_orders[order_id]
                
                # Update inventory
                if order.side == OrderSide.BID:
                    mm_state.bid_fill_count += 1
                    mm_state.position.add_position(order.quantity, fill_price)
                    pending_bids.append((order_id, fill_price, order.quantity))
                else:
                    mm_state.ask_fill_count += 1
                    mm_state.position.add_position(-order.quantity, fill_price)
                    pending_asks.append((order_id, fill_price, order.quantity))
        
        # STEP 2: Match pending bids with asks to realize spreads
        while pending_bids and pending_asks:
            bid_id, bid_price, bid_qty = pending_bids.pop(0)
            ask_id, ask_price, ask_qty = pending_asks.pop(0)
            
            # Spread realized
            spread_bps = (ask_price - bid_price) / bid_price * 10000
            if spread_bps > 0:
                mm_state.realized_pnl += spread_bps / 10000
                mm_state.round_trips += 1
            
            # If quantities don't match, re-queue
            if bid_qty < ask_qty:
                pending_asks.insert(0, (ask_id, ask_price, ask_qty - bid_qty))
            elif ask_qty < bid_qty:
                pending_bids.insert(0, (bid_id, bid_price, bid_qty - ask_qty))
        
        # STEP 3: Place offsetting orders for fresh fills
        for order in filled_this_tick:
            mid_price = current_price
            
            if order.side == OrderSide.BID:
                # Bid filled; place ask to capture spread
                improvement = MARKET_MAKING_PARAMS['offset_improvement_bps'] / 10000
                ask_price = mid_price * (1 + improvement)
                
                if mm_state.position.quantity - order.quantity <= MAX_INVENTORY_CAP:
                    new_order = Order(
                        order_id=mm_state.next_order_id,
                        side=OrderSide.ASK,
                        price=ask_price,
                        quantity=order.quantity,
                        tick_placed=tick_idx,
                        parent_order_id=order.order_id
                    )
                    mm_state.active_orders[mm_state.next_order_id] = new_order
                    mm_state.next_order_id += 1
                    mm_state.quotes_placed += 1
            
            else:  # ASK filled
                # Ask filled; place bid to capture spread
                improvement = MARKET_MAKING_PARAMS['offset_improvement_bps'] / 10000
                bid_price = mid_price * (1 - improvement)
                
                if mm_state.position.quantity + order.quantity >= -MAX_INVENTORY_CAP:
                    new_order = Order(
                        order_id=mm_state.next_order_id,
                        side=OrderSide.BID,
                        price=bid_price,
                        quantity=order.quantity,
                        tick_placed=tick_idx,
                        parent_order_id=order.order_id
                    )
                    mm_state.active_orders[mm_state.next_order_id] = new_order
                    mm_state.next_order_id += 1
                    mm_state.quotes_placed += 1
        
        # STEP 4: Place new MM quotes (if safe regime)
        if regime == "safe":
            can_place_bid = mm_state.position.quantity < MAX_INVENTORY_CAP
            can_place_ask = mm_state.position.quantity > -MAX_INVENTORY_CAP
            
            active_bids = sum(1 for o in mm_state.active_orders.values() if o.side == OrderSide.BID)
            active_asks = sum(1 for o in mm_state.active_orders.values() if o.side == OrderSide.ASK)
            
            # Place bid if we have capacity
            if can_place_bid and active_bids < 1:
                offset = MARKET_MAKING_PARAMS['spread_offset_bps'] / 10000
                bid_price = current_price * (1 - offset)
                
                bid_order = Order(
                    order_id=mm_state.next_order_id,
                    side=OrderSide.BID,
                    price=bid_price,
                    quantity=1,
                    tick_placed=tick_idx
                )
                mm_state.active_orders[mm_state.next_order_id] = bid_order
                mm_state.next_order_id += 1
                mm_state.quotes_placed += 1
            
            # Place ask if we have capacity
            if can_place_ask and active_asks < 1:
                offset = MARKET_MAKING_PARAMS['spread_offset_bps'] / 10000
                ask_price = current_price * (1 + offset)
                
                ask_order = Order(
                    order_id=mm_state.next_order_id,
                    side=OrderSide.ASK,
                    price=ask_price,
                    quantity=1,
                    tick_placed=tick_idx
                )
                mm_state.active_orders[mm_state.next_order_id] = ask_order
                mm_state.next_order_id += 1
                mm_state.quotes_placed += 1
        
        else:  # regime == "hostile"
            # Cancel all quotes in hostile regime
            for order in list(mm_state.active_orders.values()):
                mm_state.quotes_cancelled_hostile += 1
                del mm_state.active_orders[order.order_id]
    
    return mm_state

# ============================================================================
# SIMULATION
# ============================================================================

def generate_synthetic_price_series(seed: int, num_ticks: int = 200) -> List[float]:
    """Generate realistic price series."""
    np.random.seed(seed)
    
    prices = [0.5]
    
    for _ in range(num_ticks - 1):
        step = np.random.normal(0, 0.01)
        reversion = (0.5 - prices[-1]) * 0.05
        new_price = prices[-1] + step + reversion
        new_price = np.clip(new_price, 0.01, 0.99)
        prices.append(new_price)
    
    return prices

def run_full_simulation(num_seeds: int = NUM_SEEDS,
                       ticks_per_seed: int = TICKS_PER_SEED,
                       markets_per_seed: int = MARKETS_PER_SEED):
    """Run full simulation."""
    print(f"""
================================================================================
PHASE 20 - MARKET MAKING FOUNDATION
================================================================================

Configuration:
  Seeds: {num_seeds}
  Ticks per seed: {ticks_per_seed}
  Markets per seed: {markets_per_seed}
  Total markets: {num_seeds * markets_per_seed}

Market Making Parameters:
  Spread offset: {MARKET_MAKING_PARAMS['spread_offset_bps']} bps
  Offsetting improvement: {MARKET_MAKING_PARAMS['offset_improvement_bps']} bps
  Base fill probability: {MARKET_MAKING_PARAMS['order_fill_prob_base']:.1%}
  Max inventory cap: ±{MAX_INVENTORY_CAP}

Costs (per trade):
  Spread: {COSTS['spread_bps']} bps
  Slippage: {COSTS['slippage_bps']} bps
  Taker fee: {COSTS['taker_fee_bps']} bps
  Total: {COST_PER_TRADE_BPS} bps

Running simulation...
================================================================================
""")
    
    results = {
        'total_orders_placed': 0,
        'total_bid_fills': 0,
        'total_ask_fills': 0,
        'total_fills': 0,
        'fill_rate_pct': 0.0,
        'total_round_trips': 0,
        'realized_spread_pnl_gross': 0.0,
        'avg_spread_per_round_trip_bps': 0.0,
        'total_pnl_gross': 0.0,
        'total_cost_bps': 0.0,
        'total_pnl_net': 0.0,
        'final_inventory': 0,
        'quotes_placed': 0,
        'quotes_cancelled_hostile': 0,
        'k3_suppression_rate': 0.0,
    }
    
    all_markets = []
    
    for seed in range(num_seeds):
        if (seed + 1) % 10 == 0:
            print(f"  Seed {seed + 1}/{num_seeds}")
        
        for market_idx in range(markets_per_seed):
            market_id = f"seed{seed:02d}_market{market_idx:02d}"
            ticks = generate_synthetic_price_series(seed + market_idx, ticks_per_seed)
            mm_state = run_single_market_mm(market_id, ticks, seed)
            all_markets.append(mm_state)
            
            # Accumulate results
            results['total_orders_placed'] += mm_state.next_order_id
            results['total_bid_fills'] += mm_state.bid_fill_count
            results['total_ask_fills'] += mm_state.ask_fill_count
            results['total_fills'] += mm_state.bid_fill_count + mm_state.ask_fill_count
            results['total_round_trips'] += mm_state.round_trips
            results['realized_spread_pnl_gross'] += mm_state.realized_pnl
            results['final_inventory'] += mm_state.position.quantity
            results['quotes_placed'] += mm_state.quotes_placed
            results['quotes_cancelled_hostile'] += mm_state.quotes_cancelled_hostile
    
    # Post-process
    results['total_fills'] = max(1, results['total_fills'])
    results['fill_rate_pct'] = (results['total_fills'] / max(1, results['total_orders_placed'])) * 100
    results['total_pnl_gross'] = results['realized_spread_pnl_gross']
    results['total_cost_bps'] = COST_PER_TRADE_BPS * results['total_fills']
    results['total_pnl_net'] = results['total_pnl_gross'] * 10000 - results['total_cost_bps']
    
    if results['total_round_trips'] > 0:
        results['avg_spread_per_round_trip_bps'] = (results['realized_spread_pnl_gross'] / results['total_round_trips']) * 10000
    
    if results['quotes_placed'] > 0:
        results['k3_suppression_rate'] = (results['quotes_cancelled_hostile'] / results['quotes_placed']) * 100
    
    return results, all_markets

# ============================================================================
# REPORTING
# ============================================================================

def print_results_table(results: dict):
    """Print results."""
    print(f"""
================================================================================
PHASE 20 - RESULTS
================================================================================

CORE METRICS

Metric                          | Value
{'-'*70}
Total orders placed             | {results['total_orders_placed']:>10}
Total bid fills                 | {results['total_bid_fills']:>10}
Total ask fills                 | {results['total_ask_fills']:>10}
Total fills (both sides)        | {results['total_fills']:>10}
Fill rate                       | {results['fill_rate_pct']:>9.2f}%

SPREAD CAPTURE

Metric                          | Value
{'-'*70}
Round-trip spreads realized     | {results['total_round_trips']:>10}
Avg spread per round-trip       | {results['avg_spread_per_round_trip_bps']:>9.2f} bps
Cost per trade                  | {COST_PER_TRADE_BPS:>10} bps

P&L ACCOUNTING

Metric                          | Value
{'-'*70}
Gross PnL (spread capture)      | {results['total_pnl_gross']:>10.6f}
Total cost drag (bps)           | {results['total_cost_bps']:>10.2f}
Net PnL (after costs)           | {results['total_pnl_net']:>10.2f}
Net PnL per fill                | {results['total_pnl_net'] / results['total_fills']:>10.6f}

INVENTORY & RISK

Metric                          | Value
{'-'*70}
Final net inventory             | {results['final_inventory']:>10}
Avg final position              | {results['final_inventory'] / (NUM_SEEDS * MARKETS_PER_SEED):>10.2f}

K3 REGIME SUPPRESSION

Metric                          | Value
{'-'*70}
Quotes placed (total)           | {results['quotes_placed']:>10}
Quotes cancelled (hostile)      | {results['quotes_cancelled_hostile']:>10}
K3 suppression rate             | {results['k3_suppression_rate']:>9.2f}%

================================================================================
""")

def answer_key_questions(results: dict):
    """Answer 4 key questions."""
    print("""
================================================================================
KEY QUESTIONS - SPREAD CAPTURE VIABILITY
================================================================================

Q1: Does spread capture generate positive PnL before costs?
""")
    
    gross_pnl = results['total_pnl_gross']
    if gross_pnl > 0.01:
        print(f"   ✓ YES: Gross PnL = {gross_pnl:.6f}")
        print(f"     Spread capture is VIABLE at the fundamental level.")
        q1_pass = True
    else:
        print(f"   ✗ NO: Gross PnL = {gross_pnl:.6f}")
        print(f"     Insufficient spread capture.")
        q1_pass = False
    
    print("""
Q2: How often are we filled vs missed? (Participation rate)
""")
    fill_rate = results['fill_rate_pct']
    if fill_rate > 50:
        print(f"   ✓ STRONG: Fill rate = {fill_rate:.1f}%")
        print(f"     Good participation in available opportunities.")
        q2_pass = True
    elif fill_rate > 30:
        print(f"   ~ MODERATE: Fill rate = {fill_rate:.1f}%")
        print(f"     Reasonable but not optimal.")
        q2_pass = True
    else:
        print(f"   ✗ WEAK: Fill rate = {fill_rate:.1f}%")
        print(f"     Poor participation.")
        q2_pass = False
    
    print("""
Q3: Does inventory drift accumulate over time? (Imbalance risk)
""")
    avg_inventory = results['final_inventory'] / (NUM_SEEDS * MARKETS_PER_SEED)
    if abs(avg_inventory) < 0.5:
        print(f"   ✓ CONTROLLED: Final avg inventory = {avg_inventory:.3f}")
        print(f"     Excellent balance.")
        q3_pass = True
    elif abs(avg_inventory) < 1.5:
        print(f"   ~ ACCEPTABLE: Final avg inventory = {avg_inventory:.3f}")
        print(f"     Some drift but manageable.")
        q3_pass = True
    else:
        print(f"   ✗ DRIFTING: Final avg inventory = {avg_inventory:.3f}")
        print(f"     Significant accumulation.")
        q3_pass = False
    
    print("""
Q4: Does K3 reduce adverse fills? (Regime protection)
""")
    suppression_rate = results['k3_suppression_rate']
    if suppression_rate > 30:
        print(f"   ✓ ACTIVE: Suppression rate = {suppression_rate:.1f}%")
        print(f"     K3 blocking significant hostile activity.")
        q4_pass = True
    elif suppression_rate > 10:
        print(f"   ~ PARTIAL: Suppression rate = {suppression_rate:.1f}%")
        print(f"     K3 providing some protection.")
        q4_pass = True
    else:
        print(f"   ✗ MINIMAL: Suppression rate = {suppression_rate:.1f}%")
        print(f"     Limited K3 impact.")
        q4_pass = False
    
    print("""
================================================================================
VERDICT
================================================================================
""")
    
    passed = sum([q1_pass, q2_pass, q3_pass, q4_pass])
    
    if passed >= 3:
        print(f"✓ SPREAD CAPTURE IS FUNDAMENTALLY VIABLE")
        print(f"  ({passed}/4 viability checks passed)")
        print(f"\n  Market making shows promise. Ready for:")
        print(f"  - Real data validation")
        print(f"  - Spread width optimization")
        print(f"  - Cost model refinement")
    elif passed == 2:
        print(f"~ SPREAD CAPTURE IS MARGINAL")
        print(f"  ({passed}/4 viability checks passed)")
        print(f"\n  Needs improvement in key areas.")
    else:
        print(f"✗ SPREAD CAPTURE IS NOT VIABLE")
        print(f"  ({passed}/4 viability checks passed)")
        print(f"\n  Fundamental issues present.")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results, markets = run_full_simulation()
    print_results_table(results)
    answer_key_questions(results)
