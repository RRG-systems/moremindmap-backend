# D.J.'s Directive — Apr 25, 2026

## The Mission (Clear Now)

"You're just learning how to play the game. We test... talk about what we learned and try again... log it. We will come back to the logs."

**Translation:** 
- I don't ask you "what should we do?" — I **make decisions** to chase positive PnL
- Every run teaches something. Log it. Come back later with patterns.
- Goal: Several runs where we **actually create positive PnL**, then we'll see the pattern
- Your job: Drive the Ferrari. Learn the machine. Iterate.

## Key Insight

"It's hard. we are learning from every experience... this is great."

You're not asking for perfection. You're asking for **deliberate experimentation + logging + learning over time.**

This changes everything. I'm not supposed to ask permission. I'm supposed to:
1. Make a hypothesis
2. Test it
3. Log results
4. Try again with new hypothesis
5. Look for patterns after 5-10 runs

---

## My Plan to Get PnL Positive (Session N+1)

### Hypothesis 1: Win Rate Confirmation
**Problem last time:** Promoted baby on 52% win rate (Nursery) → 37.5% win (Arena) → lost $125.

**Why:** Win rate doesn't travel. A 52% winner in Nursery might be 40% in Arena due to:
- Different execution conditions
- Market regime shift
- Sampling noise

**New approach:**
1. Spawn babies (30, not 90 — smaller sample, less noise)
2. Wait for babies to accumulate 100+ trades each
3. Only promote if:
   - Win rate > 55% (high confidence)
   - **AND** PnL > 0 (not just win rate)
   - **AND** PnL trend is positive (last 30 trades better than first 30)
4. Log the baby's full signature before promotion
5. Compare: Did promoted baby maintain its edge in Arena?

**Metric:** If promoted baby stays >50% win in Arena for 50+ trades, we found something.

---

### Hypothesis 2: Calibration As Edge Confirmation
**Problem:** We calibrated 5 times without clear feedback on what worked.

**New approach:**
1. Promote a baby to Arena
2. **Don't calibrate immediately** — let it run MODERATE for 50 trades
3. Measure: Is Arena PnL improving or degrading?
4. **Then** calibrate based on Arena performance (not Nursery signature)
5. If Arena PnL gets worse after calibration, revert

**Metric:** Does calibration improve Arena PnL? Track before/after.

---

### Hypothesis 3: Market Regime Detection
**Problem:** We don't know if the market is trending, mean-reverting, or ranging. Different strategies win in different regimes.

**New approach:**
1. Track market volatility/direction from signal data
2. When promoting, note the market regime (trending/ranging/high-vol)
3. Track which regimes baby performs in
4. Build regime map: "Baby X wins in ranging markets, loses in trends"

**Metric:** Correlate baby performance with market regime. Pattern emerges.

---

### Hypothesis 4: Genetic Diversity
**Problem:** All babies are mutations of baseline. Maybe we need more diversity.

**New approach:**
1. Spawn babies with different mutation types (not just entry_threshold)
2. Track which mutation types perform best
3. Weight future spawns toward winning mutations
4. Example: "exit_threshold mutations beat entry_threshold mutations in this market"

**Metric:** Win % by mutation type. Use winners as templates.

---

## The Playbook (Next 5 Runs)

**Run 1 (Next):** Conservative promotion (100+ trades, PnL > 0, trend positive) + no early calibration
**Run 2:** Same, but track market regime
**Run 3:** Compare 2 different babies promoted simultaneously (A vs B)
**Run 4:** Test calibration impact (MODERATE → AGGRESSIVE mid-run)
**Run 5:** Mutation type analysis (which types are winning?)

After 5 runs: Review logs. Identify pattern.

---

## What I'm Committing To

1. **Make decisions, not ask permission.** I propose → test → log → learn
2. **Set minimum standards before promotion:**
   - 100+ trades minimum
   - Win rate > 55%
   - PnL > 0
   - Positive trend (last 30 > first 30)

3. **Log everything obsessively:**
   - Promotion reason (why this baby?)
   - Pre-promotion metrics (Nursery signature)
   - Post-promotion metrics (Arena signature)
   - Market regime at promotion time
   - Calibration decisions and their impact

4. **Experiment systematically:**
   - Run 1: Test conservative promotion
   - Run 2: Add regime tracking
   - Run 3: Compare babies side-by-side
   - Run 4: Test calibration impact
   - Run 5: Analyze mutations

5. **Pattern search after N runs:**
   - What got us closest to positive?
   - Did regime matter?
   - Did mutation type matter?
   - Did calibration help or hurt?

---

## Success Definition

"Several runs where we actually create positive PnL" = **2-3 runs with positive Arena shadow PnL** (could be small, like +$50, but real)

Once we have 2-3 positive runs, we look at the logs and ask: **What was different? Regime? Baby type? Calibration? Promotion timing?**

That's the pattern.

---

**Status:** Ready to drive the Ferrari. Logs are open. Let's learn.
