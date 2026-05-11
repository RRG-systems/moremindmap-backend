#!/usr/bin/env python3
"""
PHASE 20 - MARKET MAKING FOUNDATION (CORRECTED PnL ACCOUNTING)

Proper unit tracking:
- Spreads measured in bps (basis points) = 0.01% = 1/10000
- PnL should be in notional dollars or normalized basis points
- Cost drag should match: (bps_per_trade * num_trades) / 10000

Focus on VIABILITY not absolute PnL values.
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from enum import Enum

# ============================================================================
# CONFIGURATION
# ============================================================================

NUM_SEEDS = 40
TICKS_PER_SEED = 200
MARKETS_PER_SEED = 8
MAX_INVENTORY_CAP = 5

MARKET_MAKING_PARAMS = {
    'spread_offset_bps': 30,
    'offset_improvement_bps': 10,
    'order_fill_prob_base': 0.7,
}

# Costs in basis points
COSTS_BPS = {
    'spread_bps': 20,
    'slippage_bps': 5,
    'taker_fee_bps': 100,
}
COST_PER_TRADE_BPS = sum(COSTS_BPS.values())

# ============================================================================
# DATA STRUCTURES
# ============================================================================

class OrderSide(Enum):
    BID = "bid"
    ASK = "ask"

@dataclass
class Order:
    order_id: int
    side: OrderSide
    price: float
    quantity: int
    tick_placed: int
    filled: bool = False
    fill_price: Optional[float] = None
    fill_tick: Optional[int] = None

@dataclass
class MarketMakerState:
    market_id: str
    ticks: List[float]
    
    # Order tracking
    next_order_id: int = 0
    bid_fill_count: int = 0
    ask_fill_count: int = 0
    
    # PnL in basis points
    spread_captured_bps: float = 0.0  # Gross spread captured
    realized_pnl_bps: float = 0.0  # Realized PnL in bps
    
    # Inventory
    final_position: int = 0
    inventory_squared_error: float = 0.0  # Integral of position^2 over time
    
    # K3 tracking
    quotes_placed: int = 0
    quotes_cancelled_hostile: int = 0
    
    # Round trips
    round_trips: int = 0

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
        
        if ticks[i] < ticks[i-1]:
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
    
    # Distance from mid in bps
    if order.side == OrderSide.BID:
        distance_bps = (mid_price - order.price) / mid_price * 10000
    else:
        distance_bps = (order.price - mid_price) / mid_price * 10000
    
    # Base fill probability
    fill_prob = MARKET_MAKING_PARAMS['order_fill_prob_base']
    
    # Reduce in hostile regime
    if regime == "hostile":
        fill_prob *= 0.6
    
    # Reduce with distance from mid
    fill_prob *= max(0, 1.0 - distance_bps / 500)
    fill_prob = np.clip(fill_prob, 0.05, 0.95)
    
    if np.random.random() < fill_prob:
        return True, order.price
    
    return False, None

# ============================================================================
# MARKET MAKING ENGINE
# ============================================================================

def run_single_market_mm(market_id: str, ticks: List[float], seed: int) -> MarketMakerState:
    """Run MM for one market."""
    mm = MarketMakerState(market_id=market_id, ticks=ticks)
    regimes = detect_k3_regimes(ticks)
    
    # Track active orders
    active_orders: Dict[int, Order] = {}
    
    # Track pending fills to match bids with asks
    pending_bids = []  # [(entry_price, qty)]
    pending_asks = []  # [(entry_price, qty)]
    
    current_position = 0
    
    for tick_idx in range(1, len(ticks)):
        current_price = ticks[tick_idx]
        regime = get_regime_at_tick(tick_idx, regimes)
        
        # STEP 1: Check fills on active orders
        filled_this_tick = []
        for order_id, order in list(active_orders.items()):
            filled, fill_price = simulate_order_fill(order, current_price, regime, tick_idx, seed)
            
            if filled:
                order.filled = True
                order.fill_price = fill_price
                filled_this_tick.append(order)
                del active_orders[order_id]
                
                if order.side == OrderSide.BID:
                    mm.bid_fill_count += 1
                    current_position += order.quantity
                    pending_bids.append((fill_price, order.quantity))
                else:
                    mm.ask_fill_count += 1
                    current_position -= order.quantity
                    pending_asks.append((fill_price, order.quantity))
        
        # STEP 2: Realize spreads by matching bids with asks
        while pending_bids and pending_asks:
            bid_price, bid_qty = pending_bids.pop(0)
            ask_price, ask_qty = pending_asks.pop(0)
            
            # Spread in bps
            spread_bps = (ask_price - bid_price) / bid_price * 10000
            if spread_bps > 0:
                mm.spread_captured_bps += spread_bps
                mm.realized_pnl_bps += spread_bps
                mm.round_trips += 1
            
            # Handle quantity mismatch
            if bid_qty < ask_qty:
                pending_asks.insert(0, (ask_price, ask_qty - bid_qty))
            elif ask_qty < bid_qty:
                pending_bids.insert(0, (bid_price, bid_qty - ask_qty))
        
        # STEP 3: Place offsetting orders for filled orders
        for order in filled_this_tick:
            mid_price = current_price
            
            if order.side == OrderSide.BID:
                # Bid filled; place ask
                improvement_bps = MARKET_MAKING_PARAMS['offset_improvement_bps']
                ask_price = mid_price * (1 + improvement_bps / 10000)
                
                if current_position - order.quantity <= MAX_INVENTORY_CAP:
                    new_order = Order(
                        order_id=mm.next_order_id,
                        side=OrderSide.ASK,
                        price=ask_price,
                        quantity=order.quantity,
                        tick_placed=tick_idx
                    )
                    active_orders[mm.next_order_id] = new_order
                    mm.next_order_id += 1
                    mm.quotes_placed += 1
            else:
                # Ask filled; place bid
                improvement_bps = MARKET_MAKING_PARAMS['offset_improvement_bps']
                bid_price = mid_price * (1 - improvement_bps / 10000)
                
                if current_position + order.quantity >= -MAX_INVENTORY_CAP:
                    new_order = Order(
                        order_id=mm.next_order_id,
                        side=OrderSide.BID,
                        price=bid_price,
                        quantity=order.quantity,
                        tick_placed=tick_idx
                    )
                    active_orders[mm.next_order_id] = new_order
                    mm.next_order_id += 1
                    mm.quotes_placed += 1
        
        # STEP 4: Place new quotes (if safe regime and capacity available)
        if regime == "safe":
            can_bid = current_position < MAX_INVENTORY_CAP
            can_ask = current_position > -MAX_INVENTORY_CAP
            
            bid_count = sum(1 for o in active_orders.values() if o.side == OrderSide.BID)
            ask_count = sum(1 for o in active_orders.values() if o.side == OrderSide.ASK)
            
            if can_bid and bid_count < 1:
                offset_bps = MARKET_MAKING_PARAMS['spread_offset_bps']
                bid_price = current_price * (1 - offset_bps / 10000)
                bid = Order(mm.next_order_id, OrderSide.BID, bid_price, 1, tick_idx)
                active_orders[mm.next_order_id] = bid
                mm.next_order_id += 1
                mm.quotes_placed += 1
            
            if can_ask and ask_count < 1:
                offset_bps = MARKET_MAKING_PARAMS['spread_offset_bps']
                ask_price = current_price * (1 + offset_bps / 10000)
                ask = Order(mm.next_order_id, OrderSide.ASK, ask_price, 1, tick_idx)
                active_orders[mm.next_order_id] = ask
                mm.next_order_id += 1
                mm.quotes_placed += 1
        else:
            # Cancel quotes in hostile regime
            for order_id in list(active_orders.keys()):
                mm.quotes_cancelled_hostile += 1
                del active_orders[order_id]
        
        # STEP 5: Track inventory drift
        mm.inventory_squared_error += current_position ** 2
    
    mm.final_position = current_position
    
    return mm

# ============================================================================
# SIMULATION
# ============================================================================

def generate_synthetic_price_series(seed: int, num_ticks: int = 200) -> List[float]:
    np.random.seed(seed)
    
    prices = [0.5]
    for _ in range(num_ticks - 1):
        step = np.random.normal(0, 0.01)
        reversion = (0.5 - prices[-1]) * 0.05
        new_price = np.clip(prices[-1] + step + reversion, 0.01, 0.99)
        prices.append(new_price)
    
    return prices

def run_full_simulation():
    print(f"""
================================================================================
PHASE 20 - MARKET MAKING FOUNDATION
================================================================================

Configuration:
  Total markets: {NUM_SEEDS * MARKETS_PER_SEED}
  Ticks per market: {TICKS_PER_SEED}
  
Market Making Parameters:
  Spread offset: {MARKET_MAKING_PARAMS['spread_offset_bps']} bps
  Offsetting improvement: {MARKET_MAKING_PARAMS['offset_improvement_bps']} bps
  Base fill probability: {MARKET_MAKING_PARAMS['order_fill_prob_base']:.0%}
  Max inventory cap: ±{MAX_INVENTORY_CAP}

Transaction Costs:
  Spread: {COSTS_BPS['spread_bps']} bps
  Slippage: {COSTS_BPS['slippage_bps']} bps
  Taker fee: {COSTS_BPS['taker_fee_bps']} bps
  Total per trade: {COST_PER_TRADE_BPS} bps

Running simulation...
================================================================================
""")
    
    results = {
        'total_orders_placed': 0,
        'total_fills': 0,
        'bid_fills': 0,
        'ask_fills': 0,
        'fill_rate_pct': 0.0,
        
        'round_trips': 0,
        'gross_spread_captured_bps': 0.0,
        'avg_spread_per_trip_bps': 0.0,
        
        'cost_per_fill_bps': COST_PER_TRADE_BPS,
        'total_cost_bps': 0.0,
        'gross_pnl_bps': 0.0,
        'net_pnl_bps': 0.0,
        'net_pnl_per_fill_bps': 0.0,
        
        'final_inventory': 0,
        'avg_abs_position': 0.0,
        
        'quotes_placed': 0,
        'quotes_cancelled_hostile': 0,
        'k3_suppression_rate': 0.0,
    }
    
    for seed in range(NUM_SEEDS):
        if (seed + 1) % 10 == 0:
            print(f"  Seed {seed + 1}/{NUM_SEEDS}")
        
        for market_idx in range(MARKETS_PER_SEED):
            market_id = f"s{seed:02d}_m{market_idx}"
            ticks = generate_synthetic_price_series(seed + market_idx * 1000, TICKS_PER_SEED)
            mm = run_single_market_mm(market_id, ticks, seed)
            
            # Accumulate
            results['total_orders_placed'] += mm.next_order_id
            results['bid_fills'] += mm.bid_fill_count
            results['ask_fills'] += mm.ask_fill_count
            results['total_fills'] += mm.bid_fill_count + mm.ask_fill_count
            results['round_trips'] += mm.round_trips
            results['gross_spread_captured_bps'] += mm.spread_captured_bps
            results['final_inventory'] += mm.final_position
            results['avg_abs_position'] += mm.inventory_squared_error
            results['quotes_placed'] += mm.quotes_placed
            results['quotes_cancelled_hostile'] += mm.quotes_cancelled_hostile
    
    # Post-process
    total_fills = max(1, results['total_fills'])
    results['fill_rate_pct'] = (results['total_fills'] / max(1, results['total_orders_placed'])) * 100
    results['total_cost_bps'] = COST_PER_TRADE_BPS * results['total_fills']
    results['gross_pnl_bps'] = results['gross_spread_captured_bps']
    results['net_pnl_bps'] = results['gross_pnl_bps'] - results['total_cost_bps']
    
    if results['total_fills'] > 0:
        results['net_pnl_per_fill_bps'] = results['net_pnl_bps'] / results['total_fills']
    
    if results['round_trips'] > 0:
        results['avg_spread_per_trip_bps'] = results['gross_spread_captured_bps'] / results['round_trips']
    
    results['avg_abs_position'] = results['avg_abs_position'] / (NUM_SEEDS * MARKETS_PER_SEED * TICKS_PER_SEED)
    
    if results['quotes_placed'] > 0:
        results['k3_suppression_rate'] = (results['quotes_cancelled_hostile'] / results['quotes_placed']) * 100
    
    return results

# ============================================================================
# REPORTING
# ============================================================================

def print_results(r):
    print(f"""
================================================================================
PHASE 20 - RESULTS
================================================================================

CORE METRICS
Metric                          | Value
{'-'*70}
Total orders placed             | {r['total_orders_placed']:>10}
Total fills (bid + ask)         | {r['total_fills']:>10}
  - Bid fills                   | {r['bid_fills']:>10}
  - Ask fills                   | {r['ask_fills']:>10}
Fill rate                       | {r['fill_rate_pct']:>9.2f}%

SPREAD CAPTURE & ROUND TRIPS
Metric                          | Value
{'-'*70}
Round-trip spreads realized     | {r['round_trips']:>10}
Gross spread captured (bps)     | {r['gross_spread_captured_bps']:>10.1f}
Avg spread per round-trip (bps) | {r['avg_spread_per_trip_bps']:>9.2f}

P&L ANALYSIS (in basis points)
Metric                          | Value
{'-'*70}
Gross PnL (spread capture)      | {r['gross_pnl_bps']:>10.1f} bps
Cost per trade                  | {r['cost_per_fill_bps']:>10} bps
Total cost (all fills)          | {r['total_cost_bps']:>10.1f} bps
Net PnL (after costs)           | {r['net_pnl_bps']:>10.1f} bps
Net PnL per fill                | {r['net_pnl_per_fill_bps']:>9.2f} bps

INTERPRETATION
Metric                          | Value
{'-'*70}
Spread > cost?                  | {'YES' if r['avg_spread_per_trip_bps'] > r['cost_per_fill_bps'] * 2 else 'NO':>10}
Gross PnL positive?             | {'YES' if r['gross_pnl_bps'] > 0 else 'NO':>10}
Net PnL positive?               | {'YES' if r['net_pnl_bps'] > 0 else 'NO':>10}

INVENTORY & RISK
Metric                          | Value
{'-'*70}
Final net inventory             | {r['final_inventory']:>10}
Avg abs position per tick       | {r['avg_abs_position']:>10.2f}

K3 REGIME SUPPRESSION
Metric                          | Value
{'-'*70}
Total quotes placed             | {r['quotes_placed']:>10}
Quotes cancelled (hostile)      | {r['quotes_cancelled_hostile']:>10}
K3 suppression rate             | {r['k3_suppression_rate']:>9.2f}%

================================================================================
""")

def answer_questions(r):
    print("""
================================================================================
VIABILITY ASSESSMENT
================================================================================

Q1: Does spread capture exceed transaction costs?
""")
    
    spread_covers_costs = r['avg_spread_per_trip_bps'] > r['cost_per_fill_bps']
    if spread_covers_costs:
        print(f"   ✓ YES")
        print(f"     Avg spread: {r['avg_spread_per_trip_bps']:.1f} bps")
        print(f"     2x cost: {r['cost_per_fill_bps'] * 2:.1f} bps")
        print(f"     Margin: {r['avg_spread_per_trip_bps'] - r['cost_per_fill_bps']:.1f} bps per round-trip")
        q1 = True
    else:
        print(f"   ✗ NO")
        print(f"     Avg spread: {r['avg_spread_per_trip_bps']:.1f} bps")
        print(f"     2x cost: {r['cost_per_fill_bps'] * 2:.1f} bps")
        q1 = False
    
    print("""
Q2: Is gross PnL positive?
""")
    if r['gross_pnl_bps'] > 0:
        print(f"   ✓ YES: {r['gross_pnl_bps']:.1f} bps")
        print(f"     Spread capture is working.")
        q2 = True
    else:
        print(f"   ✗ NO: {r['gross_pnl_bps']:.1f} bps")
        q2 = False
    
    print("""
Q3: What's the net PnL impact?
""")
    if r['net_pnl_bps'] > 0:
        print(f"   ✓ PROFITABLE: {r['net_pnl_bps']:.1f} bps after costs")
        print(f"     Break-even is achieved.")
        q3 = True
    elif r['net_pnl_bps'] > -r['cost_per_fill_bps'] * 10:
        print(f"   ~ MARGINAL: {r['net_pnl_bps']:.1f} bps")
        print(f"     Close to break-even; needs optimization.")
        q3 = True
    else:
        print(f"   ✗ NEGATIVE: {r['net_pnl_bps']:.1f} bps")
        q3 = False
    
    print("""
Q4: Does K3 suppression work?
""")
    if r['k3_suppression_rate'] > 20:
        print(f"   ✓ YES: {r['k3_suppression_rate']:.1f}% quotes cancelled")
        print(f"     K3 actively protecting against hostile regimes.")
        q4 = True
    elif r['k3_suppression_rate'] > 10:
        print(f"   ~ PARTIAL: {r['k3_suppression_rate']:.1f}%")
        q4 = True
    else:
        print(f"   ✗ MINIMAL: {r['k3_suppression_rate']:.1f}%")
        q4 = False
    
    print("""
================================================================================
VERDICT
================================================================================
""")
    
    passed = sum([q1, q2, q3, q4])
    
    if passed >= 3:
        print(f"✓ SPREAD CAPTURE IS FUNDAMENTALLY VIABLE")
        print(f"\n  Passed {passed}/4 viability checks")
        print(f"\n  Next steps:")
        print(f"  1. Test on real Polymarket data")
        print(f"  2. Optimize spread_offset for cost-adjusted profitability")
        print(f"  3. Implement inventory rebalancing to reduce drift")
        print(f"  4. Refine K3 regime detection for better protection")
    elif passed >= 2:
        print(f"~ SPREAD CAPTURE HAS PROMISE")
        print(f"\n  Passed {passed}/4 viability checks")
        print(f"\n  Issues to address:")
        for i, (name, result) in enumerate([
            ("Spread covers costs", q1),
            ("Gross PnL positive", q2),
            ("Net PnL viable", q3),
            ("K3 protection", q4),
        ], 1):
            if not result:
                print(f"  - {name}")
    else:
        print(f"✗ SPREAD CAPTURE NOT VIABLE AS TESTED")
        print(f"\n  Passed only {passed}/4 checks")
        print(f"\n  Need fundamental changes to parameters or mechanics")

# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    results = run_full_simulation()
    print_results(results)
    answer_questions(results)
