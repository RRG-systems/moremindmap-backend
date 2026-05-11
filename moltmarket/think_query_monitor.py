"""
THINK Query Monitor — Background job that watches for user questions.

When a new query arrives in THINK, this sends it to the operator (via webhook/cron).
Operator responds, response gets stored, frontend picks it up.
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime


class ThinkQueryMonitor:
    """Monitor for new THINK queries."""
    
    def __init__(self, dashboard_state_file=None):
        self.dashboard_state_file = dashboard_state_file
        self.last_query = None
        self.last_query_time = None
        self.running = False
    
    def start(self):
        """Start monitoring in background thread."""
        self.running = True
        thread = threading.Thread(target=self._monitor_loop, daemon=True)
        thread.start()
        print("[THINK MONITOR] ✓ Background monitoring started")
    
    def _monitor_loop(self):
        """Continuously check for new queries."""
        while self.running:
            try:
                # This would check a shared state or query queue
                # For now, it's a placeholder for the real implementation
                time.sleep(0.5)
            except Exception as e:
                print(f"[MONITOR ERROR] {e}")
                time.sleep(1)
    
    def stop(self):
        """Stop monitoring."""
        self.running = False
        print("[THINK MONITOR] Stopped")


# Simpler approach: Store queries in a file that cron can check
class ThinkQueryQueue:
    """File-based query queue."""
    
    def __init__(self, queue_file='/tmp/think_queries.json'):
        self.queue_file = queue_file
        self._ensure_queue_exists()
    
    def _ensure_queue_exists(self):
        if not Path(self.queue_file).exists():
            self._write_queue({'queries': [], 'last_checked': None})
    
    def _read_queue(self):
        try:
            with open(self.queue_file, 'r') as f:
                return json.load(f)
        except:
            return {'queries': [], 'last_checked': None}
    
    def _write_queue(self, data):
        with open(self.queue_file, 'w') as f:
            json.dump(data, f)
    
    def add_query(self, query_id, query_text, timestamp):
        """Add query to queue."""
        queue = self._read_queue()
        queue['queries'].append({
            'id': query_id,
            'text': query_text,
            'timestamp': timestamp,
            'answered': False
        })
        self._write_queue(queue)
        print(f"[THINK QUEUE] Query added: {query_text[:50]}")
    
    def get_unanswered(self):
        """Get all unanswered queries."""
        queue = self._read_queue()
        return [q for q in queue['queries'] if not q.get('answered')]
    
    def mark_answered(self, query_id):
        """Mark query as answered."""
        queue = self._read_queue()
        for q in queue['queries']:
            if q['id'] == query_id:
                q['answered'] = True
        self._write_queue(queue)


# Integration with Flask
query_queue = ThinkQueryQueue()


def integrate_query_queue_into_flask(app):
    """Wire query queue into Flask for automatic operator notification."""
    
    @app.route('/api/think/query', methods=['POST'])
    def think_query():
        """Enhanced endpoint that queues queries for operator."""
        from flask import request, jsonify
        
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'status': 'error', 'message': 'Empty query'}), 400
        
        # Generate query ID
        query_id = f"q_{int(time.time()*1000)}"
        
        # Add to queue for operator
        query_queue.add_query(query_id, query, datetime.now().isoformat())
        
        print(f"[THINK] New query queued: {query_id}")
        
        # Return waiting status
        return jsonify({
            'status': 'waiting',
            'message': 'Operator is analyzing...',
            'query_id': query_id,
            'timestamp': datetime.now().isoformat(),
        }), 202
    
    print("[THINK QUEUE] Flask integration active")
