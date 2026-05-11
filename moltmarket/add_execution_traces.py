#!/usr/bin/env python3
"""Add execution traces to moltmarket_dashboard.py"""

with open('moltmarket_dashboard.py', 'r') as f:
    content = f.read()

# Trace 1: Add trace at start of execute_baby_variant
old1 = """def execute_baby_variant(baby, market_data=None):
    \"\"\"Execute baby through unified execution pipeline (same signal as Arena).\"\"\"
    baby_id = baby['variant_id']
    
    if not unified_executor:"""

new1 = """def execute_baby_variant(baby, market_data=None):
    \"\"\"Execute baby through unified execution pipeline (same signal as Arena).\"\"\"
    baby_id = baby['variant_id']
    print(f"[TRACE BABY] execute_baby_variant START for {baby_id}")
    
    if not unified_executor:"""

content = content.replace(old1, new1)

# Trace 2: Add trace before signal generation
old2 = """        # Generate signal with 15% probability (same as Arena)
        import random
        if True:  # TESTING: always generate. Change back to: if random.random() < 0.15:
            asset = random.choice(['BTC', 'ETH'])
            side = random.choice(['long', 'short'])"""

new2 = """        # Generate signal with 15% probability (same as Arena)
        import random
        print(f"[TRACE BABY] About to generate signal for {baby_id}")
        if True:  # TESTING: always generate. Change back to: if random.random() < 0.15:
            print(f"[TRACE BABY] Signal generation condition TRUE for {baby_id}")
            asset = random.choice(['BTC', 'ETH'])
            side = random.choice(['long', 'short'])
            print(f"[TRACE BABY] Generated signal: {asset} {side} for {baby_id}")"""

content = content.replace(old2, new2)

# Trace 3: Add trace before unified_executor call
old3 = """            # Execute through unified pipeline
            trade = unified_executor.execute_signal(
                source='baby',
                trader_id=baby_id,
                signal=signal
            )
            
            if trade:"""

new3 = """            # Execute through unified pipeline
            print(f"[TRACE BABY] Calling unified_executor.execute_signal for {baby_id}")
            trade = unified_executor.execute_signal(
                source='baby',
                trader_id=baby_id,
                signal=signal
            )
            print(f"[TRACE BABY] execute_signal returned: {trade is not None}")
            
            if trade:"""

content = content.replace(old3, new3)

# Trace 4: Add trace to main loop
old4 = """            # NURSERY: Execute all active babies
            active_babies = evolution_engine.babies if evolution_engine.babies else []
            if active_babies:
                print(f"[NURSERY LOOP] babies active: {len(active_babies)}")
                for baby in active_babies:
                    baby_id = baby['variant_id']
                    print(f"[BABY EVAL] baby_id={baby_id}")
                    execute_baby_variant(baby)"""

new4 = """            # NURSERY: Execute all active babies
            active_babies = evolution_engine.babies if evolution_engine.babies else []
            if active_babies:
                print(f"[TRACE MAIN] NURSERY LOOP: {len(active_babies)} babies active")
                for baby in active_babies:
                    baby_id = baby['variant_id']
                    print(f"[TRACE MAIN] Calling execute_baby_variant for {baby_id}")
                    execute_baby_variant(baby)"""

content = content.replace(old4, new4)

with open('moltmarket_dashboard.py', 'w') as f:
    f.write(content)

print("✓ Added execution traces")
