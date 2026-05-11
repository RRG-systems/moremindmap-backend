# Money Layer Enforcement Test — Phase 4.5 Validation

**Goal:** Prove discipline works under pressure. STOP/THROTTLE must actually block trades.

**Test 1: Force STOP and verify blocking**

Setup:
- Active bot trading normally
- Monitor dashboard for drawdown
- Trigger STOP manually (or wait for natural threshold)

Verify:
- [ ] Risk state changes from NORMAL → STOP (dashboard shows it)
- [ ] New trades are BLOCKED (no executions after STOP)
- [ ] Money state API returns risk_state: "STOP"
- [ ] Position size multiplier = 0 (no new size)
- [ ] Existing positions continue (don't force-close)

**Test 2: Allocation reduction on degradation**

Setup:
- Active bot with 1% allocation
- Monitor metrics (survival %, drawdown %)
- Force degradation (or let it happen naturally)

Verify:
- [ ] Survival drops below 85% → allocation CUT to 50% (0.5%)
- [ ] Drawdown exceeds 8% → STOP triggered
- [ ] Dashboard shows allocation change in real-time
- [ ] Money state API reflects new allocation

**Test 3: Replacement on bot failure**

Setup:
- Active bot hits STOP or 0% allocation
- System should auto-select best candidate

Verify:
- [ ] Old bot marked STOPPED
- [ ] Best candidate selected (by score)
- [ ] New bot allocated 1%
- [ ] Money state shows new active_bot_id
- [ ] Trades resume with new bot

**Test 4: SIM = LIVE (verify thresholds)**

Check:
- [ ] 8% drawdown → STOP (both SIM and LIVE code paths)
- [ ] 85% survival → allocation cut
- [ ] 70% survival → kill (0% allocation)
- [ ] No override/bypass paths exist

---

## Execution

**How to trigger STOP manually (for testing):**

Option 1: Force drawdown in simulator
```python
# In dashboard, find where equity is updated
# Artificially reduce it to trigger >8% DD
```

Option 2: Wait for natural drawdown
- Let bot trade 30-50 times
- Eventually DD will hit 8%
- System should auto-STOP

**Monitoring:**

1. **Dashboard:**
   - ACTIVE STRATEGY shows allocation %
   - Risk state visible (NORMAL/THROTTLE/STOP)

2. **API:**
   - `/api/money-state` shows live risk_state
   - `/api/control` shows control_action

3. **Terminal:**
   - `[CONTROL]` lines show when STOP/THROTTLE triggers
   - Trade execution lines show when blocked

---

## Success Criteria

✅ **STOP blocks new trades** (zero new executions after trigger)
✅ **Allocation cuts work** (1% → 0.5% on degradation)
✅ **Replacement works** (bot dies → candidate takes over)
✅ **State visible** (dashboard + API show real-time changes)
✅ **No bypass** (no way to force-trade during STOP)

If all pass → **Money layer is TRUSTED and ENFORCED**

---

## Next: MOLT Feed Test

After enforcement validates, test:
- Agents posting (seed agents generating ideas)
- Disagreements visible (red posts showing conflicts)
- Spawn-from-idea works (can spawn babies from MOLT suggestions)

---

**Start with Test 1: Force STOP and verify blocking.**

Report back when STOP triggers.
