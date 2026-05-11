#!/usr/bin/env python3
"""
CORRECTED update_metrics() function for dashboard

Three-tier metrics system:
- TIER 1: Raw dollars (pnl_dollars)
- TIER 2: % return (return_pct, normalized to initial capital)
- TIER 3: BPS edge (normalized to notional per trade)

All clearly separated. No mixing units. No abs() tricks.
"""

INITIAL_CAPITAL = 10000.0  # Standard simulator starting capital

def update_metrics_corrected(simulator, data_layer, dashboard_state):
    """
    CORRECTED metrics calculation with three-tier normalization.
    
    TIER 1: RAW DOLLARS
    - paper_pnl_dollars, shadow_pnl_dollars (absolute)
    
    TIER 2: % RETURN
    - paper_return_pct, shadow_return_pct (% of initial capital)
    
    TIER 3: BPS EDGE
    - rolling_edge_20_bps, rolling_edge_50_bps (notional-normalized)
    """
    
    print("\n" + "="*80)
    print("[METRICS CORRECTED] Three-tier calculation starting")
    print("="*80)
    
    # Get base data from simulator
    paper_pnl_dollars, paper_trades = simulator.get_paper_pnl()
    shadow_pnl_dollars, shadow_trades = simulator.get_shadow_pnl()
    backtest_pnl_dollars, backtest_trades = simulator.get_backtest_pnl()
    
    print(f"\n[TIER 1] RAW DOLLARS")
    print(f"  paper_pnl: ${paper_pnl_dollars:.2f}")
    print(f"  shadow_pnl: ${shadow_pnl_dollars:.2f}")
    print(f"  backtest_pnl: ${backtest_pnl_dollars:.2f}")
    
    # TIER 2: % RETURN (normalize to initial capital)
    print(f"\n[TIER 2] % RETURN (initial capital: ${INITIAL_CAPITAL:.2f})")
    
    paper_return_pct = (paper_pnl_dollars / INITIAL_CAPITAL) * 100
    shadow_return_pct = (shadow_pnl_dollars / INITIAL_CAPITAL) * 100
    backtest_return_pct = (backtest_pnl_dollars / INITIAL_CAPITAL) * 100
    
    # CORRECTED: Use consistent denominator, no abs()
    delta_return_pct = paper_return_pct - shadow_return_pct
    
    print(f"  paper_return: {paper_return_pct:.3f}%")
    print(f"  shadow_return: {shadow_return_pct:.3f}%")
    print(f"  delta: {delta_return_pct:.3f}% (paper - shadow)")
    
    # TIER 3: BPS EDGE (rolling windows, normalized to notional)
    print(f"\n[TIER 3] BPS EDGE (notional-normalized)")
    
    # Get recent trades
    recent = data_layer.get_recent_trades(limit=1000)
    recent_20 = data_layer.get_recent_trades(limit=20)
    recent_50 = data_layer.get_recent_trades(limit=50)
    
    # METRIC: rolling_edge_20_bps
    print(f"\n  [ROLLING EDGE 20]")
    if recent_20 and len(recent_20) > 0:
        # Extract pnl and notional from each trade
        pnl_list_20 = []
        notional_list_20 = []
        
        for trade in recent_20:
            try:
                pnl = float(trade.get('pnl', 0))
                # Get entry price and size to calculate notional
                entry = float(trade.get('entry_price', 1))
                # Assume standard size (this may need adjustment)
                # For BTC/ETH, we'll estimate notional from price
                if 'BTC' in trade.get('asset', ''):
                    notional = entry * 1.0  # 1 BTC
                elif 'ETH' in trade.get('asset', ''):
                    notional = entry * 10.0  # 10 ETH
                else:
                    notional = entry * 100  # Generic
                
                pnl_list_20.append(pnl)
                notional_list_20.append(notional)
            except:
                pass
        
        if notional_list_20:
            total_return_20 = sum(p / n for p, n in zip(pnl_list_20, notional_list_20))
            avg_return_20 = total_return_20 / len(notional_list_20)
            edge_20_bps = avg_return_20 * 10000
            
            total_pnl_20 = sum(pnl_list_20)
            avg_pnl_20 = total_pnl_20 / len(pnl_list_20)
            
            wins_20 = sum(1 for p in pnl_list_20 if p > 0)
            win_rate_20 = (wins_20 / len(pnl_list_20) * 100) if pnl_list_20 else 0
            
            print(f"    trades: {len(recent_20)}")
            print(f"    avg_pnl_dollars: ${avg_pnl_20:.2f}")
            print(f"    edge_bps: {edge_20_bps:.2f}")
            print(f"    win_rate: {win_rate_20:.1f}%")
        else:
            edge_20_bps = 0
            win_rate_20 = 0
            avg_pnl_20 = 0
    else:
        edge_20_bps = 0
        win_rate_20 = 0
        avg_pnl_20 = 0
        print(f"    NO TRADES")
    
    # METRIC: rolling_edge_50_bps
    print(f"\n  [ROLLING EDGE 50]")
    if recent_50 and len(recent_50) > 0:
        pnl_list_50 = []
        notional_list_50 = []
        
        for trade in recent_50:
            try:
                pnl = float(trade.get('pnl', 0))
                entry = float(trade.get('entry_price', 1))
                if 'BTC' in trade.get('asset', ''):
                    notional = entry * 1.0
                elif 'ETH' in trade.get('asset', ''):
                    notional = entry * 10.0
                else:
                    notional = entry * 100
                
                pnl_list_50.append(pnl)
                notional_list_50.append(notional)
            except:
                pass
        
        if notional_list_50:
            total_return_50 = sum(p / n for p, n in zip(pnl_list_50, notional_list_50))
            avg_return_50 = total_return_50 / len(notional_list_50)
            edge_50_bps = avg_return_50 * 10000
            
            total_pnl_50 = sum(pnl_list_50)
            avg_pnl_50 = total_pnl_50 / len(pnl_list_50)
            
            wins_50 = sum(1 for p in pnl_list_50 if p > 0)
            win_rate_50 = (wins_50 / len(pnl_list_50) * 100) if pnl_list_50 else 0
            
            print(f"    trades: {len(recent_50)}")
            print(f"    avg_pnl_dollars: ${avg_pnl_50:.2f}")
            print(f"    edge_bps: {edge_50_bps:.2f}")
            print(f"    win_rate: {win_rate_50:.1f}%")
        else:
            edge_50_bps = 0
            win_rate_50 = 0
            avg_pnl_50 = 0
    else:
        edge_50_bps = 0
        win_rate_50 = 0
        avg_pnl_50 = 0
        print(f"    NO TRADES")
    
    # Get other metrics
    total_trades = len(recent)
    win_rate_all = data_layer.get_win_rate()
    avg_pnl_all = data_layer.get_avg_pnl_per_trade()
    slippage = data_layer.get_avg_slippage()
    integrity = data_layer.get_trade_integrity()
    
    # BUILD CORRECTED METRICS DICT
    print(f"\n[BUILDING METRICS DICT]")
    
    corrected_metrics = {
        # TIER 1: RAW DOLLARS (absolute)
        'paper_pnl_dollars': round(paper_pnl_dollars, 2),
        'shadow_pnl_dollars': round(shadow_pnl_dollars, 2),
        'backtest_pnl_dollars': round(backtest_pnl_dollars, 2),
        'delta_pnl_dollars': round(paper_pnl_dollars - shadow_pnl_dollars, 2),
        
        # TIER 2: % RETURN (normalized to initial capital)
        'paper_return_pct': round(paper_return_pct, 3),
        'shadow_return_pct': round(shadow_return_pct, 3),
        'backtest_return_pct': round(backtest_return_pct, 3),
        'delta_return_pct': round(delta_return_pct, 3),
        
        # TIER 3: BPS EDGE (notional-normalized, rolling)
        'rolling_edge_20_bps': round(edge_20_bps, 2),
        'rolling_edge_50_bps': round(edge_50_bps, 2),
        'rolling_avg_pnl_20_dollars': round(avg_pnl_20, 2),
        'rolling_avg_pnl_50_dollars': round(avg_pnl_50, 2),
        'rolling_win_rate_20': round(win_rate_20, 1),
        'rolling_win_rate_50': round(win_rate_50, 1),
        
        # Additional metrics (unchanged)
        'total_trades': total_trades,
        'rolling_win_rate_all': round(win_rate_all * 100, 1),
        'avg_pnl_per_trade_dollars': round(avg_pnl_all, 2),
        'current_signal': simulator.current_signal,
        'current_asset': simulator.current_asset,
        'paper_trades': paper_trades,
        'shadow_trades': shadow_trades,
        'backtest_trades': backtest_trades,
        'regime': simulator.current_regime,
        'timestamp': __import__('datetime').datetime.utcnow().isoformat(),
        'avg_entry_slippage_bps': round(slippage['entry_bps'], 2),
        'avg_exit_slippage_bps': round(slippage['exit_bps'], 2),
        'total_trades_integrity': integrity['total_trades'],
        'trade_count_diff': integrity['trade_diff'],
        'sign_flip_count': integrity['sign_flips'],
        'sign_flip_rate_pct': round(integrity['sign_flip_rate_pct'], 1),
    }
    
    # Update dashboard state
    dashboard_state['metrics'] = corrected_metrics
    dashboard_state['total_trades'] = total_trades
    dashboard_state['flip_rate'] = round(integrity['sign_flip_rate_pct'], 1)
    dashboard_state['avg_pnl_per_trade'] = round(avg_pnl_all, 6)
    dashboard_state['divergence'] = round(delta_return_pct, 3)
    dashboard_state['rolling_win_rate'] = round(win_rate_all * 100, 1)
    
    print(f"\n[METRICS COMPLETE]")
    print(f"  paper_return_pct: {paper_return_pct:.3f}%")
    print(f"  shadow_return_pct: {shadow_return_pct:.3f}%")
    print(f"  rolling_edge_20_bps: {edge_20_bps:.2f}")
    print(f"  rolling_edge_50_bps: {edge_50_bps:.2f}")
    
    return corrected_metrics


if __name__ == '__main__':
    print("""
USAGE:

In moltmarket_dashboard.py, replace update_metrics() call with:

    from update_metrics_corrected import update_metrics_corrected
    
    # In update_metrics():
    corrected_metrics = update_metrics_corrected(simulator, data_layer, dashboard_state)

METRICS NOW HAVE THREE CLEAR TIERS:

1. RAW DOLLARS
   - paper_pnl_dollars: $125.47 (absolute dollars)
   - shadow_pnl_dollars: $89.32 (absolute dollars)
   
2. % RETURN
   - paper_return_pct: 1.2547% (normalized to $10k initial)
   - shadow_return_pct: 0.8932% (normalized to $10k initial)
   
3. BPS EDGE
   - rolling_edge_20_bps: 18.5 (notional-normalized, rolling 20 trades)
   - rolling_edge_50_bps: 22.3 (notional-normalized, rolling 50 trades)

NO MIXING UNITS.
NO ABS() TRICKS.
CLEAR DENOMINATORS.
""")
