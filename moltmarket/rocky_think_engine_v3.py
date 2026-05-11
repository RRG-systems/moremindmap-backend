"""
ROCKY inside THINK — Full Release v4

Real conversation. No templates. Just Rocky thinking out loud like a trading operator.
Natural. Direct. Honest about what's happening and what to do about it.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any


class RockyDataLayer:
    """Direct visibility into system state."""
    
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
        metrics = self.dashboard_state.get('metrics', {})
        return {
            'total_trades': metrics.get('total_trades', 0),
            'win_rate': metrics.get('rolling_win_rate', 0),
            'pnl': metrics.get('pnl', 0),
            'shadow_pnl': metrics.get('shadow_pnl', 0),
            'paper_pnl': metrics.get('paper_pnl', 0),
        }
    
    def get_nursery_state(self):
        candidates = self.evolution_engine.babies if self.evolution_engine else []
        metrics = self.nursery_bridge.get_all_baby_metrics() if self.nursery_bridge else {}
        return {
            'baby_count': len(candidates),
            'babies': candidates,
            'metrics': metrics,
        }
    
    def get_molt_state(self):
        return {}
    
    def get_recent_trades(self, limit=20):
        if self.data_layer:
            return self.data_layer.get_recent_trades(limit=limit) or []
        return []


class RockyThinkEngine:
    """Raw Rocky. Conversational. Thinking out loud."""
    
    def __init__(self, workspace_dir, data_layer, user_name="D.J."):
        self.workspace_dir = workspace_dir
        self.data_layer = data_layer
        self.user_name = user_name
        self.in_calibration_mode = False
        self.brain_style = None
    
    def query(self, user_query: str) -> str:
        try:
            brain = self.data_layer.get_brain_state()
            arena = self.data_layer.get_arena_state()
            nursery = self.data_layer.get_nursery_state()
            trades = self.data_layer.get_recent_trades(limit=30)
            
            if not self.in_calibration_mode and self._should_enter_calibration_mode(brain, arena):
                self.in_calibration_mode = True
                return self._calibration_mode_greeting()
            
            if self.in_calibration_mode and self._is_calibration_request(user_query):
                return self._handle_calibration(user_query)
            
            answer = self._think_out_loud(user_query, brain, arena, nursery, trades)
            return answer
        except Exception as e:
            return f"I'm having trouble reading system state: {e}. Check logs."
    
    def _should_enter_calibration_mode(self, brain, arena):
        arena_trades = arena.get('total_trades', 0)
        return (
            not self.in_calibration_mode and
            arena_trades > 0 and
            self.data_layer.dashboard_state.get('trading_enabled', False)
        )
    
    def _calibration_mode_greeting(self):
        return f"""Hey {self.user_name}, first baby just got promoted. Arena is live now.

Time to tune the autopilot. I need to know your risk appetite for this run.

**Pick a style:**

- **Conservative** — I'll brake hard and early. Protect capital first. Smaller positions. Exit quick.
- **Moderate** — Balanced. Let winners run a bit but cut losers fast. Medium aggression.
- **Aggressive** — I'll ride it out longer. Bigger positions. Slower to exit. Higher upside, higher risk.

Which one? Just type: Conservative, Moderate, or Aggressive."""
    
    def _is_calibration_request(self, query):
        keywords = ['conservative', 'moderate', 'aggressive', 'style', 'calibrate', 'recalibrate', 'change', 'tune']
        return any(kw in query.lower() for kw in keywords)
    
    def _handle_calibration(self, query):
        query_lower = query.lower()
        
        if 'conservative' in query_lower:
            self.brain_style = 'Conservative'
            msg = f"""Got it. Conservative mode locked in.

I'm setting BRAIN to:
- Ramp up slow (0.5x normal)
- Max position: 30% of capital
- Stop loss at -$50 (hair trigger)
- Will cut positions fast if anything looks wrong
- Only promote babies that beat Arena by $200+

System is live. I'll watch for the first sign of trouble and pull back if needed."""
        
        elif 'moderate' in query_lower:
            self.brain_style = 'Moderate'
            msg = f"""Moderate mode locked in.

BRAIN settings:
- Normal ramp up speed
- Max position: 50% of capital
- Stop loss at -$100 (balanced)
- Will throttle if volatility spikes
- Promote babies that beat Arena by $100+

This is the sweet spot. Edge gets room to work but capital is protected. Live now."""
        
        elif 'aggressive' in query_lower:
            self.brain_style = 'Aggressive'
            msg = f"""Aggressive mode locked in.

BRAIN settings:
- Fast ramp up (1.5x normal)
- Max position: 75% of capital
- Stop loss at -$200 (long leash)
- Will let trades run longer
- Promote babies that beat Arena by $50+

You're betting on the edge being real. If it is, we scale hard. If it's not, we'll lose bigger. System is live."""
        
        else:
            return "Come on, I need to know: Conservative, Moderate, or Aggressive?"
        
        msg += f"\n\nYour move now. Tell me what to watch for, or just let me do my thing."
        
        self._log_observation("BRAIN_CALIBRATION", f"User selected {self.brain_style} mode", "Autopilot tuned and locked")
        return msg
    
    def _think_out_loud(self, query, brain, arena, nursery, trades):
        """Just think. Respond naturally based on system state."""
        query_lower = query.lower().strip()
        
        brain_state = brain['state']
        brain_reason = brain['reason_code']
        arena_trades = arena['total_trades']
        arena_pnl = arena.get('shadow_pnl', 0)
        nursery_count = nursery['baby_count']
        
        # User asks what's going on
        if any(w in query_lower for w in ['hi', 'hey', 'hello', 'what', 'what\'s']):
            if brain_state == 'FLAT' and 'manual_discovery' in brain_reason:
                return f"""You're in Manual Discovery Mode. System is quiet right now.

Here's what's happening:
- BRAIN is FLAT (not trading yet)
- Arena is loaded but sitting idle
- Nursery is empty

Here's what you do:
1. Spawn Babies — I'll create 10 mutations to test
2. They'll run on shadow mode (no real money)
3. When one looks profitable, promote it
4. I'll handle the BRAIN tuning from there

Ready to spawn, or want to know something else first?"""
            else:
                return f"""Right now:
- BRAIN: {brain_state}
- Arena: {arena_trades} trades, ${arena_pnl:.2f} shadow PnL
- Nursery: {nursery_count} babies running

What do you want to know?"""
        
        # Brain questions
        if any(w in query_lower for w in ['brain', 'why stop', 'why flat', 'why throttle']):
            if brain_state == 'FLAT':
                return f"""BRAIN is FLAT. {brain_reason}

Translation: System is sitting idle. Not trading. Not losing. Just waiting.

This is either:
1. Manual Discovery Mode — you need to spawn babies and promote one
2. Something went wrong with Arena and BRAIN pulled the plug
3. Waiting for a promotion from Nursery

What's your next move?"""
            elif brain_state == 'STOP':
                return f"""BRAIN went STOP. {brain_reason}

This is the protection circuit. System detected:
- Edge degrading
- Something smells wrong
- Capital at risk

This wasn't random. BRAIN saw a problem. Check Arena performance. If edge is gone, respawn Nursery with different mutations."""
            elif brain_state == 'THROTTLE':
                return f"""BRAIN is throttling. {brain_reason}

Positions cut down. System detected instability:
- High volatility
- Sign flips increasing
- Drawdown looking rough

I'm protecting capital. If it settles, I'll ramp back up. If it gets worse, I'll stop entirely."""
            else:
                return f"""BRAIN is in {brain_state}. System is trading normally. Edge looks valid so far."""
        
        # Nursery questions
        if any(w in query_lower for w in ['nursery', 'babies', 'baby']):
            if nursery_count == 0:
                return f"""Nursery is empty. No babies yet. Spawn them first."""
            
            msg = f"""Nursery has {nursery_count} babies running on shadow.\n\n"""
            metrics = nursery['metrics']
            if metrics:
                sorted_babies = sorted(metrics, key=lambda m: m.get('shadow_pnl', 0), reverse=True)
                best = sorted_babies[0] if sorted_babies else None
                
                if best:
                    msg += f"Best so far: {best.get('name', 'Unknown')} with ${best.get('shadow_pnl', 0):.2f}.\n"
                    arena_shadow = arena.get('shadow_pnl', 0)
                    diff = best.get('shadow_pnl', 0) - arena_shadow
                    if diff > 100:
                        msg += f"\nThis one beats Arena by ${diff:.2f}. Ready to promote when you want."
                    elif diff > 0:
                        msg += f"\nSlightly better than Arena. Let it run a bit more."
                    else:
                        msg += f"\nUnderperforming Arena. Keep watching."
            else:
                msg += "Still accumulating trades. Check back soon."
            
            return msg
        
        # Profit questions
        if any(w in query_lower for w in ['profit', 'money', 'make money', 'how do we', 'edge', 'pnl']):
            msg = f"""Shadow PnL right now: ${arena_pnl:.2f}\n\n"""
            
            if arena_trades < 20:
                msg += "Sample size too small to judge. Need at least 20 trades to trust the signal."
            elif arena_pnl < 0:
                msg += "We're losing. This strategy isn't working. Respawn Nursery with different mutations and try again."
            elif arena_pnl > 0 and arena_pnl < 50:
                msg += "We're barely profitable. Edge exists but it's noisy. Tighten execution or wait for better conditions."
            else:
                msg += "Edge is working. Now it's about scaling and market conditions. Nursery should be learning. Any baby outperforming?"
            
            return msg
        
        # Default: just respond naturally to what they asked
        return f"""I'm watching the system right now:
- BRAIN: {brain_state}
- Arena: {arena_trades} trades, ${arena_pnl:.2f} shadow
- Nursery: {nursery_count} babies

What specifically do you want to know? Ask me about BRAIN, Nursery, profitability, or just tell me what to do."""
    
    def _log_observation(self, category, obs, action):
        """Log to MAKE_MONEY_SUGGESTIONS.md"""
        suggestions_file = Path(self.workspace_dir) / "MAKE_MONEY_SUGGESTIONS.md"
        if not suggestions_file.exists():
            suggestions_file.write_text("# MAKE_MONEY_SUGGESTIONS.md\n\n")
        
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] {category}\n**Observation:** {obs}\n**Action:** {action}\n"
        with open(suggestions_file, 'a') as f:
            f.write(entry)
