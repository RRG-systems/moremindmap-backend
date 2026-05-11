/**
 * ROCKY inside THINK — Conversational Panel UI v3
 * 
 * Real conversation. No templates. Raw Rocky.
 * - Free-text input (blank on load)
 * - Conversational flow
 * - Auto-scroll to latest
 * - Support markdown formatting
 */

class RockyThinkPanel {
    constructor() {
        this.messagesContainer = document.getElementById('thinkMessages');
        this.inputBox = document.getElementById('thinkInput');
        this.sendBtn = document.getElementById('thinkSendBtn');
        this.emptyState = document.getElementById('thinkEmptyState');
        this.chatBox = document.getElementById('thinkChatBox');
        this.currentQueryId = null;
        
        this.setupEventListeners();
        this.logInit();
    }
    
    setupEventListeners() {
        if (this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.submit());
        }
        
        if (this.inputBox) {
            this.inputBox.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.submit();
                }
            });
        }
    }
    
    logInit() {
        console.log('[ROCKY THINK PANEL] Initialized');
        console.log('  Input:', this.inputBox ? '✓' : '✗');
        console.log('  Send button:', this.sendBtn ? '✓' : '✗');
        console.log('  Messages:', this.messagesContainer ? '✓' : '✗');
    }
    
    async submit() {
        const query = this.inputBox?.value?.trim();
        
        if (!query) {
            console.log('[ROCKY] Empty query, ignoring');
            return;
        }
        
        console.log('[ROCKY THINK] Submitting query:', query);
        
        // Add user message to UI
        this.addMessage('user', query);
        
        // Clear input
        if (this.inputBox) {
            this.inputBox.value = '';
        }
        
        // Send to operator and wait for response
        try {
            console.log('[THINK] Sending to operator...');
            
            const response = await fetch('/api/think/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ query: query })
            });
            
            if (!response.ok) {
                const text = await response.text();
                console.error('[THINK ERROR]', response.status, text);
                this.addMessage('rocky', `Error: ${response.status}`);
                return;
            }
            
            const data = await response.json();
            this.currentQueryId = data.query_id;
            
            if (data.status === 'success') {
                // Got response immediately
                this.addMessage('rocky', data.answer);
            } else if (data.status === 'waiting') {
                // Operator is working. Poll for response.
                this.addMessage('rocky', '...');
                this.pollForResponse();
            } else {
                this.addMessage('rocky', `${data.message}`);
            }
            
        } catch (err) {
            console.error('[THINK ERROR]', err.message);
            this.addMessage('rocky', `Error: ${err.message}`);
        }
    }
    
    async pollForResponse() {
        // Poll for operator response every 500ms, up to 30 seconds
        let attempts = 0;
        const maxAttempts = 60;
        
        const poll = async () => {
            attempts++;
            
            try {
                const response = await fetch('/api/think/query', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ query_id: this.currentQueryId })
                });
                
                if (!response.ok) return;
                
                const data = await response.json();
                
                if (data.status === 'success' && data.answer) {
                    // Got response! Remove the "..." placeholder
                    const messages = this.messagesContainer.querySelectorAll('.think-message-rocky');
                    if (messages.length > 0) {
                        const lastMessage = messages[messages.length - 1];
                        if (lastMessage.textContent === '...') {
                            lastMessage.remove();
                        }
                    }
                    this.addMessage('rocky', data.answer);
                    return;
                }
            } catch (err) {
                console.error('[POLL ERROR]', err.message);
            }
            
            if (attempts < maxAttempts) {
                setTimeout(poll, 500);
            } else {
                // Timeout
                const messages = this.messagesContainer.querySelectorAll('.think-message-rocky');
                if (messages.length > 0) {
                    const lastMessage = messages[messages.length - 1];
                    if (lastMessage.textContent === '...') {
                        lastMessage.textContent = 'Timeout waiting for response.';
                    }
                }
            }
        };
        
        poll();
    }
    
    addMessage(role, text) {
        // Create message element
        const msgDiv = document.createElement('div');
        msgDiv.className = `think-message think-message-${role}`;
        
        // Parse markdown
        const html = this.parseMarkdown(text);
        msgDiv.innerHTML = html;
        
        // Add to container
        if (this.messagesContainer) {
            this.messagesContainer.appendChild(msgDiv);
            
            // Auto-scroll to bottom
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
        
        // Show chat box, hide empty state
        if (this.chatBox) {
            this.chatBox.classList.remove('hidden');
        }
        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
        
        console.log(`[THINK MESSAGE] ${role}: ${text.substring(0, 50)}...`);
    }
    
    parseMarkdown(text) {
        // Basic markdown support
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')  // bold
            .replace(/\*(.*?)\*/g, '<em>$1</em>')              // italic
            .replace(/`(.*?)`/g, '<code>$1</code>')            // inline code
            .replace(/\n/g, '<br>');                            // newlines
        
        return html;
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[THINK PANEL] Loading Rocky...');
    window.rockyThinkPanel = new RockyThinkPanel();
});
