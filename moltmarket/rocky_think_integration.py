"""
Integration layer: Wire ROCKY (v3) into the /api/think/query endpoint.

Raw Rocky. No templates. Real conversation about what's happening in MOLTmarket.
"""

from pathlib import Path
from flask import jsonify, request
from rocky_think_engine_v6 import RockyThinkEngine, RockyDataLayer


def setup_rocky_think_endpoint(app, dashboard_state, data_layer, simulator, nursery_bridge, evolution_engine):
    """
    Wire Rocky into the Flask app's /api/think/query endpoint.
    
    Rocky answers questions by looking at real system state (BRAIN, Nursery, Arena, MOLT).
    Returns conversational diagnosis, not structured response.
    """
    
    @app.route('/api/think/query', methods=['POST'])
    def think_query():
        """ROCKY inside THINK — live conversation about MOLTmarket"""
        try:
            data = request.get_json()
            query = data.get('query', '').strip()
            
            if not query:
                return jsonify({
                    'status': 'error',
                    'message': 'Empty query'
                }), 400
            
            # Initialize Rocky's data access layer
            data_access = RockyDataLayer(
                dashboard_state=dashboard_state,
                data_layer=data_layer,
                simulator=simulator,
                nursery_bridge=nursery_bridge,
                evolution_engine=evolution_engine,
            )
            
            # Get user name from system state
            user_name = dashboard_state.get('user_name', 'Operator')
            
            # Initialize Rocky with user context
            rocky_engine = RockyThinkEngine(Path.cwd(), data_access, user_name=user_name)
            answer = rocky_engine.query(query)
            
            print(f"[ROCKY] {user_name} asked: '{query}' | Answer length: {len(answer)}")
            
            return jsonify({
                'status': 'success',
                'answer': answer,
                'timestamp': data_access.get_brain_state()['state'],
            }), 200
        
        except Exception as e:
            print(f"[ROCKY] ERROR: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'status': 'error',
                'message': str(e)
            }), 500
    
    print("[ROCKY INTEGRATION] ✓ /api/think/query endpoint wired to Rocky v3")
