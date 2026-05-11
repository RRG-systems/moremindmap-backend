#!/usr/bin/env python3
"""Debug why get_trader_metrics returns empty"""

with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# Add detailed logging to the metrics query
old_query = """                if unified_ledger:
                    metrics = unified_ledger.get_trader_metrics(baby_id)
                    if metrics:"""

new_query = """                if unified_ledger:
                    print(f"[DEBUG QUERY] Looking up metrics for baby_id: {baby_id}")
                    print(f"[DEBUG QUERY] Total trades in ledger: {len(unified_ledger.trades)}")
                    print(f"[DEBUG QUERY] Traders with records: {list(unified_ledger.trader_trades.keys())[:5]}")
                    
                    metrics = unified_ledger.get_trader_metrics(baby_id)
                    print(f"[DEBUG QUERY] Query result: {metrics}")
                    
                    if metrics:"""

content = content.replace(old_query, new_query)

with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("✓ Added detailed metrics query logging")
