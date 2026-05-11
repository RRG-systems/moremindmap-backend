/**
 * THINK Chat Handler
 * Converts THINK diagnostic engine into constrained chat interface
 * 
 * PHASE 10.2 CONSTRAINTS:
 * - No guessing, no hallucination
 * - Max 3 patterns per analysis
 * - 1 adjustment max per recommendation
 * - Output "Insufficient evidence" if data weak
 * - Natural language but strictly structured
 */

class ThinkChatHandler {
    constructor() {
        this.emptyState = document.getElementById('thinkEmptyState');
        this.chatBox = document.getElementById('thinkChatBox');
        this.messagesContainer = document.getElementById('thinkMessages');
        this.input = document.getElementById('thinkInput');
        this.sendBtn = document.getElementById('thinkSendBtn');
        this.exampleBtns = document.querySelectorAll('.example-btn');
        
        this.setupListeners();
        console.log('[THINK CHAT] Handler initialized');
    }
    
    setupListeners() {
        // Example button clicks
        this.exampleBtns.forEach(btn => {
            btn.addEventListener('click', () => {
                const query = btn.dataset.query;
                this.sendQuery(this.getQueryLabel(query));
            });
        });
        
        // Input field
        this.input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendQuery(this.input.value);
            }
        });
        
        // Send button
        this.sendBtn.addEventListener('click', () => {
            this.sendQuery(this.input.value);
        });
    }
    
    getQueryLabel(queryType) {
        const labels = {
            'analyze': 'Analyze',
            'why_stopped': 'Why stopped?',
            'why_flat': 'Why flat?',
            'biggest_problem': 'Biggest problem?',
            'next_adjustment': 'Next adjustment?',
        };
        return labels[queryType] || queryType;
    }
    
    async sendQuery(query) {
        if (!query.trim()) {
            return;
        }
        
        console.log('[THINK CHAT] Sending query:', query);
        
        // Clear input
        this.input.value = '';
        
        // Show chat box (hide empty state)
        this.emptyState.classList.add('hidden');
        this.chatBox.classList.remove('hidden');
        
        // Add user message to chat
        this.addMessage('user', query);
        
        // Show loading indicator
        this.addMessage('system', '⏳ Analyzing...');
        
        try {
            // Send query to backend
            const response = await fetch('/api/think/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(() => ({}));
                throw new Error(errorData.message || `HTTP ${response.status}`);
            }
            
            const data = await response.json();
            
            if (data.status === 'success') {
                // Remove loading message
                const lastMsg = this.messagesContainer.lastElementChild;
                if (lastMsg && lastMsg.dataset.role === 'system') {
                    lastMsg.remove();
                }
                
                // Display response
                this.displayResponse(data.response, data.analysis_type);
            } else {
                throw new Error(data.message || 'API returned error');
            }
        } catch (error) {
            console.error('[THINK CHAT] Error:', error);
            
            // Remove loading message
            const lastMsg = this.messagesContainer.lastElementChild;
            if (lastMsg && lastMsg.dataset.role === 'system') {
                lastMsg.remove();
            }
            
            this.addMessage('error', `✗ Error: ${error.message}`);
        }
    }
    
    displayResponse(responseData, analysisType) {
        let content = '';
        
        // Main answer
        if (responseData.answer) {
            content += `<div class="think-answer">${responseData.answer}</div>`;
        }
        
        // Patterns (for analysis types that have them)
        if (responseData.patterns && responseData.patterns.length > 0) {
            content += `<div class="think-patterns">`;
            content += `<div class="patterns-label">Identified patterns:</div>`;
            responseData.patterns.forEach((pattern, idx) => {
                content += `<div class="pattern-item">• ${pattern}</div>`;
            });
            content += `</div>`;
        }
        
        // Recommendation
        if (responseData.recommendation) {
            content += `<div class="think-recommendation">`;
            content += `<div class="recommendation-label">💡 Recommendation:</div>`;
            content += `<div class="recommendation-text">${responseData.recommendation}</div>`;
            content += `</div>`;
        }
        
        // Confidence (if available)
        if (typeof responseData.confidence === 'number') {
            const confidenceLevel = responseData.confidence >= 0.7 ? 'high' : 
                                   responseData.confidence >= 0.4 ? 'medium' : 'low';
            content += `<div class="think-confidence confidence-${confidenceLevel}">Confidence: ${Math.round(responseData.confidence * 100)}%</div>`;
        }
        
        this.addMessage('think', content);
    }
    
    addMessage(role, content) {
        const messageEl = document.createElement('div');
        messageEl.className = `think-message think-message-${role}`;
        messageEl.dataset.role = role;
        
        if (role === 'user') {
            messageEl.innerHTML = `<div class="message-content">${this.escapeHtml(content)}</div>`;
        } else if (role === 'error') {
            messageEl.innerHTML = `<div class="message-content error-text">${content}</div>`;
        } else if (role === 'system') {
            messageEl.innerHTML = `<div class="message-content system-text">${content}</div>`;
        } else {
            // THINK response (contains HTML)
            messageEl.innerHTML = `<div class="message-content">${content}</div>`;
        }
        
        this.messagesContainer.appendChild(messageEl);
        
        // Auto-scroll to bottom
        this.messagesContainer.parentElement.scrollTop = this.messagesContainer.parentElement.scrollHeight;
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.thinkChatHandler = new ThinkChatHandler();
    });
} else {
    window.thinkChatHandler = new ThinkChatHandler();
}
