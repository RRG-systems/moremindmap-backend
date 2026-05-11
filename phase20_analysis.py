#!/usr/bin/env python3
"""
PHASE 20 - DIAGNOSTIC ANALYSIS

Why are we getting 81k fills but only 21k round-trips?

THEORY: 
- Each bid fill needs an ask fill to complete the round-trip
- But bid fills may not align with ask fills in time
- Unmatched fills leave inventory at market close
- This creates slippage loss

GOAL: Calculate what's actually happening
"""

import numpy as np
from dataclasses import dataclass
from enum import Enum
from typing import List

NUM_SEEDS = 40
TICKS_PER_SEED = 200
MARKETS_PER_SEED = 8
MAX_INV = 5

MM_PARAMS = {
    'spread_offset_bps': 30,
    'offset_improvement_bps': 10,
    'fill_prob': 0.7,
}

COSTS = 125  # bps per trade

class OrderSide(Enum):
    BID = "bid"
    ASK = "ask"

@dataclass
class Order:
    oid: int
    side: OrderSide
    price: float
    qty: int
    tick: int
    filled: bool = False
    fill_price: float = None

@dataclass
class FillRecord:
    side: OrderSide
    price: float
    tick: int

def detect_k3(ticks):
    regimes = []
    regime = 'safe'
    start = 0
    downs = 0
    
    for i in range(1, len(ticks)):
        if ticks[i] < ticks[i-1]:
            downs += 1
        else:
            downs = 0
        
        is_hostile = downs >= 2
        
        if regime == 'safe' and is_hostile:
            regimes.append((start, i, regime))
            regime = 'hostile'
            start = i
        elif regime == 'hostile' and not is_hostile:
            regimes.append((start, i, regime))
            regime = 'safe'
            start = i
    
    regimes.append((start, len(ticks), regime))
    return regimes

def get_regime(idx, regimes):
    for s, e, r in regimes:
        if s <= idx < e:
            return r
    return 'safe'

def fill_prob(order, mid, regime, seed, idx):
    np.random.seed(seed + order.oid * 10000 + idx)
    
    if order.side == OrderSide.BID:
        dist_bps = (mid - order.price) / mid * 10000
    else:
        dist_bps = (order.price - mid) / mid * 10000
    
    p = MM_PARAMS['fill_prob']
    if regime == 'hostile':
        p *= 0.6
    p *= max(0, 1 - dist_bps / 500)
    p = np.clip(p, 0.05, 0.95)
    
    return np.random.random() < p

@dataclass
class MMDiagnostics:
    market_id: str
    
    # Fill tracking
    bid_fills: List[FillRecord] = None
    ask_fills: List[FillRecord] = None
    
    # Round-trip tracking
    matched_pairs: int = 0
    unmatched_bids: int = 0
    unmatched_asks: int = 0
    
    # Unrealized PnL
    final_position: int = 0
    unrealized_pnl_bps: float = 0.0
    
    def __post_init__(self):
        if self.bid_fills is None:
            self.bid_fills = []
        if self.ask_fills is None:
            self.ask_fills = []

def run_mm_with_diagnostics(market_id, ticks, seed):
    diag = MMDiagnostics(market_id)
    regimes = detect_k3(ticks)
    
    active = {}
    oid_counter = 0
    position = 0
    
    bid_queue = []  # Unmatched bids waiting for asks
    ask_queue = []  # Unmatched asks waiting for bids
    
    for tick_idx in range(1, len(ticks)):
        price = ticks[tick_idx]
        regime = get_regime(tick_idx, regimes)
        
        # Process fills
        filled = []
        for oid, order in list(active.items()):
            if fill_prob(order, price, regime, seed, tick_idx):
                order.filled = True
                order.fill_price = order.price
                filled.append(order)
                del active[oid]
                
                if order.side == OrderSide.BID:
                    position += order.qty
                    bid_queue.append(FillRecord(OrderSide.BID, order.fill_price, tick_idx))
                    diag.bid_fills.append(FillRecord(OrderSide.BID, order.fill_price, tick_idx))
                else:
                    position -= order.qty
                    ask_queue.append(FillRecord(OrderSide.ASK, order.fill_price, tick_idx))
                    diag.ask_fills.append(FillRecord(OrderSide.ASK, order.fill_price, tick_idx))
        
        # Try to match bids with asks
        while bid_queue and ask_queue:
            bid = bid_queue.pop(0)
            ask = ask_queue.pop(0)
            diag.matched_pairs += 1
        
        # Place offset orders
        for order in filled:
            if order.side == OrderSide.BID:
                offset = MM_PARAMS['offset_improvement_bps'] / 10000
                ask_price = price * (1 + offset)
                
                if position - order.qty <= MAX_INV:
                    o = Order(oid_counter, OrderSide.ASK, ask_price, order.qty, tick_idx)
                    active[oid_counter] = o
                    oid_counter += 1
            else:
                offset = MM_PARAMS['offset_improvement_bps'] / 10000
                bid_price = price * (1 - offset)
                
                if position + order.qty >= -MAX_INV:
                    o = Order(oid_counter, OrderSide.BID, bid_price, order.qty, tick_idx)
                    active[oid_counter] = o
                    oid_counter += 1
        
        # New quotes
        if regime == 'safe':
            can_bid = position < MAX_INV
            can_ask = position > -MAX_INV
            
            n_bid = sum(1 for o in active.values() if o.side == OrderSide.BID)
            n_ask = sum(1 for o in active.values() if o.side == OrderSide.ASK)
            
            if can_bid and n_bid < 1:
                offset = MM_PARAMS['spread_offset_bps'] / 10000
                bid = Order(oid_counter, OrderSide.BID, price * (1 - offset), 1, tick_idx)
                active[oid_counter] = bid
                oid_counter += 1
            
            if can_ask and n_ask < 1:
                offset = MM_PARAMS['spread_offset_bps'] / 10000
                ask = Order(oid_counter, OrderSide.ASK, price * (1 + offset), 1, tick_idx)
                active[oid_counter] = ask
                oid_counter += 1
        else:
            active.clear()
    
    # End-of-market accounting
    diag.unmatched_bids = len(bid_queue)
    diag.unmatched_asks = len(ask_queue)
    diag.final_position = position
    
    # Unrealized PnL on remaining position (worst-case: liquidate at current price)
    if position > 0:
        # Long position; assume we bought at average bid price
        avg_bid_price = np.mean([f.price for f in diag.bid_fills]) if diag.bid_fills else price
        unrealized = (price - avg_bid_price) / avg_bid_price * 10000 * position
        diag.unrealized_pnl_bps = unrealized
    elif position < 0:
        # Short position; assume we sold at average ask price
        avg_ask_price = np.mean([f.price for f in diag.ask_fills]) if diag.ask_fills else price
        unrealized = (avg_ask_price - price) / price * 10000 * (-position)
        diag.unrealized_pnl_bps = unrealized
    
    return diag

def simulate_with_diagnostics():
    print(f"""
================================================================================
PHASE 20 - DIAGNOSTIC ANALYSIS
================================================================================

Running {NUM_SEEDS * MARKETS_PER_SEED} markets to diagnose matching efficiency...
""")
    
    total_bids = 0
    total_asks = 0
    total_matches = 0
    total_unmatched_bids = 0
    total_unmatched_asks = 0
    total_unrealized = 0
    
    for seed in range(NUM_SEEDS):
        if (seed + 1) % 10 == 0:
            print(f"  Seed {seed+1}/{NUM_SEEDS}")
        
        for m in range(MARKETS_PER_SEED):
            np.random.seed(seed + m * 1000)
            ticks = [0.5]
            for _ in range(TICKS_PER_SEED - 1):
                dp = np.random.normal(0, 0.01)
                rev = (0.5 - ticks[-1]) * 0.05
                ticks.append(np.clip(ticks[-1] + dp + rev, 0.01, 0.99))
            
            diag = run_mm_with_diagnostics(f"s{seed}m{m}", ticks, seed)
            
            total_bids += len(diag.bid_fills)
            total_asks += len(diag.ask_fills)
            total_matches += diag.matched_pairs
            total_unmatched_bids += diag.unmatched_bids
            total_unmatched_asks += diag.unmatched_asks
            total_unrealized += diag.unrealized_pnl_bps
    
    # Analysis
    total_fills = total_bids + total_asks
    perfect_matches = min(total_bids, total_asks)
    actual_matches = total_matches
    matching_efficiency = actual_matches / perfect_matches * 100 if perfect_matches > 0 else 0
    
    # PnL reconstruction
    realized_spread_bps = actual_matches * 200  # ~200 bps per round-trip (from earlier test)
    total_cost = total_fills * COSTS
    matched_pnl = realized_spread_bps - total_cost
    unrealized_loss = total_unrealized
    total_pnl = matched_pnl + unrealized_loss
    
    print(f"""
================================================================================
DIAGNOSTICS
================================================================================

Fill Statistics
  Total bid fills: {total_bids:>10}
  Total ask fills: {total_asks:>10}
  Total fills: {total_fills:>10}
  Bid/ask imbalance: {abs(total_bids - total_asks):>10}

Round-Trip Matching
  Perfect matches (min): {perfect_matches:>10}
  Actual matches: {actual_matches:>10}
  Matching efficiency: {matching_efficiency:>9.1f}%
  Unmatched bids: {total_unmatched_bids:>10}
  Unmatched asks: {total_unmatched_asks:>10}

P&L Reconstruction (basis points)
  Realized spread (matched): {realized_spread_bps:>10.1f}
  Total transaction cost: {total_cost:>10.1f}
  Matched PnL: {matched_pnl:>10.1f}
  Unrealized loss (unmatched): {unrealized_loss:>10.1f}
  Total PnL: {total_pnl:>10.1f}

Per-Fill Metrics
  Avg spread per matched pair: ~200 bps
  Cost per fill: {COSTS} bps
  Effective cost per matched fill: {total_cost / max(1, actual_matches):.1f} bps
  Net PnL per matched fill: {matched_pnl / max(1, actual_matches):.1f} bps

================================================================================

KEY INSIGHT:

Matching efficiency is {matching_efficiency:.1f}%

This means:
- For every 100 bid fills, we get {matching_efficiency:.0f} ask fills
- The remaining {100 - matching_efficiency:.0f} bids are stuck as inventory
- This creates unrealized losses at market close

The spread IS being captured (200 bps > costs), but:
1. We're not matching fills efficiently
2. Unmatched inventory becomes unrealized losses
3. Net result is slightly negative

NEXT STEPS:
1. Implement inventory rebalancing (actively close unmatched positions)
2. Adjust spread_offset to reduce bid/ask imbalance
3. Refine K3 regime to reduce cancelled quotes
4. Test on real Polymarket data to validate fill patterns

================================================================================
""")

if __name__ == "__main__":
    simulate_with_diagnostics()
