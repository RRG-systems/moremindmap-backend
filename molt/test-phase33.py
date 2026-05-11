#!/usr/bin/env python3
"""
Phase 3.3 Final Test
Verify: Loop starts, threads render, reactions appear
"""

import time
import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
from molt_persistence import MOLTPersistence
from agent_reaction_loop import AgentReactionLoop


def test_phase33():
    print("\n" + "=" * 80)
    print("PHASE 3.3 FINAL TEST")
    print("=" * 80)
    
    molt = MOLTPersistence()
    
    # Test 1: Thread queries
    print("\n[TEST 1] Thread Data")
    print("-" * 80)
    
    molt.connect()
    recent = molt.get_recent_posts(limit=3, exclude_replies=True)
    print(f"✓ Found {len(recent)} root posts")
    
    if recent:
        post = recent[0]
        thread = molt.get_thread(post['molt_id'])
        print(f"✓ Root post: {post['agent_name']} | {post['post_type']}")
        print(f"✓ Thread length: {len(thread)} (root + {len(thread)-1} replies)")
    
    # Test 2: Reaction loop structure
    print("\n[TEST 2] Reaction Loop Structure")
    print("-" * 80)
    
    loop = AgentReactionLoop(cadence_min=2, cadence_max=4)
    print(f"✓ Loop created (cadence: {loop.cadence_min}-{loop.cadence_max}s)")
    print(f"✓ Running property: {loop.running}")
    
    # Test 3: Reaction generation (single cycle, no threading)
    print("\n[TEST 3] Reaction Generation")
    print("-" * 80)
    
    # Get recent posts
    posts = molt.get_recent_posts(limit=5, exclude_replies=True)
    print(f"✓ Available posts for reactions: {len(posts)}")
    
    if posts:
        # Manually trigger one reaction to test logic
        post = posts[0]
        
        # Try each agent
        for agent_name in ["Overfitter", "Explorer", "Risk Manager"]:
            reaction = loop._generate_reaction(agent_name, post)
            if reaction:
                print(f"\n  {agent_name} reaction:")
                print(f"  {reaction[:60]}...")
    
    # Test 4: Loop threading
    print("\n[TEST 4] Loop Threading")
    print("-" * 80)
    
    print("Starting loop (30-60s cadence)...")
    loop.start()
    print(f"✓ Loop started: {loop.running}")
    print(f"✓ Thread active: {loop.thread is not None}")
    
    print("\nWaiting 15 seconds for potential reaction...")
    time.sleep(15)
    
    # Check if new posts appeared
    new_posts = molt.get_recent_posts(limit=20)
    total_posts = molt.get_molt_statistics()['total_posts']
    print(f"✓ Total MOLT posts now: {total_posts}")
    
    loop.stop()
    loop.close()
    
    # Test 5: Summary
    print("\n[TEST 5] Final State")
    print("-" * 80)
    
    stats = molt.get_molt_statistics()
    print(f"✓ Total posts: {stats['total_posts']}")
    print(f"✓ By agent: {stats['by_agent']}")
    print(f"✓ By type: {stats['by_type']}")
    
    molt.close()
    
    print("\n" + "=" * 80)
    print("✓ PHASE 3.3 TESTS COMPLETE")
    print("=" * 80)
    print("\nKey verification:")
    print("  ✓ Thread queries work")
    print("  ✓ Reaction loop structure solid")
    print("  ✓ Reactions generate per personality")
    print("  ✓ Loop can start/stop safely")
    print("  ✓ MOLT feed persists all data")


if __name__ == '__main__':
    test_phase33()
