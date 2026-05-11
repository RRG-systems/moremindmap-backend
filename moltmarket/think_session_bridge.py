"""
THINK Session Bridge — Bidirectional pipe between OpenClaw and THINK dashboard.

When dashboard starts: "ROCKY is in THINK"
When dashboard stops: "ROCKY has left the building!"
Everything typed here → appears in THINK
Everything in THINK → appears here (one unified chat)
"""

import json
from datetime import datetime
from pathlib import Path
import atexit
from think_entrance_messages import get_random_entrance, get_random_exit


class ThinkSessionBridge:
    """Manages the OpenClaw ↔ THINK conversation pipe."""
    
    def __init__(self, think_message_file='/tmp/think_messages.jsonl'):
        self.think_message_file = think_message_file
        self.session_active = False
        self._ensure_file_exists()
    
    def _ensure_file_exists(self):
        Path(self.think_message_file).touch()
    
    def start_session(self):
        """Dashboard has started. Announce Rocky with random entrance."""
        self.session_active = True
        entrance = get_random_entrance()
        self.add_message('system', entrance)
        print(f"[THINK BRIDGE] ✓ Session started - {entrance}")
    
    def stop_session(self):
        """Dashboard has stopped. Say goodbye with random exit."""
        exit_msg = get_random_exit()
        self.add_message('system', exit_msg)
        self.session_active = False
        print(f"[THINK BRIDGE] ✗ Session stopped - {exit_msg}")
    
    def add_message(self, role, text, timestamp=None):
        """Add a message to the THINK stream."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
        
        message = {
            'role': role,
            'text': text,
            'timestamp': timestamp
        }
        
        # Append to JSONL file
        with open(self.think_message_file, 'a') as f:
            f.write(json.dumps(message) + '\n')
        
        print(f"[THINK BRIDGE] [{role}] {text[:60]}")
    
    def get_all_messages(self):
        """Get all messages for THINK display."""
        messages = []
        try:
            with open(self.think_message_file, 'r') as f:
                for line in f:
                    if line.strip():
                        messages.append(json.loads(line))
        except FileNotFoundError:
            pass
        return messages
    
    def get_messages_since(self, timestamp):
        """Get messages after a specific timestamp."""
        messages = []
        try:
            with open(self.think_message_file, 'r') as f:
                for line in f:
                    if line.strip():
                        msg = json.loads(line)
                        if msg['timestamp'] > timestamp:
                            messages.append(msg)
        except FileNotFoundError:
            pass
        return messages


# Global bridge instance
think_bridge = ThinkSessionBridge()


def setup_think_session_endpoints(app):
    """Wire THINK session endpoints into Flask."""
    from flask import jsonify, request
    
    @app.route('/api/think/session/start', methods=['POST'])
    def think_session_start():
        """Signal that trading session has started."""
        think_bridge.start_session()
        return jsonify({'status': 'ok', 'message': 'ROCKY is in THINK'}), 200
    
    @app.route('/api/think/session/stop', methods=['POST'])
    def think_session_stop():
        """Signal that trading session has stopped."""
        think_bridge.stop_session()
        return jsonify({'status': 'ok', 'message': 'ROCKY has left the building'}), 200
    
    @app.route('/api/think/messages', methods=['GET'])
    def think_get_messages():
        """Get all messages for THINK display."""
        messages = think_bridge.get_all_messages()
        return jsonify({'messages': messages}), 200
    
    @app.route('/api/think/messages/since', methods=['POST'])
    def think_get_messages_since():
        """Get messages since a timestamp (for polling)."""
        data = request.get_json()
        timestamp = data.get('timestamp', '2000-01-01T00:00:00')
        messages = think_bridge.get_messages_since(timestamp)
        return jsonify({'messages': messages}), 200
    
    @app.route('/api/think/message', methods=['POST'])
    def think_add_message():
        """Add a message from OpenClaw to THINK."""
        data = request.get_json()
        role = data.get('role', 'assistant')
        text = data.get('text', '')
        
        if not text:
            return jsonify({'status': 'error', 'message': 'Empty message'}), 400
        
        think_bridge.add_message(role, text)
        return jsonify({'status': 'ok'}), 200
    
    print("[THINK SESSION BRIDGE] ✓ Endpoints wired")


def cleanup_on_exit():
    """Called when dashboard stops."""
    if think_bridge.session_active:
        think_bridge.stop_session()


# Register cleanup
atexit.register(cleanup_on_exit)
