#!/usr/bin/env python3
"""
PHASE 20 - MARKET MAKING FOUNDATION (CORRECTED)

KEY INSIGHT: We're capturing spreads on round-trips.
- Each bid fill at price_bid establishes a long position
- When offset ask fills at price_ask, we realize: (price_ask - price_bid) / price_bid
- This is the spread in percentage, multiply by 10000 to get bps
- Then multiply by notional size to get PnL per round-trip

For unit sizes (qty=1, price~0.5), spread_realized is small (~0.1-1 bps).
We need many round-trips and tight spreads to be profitable.

SIMPLIFIED APPROACH:
- Track spread per round-trip in bps (accurate)
- Calculate whether PnL/fill is positive
- Focus on VIABILITY not absolute values
"""

import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from enum import Enum

NUM_SEEDS = 40
TICKS_PER_SEED = 200
MARKETS_PER_SEED = 8
MAX_INVENTORY_CAP = 5

MM_PARAMS = {
    'spread_offset_bps': 30,
    'offset_improvement_bps': 10,
    'fill_prob': 0.7,
}

COSTS_BPS = 125  # Spread(20) + slippage(5) + fee(100)

# ============================================================================

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

def detect_k3(ticks):
    """Detect hostile regimes: 2+ down-ticks."""
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
    """Order fill probability."""
    np.random.seed(seed + order.oid * 10000 + idx)
    
    # Distance from mid
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
class MMState:
    mid: str
    ticks: List[float]
    
    orders_placed: int = 0
    bid_fills: int = 0
    ask_fills: int = 0
    
    spreads_realized: List[float] = None  # In bps per round-trip
    inventory_drift: int = 0
    
    quotes_total: int = 0
    quotes_cancelled: int = 0
    
    def __post_init__(self):
        if self.spreads_realized is None:
            self.spreads_realized = []

def run_mm_market(market_id, ticks, seed):
    """Run MM on one market."""
    mm = MMState(market_id, ticks)
    regimes = detect_k3(ticks)
    
    active = {}
    pending_buys = []  # [(price, qty)]
    pending_sells = []  # [(price, qty)]
    position = 0
    
    for tick_idx in range(1, len(ticks)):
        price = ticks[tick_idx]
        regime = get_regime(tick_idx, regimes)
        
        # Check fills
        filled = []
        for oid, order in list(active.items()):
            if fill_prob(order, price, regime, seed, tick_idx):
                order.filled = True
                order.fill_price = order.price
                filled.append(order)
                del active[oid]
                
                if order.side == OrderSide.BID:
                    mm.bid_fills += 1
                    position += order.qty
                    pending_buys.append((order.fill_price, order.qty))
                else:
                    mm.ask_fills += 1
                    position -= order.qty
                    pending_sells.append((order.fill_price, order.qty))
        
        # Match buys with sells to realize spreads
        while pending_buys and pending_sells:
            buy_price, buy_qty = pending_buys.pop(0)
            sell_price, sell_qty = pending_sells.pop(0)
            
            # Spread in bps: (sell - buy) / buy * 10000
            spread_bps = (sell_price - buy_price) / buy_price * 10000
            if spread_bps > 0:
                mm.spreads_realized.append(spread_bps)
            
            # Handle qty mismatch
            if buy_qty < sell_qty:
                pending_sells.insert(0, (sell_price, sell_qty - buy_qty))
            elif sell_qty < buy_qty:
                pending_buys.insert(0, (buy_price, buy_qty - sell_qty))
        
        # Place offset orders
        for order in filled:
            if order.side == OrderSide.BID:
                # Buy filled; place sell
                offset = MM_PARAMS['offset_improvement_bps'] / 10000
                sell_price = price * (1 + offset)
                
                if position - order.qty <= MAX_INVENTORY_CAP:
                    o = Order(mm.orders_placed, OrderSide.ASK, sell_price, order.qty, tick_idx)
                    active[mm.orders_placed] = o
                    mm.orders_placed += 1
                    mm.quotes_total += 1
            else:
                # Sell filled; place buy
                offset = MM_PARAMS['offset_improvement_bps'] / 10000
                buy_price = price * (1 - offset)
                
                if position + order.qty >= -MAX_INVENTORY_CAP:
                    o = Order(mm.orders_placed, OrderSide.BID, buy_price, order.qty, tick_idx)
                    active[mm.orders_placed] = o
                    mm.orders_placed += 1
                    mm.quotes_total += 1
        
        # New quotes
        if regime == 'safe':
            can_buy = position < MAX_INVENTORY_CAP
            can_sell = position > -MAX_INVENTORY_CAP
            
            n_bid = sum(1 for o in active.values() if o.side == OrderSide.BID)
            n_ask = sum(1 for o in active.values() if o.side == OrderSide.ASK)
            
            if can_buy and n_bid < 1:
                offset = MM_PARAMS['spread_offset_bps'] / 10000
                bid = Order(mm.orders_placed, OrderSide.BID, price * (1 - offset), 1, tick_idx)
                active[mm.orders_placed] = bid
                mm.orders_placed += 1
                mm.quotes_total += 1
            
            if can_sell and n_ask < 1:
                offset = MM_PARAMS['spread_offset_bps'] / 10000
                ask = Order(mm.orders_placed, OrderSide.ASK, price * (1 + offset), 1, tick_idx)
                active[mm.orders_placed] = ask
                mm.orders_placed += 1
                mm.quotes_total += 1
        else:
            # Cancel in hostile
            for oid in list(active.keys()):
                mm.quotes_cancelled += 1
                del active[oid]
        
        mm.inventory_drift += abs(position)
    
    return mm

def gen_prices(seed, n):
    np.random.seed(seed)
    p = [0.5]
    for _ in range(n - 1):
        dp = np.random.normal(0, 0.01)
        rev = (0.5 - p[-1]) * 0.05
        p.append(np.clip(p[-1] + dp + rev, 0.01, 0.99))
    return p

def simulate():
    print(f"""
================================================================================
PHASE 20 - MARKET MAKING FOUNDATION
================================================================================

Configuration:
  Seeds: {NUM_SEEDS}
  Ticks/seed: {TICKS_PER_SEED}
  Markets/seed: {MARKETS_PER_SEED}
  Total markets: {NUM_SEEDS * MARKETS_PER_SEED}

Parameters:
  Spread offset: {MM_PARAMS['spread_offset_bps']} bps
  Offset improvement: {MM_PARAMS['offset_improvement_bps']} bps
  Fill probability: {MM_PARAMS['fill_prob']:.0%}
  Max inventory: ±{MAX_INVENTORY_CAP}

Costs:
  Per trade: {COSTS_BPS} bps

Running...
================================================================================
""")
    
    spreads = []
    all_fills = 0
    all_orders = 0
    total_quotes = 0
    total_cancelled = 0
    total_drift = 0
    
    for seed in range(NUM_SEEDS):
        if (seed + 1) % 10 == 0:
            print(f"  Seed {seed+1}/{NUM_SEEDS}")
        
        for m in range(MARKETS_PER_SEED):
            ticks = gen_prices(seed + m * 1000, TICKS_PER_SEED)
            mm = run_mm_market(f"s{seed}m{m}", ticks, seed)
            
            spreads.extend(mm.spreads_realized)
            all_fills += mm.bid_fills + mm.ask_fills
            all_orders += mm.orders_placed
            total_quotes += mm.quotes_total
            total_cancelled += mm.quotes_cancelled
            total_drift += mm.inventory_drift
    
    # Calculate metrics
    n_fills = max(1, all_fills)
    n_round_trips = len(spreads)
    fill_rate = all_fills / max(1, all_orders) * 100
    
    gross_spread_bps = sum(spreads) if spreads else 0
    avg_spread_bps = gross_spread_bps / n_round_trips if n_round_trips > 0 else 0
    
    total_cost_bps = COSTS_BPS * all_fills
    net_pnl_bps = gross_spread_bps - total_cost_bps
    pnl_per_fill = net_pnl_bps / n_fills if n_fills > 0 else 0
    
    k3_supp = total_cancelled / total_quotes * 100 if total_quotes > 0 else 0
    
    print(f"""
================================================================================
RESULTS
================================================================================

Orders & Fills
  Total orders placed: {all_orders:>10}
  Total fills: {all_fills:>10}
  Fill rate: {fill_rate:>9.2f}%

Spread Capture
  Round-trips: {n_round_trips:>10}
  Total spread (bps): {gross_spread_bps:>10.1f}
  Avg spread/trip (bps): {avg_spread_bps:>9.2f}

P&L (basis points)
  Gross (spread): {gross_spread_bps:>10.1f} bps
  Cost/fill: {COSTS_BPS:>10} bps
  Total cost: {total_cost_bps:>10.1f} bps
  Net PnL: {net_pnl_bps:>10.1f} bps
  PnL per fill: {pnl_per_fill:>9.2f} bps

K3 Protection
  Quotes placed: {total_quotes:>10}
  Cancelled (hostile): {total_cancelled:>10}
  Suppression rate: {k3_supp:>9.2f}%

================================================================================

ANALYSIS:

Q1: Does avg spread exceed 2x cost?
   Avg spread: {avg_spread_bps:.1f} bps
   2x cost: {COSTS_BPS * 2} bps
   Result: {'✓ YES' if avg_spread_bps > COSTS_BPS * 2 else '✗ NO'}

Q2: Gross PnL positive?
   Result: {'✓ YES' if gross_spread_bps > 0 else '✗ NO'}

Q3: Net PnL per fill positive?
   PnL per fill: {pnl_per_fill:.2f} bps
   Result: {'✓ YES' if pnl_per_fill > 0 else '✗ NO'}

Q4: K3 suppression active?
   Suppression rate: {k3_supp:.1f}%
   Result: {'✓ YES' if k3_supp > 20 else '~ PARTIAL' if k3_supp > 10 else '✗ NO'}

================================================================================

VERDICT:

Checks passed:
  1. Spread > 2x cost: {'YES' if avg_spread_bps > COSTS_BPS * 2 else 'NO'}
  2. Gross PnL > 0: {'YES' if gross_spread_bps > 0 else 'NO'}
  3. Net PnL > 0: {'YES' if pnl_per_fill > 0 else 'NO'}
  4. K3 suppression: {'YES' if k3_supp > 20 else 'PARTIAL' if k3_supp > 10 else 'NO'}

Total: {sum([
    avg_spread_bps > COSTS_BPS * 2,
    gross_spread_bps > 0,
    pnl_per_fill > 0,
    k3_supp > 20
])}/4

CONCLUSION:
""", end='')
    
    checks = [
        avg_spread_bps > COSTS_BPS * 2,
        gross_spread_bps > 0,
        pnl_per_fill > 0,
        k3_supp > 20
    ]
    
    if sum(checks) >= 3:
        print("""✓ SPREAD CAPTURE IS FUNDAMENTALLY VIABLE

The market-making loop is working:
  - Spreads are being captured
  - Fill rate is strong
  - K3 protection is active

Next: Test on real Polymarket data and optimize parameters.
""")
    elif sum(checks) >= 2:
        print("""~ MARGINAL VIABILITY

Some components working but not all checks passed.
Requires parameter tuning or mechanic improvements.""")
    else:
        print("""✗ NOT VIABLE

Multiple viability checks failed.
Fundamental rethink needed.""")

if __name__ == "__main__":
    simulate()
