// MOLTmarket Dashboard - Client-side interactivity

class Dashboard {
    constructor() {
        this.chart = null;
        this.updateInterval = 1000; // Update every 1 second
        this.metrics = {};
        this.equityCurves = {
            paper: [],
            shadow: [],
            backtest: [],
        };
        this.nurseryPollingInterval = null;
        
        this.init();
    }
    
    init() {
        this.setupEventListeners();
        this.initChart();
        this.startPolling();
    }
    
    setupEventListeners() {
        // Time range buttons
        document.querySelectorAll('.range-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.range-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                // TODO: Filter data by time range
            });
        });
        
        // Chart toggles
        document.getElementById('toggle-paper').addEventListener('change', () => this.updateChart());
        document.getElementById('toggle-shadow').addEventListener('change', () => this.updateChart());
        document.getElementById('toggle-backtest').addEventListener('change', () => this.updateChart());
        
        // PHASE 31: Spawn babies button
        const spawnBtn = document.getElementById('spawnBabiesBtn');
        if (spawnBtn) {
            spawnBtn.addEventListener('click', () => {
                console.log('[NURSERY] spawn button clicked');
                this.spawnNursery();
            });
        }
    }
    
    initChart() {
        const ctx = document.getElementById('equityChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [
                    {
                        label: 'Paper',
                        data: [],
                        borderColor: '#4dd0e1',
                        backgroundColor: 'rgba(77, 208, 225, 0.05)',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Shadow',
                        data: [],
                        borderColor: '#ff7043',
                        backgroundColor: 'rgba(255, 112, 67, 0.05)',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y',
                    },
                    {
                        label: 'Backtest',
                        data: [],
                        borderColor: '#81c784',
                        backgroundColor: 'rgba(129, 199, 132, 0.05)',
                        borderWidth: 2,
                        pointRadius: 0,
                        pointHoverRadius: 4,
                        tension: 0.4,
                        fill: false,
                        yAxisID: 'y',
                    },
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                interaction: {
                    intersect: false,
                    mode: 'index',
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top',
                        labels: {
                            color: '#b0bec5',
                            font: { size: 12 },
                            padding: 16,
                            usePointStyle: true,
                        }
                    },
                    tooltip: {
                        backgroundColor: '#1a1f3a',
                        titleColor: '#e8eaf6',
                        bodyColor: '#b0bec5',
                        borderColor: '#2a3f5f',
                        borderWidth: 1,
                        padding: 12,
                        callbacks: {
                            label: function(context) {
                                return context.dataset.label + ': $' + context.parsed.y.toLocaleString('en-US', {maximumFractionDigits: 2});
                            }
                        }
                    }
                },
                scales: {
                    y: {
                        type: 'linear',
                        position: 'left',
                        ticks: {
                            color: '#b0bec5',
                            callback: function(value) {
                                return '$' + value.toLocaleString('en-US', {maximumFractionDigits: 0});
                            }
                        },
                        grid: {
                            color: '#2a3f5f',
                            drawBorder: false,
                        }
                    },
                    x: {
                        ticks: {
                            color: '#b0bec5',
                        },
                        grid: {
                            display: false,
                            drawBorder: false,
                        }
                    }
                }
            }
        });
    }
    
    async fetchMetrics() {
        try {
            const response = await fetch('/api/metrics');
            if (!response.ok) {
                console.error(`[API ERROR] /api/metrics returned ${response.status}`);
                return {};
            }
            const data = await response.json();
            this.metrics = data;
            this.updateKPIs();
            return data;
        } catch (e) {
            console.error('Error fetching metrics:', e);
            return {};
        }
    }
    
    async fetchEquityCurves() {
        try {
            const response = await fetch('/api/equity-curves');
            if (!response.ok) {
                console.error(`[API ERROR] /api/equity-curves returned ${response.status}`);
                return {};
            }
            const data = await response.json();
            
            // [PHASE 30] Store raw data
            this.equityCurves = {
                paper: data.paper || [],
                shadow: data.shadow || [],
                backtest: data.backtest || [],
            };
            
            // [PHASE 30] Debug logging - verify all 3 arrays are present
            console.log('[PHASE 30] Frontend received equity curves:');
            console.log('  Paper length:', this.equityCurves.paper.length, 'points');
            if (this.equityCurves.paper.length > 0) {
                console.log('  Paper first:', this.equityCurves.paper[0]);
                console.log('  Paper last:', this.equityCurves.paper[this.equityCurves.paper.length - 1]);
            }
            console.log('  Shadow length:', this.equityCurves.shadow.length, 'points');
            if (this.equityCurves.shadow.length > 0) {
                console.log('  Shadow first:', this.equityCurves.shadow[0]);
                console.log('  Shadow last:', this.equityCurves.shadow[this.equityCurves.shadow.length - 1]);
            }
            console.log('  Backtest length:', this.equityCurves.backtest.length, 'points');
            if (this.equityCurves.backtest.length > 0) {
                console.log('  Backtest first:', this.equityCurves.backtest[0]);
                console.log('  Backtest last:', this.equityCurves.backtest[this.equityCurves.backtest.length - 1]);
            }
            
            this.updateChart();
            return data;
        } catch (e) {
            console.error('Error fetching equity curves:', e);
        }
    }
    
    async fetchTrades() {
        try {
            const response = await fetch('/api/trades');
            if (!response.ok) {
                console.error(`[API ERROR] /api/trades returned ${response.status}`);
                return [];
            }
            const trades = await response.json();
            this.updateTradesTable(trades || []);
            return trades;
        } catch (e) {
            console.error('Error fetching trades:', e);
            return [];
        }
    }
    
    async fetchBreakdowns() {
        try {
            const response = await fetch('/api/breakdowns');
            if (!response.ok) {
                console.error(`[API ERROR] /api/breakdowns returned ${response.status}`);
                return {};
            }
            const breakdowns = await response.json();
            this.updateBreakdowns(breakdowns || {});
            return breakdowns;
        } catch (e) {
            console.error('Error fetching breakdowns:', e);
            return {};
        }
    }
    
    updateKPIs() {
        const m = this.metrics;
        
        // Paper Value
        document.getElementById('kpi-paper').textContent = '$' + (m.paper_pnl_dollars || 0).toLocaleString('en-US', {maximumFractionDigits: 2});
        
        // Shadow Value
        document.getElementById('kpi-shadow').textContent = '$' + (m.shadow_pnl_dollars || 0).toLocaleString('en-US', {maximumFractionDigits: 2});
        
        // Delta
        const deltaValue = m.delta_return_pct || 0;
        document.getElementById('kpi-delta').textContent = deltaValue.toFixed(2) + '%';
        
        // Backtest Edge
        document.getElementById('kpi-edge').textContent = (m.backtest_edge_bps || 0).toFixed(2);
        
        // Total Trades
        document.getElementById('kpi-trades').textContent = m.total_trades || 0;
        
        // Win Rate
        document.getElementById('kpi-winrate').textContent = (m.rolling_win_rate || 0).toFixed(1);
        
        // Avg PnL
        document.getElementById('kpi-avgpnl').textContent = '$' + (m.avg_pnl_per_trade || 0).toFixed(2);
        
        // Signal / Asset
        document.getElementById('signal-name').textContent = m.current_signal || '—';
        document.getElementById('asset-name').textContent = m.current_asset || '—';
        document.getElementById('regime-label').textContent = 'Regime: ' + (m.regime || '—');
        
        // Update status
        const statusText = document.getElementById('status-text');
        statusText.textContent = 'Live';
        
        // PHASE 28: Execution Diagnostics
        document.getElementById('kpi-entry-slippage').textContent = (m.avg_entry_slippage_bps || 0).toFixed(2);
        document.getElementById('kpi-exit-slippage').textContent = (m.avg_exit_slippage_bps || 0).toFixed(2);
        document.getElementById('kpi-sign-flips').textContent = (m.sign_flip_rate_pct || 0).toFixed(1);
        document.getElementById('flip-count').textContent = `${m.sign_flip_count || 0} of ${m.total_trades_integrity || 0} trades`;
        
        // Update Active Strategy from metrics
        const strategyId = m.active_strategy_id || 'baseline';
        const generation = m.active_strategy_generation || 0;
        updateActiveStrategyLabel(strategyId, generation);
        
        // Update Simulator Feed Indicators
        const simId = m.simulator_instance_id || '—';
        document.getElementById('arena-simulator-id').textContent = simId;
        document.getElementById('nursery-simulator-id').textContent = simId;
        
        // Color-code: both same = good
        if (simId !== '—') {
            const color = '#00aa00';
            document.getElementById('arena-simulator-id').style.color = color;
            document.getElementById('nursery-simulator-id').style.color = color;
        }
    }
    
    updateChart() {
        // [PHASE 30] CRITICAL FIX: Extract visibility toggles
        const paperVisible = document.getElementById('toggle-paper').checked;
        const shadowVisible = document.getElementById('toggle-shadow').checked;
        const backtestVisible = document.getElementById('toggle-backtest').checked;
        
        // [PHASE 30] Get raw curves (array of {timestamp, value})
        const paperCurve = this.equityCurves.paper || [];
        const shadowCurve = this.equityCurves.shadow || [];
        const backtestCurve = this.equityCurves.backtest || [];
        
        // [PHASE 30] Extract value arrays and take last 100 points
        const paperValues = paperCurve.slice(-100).map(p => p.value);
        const shadowValues = shadowCurve.slice(-100).map(p => p.value);
        const backtestValues = backtestCurve.slice(-100).map(p => p.value);
        
        // [PHASE 30] Create labels for all data points
        const maxLen = Math.max(paperValues.length, shadowValues.length, backtestValues.length);
        const labels = Array.from({length: maxLen}, (_, i) => i);
        
        // [PHASE 30] DEBUG: Log all arrays before update
        console.log('[PHASE 30] updateChart() called:');
        console.log('  Visibility - Paper:', paperVisible, 'Shadow:', shadowVisible, 'Backtest:', backtestVisible);
        console.log('  Data lengths - Paper:', paperValues.length, 'Shadow:', shadowValues.length, 'Backtest:', backtestValues.length);
        console.log('  Paper values:', paperValues);
        console.log('  Shadow values:', shadowValues);
        console.log('  Backtest values:', backtestValues);
        console.log('  Max length:', maxLen, 'Labels:', labels);
        
        // [PHASE 30] CRITICAL: Update all three datasets
        this.chart.data.labels = labels;
        this.chart.data.datasets[0].data = paperVisible ? paperValues : [];
        this.chart.data.datasets[1].data = shadowVisible ? shadowValues : [];
        this.chart.data.datasets[2].data = backtestVisible ? backtestValues : [];
        
        // [PHASE 30] DEBUG: Verify after update
        console.log('[PHASE 30] After chart update:');
        console.log('  Dataset 0 (Paper) length:', this.chart.data.datasets[0].data.length);
        console.log('  Dataset 1 (Shadow) length:', this.chart.data.datasets[1].data.length);
        console.log('  Dataset 2 (Backtest) length:', this.chart.data.datasets[2].data.length);
        console.log('  Dataset 0 (Paper) data:', this.chart.data.datasets[0].data);
        console.log('  Dataset 1 (Shadow) data:', this.chart.data.datasets[1].data);
        console.log('  Dataset 2 (Backtest) data:', this.chart.data.datasets[2].data);
        
        this.chart.update('none'); // No animation
    }
    
    updateTradesTable(trades) {
        const tbody = document.querySelector('.trades-table tbody');
        tbody.innerHTML = '';
        
        trades.slice(-30).reverse().forEach(trade => {
            const row = document.createElement('tr');
            
            const pnlValue = parseFloat(trade.pnl || 0);
            const pnlClass = pnlValue > 0 ? 'pnl-positive' : pnlValue < 0 ? 'pnl-negative' : '';
            const sourceClass = `source-${trade.source}`;
            
            const date = new Date(trade.timestamp);
            const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', second: '2-digit' });
            
            row.innerHTML = `
                <td>${timeStr}</td>
                <td>${trade.asset}</td>
                <td>${trade.signal}</td>
                <td><span class="${sourceClass}">${trade.source}</span></td>
                <td>${trade.side}</td>
                <td>$${parseFloat(trade.entry_price).toFixed(2)}</td>
                <td>$${parseFloat(trade.exit_price).toFixed(2)}</td>
                <td><span class="${pnlClass}">$${pnlValue.toFixed(2)}</span></td>
                <td>${trade.duration}s</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    updateBreakdowns(breakdowns) {
        this.updateBreakdownTable('breakdown-asset', breakdowns.by_asset);
        this.updateBreakdownTable('breakdown-signal', breakdowns.by_signal);
        this.updateBreakdownTable('breakdown-regime', breakdowns.by_regime);
        this.updateBreakdownTable('breakdown-direction', breakdowns.by_direction);
    }
    
    updateBreakdownTable(elementId, data) {
        const tbody = document.getElementById(elementId);
        tbody.innerHTML = '';
        
        Object.entries(data || {}).forEach(([name, stats]) => {
            const row = document.createElement('tr');
            const winPct = (stats.win_rate * 100).toFixed(1);
            const pnlStr = '$' + stats.total_pnl.toFixed(2);
            
            row.innerHTML = `
                <td>${name}</td>
                <td>${stats.count}</td>
                <td>${pnlStr}</td>
                <td>${winPct}%</td>
            `;
            
            tbody.appendChild(row);
        });
    }
    
    startPolling() {
        const poll = async () => {
            await this.fetchMetrics();
            await this.fetchEquityCurves();
            await this.fetchTrades();
            await this.fetchBreakdowns();
        };
        
        // Initial poll
        poll();
        
        // Set interval
        setInterval(poll, this.updateInterval);
    }

    // PHASE 31: Nursery spawn and polling
    async spawnNursery() {
        console.log('[NURSERY] spawnNursery() called');
        console.log('[NURSERY] Sending spawn request to /api/nursery/spawn');
        
        // Disable button during spawn
        const btn = document.getElementById('spawnBabiesBtn');
        if (btn) btn.disabled = true;
        
        try {
            const response = await fetch('/api/nursery/spawn', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            console.log('[NURSERY] Spawn response received, status:', response.status);
            const data = await response.json();
            console.log('[NURSERY] Spawn response data:', data);
            
            if (data.status === 'success') {
                console.log(`[NURSERY] Successfully spawned ${data.babies_count} babies`);
                
                // Immediately fetch leaderboard
                setTimeout(() => {
                    console.log('[NURSERY] Fetching leaderboard after spawn');
                    this.fetchNurseryLeaderboard();
                }, 500);
                
                // Start polling
                this.startNurseryPolling();
            } else {
                console.error('[NURSERY] Spawn failed:', data.error || data.message);
            }
        } catch (error) {
            console.error('[NURSERY] Spawn request error:', error);
        } finally {
            // Re-enable button
            const btn = document.getElementById('spawnBabiesBtn');
            if (btn) btn.disabled = false;
        }
    }
    
    async fetchNurseryLeaderboard() {
        try {
            const response = await fetch('/api/nursery/leaderboard');
            const data = await response.json();
            
            console.log("[NURSERY] leaderboard rows =", data.leaderboard?.length || 0);
            
            if (!data.leaderboard || data.leaderboard.length === 0) {
                console.log("[NURSERY] no leaderboard data yet");
                return;
            }
            
            this.updateNurseryPanel(data.leaderboard);
        } catch (err) {
            console.error("[NURSERY] leaderboard fetch error:", err);
        }
    }
    
    startNurseryPolling() {
        // Clear any existing polling interval
        if (this.nurseryPollingInterval) {
            clearInterval(this.nurseryPollingInterval);
        }
        
        // Poll every 3 seconds
        console.log("[NURSERY] starting leaderboard polling (3s interval)");
        this.nurseryPollingInterval = setInterval(async () => {
            await this.fetchNurseryLeaderboard();
        }, 3000);
    }
    
    stopNurseryPolling() {
        if (this.nurseryPollingInterval) {
            clearInterval(this.nurseryPollingInterval);
            this.nurseryPollingInterval = null;
            console.log("[NURSERY] stopped polling");
        }
    }

    updateNurseryPanel(leaderboard) {
        if (!leaderboard || leaderboard.length === 0) {
            document.getElementById('nursery-body').innerHTML = '<tr><td colspan="8" style="text-align: center; color: #999;">No nursery data</td></tr>';
            document.getElementById('nursery-status').textContent = 'idle';
            document.getElementById('nursery-count').textContent = '0';
            document.getElementById('top-candidate').textContent = '—';
            return;
        }

        // Update status
        document.getElementById('nursery-status').textContent = 'active';
        document.getElementById('nursery-count').textContent = leaderboard.length;
        
        const topCandidate = leaderboard[0];
        document.getElementById('top-candidate').textContent = `${topCandidate.variant_id} (${topCandidate.score.toFixed(1)})`;

        // Populate table rows
        const tbody = document.getElementById('nursery-body');
        tbody.innerHTML = '';

        leaderboard.forEach((baby, rank) => {
            const score = baby.score;
            let rowClass = 'weak';
            
            if (score > 70) {
                rowClass = 'strong';
            } else if (score >= 40) {
                rowClass = 'borderline';
            }

            const row = document.createElement('tr');
            row.className = rowClass;
            row.innerHTML = `
                <td>${baby.variant_id}</td>
                <td>${baby.mutation_type}</td>
                <td>${baby.trades}</td>
                <td>$${baby.shadow_pnl.toFixed(2)}</td>
                <td>${baby.flip_rate.toFixed(1)}%</td>
                <td>${baby.degradation.toFixed(1)}%</td>
                <td>${score.toFixed(1)}</td>
                <td>${baby.status}</td>
            `;
            tbody.appendChild(row);
        });
        
        console.log(`[NURSERY] updated ${leaderboard.length} rows in leaderboard`);
    }
}

// Initialize dashboard when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.dashboard = new Dashboard();
});

// PHASE 29: New Run button handler
document.addEventListener('DOMContentLoaded', () => {
    const newRunBtn = document.getElementById('newRunButton');
    if (newRunBtn) {
        newRunBtn.addEventListener('click', async () => {
            console.log('[PHASE 29] New Run button clicked');
            
            if (!confirm('Start new experiment run? All current data will be finalized and preserved.')) {
                return;
            }
            
            try {
                // POST /api/new_run (preserves active strategy)
                const response = await fetch('/api/new_run', { method: 'POST' });
                const result = await response.json();
                
                if (result.status === 'reset_complete') {
                    console.log('[PHASE 29] Reset complete:', result.new_run_id);
                    
                    // [PHASE 30] Clear chart by resetting equity curves
                    if (window.dashboard) {
                        window.dashboard.equityCurves = {
                            paper: [],
                            shadow: [],
                            backtest: [],
                        };
                        window.dashboard.updateChart();
                    }
                    
                    // Reset KPI cards to zero (with null guards)
                    const safeSetKPI = (id, value) => {
                        const el = document.getElementById(id);
                        if (el) {
                            // Only update the text node, preserve child spans (like .bps-suffix, .pct-suffix)
                            const firstNode = el.firstChild;
                            if (firstNode && firstNode.nodeType === Node.TEXT_NODE) {
                                firstNode.textContent = value;
                            } else if (!el.querySelector('span')) {
                                // If no span children, safe to use textContent
                                el.textContent = value;
                            }
                        }
                    };
                    
                    safeSetKPI('kpi-trades', '0');
                    safeSetKPI('kpi-winrate', '0.0');
                    safeSetKPI('kpi-edge', '0.00');
                    safeSetKPI('kpi-entry-slippage', '0.00');
                    safeSetKPI('kpi-exit-slippage', '0.00');
                    safeSetKPI('kpi-sign-flips', '0');
                    
                    // Update run_id display
                    const runIdEl = document.getElementById('run-id');
                    if (runIdEl) {
                        runIdEl.textContent = result.new_run_id;
                    }
                    
                    // Show notification
                    showNotification(`New run started: ${result.new_run_id}`, 'success');
                    
                    // [PHASE 32.5C] Force full page reload to refresh Trade Breakdowns and all metrics
                    console.log('[PHASE 32.5C] Reloading page to refresh all data after reset...');
                    setTimeout(() => {
                        window.location.reload();
                    }, 800);
                    
                    // Log previous run summary
                    if (result.previous_run_summary) {
                        console.log('[PHASE 29] Previous run summary:', result.previous_run_summary);
                    }
                } else {
                    showNotification(`Error: ${result.message}`, 'error');
                }
            } catch (e) {
                console.error('[PHASE 29] Error calling reset endpoint:', e);
                showNotification('Error resetting experiment', 'error');
            }
        });
    }
});

// Notification helper
function showNotification(message, type = 'info') {
    console.log(`[NOTIFICATION] ${type.toUpperCase()}: ${message}`);
    // Could add toast notification UI here
}

// =========================================================================
// PHASE 31.4: SPAWN BUTTON EXPLICIT EVENT LISTENER
// =========================================================================
console.log('[NURSERY] Registering spawn button listener (explicit binding)');

const spawnBtn = document.getElementById('spawnBabiesBtn');

if (spawnBtn) {
    console.log('[NURSERY] Spawn button found in DOM');
    
    spawnBtn.addEventListener('click', function(e) {
        e.preventDefault();
        console.log('[NURSERY] Spawn button clicked!');
        
        // Call spawn method on window.dashboard
        if (window.dashboard) {
            console.log('[NURSERY] Calling window.dashboard.spawnNursery()');
            window.dashboard.spawnNursery();
        } else {
            console.error('[NURSERY] ERROR: window.dashboard not found');
        }
    });
    
    console.log('[NURSERY] Explicit event listener attached to spawn button');
} else {
    console.error('[NURSERY] ERROR: Spawn button element not found (ID: spawnBabiesBtn)');
}

// =========================================================================
// PHASE 32.2: FRONTEND CONTROL LAYER + ACTIVE STRATEGY IDENTITY
// =========================================================================

console.log('[PHASE 32.2] Initializing frontend control layer...');

// Global state for active strategy
let activeStrategy = {
    id: 'baseline',
    generation: 0,
};

// PART 1: Update active strategy label
function updateActiveStrategyLabel(strategyId, generation) {
    activeStrategy = { id: strategyId, generation: generation };
    const label = document.getElementById('active-strategy');
    if (label) {
        label.textContent = `${strategyId} • Gen ${generation}`;
        console.log(`[PHASE 32.2] Updated active strategy label: ${strategyId} • Gen ${generation}`);
    }
}

// PART 2: Add promote button to nursery leaderboard
function updateNurseryLeaderboardWithActions(leaderboard) {
    if (!leaderboard || leaderboard.length === 0) {
        document.getElementById('nursery-body').innerHTML = '<tr><td colspan="9" style="text-align: center; color: #999;">No nursery data</td></tr>';
        document.getElementById('nursery-status').textContent = 'idle';
        document.getElementById('nursery-count').textContent = '0';
        document.getElementById('top-candidate').textContent = '—';
        return;
    }

    // Update status
    document.getElementById('nursery-status').textContent = 'active';
    document.getElementById('nursery-count').textContent = leaderboard.length;
    
    const topCandidate = leaderboard[0];
    document.getElementById('top-candidate').textContent = `${topCandidate.variant_id} (${topCandidate.score.toFixed(1)})`;

    // Populate table rows with action column
    const tbody = document.getElementById('nursery-body');
    tbody.innerHTML = '';

    leaderboard.forEach((baby, rank) => {
        const score = baby.score;
        let rowClass = 'weak';
        
        if (score > 70) {
            rowClass = 'strong';
        } else if (score >= 40) {
            rowClass = 'borderline';
        }

        const row = document.createElement('tr');
        row.className = rowClass;
        
        // TASK 3: Button only highlights when shadow_pnl > 0 (positive)
        const isPositive = baby.shadow_pnl > 0;
        const canPromote = isPositive;
        
        const promoteBtn = document.createElement('button');
        promoteBtn.className = 'btn-promote';
        promoteBtn.disabled = !canPromote;
        
        if (isPositive) {
            promoteBtn.textContent = '✓ Promote to Main Arena';
            promoteBtn.style.backgroundColor = '#4CAF50';  // Green
            promoteBtn.style.color = 'white';
            promoteBtn.addEventListener('click', async (e) => {
                e.preventDefault();
                console.log(`[PROMOTE CLICK] button clicked for ${baby.variant_id}`);
                await promoteVariant(baby.variant_id);
            });
        } else {
            promoteBtn.textContent = '✗ Negative PnL';
            promoteBtn.style.backgroundColor = '#ccc';  // Gray
            promoteBtn.style.color = '#666';
            promoteBtn.style.cursor = 'not-allowed';
            promoteBtn.title = `Requires positive shadow PnL (current: $${baby.shadow_pnl.toFixed(2)})`;
        }
        
        const actionCell = document.createElement('td');
        actionCell.appendChild(promoteBtn);
        
        row.innerHTML = `
            <td>${baby.variant_id}</td>
            <td>${baby.mutation_type}</td>
            <td>${baby.trades}</td>
            <td>$${baby.shadow_pnl.toFixed(2)}</td>
            <td>${baby.flip_rate.toFixed(1)}%</td>
            <td>${baby.degradation.toFixed(1)}%</td>
            <td>${score.toFixed(1)}</td>
            <td>${baby.status}</td>
        `;
        row.appendChild(actionCell);
        tbody.appendChild(row);
    });
    
    console.log(`[PHASE 32.2] Updated ${leaderboard.length} rows in leaderboard with action column`);
}

// PART 2: Promote variant to main arena
async function promoteVariant(variantId) {
    console.log(`[PHASE 32.2] Promoting variant: ${variantId}`);
    
    const promoteBtn = event.target;
    promoteBtn.disabled = true;
    const originalText = promoteBtn.textContent;
    promoteBtn.textContent = 'Promoting...';
    
    try {
        const response = await fetch(`/api/nursery/promote/${variantId}`, {
            method: 'POST',
        });
        
        const result = await response.json();
        console.log(`[PROMOTE API] response status=${response.status}`, result);
        
        if (response.ok && (result.success || result.status === 'success')) {
            console.log(`[PROMOTE API] Promotion successful:`, result);
            
            // Update active strategy label
            updateActiveStrategyLabel(variantId, 1);
            
            // Clear nursery panel
            document.getElementById('nursery-body').innerHTML = '<tr><td colspan="9" style="text-align: center; color: #999;">Nursery cleared after promotion</td></tr>';
            document.getElementById('nursery-status').textContent = 'inactive';
            document.getElementById('nursery-count').textContent = '0';
            document.getElementById('top-candidate').textContent = '—';
            
            const message = result.message || `${variantId} promoted to main arena! (PnL: $${result.shadow_pnl?.toFixed(2) || '?'})`;
            showNotification(message, 'success');
        } else {
            const errorMsg = result.error || result.reason || 'Unknown error';
            console.error(`[PROMOTE API] Promotion failed (status=${response.status}):`, result);
            showNotification(`Promotion failed: ${errorMsg}`, 'error');
            promoteBtn.disabled = false;
            promoteBtn.textContent = originalText;
        }
    } catch (e) {
        console.error(`[PHASE 32.2] Error promoting variant:`, e);
        showNotification('Error promoting variant', 'error');
        promoteBtn.disabled = false;
        promoteBtn.textContent = originalText;
    }
}

// PART 4: Reset to baseline strategy
async function resetToBaseline() {
    console.log('[PHASE 32.2] Resetting to baseline strategy...');
    
    if (!confirm('Reset to baseline strategy? This will change the active strategy but NOT reset equity/P&L.')) {
        return;
    }
    
    try {
        const response = await fetch('/api/strategy/reset_to_baseline', {
            method: 'POST',
        });
        
        const result = await response.json();
        
        if (response.ok && result.status === 'success') {
            console.log(`[PHASE 32.2] Reset to baseline complete:`, result);
            
            // Update active strategy label
            updateActiveStrategyLabel('baseline', 0);
            
            showNotification('Reset to baseline strategy - equity/P&L preserved', 'success');
        } else {
            console.error(`[PHASE 32.2] Reset failed:`, result);
            showNotification(`Reset failed: ${result.error}`, 'error');
        }
    } catch (e) {
        console.error(`[PHASE 32.2] Error resetting to baseline:`, e);
        showNotification('Error resetting to baseline', 'error');
    }
}

// PART 6+7: Capital reset confirmation modal
let currentStrategyNameForReset = 'baseline';

function initCapitalResetModal() {
    console.log('[PHASE 32.2] Initializing capital reset modal...');
    
    const modal = document.getElementById('resetCapitalModal');
    const resetCapitalBtn = document.getElementById('resetCapitalBtn');
    const modalCloseBtn = document.getElementById('modalCloseBtn');
    const modalCancelBtn = document.getElementById('modalCancelBtn');
    const modalConfirmBtn = document.getElementById('modalConfirmBtn');
    const strategyNameInput = document.getElementById('strategyNameConfirm');
    const confirmationHint = document.getElementById('confirmationHint');
    const modalOverlay = document.querySelector('.modal-overlay');
    
    if (!resetCapitalBtn) {
        console.error('[PHASE 32.2] Reset capital button not found');
        return;
    }
    
    // PART 5: Open modal on button click
    resetCapitalBtn.addEventListener('click', () => {
        console.log('[PHASE 32.2] Reset capital button clicked');
        currentStrategyNameForReset = activeStrategy.id;
        strategyNameInput.value = '';
        modalConfirmBtn.disabled = true;
        confirmationHint.textContent = `Type "${currentStrategyNameForReset}" to confirm`;
        confirmationHint.classList.remove('match');
        modal.classList.remove('hidden');
    });
    
    // Close modal
    const closeModal = () => {
        modal.classList.add('hidden');
        strategyNameInput.value = '';
        strategyNameInput.focus();
    };
    
    if (modalCloseBtn) {
        modalCloseBtn.addEventListener('click', closeModal);
    }
    
    if (modalCancelBtn) {
        modalCancelBtn.addEventListener('click', closeModal);
    }
    
    if (modalOverlay) {
        modalOverlay.addEventListener('click', closeModal);
    }
    
    // PART 7: Exact match confirmation (case-sensitive, no autofill)
    strategyNameInput.addEventListener('input', (e) => {
        const input = e.target.value;
        const isMatch = input === currentStrategyNameForReset;
        
        modalConfirmBtn.disabled = !isMatch;
        
        if (isMatch) {
            confirmationHint.textContent = '✓ Ready to confirm';
            confirmationHint.classList.add('match');
        } else {
            confirmationHint.textContent = `Type "${currentStrategyNameForReset}" to confirm`;
            confirmationHint.classList.remove('match');
        }
    });
    
    // PART 8: Execute capital reset
    if (modalConfirmBtn) {
        modalConfirmBtn.addEventListener('click', async () => {
            console.log('[PHASE 32.2] Confirming capital reset...');
            
            modalConfirmBtn.disabled = true;
            const originalText = modalConfirmBtn.textContent;
            modalConfirmBtn.textContent = 'Resetting...';
            
            try {
                const response = await fetch('/api/arena/reset_capital', {
                    method: 'POST',
                });
                
                const result = await response.json();
                
                if (response.ok && result.status === 'success') {
                    console.log(`[PHASE 32.2] Capital reset complete:`, result);
                    
                    closeModal();
                    
                    // Reset KPI cards
                    document.getElementById('kpi-paper').textContent = '$10,000.00';
                    document.getElementById('kpi-shadow').textContent = '$10,000.00';
                    document.getElementById('kpi-delta').textContent = '0.00%';
                    document.getElementById('kpi-trades').textContent = '0';
                    document.getElementById('kpi-winrate').textContent = '0.0%';
                    
                    // Reset chart if needed
                    if (window.dashboard) {
                        window.dashboard.equityCurves = {
                            paper: [],
                            shadow: [],
                            backtest: [],
                        };
                        window.dashboard.updateChart();
                    }
                    
                    showNotification('Arena capital reset to $10,000 - strategy unchanged', 'success');
                } else {
                    console.error(`[PHASE 32.2] Reset failed:`, result);
                    showNotification(`Reset failed: ${result.error}`, 'error');
                    modalConfirmBtn.disabled = false;
                    modalConfirmBtn.textContent = originalText;
                }
            } catch (e) {
                console.error(`[PHASE 32.2] Error resetting capital:`, e);
                showNotification('Error resetting capital', 'error');
                modalConfirmBtn.disabled = false;
                modalConfirmBtn.textContent = originalText;
            }
        });
    }
}

// PART 4: Reset baseline button event listener
function initResetButtons() {
    console.log('[PHASE 32.2] Initializing reset buttons...');
    
    const resetBaselineBtn = document.getElementById('resetBaselineBtn');
    if (resetBaselineBtn) {
        resetBaselineBtn.addEventListener('click', resetToBaseline);
    }
}

// Hook into existing updateNurseryPanel to use new version with actions
const OriginalDashboard = Dashboard;
Dashboard.prototype.updateNurseryPanel = function(leaderboard) {
    updateNurseryLeaderboardWithActions(leaderboard);
};

// Initialize on DOM ready
document.addEventListener('DOMContentLoaded', () => {
    console.log('[PHASE 32.2] Initializing PHASE 32.2 features...');
    setTimeout(() => {
        initCapitalResetModal();
        initResetButtons();
        console.log('[PHASE 32.2] Initialization complete');
    }, 100);
});


// === NEW FEATURES: DNA Viewer, Save DNA, Evaluate Bot ===

// SAVE DNA Button
document.addEventListener('DOMContentLoaded', function() {
    const saveDnaBtn = document.getElementById('saveDnaBtn');
    const evaluateBotBtn = document.getElementById('evaluateBotBtn');
    
    if (saveDnaBtn) {
        saveDnaBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/arena/save_dna', { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    alert(`✓ DNA saved: ${data.filename}`);
                } else {
                    alert('Save failed: ' + (data.error || 'Unknown error'));
                }
            } catch (e) {
                alert('Error: ' + e.message);
            }
        });
    }
    
    // EVALUATE BOT Button
    if (evaluateBotBtn) {
        evaluateBotBtn.addEventListener('click', async () => {
            try {
                const res = await fetch('/api/arena/evaluate');
                const data = await res.json();
                
                // Show DNA panel
                const dnaPanel = document.getElementById('dnaPanel');
                if (dnaPanel) {
                    dnaPanel.classList.remove('hidden');
                    
                    // Fetch DNA
                    const dnaRes = await fetch('/api/arena/dna');
                    const dna = await dnaRes.json();
                    
                    let dnaHtml = `
                        <div style="font-size: 11px; margin-bottom: 10px;">
                            <div><strong>Bot ID:</strong> ${dna.bot_id}</div>
                            <div><strong>Generation:</strong> ${dna.generation}</div>
                            <div><strong>Strategy:</strong> ${dna.strategy_type}</div>
                        </div>
                        <div style="font-size: 10px;">
                            <strong>Parameters:</strong>
                            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 5px; margin-top: 5px;">
                    `;
                    
                    for (const [k, v] of Object.entries(dna.parameters || {})) {
                        const val = typeof v === 'number' ? v.toFixed(4) : v;
                        dnaHtml += `<div>${k}: <span style="color: #FFB84D;">${val}</span></div>`;
                    }
                    
                    dnaHtml += '</div></div>';
                    document.getElementById('dnaContent').innerHTML = dnaHtml;
                }
                
                // Show evaluation panel
                const evalPanel = document.getElementById('evalPanel');
                if (evalPanel) {
                    evalPanel.classList.remove('hidden');
                    
                    const badgeColor = data.status === 'PASS' ? '#4CAF50' : '#FF5252';
                    let evalHtml = `
                        <div style="padding: 10px; background: #0f1220; border-radius: 4px; margin-bottom: 10px;">
                            <div style="color: ${badgeColor}; font-weight: bold; font-size: 14px; margin-bottom: 10px;">
                                ${data.status}
                            </div>
                            
                            <div style="font-size: 11px; margin-bottom: 10px;">
                                <strong>Checks:</strong>
                    `;
                    
                    for (const check of data.checks || []) {
                        const icon = check.passed ? '✔' : '✖';
                        const color = check.passed ? '#4CAF50' : '#FF5252';
                        evalHtml += `
                            <div style="color: ${color}; margin-top: 3px;">
                                ${icon} ${check.name}: ${check.value}
                            </div>
                        `;
                    }
                    
                    evalHtml += '</div>';
                    
                    if (data.reasons && data.reasons.length > 0) {
                        evalHtml += `
                            <div style="font-size: 10px; color: #FF5252; margin-bottom: 10px;">
                                <strong>Issues:</strong>
                        `;
                        for (const reason of data.reasons) {
                            evalHtml += `<div>→ ${reason}</div>`;
                        }
                        evalHtml += '</div>';
                    }
                    
                    evalHtml += `
                        <div style="font-size: 10px; color: #FFD54F;">
                            <strong>Recommendation:</strong><br>${data.recommendation}
                        </div>
                    `;
                    
                    document.getElementById('evalContent').innerHTML = evalHtml;
                }
            } catch (e) {
                alert('Evaluate failed: ' + e.message);
            }
        });
    }
});

    // Rocky Insight Button Handler
    let currentRockyInsight = null;
    
    const rockyInsightBtn = document.getElementById('rockyInsightBtn');
    const rockyApproveBtn = document.getElementById('rockyApproveBtn');
    const rockyRejectBtn = document.getElementById('rockyRejectBtn');
    const rockyDecisionButtons = document.getElementById('rockyDecisionButtons');
    
    if (rockyInsightBtn) {
        rockyInsightBtn.addEventListener('click', async () => {
            console.log('[ROCKY] Generating insight...');
            rockyInsightBtn.disabled = true;
            rockyInsightBtn.textContent = '[Thinking...]';
            
            // FIX: Reset decision buttons to pristine state for new insight
            rockyApproveBtn.disabled = false;
            rockyApproveBtn.textContent = '[APPROVE]';
            rockyApproveBtn.style.opacity = '1';
            rockyRejectBtn.disabled = false;
            rockyRejectBtn.textContent = '[REJECT]';
            rockyRejectBtn.style.opacity = '1';
            currentRockyInsight = null;  // Clear old insight
            
            try {
                const response = await fetch('/api/rocky/insight');
                const data = await response.json();
                
                if (data.status === 'success') {
                    console.log('[ROCKY] Insight generated');
                    
                    // Store current insight for decision tracking
                    currentRockyInsight = {
                        run_id: data.run_id,
                        bot_id: data.bot_id,
                        timestamp: data.timestamp
                    };
                    
                    // Format output
                    let rockyHtml = `
                        <div style="color: #00d4ff; margin-bottom: 15px; border-bottom: 1px solid #0f3460; padding-bottom: 10px;">
                            <strong>NOTES:</strong>
                        </div>
                        <div style="color: #aaa; margin-bottom: 20px; padding: 10px; background: #0a0e14; border-left: 2px solid #00d4ff;">
                            ${data.notes}
                        </div>
                        
                        <div style="color: #00d4ff; margin-bottom: 15px; border-bottom: 1px solid #0f3460; padding-bottom: 10px;">
                            <strong>PROPOSAL:</strong>
                        </div>
                        <div style="color: #aaa; white-space: pre-wrap; font-size: 10px; padding: 10px; background: #0a0e14;">
                            ${data.proposal}
                        </div>
                        
                        <div style="color: #4CAF50; margin-top: 15px; padding: 10px; background: #0a2e0a; border-left: 3px solid #4CAF50; font-size: 10px; font-weight: bold;">
                            ✓ By clicking [APPROVE], this mutation will be applied to your next spawn (10 babies)
                        </div>
                    `;
                    
                    document.getElementById('rockyContent').innerHTML = rockyHtml;
                    rockyDecisionButtons.style.display = 'flex';
                } else {
                    document.getElementById('rockyContent').innerHTML = `<div style="color: #FF5252;">Error: ${data.error}</div>`;
                    rockyDecisionButtons.style.display = 'none';
                }
            } catch (e) {
                document.getElementById('rockyContent').innerHTML = `<div style="color: #FF5252;">Error: ${e.message}</div>`;
                rockyDecisionButtons.style.display = 'none';
            } finally {
                rockyInsightBtn.disabled = false;
                rockyInsightBtn.textContent = '[Generate Insight]';
            }
        });
    }
    
    // Decision Button Handlers
    if (rockyApproveBtn) {
        rockyApproveBtn.addEventListener('click', async () => {
            if (!currentRockyInsight) {
                alert('No insight to approve');
                return;
            }
            
            console.log('[ROCKY] Recording APPROVED decision');
            rockyApproveBtn.disabled = true;
            
            try {
                const response = await fetch('/api/rocky/decision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        decision: 'APPROVED',
                        run_id: currentRockyInsight.run_id,
                        bot_id: currentRockyInsight.bot_id
                    })
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    rockyApproveBtn.textContent = '✓ APPROVED';
                    rockyApproveBtn.style.opacity = '0.6';
                    rockyRejectBtn.disabled = true;
                    rockyRejectBtn.style.opacity = '0.3';
                    console.log('[ROCKY] Decision recorded');
                    
                    // FIX: Clear after 2s so user can generate new insight
                    setTimeout(() => {
                        rockyDecisionButtons.style.display = 'none';
                        rockyInsightBtn.disabled = false;
                        rockyInsightBtn.textContent = '[Generate Insight]';
                        document.getElementById('rockyContent').innerHTML = '<div style="color: #666;">Ready for next insight...</div>';
                    }, 2000);
                } else {
                    alert('Failed to record decision');
                    rockyApproveBtn.disabled = false;
                }
            } catch (e) {
                alert('Error: ' + e.message);
                rockyApproveBtn.disabled = false;
            }
        });
    }
    
    if (rockyRejectBtn) {
        rockyRejectBtn.addEventListener('click', async () => {
            if (!currentRockyInsight) {
                alert('No insight to reject');
                return;
            }
            
            console.log('[ROCKY] Recording REJECTED decision');
            rockyRejectBtn.disabled = true;
            
            try {
                const response = await fetch('/api/rocky/decision', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        decision: 'REJECTED',
                        run_id: currentRockyInsight.run_id,
                        bot_id: currentRockyInsight.bot_id
                    })
                });
                
                const data = await response.json();
                if (data.status === 'success') {
                    rockyRejectBtn.textContent = '✗ REJECTED';
                    rockyRejectBtn.style.opacity = '0.6';
                    rockyApproveBtn.disabled = true;
                    rockyApproveBtn.style.opacity = '0.3';
                    console.log('[ROCKY] Decision recorded');
                    
                    // FIX: Clear after 2s so user can generate new insight
                    setTimeout(() => {
                        rockyDecisionButtons.style.display = 'none';
                        rockyInsightBtn.disabled = false;
                        rockyInsightBtn.textContent = '[Generate Insight]';
                        document.getElementById('rockyContent').innerHTML = '<div style="color: #666;">Ready for next insight...</div>';
                    }, 2000);
                } else {
                    alert('Failed to record decision');
                    rockyRejectBtn.disabled = false;
                }
            } catch (e) {
                alert('Error: ' + e.message);
                rockyRejectBtn.disabled = false;
            }
        });
    }

    // PHASE 4: Mutation Status Polling
    let mutationCheckInterval = null;
    
    async function checkMutationStatus() {
        try {
            const response = await fetch('/api/rocky/mutation_status');
            const data = await response.json();
            
            const banner = document.getElementById('mutationBanner');
            if (data.has_pending_mutation) {
                banner.style.display = 'flex';
                console.log('[PHASE 4] Mutation ready:', data.mutation_summary);
            } else {
                banner.style.display = 'none';
            }
        } catch (e) {
            console.log('[PHASE 4] Error checking mutation status:', e.message);
        }
    }
    
    // Check on page load
    checkMutationStatus();
    
    // Poll every 3 seconds
    mutationCheckInterval = setInterval(checkMutationStatus, 3000);
    
    // Mutation applied confirmation
    window.showMutationApplied = function() {
        const banner = document.getElementById('mutationBanner');
        if (banner) {
            const originalHTML = banner.innerHTML;
            banner.innerHTML = '<div style="display: flex; align-items: center; gap: 12px;"><span style="font-size: 20px;">✓</span><div style="flex: 1;"><strong>Mutation Applied</strong><br><span style="font-size: 12px; color: #ccc;">New generation created from approved proposal.</span></div></div>';
            banner.style.background = '#0d3818';
            setTimeout(() => {
                banner.innerHTML = originalHTML;
                banner.style.display = 'none';
                banner.style.background = '#1b5e20';
            }, 3000);
        }
    };


    // PHASE 6: Mutation Results Polling
    async function checkMutationResults() {
        try {
            const response = await fetch('/api/mutation/results');
            const data = await response.json();
            
            const panel = document.getElementById('mutationResultsContent');
            
            if (data.has_results && data.result) {
                const r = data.result;
                const resultColor = r.result === 'HELPED' ? '#4CAF50' : (r.result === 'HURT' ? '#FF5252' : '#FFD54F');
                
                let resultsHtml = `
                    <div style="margin-bottom: 12px;">
                        <div style="color: #00d4ff; margin-bottom: 8px;">
                            <strong>${r.mutation_type} Mutation (Gen ${r.generation})</strong>
                        </div>
                        <div style="color: ${resultColor}; font-size: 13px; font-weight: bold; margin-bottom: 12px;">
                            Result: ${r.result}
                        </div>
                    </div>
                    
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px;">
                        <div>
                            <div style="color: #888; font-size: 10px; margin-bottom: 4px;">CONTROL (${r.control.count} babies)</div>
                            <div style="border-left: 2px solid #666; padding-left: 8px; color: #aaa; font-size: 10px; line-height: 1.6;">
                                PnL: ${(r.control.avg_pnl * 10000).toFixed(1)} bps<br>
                                Flip: ${r.control.avg_flip_rate.toFixed(1)}%<br>
                                DD: ${r.control.avg_drawdown.toFixed(1)}%<br>
                                Survival: ${r.control.survival_rate.toFixed(1)}%
                            </div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 10px; margin-bottom: 4px;">MUTATED (${r.mutated.count} babies)</div>
                            <div style="border-left: 2px solid #00d4ff; padding-left: 8px; color: #aaa; font-size: 10px; line-height: 1.6;">
                                PnL: ${(r.mutated.avg_pnl * 10000).toFixed(1)} bps<br>
                                Flip: ${r.mutated.avg_flip_rate.toFixed(1)}%<br>
                                DD: ${r.mutated.avg_drawdown.toFixed(1)}%<br>
                                Survival: ${r.mutated.survival_rate.toFixed(1)}%
                            </div>
                        </div>
                    </div>
                `;
                
                panel.innerHTML = resultsHtml;
            } else {
                panel.innerHTML = '<div style="color: #666;">Waiting for mutation results...</div>';
            }
        } catch (e) {
            console.log('[PHASE 6] Error checking results:', e.message);
        }
    }
    
    // Check on page load
    checkMutationResults();
    
    // Poll every 5 seconds
    setInterval(checkMutationResults, 5000);


    // PHASE 7: Trajectory Polling
    async function checkTrajectory() {
        try {
            const response = await fetch('/api/trajectory');
            const data = await response.json();
            
            const panel = document.getElementById('trajectoryContent');
            
            if (data.has_trajectory && data.trajectory) {
                const t = data.trajectory;
                
                const getColor = (traj) => {
                    if (traj === 'IMPROVING') return '#4CAF50';
                    if (traj === 'DEGRADING') return '#FF5252';
                    return '#FFD54F';
                };
                
                let trajHtml = `
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                        <div>
                            <div style="color: #888; font-size: 10px; margin-bottom: 8px;">CONTROL</div>
                            <div style="border-left: 2px solid #666; padding-left: 8px; color: #aaa; font-size: 10px; line-height: 1.8;">
                                ↑ Improving: ${t.control.improving_pct.toFixed(0)}%<br>
                                ↓ Degrading: ${t.control.degrading_pct.toFixed(0)}%<br>
                                → Stable: ${t.control.stable_pct.toFixed(0)}%
                            </div>
                            <div style="margin-top: 8px; color: ${getColor(t.control.trajectory)}; font-weight: bold; font-size: 11px;">
                                ${t.control.trajectory}
                            </div>
                        </div>
                        <div>
                            <div style="color: #888; font-size: 10px; margin-bottom: 8px;">MUTATED</div>
                            <div style="border-left: 2px solid #00d4ff; padding-left: 8px; color: #aaa; font-size: 10px; line-height: 1.8;">
                                ↑ Improving: ${t.mutated.improving_pct.toFixed(0)}%<br>
                                ↓ Degrading: ${t.mutated.degrading_pct.toFixed(0)}%<br>
                                → Stable: ${t.mutated.stable_pct.toFixed(0)}%
                            </div>
                            <div style="margin-top: 8px; color: ${getColor(t.mutated.trajectory)}; font-weight: bold; font-size: 11px;">
                                ${t.mutated.trajectory}
                            </div>
                        </div>
                    </div>
                `;
                
                panel.innerHTML = trajHtml;
            } else {
                panel.innerHTML = '<div style="color: #666;">Waiting for trajectory analysis...</div>';
            }
        } catch (e) {
            console.log('[PHASE 7] Error checking trajectory:', e.message);
        }
    }
    
    // Check on page load
    checkTrajectory();
    
    // Poll every 5 seconds
    setInterval(checkTrajectory, 5000);


    // PHASE 8: Control Layer Polling
    async function checkControl() {
        try {
            const response = await fetch('/api/control');
            const data = await response.json();
            
            const panel = document.getElementById('controlContent');
            
            if (data.decision) {
                const d = data.decision;
                
                let actionColor = '#FFD54F';
                if (d.action === 'STOP') actionColor = '#FF5252';
                else if (d.action === 'THROTTLE') actionColor = '#FFA726';
                else if (d.action === 'SWITCH') actionColor = '#AB47BC';
                else if (d.action === 'WARMUP') actionColor = '#64B5F6';
                else if (d.action === 'NORMAL') actionColor = '#4CAF50';
                
                let controlHtml = `
                    <div style="margin-bottom: 12px;">
                        <div style="color: ${actionColor}; font-size: 13px; font-weight: bold; margin-bottom: 8px;">
                            ${d.action}
                        </div>
                        <div style="color: #aaa; font-size: 10px; line-height: 1.6; margin-bottom: 10px;">
                            ${d.reason}
                        </div>
                    </div>
                    
                    <div style="border-top: 1px solid #333; padding-top: 8px; color: #888; font-size: 9px; line-height: 1.5;">
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                            <div>
                                PnL: ${d.metrics_snapshot.pnl_bps.toFixed(1)} bps<br>
                                Trades: ${d.metrics_snapshot.total_trades}
                            </div>
                            <div>
                                DD: ${d.metrics_snapshot.drawdown_pct.toFixed(1)}%<br>
                                Survival: ${d.metrics_snapshot.survival_pass ? '✓' : '✗'}
                            </div>
                        </div>
                    </div>
                `;
                
                panel.innerHTML = controlHtml;
            } else {
                panel.innerHTML = '<div style="color: #666;">Error evaluating control...</div>';
            }
        } catch (e) {
            console.log('[PHASE 8] Error checking control:', e.message);
        }
    }
    
    // Check on page load
    checkControl();
    
    // Poll every 3 seconds (faster than other panels)
    setInterval(checkControl, 3000);

