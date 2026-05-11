#!/usr/bin/env python3
"""
Rocky's Reasoning Layer — Phase 2.5
Uses THINK Memory to generate grounded, evidence-backed insights.

Key principle: Memory → reasoning → natural output
No data dumps. Weave history into conversation.
"""

import json
import sqlite3
from pathlib import Path
from datetime import datetime


class RockyReasoning:
    """
    Rocky's conversational reasoning engine.
    Uses THINK Memory to ground responses in real history.
    """
    
    def __init__(self, think_db_path=None):
        """
        Initialize Rocky's reasoning layer.
        
        Args:
            think_db_path: Path to THINK Memory SQLite database
        """
        if not think_db_path:
            think_db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
        
        self.db_path = think_db_path
        self.db_conn = None
    
    def connect(self):
        """Open database connection"""
        self.db_conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        self.db_conn.row_factory = sqlite3.Row
        return self.db_conn
    
    def close(self):
        """Close database connection"""
        if self.db_conn:
            self.db_conn.close()
            self.db_conn = None
    
    # =====================================================
    # MEMORY FETCHES
    # =====================================================
    
    def _fetch_bot_origin(self, bot_id):
        """Fetch bot origin with hypothesis and mutation chain"""
        cursor = self.db_conn.cursor()
        
        # Get bot
        cursor.execute("SELECT * FROM bots WHERE bot_id = ?", [bot_id])
        bot = cursor.fetchone()
        if not bot:
            return None
        
        bot = dict(bot)
        
        # Get hypothesis
        cursor.execute("SELECT * FROM hypotheses WHERE hypothesis_id = ?", [bot['hypothesis_id']])
        hyp = cursor.fetchone()
        if hyp:
            hyp = dict(hyp)
            hyp['failure_modes'] = json.loads(hyp['failure_modes'] or '[]')
        
        # Get mutation that created this bot (if any)
        mutation = None
        if bot['created_by_mutation_id']:
            cursor.execute("SELECT * FROM mutations WHERE mutation_id = ?", [bot['created_by_mutation_id']])
            mutation = cursor.fetchone()
            if mutation:
                mutation = dict(mutation)
                mutation['parameter_changes'] = json.loads(mutation['parameter_changes'])
        
        return {
            'bot': bot,
            'hypothesis': hyp,
            'mutation': mutation
        }
    
    def _fetch_hypothesis_history(self, hypothesis_id):
        """Fetch mutation history on hypothesis"""
        cursor = self.db_conn.cursor()
        
        # Get all mutations
        cursor.execute("""
            SELECT * FROM mutations
            WHERE hypothesis_id = ?
            ORDER BY created_at DESC
        """, [hypothesis_id])
        
        mutations = [dict(row) for row in cursor.fetchall()]
        
        # Parse JSON fields
        for mut in mutations:
            mut['parameter_changes'] = json.loads(mut['parameter_changes'])
        
        # Summarize by result
        summary = {
            'total': len(mutations),
            'helped': [],
            'hurt': [],
            'inconclusive': [],
            'pending': []
        }
        
        for mut in mutations:
            if mut['result'] in summary:
                summary[mut['result']].append({
                    'diagnosis': mut['diagnosis'],
                    'mutation_type': mut['mutation_type'],
                    'summary': mut['result_summary']
                })
        
        return summary
    
    def _fetch_prior_attempts(self, hypothesis_id, issue):
        """Find prior attempts at this issue"""
        cursor = self.db_conn.cursor()
        
        # Search for similar diagnoses
        cursor.execute("""
            SELECT * FROM mutations
            WHERE hypothesis_id = ? AND diagnosis LIKE ?
            ORDER BY created_at DESC
        """, [hypothesis_id, f"%{issue}%"])
        
        results = [dict(row) for row in cursor.fetchall()]
        for row in results:
            row['parameter_changes'] = json.loads(row['parameter_changes'])
        
        return results
    
    def _fetch_hypothesis_status(self, hypothesis_id):
        """Fetch hypothesis performance summary"""
        cursor = self.db_conn.cursor()
        
        cursor.execute("SELECT * FROM hypotheses WHERE hypothesis_id = ?", [hypothesis_id])
        hyp = dict(cursor.fetchone())
        
        cursor.execute("""
            SELECT COUNT(*) as total,
                   SUM(CASE WHEN current_status = 'promoted' THEN 1 ELSE 0 END) as promoted,
                   SUM(CASE WHEN current_status = 'failed' THEN 1 ELSE 0 END) as failed,
                   MAX(CASE WHEN current_status = 'promoted' THEN latest_metrics_json ELSE NULL END) as best_metrics
            FROM bots
            WHERE hypothesis_id = ?
        """, [hypothesis_id])
        
        bot_stats = dict(cursor.fetchone())
        if bot_stats['best_metrics']:
            bot_stats['best_metrics'] = json.loads(bot_stats['best_metrics'])
        
        return {
            'hypothesis': hyp,
            'bot_stats': bot_stats
        }
    
    def _fetch_bot_promotion_context(self, bot_id):
        """Fetch all decisions related to this bot"""
        cursor = self.db_conn.cursor()
        
        cursor.execute("""
            SELECT * FROM decisions
            WHERE related_bot_id = ?
            ORDER BY timestamp DESC
        """, [bot_id])
        
        decisions = [dict(row) for row in cursor.fetchall()]
        for dec in decisions:
            dec['context_snapshot'] = json.loads(dec['context_snapshot'] or '{}')
        
        return decisions
    
    # =====================================================
    # ROCKY'S CONVERSATIONAL OUTPUTS
    # =====================================================
    
    def should_i_promote_this_bot(self, bot_id):
        """
        User asks: "Should I promote this bot?"
        
        Returns:
            (recommendation: str, reasoning: str, confidence: str)
        """
        origin = self._fetch_bot_origin(bot_id)
        if not origin:
            return None, "Bot not found in memory", "uncertain"
        
        bot = origin['bot']
        hypothesis = origin['hypothesis']
        mutation = origin['mutation']
        
        # Fetch context
        metrics = json.loads(bot['latest_metrics_json'] or '{}')
        hyp_status = self._fetch_hypothesis_status(hypothesis['hypothesis_id'])
        history = self._fetch_hypothesis_history(hypothesis['hypothesis_id'])
        
        # Build reasoning
        reasoning_points = []
        recommendation = "yes"
        confidence = "high"
        
        # Check 1: Sample size
        trades = metrics.get('trades', 0)
        if trades < 30:
            reasoning_points.append(f"Small sample: only {trades} trades. Need at least 30-50 for confidence.")
            confidence = "low"
        else:
            reasoning_points.append(f"Decent sample: {trades} trades.")
        
        # Check 2: Trajectory
        trajectory = metrics.get('trajectory')
        if trajectory == 'degrading':
            reasoning_points.append("Trajectory is degrading—not ready yet.")
            recommendation = "wait"
            confidence = "medium"
        elif trajectory == 'improving':
            reasoning_points.append("Trajectory improving—good sign.")
        
        # Check 3: Survival
        survival = metrics.get('survival', 0)
        if survival < 0.80:
            reasoning_points.append(f"Survival {survival:.0%} is weak. Expect drawdowns.")
            recommendation = "wait"
        else:
            reasoning_points.append(f"Survival {survival:.0%} is solid.")
        
        # Check 4: Hypothesis strength
        bot_stats = hyp_status['bot_stats']
        if bot_stats['failed'] and bot_stats['failed'] > bot_stats['promoted']:
            reasoning_points.append(f"This hypothesis has had {bot_stats['failed']} failures vs {bot_stats['promoted']} successes. Weak hypothesis.")
            recommendation = "reject"
            confidence = "high"
        elif bot_stats['promoted'] > 0:
            reasoning_points.append(f"This hypothesis has worked before ({bot_stats['promoted']} promotions). Good sign.")
        
        # Check 4b: Mutation history
        if history['total'] > 0:
            helped = len(history['helped'])
            if helped > 0:
                reasoning_points.append(f"Mutations on this hypothesis have worked ({helped} successful). This bot is refinement of something proven.")
        
        # Check 5: Is current problem repeated?
        if mutation:
            diagnosis = mutation['diagnosis']
            prior_attempts = self._fetch_prior_attempts(hypothesis['hypothesis_id'], diagnosis)
            if len(prior_attempts) > 1:
                helped_count = sum(1 for m in prior_attempts if m['result'] == 'helped')
                if helped_count == 0:
                    reasoning_points.append(f"You've tried fixing '{diagnosis}' {len(prior_attempts)} times. Never worked. Different approach needed.")
                    recommendation = "reject"
                elif helped_count >= 1:
                    reasoning_points.append(f"You fixed '{diagnosis}' before. This mutation follows that pattern—reasonable.")
        
        # Construct natural response
        reasoning = " ".join(reasoning_points)
        
        return recommendation, reasoning, confidence
    
    def why_is_this_failing(self, bot_id):
        """
        User asks: "Why is this bot failing?"
        
        Returns:
            (diagnosis: str, reference: str)
        """
        origin = self._fetch_bot_origin(bot_id)
        if not origin:
            return None, "Bot not found"
        
        bot = origin['bot']
        hypothesis = origin['hypothesis']
        metrics = json.loads(bot['latest_metrics_json'] or '{}')
        
        # Identify likely problem
        flip_rate = metrics.get('flip_rate', 0)
        divergence = metrics.get('divergence', 0)
        survival = metrics.get('survival', 1.0)
        
        diagnosis = None
        reference = None
        
        if flip_rate > 0.15:
            diagnosis = "high flip rate (overtrading)"
            prior = self._fetch_prior_attempts(hypothesis['hypothesis_id'], "flip rate")
            if prior:
                helped = sum(1 for m in prior if m['result'] == 'helped')
                if helped > 0:
                    reference = f"You've fixed this before. {helped} mutation(s) that worked: tighten selectivity or entry threshold."
                else:
                    reference = f"You've tried fixing this {len(prior)} times without success. Might not be a parameter problem—could be hypothesis issue."
        
        elif divergence > 0.10:
            diagnosis = "high divergence (model drift)"
            reference = "Model isn't behaving as expected. Hypothesis regime assumption may have shifted."
        
        elif survival < 0.80:
            diagnosis = "weak survival (drawdown hits hard)"
            reference = "Risk management is tight or hypothesis is fragile. Consider smaller sizing or tighter stops."
        
        else:
            diagnosis = "unclear from metrics"
            reference = "Check logs. Might be execution issue or regime change."
        
        return diagnosis, reference
    
    def what_should_i_try_next(self, bot_id):
        """
        User asks: "What should I try next?"
        
        Returns:
            (suggestion: str, reasoning: str)
        """
        origin = self._fetch_bot_origin(bot_id)
        if not origin:
            return None, "Bot not found"
        
        hypothesis = origin['hypothesis']
        bot = origin['bot']
        metrics = json.loads(bot['latest_metrics_json'] or '{}')
        
        # Fetch history
        history = self._fetch_hypothesis_history(hypothesis['hypothesis_id'])
        
        # Identify what's been tried
        mutation_types_tried = {}
        for result_type in ['helped', 'hurt', 'inconclusive']:
            for mut in history[result_type]:
                mt = mut['mutation_type']
                if mt not in mutation_types_tried:
                    mutation_types_tried[mt] = {'helped': 0, 'hurt': 0}
                
                if result_type == 'helped':
                    mutation_types_tried[mt]['helped'] += 1
                else:
                    mutation_types_tried[mt]['hurt'] += 1
        
        # Identify problem
        flip_rate = metrics.get('flip_rate', 0)
        divergence = metrics.get('divergence', 0)
        
        suggestion = None
        reasoning = None
        
        if flip_rate > 0.15:
            # High flip rate problem
            selectivity_history = mutation_types_tried.get('selectivity', {})
            
            if selectivity_history['helped'] > 0:
                # Tightening selectivity worked before
                suggestion = "Tighten selectivity further. You've done this before with success."
                reasoning = f"Selectivity mutations helped {selectivity_history['helped']} time(s) before. Incremental improvement strategy."
            
            elif selectivity_history['hurt'] > 0:
                # Tightening hurt, try entry instead
                suggestion = "Try tightening entry threshold instead. Different angle on the same problem."
                reasoning = f"Selectivity backfired {selectivity_history['hurt']} time(s). Entry threshold is different lever—might work."
            
            else:
                # First time trying
                suggestion = "Start with selectivity tightening. Reduces false entries."
                reasoning = "Haven't tried this on this hypothesis yet. Highest-probability fix for flip rate."
        
        elif divergence > 0.10:
            suggestion = "Kill this bot and spawn from hypothesis again. Divergence suggests model misalignment."
            reasoning = "Not a parameter problem—fundamental hypothesis issue. Mutation won't help."
        
        else:
            # No clear problem identified
            suggestion = "Run it longer. Need more data to diagnose."
            reasoning = f"Metrics look OK (flip rate {flip_rate:.0%}, divergence {divergence:.2f}). Let it establish pattern."
        
        return suggestion, reasoning
    
    def challenge_promotion_decision(self, bot_id, user_reason):
        """
        Rocky pushes back if promotion looks risky.
        
        Returns:
            (challenge: str or None, severity: str)
            None if promotion seems reasonable
        """
        origin = self._fetch_bot_origin(bot_id)
        if not origin:
            return None, "unknown"
        
        hypothesis = origin['hypothesis']
        bot = origin['bot']
        metrics = json.loads(bot['latest_metrics_json'] or '{}')
        hyp_status = self._fetch_hypothesis_status(hypothesis['hypothesis_id'])
        history = self._fetch_hypothesis_history(hypothesis['hypothesis_id'])
        
        # Check for red flags
        
        # Red flag 1: Repeated failures on this hypothesis
        bot_stats = hyp_status['bot_stats']
        if bot_stats['failed'] and bot_stats['failed'] >= 3:
            return (
                f"This hypothesis has failed {bot_stats['failed']} times. "
                f"Promoting again is throwing good capital after bad. Retire and try something else.",
                "high"
            )
        
        # Red flag 2: Low sample size
        trades = metrics.get('trades', 0)
        if trades < 20:
            return (
                f"Only {trades} trades. Too small to trust. Run it another week.",
                "medium"
            )
        
        # Red flag 3: Weak survival
        survival = metrics.get('survival', 1.0)
        if survival < 0.75:
            return (
                f"Survival is {survival:.0%}. Expect 25% drawdown. That's brutal.",
                "high"
            )
        
        # Red flag 4: Degrading trajectory
        trajectory = metrics.get('trajectory')
        if trajectory == 'degrading':
            return (
                "Trajectory is degrading. It's getting worse, not better. Wait.",
                "medium"
            )
        
        # Red flag 5: Contradictory signals
        flip_rate = metrics.get('flip_rate', 0)
        pnl = metrics.get('shadow_pnl', 0)
        if flip_rate > 0.20 and pnl > 0.02:
            return (
                f"Flip rate is {flip_rate:.0%} but PnL is +{pnl*100:.1f}%. "
                f"Suspicious—you're getting lucky, not finding edge.",
                "medium"
            )
        
        # No red flags
        return None, "ok"
    
    def generate_proposal_note(self, bot_id, mutation_type, rationale):
        """
        Generate a PROPOSAL for user consideration.
        Grounded in history, not generic.
        
        Returns:
            (proposal_text: str, confidence: str)
        """
        origin = self._fetch_bot_origin(bot_id)
        if not origin:
            return None, "unknown"
        
        hypothesis = origin['hypothesis']
        history = self._fetch_hypothesis_history(hypothesis['hypothesis_id'])
        
        # Check if this mutation type has been tried
        tried_mutations = {
            'helped': [],
            'hurt': [],
        }
        
        for result in ['helped', 'hurt']:
            for mut in history[result]:
                if mut['mutation_type'] == mutation_type:
                    tried_mutations[result].append(mut)
        
        # Build proposal text
        lines = [
            f"**Mutation Proposal: {mutation_type.upper()}**",
            f"",
            f"Rationale: {rationale}",
        ]
        
        # Add history context
        if tried_mutations['helped']:
            count = len(tried_mutations['helped'])
            lines.append(f"")
            lines.append(f"✓ This mutation type has worked before ({count} success). Probability higher.")
        
        if tried_mutations['hurt']:
            count = len(tried_mutations['hurt'])
            lines.append(f"")
            lines.append(f"⚠ This mutation has also backfired ({count} times). Be cautious.")
        
        if not tried_mutations['helped'] and not tried_mutations['hurt']:
            lines.append(f"")
            lines.append(f"• First time trying {mutation_type} on this hypothesis. Unproven.")
        
        # Confidence
        if tried_mutations['helped'] and not tried_mutations['hurt']:
            confidence = "high"
        elif tried_mutations['hurt'] and not tried_mutations['helped']:
            confidence = "low"
        else:
            confidence = "medium"
        
        proposal_text = "\n".join(lines)
        return proposal_text, confidence


# =====================================================
# HELPER: Quick reasoning without full context
# =====================================================

def rocky_quick_thought(query, bot_id=None):
    """
    Quick conversational thought from Rocky.
    Falls back to light reasoning if bot_id missing.
    
    Args:
        query: User's question or statement
        bot_id: Bot ID if applicable
    
    Returns:
        str (Rocky's response)
    """
    if not bot_id:
        # Light reasoning, no database
        if 'promote' in query.lower():
            return "Need more context. Which bot? What's its track record on this hypothesis?"
        elif 'fail' in query.lower():
            return "Could be parameter problem or regime shift. Run evaluation to check metrics."
        else:
            return "What specifically do you want to test? Hypothesis first, then bot."
    
    # Use memory
    rocky = RockyReasoning()
    rocky.connect()
    
    try:
        if 'promote' in query.lower():
            rec, reasoning, conf = rocky.should_i_promote_this_bot(bot_id)
            return f"{rec.upper()}: {reasoning} (confidence: {conf})"
        
        elif 'fail' in query.lower() or 'wrong' in query.lower():
            diagnosis, reference = rocky.why_is_this_failing(bot_id)
            return f"Likely issue: {diagnosis}. {reference}"
        
        elif 'next' in query.lower() or 'try' in query.lower():
            suggestion, reasoning = rocky.what_should_i_try_next(bot_id)
            return f"{suggestion} — {reasoning}"
        
        else:
            return "Ask me about promoting, failing, or what to try next."
    
    finally:
        rocky.close()


# =====================================================
# CLARIFYING QUESTIONS (Phase 2.6 Enhancement)
# =====================================================

def rocky_clarify_scope(query):
    """
    Ask clarifying questions when user query is ambiguous.
    Returns suggested options for user to choose from.
    
    Args:
        query: User's question
    
    Returns:
        (needs_clarification: bool, options: list)
    """
    query_lower = query.lower()
    
    # Detect ambiguous queries
    if 'delta' in query_lower or 'difference' in query_lower or 'paper' in query_lower:
        return True, [
            "1. The overall Arena (baseline vs current state)",
            "2. Your current baby swarm (which babies)",
            "3. A specific baby (compare to others)"
        ]
    
    elif 'flip' in query_lower or 'sign flip' in query_lower:
        return True, [
            "1. Arena-wide flip rates",
            "2. Specific baby flip rate", 
            "3. Comparison between babies"
        ]
    
    elif 'promote' in query_lower or 'kill' in query_lower:
        return True, [
            "1. A specific baby you have in mind",
            "2. The best performer right now",
            "3. The worst performer"
        ]
    
    elif 'performance' in query_lower or 'how' in query_lower:
        return True, [
            "1. Overall swarm performance",
            "2. Best vs worst baby",
            "3. A specific baby"
        ]
    
    return False, []
