/**
 * BRAIN Panel Status Poller
 * Handles BRAIN status updates only (THINK is handled separately in think_chat_handler_fixed.js)
 */

class BrainStatusPoller {
    constructor() {
        this.brainStatusContent = document.getElementById('brainStatusContent');
        
        if (!this.brainStatusContent) {
            console.error('[BRAIN] ERROR: brainStatusContent element not found');
            return;
        }
        
        console.log('[BRAIN] Status poller initialized');
        
        // Start polling immediately and every 2 seconds
        this.updateBrainStatus();
        setInterval(() => this.updateBrainStatus(), 2000);
    }
    
    async updateBrainStatus() {
        try {
            const response = await fetch('/api/brain/status');
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }
            
            const data = await response.json();
            this.displayBrainStatus(data);
        } catch (error) {
            console.error('[BRAIN] Status update error:', error);
            if (this.brainStatusContent) {
                this.brainStatusContent.innerHTML = `<div style="color: #ff6b6b;">Error loading BRAIN status</div>`;
            }
        }
    }
    
    displayBrainStatus(data) {
        if (!this.brainStatusContent) return;
        
        const state = data.state || 'UNKNOWN';
        const reason = data.reason_code || 'unknown';
        const text = data.reason_text || 'No reason available';
        const enforcement = data.enforcement || {};
        
        // Determine state color and icon
        let stateColor = '#888';
        let stateIcon = '⚪';
        
        switch(state) {
            case 'NORMAL':
                stateColor = '#4CAF50';
                stateIcon = '🟢';
                break;
            case 'THROTTLE':
                stateColor = '#FF9800';
                stateIcon = '🟡';
                break;
            case 'FLAT':
                stateColor = '#ffb74d';
                stateIcon = '🟠';
                break;
            case 'STOP':
                stateColor = '#f44336';
                stateIcon = '🔴';
                break;
            default:
                stateColor = '#999';
                stateIcon = '⚪';
        }
        
        // Build HTML content
        let html = `
            <div style="color: ${stateColor}; margin-bottom: 12px; font-weight: bold; font-size: 13px;">${stateIcon} State: <strong>${state}</strong></div>
            <div style="color: #aaa; font-size: 11px; margin-bottom: 8px;">Reason: <strong>${reason}</strong></div>
            <div style="color: #666; font-size: 10px; margin-bottom: 12px;">${text}</div>
        `;
        
        // Add enforcement flags
        html += '<div style="color: #aaa; font-size: 11px; font-weight: bold; margin-bottom: 6px;">Enforcement:</div>';
        
        if (enforcement.trading_blocked) {
            html += '<div style="color: #f44336; font-size: 10px; margin-left: 8px;">⛔ Trading Blocked</div>';
        } else if (enforcement.trading_throttled) {
            html += '<div style="color: #FF9800; font-size: 10px; margin-left: 8px;">⚠️ Trading Throttled (50% size)</div>';
        } else {
            html += '<div style="color: #4CAF50; font-size: 10px; margin-left: 8px;">✓ Trading Allowed (100% size)</div>';
        }
        
        if (enforcement.no_active_strategy) {
            html += '<div style="color: #7a8fa3; font-size: 10px; margin-left: 8px;">🔇 No Active Strategy</div>';
        }
        
        this.brainStatusContent.innerHTML = html;
    }
}

// Initialize BRAIN poller when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.brainPoller = new BrainStatusPoller();
    });
} else {
    window.brainPoller = new BrainStatusPoller();
}
