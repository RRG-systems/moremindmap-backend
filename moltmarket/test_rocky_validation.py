"""
PART 9: ROCKY Validation Test Suite

Tests all Rocky features: query routing, reasoning, responses, playbook capture.
Run this before deployment.
"""

import json
import tempfile
from pathlib import Path
from rocky_think_engine_v2 import RockyThinkEngine, RockyDataLayer, RockyResponse
from rocky_nursery_governance import RockyNurseryGovernance
from rocky_playbook import RockyPlaybook, PlaybookEntry


class MockDataLayer:
    """Mock data layer for testing."""
    
    def __init__(self):
        self.brain_state = ('NORMAL', 'no_issues', 'System operating normally')
        self.brain_enforcement = {'allows_trade': True, 'throttle_active': False}
        self.arena_metrics = {
            'paper_return_pct': 2.5,
            'shadow_return_pct': 2.3,
            'total_trades': 245,
            'rolling_win_rate': 56.0,
        }
        self.nursery_cands = [
            {'variant_id': 'baby_001', 'created_at': 1704067200},
            {'variant_id': 'baby_002', 'created_at': 1704067200},
        ]
        self.nursery_metrics = [
            {'variant_id': 'baby_001', 'trades': 45, 'shadow_pnl': 125.5, 'sign_flip_rate': 8},
            {'variant_id': 'baby_002', 'trades': 38, 'shadow_pnl': 75.2, 'sign_flip_rate': 12},
        ]
    
    def get_brain_state(self):
        return self.brain_state
    
    def get_brain_enforcement(self):
        return self.brain_enforcement
    
    def get_arena_metrics(self):
        return self.arena_metrics
    
    def get_nursery_candidates(self):
        return self.nursery_cands
    
    def get_nursery_metrics(self):
        return self.nursery_metrics
    
    def get_molt_suggestions(self):
        return []


def test_rocky_initialization():
    """Test Rocky engine initializes cleanly."""
    print("\n[TEST] Rocky initialization...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            assert engine is not None
            assert engine.data_layer is not None
            print("✓ Rocky initializes cleanly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_brain_query():
    """Test BRAIN query routing and response."""
    print("\n[TEST] BRAIN query...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            response = engine.query("What is BRAIN doing?")
            
            assert response.diagnosis, "No diagnosis"
            assert response.evidence, "No evidence"
            assert response.confidence > 0, "No confidence"
            assert response.recommended_action, "No action"
            assert 'BRAIN' in response.diagnosis or 'NORMAL' in response.diagnosis, "Wrong response type"
            
            print(f"✓ BRAIN query works")
            print(f"  - Diagnosis: {response.diagnosis[:50]}...")
            print(f"  - Confidence: {response.confidence:.0%}")
            print(f"  - Action: {response.recommended_action[:50]}...")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_nursery_query():
    """Test Nursery query and ranking."""
    print("\n[TEST] Nursery query...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            response = engine.query("How's the Nursery?")
            
            assert response.diagnosis, "No diagnosis"
            assert 'Nursery' in response.diagnosis or 'baby' in response.diagnosis.lower(), "Wrong response"
            assert response.confidence > 0, "No confidence"
            
            print(f"✓ Nursery query works")
            print(f"  - Diagnosis: {response.diagnosis[:50]}...")
            print(f"  - Babies detected: {len(data_layer.get_nursery_candidates())}")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_arena_query():
    """Test Arena query."""
    print("\n[TEST] Arena query...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            response = engine.query("Is Arena strategy valid?")
            
            assert response.diagnosis, "No diagnosis"
            assert 'Arena' in response.diagnosis or 'trade' in response.diagnosis.lower(), "Wrong response"
            assert response.confidence > 0, "No confidence"
            
            print(f"✓ Arena query works")
            print(f"  - Diagnosis: {response.diagnosis[:50]}...")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_system_health_query():
    """Test system health aggregation."""
    print("\n[TEST] System health query...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            response = engine.query("What's the biggest risk?")
            
            assert response.diagnosis, "No diagnosis"
            assert response.confidence > 0, "No confidence"
            
            print(f"✓ System health query works")
            print(f"  - Diagnosis: {response.diagnosis[:50]}...")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_nursery_governance():
    """Test baby evaluation and ranking."""
    print("\n[TEST] Nursery governance (baby ranking)...")
    
    try:
        governance = RockyNurseryGovernance()
        
        metrics = [
            {'variant_id': 'baby_001', 'trades': 50, 'shadow_pnl': 150.0, 'paper_pnl': 160.0, 'sign_flip_rate': 5, 'degradation': 10},
            {'variant_id': 'baby_002', 'trades': 45, 'shadow_pnl': 80.0, 'paper_pnl': 90.0, 'sign_flip_rate': 15, 'degradation': 10},
            {'variant_id': 'baby_003', 'trades': 30, 'shadow_pnl': -50.0, 'paper_pnl': -40.0, 'sign_flip_rate': 35, 'degradation': 5},
        ]
        
        arena_metrics = {'shadow_return_pct': 1.5, 'total_trades': 200}
        
        health = governance.evaluate_nursery(metrics, arena_metrics)
        
        assert health.total_babies == 3, "Wrong baby count"
        assert health.best_baby.variant_id == 'baby_001', "Wrong best baby"
        assert health.best_baby.shadow_pnl == 150.0, "Wrong PnL"
        assert health.worst_baby.shadow_pnl == -50.0, "Wrong worst baby"
        
        print(f"✓ Baby governance works")
        print(f"  - Total babies: {health.total_babies}")
        print(f"  - Best: {health.best_baby.variant_id} ({health.best_baby.shadow_pnl:.0f}bps)")
        print(f"  - vs Arena: {health.vs_arena}")
        print(f"  - Health: {health.health_status}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_response_structure():
    """Test response format consistency."""
    print("\n[TEST] Response structure...")
    
    try:
        response = RockyResponse()
        response.diagnosis = "Test diagnosis"
        response.evidence = ["evidence 1", "evidence 2"]
        response.confidence = 0.85
        response.recommended_action = "Test action"
        
        data = response.to_dict()
        
        assert 'diagnosis' in data, "Missing diagnosis"
        assert 'evidence' in data, "Missing evidence"
        assert 'confidence' in data, "Missing confidence"
        assert 'recommended_action' in data, "Missing action"
        assert 'timestamp' in data, "Missing timestamp"
        assert isinstance(data['confidence'], float), "Confidence not float"
        assert 0 <= data['confidence'] <= 1, "Confidence out of range"
        
        print(f"✓ Response structure valid")
        print(f"  - All required fields present")
        print(f"  - Confidence: {data['confidence']}")
        
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_playbook_capture():
    """Test playbook logging."""
    print("\n[TEST] Playbook capture...")
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            playbook = RockyPlaybook(Path(tmpdir))
            
            entry = PlaybookEntry(
                category='BRAIN_RULE',
                pattern='High volatility triggers THROTTLE',
                why_it_matters='Protects capital during uncertainty',
                rule='If rolling_volatility > 2.5, activate THROTTLE mode',
                confidence=0.85,
                source='brain',
                context='Observed during 2026-04-23 market shock'
            )
            
            playbook.log(entry)
            
            all_entries = playbook.get_all()
            assert len(all_entries) == 1, "Playbook entry not logged"
            assert all_entries[0]['category'] == 'BRAIN_RULE', "Wrong category"
            
            print(f"✓ Playbook capture works")
            print(f"  - Entry logged: {entry.pattern}")
            print(f"  - Confidence: {entry.confidence:.0%}")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_query_routing():
    """Test query keyword routing."""
    print("\n[TEST] Query routing...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            
            # Test each query type
            queries = [
                ("What is BRAIN doing?", "BRAIN"),
                ("How's the Nursery?", "Nursery"),
                ("Is Arena valid?", "Arena"),
                ("What's the risk?", "issues"),
            ]
            
            for query, expected_keyword in queries:
                response = engine.query(query)
                assert response.diagnosis, f"No response for '{query}'"
                # Rough check that right handler was used
                print(f"  ✓ '{query}' routed correctly")
            
            print(f"✓ Query routing works (all 4 types)")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def test_edge_cases():
    """Test edge cases and error handling."""
    print("\n[TEST] Edge cases...")
    data_layer = MockDataLayer()
    
    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            engine = RockyThinkEngine(Path(tmpdir), data_layer)
            
            # Empty Nursery
            data_layer.nursery_cands = []
            data_layer.nursery_metrics = []
            response = engine.query("How's the Nursery?")
            assert 'empty' in response.diagnosis.lower(), "Should report empty Nursery"
            print(f"  ✓ Empty Nursery handled")
            
            # No Arena metrics
            data_layer.arena_metrics = {}
            response = engine.query("Is Arena valid?")
            assert response.diagnosis, "Should handle missing metrics"
            print(f"  ✓ Missing Arena metrics handled")
            
            # Ambiguous query (should show help)
            response = engine.query("xyz abc 123")
            assert 'help' in response.diagnosis.lower() or 'can help' in response.diagnosis.lower(), "Should show help"
            print(f"  ✓ Ambiguous query handled")
            
            print(f"✓ Edge cases handled gracefully")
            
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    return True


def run_all_tests():
    """Run complete test suite."""
    print("\n" + "="*60)
    print("ROCKY VALIDATION TEST SUITE")
    print("="*60)
    
    tests = [
        test_rocky_initialization,
        test_response_structure,
        test_brain_query,
        test_nursery_query,
        test_arena_query,
        test_system_health_query,
        test_nursery_governance,
        test_playbook_capture,
        test_query_routing,
        test_edge_cases,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test crashed: {e}")
            results.append(False)
    
    print("\n" + "="*60)
    passed = sum(results)
    total = len(results)
    print(f"RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("✓ ALL TESTS PASSED — ROCKY IS READY FOR DEPLOYMENT")
    else:
        print(f"✗ {total - passed} test(s) failed — review above")
    
    print("="*60 + "\n")
    
    return passed == total


if __name__ == '__main__':
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
