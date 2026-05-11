# Tomorrow's Action Plan — Get Babies Trading

**Current State:**
- ✅ Babies spawn successfully
- ✅ Leaderboard endpoint returns empty safely (MOLT isolated)
- ✅ Main loop calls `execute_baby_variant()` for each baby
- ❌ Babies show 0 trades (execution not happening)

**Root Cause:**
`execute_baby_variant()` is being called but `unified_executor.execute_signal()` either:
1. Not being called (code path issue)
2. Being called but returning None (execution failure)
3. Executing but not updating baby metrics (ledger sync issue)

**Debug Steps (in order):**

### Step 1: Add hardcore logging to execute_baby_variant
```python
def execute_baby_variant(baby, market_data=None):
    baby_id = baby['variant_id']
    print(f"[BABY-TRACE] START execute_baby_variant for {baby_id}")
    
    # ... existing checks ...
    
    print(f"[BABY-TRACE] About to generate signal...")
    if True:  # Always generate for testing
        asset = 'BTC'
        side = 'long'
        entry = simulator._get_price(asset)
        exit_p = simulator._get_price(asset)
        
        print(f"[BABY-TRACE] Signal: {asset} {side}")
        print(f"[BABY-TRACE] unified_executor = {unified_executor is not None}")
        
        trade = unified_executor.execute_signal(
            source='baby',
            trader_id=baby_id,
            signal={'asset': asset, 'side': side, 'entry_price': entry, 'exit_price': exit_p, 'size': 1.0}
        )
        
        print(f"[BABY-TRACE] Trade result: {trade}")
        if trade:
            print(f"[BABY-TRACE] ✓ Trade executed: ${trade.pnl:.2f}")
        else:
            print(f"[BABY-TRACE] ✗ Trade returned None")
```

Add this logging, restart, spawn babies, **wait 5 seconds**, then **screenshot the terminal logs**.

### Step 2: If BABY-TRACE shows execute_signal returning None
Check `unified_executor.execute_signal()` in `unified_execution_pipeline.py` line ~120.
Look for early returns that might short-circuit execution.

### Step 3: If trades are executing but metrics not updating
The issue is the leaderboard reads from `evolution_engine.babies` which has old metrics.
Need to wire unified_ledger metrics back to baby objects.

### Step 4: Confirm the unified_ledger is recording
Add this after spawn:
```python
print(f"[LEDGER] Total trades recorded: {len(unified_ledger.trades)}")
for trader_id in unified_ledger.trader_pnl:
    print(f"[LEDGER] {trader_id}: {unified_ledger.trader_trades[trader_id]} trades, ${unified_ledger.trader_pnl[trader_id]:.2f}")
```

**The Goal:**
Get console output showing:
- `[BABY-TRACE] Signal generated`
- `[BABY-TRACE] ✓ Trade executed: $X.XX`
- `[LEDGER] 10 trades recorded`

Once you see that, babies are trading and we just need to sync metrics to the UI.

**Time Estimate:** 15-30 minutes to debug via logs, fix the issue, and confirm trades show in leaderboard.

**Do NOT:**
- Keep chasing MOLT schema issues
- Keep restarting without adding logging
- Change core unified executor logic

**DO:**
- Add logging
- Take screenshots of terminal
- Tell me exactly what the trace shows
- Then I'll fix the specific issue

---

**Key Files to Touch Tomorrow:**
1. `moltmarket_dashboard.py` — `execute_baby_variant()` function (add logging)
2. `unified_execution_pipeline.py` — Debug `execute_signal()` if needed
3. Terminal logs — The diagnostic truth

You're 99% there. One debug cycle away from babies trading live.
