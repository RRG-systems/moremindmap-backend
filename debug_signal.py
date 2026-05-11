#!/usr/bin/env python3
import numpy as np
from datetime import datetime, timedelta

# Recreate synthetic data to debug signal
np.random.seed(42)

# Generate single market price path
prices = [0.50 + np.random.normal(0, 0.02)]
total_ticks = 12 * 60  # 60 days, 12 ticks/day

for i in range(total_ticks - 1):
    drift = (0.50 - prices[-1]) * 0.05
    shock = np.random.normal(0, 0.015)
    new_price = np.clip(prices[-1] + drift + shock, 0.01, 0.99)
    prices.append(new_price)

# Convert to OHLC ticks
ticks = []
start_time = datetime.utcnow() - timedelta(days=60)

for i, price in enumerate(prices):
    o = price + np.random.normal(0, 0.002)
    h = max(price, o) + abs(np.random.normal(0, 0.003))
    l = min(price, o) - abs(np.random.normal(0, 0.003))
    c = price + np.random.normal(0, 0.002)
    
    tick_time = start_time + timedelta(hours=i * (24 / 12))
    
    ticks.append({
        'timestamp': int(tick_time.timestamp()),
        'open': np.clip(o, 0.01, 0.99),
        'high': np.clip(h, 0.01, 0.99),
        'low': np.clip(l, 0.01, 0.99),
        'close': np.clip(c, 0.01, 0.99),
        'volume': np.random.uniform(500, 5000),
    })

print("Generated {} ticks".format(len(ticks)))
print("Price range: {:.3f} - {:.3f}".format(
    min(t['close'] for t in ticks),
    max(t['close'] for t in ticks)
))

# Now debug momentum reversal signal on first 150 ticks
test_ticks = ticks[:150]

trades = []
i = 5

signal_detections = []

while i < len(test_ticks):
    lookback_start = test_ticks[i-5]['close']
    current = test_ticks[i]['close']
    drop_pct = (lookback_start - current) / lookback_start * 100
    last_down = (test_ticks[i-1]['close'] - test_ticks[i]['close']) / test_ticks[i-1]['close'] * 100
    
    if drop_pct >= 0.5 and last_down < 0.0:
        signal_detections.append((i, drop_pct, last_down))
        
        # Entry
        entry_price = test_ticks[i+1]['open'] if i+1 < len(test_ticks) else test_ticks[i]['close']
        entry_idx = i + 1
        
        # Find exit
        exit_found = False
        for exit_idx in range(entry_idx + 1, len(test_ticks)):
            highest = max(test_ticks[j]['high'] for j in range(entry_idx, exit_idx+1))
            lowest = min(test_ticks[j]['low'] for j in range(entry_idx, exit_idx+1))
            
            profit_pct = (highest - entry_price) / entry_price * 100
            loss_pct = (entry_price - lowest) / entry_price * 100
            
            if profit_pct >= 2.0:
                exit_price = entry_price * 1.02
                status = 'TARGET'
                exit_found = True
                break
            elif loss_pct >= 2.0:
                exit_price = entry_price * 0.98
                status = 'STOP'
                exit_found = True
                break
        
        if exit_found:
            pnl = exit_price - entry_price
            trades.append({
                'entry_idx': entry_idx,
                'entry': entry_price,
                'exit': exit_price,
                'pnl': pnl,
                'pnl_pct': pnl/entry_price*100,
                'status': status,
            })
            print("Trade {}: Entry {:.4f} Exit {:.4f} ({}) PnL: {:.5f} ({:.2f}%)".format(
                len(trades), entry_price, exit_price, status, pnl, pnl/entry_price*100
            ))
            i = exit_idx + 1
    
    i += 1

print("\nSignal detections: {}".format(len(signal_detections)))
print("First 5 detections: {}".format(signal_detections[:5]))
print("Trades from detections: {}".format(len(trades)))

if trades:
    wins = sum(1 for t in trades if t['pnl'] > 0)
    print("\nBefore friction:")
    print("  Win rate: {:.1f}%".format(wins/len(trades)*100))
    print("  Avg PnL: ${:.5f}".format(np.mean([t['pnl'] for t in trades])))
    print("  Total PnL: ${:.5f}".format(sum(t['pnl'] for t in trades)))
    
    # Now apply friction
    friction_pct = 0.01277 + 0.001 + 0.005  # spread + slippage + fee
    friction_pnl = [t['pnl'] - friction_pct*t['entry'] for t in trades]
    friction_wins = sum(1 for p in friction_pnl if p > 0)
    print("\nAfter friction ({:.2f}%):".format(friction_pct*100))
    print("  Win rate: {:.1f}%".format(friction_wins/len(friction_pnl)*100))
    print("  Avg PnL: ${:.5f}".format(np.mean(friction_pnl)))
    print("  Total PnL: ${:.5f}".format(sum(friction_pnl)))
