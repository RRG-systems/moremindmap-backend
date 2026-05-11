#!/usr/bin/env python3
"""
Agent Observation Layer — Phase 4.0
Agents post observations about simulation outcomes

Triggers:
- Trade completion (paper vs shadow divergence)
- Significant drawdown or win streak
- Baby promotion/elimination
- Mutation hypothesis spawn

Posts go directly to MOLT feed as agent_note or agent_proposal.
"""

import json
import random
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime

from molt_persistence import MOLTPersistence


class AgentObservationLayer:
    """Agents observe simulation outcomes and post to MOLT feed"""
    
    def __init__(self):
        self.molt = MOLTPersistence()
        self.molt.connect()
        self.last_observation_state = {
            'last_trade_count': 0,
            'last_paper_pnl': 0.0,
            'last_shadow_pnl': 0.0,
            'last_max_drawdown': 0.0,
            'streak_wins': 0,
            'streak_losses': 0,
        }
    
    def close(self):
        """Close database connection"""
        self.molt.close()
    
    def observe_trade_execution(
        self,
        trade_data: Dict,
        all_trades: List[Dict],
        paper_pnl: float,
        shadow_pnl: float
    ) -> Optional[str]:
        """
        Observe a completed trade and post if noteworthy
        
        Args:
            trade_data: {'asset', 'side', 'entry_price', 'exit_price', 'pnl', 'source'}
            all_trades: recent trades for streak analysis
            paper_pnl: cumulative paper PnL
            shadow_pnl: cumulative shadow PnL
        
        Returns:
            molt_id if post created, None otherwise
        """
        source = trade_data.get('source', 'unknown')
        pnl = float(trade_data.get('pnl', 0))
        asset = trade_data.get('asset', 'UNKNOWN')
        
        # Track streaks
        if pnl > 0:
            self.last_observation_state['streak_wins'] += 1
            self.last_observation_state['streak_losses'] = 0
        else:
            self.last_observation_state['streak_losses'] += 1
            self.last_observation_state['streak_wins'] = 0
        
        # Post on significant outcomes
        wins = self.last_observation_state['streak_wins']
        losses = self.last_observation_state['streak_losses']
        
        # Win streak detected
        if wins == 3:  # First 3-win streak
            agent = random.choice(['Overfitter', 'Explorer'])
            content = self._compose_win_streak_post(asset, wins, paper_pnl, shadow_pnl)
            molt_id = self.molt.log_agent_note(
                agent,
                content,
                topic='performance'
            )
            print(f"[MOLT] {agent} posted: {wins}-trade win streak detected")
            return molt_id
        
        # Loss streak detected
        if losses == 3:
            agent = 'Risk Manager'
            content = self._compose_loss_streak_post(asset, losses, paper_pnl, shadow_pnl)
            molt_id = self.molt.log_agent_note(
                agent,
                content,
                topic='risk'
            )
            print(f"[MOLT] {agent} posted: {losses}-trade loss streak detected")
            return molt_id
        
        # Paper vs shadow divergence
        divergence_pct = ((paper_pnl - shadow_pnl) / abs(shadow_pnl) * 100) if shadow_pnl != 0 else 0
        
        if abs(divergence_pct) > 20:  # >20% divergence is notable
            agent = 'Explorer'
            content = self._compose_divergence_post(divergence_pct, paper_pnl, shadow_pnl, asset)
            molt_id = self.molt.log_agent_note(
                agent,
                content,
                topic='execution'
            )
            print(f"[MOLT] {agent} posted: paper/shadow divergence detected ({divergence_pct:.1f}%)")
            return molt_id
        
        return None
    
    def observe_drawdown(self, current_drawdown: float, max_drawdown: float) -> Optional[str]:
        """
        Observe drawdown event
        
        Args:
            current_drawdown: current drawdown %
            max_drawdown: historical max drawdown %
        
        Returns:
            molt_id if post created
        """
        last_dd = self.last_observation_state['last_max_drawdown']
        
        # New max drawdown
        if max_drawdown > last_dd and max_drawdown > 5:
            self.last_observation_state['last_max_drawdown'] = max_drawdown
            
            agent = 'Risk Manager'
            content = f"""[Agent Risk Manager]

**Drawdown Alert:** New max drawdown reached.

Max: {max_drawdown:.1f}%
Current: {current_drawdown:.1f}%

This exceeds survival threshold. Recommend reducing size or tightening stops."""
            
            molt_id = self.molt.log_agent_note(
                agent,
                content,
                topic='risk'
            )
            print(f"[MOLT] Risk Manager posted: max drawdown {max_drawdown:.1f}%")
            return molt_id
        
        return None
    
    def observe_mutation_spawn(
        self,
        mutation_hypothesis: Dict,
        spawned_bot_ids: List[str]
    ) -> Optional[str]:
        """
        Observe mutation hypothesis spawn
        
        Args:
            mutation_hypothesis: {'hypothesis_id', 'description', 'mutation_type', ...}
            spawned_bot_ids: [canonical_id, variant_1, ..., variant_10]
        
        Returns:
            molt_id of proposal post
        """
        agent = self._select_agent_for_mutation(mutation_hypothesis)
        
        content = self._compose_mutation_proposal_post(
            mutation_hypothesis,
            len(spawned_bot_ids)
        )
        
        hypothesis_id = mutation_hypothesis.get('hypothesis_id', 'unknown')
        
        molt_id = self.molt.log_agent_proposal(
            agent,
            content,
            hypothesis_id,
            spawned_bot_ids,
            topic=mutation_hypothesis.get('description', 'mutation')
        )
        
        print(f"[MOLT] {agent} posted proposal: {hypothesis_id}")
        return molt_id
    
    def observe_baby_promotion(
        self,
        winner_bot_id: str,
        winner_metrics: Dict,
        losers_count: int
    ) -> Optional[str]:
        """
        Observe baby variant winning
        
        Args:
            winner_bot_id: promoted bot ID
            winner_metrics: {'fitness', 'trades', 'pnl', ...}
            losers_count: how many siblings lost
        
        Returns:
            molt_id if post created
        """
        agent = 'Overfitter'
        
        fitness = winner_metrics.get('fitness', 0)
        trades = winner_metrics.get('trades', 0)
        pnl = winner_metrics.get('pnl', 0)
        
        content = f"""[Agent Overfitter]

**Promotion Alert!** Baby variant wins.

Bot: {winner_bot_id}
Fitness: {fitness:.2f}
Trades: {trades}
PnL: ${pnl:.2f}

Defeated {losers_count} siblings. This approach is working."""
        
        molt_id = self.molt.log_agent_note(
            agent,
            content,
            topic='promotion'
        )
        
        print(f"[MOLT] Overfitter posted: {winner_bot_id} promoted")
        return molt_id
    
    def observe_baby_elimination(
        self,
        loser_bot_id: str,
        loser_metrics: Dict,
        reason: str
    ) -> Optional[str]:
        """
        Observe baby variant eliminated
        
        Args:
            loser_bot_id: eliminated bot ID
            loser_metrics: {'fitness', 'trades', 'drawdown', ...}
            reason: 'low_fitness' | 'max_drawdown' | 'survival_failure'
        
        Returns:
            molt_id if post created
        """
        if reason == 'survival_failure':
            agent = 'Risk Manager'
            content = f"""[Agent Risk Manager]

**Elimination:** Variant failed survival.

Bot: {loser_bot_id}
Reason: Exceeded risk threshold
Max Drawdown: {loser_metrics.get('max_drawdown', 0):.1f}%

This is why we test. Mutation was too aggressive."""
        
        elif reason == 'low_fitness':
            agent = 'Explorer'
            content = f"""[Agent Explorer]

**Dead End:** Variant didn't scale.

Bot: {loser_bot_id}
Fitness: {loser_metrics.get('fitness', 0):.2f}
Trades: {loser_metrics.get('trades', 0)}

Hypothesis was interesting but not robust. Back to drawing board."""
        
        else:
            return None
        
        molt_id = self.molt.log_agent_note(
            agent,
            content,
            topic='elimination'
        )
        
        print(f"[MOLT] {agent} posted: {loser_bot_id} eliminated ({reason})")
        return molt_id
    
    # =========== COMPOSITION HELPERS ===========
    
    def _compose_win_streak_post(self, asset: str, streak: int, paper: float, shadow: float) -> str:
        """Compose win streak observation"""
        templates = [
            f"[Agent Overfitter]\n\n**STREAK!** {streak} wins on {asset}.\n\nPaper: ${paper:.2f} | Shadow: ${shadow:.2f}\n\nMomentum real. Scaling this.",
            f"[Agent Overfitter]\n\n{streak}-trade wins. This signal is WORKING on {asset}.\n\nKeep pushing.",
        ]
        return random.choice(templates)
    
    def _compose_loss_streak_post(self, asset: str, streak: int, paper: float, shadow: float) -> str:
        """Compose loss streak observation"""
        templates = [
            f"[Agent Risk Manager]\n\n**ALERT:** {streak}-trade losses on {asset}.\n\nPaper: ${paper:.2f} | Shadow: ${shadow:.2f}\n\nReverse course. Stop, review, then resume.",
            f"[Agent Risk Manager]\n\n{streak} losses. This isn't working.\n\nReduce size. {asset} is choppy.",
        ]
        return random.choice(templates)
    
    def _compose_divergence_post(self, divergence: float, paper: float, shadow: float, asset: str) -> str:
        """Compose paper/shadow divergence observation"""
        direction = "Paper ahead" if divergence > 0 else "Shadow ahead"
        templates = [
            f"[Agent Explorer]\n\n**Divergence:** Paper and shadow split {abs(divergence):.1f}% on {asset}.\n\n{direction}.\n\nExecution cost building up?",
            f"[Agent Explorer]\n\n{abs(divergence):.1f}% gap between paper and shadow. Slippage or signal decay?",
        ]
        return random.choice(templates)
    
    def _select_agent_for_mutation(self, hypothesis: Dict) -> str:
        """Select agent to post mutation hypothesis"""
        mutation_type = hypothesis.get('mutation_type', 'unknown')
        
        if 'aggressive' in mutation_type.lower():
            return 'Overfitter'
        elif 'risk' in mutation_type.lower() or 'conservative' in mutation_type.lower():
            return 'Risk Manager'
        else:
            return 'Explorer'
    
    def _compose_mutation_proposal_post(self, hypothesis: Dict, spawn_count: int) -> str:
        """Compose mutation hypothesis proposal"""
        hypothesis_id = hypothesis.get('hypothesis_id', 'unknown')
        description = hypothesis.get('description', 'new variant')
        mutation_type = hypothesis.get('mutation_type', 'unknown')
        
        agent = self._select_agent_for_mutation(hypothesis)
        
        templates = {
            'Overfitter': f"""[Agent Overfitter]

**Hypothesis:** {description}

Type: {mutation_type}
Variants: {spawn_count}

This could work. Spawning nursery.""",
            
            'Risk Manager': f"""[Agent Risk Manager]

**Hypothesis:** {description}

Type: {mutation_type}
Variants: {spawn_count}

Conservative approach. Testing with {spawn_count} variants.""",
            
            'Explorer': f"""[Agent Explorer]

**Hypothesis:** {description}

Type: {mutation_type}
Variants: {spawn_count}

Interesting angle. Let's test.""",
        }
        
        return templates.get(agent, f"[Agent ?]\n\nTesting: {description}")


if __name__ == '__main__':
    # Test observation layer
    obs = AgentObservationLayer()
    
    # Simulate trade
    trade = {'asset': 'BTC', 'side': 'long', 'pnl': 0.0050, 'source': 'paper'}
    obs.observe_trade_execution(trade, [], 100.0, 95.0)
    
    obs.close()
