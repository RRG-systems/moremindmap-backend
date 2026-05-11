# RESET ARENA CAPITAL — IMPLEMENTATION PLAN

**Date:** 2026-04-17  
**Status:** IN PROGRESS  
**Objective:** Implement "Reset Arena Capital" logic for fresh evaluation windows

---

## UNDERSTANDING

Current state:
- Backend: `/Users/rrg/moltmarket/server/api.py` (Flask + MultiMarketArena)
- Frontend: `/Users/rrg/moltmarket/viewer/src/App.jsx` (React)
- Engine: `/Users/rrg/moltmarket/engine/multi_market_arena.py` (simulation)

Current metric flow:
1. User clicks "RUN" → `POST /api/start`
2. Background thread runs simulation ticks
3. `GET /api/state` returns current metrics (computed from entire closed_trades list)
4. Frontend displays metrics

Problem:
- Metrics are calculated from **all historical trades**
- No way to isolate a new evaluation window
- Mutation Brain will see blended pre/post-reset data

---

## SOLUTION: ARENA SEGMENTS

Introduce `arena_segment_id` (timestamp-based) to partition metrics:

### Data Model Changes

**UniverseState:**
- Add: `arena_segment_id: str` (ISO timestamp when segment started)
- Add: `segment_closed_trades: List[ClosedTrade]` (trades in current segment only)

**MultiMarketArena:**
- Add: `current_segment_id: str` (initialized at creation)
- Add: `segment_start_tick: int` (tick number when segment began)
- Add method: `reset_arena_segment()` → clears segment metrics, creates new segment_id

**ClosedTrade:**
- Add: `segment_id: str` (for tracking; helps with debugging)

---

## IMPLEMENTATION STEPS

### 1. Backend Changes

**File: `engine/multi_market_arena.py`**

Add to `UniverseState`:
```python
arena_segment_id: str  # When this segment started (ISO timestamp)
segment_closed_trades: List[ClosedTrade]  # Trades in this segment only
```

Add to `MultiMarketArena`:
```python
def __init__(...):
    self.arena_segment_id = datetime.utcnow().isoformat()
    self.segment_closed_trades = []
    self.segment_start_tick = 0

def reset_arena_segment(self):
    """Reset metrics for fresh evaluation window."""
    self.arena_segment_id = datetime.utcnow().isoformat()
    self.segment_closed_trades = []  # Clear segment trades
    self.segment_start_tick = self.tick_count
    # Keep: open_positions, closed_trades, blocked_markets, bot identity
    
def _on_trade_close(self, trade: ClosedTrade):
    """Add to both historical and segment lists."""
    self.closed_trades.append(trade)
    self.segment_closed_trades.append(trade)
```

Update `get_universe_state()`:
```python
return UniverseState(
    tick=self.tick_count,
    timestamp=datetime.utcnow(),
    markets=self.current_markets,
    open_positions=self.open_positions,
    closed_trades=self.segment_closed_trades,  # Use SEGMENT trades only
    arena_segment_id=self.arena_segment_id,
    blocked_markets=self.blocked_markets,
)
```

**File: `server/api.py`**

Add endpoint:
```python
@app.route('/api/arena/reset', methods=['POST'])
def reset_arena():
    """Reset metrics for active strategy."""
    if not simulation_state['baseline_sim']:
        return jsonify({'error': 'Not initialized'}), 400
    
    # Reset the evolved variant (active bot)
    simulation_state['evolved_sim'].reset_arena_segment()
    
    return jsonify({
        'status': 'reset',
        'new_segment_id': simulation_state['evolved_sim'].arena_segment_id,
        'tick': simulation_state['tick'],
    })
```

### 2. Frontend Changes

**File: `viewer/src/App.jsx`**

Add button in control bar:
```jsx
<button 
  onClick={handleResetArena} 
  className="btn-warning"
  style={{ marginLeft: '10px' }}
>
  Reset Arena Capital
</button>
```

Add handler:
```javascript
const handleResetArena = async () => {
  try {
    const res = await fetch(`${API_URL}/arena/reset`, { method: 'POST' });
    const data = await res.json();
    console.log('Arena reset:', data);
    await refreshState();
  } catch (e) {
    console.error('Reset failed:', e);
  }
};
```

Update state display to show segment info:
```jsx
{state.evolved?.segment_id && (
  <span className="segment-info">
    Segment: {state.evolved.segment_id.substring(11, 19)}
  </span>
)}
```

### 3. CSS Update

**File: `viewer/src/App.css`**

Add button style:
```css
.btn-warning {
  background-color: #ff9800;
  color: white;
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-weight: bold;
}

.btn-warning:hover {
  background-color: #f57c00;
}
```

---

## RESET BEHAVIOR

When user clicks **[ Reset Arena Capital ]**:

✅ RESET:
- `segment_closed_trades` → empty list
- `arena_segment_id` → new ISO timestamp
- `segment_start_tick` → current tick count
- All derived metrics:
  - total_trades → 0
  - trade_sign_flips → 0
  - rolling_win_rate → 0
  - avg_pnl_per_trade → 0
  - avg_entry_slippage → 0
  - avg_exit_slippage → 0
  - paper_rolling_value → 0
  - shadow_rolling_value → 0

❌ DO NOT RESET:
- `active_strategy_id` (bot identity)
- `generation` number
- `lineage` chain
- DNA / parameters
- Mutation history
- Nursery state
- Historical `closed_trades` (audit trail)
- Open positions (continue existing)

---

## VERIFICATION

After reset:
1. Dashboard metrics return to zero
2. Bot continues trading from existing positions
3. New trades rebuild metrics from zero
4. Historical data preserved in `closed_trades` (not shown)
5. Segment ID visible in debug info
6. Gen 9 bot is still Gen 9
7. Mutation Brain can safely assume fresh metrics = current behavior only

---

## TIMELINE

- [ ] Update `multi_market_arena.py` (data model + reset logic)
- [ ] Update `server/api.py` (new endpoint)
- [ ] Update `viewer/src/App.jsx` (button + handler)
- [ ] Update `viewer/src/App.css` (button styling)
- [ ] Test reset flow end-to-end
- [ ] Verify Mutation Brain receives clean segment data

---

## MUTATION BRAIN ASSUMPTION

After this is complete, Mutation Brain can safely assume:
- ALL metrics on active bot = ONLY post-reset behavior
- NO blended pre/post data
- Accurate performance window for mutation decisions
- Clean evaluation each generation

