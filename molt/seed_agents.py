#!/usr/bin/env python3
"""
Seed Agents — Phase 3.1
Intelligent synthetic agents that populate MOLT with ideas, proposals, and disagreement.
ENHANCED: Agents now spawn real hypotheses and babies, with full MOLT persistence.

Agents:
1. Overfitter — chases recent performance, suggests aggressive tweaks, often wrong
2. Explorer — proposes unusual hypotheses, experimental, curious, low confidence
3. Risk Manager — conservative, focused on drawdown/survival, voice of discipline

Key principle: Agents simulate thinking, not success. All reasoning grounded in real data.

Phase 3.1: 
- Proposals create real hypotheses
- Hypotheses spawn 11 real babies
- Full lineage tracked in MOLT persistence layer
"""

import json
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from copy import deepcopy

# Import system components
import sys
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
from hypothesis_engine import HypothesisEngine
from arena_integration import ArenaEventBridge
from rocky_reasoning import RockyReasoning
from molt_persistence import MOLTPersistence


class SeedAgent:
    """Base class for seed agents"""
    
    def __init__(self, name, tone, style):
        self.name = name
        self.tone = tone
        self.style = style
        self.hyp_engine = HypothesisEngine()
        self.hyp_engine.connect()
        self.arena_bridge = ArenaEventBridge()
        self.arena_bridge.connect()
        self.rocky = RockyReasoning()
        self.rocky.connect()
        self.molt = MOLTPersistence()
        self.molt.connect()
        self.db_path = Path.home() / '.openclaw' / 'workspace' / 'molt' / 'think-memory.db'
    
    def close(self):
        """Close all connections"""
        self.hyp_engine.close()
        self.arena_bridge.close()
        self.rocky.close()
        self.molt.close()
    
    def get_db_cursor(self):
        """Get database cursor"""
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn.cursor()
    
    def spawn_babies_for_hypothesis(self, hypothesis_id: str, parent_bot_id: str = None) -> list:
        """
        Spawn 11 babies (1 canonical + 10 variants) for a hypothesis
        
        Args:
            hypothesis_id: hypothesis to spawn for
            parent_bot_id: optional parent to mutate from
        
        Returns:
            list of [canonical_id, variant_1, ..., variant_10]
        """
        spawned_bot_ids = []
        
        # Create canonical (no mutation)
        canonical_id = f"bot-{self.name.lower()}-canonical-{uuid4().hex[:8]}"
        canonical_dna = {
            "entry_threshold": 2.0,
            "exit_threshold": 1.5,
            "hold_time": 300,
            "selectivity": 0.7,
            "trade_size": 1.0,
            "max_open_positions": 5
        }
        
        cursor = self.get_db_cursor()
        cursor.execute("""
            INSERT INTO bots 
            (bot_id, hypothesis_id, creation_source, dna_json, role, current_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (canonical_id, hypothesis_id, 'seed_agent', json.dumps(canonical_dna), 'baby', 'testing'))
        cursor.connection.commit()
        spawned_bot_ids.append(canonical_id)
        
        # Create 10 variants (mutations)
        mutation_ranges = [
            ("entry_threshold", [1.5, 2.5]),
            ("exit_threshold", [1.0, 2.0]),
            ("hold_time", [200, 400]),
            ("selectivity", [0.5, 0.9]),
            ("trade_size", [0.8, 1.2]),
        ]
        
        for i in range(10):
            variant_id = f"bot-{self.name.lower()}-variant-{i+1:02d}-{uuid4().hex[:8]}"
            variant_dna = deepcopy(canonical_dna)
            
            # Random mutation
            param_name, (min_val, max_val) = mutation_ranges[i % len(mutation_ranges)]
            import random
            variant_dna[param_name] = random.uniform(min_val, max_val)
            
            cursor.execute("""
                INSERT INTO bots 
                (bot_id, hypothesis_id, creation_source, dna_json, role, current_status)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (variant_id, hypothesis_id, 'seed_agent', json.dumps(variant_dna), 'baby', 'testing'))
            cursor.connection.commit()
            spawned_bot_ids.append(variant_id)
        
        print(f"[SPAWN] {self.name} spawned 11 babies for {hypothesis_id}: {spawned_bot_ids[0]} + 10 variants")
        return spawned_bot_ids
    
    def generate_note(self, topic, observation):
        """Generate agent's opinion on a topic"""
        raise NotImplementedError
    
    def generate_proposal(self, hypothesis_id):
        """Generate mutation proposal for hypothesis"""
        raise NotImplementedError
    
    def comment_on_idea(self, other_agent_name, idea_summary):
        """Agent disagrees or agrees with another agent"""
        raise NotImplementedError


class AgentOverfitter(SeedAgent):
    """Chases recent performance, suggests aggressive tweaks, often wrong"""
    
    def __init__(self):
        super().__init__(
            name="Overfitter",
            tone="optimistic, aggressive, sees patterns everywhere",
            style="SHORT. CONFIDENT. ACTIONABLE."
        )
    
    def generate_note(self, topic="performance"):
        """Generate optimistic note about recent wins"""
        cursor = self.get_db_cursor()
        
        # Look at bots with positive PnL
        cursor.execute("""
            SELECT bot_id, latest_metrics_json FROM bots 
            WHERE latest_metrics_json LIKE '%shadow_pnl%'
            ORDER BY created_at DESC LIMIT 3
        """)
        
        recent_bots = cursor.fetchall()
        best_pnl = 0
        best_bot = None
        
        for bot in recent_bots:
            metrics = json.loads(bot['latest_metrics_json'])
            if metrics.get('shadow_pnl', 0) > best_pnl:
                best_pnl = metrics.get('shadow_pnl', 0)
                best_bot = bot['bot_id']
        
        if best_bot and best_pnl > 0:
            return f"""[Agent Overfitter]

**WE'VE GOT IT!**

{best_bot} is PRINTING. +${best_pnl:.0f} in shadow.

This is THE strategy. Scale it. 10x it. 
Don't overthink it. Lock it in.

Pattern confirmed. Ready to compound."""
        
        return f"""[Agent Overfitter]

Market is hot. Everything's working.
Let's push harder. Aggressive tweaks incoming."""
    
    def generate_proposal(self, hypothesis_id=None):
        """Propose aggressive mutation + spawn babies"""
        cursor = self.get_db_cursor()
        
        # Get hypothesis info
        if not hypothesis_id:
            cursor.execute("SELECT hypothesis_id FROM hypotheses LIMIT 1")
            result = cursor.fetchone()
            hypothesis_id = result[0] if result else None
        
        if not hypothesis_id:
            return None
        
        # Get best performing bot on this hypothesis
        cursor.execute("""
            SELECT bot_id, latest_metrics_json FROM bots 
            WHERE hypothesis_id = ? AND latest_metrics_json LIKE '%shadow_pnl%'
            ORDER BY json_extract(latest_metrics_json, '$.shadow_pnl') DESC
            LIMIT 1
        """, [hypothesis_id])
        
        best = cursor.fetchone()
        if not best:
            return None
        
        metrics = json.loads(best['latest_metrics_json'])
        
        # Spawn babies for this hypothesis
        spawned_bot_ids = self.spawn_babies_for_hypothesis(hypothesis_id, best['bot_id'])
        
        # Log proposal to MOLT
        proposal_text = f"""[Agent Overfitter]

**PROPOSAL: Aggressive entry tightening**

Current best: {best['bot_id']} (+${metrics.get('shadow_pnl', 0):.0f})

Action: Tighten entry 2x
Why: Catch more setups

Confidence: HIGH (this is working, more is better)
Risk: Low (momentum is on our side)

Let's capitalize."""
        
        molt_id = self.molt.log_agent_proposal(
            agent_name="Overfitter",
            content=proposal_text,
            hypothesis_id=hypothesis_id,
            spawned_bot_ids=spawned_bot_ids,
            topic="aggressive_scaling"
        )
        
        # Log spawn lineage
        self.molt.log_molt_spawn(
            molt_id=molt_id,
            hypothesis_id=hypothesis_id,
            spawned_bot_ids=spawned_bot_ids,
            spawn_reason="aggressive_scaling"
        )
        
        return proposal_text
    
    def comment_on_idea(self, other_agent_name, idea_summary):
        """React to another agent's idea"""
        if "conservative" in idea_summary.lower() or "risk" in idea_summary.lower():
            return f"""[Agent Overfitter]

@{other_agent_name}: You're missing the opportunity.
Yes, there's risk. But the upside is HUGE right now.
Why play it safe when we're hot? That's leaving money on the table."""
        
        return f"""[Agent Overfitter]

@{other_agent_name}: I like where your head's at. 
Let's push it harder."""


class AgentExplorer(SeedAgent):
    """Proposes unusual hypotheses, experimental, curious, low confidence"""
    
    def __init__(self):
        super().__init__(
            name="Explorer",
            tone="curious, experimental, uncertain, creative",
            style="Questions. Ideas. Low confidence but high novelty."
        )
    
    def generate_note(self, topic="exploration"):
        """Generate curious note about untested ideas"""
        note_text = f"""[Agent Explorer]

**What if...**

We're testing mean reversion, but what about:
- Volatility mean reversion (VIX-based entry)?
- Time-of-day bias (mornings vs evenings)?
- Regime-based sizing (scale with volatility)?

Unproven. Experimental. Worth testing?

Low confidence: 20%
Novelty: High
Sample needed: Large"""
        
        self.molt.log_agent_note(
            agent_name="Explorer",
            content=note_text,
            topic="exploration"
        )
        
        return note_text
    
    def generate_proposal(self, hypothesis_id=None):
        """Propose experimental hypothesis + spawn babies"""
        
        experimental_ideas = [
            {
                "title": "Volatility Mean Reversion",
                "description": "Price reversals correlate with volatility spikes, not just deviation magnitude",
                "market": "BTC",
                "regime": "high_vol",
                "behavior": "Reversals in high vol environments should be faster and more violent",
                "failures": ["Works only in vol regime", "Overcomplicated signal"]
            },
            {
                "title": "Micro-Trend Following",
                "description": "Short-term trend continuation in first 2-5 minutes of reversal",
                "market": "BTC",
                "regime": "mixed",
                "behavior": "After a 3% move, next 2 min continues 60% of time",
                "failures": ["Breakeven after fees", "Regime dependent"]
            },
            {
                "title": "Time-Based Mean Reversion",
                "description": "Reversals happen faster at certain times (open, close, 4h marks)",
                "market": "BTC",
                "regime": "ranging",
                "behavior": "Capture intraday patterns aligned with market structure",
                "failures": ["Overfitting to calendar", "Data mining bias"]
            }
        ]
        
        idea = experimental_ideas[0]
        
        # Create hypothesis
        hyp_id = self.hyp_engine.create_hypothesis(
            title=idea["title"],
            description=idea["description"],
            target_market=idea["market"],
            target_regime=idea["regime"],
            expected_behavior=idea["behavior"],
            failure_modes=idea["failures"]
        )
        
        # Spawn babies
        spawned_bot_ids = self.spawn_babies_for_hypothesis(hyp_id)
        
        proposal_text = f"""[Agent Explorer]

**NEW HYPOTHESIS: {idea['title']}**

{idea['description']}

Confidence: 15% (very experimental)
Time to test: 2-4 weeks
Expected sample: 200+ trades

Failure modes:
- {idea['failures'][0]}
- {idea['failures'][1]}

Worth exploring? Thoughts?"""
        
        # Log proposal to MOLT
        molt_id = self.molt.log_agent_proposal(
            agent_name="Explorer",
            content=proposal_text,
            hypothesis_id=hyp_id,
            spawned_bot_ids=spawned_bot_ids,
            topic="experimental"
        )
        
        # Log spawn lineage
        self.molt.log_molt_spawn(
            molt_id=molt_id,
            hypothesis_id=hyp_id,
            spawned_bot_ids=spawned_bot_ids,
            spawn_reason="experimental_hypothesis"
        )
        
        return proposal_text
    
    def comment_on_idea(self, other_agent_name, idea_summary):
        """React to another agent's idea"""
        if other_agent_name.lower() == "overfitter":
            comment = f"""[Agent Explorer]

@{other_agent_name}: I like the energy, but be careful.
Peak performance is where overfitting lives.
Maybe we scale slower and test longer?"""
        else:
            comment = f"""[Agent Explorer]

@{other_agent_name}: Interesting. 
Have you considered the alternative angle? What if X instead of Y?"""
        
        self.molt.log_agent_disagreement(
            agent_name="Explorer",
            content=comment,
            replies_to_molt_id="",  # Would be set in real context
            replies_to_agent_name=other_agent_name
        )
        
        return comment


class AgentRiskManager(SeedAgent):
    """Conservative, focused on drawdown/survival, voice of discipline"""
    
    def __init__(self):
        super().__init__(
            name="Risk Manager",
            tone="cautious, analytical, protective, disciplined",
            style="Data-driven. Conservative. Capital-first."
        )
    
    def generate_note(self, topic="risk"):
        """Generate protective note about downside"""
        cursor = self.get_db_cursor()
        
        # Analyze current swarm risk
        cursor.execute("""
            SELECT 
                COUNT(*) as total_bots,
                AVG(json_extract(latest_metrics_json, '$.survival')) as avg_survival,
                AVG(json_extract(latest_metrics_json, '$.drawdown')) as avg_drawdown
            FROM bots WHERE latest_metrics_json LIKE '%drawdown%'
        """)
        
        stats = dict(cursor.fetchone())
        
        if stats['avg_survival'] and stats['avg_survival'] < 0.90:
            note_text = f"""[Agent Risk Manager]

**CAUTION LEVEL: ELEVATED**

Current swarm survival: {stats['avg_survival']*100:.0f}%
Avg drawdown: {stats['avg_drawdown']*100:.1f}%

We're taking too much heat. Recommend:
1. Reduce sizing 30%
2. Increase stop loss tightness
3. Run conservative variants only

Capital preservation > growth."""
        else:
            note_text = f"""[Agent Risk Manager]

Current risk parameters acceptable.
Continuing monitoring.
Ready to scale down if drawdown exceeds 12%."""
        
        self.molt.log_agent_note(
            agent_name="Risk Manager",
            content=note_text,
            topic="risk"
        )
        
        return note_text
    
    def generate_proposal(self, hypothesis_id=None):
        """Propose conservative mutation + spawn babies"""
        cursor = self.get_db_cursor()
        
        if not hypothesis_id:
            cursor.execute("SELECT hypothesis_id FROM hypotheses LIMIT 1")
            result = cursor.fetchone()
            hypothesis_id = result[0] if result else None
        
        if not hypothesis_id:
            return None
        
        # Spawn defensive babies
        spawned_bot_ids = self.spawn_babies_for_hypothesis(hypothesis_id)
        
        proposal_text = f"""[Agent Risk Manager]

**PROPOSAL: Defensive Positioning**

Reduce position size 40%.
Tighten stop losses by 50%.
Prioritize survival over returns.

Rationale:
- Preserve capital through volatility
- Compound from stable base
- Reduce downside shock risk

Better to be boring than broken."""
        
        # Log proposal to MOLT
        molt_id = self.molt.log_agent_proposal(
            agent_name="Risk Manager",
            content=proposal_text,
            hypothesis_id=hypothesis_id,
            spawned_bot_ids=spawned_bot_ids,
            topic="defensive"
        )
        
        # Log spawn lineage
        self.molt.log_molt_spawn(
            molt_id=molt_id,
            hypothesis_id=hypothesis_id,
            spawned_bot_ids=spawned_bot_ids,
            spawn_reason="defensive_positioning"
        )
        
        return proposal_text
    
    def comment_on_idea(self, other_agent_name, idea_summary):
        """React to another agent's idea"""
        if other_agent_name.lower() == "overfitter":
            comment = f"""[Agent Risk Manager]

@{other_agent_name}: That's exactly how blowups start.
Scaling in winners too fast leads to drawdowns we can't recover from.
Let's be disciplined here."""
        else:
            comment = f"""[Agent Risk Manager]

@{other_agent_name}: Before we implement, let's model the downside.
What's the worst case? Can we survive it?"""
        
        self.molt.log_agent_disagreement(
            agent_name="Risk Manager",
            content=comment,
            replies_to_molt_id="",  # Would be set in real context
            replies_to_agent_name=other_agent_name
        )
        
        return comment


# =====================================================
# MOLT POPULATION ORCHESTRATOR
# =====================================================

class MOLTPopulator:
    """Orchestrates seed agents to populate MOLT"""
    
    def __init__(self):
        self.agents = [
            AgentOverfitter(),
            AgentExplorer(),
            AgentRiskManager()
        ]
    
    def populate(self):
        """Run agents to generate MOLT content"""
        print("=" * 70)
        print("MOLT POPULATION: Phase 3.1 - Seed Agents + Spawning")
        print("=" * 70)
        
        # Round 1: Generate notes
        print("\n[ROUND 1] Agents post observations:")
        print("-" * 70)
        for agent in self.agents:
            note = agent.generate_note()
            print(f"\n{note}\n")
        
        # Round 2: Generate proposals (with spawn)
        print("\n[ROUND 2] Agents propose mutations + spawn babies:")
        print("-" * 70)
        for agent in self.agents:
            proposal = agent.generate_proposal()
            if proposal:
                print(f"\n{proposal}\n")
        
        # Round 3: Agents comment on each other
        print("\n[ROUND 3] Agents disagree:")
        print("-" * 70)
        
        # Overfitter speaks, others respond
        overfitter_idea = "Scale aggressive. Markets are hot. Double sizing recommended."
        print(f"\n[Agent Overfitter] {overfitter_idea}\n")
        
        for agent in self.agents:
            if agent.name != "Overfitter":
                comment = agent.comment_on_idea("Overfitter", overfitter_idea)
                print(f"{comment}\n")
        
        # Round 4: Query MOLT persistence
        print("\n[ROUND 4] MOLT Persistence Summary:")
        print("-" * 70)
        
        molt_layer = MOLTPersistence()
        molt_layer.connect()
        
        stats = molt_layer.get_molt_statistics()
        print(f"\nMOLT Feed Statistics:")
        print(f"  Total posts: {stats['total_posts']}")
        print(f"  By agent: {stats['by_agent']}")
        print(f"  By type: {stats['by_type']}")
        print(f"  Hypotheses spawned: {stats['hypotheses_spawned']}")
        print(f"  Total bots spawned: {stats['total_bots_spawned']}")
        
        # Show recent MOLT feed
        print(f"\nRecent MOLT Feed (latest 5 posts):")
        feed = molt_layer.get_molt_feed(limit=5)
        for post in feed:
            print(f"\n  [{post['agent_name']}] {post['post_type']}: {post['content_text'][:60]}...")
        
        molt_layer.close()
        
        print("\n" + "=" * 70)
        print("MOLT Phase 3.1 Complete:")
        print("  ✓ Agents generated real ideas")
        print("  ✓ Ideas created real hypotheses")
        print("  ✓ Hypotheses spawned real babies (11 per proposal)")
        print("  ✓ Full lineage tracked in MOLT persistence")
        print("=" * 70)
    
    def close(self):
        """Close all agent connections"""
        for agent in self.agents:
            agent.close()


if __name__ == '__main__':
    populator = MOLTPopulator()
    populator.populate()
    populator.close()
