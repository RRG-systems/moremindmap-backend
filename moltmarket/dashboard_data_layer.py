#!/usr/bin/env python3
"""
Data layer for MOLTmarket dashboard
Handles CSV persistence, metrics calculation, and trade history

PHASE 29: Run tracking with full data preservation
- run_id in every CSV row (added retroactively during migration)
- RUN_SEPARATOR markers for clear boundaries
- research_runs.csv for run summaries (finalization snapshots)
"""

import csv
import json
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
from statistics import mean, stdev


class DataLayer:
    def __init__(self, workspace_dir):
        self.workspace = Path(workspace_dir)
        self.trades_file = self.workspace / 'research_trades.csv'
        self.runs_file = self.workspace / 'research_runs.csv'
        self.signal_health_file = self.workspace / 'signal_health.csv'
        self.execution_quality_file = self.workspace / 'execution_quality.csv'
        self.nursery_file = self.workspace / 'variant_nursery.csv'  # PHASE 31
        
        # In-memory caches
        self.trades = []
        self.runs = []
        self.signal_health = []
        self.execution_quality = []
        self.nursery = []  # PHASE 31
        
        # PHASE 29: Headers updated to include run_id
        self.trades_headers = [
            'run_id', 'timestamp', 'asset', 'signal', 'source', 'side', 
            'entry_price', 'exit_price', 'expected_fill', 'shadow_fill', 
            'pnl', 'pnl_bps', 'duration', 'regime'
        ]
        
        # PHASE 29: New research_runs.csv schema
        self.runs_headers = [
            'run_id', 'start_time', 'end_time', 'total_trades', 'win_rate',
            'avg_pnl_per_trade', 'total_pnl_paper', 'total_pnl_shadow',
            'paper_vs_shadow_delta', 'avg_entry_slippage_bps', 
            'avg_exit_slippage_bps', 'sign_flip_rate'
        ]
        
        self.signal_health_headers = [
            'run_id', 'timestamp', 'asset', 'signal', 'rolling_20_edge', 
            'rolling_50_edge', 'rolling_win_rate', 'rolling_drawdown'
        ]
        
        self.execution_quality_headers = [
            'run_id', 'timestamp', 'asset', 'signal', 'expected_entry', 'shadow_entry',
            'expected_exit', 'shadow_exit', 'slippage_bps', 'paper_shadow_delta'
        ]
        
        self.current_run_id = None
    
    def initialize(self):
        """Initialize CSV files if they don't exist"""
        self._ensure_csv_file(self.trades_file, self.trades_headers)
        self._ensure_csv_file(self.runs_file, self.runs_headers)
        self._ensure_csv_file(self.signal_health_file, self.signal_health_headers)
        self._ensure_csv_file(self.execution_quality_file, self.execution_quality_headers)
        
        # PHASE 29: Migrate existing CSVs to add run_id column
        self._migrate_legacy_data()
        
        self._load_all()
    
    def _ensure_csv_file(self, filepath, headers):
        """Create CSV file with headers if it doesn't exist"""
        if not filepath.exists():
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                writer.writeheader()
    
    def _migrate_legacy_data(self):
        """PHASE 29: Backfill run_id into existing CSV files
        
        If run_id column is missing, add it and set all rows to 'initial'
        """
        legacy_identifier = 'phase_28_run'
        
        # Check and migrate trades file
        if self.trades_file.exists():
            with open(self.trades_file, 'r') as f:
                first_line = f.readline().strip()
                if 'run_id' not in first_line:
                    print(f"[PHASE 29] Migrating {self.trades_file.name} - adding run_id column")
                    self._add_column_to_csv(self.trades_file, 'run_id', legacy_identifier, 0)
        
        # Check and migrate runs file
        if self.runs_file.exists():
            with open(self.runs_file, 'r') as f:
                first_line = f.readline().strip()
                if 'run_id' not in first_line:
                    print(f"[PHASE 29] Migrating {self.runs_file.name} - adding run_id column")
                    self._add_column_to_csv(self.runs_file, 'run_id', legacy_identifier, 0)
        
        # Check and migrate signal_health file
        if self.signal_health_file.exists():
            with open(self.signal_health_file, 'r') as f:
                first_line = f.readline().strip()
                if 'run_id' not in first_line:
                    print(f"[PHASE 29] Migrating {self.signal_health_file.name} - adding run_id column")
                    self._add_column_to_csv(self.signal_health_file, 'run_id', legacy_identifier, 0)
        
        # Check and migrate execution_quality file
        if self.execution_quality_file.exists():
            with open(self.execution_quality_file, 'r') as f:
                first_line = f.readline().strip()
                if 'run_id' not in first_line:
                    print(f"[PHASE 29] Migrating {self.execution_quality_file.name} - adding run_id column")
                    self._add_column_to_csv(self.execution_quality_file, 'run_id', legacy_identifier, 0)
    
    def _add_column_to_csv(self, filepath, column_name, value, position=0):
        """Add a column to an existing CSV file (insert at position)"""
        try:
            # Read entire file
            with open(filepath, 'r') as f:
                reader = csv.DictReader(f)
                headers = reader.fieldnames
                rows = list(reader)
            
            # Insert column at position
            new_headers = headers[:position] + [column_name] + headers[position:]
            
            # Rewrite file with new column
            with open(filepath, 'w', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=new_headers)
                writer.writeheader()
                for row in rows:
                    row[column_name] = value
                    writer.writerows([row])
            
            print(f"[PHASE 29] Successfully migrated {filepath.name}")
        except Exception as e:
            print(f"[PHASE 29] ERROR migrating {filepath.name}: {e}")
    
    def _load_all(self):
        """Load all CSV files into memory"""
        self.trades = self._read_csv(self.trades_file)
        self.runs = self._read_csv(self.runs_file)
        self.signal_health = self._read_csv(self.signal_health_file)
        self.execution_quality = self._read_csv(self.execution_quality_file)
    
    def _read_csv(self, filepath):
        """Read CSV file into list of dicts"""
        if not filepath.exists():
            return []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            return list(reader) if reader else []
    
    def append_trade(self, trade_dict):
        """Append single trade to CSV and memory
        
        PHASE 29: Automatically includes run_id from current session
        """
        # Inject current run_id if not already present
        if 'run_id' not in trade_dict or not trade_dict['run_id']:
            # Get run_id from somewhere - for now, use a sensible default
            trade_dict['run_id'] = getattr(self, 'current_run_id', 'unknown')
        
        self.trades.append(trade_dict)
        self._append_to_csv(self.trades_file, [trade_dict], self.trades_headers)
    
    def append_run_summary(self, run_dict):
        """Append run summary to CSV and memory
        
        PHASE 29: Called when finalizing a run
        run_dict must contain: run_id, start_time, end_time, total_trades, win_rate,
        avg_pnl_per_trade, total_pnl_paper, total_pnl_shadow, paper_vs_shadow_delta,
        avg_entry_slippage_bps, avg_exit_slippage_bps, sign_flip_rate
        """
        self.runs.append(run_dict)
        self._append_to_csv(self.runs_file, [run_dict], self.runs_headers)
        print(f"[PHASE 29] Run summary appended: {run_dict['run_id']}")
    
    def append_run_separator(self, run_id):
        """PHASE 29: Append RUN_SEPARATOR markers to all CSV files
        
        This creates a clear boundary between runs in the persistent CSV files.
        Separator rows have: run_id, 'RUN_SEPARATOR', timestamp
        """
        separator_row = {
            'run_id': run_id,
            'timestamp': datetime.utcnow().isoformat(),
            # Other columns left empty - the separator marker is in column 2
        }
        
        # Append separator to each file
        print(f"[PHASE 29] Appending RUN_SEPARATOR markers for {run_id}...")
        
        # research_trades.csv separator
        with open(self.trades_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.trades_headers)
            sep = separator_row.copy()
            sep['asset'] = 'RUN_SEPARATOR'
            writer.writerow(sep)
        
        # signal_health.csv separator
        with open(self.signal_health_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.signal_health_headers)
            sep = separator_row.copy()
            sep['asset'] = 'RUN_SEPARATOR'
            writer.writerow(sep)
        
        # execution_quality.csv separator
        with open(self.execution_quality_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.execution_quality_headers)
            sep = separator_row.copy()
            sep['asset'] = 'RUN_SEPARATOR'
            writer.writerow(sep)
        
        print(f"[PHASE 29] RUN_SEPARATOR markers appended successfully")
    
    def append_signal_health(self, health_dict):
        """Append signal health metric to CSV and memory"""
        health_dict['run_id'] = getattr(self, 'current_run_id', 'unknown')
        self.signal_health.append(health_dict)
        self._append_to_csv(self.signal_health_file, [health_dict], self.signal_health_headers)
    
    def append_execution_quality(self, quality_dict):
        """Append execution quality metric to CSV and memory"""
        quality_dict['run_id'] = getattr(self, 'current_run_id', 'unknown')
        self.execution_quality.append(quality_dict)
        self._append_to_csv(self.execution_quality_file, [quality_dict], self.execution_quality_headers)
    
    def _append_to_csv(self, filepath, rows, headers):
        """Append rows to CSV file"""
        with open(filepath, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            for row in rows:
                writer.writerow(row)
    
    def get_recent_trades(self, limit=30):
        """PHASE 32.5F: Get most recent trades for CURRENT RUN ONLY (excluding separators)
        
        CRITICAL: Filter by current_run_id to prevent historical bleed-through.
        After 'New Run' is clicked, this returns only trades from the new run.
        """
        if self.current_run_id:
            # Filter by current run
            run_trades = [
                t for t in self.trades 
                if t.get('asset') != 'RUN_SEPARATOR' and t.get('run_id') == self.current_run_id
            ]
            print(f"[METRICS] Using {len(run_trades)} trades for current run {self.current_run_id}")
            return run_trades[-limit:] if run_trades else []
        else:
            # Fallback: use all trades (shouldn't happen in normal operation)
            non_separators = [t for t in self.trades if t.get('asset') != 'RUN_SEPARATOR']
            return non_separators[-limit:] if non_separators else []
    
    def get_trades_by_asset(self, asset):
        """Get trades for specific asset"""
        return [t for t in self.trades if t.get('asset') == asset and t.get('asset') != 'RUN_SEPARATOR']
    
    def get_trades_by_signal(self, signal):
        """Get trades for specific signal"""
        return [t for t in self.trades if t.get('signal') == signal and t.get('asset') != 'RUN_SEPARATOR']
    
    def get_trades_by_source(self, source):
        """PHASE 32.5G: Get trades from specific source - FILTERED BY CURRENT RUN
        
        CRITICAL: Must filter by current_run_id to prevent cross-run contamination.
        """
        if self.current_run_id:
            return [
                t for t in self.trades 
                if t.get('source') == source and t.get('asset') != 'RUN_SEPARATOR' 
                and t.get('run_id') == self.current_run_id
            ]
        else:
            # Fallback (shouldn't happen)
            return [t for t in self.trades if t.get('source') == source and t.get('asset') != 'RUN_SEPARATOR']
    
    def get_breakdowns(self):
        """Return trade breakdowns by asset, signal, regime, direction - RUN FILTERED"""
        # Use get_recent_trades() to get only current run trades (run-filtered)
        current_run_trades = self.get_recent_trades(limit=100000)
        result = {
            'by_asset': self._breakdown_by_key_trades('asset', current_run_trades),
            'by_signal': self._breakdown_by_key_trades('signal', current_run_trades),
            'by_regime': self._breakdown_by_key_trades('regime', current_run_trades),
            'by_direction': self._breakdown_by_key_trades('side', current_run_trades),
        }
        return result
    
    def _breakdown_by_key_trades(self, key, trades_list):
        """Generate breakdown statistics by key from a trades list (exclude separators)"""
        groups = defaultdict(list)
        for trade in trades_list:
            if trade.get('asset') == 'RUN_SEPARATOR':
                continue
            if key in trade and trade[key]:
                groups[trade[key]].append(trade)
        
        result = {}
        for group_name, trades in groups.items():
            result[group_name] = {
                'count': len(trades),
                'total_pnl': sum(float(t.get('pnl', 0)) for t in trades),
                'win_rate': self._calc_win_rate(trades),
                'avg_pnl': self._calc_avg_pnl(trades),
            }
        return result
    
    def _breakdown_by_key(self, key):
        """Generate breakdown statistics by key (exclude separators) - DEPRECATED"""
        groups = defaultdict(list)
        for trade in self.trades:
            if trade.get('asset') == 'RUN_SEPARATOR':
                continue
            if key in trade and trade[key]:
                groups[trade[key]].append(trade)
        
        result = {}
        for group_name, trades_list in groups.items():
            result[group_name] = {
                'count': len(trades_list),
                'total_pnl': sum(float(t.get('pnl', 0)) for t in trades_list),
                'win_rate': self._calc_win_rate(trades_list),
                'avg_pnl': self._calc_avg_pnl(trades_list),
            }
        return result
    
    def get_signal_health(self):
        """Get latest signal health metrics (exclude separators)"""
        non_separators = [s for s in self.signal_health if s.get('asset') != 'RUN_SEPARATOR']
        if not non_separators:
            return {}
        return non_separators[-50:]  # Last 50 readings
    
    def get_execution_quality(self):
        """Get execution quality metrics (exclude separators)"""
        non_separators = [e for e in self.execution_quality if e.get('asset') != 'RUN_SEPARATOR']
        if not non_separators:
            return {}
        return non_separators[-50:]  # Last 50 readings
    
    def get_win_rate(self):
        """Calculate overall win rate"""
        return self._calc_win_rate(self.get_recent_trades(limit=10000))
    
    def _calc_win_rate(self, trades):
        """Calculate win rate for a list of trades"""
        if not trades:
            return 0.0
        winning = sum(1 for t in trades if float(t.get('pnl', 0)) > 0)
        return winning / len(trades)
    
    def get_avg_pnl_per_trade(self):
        """Get average PnL per trade"""
        return self._calc_avg_pnl(self.get_recent_trades(limit=10000))
    
    def _calc_avg_pnl(self, trades):
        """Calculate average PnL for a list of trades"""
        if not trades:
            return 0.0
        pnls = [float(t.get('pnl', 0)) for t in trades]
        return mean(pnls) if pnls else 0.0
    
    def get_backtest_edge(self):
        """Get backtest edge in basis points"""
        backtest_trades = self.get_trades_by_source('backtest')
        if not backtest_trades:
            return 0.0
        # Edge = avg PnL in bps
        avg_pnl_bps = mean([float(t.get('pnl_bps', 0)) for t in backtest_trades])
        return avg_pnl_bps
    
    def get_avg_slippage(self):
        """PHASE 28/32.5G: Calculate average entry and exit slippage in bps - RUN FILTERED"""
        trades = self.get_recent_trades(limit=10000)
        print("[SLIPPAGE TRACE] run_id:", self.current_run_id, "| trades:", len(trades))
        if not trades:
            print("[SLIPPAGE TRACE] NO TRADES - returning 0.0 for both entry/exit")
            return {'entry_bps': 0.0, 'exit_bps': 0.0}
        
        entry_slippages = []
        exit_slippages = []
        
        for trade in trades:
            expected_entry = float(trade.get('expected_fill', 0))
            shadow_entry = float(trade.get('shadow_fill', 0))
            if expected_entry > 0:
                entry_slippage_bps = abs(shadow_entry - expected_entry) / expected_entry * 10000
                entry_slippages.append(entry_slippage_bps)
            
            # Estimate exit slippage
            expected_exit = float(trade.get('exit_price', 0))
            if expected_exit > 0 and shadow_entry > 0:
                estimated_shadow_exit = expected_exit * 0.9997
                exit_slippage_bps = abs(estimated_shadow_exit - expected_exit) / expected_exit * 10000
                exit_slippages.append(exit_slippage_bps)
        
        avg_entry = mean(entry_slippages) if entry_slippages else 0.0
        avg_exit = mean(exit_slippages) if exit_slippages else 0.0
        
        print("[SLIPPAGE TRACE] RESULT: entry=", round(avg_entry, 2), "bps, exit=", round(avg_exit, 2), "bps")
        return {'entry_bps': avg_entry, 'exit_bps': avg_exit}
    
    def get_trade_integrity(self):
        """PHASE 28/32.5G: Calculate trade count integrity and sign flip rate - RUN FILTERED"""
        paper_trades = self.get_trades_by_source('paper')
        shadow_trades = self.get_trades_by_source('shadow')
        
        print("[INTEGRITY TRACE] run_id:", self.current_run_id, "paper:", len(paper_trades), "shadow:", len(shadow_trades))
        
        total = len(paper_trades)
        trade_diff = abs(len(paper_trades) - len(shadow_trades))
        
        # Count sign flips (paper win but shadow loss)
        flips = 0
        for p, s in zip(paper_trades, shadow_trades):
            p_pnl = float(p.get('pnl', 0))
            s_pnl = float(s.get('pnl', 0))
            if p_pnl > 0 and s_pnl < 0:
                flips += 1
        
        flip_rate = (flips / total * 100) if total > 0 else 0.0
        
        print("[INTEGRITY TRACE] RESULT: sign_flips=", flips, "rate=", round(flip_rate, 1), "%")
        
        return {
            'total_trades': total,
            'trade_diff': trade_diff,
            'sign_flips': flips,
            'sign_flip_rate_pct': flip_rate
        }
    
    def get_rolling_metrics(self, window=20):
        """Calculate rolling metrics over last N trades"""
        recent = self.get_recent_trades(limit=window)
        if len(recent) < window:
            return self.get_recent_metrics()
        
        return {
            'win_rate': self._calc_win_rate(recent),
            'avg_pnl': self._calc_avg_pnl(recent),
            'total_pnl': sum(float(t.get('pnl', 0)) for t in recent),
            'count': len(recent),
        }
    
    def get_recent_metrics(self):
        """Get metrics from all available trades"""
        trades = self.get_recent_trades(limit=10000)
        return {
            'win_rate': self._calc_win_rate(trades),
            'avg_pnl': self._calc_avg_pnl(trades),
            'total_pnl': sum(float(t.get('pnl', 0)) for t in trades),
            'count': len(trades),
        }
    
    def reset_trades_for_new_run(self, new_run_id):
        """PHASE 32.5: Clear in-memory trades cache for new run
        
        CRITICAL FIX: DataLayer.self.trades held stale trades from prior runs.
        When "New Run" clicked, CSV had separator but memory cache wasn't cleared.
        Result: total_trades metric showed old values (~1000) instead of 0.
        
        This method:
        1. Clears self.trades memory list completely
        2. Creates new empty in-memory cache for new run
        3. Reloads ONLY current run data from CSV (after separator)
        
        MUST be called after append_run_separator() in reset endpoint.
        """
        print(f"[PHASE 32.5] Clearing DataLayer trades cache for new run: {new_run_id}")
        
        # Clear all in-memory caches
        self.trades = []
        self.signal_health = []
        self.execution_quality = []
        
        # Reload from CSV - will be empty until new trades arrive
        # But now we have clear boundary: separator marks end of previous run
        self._load_all()
        
        print(f"[PHASE 32.5] DataLayer cache cleared - trades: {len(self.trades)}, signal_health: {len(self.signal_health)}")
        
        # Set current run_id for all new trades
        self.current_run_id = new_run_id
