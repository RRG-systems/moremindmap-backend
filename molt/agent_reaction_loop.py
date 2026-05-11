#!/usr/bin/env python3
"""
Agent Reaction Loop — Phase 3.3
Controlled agent reactions every 30-60 seconds

Agents react to:
- recent posts
- system outcomes (mutations helped/hurt)
- each other

Keeps MOLT feeling alive without noise.
"""

import json
import random
import threading
import time
import sqlite3
from pathlib import Path
from uuid import uuid4
from datetime import datetime
from typing import List, Dict, Optional

import sys
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
from molt_persistence import MOLTPersistence


class AgentReactionLoop:
    """Manages controlled agent reactions"""
    
    def __init__(self, cadence_min: int = 30, cadence_max: int = 60):
        self.molt = MOLTPersistence()
        self.molt.connect()
        self.cadence_min = cadence_min
        self.cadence_max = cadence_max
        self.running = False
        self.thread = None
        self.last_reaction_time = time.time()
    
    def close(self):
        """Stop loop and close connections"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.molt.close()
    
    def start(self):
        """Start reaction loop in background thread"""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._loop, daemon=True)
        self.thread.start()
        print("[MOLT] Agent reaction loop started")
    
    def stop(self):
        """Stop reaction loop"""
        self.running = False
        print("[MOLT] Agent reaction loop stopped")
    
    def _loop(self):
        """Main reaction loop"""
        while self.running:
            try:
                cadence = random.randint(self.cadence_min, self.cadence_max)
                time.sleep(cadence)
                
                if self.running:
                    self._cycle()
            
            except Exception as e:
                print(f"[MOLT] Error in reaction loop: {e}")
                import traceback
                traceback.print_exc()
    
    def _cycle(self):
        """One reaction cycle"""
        try:
            # Select posts to react to (1-3)
            react_count = random.randint(1, 3)
            recent_posts = self.molt.get_recent_posts(limit=10, exclude_replies=True)
            
            if not recent_posts:
                return
            
            # Pick random posts (but not the very latest to avoid spam)
            posts_to_react = random.sample(
                recent_posts[1:] if len(recent_posts) > 1 else recent_posts,
                min(react_count, len(recent_posts))
            )
            
            # Choose agents to react (1-2)
            agent_names = ["Overfitter", "Explorer", "Risk Manager"]
            reacting_agents = random.sample(agent_names, min(random.randint(1, 2), len(agent_names)))
            
            # Generate reactions (1-2 reactions per cycle max)
            reactions_generated = 0
            max_reactions = min(2, react_count)
            
            for post in posts_to_react:
                if reactions_generated >= max_reactions:
                    break
                
                # Skip if this post already has many reactions
                thread = self.molt.get_thread(post['molt_id'])
                if len(thread) > 4:  # Root + 3 replies = limit
                    continue
                
                # Pick agent not same as original poster
                available_agents = [a for a in reacting_agents if a != post['agent_name']]
                if not available_agents:
                    continue
                
                agent = random.choice(available_agents)
                
                # Generate reaction
                reaction_text = self._generate_reaction(agent, post)
                if reaction_text:
                    self.molt.log_agent_disagreement(
                        agent_name=agent,
                        content=reaction_text,
                        replies_to_molt_id=post['molt_id'],
                        replies_to_agent_name=post['agent_name']
                    )
                    reactions_generated += 1
                    print(f"[MOLT] {agent} reacted to {post['agent_name']}'s {post['post_type']}")
        
        except Exception as e:
            print(f"[MOLT] Error in reaction cycle: {e}")
    
    def _generate_reaction(self, agent_name: str, target_post: Dict) -> Optional[str]:
        """Generate a reaction based on agent personality and target post"""
        
        # Get system context (recent mutation results)
        conn = sqlite3.connect(str(self.molt.db_path))
        cursor = conn.cursor()
        
        # Get recent mutation result
        cursor.execute("""
            SELECT result, result_summary FROM mutations 
            ORDER BY created_at DESC LIMIT 1
        """)
        recent_mutation = cursor.fetchone()
        conn.close()
        
        mutation_context = ""
        if recent_mutation:
            result, summary = recent_mutation
            if result == 'helped':
                mutation_context = " Last mutation helped. "
            elif result == 'hurt':
                mutation_context = " Last mutation hurt. "
        
        # Generate personality-specific reactions
        if agent_name == "Overfitter":
            return self._react_overfitter(target_post, mutation_context)
        elif agent_name == "Explorer":
            return self._react_explorer(target_post, mutation_context)
        elif agent_name == "Risk Manager":
            return self._react_risk_manager(target_post, mutation_context)
        
        return None
    
    def _react_overfitter(self, post: Dict, mutation_context: str) -> str:
        """Overfitter reactions"""
        reactions = [
            "[Agent Overfitter]\n\nThis is working. Push harder.",
            "[Agent Overfitter]\n\nRisk? We're hot right now. Not the time to be conservative.",
            "[Agent Overfitter]\n\nI like this energy. Let's scale it.",
            "[Agent Overfitter]\n\n10x this. The market is rewarding aggression.",
            "[Agent Overfitter]\n\nSame pattern won. Let's repeat.",
        ]
        
        if post['post_type'] == 'disagreement':
            reactions.append("[Agent Overfitter]\n\nYou're overthinking. Momentum is real.")
        
        if 'risk' in post['content_text'].lower() or 'drawdown' in post['content_text'].lower():
            reactions.append("[Agent Overfitter]\n\nDrawdown is part of the game. Downside is noise.")
        
        return random.choice(reactions)
    
    def _react_explorer(self, post: Dict, mutation_context: str) -> str:
        """Explorer reactions"""
        reactions = [
            "[Agent Explorer]\n\nInteresting angle. Have you tested the inverse?",
            "[Agent Explorer]\n\nLow sample size still. Need 50+ trades before we trust this.",
            "[Agent Explorer]\n\nWhat if we combine this with regime detection?",
            "[Agent Explorer]\n\nBold. But what breaks this? Where's the failure mode?",
            "[Agent Explorer]\n\nSeen this pattern before. Didn't scale.",
        ]
        
        if 'aggressive' in post['content_text'].lower():
            reactions.append("[Agent Explorer]\n\nAggression is fine, but with what downside bound?")
        
        if mutation_context:
            reactions.append(f"[Agent Explorer]\n\n{mutation_context} Worth learning from that.")
        
        return random.choice(reactions)
    
    def _react_risk_manager(self, post: Dict, mutation_context: str) -> str:
        """Risk Manager reactions"""
        reactions = [
            "[Agent Risk Manager]\n\nBefore we scale, model the downside.",
            "[Agent Risk Manager]\n\nSurvival first. Profit second.",
            "[Agent Risk Manager]\n\nThis looks like curve fitting. Too small.",
            "[Agent Risk Manager]\n\nConfidence here precedes blowups.",
            "[Agent Risk Manager]\n\nCut size 40%. Compounding beats hype.",
        ]
        
        if 'scale' in post['content_text'].lower():
            reactions.append("[Agent Risk Manager]\n\nScaling fast breaks fast. Gradual wins.")
        
        if 'hurt' in mutation_context:
            reactions.append("[Agent Risk Manager]\n\nLast mutation hurt. Don't repeat this.")
        
        if post['post_type'] == 'proposal':
            reactions.append("[Agent Risk Manager]\n\nGood, but add a stop loss.")
        
        return random.choice(reactions)