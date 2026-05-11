# RESTART SIMULATION BUTTON ✅ ADDED

**Date:** 2026-04-21 22:05 MST  
**Status:** COMPLETE + READY  

---

## What Was Added

### 1. ✅ Backend Endpoint

**File:** `moltmarket_dashboard.py` (added before `if __name__ == '__main__':`)

```python
@app.route('/api/restart-simulation', methods=['POST'])
def restart_simulation():
    """Restart simulation from CSV state (persistent, non-destructive)"""
    # Gets current state
    # Calls recover_simulator_state()
    # Returns restored PnL
```

**Behavior:** Reloads simulator from CSV without resetting equity.

### 2. ✅ UI Button

**File:** `templates/dashboard.html` (line 304)

```html
<button id="restartSimBtn" class="btn-restart-sim" title="Restart simulation from CSV (reload from saved state)">[ Restart Simulation ]</button>
```

**Location:** Next to "Refill Paper Capital" in control panel

### 3. ✅ JavaScript Handler

**File:** `static/restart_simulation_handler.js` (new)

```javascript
restartSimBtn.addEventListener('click', async () => {
    fetch('/api/restart-simulation', { method: 'POST' })
    // Shows alert with restored PnL
    // Reloads page
})
```

**Behavior:** 
- Asks for confirmation
- Calls endpoint
- Shows results
- Reloads dashboard

### 4. ✅ HTML Integration

**File:** `templates/dashboard.html` (bottom)

```html
<script src="{{ url_for('static', filename='restart_simulation_handler.js') }}"></script>
```

---

## How It Works

1. **User clicks:** "[ Restart Simulation ]" button
2. **Confirmation dialog** appears
3. **If yes:**
   - POST to `/api/restart-simulation`
   - Backend calls `recover_simulator_state()`
   - Returns restored PnL
   - Shows alert with values
   - Reloads page
4. **Dashboard reloads** with correct state

---

## Key Difference

| Button | Action |
|--------|--------|
| **New Run** (removed) | Reset to $0 (destructive) |
| **Restart Simulation** (new) | Reload from CSV (persistent) |
| **Refill Paper Capital** | Add $10k (additive) |

---

## Testing

1. Restart dashboard:
   ```bash
   pkill -f moltmarket_dashboard
   python3 moltmarket_dashboard.py
   ```

2. Look for button: "[ Restart Simulation ]" in control panel

3. Click it:
   - Confirm dialog
   - Should show PnL restored
   - Page reloads

4. Expected output in terminal:
   ```
   [RESTART] Restarting simulation from CSV...
   [RESTART] ✓ Complete
   [RESTART] Paper: $XXX → $YYY
   ```

---

## Safety

- ✅ Non-destructive (reads from CSV)
- ✅ Confirmation required
- ✅ No data loss
- ✅ Works with recovery system
- ✅ Can be called anytime

---

**Ready to restart dashboard and test.**
