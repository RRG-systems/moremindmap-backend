/**
 * THINK Panel — ROCKY Diagnostic UI (Polished)
 * 
 * Conversational interface for operator queries.
 * Clean, fast, responsive.
 */

(function() {
  const PANEL_ID = 'think-panel';
  const INPUT_ID = 'think-query-input';
  const MESSAGES_ID = 'think-messages';
  const SEND_BTN_ID = 'think-send-btn';
  
  const QUERY_ENDPOINT = '/api/think/query';
  
  class ThinkRockyPanel {
    constructor() {
      this.panel = null;
      this.input = null;
      this.messages = null;
      this.sendBtn = null;
      this.isLoading = false;
      this.init();
    }
    
    init() {
      this.panel = document.getElementById(PANEL_ID);
      this.input = document.getElementById(INPUT_ID);
      this.messages = document.getElementById(MESSAGES_ID);
      this.sendBtn = document.getElementById(SEND_BTN_ID);
      
      if (!this.panel || !this.input || !this.messages) {
        console.error('[THINK] Panel elements not found');
        return;
      }
      
      this.attachEventListeners();
      this.showWelcome();
    }
    
    attachEventListeners() {
      // Send on Enter (Shift+Enter for newline)
      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
          e.preventDefault();
          this.send();
        }
      });
      
      // Clear on Esc
      this.input.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
          this.input.value = '';
          this.input.focus();
        }
      });
      
      // Send button
      if (this.sendBtn) {
        this.sendBtn.addEventListener('click', () => this.send());
      }
    }
    
    showWelcome() {
      this.addSystemMessage('Welcome to THINK. Ask me anything about BRAIN, Nursery, Arena, or system health.');
      this.addSystemMessage('Examples: "What is BRAIN doing?" / "How\\'s the Nursery?" / "Is Arena valid?"');
    }
    
    send() {
      const query = this.input.value.trim();
      
      if (!query) {
        return;
      }
      
      if (this.isLoading) {
        return;
      }
      
      // Show user query
      this.addUserMessage(query);
      this.input.value = '';
      
      // Send to Rocky
      this.isLoading = true;
      this.sendBtn.disabled = true;
      
      fetch(QUERY_ENDPOINT, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query })
      })
      .then(r => r.json())
      .then(data => {
        if (data.error) {
          this.addErrorMessage(`Error: ${data.error}`);
        } else {
          this.addRockyMessage(data);
        }
      })
      .catch(err => {
        this.addErrorMessage(`Network error: ${err.message}`);
      })
      .finally(() => {
        this.isLoading = false;
        this.sendBtn.disabled = false;
        this.input.focus();
      });
    }
    
    addUserMessage(text) {
      const msg = document.createElement('div');
      msg.className = 'think-message think-user';
      msg.innerHTML = `<div class="think-bubble">${this.escapeHtml(text)}</div>`;
      this.messages.appendChild(msg);
      this.scrollToBottom();
    }
    
    addRockyMessage(data) {
      const msg = document.createElement('div');
      msg.className = 'think-message think-rocky';
      
      const confidence = Math.round(data.confidence * 100);
      const confidenceClass = confidence >= 80 ? 'high' : confidence >= 60 ? 'medium' : 'low';
      
      let html = '<div class="think-bubble">';
      html += `<div class="think-diagnosis">${this.escapeHtml(data.diagnosis)}</div>`;
      
      if (data.evidence && data.evidence.length > 0) {
        html += '<div class="think-evidence">';
        for (const ev of data.evidence) {
          html += `<div class="think-evidence-item">• ${this.escapeHtml(ev)}</div>`;
        }
        html += '</div>';
      }
      
      html += `<div class="think-action">${this.escapeHtml(data.recommended_action)}</div>`;
      html += `<div class="think-confidence confidence-${confidenceClass}">${confidence}% confident</div>`;
      html += '</div>';
      
      msg.innerHTML = html;
      this.messages.appendChild(msg);
      this.scrollToBottom();
    }
    
    addSystemMessage(text) {
      const msg = document.createElement('div');
      msg.className = 'think-message think-system';
      msg.innerHTML = `<div class="think-bubble">${this.escapeHtml(text)}</div>`;
      this.messages.appendChild(msg);
      this.scrollToBottom();
    }
    
    addErrorMessage(text) {
      const msg = document.createElement('div');
      msg.className = 'think-message think-error';
      msg.innerHTML = `<div class="think-bubble">⚠️ ${this.escapeHtml(text)}</div>`;
      this.messages.appendChild(msg);
      this.scrollToBottom();
    }
    
    scrollToBottom() {
      this.messages.scrollTop = this.messages.scrollHeight;
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
      window.thinkPanel = new ThinkRockyPanel();
    });
  } else {
    window.thinkPanel = new ThinkRockyPanel();
  }
})();
