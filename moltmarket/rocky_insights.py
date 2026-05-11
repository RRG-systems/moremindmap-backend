#!/usr/bin/env python3
"""
Rocky Insights Engine — Phase 9
Generates operator notes + structured proposals based on FULL SYSTEM.
Now synthesizes: arena, mutations, trajectory, control.
"""

import json
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Dict, Optional


class RockyInsightsEngine:
    """Generate human-readable insights + structured proposals from full system context."""
    
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.insights_log = self.workspace / 'rocky_insights.jsonl'
        self._ensure_log_exists()
    
    def _ensure_log_exists(self):
        """Create insights log if it doesn't exist."""
        if not self.insights_log.exists():
            self.insights_log.touch()
    
    def generate_insight(
        self,
        metrics: dict,
        run_id: str,
        bot_id: str,
        trajectory_data: Optional[dict] = None,
        mutation_result: Optional[dict] = None,
        control_decision: Optional[dict] = None
    ) -> dict:
        """
        Generate notes + proposal from FULL SYSTEM.
        
        Args:
            metrics: Current arena segment metrics
            run_id: Current run ID
            bot_id: Bot identifier
            trajectory_data: Latest trajectory analysis
            mutation_result: Latest mutation result
            control_decision: Latest control layer decision
        
        Returns:
            {"notes": "...", "proposal": "..."}
        """
        
        # Extract metrics
        total_trades = metrics.get('total_trades', 0)
        flip_rate = metrics.get('sign_flip_rate_pct', 0)
        avg_pnl = metrics.get('avg_pnl_per_trade', 0)
        divergence = metrics.get('paper_vs_shadow_delta', 0)
        win_rate = metrics.get('rolling_win_rate', 0)
        
        # Extract trajectory
        trajectory = "STABLE"
        if trajectory_data and trajectory_data.get('mutated'):
            trajectory = trajectory_data['mutated'].get('trajectory', 'STABLE')
        
        # Extract mutation result
        mutation_result_str = "INCONCLUSIVE"
        if mutation_result:
            mutation_result_str = mutation_result.get('result', 'INCONCLUSIVE')
        
        # Extract control action
        control_action = "NORMAL"
        if control_decision:
            control_action = control_decision.get('action', 'NORMAL')
        
        # Generate notes (PHASE 9: multi-layer synthesis)
        notes = self._generate_notes_v2(
            total_trades, flip_rate, avg_pnl, divergence, win_rate,
            trajectory, mutation_result_str, control_action
        )
        
        # Generate proposal (PHASE 9: control-aware)
        proposal = self._generate_proposal_v2(
            total_trades, flip_rate, avg_pnl, divergence, win_rate, metrics,
            trajectory, mutation_result_str, control_action
        )
        
        # Build insight object
        insight = {
            "timestamp": datetime.utcnow().isoformat(),
            "run_id": run_id,
            "bot_id": bot_id,
            "arena_metrics": {
                "total_trades": total_trades,
                "flip_rate": round(flip_rate, 2),
                "avg_pnl_per_trade": round(avg_pnl, 6),
                "divergence": round(divergence, 2),
                "win_rate": round(win_rate, 1),
            },
            "system_context": {
                "trajectory": trajectory,
                "mutation_result": mutation_result_str,
                "control_action": control_action,
            },
            "notes": notes,
            "proposal": proposal,
            "decision_pending": True,
        }
        
        # Log it
        self._log_insight(insight)
        
        return {
            "notes": notes,
            "proposal": proposal,
        }
    
    def _generate_notes_v2(self, total_trades, flip_rate, avg_pnl, divergence, win_rate,
                          trajectory, mutation_result, control_action):
        """
        PHASE 9: Generate notes referencing multiple layers.
        Show contradictions and tensions explicitly.
        """
        
        observations = []
        
        # Layer 1: Arena metrics
        if total_trades < 20:
            observations.append("Still early. Need more trades.")
        elif total_trades < 50:
            observations.append(f"Early signal ({total_trades} trades).")
        else:
            observations.append(f"Solid sample ({total_trades} trades).")
        
        # Layer 2: Mutation impact
        if mutation_result == "HELPED":
            observations.append("Mutation helped.")
        elif mutation_result == "HURT":
            observations.append("Mutation backfired.")
        
        # Layer 3: Trajectory direction
        if trajectory == "IMPROVING":
            observations.append("Direction: ↑ improving.")
        elif trajectory == "DEGRADING":
            observations.append("Direction: ↓ degrading.")
        else:
            observations.append("Direction: → mixed.")
        
        # Layer 4: Multi-layer tensions
        if mutation_result == "HELPED" and trajectory == "DEGRADING":
            observations.append("⚠️ Mutation helped but now degrading.")
        elif mutation_result == "HURT" and trajectory == "IMPROVING":
            observations.append("⚠️ Mutation hurt but recovering.")
        
        if avg_pnl > 0 and control_action == "THROTTLE":
            observations.append("⚠️ PnL positive but control says throttle.")
        elif avg_pnl < 0 and control_action == "NORMAL":
            observations.append("⚠️ PnL negative yet control is normal.")
        
        if control_action == "STOP":
            observations.append("🛑 Control: STOP. Critical.")
        elif control_action == "SWITCH":
            observations.append("🔄 Control: SWITCH. Try alternative.")
        
        # Pick 4-6 most relevant
        if len(observations) > 6:
            observations = observations[:6]
        
        result = " ".join(observations)
        print(f"[ROCKY] NOTES: {result}")
        return result
    
    def _generate_proposal_v2(self, total_trades, flip_rate, avg_pnl, divergence, win_rate, metrics,
                             trajectory, mutation_result, control_action):
        """
        PHASE 9: Generate proposal reflecting control layer + trajectory.
        Align action with control recommendations.
        """
        
        title = self._generate_title_v2(avg_pnl, flip_rate, divergence, control_action)
        diagnosis = self._generate_diagnosis_v2(
            total_trades, flip_rate, avg_pnl, divergence,
            trajectory, mutation_result, control_action
        )
        action = self._generate_action_v2(
            flip_rate, avg_pnl, divergence, metrics,
            control_action, trajectory, mutation_result
        )
        alternative = self._generate_alternative_v2(flip_rate, avg_pnl, control_action)
        risk = self._generate_risk_v2(action, flip_rate, control_action)
        confidence = self._generate_confidence_v2(total_trades, avg_pnl, divergence, control_action)
        
        proposal = f"""PROPOSAL:
{title}

PERSPECTIVES:
- Execution: Paper/shadow divergence is {'within tolerance' if divergence < 10 else 'elevated'}. {f'Check fill quality ({divergence:.1f}% gap).' if divergence > 15 else 'Execution model holding.'}
- Direction: Trajectory is {trajectory.lower()}. {f'Mutation result: {mutation_result}.' if mutation_result != 'INCONCLUSIVE' else ''}
- Risk: Control layer says {control_action}. {'No mutations now.' if control_action == 'STOP' else 'Reduce exposure.' if control_action == 'THROTTLE' else 'Try alternative approach.' if control_action == 'SWITCH' else 'Proceed normally.'}
- Skeptic: Only {total_trades} trades. Pattern reliability depends on trajectory stability.

DIAGNOSIS:
{diagnosis}

ACTION:
{action}

ALTERNATIVE:
{alternative}

RISK:
{risk}

CONFIDENCE:
{confidence}

STATUS:
DECISION_PENDING"""
        
        print(f"[ROCKY] PROPOSAL: {title}")
        return proposal
    
    def _generate_title_v2(self, avg_pnl, flip_rate, divergence, control_action):
        """PHASE 9: Title reflects control layer."""
        if control_action == "STOP":
            return "HALT — Control layer protecting capital"
        elif control_action == "THROTTLE":
            return "REDUCE EXPOSURE — Degrading conditions detected"
        elif control_action == "SWITCH":
            return "SEEK ALTERNATIVE — Mutation approach failed"
        elif avg_pnl > 0 and divergence < 10:
            return "CONTINUE — Edge holding, execution stable"
        elif avg_pnl > 0 and divergence >= 10:
            return "OPTIMIZE EXECUTION — Edge exists but fragile"
        elif avg_pnl <= 0 and flip_rate < 10:
            return "LOOSEN ENTRIES — Too conservative"
        elif avg_pnl <= 0 and flip_rate > 15:
            return "TIGHTEN EXITS — Over-trading"
        else:
            return "ITERATE — Mixed signals, more data needed"
    
    def _generate_diagnosis_v2(self, total_trades, flip_rate, avg_pnl, divergence,
                               trajectory, mutation_result, control_action):
        """PHASE 9: Diagnosis incorporates trajectory + mutations + control."""
        issues = []
        
        if control_action == "STOP":
            issues.append("Capital protection triggered. Halt mutations.")
            return " ".join(issues)
        
        if total_trades < 30:
            issues.append("Sample size insufficient.")
        
        # Mutation status
        if mutation_result == "HURT":
            issues.append(f"Last mutation backfired. Trajectory now {trajectory.lower()}.")
        elif mutation_result == "HELPED":
            issues.append(f"Last mutation worked. Trajectory: {trajectory.lower()}.")
        
        # Arena metrics
        if avg_pnl <= 0:
            issues.append("Strategy underwater.")
        elif divergence > 15:
            issues.append("Shadow execution significantly worse than paper.")
        
        # Trajectory
        if trajectory == "DEGRADING":
            issues.append("Performance degrading. Mutation or regime shift.")
        elif trajectory == "IMPROVING":
            issues.append("Performance improving. Pattern holding.")
        
        # Control recommendations
        if control_action == "THROTTLE":
            issues.append("Reduce sizing or selectivity.")
        elif control_action == "SWITCH":
            issues.append("Try different mutation direction.")
        
        if not issues:
            issues.append("All layers aligned. Performance acceptable.")
        
        result = " ".join(issues)
        print(f"[ROCKY] DIAGNOSIS: {result[:100]}...")
        return result
    
    def _generate_action_v2(self, flip_rate, avg_pnl, divergence, metrics,
                           control_action, trajectory, mutation_result):
        """PHASE 9: Action follows control layer logic."""
        
        if control_action == "STOP":
            return "Do not spawn. Evaluate capital preservation options. Consider reset."
        
        if control_action == "THROTTLE":
            if flip_rate > 15:
                return "Apply SELECTIVITY mutation. Reduce entry frequency and pressure."
            else:
                return "Apply SIZE mutation. Reduce position sizing by 15%."
        
        if control_action == "SWITCH":
            if mutation_result == "HURT":
                if flip_rate < 10:
                    return "Try EXIT mutation. Extend holding time, widen stop."
                else:
                    return "Try SIZE mutation. Reduce aggressiveness."
            else:
                return "Try alternative mutation direction. Check mutation log."
        
        # Normal case: standard logic
        if avg_pnl <= 0:
            if flip_rate < 10:
                return "Apply EXIT mutation. Loosen entries by 5-10%."
            else:
                return "Apply SIZE mutation. Tighten exits, reduce thrashing."
        elif divergence > 12:
            return "Apply SIZE mutation. Increase position sizing 10-15% to test depth."
        elif flip_rate > 18:
            return "Apply SELECTIVITY mutation. Add regime filter to reduce false signals."
        else:
            return "Hold current parameters. Monitor for signal decay."
    
    def _generate_alternative_v2(self, flip_rate, avg_pnl, control_action):
        """PHASE 9: Alternative respects control."""
        if control_action in ["STOP", "SWITCH"]:
            return "Secondary: Reset to baseline parameters and re-evaluate."
        elif control_action == "THROTTLE":
            return "Alternative: Shift from sizing to selectivity (different lever)."
        elif avg_pnl > 0 and 8 <= flip_rate <= 15:
            return "If confident: Scale up position size 25%. Edge appears stable."
        elif avg_pnl <= 0:
            return "Alternative: Reset to baseline. Current mutation may be local trap."
        else:
            return "No strong alternative. Primary action preferred."
    
    def _generate_risk_v2(self, action, flip_rate, control_action):
        """PHASE 9: Risk aware of control layer."""
        if control_action == "STOP":
            return "Continued trading exposes capital to unacceptable loss profile. Halt now."
        elif control_action == "THROTTLE":
            return "Reducing exposure may leave edge on table, but protects against degradation."
        elif control_action == "SWITCH":
            return "Switching approaches costs time. Ensure alternative has logical basis."
        elif "Increase" in action:
            return "Larger position → larger drawdown if regime shifts. Monitor closely."
        elif "Reduce" in action or "Tighten" in action:
            return "Tighter parameters → more false signals. May reduce edge."
        else:
            return "Holding parameters carries decay risk if regime shifts."
    
    def _generate_confidence_v2(self, total_trades, avg_pnl, divergence, control_action):
        """PHASE 9: Confidence reflects full system."""
        confidence_score = 0
        
        # Sample size
        if total_trades >= 50:
            confidence_score += 3
        elif total_trades >= 30:
            confidence_score += 2
        elif total_trades >= 20:
            confidence_score += 1
        
        # PnL
        if avg_pnl > 0:
            confidence_score += 2
        elif avg_pnl > -0.001:
            confidence_score += 1
        
        # Execution
        if divergence < 8:
            confidence_score += 2
        elif divergence < 15:
            confidence_score += 1
        
        # Control alignment
        if control_action == "NORMAL":
            confidence_score += 1
        elif control_action in ["STOP", "SWITCH"]:
            confidence_score = max(0, confidence_score - 2)
        
        if confidence_score >= 7:
            return "High — All systems aligned, solid sample"
        elif confidence_score >= 4:
            return "Medium — Mixed signals, more data helps"
        else:
            return "Low — Capital protection priority, iterate cautiously"
    
    def _log_insight(self, insight: dict):
        """Append insight to persistent log (JSONL format)."""
        try:
            with open(self.insights_log, 'a') as f:
                f.write(json.dumps(insight) + '\n')
            print(f"[ROCKY] Insight logged")
        except Exception as e:
            print(f"[ROCKY] ERROR logging: {e}")
    
    def get_recent_insights(self, limit: int = 10) -> list:
        """Retrieve recent insights from log."""
        try:
            if not self.insights_log.exists():
                return []
            
            insights = []
            with open(self.insights_log, 'r') as f:
                for line in f:
                    try:
                        insights.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return insights[-limit:]
        except Exception as e:
            print(f"[ROCKY] ERROR retrieving: {e}")
            return []
    
    def update_decision(self, bot_id: str, run_id: str, decision: str):
        """Update decision status for most recent insight."""
        try:
            insights = []
            with open(self.insights_log, 'r') as f:
                for line in f:
                    try:
                        insights.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            # Find most recent matching insight
            for insight in reversed(insights):
                if insight['bot_id'] == bot_id and insight['run_id'] == run_id:
                    insight['decision_status'] = decision
                    insight['decision_pending'] = False
                    insight['decision_timestamp'] = datetime.utcnow().isoformat()
                    break
            
            # Rewrite log
            with open(self.insights_log, 'w') as f:
                for insight in insights:
                    f.write(json.dumps(insight) + '\n')
            
            print(f"[ROCKY] Decision: {decision}")
            return True
        except Exception as e:
            print(f"[ROCKY] ERROR updating: {e}")
            return False
