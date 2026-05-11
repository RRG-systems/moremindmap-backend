"""
ROCKY v6 — Clean slate. No canned dialogue. Real data. Auto-tune on demand.

Just a working operator. You ask, I respond.
"""

import json
from datetime import datetime
from pathlib import Path


class RockyDataLayer:
    """Direct visibility into system state — real ledger data."""
    
    def __init__(self, dashboard_state, data_layer, simulator, nursery_bridge, evolution_engine):
        self.dashboard_state = dashboard_state
        self.data_layer = data_layer
        self.simulator = simulator
        self.nursery_bridge = nursery_bridge
        self.evolution_engine = evolution_engine
    
    def get_brain_state(self):
        state = self.dashboard_state.get('brain_state', 'UNKNOWN')
        reason = self.dashboard_state.get('brain_reason_code', 'unknown')
        text = self.dashboard_state.get('brain_reason_text', '')
        enforcement = self.dashboard_state.get('brain_enforcement', {})
        return {
            'state': state,
            'reason_code': reason,
            'reason_text': text,
            'enforcement': enforcement,
        }
    
    def get_arena_state(self):
        """Pull REAL data from ledger, not corrupted dashboard state."""
        if self.data_layer and hasattr(self.data_layer, 'get_arena_metrics'):
            try:
                metrics = self.data_layer.get_arena_metrics()
                return {
                    'total_trades': metrics.get('total_trades', 0),
                    'win_rate': metrics.get('win_rate', 0),
                    'pnl': metrics.get('pnl', 0),
                    'shadow_pnl': metrics.get('shadow_pnl', 0),
                    'paper_pnl': metrics.get('paper_pnl', 0),
                    'flip_rate': metrics.get('flip_rate', 0),
                }
            except:
                pass
        
        # Fallback (use dashboard state but validate)
        metrics = self.dashboard_state.get('metrics', {})
        total_trades = metrics.get('total_trades', 0)
        
        # Sanity check: if win_rate > 100% or PnL with 0 trades, it's garbage
        win_rate = metrics.get('rolling_win_rate', 0)
        if total_trades == 0 or (total_trades > 0 and (win_rate > 1.0 or win_rate < 0)):
            return {
                'total_trades': 0,
                'win_rate': 0,
                'pnl': 0,
                'shadow_pnl': 0,
                'paper_pnl': 0,
                'flip_rate': 0,
            }
        
        return {
            'total_trades': total_trades,
            'win_rate': win_rate,
            'pnl': metrics.get('pnl', 0),
            'shadow_pnl': metrics.get('shadow_pnl', 0),
            'paper_pnl': metrics.get('paper_pnl', 0),
            'flip_rate': metrics.get('flip_rate', 0),
        }
    
    def get_nursery_state(self):
        candidates = self.evolution_engine.babies if self.evolution_engine else []
        metrics = self.nursery_bridge.get_all_baby_metrics() if self.nursery_bridge else {}
        return {
            'baby_count': len(candidates),
            'babies': candidates,
            'metrics': metrics,
        }
    
    def get_recent_trades(self, limit=20):
        if self.data_layer:
            return self.data_layer.get_recent_trades(limit=limit) or []
        return []


class RockyThinkEngine:
    """No canned dialogue. Just work."""
    
    def __init__(self, workspace_dir, data_layer, user_name="D.J."):
        self.workspace_dir = workspace_dir
        self.data_layer = data_layer
        self.user_name = user_name
        self.brain_style = None
        self.brain_tuned = False
    
    def query(self, user_query: str) -> str:
        try:
            brain = self.data_layer.get_brain_state()
            arena = self.data_layer.get_arena_state()
            nursery = self.data_layer.get_nursery_state()
            trades = self.data_layer.get_recent_trades(limit=30)
            
            # Check if user is asking for calibration
            if not self.brain_tuned and self._is_calibration_request(user_query):
                return self._apply_brain_tuning(user_query, brain)
            
            # Otherwise, just respond to what they asked
            return self._respond(user_query, brain, arena, nursery, trades)
        
        except Exception as e:
            return f"Error: {e}"
    
    def _is_calibration_request(self, query):
        keywords = ['conservative', 'moderate', 'aggressive', 'calibrate', 'tune brain']
        return any(kw in query.lower() for kw in keywords)
    
    def _apply_brain_tuning(self, query, brain):
        """User asked for calibration. Apply it."""
        query_lower = query.lower()
        
        if 'conservative' in query_lower:
            self.brain_style = 'Conservative'
            settings = {
                'position_size': 0.30,
                'stop_loss': -50,
                'throttle_threshold': 15,
                'promotion_requirement': 200,
            }
            reasoning = "Capital protection first. Small positions. Hair-trigger stops."
        elif 'moderate' in query_lower:
            self.brain_style = 'Moderate'
            settings = {
                'position_size': 0.50,
                'stop_loss': -100,
                'throttle_threshold': 20,
                'promotion_requirement': 100,
            }
            reasoning = "Sweet spot. Edge gets room but we're protected."
        elif 'aggressive' in query_lower:
            self.brain_style = 'Aggressive'
            settings = {
                'position_size': 0.75,
                'stop_loss': -200,
                'throttle_threshold': 25,
                'promotion_requirement': 50,
            }
            reasoning = "Betting on the edge. Long leash. Scale if it works."
        else:
            return "Which style: Conservative, Moderate, or Aggressive?"
        
        self.brain_tuned = True
        
        msg = f"""BRAIN tuned to {self.brain_style}.

- Position size: {settings['position_size']*100:.0f}% of capital
- Stop loss: ${settings['stop_loss']}
- Throttle on sign flips > {settings['throttle_threshold']}%
- Promote babies beating Arena by ${settings['promotion_requirement']}+

{reasoning}

System is live."""
        
        self._log_observation(
            "BRAIN_CALIBRATION",
            f"Applied {self.brain_style}",
            reasoning
        )
        
        return msg
    
    def _respond(self, query, brain, arena, nursery, trades):
        """Just respond naturally to what they asked."""
        query_lower = query.lower().strip()
        
        arena_pnl = arena.get('shadow_pnl', 0)
        arena_trades = arena.get('total_trades', 0)
        win_rate = arena.get('win_rate', 0)
        flip_rate = arena.get('flip_rate', 0)
        brain_state = brain['state']
        
        # Status
        if any(w in query_lower for w in ['status', 'what', "what's", 'state', 'how']):
            msg = f"BRAIN: {brain_state} | Arena: {arena_trades} trades, ${arena_pnl:.2f} PnL | Nursery: {nursery['baby_count']} babies"
            
            if arena_trades < 20:
                msg += "\n\nStill building sample. Need 20+ trades to judge edge."
            elif arena_pnl < 0:
                msg += "\n\nWe're losing. Strategy isn't working."
            elif arena_pnl > 0 and arena_pnl < 50:
                msg += "\n\nBarely profitable. Edge exists but it's noisy."
            else:
                msg += "\n\nEdge is real. Now we scale."
            
            return msg
        
        # Profits
        if any(w in query_lower for w in ['profit', 'money', 'pnl', 'edge']):
            if arena_trades < 20:
                return f"Only {arena_trades} trades. Too early. Need 20+."
            
            msg = f"${arena_pnl:.2f} over {arena_trades} trades ({win_rate*100:.0f}% win rate).\n\n"
            
            if arena_pnl < 0:
                msg += "FAIL: Losing money. Direction is wrong or costs are killing it.\n"
                if win_rate < 0.50:
                    msg += "- Win rate below 50%: Signal is inverted. Try opposite logic."
                else:
                    msg += "- Win rate OK but losing: Execution bleed. Reduce size."
            elif arena_pnl > 0 and arena_pnl < 50:
                msg += "WEAK: Barely profitable. This is luck within noise.\n"
                msg += "- Per trade: ${:.2f}\n".format(arena_pnl/arena_trades)
                msg += "- Tighten execution. Only high conviction trades."
            else:
                msg += "GOOD: Edge is working.\n"
                msg += "- Per trade: ${:.2f}\n".format(arena_pnl/arena_trades)
                msg += "- Nursery learning?"
            
            self._log_observation("PROFIT_CHECK", f"${arena_pnl:.2f}", msg.split('\n')[1])
            return msg
        
        # Babies
        if any(w in query_lower for w in ['nursery', 'babies', 'baby', 'promote']):
            if nursery['baby_count'] == 0:
                return "Nursery empty. Spawn to test."
            
            msg = f"{nursery['baby_count']} babies running.\n"
            metrics = nursery['metrics']
            
            if metrics:
                sorted_babies = sorted(metrics, key=lambda m: m.get('shadow_pnl', 0), reverse=True)
                best = sorted_babies[0] if sorted_babies else None
                
                if best:
                    diff = best.get('shadow_pnl', 0) - arena_pnl
                    msg += f"\nBest: ${best.get('shadow_pnl', 0):.2f}. "
                    if diff > 200:
                        msg += f"Ready to promote (${diff:.0f} ahead)."
                    elif diff > 0:
                        msg += f"Ahead by ${diff:.0f}. Keep watching."
                    else:
                        msg += f"Behind by ${abs(diff):.0f}."
            else:
                msg += "Still accumulating trades."
            
            return msg
        
        # BRAIN
        if any(w in query_lower for w in ['brain', 'throttle', 'stop', 'flat']):
            msg = f"BRAIN is {brain_state}.\n"
            
            if brain_state == 'FLAT':
                msg += "System idle. Waiting for recovery or promotion."
            elif brain_state == 'STOP':
                msg += "System stopped. Detected problem. Check Arena."
            elif brain_state == 'THROTTLE':
                msg += f"Throttling. Instability detected. Sign flips at {flip_rate:.0f}%."
            else:
                msg += "Trading normally."
            
            return msg
        
        # Default
        return f"BRAIN: {brain_state} | Arena: {arena_trades} trades, ${arena_pnl:.2f} PnL | Nursery: {nursery['baby_count']} babies\n\nAsk me about profits, babies, BRAIN, or status."
    
    def _log_observation(self, category, observation, action):
        suggestions_file = Path(self.workspace_dir) / "MAKE_MONEY_SUGGESTIONS.md"
        if not suggestions_file.exists():
            suggestions_file.write_text("# MAKE_MONEY_SUGGESTIONS.md\n\n")
        
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] {category}\n**Observation:** {observation}\n**Action:** {action}\n"
        with open(suggestions_file, 'a') as f:
            f.write(entry)
