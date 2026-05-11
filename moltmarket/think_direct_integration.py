"""
THINK Direct Integration — Operator in the dashboard.

Queries are queued in /tmp/think_queries.json for the operator to respond to.
Frontend polls for responses.
"""

from flask import jsonify, request
from datetime import datetime
import json
import time
from pathlib import Path


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
            json.dump(data, f, indent=2)
    
    def add_query(self, query_text):
        """Add query to queue, return query_id."""
        query_id = f"q_{int(time.time()*1000)}"
        queue = self._read_queue()
        queue['queries'].append({
            'id': query_id,
            'text': query_text,
            'timestamp': datetime.now().isoformat(),
            'answered': False,
            'response': None
        })
        self._write_queue(queue)
        print(f"[THINK QUEUE] Query added: {query_id} - {query_text[:50]}")
        return query_id
    
    def get_response(self, query_id):
        """Get response for a query if it exists."""
        queue = self._read_queue()
        for q in queue['queries']:
            if q['id'] == query_id and q.get('answered'):
                return q.get('response')
        return None
    
    def get_unanswered(self):
        """Get all unanswered queries."""
        queue = self._read_queue()
        return [q for q in queue['queries'] if not q.get('answered')]
    
    def add_response(self, query_id, response_text):
        """Add response to a query."""
        queue = self._read_queue()
        for q in queue['queries']:
            if q['id'] == query_id:
                q['answered'] = True
                q['response'] = response_text
                q['response_time'] = datetime.now().isoformat()
        self._write_queue(queue)
        print(f"[THINK QUEUE] Response added: {query_id}")


# Global queue instance
query_queue = ThinkQueryQueue()


def setup_think_direct_endpoint(app, operator_name="Operator"):
    """Wire /api/think/query to operator with query queue."""
    
    @app.route('/api/think/query', methods=['POST'])
    def think_query():
        """Operator query endpoint with queueing."""
        try:
            data = request.get_json()
            query = data.get('query', '').strip()
            query_id = data.get('query_id')  # For polling responses
            
            if not query and not query_id:
                return jsonify({
                    'status': 'error',
                    'message': 'Need query or query_id'
                }), 400
            
            # If this is a poll for a response
            if query_id:
                response = query_queue.get_response(query_id)
                if response:
                    return jsonify({
                        'status': 'success',
                        'answer': response,
                        'timestamp': datetime.now().isoformat(),
                    }), 200
                else:
                    return jsonify({
                        'status': 'waiting',
                        'message': 'Operator is thinking...',
                    }), 202
            
            # New query - add to queue
            q_id = query_queue.add_query(query)
            
            return jsonify({
                'status': 'waiting',
                'message': 'Operator is thinking...',
                'query_id': q_id,
                'timestamp': datetime.now().isoformat(),
            }), 202
        
        except Exception as e:
            print(f"[THINK ERROR] {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    @app.route('/api/think/respond', methods=['POST'])
    def think_respond():
        """Operator sends response."""
        try:
            data = request.get_json()
            query_id = data.get('query_id')
            response = data.get('response', '').strip()
            
            if not query_id or not response:
                return jsonify({
                    'status': 'error',
                    'message': 'Need query_id and response'
                }), 400
            
            query_queue.add_response(query_id, response)
            
            return jsonify({
                'status': 'success',
                'message': 'Response stored'
            }), 200
        
        except Exception as e:
            print(f"[THINK RESPOND ERROR] {e}")
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    print("[THINK DIRECT] ✓ Operator connection active with query queue")
