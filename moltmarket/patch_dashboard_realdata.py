#!/usr/bin/env python3
"""Patch dashboard to add real-data initialization"""

file_path = "/Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py"

with open(file_path, 'r') as f:
    lines = f.readlines()

# Find line with "# PHASE 4.6: Inject BRAIN callback into simulator"
insert_after = None
for i, line in enumerate(lines):
    if "# PHASE 4.6: Inject BRAIN callback into simulator" in line:
        # Find the next blank line after simulator creation
        for j in range(i, min(i+10, len(lines))):
            if lines[j].strip() == "" and "# PHASE 31" in lines[j+1]:
                insert_after = j
                break
        break

if insert_after is None:
    print("ERROR: Could not find insertion point")
    exit(1)

# Create patch text
patch = """
# PHASE 10.3: Wire real Coinbase data (optional)
real_data_mode = False
try:
    from coinbase_market_feed import CoinbaseMarketFeed
    from execution_simulator_realdata import setup_real_data_simulation
    print("[DASHBOARD] Initializing real Coinbase feed...")
    feed = CoinbaseMarketFeed()
    if feed.connect(run_in_thread=True):
        time.sleep(2)
        if feed.is_connected():
            real_data_sim = setup_real_data_simulation(simulator, feed)
            real_data_mode = True
            print(f"[DASHBOARD] SUCCESS: Real data mode active ({real_data_sim.get_mode()})")
        else:
            print("[DASHBOARD] Feed connected but no data, using simulated prices")
    else:
        print("[DASHBOARD] Coinbase feed unavailable, using simulated prices")
except Exception as e:
    print(f"[DASHBOARD] Real data init failed: {e}, using simulated prices")

"""

# Insert patch
lines.insert(insert_after, patch)

# Write back
with open(file_path, 'w') as f:
    f.writelines(lines)

print(f"✓ Dashboard patched at line {insert_after}")
