// RESTART SIMULATION HANDLER
// Reload simulation from CSV (persistent, non-destructive)

document.addEventListener('DOMContentLoaded', () => {
    const restartSimBtn = document.getElementById('restartSimBtn');
    if (!restartSimBtn) return;
    
    restartSimBtn.addEventListener('click', async () => {
        console.log('[RESTART] Restart Simulation button clicked');
        
        if (!confirm('Restart simulation from CSV state?\n\nThis reloads from saved data without losing equity.')) {
            return;
        }
        
        try {
            const response = await fetch('/api/restart-simulation', { method: 'POST' });
            const result = await response.json();
            
            if (result.status === 'restart_complete') {
                console.log('[RESTART] Success:', result);
                alert(
                    'Simulation restarted!\n' +
                    'Paper: $' + result.paper_pnl + '\n' +
                    'Shadow: $' + result.shadow_pnl + '\n' +
                    'Trades: ' + result.paper_trades
                );
                location.reload();
            } else {
                alert('Restart failed: ' + result.message);
            }
        } catch (e) {
            alert('Error restarting simulation: ' + e);
            console.error('[RESTART] Error:', e);
        }
    });
});
