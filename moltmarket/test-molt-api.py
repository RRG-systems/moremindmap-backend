#!/usr/bin/env python3
"""
Test MOLT API layer (Phase 3.2)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'moltmarket'))
from molt_ui_layer import MOLTUILayer


def test_molt_api():
    print("\n" + "=" * 80)
    print("MOLT UI Layer API Test")
    print("=" * 80)
    
    molt_ui = MOLTUILayer()
    
    # Test 1: Get feed
    print("\n[TEST 1] Get MOLT Feed")
    print("-" * 80)
    feed = molt_ui.get_feed(limit=10)
    print(f"✓ Retrieved {len(feed)} posts")
    for post in feed[:2]:
        print(f"  - {post['agent_name']} | {post['post_type']}: {post['content_text'][:50]}...")
    
    # Test 2: Get statistics
    print("\n[TEST 2] Get Statistics")
    print("-" * 80)
    stats = molt_ui.get_statistics()
    print(f"✓ Total posts: {stats['total_posts']}")
    print(f"  By agent: {stats['by_agent']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  Hypotheses: {stats['hypotheses_spawned']}")
    print(f"  Total babies: {stats['total_bots_spawned']}")
    
    # Test 3: Get agents
    print("\n[TEST 3] Get Agent Names")
    print("-" * 80)
    agents = molt_ui.get_agent_names()
    print(f"✓ Found {len(agents)} agents: {agents}")
    
    # Test 4: Get post types
    print("\n[TEST 4] Get Post Types")
    print("-" * 80)
    post_types = molt_ui.get_post_types()
    print(f"✓ Found {len(post_types)} post types: {post_types}")
    
    # Test 5: Get lineage for first proposal
    print("\n[TEST 5] Get Lineage Detail")
    print("-" * 80)
    proposals = molt_ui.get_feed(post_type_filter='proposal', limit=1)
    if proposals:
        proposal = proposals[0]
        lineage = molt_ui.get_lineage(proposal['molt_id'])
        print(f"✓ Got lineage for: {proposal['agent_name']}")
        print(f"  Post: {proposal['molt_id']}")
        if lineage.get('hypothesis'):
            hyp = lineage['hypothesis']
            print(f"  Hypothesis: {hyp['title']}")
        if lineage.get('spawn'):
            spawn = lineage['spawn']
            total = 1 + spawn.get('variant_count', 10)
            print(f"  Spawned: {total} babies (1 canonical + {spawn.get('variant_count', 10)} variants)")
            print(f"  Canonical: {spawn['canonical_bot_id'][:40]}...")
            if spawn.get('bot_metrics'):
                print(f"  Variants tracked: {len([b for b in spawn['bot_metrics'] if not b['is_canonical']])}")
    
    # Test 6: Filter by agent
    print("\n[TEST 6] Filter by Agent")
    print("-" * 80)
    for agent in agents:
        agent_posts = molt_ui.get_feed(agent_filter=agent, limit=10)
        print(f"✓ {agent}: {len(agent_posts)} posts")
    
    molt_ui.close()
    
    print("\n" + "=" * 80)
    print("✓ ALL MOLT API TESTS PASSED")
    print("=" * 80)


if __name__ == '__main__':
    test_molt_api()
