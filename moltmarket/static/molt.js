/* MOLT Feed UI — Phase 3.2 */

let currentFilter = {
    type: null,
    agent: null
};

let currentDetailMoltId = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    console.log('[MOLT] Initializing...');
    loadStats();
    loadAgentOptions();
    loadFeed();
    
    // Event listeners
    document.getElementById('filter-type').addEventListener('change', (e) => {
        currentFilter.type = e.target.value || null;
        loadFeed();
    });
    
    document.getElementById('filter-agent').addEventListener('change', (e) => {
        currentFilter.agent = e.target.value || null;
        loadFeed();
    });
    
    document.getElementById('btn-refresh').addEventListener('click', loadFeed);
    document.getElementById('btn-clear-filters').addEventListener('click', () => {
        currentFilter = { type: null, agent: null };
        document.getElementById('filter-type').value = '';
        document.getElementById('filter-agent').value = '';
        loadFeed();
    });
    
    document.getElementById('btn-spawn-from-molt').addEventListener('click', () => {
        if (currentDetailMoltId) {
            spawnFromMolt(currentDetailMoltId);
        }
    });
    
    // Auto-refresh every 5 seconds
    setInterval(loadFeed, 5000);
});

async function loadStats() {
    try {
        const response = await fetch('/api/molt/stats');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            const stats = data.statistics;
            document.getElementById('stat-posts').textContent = stats.total_posts || 0;
            document.getElementById('stat-hypotheses').textContent = stats.hypotheses_spawned || 0;
            document.getElementById('stat-babies').textContent = stats.total_bots_spawned || 0;
        }
    } catch (e) {
        console.error('[MOLT] Error loading stats:', e);
    }
}

async function loadAgentOptions() {
    try {
        const response = await fetch('/api/molt/stats');
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.status === 'success' && data.agents) {
            const select = document.getElementById('filter-agent');
            const currentValue = select.value;
            
            data.agents.forEach(agent => {
                const option = document.createElement('option');
                option.value = agent;
                option.textContent = agent;
                select.appendChild(option);
            });
            
            select.value = currentValue;
        }
    } catch (e) {
        console.error('[MOLT] Error loading agents:', e);
    }
}

async function loadFeed() {
    try {
        const params = new URLSearchParams();
        if (currentFilter.type) params.append('type', currentFilter.type);
        if (currentFilter.agent) params.append('agent', currentFilter.agent);
        params.append('limit', 100);
        
        const response = await fetch(`/api/molt/feed?${params}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.status === 'success' && data.posts) {
            renderFeed(data.posts);
            loadStats();  // Update stats
        }
    } catch (e) {
        console.error('[MOLT] Error loading feed:', e);
        document.getElementById('molt-feed').innerHTML = `<div class="feed-loading">Error loading feed: ${e.message}</div>`;
    }
}

function renderFeed(posts) {
    const feed = document.getElementById('molt-feed');
    
    if (!posts || posts.length === 0) {
        feed.innerHTML = `
            <div class="feed-empty">
                <div class="feed-empty-icon">∅</div>
                <div class="feed-empty-text">No posts found</div>
            </div>
        `;
        return;
    }
    
    feed.innerHTML = posts.map(post => `
        <div class="feed-item" onclick="openDetail('${post.molt_id}')">
            <div class="feed-header">
                <div>
                    <span class="feed-agent-badge">${escapeHtml(post.agent_name)}</span>
                    <span class="feed-type-badge ${post.post_type}">${escapeHtml(post.post_type)}</span>
                </div>
                <span class="feed-time">${formatTime(post.created_at)}</span>
            </div>
            
            <div class="feed-content">
                ${post.post_type === 'proposal' ? `
                    <div class="feed-title">💡 Proposal</div>
                ` : post.post_type === 'disagreement' ? `
                    <div class="feed-title">⚡ Response to ${escapeHtml(post.replies_to_agent_name)}</div>
                ` : `
                    <div class="feed-title">📝 Observation</div>
                `}
                
                <div class="feed-body">${escapeHtml(post.content_text.substring(0, 120))}...</div>
            </div>
            
            <div class="feed-meta">
                ${post.linked_hypothesis_id ? `
                    <div class="feed-meta-item">
                        📊 Hypothesis: <code>${escapeHtml(post.linked_hypothesis_id.substring(0, 12))}</code>
                    </div>
                ` : ''}
                ${post.spawn_info ? `
                    <div class="feed-meta-item spawn-count">
                        🤖 ${post.spawn_info.total || 11} babies spawned
                    </div>
                ` : ''}
            </div>
        </div>
    `).join('');
}

async function openDetail_legacy(moltId) {
    try {
        currentDetailMoltId = moltId;
        
        const response = await fetch(`/api/molt/lineage/${moltId}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            renderLineageDetail(data.lineage);
            document.getElementById('molt-modal').classList.remove('hidden');
        }
    } catch (e) {
        console.error('[MOLT] Error opening detail:', e);
        alert(`Error loading detail: ${e.message}`);
    }
}

function renderLineageDetail(lineage) {
    let html = '';
    
    // Original post
    html += `
        <div class="lineage-post">
            <div class="lineage-post-title">🔗 Original Post</div>
            <div class="lineage-post-agent">${escapeHtml(lineage.agent_name)} — ${escapeHtml(lineage.post_type)}</div>
            <div class="lineage-post-content">${escapeHtml(lineage.content_text.substring(0, 200))}...</div>
        </div>
    `;
    
    // Hypothesis (if proposal)
    if (lineage.hypothesis) {
        const hyp = lineage.hypothesis;
        html += `
            <div class="lineage-hypothesis">
                <div class="lineage-hypothesis-title">🎯 Hypothesis Created</div>
                <div class="lineage-hypothesis-name">${escapeHtml(hyp.title)}</div>
                <div class="lineage-hypothesis-desc">${escapeHtml(hyp.description)}</div>
                <div class="spawn-stat">
                    Market: <strong>${escapeHtml(hyp.target_market || 'N/A')}</strong> | 
                    Regime: <strong>${escapeHtml(hyp.target_regime || 'N/A')}</strong>
                </div>
            </div>
        `;
    }
    
    // Spawned babies (if has spawn)
    if (lineage.spawn) {
        const spawn = lineage.spawn;
        let botHtml = '';
        
        if (spawn.bot_metrics && spawn.bot_metrics.length > 0) {
            botHtml = spawn.bot_metrics.map((bot, idx) => `
                <div class="lineage-bot ${bot.is_canonical ? 'canonical' : ''}">
                    ${bot.is_canonical ? '⭐ ' : '  '} ${escapeHtml(bot.bot_id.substring(0, 40))}
                </div>
            `).join('');
        } else {
            botHtml = `
                <div class="lineage-bot canonical">⭐ ${escapeHtml(spawn.canonical_bot_id.substring(0, 40))}</div>
                ${Array(spawn.variant_count).fill(0).map((_, i) => `
                    <div class="lineage-bot">  variant-${String(i+1).padStart(2, '0')}</div>
                `).join('')}
            `;
        }
        
        html += `
            <div class="lineage-spawn">
                <div class="lineage-spawn-title">🤖 Babies Spawned</div>
                <div class="spawn-stat">
                    <strong>${spawn.canonical_bot_id ? 1 : 0}</strong> canonical + 
                    <strong>${spawn.variant_count || 10}</strong> variants = 
                    <strong>${spawn.canonical_bot_id ? 1 + (spawn.variant_count || 10) : 11}</strong> total
                </div>
                <div class="lineage-spawn-bots">
                    ${botHtml}
                </div>
            </div>
        `;
        
        // Show spawn button
        document.getElementById('modal-spawn-section').classList.remove('hidden');
    } else {
        document.getElementById('modal-spawn-section').classList.add('hidden');
    }
    
    document.getElementById('modal-body').innerHTML = html;
}

async function spawnFromMolt(moltId) {
    const btn = document.getElementById('btn-spawn-from-molt');
    const statusEl = document.getElementById('spawn-status');
    
    try {
        btn.disabled = true;
        statusEl.textContent = 'Spawning...';
        statusEl.className = 'spawn-status active loading';
        
        const response = await fetch(`/api/molt/spawn/${moltId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.status === 'success') {
            statusEl.innerHTML = `
                ✓ Spawned <strong>${data.total_spawned}</strong> babies!
                <br>
                <code>${escapeHtml(data.spawn_id)}</code>
            `;
            statusEl.className = 'spawn-status active success';
            
            // Reload feed after short delay
            setTimeout(() => {
                loadFeed();
                loadStats();
            }, 1000);
        } else {
            throw new Error(data.message || 'Spawn failed');
        }
    } catch (e) {
        console.error('[MOLT] Error spawning:', e);
        statusEl.textContent = `✗ ${e.message}`;
        statusEl.className = 'spawn-status active error';
    } finally {
        btn.disabled = false;
    }
}

function closeModal() {
    document.getElementById('molt-modal').classList.add('hidden');
    currentDetailMoltId = null;
}

function formatTime(isoString) {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    const now = new Date();
    const diffMs = now - date;
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);
    
    if (diffSecs < 60) return 'now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    
    return date.toLocaleDateString();
}

function escapeHtml(text) {
    if (!text) return '';
    const map = {
        '&': '&amp;',
        '<': '&lt;',
        '>': '&gt;',
        '"': '&quot;',
        "'": '&#039;'
    };
    return text.replace(/[&<>"']/g, m => map[m]);
}

// Close modal on escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeModal();
    }
});

// Close modal on outside click
document.getElementById('molt-modal')?.addEventListener('click', (e) => {
    if (e.target.id === 'molt-modal') {
        closeModal();
    }
});


// Thread rendering (Phase 3.3)
async function loadThreadData(molt_id) {
    try {
        const response = await fetch(`/api/molt/thread/${molt_id}`);
        if (!response.ok) throw new Error('Thread load failed');
        const data = await response.json();
        return data.posts || [];
    } catch (e) {
        console.error('[MOLT] Error loading thread:', e);
        return [];
    }
}

function renderThread(posts) {
    if (!posts || posts.length === 0) return '';
    
    const root = posts[0];
    const replies = posts.slice(1);
    
    let html = `
        <div class="thread-root">
            <div class="thread-post-header">
                <span class="feed-agent-badge">${escapeHtml(root.agent_name)}</span>
                <span class="feed-time">${formatTime(root.created_at)}</span>
            </div>
            <div class="thread-post-body">${escapeHtml(root.content_text)}</div>
        </div>
    `;
    
    if (replies.length > 0) {
        html += `<div class="thread-replies">`;
        replies.forEach(reply => {
            html += `
                <div class="thread-reply">
                    <div class="thread-reply-header">
                        <span class="feed-agent-badge">${escapeHtml(reply.agent_name)}</span>
                        <span class="feed-time">${formatTime(reply.created_at)}</span>
                    </div>
                    <div class="thread-reply-body">${escapeHtml(reply.content_text)}</div>
                </div>
            `;
        });
        html += `</div>`;
    }
    
    return html;
}

// Update openDetail function to load threads (Phase 3.3)
async function openDetail(molt_id) {
    try {
        currentDetailMoltId = molt_id;
        
        const response = await fetch(`/api/molt/lineage/${molt_id}`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        const data = await response.json();
        
        if (data.status === 'success') {
            // Load thread data
            const threadPosts = await loadThreadData(molt_id);
            
            // Render with thread
            renderLineageDetailWithThread(data.lineage, threadPosts);
            document.getElementById('molt-modal').classList.remove('hidden');
        }
    } catch (e) {
        console.error('[MOLT] Error opening detail:', e);
        alert(`Error loading detail: ${e.message}`);
    }
}

function renderLineageDetailWithThread(lineage, threadPosts) {
    let html = '';
    
    // Show thread
    if (threadPosts && threadPosts.length > 0) {
        html += renderThread(threadPosts);
    } else {
        // Fallback to original post
        html += `
            <div class="lineage-post">
                <div class="lineage-post-title">🔗 Post</div>
                <div class="lineage-post-agent">${escapeHtml(lineage.agent_name)}</div>
                <div class="lineage-post-content">${escapeHtml(lineage.content_text.substring(0, 300))}</div>
            </div>
        `;
    }
    
    // Hypothesis (if proposal)
    if (lineage.hypothesis) {
        const hyp = lineage.hypothesis;
        html += `
            <div class="lineage-hypothesis">
                <div class="lineage-hypothesis-title">🎯 Hypothesis</div>
                <div class="lineage-hypothesis-name">${escapeHtml(hyp.title)}</div>
                <div class="lineage-hypothesis-desc">${escapeHtml(hyp.description)}</div>
            </div>
        `;
    }
    
    // Spawn info (if any)
    if (lineage.spawn) {
        const spawn = lineage.spawn;
        html += `
            <div class="lineage-spawn">
                <div class="lineage-spawn-title">🤖 Babies</div>
                <div class="spawn-stat"><strong>${1 + (spawn.variant_count || 10)}</strong> total (1 canonical + ${spawn.variant_count || 10} variants)</div>
            </div>
        `;
    }
    
    document.getElementById('modal-body').innerHTML = html;
}

// Override openDetail
