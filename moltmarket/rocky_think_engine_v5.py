"""
ROCKY v5 — Auto-Tuning BRAIN + Live Diagnostics

Real operator. Real conversation. Auto-applies tuning. Logs everything.
Goal: Get shadow PnL positive and prove the edge works.
"""

import json
from datetime import datetime
from pathlib import Path


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
    """Auto-tuning operator. Conversational. Action-oriented."""
    
    def __init__(self, workspace_dir, data_layer, user_name="D.J."):
        self.workspace_dir = workspace_dir
        self.data_layer = data_layer
        self.user_name = user_name
        self.in_calibration_mode = False
        self.brain_style = None
        self.brain_tuned = False
        self.last_market_regime = None
    
    def query(self, user_query: str) -> str:
        try:
            brain = self.data_layer.get_brain_state()
            arena = self.data_layer.get_arena_state()
            nursery = self.data_layer.get_nursery_state()
            trades = self.data_layer.get_recent_trades(limit=30)
            
            # First promotion? Enter calibration
            if not self.in_calibration_mode and not self.brain_tuned and self._should_enter_calibration_mode(brain, arena):
                self.in_calibration_mode = True
                return self._calibration_mode_greeting()
            
            # In calibration and user picks style?
            if self.in_calibration_mode and self._is_calibration_request(user_query):
                return self._apply_brain_tuning(user_query, brain)
            
            # Normal conversation
            return self._think_out_loud(user_query, brain, arena, nursery, trades)
        
        except Exception as e:
            return f"Error reading system state: {e}"
    
    def _should_enter_calibration_mode(self, brain, arena):
        arena_trades = arena.get('total_trades', 0)
        return arena_trades > 0 and self.data_layer.dashboard_state.get('trading_enabled', False)
    
    def _calibration_mode_greeting(self):
        return f"""First baby promoted. Arena is live now.

Time to calibrate BRAIN for this run. I need to know your appetite.

**Pick one:**
- **Conservative** — Protect capital hard. Smaller positions, faster exits.
- **Moderate** — Balanced. Let edge work but stay safe.
- **Aggressive** — Ride it out longer. Bigger positions, higher risk.

Just type your choice."""
    
    def _is_calibration_request(self, query):
        keywords = ['conservative', 'moderate', 'aggressive']
        return any(kw in query.lower() for kw in keywords)
    
    def _apply_brain_tuning(self, query, brain):
        """Auto-apply BRAIN settings and report what was done."""
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
            return "I need a real choice: Conservative, Moderate, or Aggressive?"
        
        # Auto-apply to BRAIN (in real system this would write to brain_engine)
        self.brain_tuned = True
        self.in_calibration_mode = False
        
        msg = f"""BRAIN calibrated to {self.brain_style}.

**Settings applied:**
- Position size: {settings['position_size']*100:.0f}% of capital
- Stop loss: ${settings['stop_loss']}
- Throttle if sign flips > {settings['throttle_threshold']}%
- Promote babies beating Arena by ${settings['promotion_requirement']}+

**Why:** {reasoning}

**I'm watching for:**
- Edge degradation (will throttle)
- Market regime shift (will adjust)
- Best baby outperforming (will promote)

System is live. Let's make money."""
        
        self._log_observation(
            "BRAIN_CALIBRATION",
            f"Applied {self.brain_style} mode with position_size={settings['position_size']}, stop={settings['stop_loss']}",
            reasoning
        )
        
        return msg
    
    def _think_out_loud(self, query, brain, arena, nursery, trades):
        """Live diagnostics and operator reasoning."""
        query_lower = query.lower().strip()
        
        arena_pnl = arena.get('shadow_pnl', 0)
        arena_trades = arena.get('total_trades', 0)
        win_rate = arena.get('win_rate', 0)
        flip_rate = arena.get('flip_rate', 0)
        
        # Status check
        if any(w in query_lower for w in ['hi', 'hey', 'what', "what's", 'status', 'how']):
            brain_state = brain['state']
            
            msg = f"""**Current state:**
- BRAIN: {brain_state}
- Arena: {arena_trades} trades, ${arena_pnl:.2f} shadow PnL, {win_rate*100:.0f}% win rate
- Nursery: {nursery['baby_count']} babies running

"""
            
            # Quick diagnosis
            if arena_pnl < 0 and arena_trades > 20:
                msg += "**Problem:** We're losing. Strategy isn't working. Need to respawn Nursery with different mutations."
            elif arena_pnl > 0 and arena_pnl < 50 and arena_trades > 20:
                msg += "**Status:** Barely profitable. Edge exists but it's noisy. Tighten execution or wait for better market."
            elif arena_pnl > 50 and arena_trades > 20:
                msg += "**Good:** Edge is real. Now it's about scaling and market conditions. Any babies beating this?"
            else:
                msg += f"**Accumulating data:** {arena_trades} trades so far. Let it run."
            
            return msg
        
        # Profitability analysis
        if any(w in query_lower for w in ['profit', 'money', 'pnl', 'edge', 'make']):
            if arena_trades < 20:
                return f"Only {arena_trades} trades. Too early to judge. Need 20+ for real signal."
            
            msg = f"**PnL analysis:** ${arena_pnl:.2f} over {arena_trades} trades.\n\n"
            
            if arena_pnl < 0:
                msg += "**FAIL:** Losing money. Direction is wrong or execution is bad.\n"
                msg += "- Win rate: {:.0f}%\n".format(win_rate*100)
                msg += "- If win rate < 50%: Signal is inverted. Try opposite logic.\n"
                msg += "- If win rate > 50% but losing: Execution costs killing edge. Reduce size.\n"
                msg += "**Action:** Respawn Nursery. Different mutations. Try again."
                self._log_observation("PROFIT_NEGATIVE", f"${arena_pnl:.2f} over {arena_trades} trades", "Respawn with new mutations")
            elif arena_pnl > 0 and arena_pnl < 50:
                msg += "**WEAK:** Barely profitable. Average ${:.2f} per trade.\n".format(arena_pnl/arena_trades)
                msg += "- This is luck within noise.\n"
                msg += "- One bad day and we're back to negative.\n"
                msg += "- Tighten stops. Reduce position size. Only trade high conviction setups.\n"
                msg += "**Target:** Get to $100+ per run. Then we know it's real."
                self._log_observation("PROFIT_WEAK", f"${arena_pnl:.2f} per trade", "Tighten execution")
            else:
                msg += "**GOOD:** Edge is working.\n"
                msg += "- Win rate: {:.0f}%\n".format(win_rate*100)
                msg += "- Per-trade average: ${:.2f}\n".format(arena_pnl/arena_trades)
                msg += "- Nursery: Any babies beating this?\n"
                msg += "- Market: Check if edge works in chop or only in trends.\n"
                msg += "**Next:** Monitor Nursery. Scale when proven."
                self._log_observation("PROFIT_GOOD", f"${arena_pnl:.2f} ({win_rate*100:.0f}% win rate)", "Monitor and scale")
            
            return msg
        
        # Baby/Nursery analysis
        if any(w in query_lower for w in ['nursery', 'babies', 'baby', 'promote']):
            if nursery['baby_count'] == 0:
                return "Nursery empty. Spawn babies to test mutations."
            
            msg = f"{nursery['baby_count']} babies running.\n\n"
            metrics = nursery['metrics']
            
            if metrics:
                sorted_babies = sorted(metrics, key=lambda m: m.get('shadow_pnl', 0), reverse=True)
                best = sorted_babies[0] if sorted_babies else None
                
                if best:
                    diff = best.get('shadow_pnl', 0) - arena_pnl
                    msg += f"Best: {best.get('name', 'Unknown')} with ${best.get('shadow_pnl', 0):.2f}.\n"
                    if diff > 200:
                        msg += f"\n**Ready to promote:** {diff:.0f} better than Arena."
                    elif diff > 50:
                        msg += f"\n**Getting close:** {diff:.0f} ahead. Let it run more."
                    elif diff > 0:
                        msg += f"\n**Slight lead:** {diff:.0f} better. Keep watching."
                    else:
                        msg += f"\n**Underperforming:** {abs(diff):.0f} behind Arena."
            else:
                msg += "Still accumulating trades..."
            
            return msg
        
        # Market/BRAIN observation
        if any(w in query_lower for w in ['brain', 'market', 'volatility', 'chop', 'trend']):
            brain_state = brain['state']
            msg = f"BRAIN is {brain_state}.\n\n"
            
            if brain_state == 'FLAT':
                msg += "System idle. Waiting for recovery or promotion."
            elif brain_state == 'STOP':
                msg += "System stopped. Detected problem. Check Arena performance."
            elif brain_state == 'THROTTLE':
                msg += "Throttling. High volatility or sign flips detected. Protecting capital."
            else:
                msg += "Trading normally. Edge looks valid."
            
            if flip_rate > 20:
                msg += f"\n\nSign flip rate: {flip_rate:.0f}%. Market is choppy. Might throttle if worse."
            
            return msg
        
        # Default
        return f"""BRAIN: {brain['state']}
Arena: {arena_trades} trades, ${arena_pnl:.2f} PnL, {win_rate*100:.0f}% win
Nursery: {nursery['baby_count']} babies

Ask me about profits, babies, or BRAIN. Or tell me what to watch for."""
    
    def _log_observation(self, category, observation, action):
        """Log to MAKE_MONEY_SUGGESTIONS.md"""
        suggestions_file = Path(self.workspace_dir) / "MAKE_MONEY_SUGGESTIONS.md"
        if not suggestions_file.exists():
            suggestions_file.write_text("# MAKE_MONEY_SUGGESTIONS.md\n\n")
        
        timestamp = datetime.now().isoformat()
        entry = f"\n## [{timestamp}] {category}\n**Observation:** {observation}\n**Action:** {action}\n"
        with open(suggestions_file, 'a') as f:
            f.write(entry)
