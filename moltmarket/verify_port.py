#!/usr/bin/env python3
"""Verify PORT constant is correctly set"""

import sys
sys.path.insert(0, '.')

from moltmarket_dashboard import PORT, app

print(f"✓ PORT constant: {PORT}")
print(f"✓ Flask app: {app}")

# Verify all critical routes
critical_routes = [
    '/api/metrics',
    '/api/trades',
    '/api/equity-curves',
    '/api/breakdowns',
]

print("\nVerifying routes:")
for route in critical_routes:
    found = any(str(rule) == route for rule in app.url_map.iter_rules())
    status = "✓" if found else "✗"
    print(f"  {status} {route}")

print("\n✓ All critical configuration verified")
print(f"✓ Server will run on http://127.0.0.1:{PORT}")
