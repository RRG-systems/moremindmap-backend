// THINK Chat Handler - Fixed for correct endpoint response structure

class ThinkChatHandler {
    constructor() {
        this.inputBox = document.getElementById('thinkInput');
        this.sendBtn = document.getElementById('thinkSendBtn');
        this.messagesContainer = document.getElementById('thinkMessages');
        this.emptyState = document.getElementById('thinkEmptyState');
        this.chatBox = document.getElementById('thinkChatBox');
        
        console.log('[THINK CHAT] Initializing with elements:', {
            input: this.inputBox ? 'found' : 'NOT FOUND',
            button: this.sendBtn ? 'found' : 'NOT FOUND',
            messages: this.messagesContainer ? 'found' : 'NOT FOUND',
        });
        
        if (this.inputBox && this.sendBtn) {
            this.sendBtn.addEventListener('click', () => this.handleSubmit());
            this.inputBox.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.handleSubmit();
                }
            });
            console.log('[THINK CHAT] Event listeners attached');
        } else {
            console.error('[THINK CHAT] ERROR: Missing required elements');
        }
    }
    
    addMessage(role, text) {
        if (!this.messagesContainer) return;
        
        const msgDiv = document.createElement('div');
        msgDiv.className = `think-message think-message-${role}`;
        msgDiv.dataset.role = role;
        msgDiv.innerHTML = `<div class="think-message-content">${text}</div>`;
        
        this.messagesContainer.appendChild(msgDiv);
        
        // Scroll both containers to bottom
        setTimeout(() => {
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
            if (this.chatBox) this.chatBox.scrollTop = this.chatBox.scrollHeight;
        }, 0);
    }
    
    async handleSubmit() {
        if (!this.inputBox) {
            console.error('[THINK CHAT] Input box not found');
            return;
        }
        
        const query = this.inputBox.value.trim();
        if (!query) return;
        
        console.log('[THINK CHAT] Submitting query:', query);
        
        // Show user message
        this.addMessage('user', query);
        this.inputBox.value = '';
        
        // Show loading
        this.addMessage('system', '⏳ Analyzing...');
        
        try {
            const response = await fetch('/api/think/query', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ query })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();
            console.log('[THINK CHAT] Response received:', data);
            
            // Remove loading message
            const lastMsg = this.messagesContainer.lastElementChild;
            if (lastMsg && lastMsg.dataset.role === 'system') {
                lastMsg.remove();
            }
            
            if (data.status === 'success') {
                // Display response with proper structure
                let responseText = data.answer || 'No answer available';
                
                if (data.confidence !== undefined) {
                    responseText += `\n\n[Confidence: ${Math.round(data.confidence * 100)}%]`;
                }
                
                this.addMessage('assistant', responseText);
                
                // Hide empty state
                if (this.emptyState) {
                    this.emptyState.style.display = 'none';
                }
                if (this.chatBox) {
                    this.chatBox.classList.remove('hidden');
                }
            } else {
                throw new Error(data.message || 'Unknown API error');
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
}

// Initialize on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('[THINK] Initializing chat handler...');
        window.thinkChatHandler = new ThinkChatHandler();
    });
} else {
    console.log('[THINK] DOM already loaded, initializing chat handler...');
    window.thinkChatHandler = new ThinkChatHandler();
}
