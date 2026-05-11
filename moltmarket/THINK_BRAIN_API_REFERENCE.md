# THINK + BRAIN API Reference

## Overview

Two new interactive diagnostic systems have been added to the MOLTmarket dashboard:

- **THINK**: Interactive query engine for system diagnosis
- **BRAIN**: Real-time enforcement status display

## THINK API Endpoints

All THINK endpoints are GET requests and return JSON responses.

### 1. `/api/think/analyze` [GET]

**Purpose**: Full session diagnostic analysis

**Response**:
```json
{
  "status": "success",
  "analysis": {
    "behavior_summary": "Session: 60 cycles | FLAT 10% (10 entries, 5 exits) | ...",
    "failure_patterns": [
      "Probation passes too fast (avg 3.5 cycles)",
      "Too many FLAT entries (8/60 cycles, 13%)"
    ],
    "suggested_adjustment": "Increase probation_min_cycles from 3 to 5. Re-test same conditions.",
    "confidence": 0.75,
    "timestamp": "2026-04-21T22:55:00Z"
  }
}
```

**UI Response**: Structured report with color-coded sections
- Behavior summary (green)
- Issues detected (orange/red)
- Suggested adjustment (purple)
- Confidence percentage

---

### 2. `/api/think/why_stopped` [GET]

**Purpose**: Diagnosis for STOP events

**Response**:
```json
{
  "status": "success",
  "query": "Why did we stop?",
  "answer": "System triggered STOP 5 times. Primary causes: slow bleed (2x), severe drawdown (3x)."
}
```

**UI Response**: Red-highlighted answer
- Direct diagnosis of stop triggers
- Frequency count per cause

---

### 3. `/api/think/why_flat` [GET]

**Purpose**: Diagnosis for high FLAT percentage

**Response**:
```json
{
  "status": "success",
  "query": "Why are we FLAT?",
  "answer": "System FLAT 45% of session (45/100 cycles). Likely causes: weak candidate pool, high edge threshold, or frequent probation failures."
}
```

**UI Response**: Orange-highlighted answer
- FLAT percentage
- Root cause analysis

---

### 4. `/api/think/probation_speed` [GET]

**Purpose**: Assess probation completion efficiency

**Response**:
```json
{
  "status": "success",
  "query": "Is probation too short?",
  "answer": "Probation passes quickly: avg 3.1 cycles, 60 trades. Consider increasing min_cycles to 5 or min_trades to 75 for larger sample."
}
```

**UI Response**: Blue-highlighted answer
- Average cycles per pass
- Trade count per pass
- Recommendation

---

### 5. `/api/think/biggest_problem` [GET]

**Purpose**: Identify strongest single issue

**Response**:
```json
{
  "status": "success",
  "query": "What is the biggest problem?",
  "answer": "Biggest issue: System in FLAT 70% of cycles (70/100). Candidate pool may be weak or edge threshold too high."
}
```

**UI Response**: Pink-highlighted answer
- Single strongest pattern identified
- Direct impact statement

---

### 6. `/api/think/next_adjustment` [GET]

**Purpose**: Get next testable, bounded adjustment

**Response**:
```json
{
  "status": "success",
  "query": "What should we adjust next?",
  "answer": "Decrease edge_score_threshold by 0.05 to allow more candidates. Re-test and measure restart rate."
}
```

**UI Response**: Purple-highlighted answer
- Specific parameter to adjust
- Direction of change (increase/decrease)
- Exactly one bounded change
- Re-test guidance

---

## BRAIN API Endpoint

### `/api/brain/enforcement` [GET]

**Purpose**: Get current BRAIN enforcement status (real-time read)

**Response**:
```json
{
  "status": "success",
  "brain_state": "THROTTLE",
  "reason_code": "high_volatility",
  "reason_text": "Market volatility > 25%, position size throttled",
  "enforcement_flags": {
    "allows_trade": true,
    "throttle_active": true,
    "position_size_factor": 0.5
  },
  "timestamp": "2026-04-21T22:55:15Z"
}
```

**Possible States**:
- `NORMAL` - All systems nominal, full trading enabled
- `THROTTLE` - Risk detected, position sizing reduced
- `FLAT` - No new entries, existing positions managed
- `STOP` - All trading halted, risk management active
- `UNKNOWN` - State not evaluated

**UI Display**: Color-coded state with live enforcement flags

---

## Error Responses

All endpoints return 503 if engine unavailable:

```json
{
  "status": "error",
  "message": "THINK engine not available"
}
```

---

## Usage Examples

### JavaScript (from THINK panel):

```javascript
// Query why system is flat
const response = await fetch('/api/think/why_flat');
const data = await response.json();
console.log(data.answer);
// Output: "System FLAT 45% of session (45/100 cycles). Likely causes: weak candidate pool..."
```

### cURL:

```bash
# Get full analysis
curl http://localhost:5050/api/think/analyze | jq

# Get next adjustment
curl http://localhost:5050/api/think/next_adjustment | jq .answer

# Check BRAIN status
curl http://localhost:5050/api/brain/enforcement | jq .brain_state
```

---

## Panel Locations in Dashboard

**BRAIN Panel**
- After "Control Status" panel
- Brown border (#d4a574), dark background
- Auto-updates every 3 seconds

**THINK Panel**
- After BRAIN panel
- Green border (#7cb342), dark background
- 6 query buttons in 2×3 grid
- Response display area

---

## Implementation Details

### Backend (Python)

**File**: `moltmarket_dashboard.py`

- Import: `from think_diagnostic_layer import ThinkDiagnosticLayer`
- Engine: `think_engine = ThinkDiagnosticLayer()`
- Session loader: `_load_current_session_to_think()`

**Routes**:
```python
@app.route('/api/think/analyze', methods=['GET'])
@app.route('/api/think/why_stopped', methods=['GET'])
@app.route('/api/think/why_flat', methods=['GET'])
@app.route('/api/think/probation_speed', methods=['GET'])
@app.route('/api/think/biggest_problem', methods=['GET'])
@app.route('/api/think/next_adjustment', methods=['GET'])
@app.route('/api/brain/enforcement', methods=['GET'])
```

### Frontend (JavaScript)

**File**: `static/think_brain_panel_handler.js`

- Class: `ThinkBrainPanelHandler`
- Auto-initializes on DOM ready
- Polls BRAIN status every 3 seconds
- Formats responses per query type

**HTML Panels**: `templates/dashboard.html`
- BRAIN panel: Dynamic status display
- THINK panel: Interactive query buttons + response area

---

## Response Times

| Endpoint | Typical Response | Notes |
|----------|------------------|-------|
| /api/think/analyze | 200-500ms | Full analysis, depends on trade count |
| /api/think/why_stopped | 100-200ms | Scans STOP events |
| /api/think/why_flat | 100-200ms | Checks FLAT percentage |
| /api/think/probation_speed | 100-200ms | Analyzes probation logs |
| /api/think/biggest_problem | 100-200ms | Pattern detection |
| /api/think/next_adjustment | 100-200ms | Returns single suggestion |
| /api/brain/enforcement | 50-100ms | Simple state lookup |

---

## Color Scheme

| Component | Color | Usage |
|-----------|-------|-------|
| BRAIN border | #d4a574 (brown) | Enforcement status |
| THINK border | #7cb342 (green) | Diagnostic queries |
| Analyze button | #4CAF50 (green) | Positive/comprehensive |
| Why Stopped? | #f44336 (red) | Stop events/issues |
| Why Flat? | #ff9800 (orange) | Activity/medium severity |
| Probation Speed | #2196F3 (blue) | Neutral/informational |
| Biggest Problem | #e91e63 (pink) | Priority/important |
| Next Adjustment | #9c27b0 (purple) | Actionable recommendation |

---

## Integration with Existing Systems

✓ THINK queries wrap existing methods from `ThinkDiagnosticLayer`
✓ BRAIN enforcement reads from `dashboard_state` (existing BRAIN evaluation)
✓ Session data constructed from `data_layer` and current metrics
✓ No modifications to existing endpoints or logic
✓ All new code isolated in new handlers/endpoints

---

## Troubleshooting

**THINK engine unavailable**
- Check: `think_diagnostic_layer.py` imports successfully
- Check: Flask app initialization completes
- Response: 503 error with engine unavailable message

**BRAIN status not updating**
- Check: Polling interval (set to 3 seconds in JS)
- Check: BRAIN bridge initialization in dashboard
- Response: Silent failure, status remains last known value

**Empty THINK responses**
- Cause: No trade data loaded
- Fix: Run dashboard for a bit to accumulate trades
- Response: Generic "no data" answers

---

## Future Enhancements

Possible additions:
- Custom polling interval for BRAIN
- THINK query history/logging
- Suggested adjustment batching
- Multi-session comparison
- Export diagnostic reports
