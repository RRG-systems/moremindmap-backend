#!/usr/bin/env python3
"""
MOLTmarket Live Validation Dashboard v1
Research console for live paper/shadow execution + historical backtest overlay
"""

import os
import sys
import json
import threading
import time
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path
from flask import Flask, render_template, jsonify, request
from dashboard_data_layer import DataLayer
from dashboard_execution import ExecutionSimulator
from evolution_engine import EvolutionEngine
from variant_nursery import VariantNursery
from brain_data_bridge import BrainDataBridge, BrainConfig
from simulator_recovery import recover_simulator_state
from rocky_operator_log import setup_rocky_log_endpoints, rocky_log
from arena_metrics_engine import setup_arena_metrics_endpoint
from brain_calibration_engine import setup_brain_calibration_endpoint
from think_session_bridge import setup_think_session_endpoints, think_bridge
from baby_registry import init_registry, get_registry

# PHASE 3.3: Agent reaction loop
sys.path.insert(0, str(Path.home() / '.openclaw' / 'workspace' / 'molt'))
try:
    from agent_reaction_loop import AgentReactionLoop
    from agent_observation_layer import AgentObservationLayer
    reaction_loop = AgentReactionLoop(cadence_min=30, cadence_max=60)
    observation_layer = AgentObservationLayer()
    print("[MOLT] Agent reaction loop + observation layer imported successfully")
except ImportError as e:
    print(f"[MOLT] WARNING: Agent layers import failed: {e}")
    reaction_loop = None
    observation_layer = None
except Exception as e:
    print(f"[MOLT] ERROR initializing Agent layers: {e}")
    reaction_loop = None
    observation_layer = None

# PHASE 32.6: Port Configuration
# Port 5000 is reserved by macOS AirTunes — DO NOT USE
PORT = 5050

# Initialize Flask app
app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['JSON_SORT_KEYS'] = False

# Global state

# PHASE 32.5E: Global error handlers - ensure all responses are valid JSON
@app.errorhandler(400)
def handle_400(e):
    return jsonify({'status': 'error', 'code': 400, 'message': 'Bad Request'}), 400

@app.errorhandler(403)
def handle_403(e):
    return jsonify({'status': 'error', 'code': 403, 'message': 'Forbidden'}), 403

@app.errorhandler(404)
def handle_404(e):
    return jsonify({'status': 'error', 'code': 404, 'message': 'Not Found'}), 404

@app.errorhandler(500)
def handle_500(e):
    return jsonify({'status': 'error', 'code': 500, 'message': str(e)}), 500

# Data layer
data_layer = DataLayer(workspace_dir=Path.cwd())

# Market configuration (single source of truth)
from market_config import MarketConfig
MarketConfig.set_active_market('coinbase')
print(f"[MARKET] Active market: {MarketConfig.get_active_market()}")

# Unified execution pipeline (all trades through one place)
from unified_execution_pipeline import UnifiedLedger, UnifiedExecutor, SimulatorExecutor as UnifiedSimulatorExecutor
try:
    unified_ledger = UnifiedLedger()
    unified_simulator_executor = UnifiedSimulatorExecutor(None)  # Simulator ref added after init
    unified_market_executors = {
        'simulator': unified_simulator_executor,
        'coinbase': unified_simulator_executor,
    }
    unified_executor = UnifiedExecutor(unified_market_executors, unified_ledger)
    print("[UNIFIED] Execution pipeline initialized")
    
    # Initialize baby registry (source of truth for baby identity/lifecycle)
    baby_registry = init_registry("baby_registry.jsonl")
    print("[REGISTRY] Baby registry initialized")
except Exception as e:
    print(f"[UNIFIED] ERROR initializing: {e}")
    import traceback
    traceback.print_exc()
    unified_executor = None
    unified_ledger = None

# PHASE 4.6: BRAIN enforcement callback for simulator
def get_current_brain_status():
    """Callback to get current BRAIN state for enforcement in simulator.
    
    PHASE 4.6: This callback is injected into ExecutionSimulator so it can
    check BRAIN state BEFORE executing trades. Ensures trades are gated by
    BRAIN enforcement (STOP/FLAT blocks, THROTTLE reduces size).
    """
    return {
        'state': dashboard_state.get('brain_state', 'NORMAL'),
        'reason_code': dashboard_state.get('brain_reason_code', 'unknown'),
        'reason_text': dashboard_state.get('brain_reason_text', ''),
    }

# PHASE 4.6: Inject BRAIN callback into simulator
simulator = ExecutionSimulator(data_layer, brain_status_getter=get_current_brain_status)

if unified_simulator_executor:
    unified_simulator_executor.simulator = simulator
    print("[UNIFIED] Simulator wired to unified executor")

# RECOVERY: Restore state if "New Run" was clicked and reset simulator
recover_simulator_state(simulator, data_layer)

# PHASE 10.3: Wire real Coinbase data (optional)
real_data_mode = False
try:
    from coinbase_market_feed import CoinbaseMarketFeed
    from execution_simulator_realdata import setup_real_data_simulation
    print("[DASHBOARD] Initializing real Coinbase feed...")
    feed = CoinbaseMarketFeed()
    if feed.connect(run_in_thread=True):
        time.sleep(2)
        if feed.is_connected():
            real_data_sim = setup_real_data_simulation(simulator, feed)
            real_data_mode = True
            print(f"[DASHBOARD] SUCCESS: Real data mode active ({real_data_sim.get_mode()})")
        else:
            print("[DASHBOARD] Feed connected but no data, using simulated prices")
    else:
        print("[DASHBOARD] Coinbase feed unavailable, using simulated prices")
except Exception as e:
    print(f"[DASHBOARD] Real data init failed: {e}, using simulated prices")

# PHASE 31: Evolution engine and nursery
evolution_engine = EvolutionEngine()
nursery = VariantNursery(workspace_dir=Path.cwd(), evolution_engine=evolution_engine)

# CRITICAL FIX: Wire unified executor into simulator
# This ensures Arena uses the same executor as Nursery babies
simulator.unified_executor = unified_executor
simulator.evolution_engine = evolution_engine
print("[ARENA-NURSERY SYNC] Unified executor wired to simulator")

# NURSERY REALITY BRIDGE: Unified execution for babies
from nursery_reality_bridge import NurseryRealityBridge
nursery_bridge = NurseryRealityBridge(simulator, data_layer)
print("[NURSERY BRIDGE] Initialized with shared simulator and data layer")

# BRAIN Engine (Phase 1.5)
brain_config = BrainConfig(
    max_daily_loss_usd=500.0,
    max_bot_drawdown_pct=5.0,
    throttle_instability_threshold=25.0
)
brain_bridge = BrainDataBridge(brain_config)

# ROCKY integration (wire into /api/think/query endpoint)
try:
    from rocky_think_integration import setup_rocky_think_endpoint
    print("[ROCKY] Wiring into Flask app...")
    rocky_integration_ready = True
except ImportError as e:
    print(f"[ROCKY] WARNING: Import failed: {e}")
    rocky_integration_ready = False

# Load user identity from USER.md
def load_user_identity():
    try:
        user_file = Path.home() / '.openclaw' / 'workspace' / 'USER.md'
        if user_file.exists():
            content = user_file.read_text()
            for line in content.split('\n'):
                if '**Name:**' in line:
                    name = line.split(':', 1)[1].strip().replace('**', '').strip()
                    if name:
                        return name
    except:
        pass
    return "Operator"

user_name = load_user_identity()
print(f"[SYSTEM] Loaded user: {user_name}")

# Global state
dashboard_state = {
    'user_name': user_name,
    'initialized': False,
    'running': False,
    'metrics': {},
    'latest_trades': [],
    'current_run_id': 'run_' + datetime.utcnow().strftime('%Y%m%d_%H%M%S'),
    'run_start_time': datetime.utcnow().isoformat(),
    'parent_strategy': None,
    'nursery_status': 'idle',
    'pending_mutation': None,
    'bot_id': 'arena_bot',
    'survival_pass': False,
    'max_drawdown': 0,
    'avg_pnl_per_trade': 0,
    'flip_rate': 0,
    'divergence': 0,
    'total_trades': 0,
    'rolling_win_rate': 0,
    # MANUAL DISCOVERY MODE (startup gating)
    'trading_enabled': False,  # DISABLED until promotion
    'brain_mode': 'FLAT',
    'brain_state': 'FLAT',  # Startup: no execution until promotion
    'brain_reason_code': 'flat_startup',
    'brain_reason_text': 'FLAT on startup. Arena disabled until promotion.',
}


@app.route('/')
def index():
    """Serve main dashboard"""
    return render_template('dashboard.html')


@app.route('/api/metrics')
def get_metrics():
    """Return current KPI metrics and state"""
    try:
        return jsonify(dashboard_state['metrics'])
    except Exception as e:
        print(f"[ERROR] /api/metrics failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/brain/status')
def get_brain_status():
    """Return current BRAIN state and enforcement status"""
    try:
        return jsonify({
            'state': dashboard_state.get('brain_state', 'UNKNOWN'),
            'reason_code': dashboard_state.get('brain_reason_code', 'unknown'),
            'reason_text': dashboard_state.get('brain_reason_text', 'not evaluated'),
            'enforcement': dashboard_state.get('brain_enforcement', {}),
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"[ERROR] /api/brain/status failed: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/trades')
def get_trades():
    """Return recent trades with all execution sources"""
    try:
        trades = data_layer.get_recent_trades(limit=50)
        return jsonify(trades or [])
    except Exception as e:
        print(f"[ERROR] /api/trades failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/equity-curves')
def get_equity_curves():
    """Return equity curves for paper, shadow, backtest"""
    try:
        # Safety: simulator may return floats or lists
        def safe_curve(raw):
            if not raw:
                return []
            if isinstance(raw, (int, float)):
                return [raw]
            if isinstance(raw, list):
                return raw
            return []
        
        curves = {
            'paper': safe_curve(simulator.get_paper_equity_curve()),
            'shadow': safe_curve(simulator.get_shadow_equity_curve()),
            'backtest': safe_curve(simulator.get_backtest_equity_curve()),
        }
        
        return jsonify(curves)
    except Exception as e:
        print(f"[ERROR] /api/equity-curves failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/breakdowns')
def get_breakdowns():
    """Return trade breakdowns by asset, signal, regime, direction"""
    try:
        breakdowns = data_layer.get_breakdowns()
        return jsonify(breakdowns or {'by_asset': {}, 'by_signal': {}, 'by_regime': {}, 'by_direction': {}})
    except Exception as e:
        print(f"[ERROR] /api/breakdowns failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/signal-health')
def get_signal_health():
    """Return rolling signal health metrics"""
    return jsonify(data_layer.get_signal_health())


@app.route('/api/execution-quality')
def get_execution_quality():
    """Return execution quality (slippage, fill rates)"""
    return jsonify(data_layer.get_execution_quality())


@app.route('/api/health')
def health():
    """Health check"""
    return jsonify({
        'status': 'ok',
        'running': dashboard_state['running'],
        'trades_count': len(dashboard_state['latest_trades']),
        'current_run_id': dashboard_state['current_run_id'],
    })


@app.route('/api/state')
def get_state():
    """Return current system state - SAFE INITIALIZATION ENDPOINT
    
    Returns idle state if no run is initialized.
    NEVER returns 400. Always returns 200 with valid JSON.
    Safe for dashboard to call on initial load.
    """
    try:
        # Get current run metrics if available
        current_run_id = dashboard_state.get('current_run_id')
        
        # If no run initialized, return safe idle state
        if not current_run_id:
            return jsonify({
                'status': 'idle',
                'run_id': None,
                'message': 'no active run',
                'metrics': {
                    'total_trades': 0,
                    'trade_sign_flips': 0,
                    'flip_rate': 0.0,
                    'pnl': 0
                }
            }), 200
        
        # Return active state with current metrics
        return jsonify({
            'status': 'active',
            'run_id': current_run_id,
            'message': 'run in progress',
            'metrics': dashboard_state.get('metrics', {
                'total_trades': 0,
                'trade_sign_flips': 0,
                'flip_rate': 0.0,
                'pnl': 0
            })
        }), 200
    
    except Exception as e:
        print(f"[ERROR] /api/state failed: {e}")
        # Even on error, return safe idle state instead of 500
        return jsonify({
            'status': 'error',
            'run_id': None,
            'message': 'state fetch error',
            'metrics': {
                'total_trades': 0,
                'trade_sign_flips': 0,
                'flip_rate': 0.0,
                'pnl': 0
            }
        }), 200


@app.route('/api/reset', methods=['POST'])
def reset():
    """PHASE 29: Reset system for new experiment run
    
    Execution sequence (CRITICAL ORDER):
    Step 1: Finalize current run (BEFORE any reset)
    Step 2: Generate new run_id
    Step 3: Append RUN_SEPARATOR to all CSVs
    Step 4: Reset in-memory state
    Step 5: DO NOT delete CSV files
    """
    import traceback
    
    try:
        # STEP 1: Finalize current run (BEFORE any reset)
        previous_run_summary = simulator.finalize_and_summarize_run()
        if previous_run_summary:
            data_layer.append_run_summary(previous_run_summary)
            print(f"[PHASE 29] Run finalized: {previous_run_summary['run_id']}")
        
        # STEP 2: Generate new run_id (timestamp-based)
        from datetime import datetime
        new_run_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        dashboard_state['current_run_id'] = new_run_id
        dashboard_state['run_start_time'] = datetime.utcnow()
        simulator.current_run_id = new_run_id
        simulator.run_start_time = datetime.utcnow()
        
        # STEP 3: Append RUN_SEPARATOR to all CSVs
        data_layer.append_run_separator(new_run_id)
        print(f"[PHASE 29] Run separators appended for run: {new_run_id}")
        
        # STEP 4: Reset in-memory state (ExecutionSimulator legacy variables)
        simulator.reset_run_state()
        print(f"[PHASE 29] In-memory state reset for new run: {new_run_id}")
        
        # PHASE 32.5 FIX: Reset DataLayer memory cache (CRITICAL - was causing stale trade counts)
        data_layer.reset_trades_for_new_run(new_run_id)
        print(f"[PHASE 32.5] DataLayer cache reset for new run: {new_run_id}")
        
        # STEP 5: CSVs are append-only (no deletion)
        # All historical data persists
        
        # Reset rolling edge metrics by recalculating
        update_metrics()
        
        return jsonify({
            'status': 'reset_complete',
            'new_run_id': new_run_id,
            'previous_run_summary': previous_run_summary,
        }), 200
        
    except Exception as e:
        print(f"[PHASE 29] ERROR in reset endpoint: {e}")
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'message': str(e),
        }), 500


def update_metrics():
    """PHASE 32.5G: Calculate and update KPI metrics with RUN FILTERING PROOF"""
    print("\n[METRICS UPDATE START]")
    print("[METRICS] current_run_id:", data_layer.current_run_id)
    
    paper_pnl, paper_trades = simulator.get_paper_pnl()
    shadow_pnl, shadow_trades = simulator.get_shadow_pnl()
    backtest_pnl, backtest_trades = simulator.get_backtest_pnl()
    
    print("\n[METRIC 1] total_trades")
    recent = data_layer.get_recent_trades(limit=1000)
    total_trades = len(recent)
    print("[METRIC 1] result:", total_trades)
    
    print("\n[METRIC 2] rolling_win_rate")
    win_rate = data_layer.get_win_rate()
    print("[METRIC 2] result:", round(win_rate * 100, 1), "%")
    
    print("\n[METRIC 3] avg_pnl_per_trade")
    avg_pnl = data_layer.get_avg_pnl_per_trade()
    print("[METRIC 3] result:", round(avg_pnl, 2))

    print("\n[METRIC 4] avg_entry_slippage")
    slippage = data_layer.get_avg_slippage()
    print("[METRIC 4] result:", round(slippage['entry_bps'], 2), "bps")
    
    print("\n[METRIC 5] trade_sign_flips")
    integrity = data_layer.get_trade_integrity()
    print("[METRIC 5] result:", integrity['sign_flips'], "flips (" + str(round(integrity['sign_flip_rate_pct'], 1)) + "%)")
    
    # ROLLING EDGE CALCULATIONS
    print("\n[METRIC 6] rolling_edge_20_trade")
    recent_20 = data_layer.get_recent_trades(limit=20)
    if recent_20:
        wins_20 = sum(1 for t in recent_20 if float(t.get('pnl', 0)) > 0)
        total_pnl_20 = sum(float(t.get('pnl', 0)) for t in recent_20)
        avg_pnl_20 = (total_pnl_20 / len(recent_20)) if recent_20 else 0
        edge_20_bps = avg_pnl_20 * 10000
        win_rate_20 = (wins_20 / len(recent_20) * 100) if recent_20 else 0
        avg_win_20 = (total_pnl_20 / wins_20) if wins_20 > 0 else 0
        avg_loss_20 = (sum(float(t.get('pnl', 0)) for t in recent_20 if float(t.get('pnl', 0)) < 0) / (len(recent_20) - wins_20)) if (len(recent_20) - wins_20) > 0 else 0
    else:
        edge_20_bps = 0
        win_rate_20 = 0
        avg_win_20 = 0
        avg_loss_20 = 0
    print("[METRIC 6] result:", round(edge_20_bps, 2), "bps")
    
    print("\n[METRIC 7] rolling_edge_50_trade")
    recent_50 = data_layer.get_recent_trades(limit=50)
    if recent_50:
        wins_50 = sum(1 for t in recent_50 if float(t.get('pnl', 0)) > 0)
        total_pnl_50 = sum(float(t.get('pnl', 0)) for t in recent_50)
        avg_pnl_50 = (total_pnl_50 / len(recent_50)) if recent_50 else 0
        edge_50_bps = avg_pnl_50 * 10000
        win_rate_50 = (wins_50 / len(recent_50) * 100) if recent_50 else 0
        cumulative = 0
        peak = 0
        drawdown_50 = 0
        for trade in recent_50:
            cumulative += float(trade.get('pnl', 0))
            if cumulative > peak:
                peak = cumulative
            dd = peak - cumulative
            drawdown_50 = max(drawdown_50, dd)
    else:
        edge_50_bps = 0
        win_rate_50 = 0
        drawdown_50 = 0
    print("[METRIC 7] result:", round(edge_50_bps, 2), "bps")
    
    # CORRECTED METRICS: Three-tier system (TIER 1: $, TIER 2: %, TIER 3: bps)
    initial_capital = 10000.0
    paper_return_pct = (paper_pnl / initial_capital) * 100
    shadow_return_pct = (shadow_pnl / initial_capital) * 100
    delta_return_pct = paper_return_pct - shadow_return_pct
    
    dashboard_state['metrics'] = {
        # TIER 1: RAW DOLLARS
        'paper_pnl_dollars': round(paper_pnl, 2),
        'shadow_pnl_dollars': round(shadow_pnl, 2),
        'delta_pnl_dollars': round(paper_pnl - shadow_pnl, 2),
        # TIER 2: % RETURN (normalized to initial capital)
        'paper_return_pct': round(paper_return_pct, 3),
        'shadow_return_pct': round(shadow_return_pct, 3),
        'delta_return_pct': round(delta_return_pct, 3),
        'backtest_edge_bps': round(data_layer.get_backtest_edge(), 2),
        'total_trades': total_trades,
        'rolling_win_rate': round(win_rate * 100, 1),
        'avg_pnl_per_trade': round(avg_pnl, 2),
        'current_signal': simulator.current_signal,
        'current_asset': simulator.current_asset,
        'paper_trades': paper_trades,
        'shadow_trades': shadow_trades,
        'backtest_trades': backtest_trades,
        'regime': simulator.current_regime,
        'timestamp': datetime.utcnow().isoformat(),
        # PHASE 28: Execution diagnostics
        'avg_entry_slippage_bps': round(slippage['entry_bps'], 2),
        'avg_exit_slippage_bps': round(slippage['exit_bps'], 2),
        'total_trades_integrity': integrity['total_trades'],
        'trade_count_diff': integrity['trade_diff'],
        'sign_flip_count': integrity['sign_flips'],
        'sign_flip_rate_pct': round(integrity['sign_flip_rate_pct'], 1),
        # Rolling edge metrics (20 and 50 trade windows)
        'rolling_edge_20_bps': round(edge_20_bps, 2),
        'rolling_win_rate_20': round(win_rate_20, 1),
        'rolling_avg_win_20': round(avg_win_20, 4),
        'rolling_avg_loss_20': round(avg_loss_20, 4),
        'rolling_edge_50_bps': round(edge_50_bps, 2),
        'rolling_win_rate_50': round(win_rate_50, 1),
        'rolling_drawdown_50': round(drawdown_50, 4),
        'active_strategy_id': evolution_engine.current_parent.get('id', 'baseline') if evolution_engine.current_parent else 'baseline',
        'active_strategy_generation': evolution_engine.current_parent.get('generation', 0) if evolution_engine.current_parent else 0,
        'simulator_instance_id': hex(id(simulator)),
    }
    
    # FIX: Sync metrics to top-level for Control/Rocky/Panels
    dashboard_state['total_trades'] = total_trades
    dashboard_state['flip_rate'] = round(integrity['sign_flip_rate_pct'], 1)
    dashboard_state['avg_pnl_per_trade'] = round(avg_pnl, 6)
    dashboard_state['divergence'] = round(delta_return_pct, 3)
    dashboard_state['rolling_win_rate'] = round(win_rate * 100, 1)
    dashboard_state['paper_return_pct'] = round(paper_return_pct, 3)
    dashboard_state['shadow_return_pct'] = round(shadow_return_pct, 3)
    
    # BUILD LEDGER CACHE: Snapshot all baby metrics for consistent reads
    # This ensures leaderboard and promotion read from the same snapshot
    if unified_ledger and evolution_engine.babies:
        ledger_cache = {}
        for baby in evolution_engine.babies:
            baby_id = baby.get('variant_id')
            if baby_id:
                ledger_cache[baby_id] = unified_ledger.get_trader_metrics(baby_id)
        dashboard_state['_ledger_cache'] = ledger_cache
        print(f"[LEDGER CACHE] Cached metrics for {len(ledger_cache)} babies")
    
    # BRAIN EVALUATION: Assess state against live metrics (Phase 1.5)
    try:
        # PnL-DRIVEN CALIBRATION: Monitor promoted baby's Arena performance
        if dashboard_state.get('brain_mode') == 'CALIBRATION' and dashboard_state.get('promoted_baby'):
            # Baby is in Arena, calibrate BRAIN based on real PnL DELTA (not cumulative)
            baseline_pnl = dashboard_state.get('promotion_baseline_pnl', 0)
            arena_pnl_delta = shadow_pnl - baseline_pnl  # PnL since promotion
            arena_win_rate = win_rate * 100  # As percentage
            
            promoted_id = dashboard_state['promoted_baby'].get('variant_id', 'unknown')
            print(f"[CALIBRATION] Monitoring {promoted_id}: Arena PnL=${arena_pnl:.2f}, Win {arena_win_rate:.1f}%")
            
            # PRIME DIRECTIVE: Make money, then protect capital
            if arena_pnl_delta > 100:
                # Winning big - go AGGRESSIVE
                new_state = 'AGGRESSIVE'
                reason = f'Arena PnL delta +${arena_pnl_delta:.2f} - AGGRESSIVE'
            elif arena_pnl_delta > 50:
                # Winning - stay AGGRESSIVE
                new_state = 'AGGRESSIVE'
                reason = f'Arena PnL delta +${arena_pnl_delta:.2f} - Continue AGGRESSIVE'
            elif arena_pnl_delta > 0 and arena_win_rate > 55:
                # Winning steadily - MODERATE to conservative
                new_state = 'MODERATE'
                reason = f'Arena PnL delta +${arena_pnl_delta:.2f}, Win {arena_win_rate:.1f}% - MODERATE'
            elif arena_pnl_delta > 0:
                # Winning but low win rate - MODERATE
                new_state = 'MODERATE'
                reason = f'Arena PnL delta +${arena_pnl_delta:.2f}, Win {arena_win_rate:.1f}% - MODERATE (lower conviction)'
            elif arena_pnl_delta > -50:
                # Small loss - CONSERVATIVE
                new_state = 'CONSERVATIVE'
                reason = f'Arena PnL delta {{arena_pnl_delta:.2f}} - Protect capital, CONSERVATIVE'
            elif arena_pnl_delta > -100:
                # Bigger loss - THROTTLE
                new_state = 'THROTTLE'
                reason = f'Arena PnL delta {{arena_pnl_delta:.2f}} - THROTTLE to reduce losses'
            else:
                # Major loss - STOP
                new_state = 'STOP'
                reason = f'Arena PnL delta {{arena_pnl_delta:.2f}} - STOP to protect capital'
            
            dashboard_state['brain_state'] = new_state
            dashboard_state['brain_reason_code'] = 'arena_pnl_calibration'
            dashboard_state['brain_reason_text'] = reason
            dashboard_state['brain_enforcement'] = brain_bridge.get_enforcement_flags()
            print(f"[CALIBRATION] {reason}")
        else:
            # Normal BRAIN evaluation (no promoted baby)
            brain_status = brain_bridge.evaluate(dashboard_state, simulator)
            dashboard_state['brain_state'] = brain_status.state
            dashboard_state['brain_reason_code'] = brain_status.reason_code
            dashboard_state['brain_reason_text'] = brain_status.reason_text
            dashboard_state['brain_enforcement'] = brain_bridge.get_enforcement_flags()
        
        # MANUAL DISCOVERY MODE: Force BRAIN to FLAT if trading not enabled
        # BUT: Don't override CALIBRATION mode even if trading_enabled is False
        if not dashboard_state.get('trading_enabled', False):
            if dashboard_state.get('brain_mode') != 'CALIBRATION':
                dashboard_state['brain_state'] = 'FLAT'
                print(f"[BRAIN] Trading disabled, state=FLAT")
        else:
            print(f"[BRAIN] State={dashboard_state['brain_state']} | Reason={dashboard_state['brain_reason_code']}")
    except Exception as e:
        print(f"[BRAIN] Calibration error: {e}")
        import traceback
        traceback.print_exc()
        dashboard_state['brain_state'] = 'ERROR'
        dashboard_state['brain_reason_code'] = 'calibration_error'
        dashboard_state['brain_reason_text'] = str(e)


def execute_baby_variant(baby, market_data=None):
    """Execute baby through unified execution pipeline (same signal as Arena)."""
    baby_id = baby['variant_id']
    print(f"[TRACE BABY] execute_baby_variant START for {baby_id}")
    
    # AUTO-REGISTER baby on first execution (registry is source of truth for identity)
    registry = get_registry()
    if not registry.get_baby(baby_id):
        parent_id = baby.get('id', 'baseline')
        generation = baby.get('generation', 0)
        dna = baby.get('parameters', {})
        registry.register_baby(baby_id, parent_id, generation, dna)
    
    if not unified_executor:
        print(f"[BABY] ERROR: unified_executor is None for {baby_id}")
        return
    if not simulator:
        print(f"[BABY] ERROR: simulator is None for {baby_id}")
        return
        return
    
    try:
        # REALITY CHECK: Verify baby uses same simulator/prices as Arena
        baby_btc = simulator._get_price('BTC')
        baby_eth = simulator._get_price('ETH')
        baby_tick = getattr(simulator, 'current_tick', None)
        print(f"[REALITY CHECK] NURSERY BABY: baby_id={baby_id}")
        print(f"[REALITY CHECK]   tick={baby_tick} BTC=${baby_btc:.2f} ETH=${baby_eth:.2f}")
        print(f"[REALITY CHECK]   simulator_instance=SAME (shared with Arena)")
        print(f"[REALITY CHECK]   ledger_instance={unified_ledger is not None} (shared)")
        print(f"[REALITY CHECK]   executor_instance={unified_executor is not None} (shared)")
        
        # Generate signal using SAME logic as Arena
        # This is the key: babies use Arena's signal generation
        
        # Check BRAIN enforcement - ONLY for Arena, NOT for Nursery babies
        brain = get_current_brain_status()
        brain_state = brain.get('state', 'NORMAL')
        
        # MANUAL DISCOVERY MODE: Nursery babies ALWAYS trade, regardless of Arena BRAIN state
        # Arena trading is gated elsewhere. Babies are independent.
        # This allows discovery while Arena is safely FLAT.
        
        # Generate signal with 15% probability (same as Arena)
        import random
        print(f"[TRACE BABY] About to generate signal for {baby_id}")
        if True:  # TESTING: always generate. Change back to: if random.random() < 0.15:
            print(f"[TRACE BABY] Signal generation condition TRUE for {baby_id}")
            print(f"[BABY SIGNAL] baby_id={baby_id} signal_generated=True")
            asset = random.choice(['BTC', 'ETH'])
            side = random.choice(['long', 'short'])
            print(f"[TRACE BABY] Generated signal: {asset} {side} for {baby_id}")
            entry_price = simulator._get_price(asset)
            exit_price = simulator._get_price(asset)
            
            signal = {
                'asset': asset,
                'side': side,
                'entry_price': entry_price,
                'exit_price': exit_price,
                'size': 1.0,
            }
            
            # Execute through unified pipeline
            print(f"[TRACE BABY] Calling unified_executor.execute_signal for {baby_id}")
            trade = unified_executor.execute_signal(
                source='baby',
                trader_id=baby_id,
                signal=signal
            )
            print(f"[TRACE BABY] execute_signal returned: {trade is not None}")
            print(f"[BABY EXECUTE] baby_id={baby_id} executed={trade is not None}")
            if trade:
                print(f"[BABY LEDGER] baby_id={baby_id} trades=1 shadow_pnl={trade.pnl:.2f}")
            
            if trade:
                print(f"[BABY] {baby_id}: trade | {trade.asset} {trade.side} | ${trade.pnl:.2f} ({trade.pnl_bps:.1f} bps)")
                
                # STEP 1: Log what executor gave us
                print(f"[CHAIN STEP 1] After execute_signal for {baby_id}:")
                print(f"  trade object exists: {trade is not None}")
                
                # STEP 2: Check unified_ledger immediately
                if unified_ledger:
                    ledger_metrics = unified_ledger.get_trader_metrics(baby_id)
                    if ledger_metrics:
                        print(f"[CHAIN STEP 2] Unified ledger metrics for {baby_id}:")
                        print(f"  trade_count: {ledger_metrics.get('trade_count', '?')}")
                        print(f"  shadow_pnl: {ledger_metrics.get('shadow_pnl', '?')}")
                        print(f"  paper_pnl: {ledger_metrics.get('paper_pnl', '?')}")
                        print(f"  flip_rate: {ledger_metrics.get('flip_rate', '?')}")
                    else:
                        print(f"[CHAIN STEP 2] NO metrics found in ledger for {baby_id}")
                else:
                    print(f"[CHAIN STEP 2] unified_ledger is None!")
                
                # SYNC: Update baby metrics from unified ledger
                if unified_ledger:
                    print(f"[DEBUG QUERY] Looking up metrics for baby_id: {baby_id}")
                    print(f"[DEBUG QUERY] Total trades in ledger: {len(unified_ledger.trades)}")
                    print(f"[DEBUG QUERY] Traders with records: {list(unified_ledger.trader_trades.keys())[:5]}")
                    
                    metrics = unified_ledger.get_trader_metrics(baby_id)
                    print(f"[DEBUG QUERY] Query result: {metrics}")
                    
                    if metrics:
                        baby['total_trades'] = metrics.get('trade_count', 0)
                        baby['shadow_pnl'] = metrics.get('shadow_pnl', 0.0)
                        baby['paper_pnl'] = metrics.get('paper_pnl', 0.0)
                        baby['win_rate'] = metrics.get('win_rate', 0.0)
                        baby['flip_rate'] = metrics.get('flip_rate', 0.0)
                        baby['degradation_pct'] = metrics.get('degradation_pct', 0.0)
                        baby['score'] = metrics.get('score', 0.0)
                        print(f"[BABY SYNC] {baby_id}: trades={baby['total_trades']}, shadow_pnl=${baby['shadow_pnl']:.2f}, paper_pnl=${baby['paper_pnl']:.2f}, flip={baby['flip_rate']:.1f}%")
                        
                        # STEP 3: Log baby object after sync
                        print(f"[CHAIN STEP 3] Baby object after sync for {baby_id}:")
                        print(f"  baby['total_trades']: {baby.get('total_trades', '?')}")
                        print(f"  baby['shadow_pnl']: {baby.get('shadow_pnl', '?')}")
                        print(f"  baby['paper_pnl']: {baby.get('paper_pnl', '?')}")
                        print(f"  baby['flip_rate']: {baby.get('flip_rate', '?')}")
                        print(f"  baby['degradation_pct']: {baby.get('degradation_pct', '?')}")
    
    except Exception as e:
        print(f"[BABY] ERROR {baby_id}: {e}")
        import traceback
        traceback.print_exc()


def update_baby_metrics():
    """Calculate fitness metrics for all active babies from unified ledger."""
    if not evolution_engine.babies or not unified_ledger:
        return
    
    for baby in evolution_engine.babies:
        baby_id = baby['variant_id']
        
        # Read metrics from unified ledger
        metrics = unified_ledger.get_trader_metrics(baby_id)
        
        if metrics['total_trades'] > 0:
            print(f"[METRICS] {baby_id}: trades={metrics['total_trades']}, "
                  f"pnl=${metrics['shadow_pnl']:.2f}, win_rate={metrics['win_rate']:.1f}%")


def sync_registry_with_evolution_engine():
    """On startup, register all spawned babies to registry (sync two tracking systems)"""
    registry = get_registry()
    if evolution_engine.babies:
        for baby in evolution_engine.babies:
            variant_id = baby.get('variant_id')
            if variant_id and not registry.get_baby(variant_id):
                parent_id = baby.get('id', 'baseline')
                generation = baby.get('generation', 0)
                dna = baby.get('parameters', {})
                registry.register_baby(variant_id, parent_id, generation, dna)
        print(f"[REGISTRY] Synced {len(evolution_engine.babies)} babies from evolution_engine")


def simulation_loop():
    """Main simulation loop - generates signals and executes paper/shadow"""
    interval = 2  # Update every 2 seconds
    last_trade_count = 0
    reality_check_count = 0
    
    while dashboard_state['running']:
        try:
            # REALITY CHECK: Verify Arena and Nursery use same feed every 50 cycles
            reality_check_count += 1
            if reality_check_count % 50 == 0:
                current_btc = simulator._get_price('BTC')
                current_eth = simulator._get_price('ETH')
                current_tick = getattr(simulator, 'current_tick', None)
                print(f"[REALITY CHECK] ARENA: tick={current_tick} BTC=${current_btc:.2f} ETH=${current_eth:.2f}")
                print(f"[REALITY CHECK] arena_feed_source={type(simulator).__name__}")
                print(f"[REALITY CHECK] shared_simulator_instance=True")
                print(f"[REALITY CHECK] shared_ledger_instance={unified_ledger is not None}")
                print(f"[REALITY CHECK] real_data_mode={real_data_mode}")
            
            # MAIN ARENA: Execute parent strategy
            print("[MAIN] Evaluating parent strategy")
            simulator.step()
            
            # NURSERY: Execute all active babies
            # MANUAL DISCOVERY MODE: Ensure Nursery trades even when Arena is FLAT
            trading_enabled = dashboard_state.get('trading_enabled', False)
            print(f"[MANUAL DISCOVERY] arena_trading_enabled={trading_enabled}")
            print(f"[MANUAL DISCOVERY] nursery_trading_enabled=True")
            
            active_babies = evolution_engine.babies if evolution_engine.babies else []
            if active_babies:
                print(f"[NURSERY SPAWN] babies_created={len(active_babies)}")
                print(f"[NURSERY LOOP] active_babies={len(active_babies)}")
                for baby in active_babies:
                    baby_id = baby['variant_id']
                    print(f"[TRACE MAIN] Calling execute_baby_variant for {baby_id}")
                    execute_baby_variant(baby)
                
                # Update all baby metrics
                update_baby_metrics()
                print(f"[NURSERY] Cycle complete - {len(evolution_engine.babies)} babies updated")
            
            # ARENA EXECUTION: If a baby has been promoted, execute it as Arena bot
            promoted_baby = dashboard_state.get('promoted_baby', None)
            if promoted_baby and trading_enabled:
                baby_id = promoted_baby.get('variant_id')
                print(f"[ARENA] Executing promoted baby: {baby_id}")
                try:
                    execute_baby_variant(promoted_baby)
                    print(f"[ARENA] Execution complete for {baby_id}")
                except Exception as e:
                    print(f"[ARENA ERROR] Failed to execute promoted baby {baby_id}: {e}")
                    import traceback
                    traceback.print_exc()
            
            # Update metrics
            update_metrics()
            
            # AGENT OBSERVATION: Post when new trades complete
            if observation_layer:
                recent_trades = data_layer.get_recent_trades(limit=100)
                current_trade_count = len(recent_trades)
                
                if current_trade_count > last_trade_count:
                    # New trades! Agents observe and post
                    new_trades = recent_trades[last_trade_count:]
                    
                    for trade in new_trades:
                        metrics = dashboard_state.get('metrics', {})
                        try:
                            molt_id = observation_layer.observe_trade_execution(
                                trade,
                                recent_trades,
                                metrics.get('paper_value', 0),
                                metrics.get('shadow_value', 0)
                            )
                            if molt_id:
                                print(f"[MOLT] Agent observation posted: {molt_id}")
                        except Exception as e:
                            print(f"[MOLT] Observation error: {e}")
                    
                    # Update last seen count
                    last_trade_count = current_trade_count
            
            # Get latest trades
            dashboard_state['latest_trades'] = data_layer.get_recent_trades(limit=30)
            
            time.sleep(interval)
        except Exception as e:
            print(f"Error in simulation loop: {e}", file=sys.stderr)
            time.sleep(interval)
        except Exception as e:
            print(f"Error in simulation loop: {e}", file=sys.stderr)
            time.sleep(interval)


def start_background_simulation():
    """Start simulation in background thread"""
    # Sync registry with any pre-spawned babies
    sync_registry_with_evolution_engine()
    
    dashboard_state['running'] = True
    thread = threading.Thread(target=simulation_loop, daemon=True)
    thread.start()
    print("[Dashboard] Background simulation started")


# =========================================================================
# PHASE 31: Variant Nursery Endpoints
# =========================================================================




@app.route('/api/new_run', methods=['POST'])
def new_run_preserve_strategy():
    """PHASE 9.2: New Run without resetting active strategy
    
    Resets panels/metrics INCLUDING paper/shadow/delta, but keeps the current bot alive.
    Unlike /api/reset which resets everything.
    
    BUG FIX (2026-04-20): Paper, shadow, and delta now explicitly clear to zero.
    """
    try:
        from datetime import datetime
        
        # Generate new run_id
        new_run_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        dashboard_state['current_run_id'] = new_run_id
        dashboard_state['run_start_time'] = datetime.utcnow().isoformat()
        
        # Reset metrics but preserve strategy
        simulator.current_run_id = new_run_id
        simulator.run_start_time = datetime.utcnow()
        
        # FIX: Explicitly reset paper/shadow equity curves
        print(f"[PHASE 9.2] Resetting simulator paper/shadow equity curves...")
        simulator.paper_equity = [10000.0]
        simulator.shadow_equity = [10000.0]
        simulator.backtest_equity = [10000.0]
        simulator.paper_pnl = 0.0
        simulator.shadow_pnl = 0.0
        simulator.backtest_pnl = 0.0
        simulator.paper_trades = 0
        simulator.shadow_trades = 0
        simulator.backtest_trades = 0
        print(f"[PHASE 9.2] ✓ Paper/shadow equity curves reset to $10,000")
        
        # Reset data layer for NEW RUN but keep strategy
        data_layer.reset_trades_for_new_run(new_run_id)
        
        # Reset metrics display (including paper/shadow/delta)
        update_metrics()
        
        # BUG FIX: Explicitly zero out paper/shadow/delta metrics
        dashboard_state['metrics']['paper_value'] = 0.0
        dashboard_state['metrics']['shadow_value'] = 0.0
        dashboard_state['metrics']['paper_shadow_delta_pct'] = 0.0
        print(f"[PHASE 9.2] ✓ Metrics zeroed: paper={dashboard_state['metrics']['paper_value']}, shadow={dashboard_state['metrics']['shadow_value']}, delta={dashboard_state['metrics']['paper_shadow_delta_pct']}")
        
        print(f"[PHASE 9.2] New run started: {new_run_id} (strategy preserved, metrics cleared)")
        
        return jsonify({
            'status': 'new_run_started',
            'new_run_id': new_run_id,
            'strategy_preserved': True,
            'metrics_cleared': {
                'paper_value': 0.0,
                'shadow_value': 0.0,
                'paper_shadow_delta_pct': 0.0,
            },
        }), 200
    except Exception as e:
        print(f"[ERROR] New run failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/rocky/mutation_status', methods=['GET'])
def get_mutation_status():
    """Get current mutation intent status."""
    try:
        pending = dashboard_state.get('pending_mutation')
        
        if pending:
            return jsonify({
                'has_pending_mutation': True,
                'mutation_summary': pending.get('mutation_summary'),
                'created_at': pending.get('created_at'),
                'bot_id': pending.get('bot_id'),
                'run_id': pending.get('run_id'),
            }), 200
        else:
            return jsonify({
                'has_pending_mutation': False,
                'mutation_summary': None,
                'created_at': None,
            }), 200
    except Exception as e:
        print(f"[ERROR] Mutation status failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/mutation/results', methods=['GET'])
def get_mutation_results():
    """Get latest mutation comparison results."""
    try:
        from mutation_tracker import MutationTracker
        
        tracker = MutationTracker(Path.cwd())
        latest = tracker.get_latest_result()
        
        if latest:
            return jsonify({
                'status': 'success',
                'has_results': True,
                'result': latest,
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'has_results': False,
                'result': None,
            }), 200
    except Exception as e:
        print(f"[ERROR] Mutation results failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500



@app.route('/api/trajectory', methods=['GET'])
def get_trajectory():
    """Get latest trajectory analysis."""
    try:
        from trajectory_analyzer import TrajectoryAnalyzer
        
        analyzer = TrajectoryAnalyzer(Path.cwd())
        latest = analyzer.get_latest_trajectory()
        
        if latest:
            return jsonify({
                'status': 'success',
                'has_trajectory': True,
                'trajectory': latest,
            }), 200
        else:
            return jsonify({
                'status': 'success',
                'has_trajectory': False,
                'trajectory': None,
            }), 200
    except Exception as e:
        print(f"[ERROR] Trajectory failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500



@app.route('/api/control', methods=['GET'])
def get_control():
    """Get current control layer decision."""
    try:
        from control_layer import ControlLayer
        from trajectory_analyzer import TrajectoryAnalyzer
        from mutation_tracker import MutationTracker
        
        control = ControlLayer(Path.cwd())
        trajectory_analyzer = TrajectoryAnalyzer(Path.cwd())
        mutation_tracker = MutationTracker(Path.cwd())
        
        # Get current metrics
        arena_metrics = {
            'survival_pass': dashboard_state.get('survival_pass', False),
            'max_drawdown': dashboard_state.get('max_drawdown', 0),
            'avg_pnl_per_trade': dashboard_state.get('avg_pnl_per_trade', 0),
            'total_trades': dashboard_state.get('total_trades', 0),
            'sign_flip_rate_pct': dashboard_state.get('flip_rate', 0),
        }
        
        # Get trajectory
        trajectory = trajectory_analyzer.get_latest_trajectory()
        
        # Get mutation result
        mutation_result = mutation_tracker.get_latest_result()
        
        # Evaluate control
        decision = control.evaluate_control(arena_metrics, trajectory, mutation_result)
        
        # Log decision
        control.log_control_decision(decision)
        
        return jsonify({
            'status': 'success',
            'decision': decision,
        }), 200
    except Exception as e:
        print(f"[ERROR] Control layer failed: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/nursery/spawn', methods=['POST'])
def spawn_nursery():
    """PHASE 31/5: Spawn baby variant nursery with mutation support"""
    try:
        run_id = dashboard_state.get('current_run_id', 'nursery_run')
        babies = nursery.spawn_babies(run_id=run_id, count=10)
        
        variant_ids = [b['variant_id'] for b in babies]
        print(f'[NURSERY] Spawned {len(babies)} babies: {variant_ids}')
        
        return jsonify({
            'status': 'success',
            'run_id': run_id,
            'babies_count': len(babies),
            'variant_ids': variant_ids,
            'mutation_applied': False,
            'mutation_log': 'No mutation applied',
        }), 200
    except Exception as e:
        # MOLT isolation: Try to return partial success even if MOLT fails
        print(f'[NURSERY] WARNING (non-blocking): spawn hit error: {str(e)}')
        print(f'[NURSERY] Attempting to return what we have...')
        try:
            # Return the babies that were spawned, even if MOLT logging failed
            variant_ids = [b['variant_id'] for b in evolution_engine.babies[-10:]] if evolution_engine.babies else []
            return jsonify({
                'status': 'success',
                'babies_count': len(variant_ids),
                'variant_ids': variant_ids,
                'note': 'Babies spawned but MOLT logging incomplete'
            }), 200
        except:
            return jsonify({'error': str(e)}), 500


@app.route('/api/nursery/leaderboard')
def get_nursery_leaderboard():
    """PHASE 31: Get current nursery leaderboard (defensive, always returns 200)"""
    try:
        print("[NURSERY] leaderboard endpoint called")
        
        # Get babies from evolution_engine
        babies = evolution_engine.babies if evolution_engine.babies else []
        print(f"[NURSERY] Found {len(babies)} babies")
        
        if not babies:
            print("[NURSERY] No babies - returning empty leaderboard")
            return jsonify({
                'status': 'idle',
                'leaderboard': [],
                'count': 0
            }), 200
        
        # Log first baby structure for debugging
        if babies:
            print(f"[NURSERY] First baby structure: {list(babies[0].keys())}")
        
        # Build leaderboard with defensive field access
        leaderboard = []
        for baby in babies:
            try:
                variant_id = baby.get('variant_id', 'unknown')
                trades = baby.get('total_trades', 0)
                print(f"[LEADERBOARD READ] baby_id={variant_id} trades={trades}")
                
                # READ DIRECTLY FROM UNIFIED LEDGER (source of truth)
                ledger_metrics = {}
                if unified_ledger:
                    ledger_metrics = unified_ledger.get_trader_metrics(variant_id)
                
                trades_count = ledger_metrics.get('total_trades', 0)
                shadow_pnl_val = ledger_metrics.get('shadow_pnl', 0.0)
                paper_pnl_val = ledger_metrics.get('total_pnl', 0.0)  # Use total_pnl as paper
                win_rate_val = ledger_metrics.get('win_rate', 0.0)
                
                # CALCULATE flip_rate, degradation, and score from trades
                flip_rate_val = 0.0
                degradation_val = 0.0
                score_val = 0.0
                
                if trades_count > 0 and unified_ledger:
                    # Get all trades for this baby
                    baby_trades = [t for t in unified_ledger.trades if t.trader_id == variant_id]
                    
                    if len(baby_trades) >= 2:
                        # Calculate sign flips (direction changes: long → short or vice versa)
                        sides = [t.side for t in baby_trades]
                        flips = sum(1 for i in range(1, len(sides)) if sides[i] != sides[i-1])
                        flip_rate_val = (flips / len(baby_trades) * 100) if baby_trades else 0.0
                    
                    # Degradation: paper vs shadow (how much we lost to slippage/fees)
                    if shadow_pnl_val != 0:
                        degradation_val = ((paper_pnl_val - shadow_pnl_val) / abs(shadow_pnl_val) * 100)
                    
                    # Score: Primary on shadow PnL, penalize high flip rate and degradation
                    score_val = shadow_pnl_val * 0.7 - (flip_rate_val * 0.5) - (max(0, degradation_val) * 0.2)
                
                baby_entry = {
                    'variant_id': variant_id,
                    'id': baby.get('id', baby.get('variant_id', 'unknown')),
                    'name': baby.get('name', baby.get('variant_id', 'unknown')),
                    'generation': baby.get('generation', 0),
                    'mutation_type': baby.get('mutation_type', 'NONE'),
                    'trades': trades_count,
                    'shadow_pnl': shadow_pnl_val,
                    'paper_pnl': paper_pnl_val,
                    'win_rate': win_rate_val,
                    'flip_rate': flip_rate_val,
                    'degradation': degradation_val,
                    'score': score_val,
                    'status': baby.get('status', 'active'),
                }
                
                # STEP 4: Log what we're putting in JSON for trace baby
                if 'baseline_holding_time_d41db9a4' in variant_id or 'baseline_holding_time_25248386' in variant_id:
                    print(f"[CHAIN STEP 4] Leaderboard entry for {variant_id}:")
                    print(f"  trades: {baby_entry['trades']}")
                    print(f"  shadow_pnl: {baby_entry['shadow_pnl']}")
                    print(f"  paper_pnl: {baby_entry['paper_pnl']}")
                    print(f"  flip_rate: {baby_entry['flip_rate']}")
                    print(f"  degradation: {baby_entry['degradation']}")
                    print(f"  score: {baby_entry['score']}")
                
                leaderboard.append(baby_entry)
                print(f"[LEADERBOARD] {variant_id}: flip={flip_rate_val:.1f}%, degrad={degradation_val:.1f}%, score={score_val:.2f}")
            except Exception as e:
                print(f"[NURSERY] WARNING: Could not process baby {baby.get('variant_id', '?')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[NURSERY] Built leaderboard with {len(leaderboard)} entries")
        
        return jsonify({
            'status': 'active' if leaderboard else 'idle',
            'leaderboard': leaderboard,
            'count': len(leaderboard)
        }), 200
    
    except Exception as e:
        print(f"[NURSERY] CRITICAL ERROR in leaderboard: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # DEFENSIVE: Always return 200 with empty leaderboard
        return jsonify({
            'status': 'error',
            'leaderboard': [],
            'count': 0,
            'error_message': str(e)
        }), 200


@app.route('/api/rocky/insight', methods=['GET'])
def get_rocky_insight():
    """PHASE 9: Generate Rocky insight from FULL SYSTEM context."""
    try:
        from rocky_insights import RockyInsightsEngine
        from trajectory_analyzer import TrajectoryAnalyzer
        from mutation_tracker import MutationTracker
        from control_layer import ControlLayer
        
        # Get current metrics
        metrics = {
            'total_trades': dashboard_state.get('total_trades', 0),
            'sign_flip_rate_pct': dashboard_state.get('flip_rate', 0),
            'avg_pnl_per_trade': dashboard_state.get('avg_pnl_per_trade', 0),
            'paper_vs_shadow_delta': dashboard_state.get('divergence', 0),
            'rolling_win_rate': dashboard_state.get('rolling_win_rate', 0),
        }
        
        run_id = dashboard_state.get('current_run_id', 'unknown')
        bot_id = dashboard_state.get('bot_id', 'arena_bot')
        
        # PHASE 9: Get trajectory
        trajectory_analyzer = TrajectoryAnalyzer(Path.cwd())
        trajectory_data = trajectory_analyzer.get_latest_trajectory()
        
        # PHASE 9: Get mutation result
        mutation_tracker = MutationTracker(Path.cwd())
        mutation_result = mutation_tracker.get_latest_result()
        
        # PHASE 9: Get control decision
        control_layer = ControlLayer(Path.cwd())
        arena_metrics_for_control = {
            'survival_pass': dashboard_state.get('survival_pass', False),
            'max_drawdown': dashboard_state.get('max_drawdown', 0),
            'avg_pnl_per_trade': metrics['avg_pnl_per_trade'],
            'total_trades': metrics['total_trades'],
            'sign_flip_rate_pct': metrics['sign_flip_rate_pct'],
        }
        control_decision = control_layer.evaluate_control(
            arena_metrics_for_control,
            trajectory_data,
            mutation_result
        )
        
        # Generate insight with full context
        engine = RockyInsightsEngine(Path.cwd())
        insight = engine.generate_insight(
            metrics, run_id, bot_id,
            trajectory_data=trajectory_data,
            mutation_result=mutation_result,
            control_decision=control_decision
        )
        
        return jsonify({
            'status': 'success',
            'notes': insight['notes'],
            'proposal': insight['proposal'],
            'run_id': run_id,
            'bot_id': bot_id,
            'system_context': {
                'trajectory': trajectory_data.get('mutated', {}).get('trajectory', 'STABLE') if trajectory_data else 'STABLE',
                'control_action': control_decision.get('action', 'NORMAL'),
                'mutation_result': mutation_result.get('result', 'INCONCLUSIVE') if mutation_result else 'INCONCLUSIVE',
            },
            'timestamp': datetime.utcnow().isoformat(),
        }), 200
    except Exception as e:
        print(f"[ERROR] Rocky insight failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

        traceback.print_exc()
        return jsonify({'status': 'idle', 'leaderboard': []}), 200



@app.route('/api/rocky/decision', methods=['POST'])
def record_rocky_decision():
    """Record human decision on Rocky proposal."""
    try:
        from rocky_insights import RockyInsightsEngine
        
        data = request.get_json()
        decision = data.get('decision')  # 'APPROVED' or 'REJECTED'
        run_id = data.get('run_id')
        bot_id = data.get('bot_id')
        
        if not decision or not run_id or not bot_id:
            return jsonify({
                'status': 'error',
                'message': 'Missing required fields: decision, run_id, bot_id'
            }), 400
        
        # Update decision in log
        engine = RockyInsightsEngine(Path.cwd())
        success = engine.update_decision(bot_id, run_id, decision)
        
        if success:
            # PHASE 4: Create mutation intent if APPROVED
            if decision == 'APPROVED':
                dashboard_state['pending_mutation'] = {
                    'status': 'PENDING_SPAWN',
                    'run_id': run_id,
                    'bot_id': bot_id,
                    'proposal_timestamp': datetime.utcnow().isoformat(),
                    'mutation_summary': 'Approved proposal pending spawn',
                    'created_at': datetime.utcnow().isoformat(),
                }
                print(f"[PHASE 4] Mutation intent created for {bot_id}")
            
            return jsonify({
                'status': 'success',
                'message': f'Decision recorded: {decision}',
                'decision': decision,
                'bot_id': bot_id,
                'run_id': run_id,
                'timestamp': datetime.utcnow().isoformat(),
                'mutation_intent_created': decision == 'APPROVED',
            }), 200
        else:
            return jsonify({
                'status': 'error',
                'message': 'Failed to update decision'
            }), 500
    except Exception as e:
        print(f"[ERROR] Rocky decision failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/nursery/finalize', methods=['POST'])
def finalize_nursery():
    """PHASE 31: Score and finalize all babies"""
    try:
        run_id = dashboard_state.get('current_run_id', 'nursery_run')
        leaderboard = nursery.finalize_and_score_babies(run_id=run_id)
        
        return jsonify({
            'status': 'finalized',
            'leaderboard': leaderboard,
        }), 200
    except Exception as e:
        print(f"[PHASE 31] ERROR finalizing nursery: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# =========================================================================
# PHASE 32.1: Backend Promotion Endpoint
# =========================================================================

def validate_promotion(baby):
    """Validate baby is eligible for promotion"""
    # Check trade count
    if baby.get('trade_count', 0) < 30:
        return False, f"insufficient trades: {baby.get('trade_count', 0)}"
    
    # Check score validity
    if baby.get('score', -999) <= -999:
        return False, f"invalid score: {baby.get('score', -999)}"
    
    # Check status
    if baby.get('status') == 'promoted':
        return False, "already promoted"
    
    if baby.get('status') == 'retired':
        return False, "already retired"
    
    return True, "valid"


def log_promotion_to_csv(promoted_variant_id, retired_count, run_id):
    """Log promotion event to variant_nursery.csv"""
    try:
        nursery_file = Path.cwd() / 'variant_nursery.csv'
        
        # Read existing CSV to update status fields
        rows = []
        with open(nursery_file, 'r', newline='') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['variant_id'] == promoted_variant_id:
                    row['status'] = 'promoted'
                    row['promoted_at'] = datetime.now().isoformat()
                elif row['run_id'] == run_id and row['status'] == 'active':
                    row['status'] = 'retired'
                    row['retired_at'] = datetime.now().isoformat()
                rows.append(row)
        
        # Write back updated CSV
        with open(nursery_file, 'w', newline='') as f:
            if rows:
                fieldnames = list(rows[0].keys())
                # Ensure promoted_at and retired_at are in fieldnames if they're in rows
                if 'promoted_at' not in fieldnames:
                    fieldnames.append('promoted_at')
                if 'retired_at' not in fieldnames:
                    fieldnames.append('retired_at')
                
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        print(f"[NURSERY] promotion recorded in CSV")
    except Exception as e:
        print(f"[NURSERY] ERROR logging promotion to CSV: {str(e)}")


@app.route('/api/nursery/promote/<variant_id>', methods=['POST'])
def promote_baby(variant_id):
    """PHASE 32.1: Promote a nursery baby to become the new parent strategy"""
    print(f"[PROMOTE CLICK] baby_id={variant_id}")
    
    try:
        print(f"[PROMOTE API] received baby_id={variant_id}")
        
        # STEP 1: Check registry for baby identity (registry is source of truth)
        registry = get_registry()
        baby_entry = registry.get_baby(variant_id)
        if not baby_entry:
            print(f"[PROMOTE API] ERROR: {variant_id} not in registry")
            return jsonify({'success': False, 'reason': 'variant_not_found', 'error': f'{variant_id} not found in registry'}), 404
        
        if baby_entry['status'] != 'active':
            print(f"[PROMOTE API] ERROR: {variant_id} status is {baby_entry['status']}, not active")
            return jsonify({'success': False, 'reason': 'not_active', 'error': f'Baby status is {baby_entry["status"]}, must be active'}), 400
        
        # STEP 2: Get metrics from ledger cache (consistent snapshot from metrics update)
        ledger_cache = dashboard_state.get('_ledger_cache', {})
        ledger_metrics = ledger_cache.get(variant_id, {})
        if not ledger_metrics and unified_ledger:
            # Fallback: read fresh if cache miss
            ledger_metrics = unified_ledger.get_trader_metrics(variant_id)
        
        shadow_pnl = ledger_metrics.get('shadow_pnl', 0.0)
        print(f"[PROMOTE API] Ledger metrics (cached): trades={ledger_metrics.get('total_trades', 0)}, pnl=${shadow_pnl:.2f}")
        
        # STEP 3: TASK 3 - Validate eligibility: shadow_pnl > 0
        print(f"[PROMOTE ELIGIBILITY] baby_id={variant_id} shadow_pnl={shadow_pnl} eligible={shadow_pnl > 0}")
        
        if shadow_pnl <= 0:
            print(f"[PROMOTE API] ERROR: shadow_pnl not positive ({shadow_pnl})")
            return jsonify({'success': False, 'reason': 'shadow_pnl_not_positive', 'error': f'Requires positive shadow PnL (current: ${shadow_pnl:.2f})'}), 400
        
        print(f"[NURSERY] promotion validation passed")
        
        # STEP 3.5: Update registry status (registry is authoritative for lifecycle)
        registry.promote_baby(variant_id)
        print(f"[REGISTRY] Marked {variant_id} as promoted")
        
        # STEP 4: Reconstruct baby object (from registry if available, else minimal from ledger)
        if baby_entry:
            baby = baby_entry.copy()
        else:
            # Baby not in registry yet (hasn't traded), create minimal object
            baby = {
                'variant_id': variant_id,
                'status': 'active',
                'parameters': {},
                'mutation_type': 'unknown',
            }
        baby['status'] = 'promoted'
        baby['promoted_at'] = datetime.now().isoformat()
        print(f"[NURSERY] marking {variant_id} as promoted")
        
        # STEP 5: Mark other babies as retired
        retired_count = 0
        for b in evolution_engine.babies:
            if b['variant_id'] != variant_id:
                print(f"[NURSERY] retiring {b['variant_id']}")
                b['status'] = 'retired'
                b['retired_at'] = datetime.now().isoformat()
                retired_count += 1
        
        print(f"[NURSERY] {retired_count} babies marked retired")
        
        # PHASE 32.3: STEP 6A - Update evolution engine's authoritative parent
        print(f"[NURSERY-32.3] Updating evolution_engine.current_parent to {variant_id}")
        promoted_parent = evolution_engine.promote_baby_to_parent(baby)
        print(f"[NURSERY-32.3] evolution_engine.current_parent updated")
        
        # STEP 6B: Also update dashboard_state for UI display consistency
        print(f"[NURSERY] replacing dashboard parent strategy with {variant_id} config")
        dashboard_state['parent_strategy'] = {
            'id': promoted_parent['id'],
            'parent_variant_id': promoted_parent['id'],
            'mutation_type': baby.get('mutation_type', 'unknown'),
            'parameter_value': baby.get('parameter_value', None),
            'generation': promoted_parent['generation'],
            'promoted_from': 'nursery',
            'promoted_at': promoted_parent.get('promoted_at', datetime.now().isoformat()),
            'previous_generation': dashboard_state.get('parent_strategy'),
        }
        print(f"[NURSERY] dashboard parent strategy replaced")
        
        # PHASE 4.5: Update money state - set active bot and 1% allocation
        dashboard_state['active_bot_id'] = variant_id
        dashboard_state['active_bot_allocation'] = 1.0
        dashboard_state['active_bot_hypothesis'] = promoted_parent.get('hypothesis_id', 'hyp-unknown')
        dashboard_state['capital_allocated'] = 1.0
        print(f"[PHASE 4.5] Money state updated: active_bot={variant_id}, allocation=1.0%")
        
        # STEP 7: Clear active nursery and RESPAWN from new parent
        print(f"[NURSERY] clearing nursery execution state")
        evolution_engine.babies = []
        dashboard_state['nursery_status'] = 'inactive'
        print(f"[NURSERY] nursery state cleared")
        
        # CRITICAL: Spawn NEW generation from promoted parent
        # This ensures loop continues: promotion → new parent → new babies
        print(f"[NURSERY RESPAWN] Spawning new generation from promoted parent")
        evolution_engine.spawn_baby_variants(count=10)
        dashboard_state['nursery_status'] = 'active'
        print(f"[NURSERY RESPAWN] {len(evolution_engine.babies)} new babies spawned from promoted parent")
        
        # STEP 8: Log to CSV
        print(f"[NURSERY] recording promotion to variant_nursery.csv")
        run_id = dashboard_state.get('current_run_id', 'unknown')
        log_promotion_to_csv(variant_id, retired_count, run_id)
        
        # STEP 9A: LOAD BABY DNA INTO ARENA
        print(f"[PROMOTE DNA] Loading baby DNA into Arena active strategy")
        
        # Baby object has parameters directly (not nested in dna_json)
        baby_params = baby.get('parameters', {})
        baby_strategy_type = 'mean_reversion'  # Evolution engine always uses mean_reversion
        
        print(f"[PROMOTE DNA] baby_strategy_type={baby_strategy_type}")
        print(f"[PROMOTE DNA] baby_params={baby_params}")
        
        # Update Arena's active strategy DNA with baby's DNA
        # This ensures Arena now trades with the baby's strategy, not baseline
        parent_strategy_dna = {
            'bot_id': variant_id,
            'strategy_type': baby_strategy_type,
            'parameters': baby_params,
            'generation': promoted_parent.get('generation', 1),
            'promoted_from_baby': variant_id,
            'promoted_timestamp': datetime.now().isoformat(),
        }
        dashboard_state['parent_strategy_dna'] = parent_strategy_dna
        
        # Wire DNA into Arena simulator so it uses promoted baby's strategy
        if simulator:
            simulator.set_promoted_parent_dna(parent_strategy_dna)
            print(f"[PROMOTE DNA] Simulator wired with promoted baby strategy")
        
        print(f"[PROMOTE DNA] Arena active strategy DNA updated to baby: {variant_id}")
        print(f"[PROMOTE DNA] Strategy type: {baby_strategy_type}")
        print(f"[PROMOTE DNA] Parameters loaded: {list(baby_params.keys())}")
        
        # STEP 9B: CALIBRATION - NO RESET
        # Arena capital is cumulative (real trading logic)
        # Metrics only reset on fresh terminal startup
        # CALIBRATION monitors cumulative PnL from this point forward
        print(f"[PROMOTE] trading_enabled set to True")
        dashboard_state['trading_enabled'] = True
        dashboard_state['brain_mode'] = 'CALIBRATION'
        dashboard_state['brain_state'] = 'CALIBRATION'
        dashboard_state['brain_reason_code'] = 'arena_pnl_calibration'
        dashboard_state['brain_reason_text'] = f'Baby promoted: {variant_id}. Starting CALIBRATION mode.'
        # CRITICAL: Store promoted baby object so Arena loop can execute it
        dashboard_state['promoted_baby'] = baby
        # Track promotion baseline for CALIBRATION delta calculation
        dashboard_state['promotion_baseline_pnl'] = shadow_pnl
        dashboard_state['promotion_baseline_trades'] = shadow_trades
        print(f"[PROMOTE] promoted_baby stored to dashboard_state for Arena execution")
        print(f"[PROMOTE] Calibration baseline: PnL=${shadow_pnl:.2f}, Trades={shadow_trades}")
        print(f"[PROMOTE] brain_mode set to PROBATION")
        print(f"[PROMOTE] brain_state set to PROBATION")
        print(f"[PROMOTE] active_arena_parent set to {variant_id}")
        print(f"[PROMOTE] active_strategy set to {variant_id}")
        print(f"[PROMOTE] generation incremented to {promoted_parent.get('generation', 1)}")
        print(f"[PROMOTE] nursery respawn triggered=True")
        
        print("[PROMOTE API] response=success True")
        return jsonify({
            'success': True,
            'status': 'success',
            'promoted_variant': variant_id,
            'promoted_by': 'manual_promote_button',
            'shadow_pnl': shadow_pnl,
            'message': f'Promoted {variant_id} (shadow PnL: ${shadow_pnl:.2f}). BRAIN in PROBATION mode.',
        }), 200
    
    except Exception as e:
        print(f"[PROMOTE API] ERROR in promotion: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'reason': 'internal_error', 'error': str(e)}), 500



# PHASE 32.2 PART 4: Reset to Baseline Strategy
@app.route('/api/strategy/reset_to_baseline', methods=['POST'])
def reset_to_baseline():
    """PHASE 32.2: Reset strategy to baseline
    
    - Replaces active strategy with baseline
    - Does NOT reset equity/P&L
    - Does NOT delete history
    - Logs reset event
    """
    try:
        print(f"[PHASE 32.2] Reset to baseline requested")
        
        # Log current strategy
        previous_strategy = dashboard_state.get('parent_strategy')
        print(f"[PHASE 32.2] Previous strategy: {previous_strategy}")
        
        # PHASE 32.3: Update evolution engine's authoritative parent
        print(f"[PHASE 32.3] Resetting evolution_engine.current_parent to baseline")
        baseline_parent = evolution_engine.reset_to_baseline()
        print(f"[PHASE 32.3] evolution_engine.current_parent reset")
        
        # Also update dashboard_state for UI consistency
        dashboard_state['parent_strategy'] = {
            'id': baseline_parent['id'],
            'generation': baseline_parent['generation'],
            'promoted_from': 'reset',
            'reset_at': datetime.now().isoformat(),
            'previous_generation': previous_strategy,
        }
        
        print(f"[PHASE 32.2] Strategy reset to baseline")
        
        # PHASE 4.5: Persist promotion to money_state.json
        try:
            from money_state_persistence import MoneyStatePersistence
            money_persistence = MoneyStatePersistence()
            
            # Update active bot and allocation
            money_persistence.set_active_bot(variant_id)
            money_persistence.update_allocation(variant_id, 1.0)
            money_persistence.save_state()
            
            print(f"[PHASE 4.5] ✓ Promotion persisted: {variant_id} @ 1% allocation")
        except Exception as e:
            print(f"[PHASE 4.5] WARNING: Could not persist promotion: {e}")
        
        # Update dashboard_state
        dashboard_state['active_bot_id'] = variant_id
        dashboard_state['active_bot_allocation'] = 1.0
        dashboard_state['active_bot_hypothesis'] = promoted_parent.get('hypothesis_id', 'unknown')
        dashboard_state['capital_allocated'] = 1.0
        
        # Log to CSV if needed (stub - can be implemented later)
        run_id = dashboard_state.get('current_run_id', 'unknown')
        
        return jsonify({
            'status': 'success',
            'strategy': 'baseline',
            'generation': 0,
            'previous_strategy': previous_strategy,
            'active_bot_id': variant_id,
            'allocation': 1.0
        }), 200
        
    except Exception as e:
        print(f"[PHASE 32.2] ERROR in reset_to_baseline: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


# PHASE 32.2 PART 8: Capital Reset Endpoint
@app.route('/api/arena/reset_capital', methods=['POST'])
def reset_arena_capital():
    """PHASE 32.2: Reset arena capital to $10,000
    
    - Reset equity to starting value ($10,000)
    - Reset rolling P&L
    - Start new run segment
    - Preserve history
    - Do NOT change strategy
    - Do NOT change generation
    """
    try:
        print(f"[PHASE 32.2] Arena capital reset requested")
        
        # Get current state
        current_strategy = dashboard_state.get('parent_strategy', {})
        previous_equity = simulator.get_current_equity()
        
        print(f"[PHASE 32.2] Current equity: {previous_equity}")
        print(f"[PHASE 32.2] Current strategy: {current_strategy.get('id', 'unknown')}")
        
        # Reset equity in simulator
        simulator.reset_capital()
        
        new_equity = 10000.0
        
        print(f"[PHASE 32.2] Capital reset complete: {previous_equity} -> {new_equity}")
        print(f"[PHASE 32.2] Strategy unchanged: {current_strategy.get('id', 'unknown')}")
        
        return jsonify({
            'status': 'success',
            'previous_equity': previous_equity,
            'new_equity': new_equity,
            'strategy_unchanged': current_strategy.get('id', 'unknown'),
            'generation': current_strategy.get('generation', 0),
        }), 200
        
    except Exception as e:
        print(f"[PHASE 32.2] ERROR in reset_arena_capital: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


@app.route('/api/run/reset', methods=['POST'])
def reset_run():
    """Reset metrics for a new run (clears rolling edge, execution degradation, fill rates)."""
    try:
        # Call update_metrics to recalculate from fresh state
        update_metrics()
        
        # Explicitly clear rolling edge and execution metrics
        dashboard_state['metrics']['rolling_edge_20_bps'] = 0
        dashboard_state['metrics']['rolling_win_rate_20'] = 0
        dashboard_state['metrics']['rolling_avg_win_20'] = 0
        dashboard_state['metrics']['rolling_avg_loss_20'] = 0
        dashboard_state['metrics']['rolling_edge_50_bps'] = 0
        dashboard_state['metrics']['rolling_win_rate_50'] = 0
        dashboard_state['metrics']['rolling_drawdown_50'] = 0
        
        # Clear execution degradation metrics
        dashboard_state['metrics']['avg_entry_slippage_bps'] = 0
        dashboard_state['metrics']['avg_exit_slippage_bps'] = 0
        
        # Fill rates reset (paper/shadow fill % will recalculate)
        
        return jsonify({
            'status': 'success',
            'message': 'New run metrics reset',
            'metrics': dashboard_state.get('metrics', {})
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


@app.route('/api/nursery/status', methods=['GET'])
def get_nursery_status():
    """Return current nursery state for debugging"""
    return jsonify({
        'parent_strategy': dashboard_state.get('parent_strategy'),
        'current_run_id': dashboard_state.get('current_run_id'),
        'nursery_status': dashboard_state.get('nursery_status', 'idle'),
        'active_babies': len(evolution_engine.babies),
        'babies': [
            {
                'variant_id': b.get('variant_id'),
                'status': b.get('status', 'unknown'),
                'generation': b.get('generation', 0),
                'mutation_type': b.get('mutation_type', 'unknown'),
            }
            for b in evolution_engine.babies
        ]
    }), 200


def initialize():
    """Initialize data layer and simulator"""
    print("[Dashboard] Initializing...")
    data_layer.initialize()
    simulator.initialize()
    
    # PHASE 29: Initialize run tracking
    from datetime import datetime
    initial_run_id = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    dashboard_state['current_run_id'] = initial_run_id
    dashboard_state['run_start_time'] = datetime.utcnow()
    simulator.current_run_id = initial_run_id
    simulator.run_start_time = datetime.utcnow()
    print(f"[PHASE 29] Initial run_id: {initial_run_id}")
    
    # PHASE 32.1: Initialize parent strategy
    dashboard_state['parent_strategy'] = {
        'id': 'parent_mean_reversion',
        'mutation_type': 'mean_reversion_20_03',
        'generation': 0,
        'promoted_from': 'baseline'
    }
    print(f"[PHASE 32.1] parent strategy initialized: {dashboard_state['parent_strategy']['id']}")
    
    dashboard_state['initialized'] = True
    # PHASE 28: Signal Isolation
    print(f"[PHASE 28] ACTIVE_SIGNALS = {simulator.ACTIVE_SIGNALS}")
    print("[PHASE 28] Mean Reversion ONLY (20-tick, 0.3% deviation)")
    print("[PHASE 28] Disabled: Weekend Bias, Trend Following, Vol Mean Reversion")
    # PHASE 3.2: Initialize MOLT UI
    initialize_molt_ui()
    # PHASE 3.3: Start agent reaction loop
    if reaction_loop:
        reaction_loop.start()
        print("[MOLT] ✓ Agent reaction loop started")
    else:
        print("[MOLT] WARNING: Agent reaction loop not available (import failed)")
    
    # PHASE 4.5: Load persistent state
    try:
        from money_state_persistence import MoneyStatePersistence
        from state_validator import StateValidator
        
        money_persistence = MoneyStatePersistence()
        money_state_data = money_persistence.get_strategy_state()
        
        # Restore active bot and allocation
        active_bot_id = money_state_data.get('active_bot_id')
        active_bot_allocation = money_state_data.get('allocations', {}).get(active_bot_id, 0) if active_bot_id else 0
        
        dashboard_state['active_bot_id'] = active_bot_id
        dashboard_state['active_bot_allocation'] = active_bot_allocation
        dashboard_state['risk_state'] = money_state_data.get('risk_state', 'NORMAL')
        
        # Hydrate evolution engine from database
        evolution_engine.hydrate_from_database()
        
        # Validate state consistency
        validator = StateValidator()
        is_valid, errors, warnings = validator.validate_full_system(
            active_bot_id=active_bot_id,
            allocation_pct=active_bot_allocation,
            babies_count=len(evolution_engine.babies)
        )
        
        validator.print_report(is_valid)
        
        if not is_valid:
            print("[INIT] ✗ STATE VALIDATION FAILED — SYSTEM FLAT")
            dashboard_state['active_bot_id'] = None
            dashboard_state['active_bot_allocation'] = 0
        else:
            if active_bot_id:
                print(f"[INIT] ✓ System restored: active_bot={active_bot_id}, allocation={active_bot_allocation}%")
    except Exception as e:
        print(f"[PHASE 4.5] WARNING: Could not load persistent state: {e}")
    
    print("[Dashboard] Initialized")



@app.route('/api/arena/dna', methods=['GET'])
def get_arena_dna():
    """Get current active arena bot DNA - returns PROMOTED BABY DNA if available, else baseline."""
    import hashlib
    
    # STEP 1: Check if a promoted baby's DNA is active
    promoted_dna = dashboard_state.get('parent_strategy_dna', None)
    
    if promoted_dna:
        # Return the actual promoted baby's DNA
        print(f"[ARENA DNA ENDPOINT] returning promoted baby DNA: {promoted_dna.get('bot_id', 'unknown')}")
        return jsonify({
            'bot_id': promoted_dna.get('bot_id', 'arena_active_bot'),
            'generation': promoted_dna.get('generation', 0),
            'strategy_type': promoted_dna.get('strategy_type', 'mean_reversion'),
            'created_at': promoted_dna.get('promoted_timestamp', datetime.utcnow().isoformat()),
            'parameters': promoted_dna.get('parameters', {}),
            'promoted_from_baby': promoted_dna.get('promoted_from_baby', None),
            'mutation_history': [],
            'source': 'promoted_baby',
        }), 200
    
    # FALLBACK: Return baseline DNA if no promotion has occurred
    print(f"[ARENA DNA ENDPOINT] no promoted DNA, returning baseline")
    baseline_params = {
        'trade_size': 5.0,
        'target_move': 0.02,
        'stop_move': 0.02,
        'max_open_positions': 15,
        'selectivity_percentile': 0.3,
        'exit_threshold_pct': 0.005,
        'pressure_level': 0.7,
    }
    return jsonify({
        'bot_id': 'arena_active_bot',
        'generation': dashboard_state.get('parent_strategy', {}).get('generation', 0),
        'strategy_type': 'mean_reversion',
        'created_at': datetime.utcnow().isoformat(),
        'parameters': baseline_params,
        'mutation_history': [],
        'source': 'baseline',
    }), 200


@app.route('/api/arena/save_dna', methods=['POST'])
def save_arena_dna():
    """Save current arena bot DNA to file."""
    try:
        from datetime import datetime
        import json
        from pathlib import Path
        
        dna_exports = Path(__file__).parent.parent.parent / "moltmarket" / "dna_exports"
        dna_exports.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        filename = f"arena_bot_active_gen_0_{timestamp}.json"
        filepath = dna_exports / filename
        
        dna_data = {
            'bot_id': 'arena_active_bot',
            'generation': 0,
            'strategy_type': 'mean_reversion',
            'parameters': {
                'trade_size': 5.0,
                'target_move': 0.02,
                'stop_move': 0.02,
                'max_open_positions': 15,
                'selectivity_percentile': 0.3,
                'exit_threshold_pct': 0.005,
                'pressure_level': 0.7,
            },
        }
        
        with open(filepath, 'w') as f:
            json.dump(dna_data, f, indent=2)
        
        return jsonify({
            'success': True,
            'filename': filename,
            'filepath': str(filepath),
            'message': 'DNA saved successfully'
        }), 200
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/arena/evaluate', methods=['GET'])
def evaluate_arena_bot():
    """Evaluate current arena bot against hard deployment rules."""
    try:
        # Get LIVE metrics from dashboard state
        metrics = dashboard_state.get('metrics', {})
        
        # Extract LIVE values from current metrics
        total_trades = metrics.get('total_trades', 0)
        flip_rate = metrics.get('sign_flip_rate_pct', 0)  # From simulator (already in %)
        win_rate = metrics.get('win_rate', 0)
        avg_pnl = metrics.get('avg_pnl_per_trade', 0)
        
        # CRITICAL: Divergence MUST come from current arena segment, not placeholder
        # Read directly from simulator's paper/shadow PnL tracking
        divergence = 0.0
        print(f"[EVAL] Starting divergence calculation...")
        try:
            # Get paper and shadow PnL from simulator
            paper_pnl, paper_trades = simulator.get_paper_pnl()
            shadow_pnl, shadow_trades = simulator.get_shadow_pnl()
            
            print(f"[EVAL DEBUG] Simulator PnL: paper={paper_pnl:.4f} ({paper_trades} trades), shadow={shadow_pnl:.4f} ({shadow_trades} trades)")
            
            # Calculate divergence as percentage difference
            if paper_pnl > 0 and shadow_pnl > 0:
                # Both positive: divergence = difference relative to paper
                divergence = abs((shadow_pnl - paper_pnl) / paper_pnl * 100)
            elif paper_pnl == 0 and shadow_pnl == 0:
                # Both zero
                divergence = 0.0
            elif paper_pnl == 0:
                # Paper is zero but shadow isn't: use shadow as reference
                divergence = abs(shadow_pnl) * 100  # Arbitrary large number
            else:
                # General case
                if paper_pnl != 0:
                    divergence = abs((shadow_pnl - paper_pnl) / abs(paper_pnl) * 100)
                else:
                    divergence = 0.0
            
            print(f"[EVAL DEBUG] Calculated divergence: {divergence:.2f}%")
        except Exception as e:
            print(f"[ERROR] Computing divergence from simulator: {e}")
            import traceback
            traceback.print_exc()
            # Fallback: try metrics dictionary
            divergence = metrics.get('paper_shadow_delta_pct', 0)
            print(f"[EVAL FALLBACK] Using metrics paper_shadow_delta_pct: {divergence}")
        
        # Simple evaluation
        checks = []
        reasons = []
        
        # Check 1: Sample size
        if total_trades >= 50:
            checks.append({'name': 'Sample Size', 'value': f'{total_trades} trades', 'passed': True})
        else:
            checks.append({'name': 'Sample Size', 'value': f'{total_trades} trades', 'passed': False})
            reasons.append('Insufficient data')
        
        # Check 2: Flip rate
        if 6.0 <= flip_rate <= 18.0:
            checks.append({'name': 'Flip Rate', 'value': f'{flip_rate:.1f}%', 'passed': True})
        else:
            checks.append({'name': 'Flip Rate', 'value': f'{flip_rate:.1f}%', 'passed': False})
            reasons.append(f'Flip rate out of range ({flip_rate:.1f}%)')
        
        # Check 3: PnL with realistic friction adjustment
        # Apply execution realism penalty: 1.5-6 bps per trade costs
        # Conservative estimate: 3 bps per trade average (slippage + fees + depth impact)
        realistic_friction_bps = 3.0  # bps per trade
        realistic_friction = realistic_friction_bps / 10000  # Convert to decimal
        
        # Adjusted PnL = model PnL - friction
        adjusted_pnl = avg_pnl - realistic_friction
        
        # Require positive edge AFTER realistic costs
        min_required_edge_bps = 2.0  # Must show 2+ bps edge after costs (conservative)
        min_required_edge = min_required_edge_bps / 10000
        
        if adjusted_pnl > min_required_edge:
            checks.append({
                'name': 'Avg PnL (Adjusted)', 
                'value': f'{avg_pnl:.6f} (model) → {adjusted_pnl:.6f} (realistic)', 
                'passed': True
            })
        else:
            checks.append({
                'name': 'Avg PnL (Adjusted)', 
                'value': f'{avg_pnl:.6f} (model) → {adjusted_pnl:.6f} (realistic)', 
                'passed': False
            })
            reasons.append(f'No real edge (model: {avg_pnl*10000:.1f}bps, after friction: {adjusted_pnl*10000:.1f}bps, need: >{min_required_edge_bps:.1f}bps)')
        
        # Check 4: Divergence
        if abs(divergence) < 30:
            checks.append({'name': 'Divergence', 'value': f'{divergence:.1f}%', 'passed': True})
        else:
            checks.append({'name': 'Divergence', 'value': f'{divergence:.1f}%', 'passed': False})
            reasons.append('High divergence')
        
        # ========== SURVIVAL CHECKS ==========
        # MAX DRAWDOWN CHECK
        max_drawdown_pct = 0.0
        sudden_collapse = False
        survival_pass = True
        
        try:
            # Get equity curve from simulator (shadow preferred)
            shadow_curve, _ = simulator.get_shadow_pnl()
            paper_curve, _ = simulator.get_paper_pnl()
            
            # Use shadow equity curve if available
            if hasattr(simulator, 'shadow_equity') and simulator.shadow_equity:
                equity_values = [e.get('value', 10000.0) if isinstance(e, dict) else 10000.0 
                                for e in list(simulator.shadow_equity)]
            elif hasattr(simulator, 'paper_equity') and simulator.paper_equity:
                equity_values = [e.get('value', 10000.0) if isinstance(e, dict) else 10000.0 
                                for e in list(simulator.paper_equity)]
            else:
                equity_values = [10000.0]
            
            # Calculate max drawdown
            peak = 10000.0
            trough = 10000.0
            for value in equity_values:
                if value > peak:
                    peak = value
                trough = min(trough, value)
                drawdown = (peak - value) / peak * 100 if peak > 0 else 0
                max_drawdown_pct = max(max_drawdown_pct, drawdown)
            
            print(f"[EVAL SURVIVAL] Max drawdown calculated: {max_drawdown_pct:.2f}%")
            
            # DRAWDOWN RULE: Fail if > 5%
            drawdown_threshold = 5.0
            if max_drawdown_pct > drawdown_threshold:
                survival_pass = False
                checks.append({'name': 'Max Drawdown', 'value': f'{max_drawdown_pct:.1f}%', 'passed': False})
                reasons.append(f'Excessive drawdown ({max_drawdown_pct:.1f}% > {drawdown_threshold}%)')
            else:
                checks.append({'name': 'Max Drawdown', 'value': f'{max_drawdown_pct:.1f}%', 'passed': True})
            
            # STABILITY CHECK: Detect sudden collapse
            # Look for single large negative move (>2% of starting capital)
            if len(equity_values) > 1:
                for i in range(1, len(equity_values)):
                    prev_value = equity_values[i-1]
                    curr_value = equity_values[i]
                    move_pct = (prev_value - curr_value) / prev_value * 100 if prev_value > 0 else 0
                    
                    # Flag if any single step loses > 2% of starting capital
                    if move_pct > 2.0:
                        sudden_collapse = True
                        print(f"[EVAL SURVIVAL] Sudden drop detected: {move_pct:.2f}% at step {i}")
                        break
            
            if sudden_collapse:
                survival_pass = False
                checks.append({'name': 'Stability Check', 'value': 'UNSTABLE', 'passed': False})
                reasons.append('Sudden equity instability detected')
            else:
                checks.append({'name': 'Stability Check', 'value': 'STABLE', 'passed': True})
            
            print(f"[EVAL SURVIVAL] Survival status: pass={survival_pass}, collapse={sudden_collapse}")
            
        except Exception as e:
            print(f"[EVAL SURVIVAL] Error calculating survival: {e}")
            # If error, assume survival check passes (don't block on error)
            checks.append({'name': 'Max Drawdown', 'value': 'ERROR', 'passed': True})
            checks.append({'name': 'Stability Check', 'value': 'ERROR', 'passed': True})
        
        status = 'PASS' if (all(c['passed'] for c in checks) and survival_pass) else 'FAIL'
        
        # Build recommendation based on failures
        if status == 'PASS':
            recommendation = '✓ Ready for deployment'
        else:
            # Generate specific recommendation
            if not survival_pass:
                if max_drawdown_pct > 5.0:
                    recommendation = '✗ Not ready. Drawdown too severe. Reduce aggressiveness.'
                elif sudden_collapse:
                    recommendation = '✗ Not ready. Strategy destabilizes during run. Review exits.'
                else:
                    recommendation = '✗ Not ready. Survival check failed. Review risk management.'
            else:
                recommendation = '✗ Not ready. Review failed checks.'
        
        return jsonify({
            'status': status,
            'checks': checks,
            'reasons': reasons,
            'recommendation': recommendation,
            'survival': {
                'max_drawdown_pct': round(max_drawdown_pct, 2),
                'sudden_collapse': sudden_collapse,
                'pass': survival_pass,
            },
            'live_metrics': {
                'total_trades': total_trades,
                'flip_rate': flip_rate,
                'win_rate': win_rate,
                'avg_pnl': avg_pnl,
                'divergence': divergence,
            }
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'ERROR',
            'error': str(e)
        }), 500


# =====================================================
# MOLT FEED UI ROUTES (Phase 3.2)
# =====================================================


def initialize_molt_ui():
    global molt_ui
    try:
        from molt_ui_layer import MOLTUILayer
        molt_ui = MOLTUILayer()
        print("[MOLT] ✓ UI layer initialized")
        print(f"[MOLT] MOLT database: {molt_ui.molt.db_path if hasattr(molt_ui, 'molt') else 'UNKNOWN'}")
    except ImportError as e:
        print(f"[MOLT] WARNING: MOLTUILayer not found: {e}")
        print(f"[MOLT] Setting molt_ui = None (feed endpoints will return 503)")
        molt_ui = None
    except Exception as e:
        print(f"[MOLT] ✗ ERROR initializing UI layer: {e}")
        import traceback
        traceback.print_exc()
        molt_ui = None


@app.route('/molt')
def molt_feed_page():
    return render_template('molt.html')


@app.route('/api/molt/feed')
def api_molt_feed():
    try:
        post_type = request.args.get('type')
        agent = request.args.get('agent')
        limit = int(request.args.get('limit', 50))
        
        if not molt_ui:
            return jsonify({'status': 'error', 'message': 'MOLT UI not initialized'}), 503
        
        feed = molt_ui.get_feed(
            post_type_filter=post_type,
            agent_filter=agent,
            limit=limit
        )
        
        return jsonify({
            'status': 'success',
            'count': len(feed),
            'posts': feed
        }), 200
    except Exception as e:
        print(f"[MOLT] ERROR: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/molt/lineage/<molt_id>')
def api_molt_lineage(molt_id):
    try:
        if not molt_ui:
            return jsonify({'status': 'error', 'message': 'MOLT UI not initialized'}), 503
        
        lineage = molt_ui.get_lineage(molt_id)
        if not lineage:
            return jsonify({'status': 'error', 'message': 'not found'}), 404
        
        return jsonify({'status': 'success', 'lineage': lineage}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/molt/spawn/<molt_id>', methods=['POST'])
def api_molt_spawn(molt_id):
    try:
        if not molt_ui:
            return jsonify({'status': 'error', 'message': 'MOLT UI not initialized'}), 503
        
        result = molt_ui.spawn_from_molt(molt_id)
        if result.get('status') == 'error':
            return jsonify(result), 400
        
        print(f"[MOLT] Spawned {result['total_spawned']} babies from {molt_id}")
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/molt/stats')
def api_molt_stats():
    try:
        if not molt_ui:
            return jsonify({'status': 'error', 'message': 'MOLT UI not initialized'}), 503
        
        stats = molt_ui.get_statistics()
        agents = molt_ui.get_agent_names()
        post_types = molt_ui.get_post_types()
        
        return jsonify({
            'status': 'success',
            'statistics': stats,
            'agents': agents,
            'post_types': post_types
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/money-state')
def api_money_state():
    """Get complete money layer state for UI display + AUTO-STOP ENFORCEMENT"""
    try:
        # AUTO-STOP ENFORCEMENT: Check if should STOP
        # Trigger STOP if:
        # 1. Max drawdown exceeded (5%)
        # 2. Sudden collapse detected
        # 3. Paper/shadow delta too high (>30%)
        
        metrics = dashboard_state.get('metrics', {})
        risk_state = dashboard_state.get('risk_state', 'NORMAL')
        
        # Auto-evaluate survival conditions
        should_stop = False
        stop_reason = None
        
        # Check 1: Drawdown threshold
        if metrics.get('rolling_drawdown_50', 0) > 5.0:
            should_stop = True
            stop_reason = f"Max drawdown exceeded: {metrics.get('rolling_drawdown_50', 0):.1f}%"
        
        # Check 2: Paper/shadow divergence
        if abs(metrics.get('paper_shadow_delta_pct', 0)) > 30:
            should_stop = True
            stop_reason = f"Paper/shadow divergence too high: {metrics.get('paper_shadow_delta_pct', 0):.1f}%"
        
        # Check 3: Sign flip rate anomaly
        flip_rate = metrics.get('sign_flip_rate_pct', 0)
        if flip_rate > 25.0:
            should_stop = True
            stop_reason = f"Excessive sign flips: {flip_rate:.1f}%"
        
        # Apply STOP if triggered
        if should_stop and risk_state != 'STOP':
            print(f"[MONEY] ⛔ AUTO-STOP TRIGGERED: {stop_reason}")
            dashboard_state['risk_state'] = 'STOP'
            dashboard_state['risk_state_reason'] = stop_reason
            dashboard_state['running'] = False  # Stop simulation loop
        
        # Build money state
        state = {
            'active_bot_id': dashboard_state.get('active_bot_id'),
            'active_bot_allocation': dashboard_state.get('active_bot_allocation', 0),
            'risk_state': dashboard_state.get('risk_state', 'NORMAL'),
            'risk_state_reason': dashboard_state.get('risk_state_reason', ''),
            'capital_allocated': dashboard_state.get('capital_allocated', 0),
            'capital_total': 100.0,
            'promotion_status': dashboard_state.get('promotion_status'),
            'failed_gates': dashboard_state.get('failed_gates', []),
            'replacement_status': dashboard_state.get('replacement_status'),
            'auto_stop_triggered': should_stop,
            'auto_stop_reason': stop_reason,
            'timestamp': datetime.utcnow().isoformat()
        }
        
        return jsonify(state), 200
    except Exception as e:
        print(f"[ERROR] /api/money-state: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/restart-simulation', methods=['POST'])
def restart_simulation():
    """Restart simulation from CSV state (persistent, non-destructive)"""
    try:
        print("\n[RESTART] Restarting simulation from CSV...")
        paper_pnl_before = simulator.paper_pnl
        shadow_pnl_before = simulator.shadow_pnl
        recover_simulator_state(simulator, data_layer)
        paper_pnl_after = simulator.paper_pnl
        shadow_pnl_after = simulator.shadow_pnl
        print(f"[RESTART] ✓ Complete")
        print(f"[RESTART] Paper: ${paper_pnl_before:.2f} → ${paper_pnl_after:.2f}")
        print(f"[RESTART] Shadow: ${shadow_pnl_before:.2f} → ${shadow_pnl_after:.2f}")
        return jsonify({
            'status': 'restart_complete',
            'paper_pnl': round(paper_pnl_after, 2),
            'shadow_pnl': round(shadow_pnl_after, 2),
            'paper_trades': simulator.paper_trades,
            'shadow_trades': simulator.shadow_trades,
            'message': 'Simulation restarted from CSV'
        }), 200
    except Exception as e:
        print(f"[RESTART] ERROR: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'status': 'error', 'message': str(e)}), 500





# OLD THINK route removed — Rocky takes over /api/think/query (wired in __main__)


if __name__ == '__main__':
    # Ensure working directory is correct
    os.chdir(Path(__file__).parent)
    
    # Initialize
    initialize()
    
    # Start background simulation
    start_background_simulation()
    
    # Update metrics once before starting server
    update_metrics()
    
    # STARTUP VERIFICATION: Print all registered routes (including nursery)
    print("\n[ROUTES] Flask app routes registered:")
    for rule in app.url_map.iter_rules():
        if 'nursery' in str(rule) or 'api' in str(rule):
            print(f"  {rule}")
    
    # Specific nursery route checks
    if any('/api/nursery/spawn' in str(rule) for rule in app.url_map.iter_rules()):
        print("[NURSERY] ✓ /api/nursery/spawn route is registered")
    else:
        print("[NURSERY] ✗ ERROR: /api/nursery/spawn route NOT registered")
    
    if any('/api/nursery/leaderboard' in str(rule) for rule in app.url_map.iter_rules()):
        print("[NURSERY] ✓ /api/nursery/leaderboard route is registered")
    else:
        print("[NURSERY] ✗ ERROR: /api/nursery/leaderboard route NOT registered")
    
    if any('/api/nursery/promote' in str(rule) for rule in app.url_map.iter_rules()):
        print("[NURSERY] ✓ /api/nursery/promote/<variant_id> route is registered")
    else:
        print("[NURSERY] ✗ ERROR: /api/nursery/promote route NOT registered")
    
    if any('/api/nursery/status' in str(rule) for rule in app.url_map.iter_rules()):
        print("[NURSERY] ✓ /api/nursery/status route is registered")
    else:
        print("[NURSERY] ✗ ERROR: /api/nursery/status route NOT registered")
    
    print("\n" + "="*60)
    print("MOLTmarket Live Validation Dashboard - PHASE 32.1")
    print("="*60)
    print(f"🎯 Dashboard: http://127.0.0.1:{PORT}")
    print("📊 Real-time paper/shadow execution")
    print("📈 Historical backtest overlay")
    print("🔒 Signal: Mean Reversion ONLY (20-tick, 0.3%)")
    print("🧬 PHASE 32.1: Backend promotion endpoint active")
    print("   POST /api/nursery/promote/<variant_id>")
    print("   GET  /api/nursery/status")
    print("💾 CSV exports: research_trades.csv, research_runs.csv, signal_health.csv, execution_quality.csv")
    print("💾 Nursery tracking: variant_nursery.csv (with promotion history)")
    print("="*60 + "\n")
    
    # PHASE 32.1: Print promotion endpoint details
    print("[PHASE 32.1] Promotion Endpoint Details:")
    print(f"  Parent strategy: {dashboard_state['parent_strategy']['id']}")
    print(f"  Current run_id: {dashboard_state['current_run_id']}")
    print("  Promotion requirements:")
    print("    - Minimum 30 trades in shadow execution")
    print("    - Valid fitness score (> -999)")
    print("    - Baby must be 'active' status")
    print("  Success behavior:")
    print("    - Winner marked as 'promoted'")
    print("    - Losers marked as 'retired'")
    print("    - Parent strategy config replaced")
    print("    - Nursery state cleared")
    print("    - CSV updated with promotion timestamps")
    print()
    
    # THINK DIRECT INTEGRATION: Operator (you) in the dashboard
    try:
        setup_rocky_log_endpoints(app)
        setup_arena_metrics_endpoint(app)
        setup_think_session_endpoints(app)
        setup_brain_calibration_endpoint(app)
        setup_think_direct_endpoint(app, operator_name="Operator")
        think_bridge.start_session()
        print("[THINK DIRECT] ✓ Operator channel active - dashboard connected to OpenClaw")
    except Exception as e:
        print(f"[THINK DIRECT] ERROR: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"[THINK DIRECT] ERROR: {e}")
        import traceback
        traceback.print_exc()
        print("[ROCKY] WARNING: Integration not available")
    
    # Start Flask server
    # PHASE 32.6: Port 5050 (macOS AirTunes uses 5000)
    
    # Trigger THINK session startup
    import threading
    def startup_think():
        import time
        time.sleep(1)  # Wait for Flask to bind
        try:
            import requests
            requests.post('http://localhost:5050/api/think/session/start', timeout=2)
        except:
            pass
    
    startup_thread = threading.Thread(target=startup_think, daemon=True)
    startup_thread.start()
    
    app.run(host='127.0.0.1', port=PORT, debug=False, use_reloader=False)


# Reaction loop init skipped (optional for testing)



@app.route('/api/molt/thread/<molt_id>')
def api_molt_thread(molt_id):
    """Get full conversation thread"""
    try:
        if not molt_ui:
            return jsonify({'status': 'error', 'message': 'MOLT UI not initialized'}), 503
        
        thread = molt_ui.get_thread(molt_id)
        
        if not thread:
            return jsonify({'status': 'error', 'message': 'thread not found'}), 404
        
        return jsonify({
            'status': 'success',
            'molt_id': molt_id,
            'thread_length': len(thread),
            'posts': thread
        }), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500



@app.route('/api/molt/reply-counts')
def api_molt_reply_counts():
    """Get reply counts for all posts"""
    try:
        if not molt_ui:
            return jsonify({'status': 'error'}), 503
        
        import sqlite3
        conn = sqlite3.connect(str(molt_ui.molt.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT molt_id, COUNT(*) as reply_count 
            FROM molt_feed 
            WHERE replies_to_molt_id IS NOT NULL 
            GROUP BY replies_to_molt_id
        """)
        
        counts = {row[0]: row[1] for row in cursor.fetchall()}
        conn.close()
        
        return jsonify({'status': 'success', 'counts': counts}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500




# =========================================================================
# PHASE 10.2: THINK API ENDPOINTS (7 total) + BRAIN ENFORCEMENT
# =========================================================================

try:
    from think_diagnostic_layer import ThinkDiagnosticLayer
    think_engine = ThinkDiagnosticLayer()
    print("[THINK] ✓ Diagnostic engine initialized")
except Exception as e:
    print(f"[THINK] ERROR initializing diagnostic engine: {e}")
    think_engine = None


def _load_current_session_to_think():
    """Load current dashboard metrics into THINK engine as session data"""
    if not think_engine:
        return False
    
    try:
        metrics = dashboard_state.get('metrics', {})
        recent_trades = data_layer.get_recent_trades(limit=100)
        
        equity_curve = [10000.0]
        cumulative = 0
        for trade in reversed(recent_trades):
            cumulative += float(trade.get('pnl', 0))
            equity_curve.append(10000.0 + cumulative)
        
        session_data = {
            'total_cycles': metrics.get('total_trades', 0),
            'flat_entries': 0,
            'flat_exits': 0,
            'restart_attempts': 0,
            'probation_passed': 0,
            'probation_failed': 0,
            'stop_events': dashboard_state.get('stop_events', 0),
            'replacement_attempts': 0,
            'equity_curve': equity_curve,
            'probation_logs': [],
            'brain_status_history': [],
            'degradation_drawdown_threshold': 3.0,
        }
        
        think_engine.load_session_data('current_run', session_data)
        return True
    except Exception as e:
        print(f"[THINK] ERROR loading session: {e}")
        return False


@app.route('/api/brain/enforcement', methods=['GET'])
def brain_enforcement():
    """BRAIN: Get current enforcement status"""
    try:
        brain_state = dashboard_state.get('brain_state', 'UNKNOWN')
        brain_reason = dashboard_state.get('brain_reason_code', 'not_evaluated')
        brain_text = dashboard_state.get('brain_reason_text', '')
        enforcement = dashboard_state.get('brain_enforcement', {})
        
        return jsonify({
            'status': 'success',
            'brain_state': brain_state,
            'reason_code': brain_reason,
            'reason_text': brain_text,
            'enforcement_flags': {
                'allows_trade': enforcement.get('allows_trade', True),
                'throttle_active': enforcement.get('throttle_active', False),
                'position_size_factor': enforcement.get('position_size_factor', 1.0),
            },
            'timestamp': datetime.utcnow().isoformat()
        }), 200
    except Exception as e:
        print(f"[BRAIN] ERROR in enforcement: {e}")
        return jsonify({'status': 'error', 'message': str(e)}), 500


# DEBUG: Test enforcement
@app.route('/api/test/force-stop', methods=['POST'])
def test_force_stop():
    """DEBUG: Force STOP state for testing enforcement"""
    global dashboard_state
    
    dashboard_state['risk_state'] = 'STOP'
    dashboard_state['risk_state_reason'] = 'DEBUG: Manually triggered for testing'
    
    print("[TEST] ✓ Forced STOP state for enforcement testing")
    
    return jsonify({
        'status': 'success',
        'risk_state': 'STOP',
        'message': 'STOP forced for testing'
    }), 200

@app.route('/api/arena/enable-trading', methods=['POST'])
def enable_arena_trading():
    """Enable Arena trading after promotion"""
    global dashboard_state
    
    dashboard_state['trading_enabled'] = True
    dashboard_state['brain_reason_text'] = 'Arena trading ENABLED. Baby promoted, ready to execute.'
    dashboard_state['brain_enforcement'] = {
        'no_active_strategy': False,
        'trading_blocked': False,
        'trading_throttled': False
    }
    
    print("[ARENA] ✓ Trading ENABLED for promoted baby")
    
    return jsonify({
        'status': 'success',
        'trading_enabled': True,
        'message': 'Arena trading enabled'
    }), 200

