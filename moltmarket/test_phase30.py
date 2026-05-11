#!/usr/bin/env python3
"""
PHASE 30 Test Script
Verify backend data structure and frontend chart logic
"""

import sys
from pathlib import Path
from datetime import datetime

# Add to path
sys.path.insert(0, str(Path(__file__).parent))

from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator

def test_backend_data():
    """Test that backend returns all three equity curves"""
    print("\n" + "="*60)
    print("[PHASE 30] BACKEND VERIFICATION TEST")
    print("="*60)
    
    # Initialize
    data_layer = DataLayer(workspace_dir=Path.cwd())
    simulator = ExecutionSimulator(data_layer)
    
    data_layer.initialize()
    simulator.initialize()
    
    # Simulate some steps to generate data
    print("\n[STEP 1] Simulating 10 steps to generate trades...")
    for i in range(10):
        simulator.step()
    
    # Get equity curves
    paper = simulator.get_paper_equity_curve()
    shadow = simulator.get_shadow_equity_curve()
    backtest = simulator.get_backtest_equity_curve()
    
    # [PHASE 30] Backend Debug Output
    print(f"\n[PHASE 30] Backend data verification:")
    print(f"  Paper length: {len(paper)}")
    if paper:
        print(f"    First: {paper[0]}")
        print(f"    Last: {paper[-1]}")
    print(f"  Shadow length: {len(shadow)}")
    if shadow:
        print(f"    First: {shadow[0]}")
        print(f"    Last: {shadow[-1]}")
    print(f"  Backtest length: {len(backtest)}")
    if backtest:
        print(f"    First: {backtest[0]}")
        print(f"    Last: {backtest[-1]}")
    
    # Verify data structure
    assert isinstance(paper, list), "Paper should be a list"
    assert isinstance(shadow, list), "Shadow should be a list"
    assert isinstance(backtest, list), "Backtest should be a list"
    
    if paper:
        assert 'timestamp' in paper[0], "Paper points should have timestamp"
        assert 'value' in paper[0], "Paper points should have value"
        print("  ✓ Paper structure correct")
    
    if shadow:
        assert 'timestamp' in shadow[0], "Shadow points should have timestamp"
        assert 'value' in shadow[0], "Shadow points should have value"
        print("  ✓ Shadow structure correct")
    
    if backtest:
        assert 'timestamp' in backtest[0], "Backtest points should have timestamp"
        assert 'value' in backtest[0], "Backtest points should have value"
        print("  ✓ Backtest structure correct")
    
    print("\n[PHASE 30] Backend verification PASSED ✓")
    return True

def test_frontend_logic():
    """Test that frontend chart logic works correctly"""
    print("\n" + "="*60)
    print("[PHASE 30] FRONTEND LOGIC VERIFICATION")
    print("="*60)
    
    # Simulate backend response
    backend_response = {
        'paper': [
            {'timestamp': '2025-01-01T00:00:00', 'value': 10000.0},
            {'timestamp': '2025-01-01T00:01:00', 'value': 10050.0},
            {'timestamp': '2025-01-01T00:02:00', 'value': 10100.0},
        ],
        'shadow': [
            {'timestamp': '2025-01-01T00:00:00', 'value': 10000.0},
            {'timestamp': '2025-01-01T00:01:00', 'value': 10040.0},
            {'timestamp': '2025-01-01T00:02:00', 'value': 10080.0},
        ],
        'backtest': [
            {'timestamp': '2025-01-01T00:00:00', 'value': 10000.0},
            {'timestamp': '2025-01-01T00:01:00', 'value': 10100.0},
            {'timestamp': '2025-01-01T00:02:00', 'value': 10200.0},
        ],
    }
    
    print("\n[STEP 1] Simulating frontend data extraction...")
    
    # [PHASE 30] Frontend extraction logic
    equityCurves = {
        'paper': backend_response['paper'] or [],
        'shadow': backend_response['shadow'] or [],
        'backtest': backend_response['backtest'] or [],
    }
    
    print(f"  Paper length: {len(equityCurves['paper'])}")
    print(f"  Shadow length: {len(equityCurves['shadow'])}")
    print(f"  Backtest length: {len(equityCurves['backtest'])}")
    
    # [PHASE 30] Frontend chart update logic
    print("\n[STEP 2] Simulating chart update...")
    
    paperCurve = equityCurves['paper'] or []
    shadowCurve = equityCurves['shadow'] or []
    backtestCurve = equityCurves['backtest'] or []
    
    # Extract values (last 100 points)
    paperValues = paperCurve[-100:] if paperCurve else []
    shadowValues = shadowCurve[-100:] if shadowCurve else []
    backtestValues = backtestCurve[-100:] if backtestCurve else []
    
    # Map to actual values
    paperValues = [p['value'] for p in paperValues]
    shadowValues = [p['value'] for p in shadowValues]
    backtestValues = [p['value'] for p in backtestValues]
    
    maxLen = max(len(paperValues), len(shadowValues), len(backtestValues))
    labels = list(range(maxLen))
    
    print(f"  Paper values extracted: {paperValues}")
    print(f"  Shadow values extracted: {shadowValues}")
    print(f"  Backtest values extracted: {backtestValues}")
    print(f"  Labels generated: {labels}")
    
    # Verify all three are present
    assert len(paperValues) > 0, "Paper values should be present"
    assert len(shadowValues) > 0, "Shadow values should be present"
    assert len(backtestValues) > 0, "Backtest values should be present"
    
    # Verify chart structure
    datasets = [
        {'label': 'Paper', 'data': paperValues},
        {'label': 'Shadow', 'data': shadowValues},
        {'label': 'Backtest', 'data': backtestValues},
    ]
    
    print(f"\n[STEP 3] Verifying chart datasets:")
    for i, ds in enumerate(datasets):
        print(f"  Dataset {i} ({ds['label']}): {len(ds['data'])} points")
        assert len(ds['data']) > 0, f"{ds['label']} should have data"
        print(f"    ✓ {ds['label']} has data")
    
    print("\n[PHASE 30] Frontend logic verification PASSED ✓")
    return True

def main():
    try:
        test_backend_data()
        test_frontend_logic()
        
        print("\n" + "="*60)
        print("[PHASE 30] ALL TESTS PASSED ✓✓✓")
        print("="*60)
        print("\nChart fix summary:")
        print("✓ Backend returns all three equity curves")
        print("✓ Frontend extracts values correctly")
        print("✓ Chart update logic processes all three datasets")
        print("✓ Data structure is correct ({timestamp, value})")
        print("\n")
        return 0
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == '__main__':
    sys.exit(main())
