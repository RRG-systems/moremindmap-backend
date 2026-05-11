"""
Manual bridge for testing operator responses.

When Rocky (the operator) responds in OpenClaw, use this to send responses back to THINK.

Usage:
    python3 think_manual_bridge.py "Your response text here"
"""

import requests
import sys
import json

def send_response_to_think(response_text):
    """Send operator response back to THINK dashboard."""
    try:
        url = 'http://localhost:5050/api/think/respond'
        data = {'response': response_text}
        
        result = requests.post(url, json=data)
        
        if result.status_code == 200:
            print(f"✓ Response sent to THINK: {response_text[:50]}...")
            return True
        else:
            print(f"✗ Error: {result.status_code} - {result.text}")
            return False
    except Exception as e:
        print(f"✗ Connection error: {e}")
        return False

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 think_manual_bridge.py 'Your response here'")
        sys.exit(1)
    
    response = ' '.join(sys.argv[1:])
    send_response_to_think(response)
