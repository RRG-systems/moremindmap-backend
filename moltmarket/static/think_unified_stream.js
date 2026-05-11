/**
 * THINK Unified Stream — OpenClaw ↔ Dashboard bidirectional pipe
 * 
 * Everything typed here appears in THINK
 * Everything in THINK appears here
 * One conversation, two interfaces
 */

class ThinkUnifiedStream {
    constructor() {
        this.messagesContainer = document.getElementById('thinkMessages');
        this.inputBox = document.getElementById('thinkInput');
        this.sendBtn = document.getElementById('thinkSendBtn');
        this.emptyState = document.getElementById('thinkEmptyState');
        this.chatBox = document.getElementById('thinkChatBox');
        
        this.lastMessageTime = null;
        this.setupEventListeners();
        this.startPolling();
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
        console.log('[THINK UNIFIED] Connected to session');
    }
    
    async submit() {
        const text = this.inputBox?.value?.trim();
        
        if (!text) {
            console.log('[THINK] Empty input');
            return;
        }
        
        console.log('[THINK] Sending:', text);
        
        // Add user message locally
        this.addMessage('user', text);
        
        // Clear input
        if (this.inputBox) {
            this.inputBox.value = '';
        }
        
        // Send to backend
        try {
            const response = await fetch('/api/think/message', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ role: 'user', text: text })
            });
            
            if (!response.ok) {
                console.error('[THINK ERROR]', response.status);
            }
        } catch (err) {
            console.error('[THINK SEND ERROR]', err.message);
        }
    }
    
    addMessage(role, text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `think-message think-message-${role}`;
        
        // Parse markdown
        const html = this.parseMarkdown(text);
        msgDiv.innerHTML = html;
        
        if (this.messagesContainer) {
            this.messagesContainer.appendChild(msgDiv);
            this.messagesContainer.scrollTop = this.messagesContainer.scrollHeight;
        }
        
        // Show chat box, hide empty state
        if (this.chatBox) {
            this.chatBox.classList.remove('hidden');
        }
        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
    }
    
    parseMarkdown(text) {
        let html = text
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/`(.*?)`/g, '<code>$1</code>')
            .replace(/\n/g, '<br>');
        return html;
    }
    
    startPolling() {
        // Poll for new messages every 500ms
        setInterval(() => this.pollMessages(), 500);
    }
    
    async pollMessages() {
        try {
            const url = this.lastMessageTime 
                ? '/api/think/messages/since'
                : '/api/think/messages';
            
            const body = this.lastMessageTime 
                ? { timestamp: this.lastMessageTime }
                : null;
            
            const response = await fetch(url, {
                method: this.lastMessageTime ? 'POST' : 'GET',
                headers: { 'Content-Type': 'application/json' },
                ...(body && { body: JSON.stringify(body) })
            });
            
            if (!response.ok) return;
            
            const data = await response.json();
            const messages = data.messages || [];
            
            for (const msg of messages) {
                this.addMessage(msg.role, msg.text);
                this.lastMessageTime = msg.timestamp;
            }
        } catch (err) {
            console.error('[THINK POLL ERROR]', err.message);
        }
    }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[THINK UNIFIED] Loading...');
    window.thinkUnifiedStream = new ThinkUnifiedStream();
});
