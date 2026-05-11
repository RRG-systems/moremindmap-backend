# TEST PLAN: Arena Execution Fix

## Pre-Test Checklist
- [ ] Kill any existing dashboard processes
- [ ] Clean ledger: `rm -f moltmarket/research_trades.csv`
- [ ] Verify edits applied:
  - [ ] `grep "promoted_baby stored" moltmarket_dashboard.py` returns match
  - [ ] `grep "ARENA EXECUTION.*promoted baby" moltmarket_dashboard.py` returns match

## Test Steps

### Step 1: Start Dashboard
```bash
cd /Users/rrg/.openclaw/workspace/moltmarket
python3 moltmarket_dashboard.py
# Wait for "Dashboard running on http://localhost:5050"
```

### Step 2: Spawn Babies
- Open http://localhost:5050
- Click **"SPAWN BABIES"**
- Wait 30 seconds (should see babies trading in Nursery)
- **Verify:** Dashboard shows trade count increasing

### Step 3: Promote Best Baby
- Click on any baby with positive PnL (shadow_pnl > 0)
- Click **"PROMOTE"**
- **Verify:**
  - Green success message appears
  - trading_enabled = True
  - BRAIN mode = PROBATION
  - **CRITICAL:** `[PROMOTE] promoted_baby stored to dashboard_state for Arena execution` appears in terminal

### Step 4: Verify Arena Execution
Wait 10 seconds. **Check terminal output for:**
```
[ARENA] Executing promoted baby: <baby_id>
[ARENA] Execution complete for <baby_id>
```

If you see these messages, Arena is executing! ✅

### Step 5: Check Ledger
Stop dashboard (Ctrl+C), then:
```bash
cd /Users/rrg/.openclaw/workspace/moltmarket
head -20 research_trades.csv
```

**Verify:** New rows appear with trades after promotion time
- Multiple rows with different timestamps
- source columns showing 'paper', 'shadow', or 'paper_baby'
- Non-zero PnL values

## Troubleshooting

### No "[ARENA] Executing" messages
- Check that `trading_enabled` is True (should be after promotion)
- Check that `promoted_baby` is not None in dashboard_state
- Look for `[ARENA ERROR]` messages

### trades.csv still empty
- Dashboard may not be writing to CSV
- Check file permissions: `ls -la research_trades.csv`
- Check for errors in terminal

### Ledger has no trades at all
- Simulator may not be running
- Check for Python exceptions in terminal
- Verify `simulator.step()` is being called

## Success Criteria
- ✅ Terminal shows "[ARENA] Executing" after promotion
- ✅ Ledger shows trade rows after promotion
- ✅ Dashboard PnL updates in real-time
- ✅ Zero timeouts or exceptions

## Next
If test passes: Arena execution is fixed! Ready to deploy.
