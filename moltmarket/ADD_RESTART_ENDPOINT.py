#!/usr/bin/env python3
"""
Adds /api/restart-simulation endpoint to moltmarket_dashboard.py

This script finds the right place to insert the endpoint and adds it.
Run: python3 ADD_RESTART_ENDPOINT.py
"""

import sys

file_path = "/Users/rrg/.openclaw/workspace/moltmarket/moltmarket_dashboard.py"

# Read the file
with open(file_path, 'r') as f:
    content = f.read()

# Endpoint code to insert
endpoint_code = '''

@app.route('/api/restart-simulation', methods=['POST'])
def restart_simulation():
    """Restart simulation from CSV state (persistent, non-destructive)
    
    Unlike /api/reset which starts fresh, this reloads simulator from CSV.
    Useful for recovering from crashes or re-syncing state.
    """
    try:
        print("\\n[RESTART] Restarting simulation from CSV...")
        
        # Get current state before restart
        paper_pnl_before = simulator.paper_pnl
        shadow_pnl_before = simulator.shadow_pnl
        
        # Restart from CSV
        recover_simulator_state(simulator, data_layer)
        
        # Get state after restart
        paper_pnl_after = simulator.paper_pnl
        shadow_pnl_after = simulator.shadow_pnl
        
        print(f"[RESTART] ✓ Complete")
        print(f"[RESTART] Paper: ${paper_pnl_before:.2f} → ${paper_pnl_after:.2f}")
        print(f"[RESTART] Shadow: ${shadow_pnl_before:.2f} → ${shadow_pnl_after:.2f}")
        
        return jsonify({
            'status': 'restart_complete',
            'paper_pnl': round(paper_pnl_after, 2),
            'shadow_pnl': round(shadow_pnl_after, 2),
            'paper_trades': simulator.paper_trades,
            'shadow_trades': simulator.shadow_trades,
            'message': 'Simulation restarted from CSV'
        }), 200
    
    except Exception as e:
        print(f"[RESTART] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500
'''

# Find insertion point: right after the /api/reset endpoint
search_str = "@app.route('/api/reset', methods=['POST'])"
if search_str in content:
    # Find the end of the reset function
    idx = content.find(search_str)
    # Find the next @app.route after this one
    next_route_idx = content.find("@app.route('", idx + 100)
    
    if next_route_idx > 0:
        print(f"✓ Found insertion point at character {next_route_idx}")
        # Insert before the next route
        new_content = content[:next_route_idx] + endpoint_code + "\n\n" + content[next_route_idx:]
        
        # Write back
        with open(file_path, 'w') as f:
            f.write(new_content)
        
        print("✓ Endpoint added successfully")
        sys.exit(0)

print("✗ Could not find insertion point. Check file manually.")
sys.exit(1)
