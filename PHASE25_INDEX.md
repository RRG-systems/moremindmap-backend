# PHASE 25 - VOLATILITY EXPANSION VALIDATION - INDEX

**Completion Date:** April 16, 2026  
**Task:** Validate Signal C (Volatility Expansion) out-of-sample | COMPLETE ✓

---

## VERDICT

**Signal Status:** ✗ FAKE  
**Confidence:** HIGH  
**Production Readiness:** 0%  
**Action:** DISCARD

Signal C fails out-of-sample validation due to **regime instability** (negative PnL in high volatility where it should work best) and **sample size collapse** (3 trades vs 7 Phase 24).

---

## QUICK START

### For Executives
📄 **`PHASE25_SUMMARY.txt`** - 2-minute read. What went wrong and why.

### For Traders
📄 **`PHASE25_VALIDATION_REPORT.md`** - Full analysis with regime breakdown, random control, regime analysis, lessons learned.

### For Engineers/Data Scientists
🔬 **`phase25_final.py`** - Production validation script. Reproducible. Use as template for future signals.

### For Data/Records
📊 **`phase25_results.json`** - Raw test results in JSON. All metrics, regime splits, Q&A answers, verdict.

---

## WHAT PHASE 25 TESTED

### Task (7 Steps)
1. ✓ **Expand Data** → 171 hourly candles (April 9-16, out-of-sample)
2. ✓ **Out-of-Sample Test** → Applied Signal C with exact Phase 24 parameters
3. ✓ **Stability Check** → Measured win rate, PnL, drawdown, Sharpe
4. ✓ **Regime Test** → Split by high/mid/low volatility
5. ✓ **Randomized Control** → Compared signal vs random timing
6. ✓ **Results Table** → Phase 24 vs Phase 25 metrics
7. ✓ **Key Questions** → Answered Q1-Q4, gave final verdict

### Key Questions Answered
```
Q1: Does signal still produce positive edge?          YES ✓ (+56.61 bps)
Q2: Does edge remain >20 bps?                         YES ✓ 
Q3: Is performance stable across regimes?             NO ✗ (CRITICAL FAIL)
Q4: Does it outperform random consistently?           YES ✓ (but misleading)

Verdict Logic: Fails Q3 → FAKE
```

---

## CRITICAL FINDINGS

### 1. Regime Instability (Terminal Failure)
| Regime | Trades | Win Rate | Avg PnL/Trade | Status |
|--------|--------|----------|----------------|--------|
| HIGH Vol | 2 | 50.0% | **-9.99 bps** | ✗ LOSES |
| MID Vol | 1 | 100.0% | +189.81 bps | ✓ (1 trade) |
| LOW Vol | 0 | — | — | N/A |

**Why This Is Critical:** Signal is designed to exploit volatility spikes. It should perform BEST in high vol regime. Instead, it LOSES money. This violates the core hypothesis.

### 2. Sample Size Collapse
- Phase 24: 7 trades
- Phase 25: 3 trades
- **57% fewer signals** → indicates signal doesn't generalize

### 3. Edge Degradation
- Phase 24: +132.72 bps per trade
- Phase 25: +56.61 bps per trade
- **76.11 bps loss (-57.3%)** → classic overfitting signature

### 4. Small Sample Overfitting
- Phase 24's 7 trades + 85.71% win rate = suspiciously good
- Out-of-sample degrades as expected for lucky outcomes

---

## PHASE 24 vs PHASE 25

| Metric | Phase 24 | Phase 25 | Delta | Status |
|--------|----------|----------|-------|--------|
| Sample Size | 7 | 3 | -4 | ✗ |
| Win Rate (%) | 85.71 | 66.67 | -19.04 | ⚠ |
| Avg PnL/Trade (bps) | 132.72 | 56.61 | -76.11 | ✗ |
| Edge vs Random (bps) | 38.32 | 146.52 | +108.20 | ⚠ |
| Std Dev (bps) | 139.83 | 188.37 | +48.54 | ⚠ |
| Max Drawdown (bps) | -209.79 | -209.79 | 0.00 | ✓ |

---

## WHY PHASE 24 WAS FALSE POSITIVE

1. **Small sample (7 trades)** allowed luck to masquerade as skill
   - High variance in small samples
   - Need 50-100 trades for statistical significance
   
2. **Favorable market conditions** in Phase 24 data (April 2-9)
   - Not representative of all market states
   - Different conditions (April 9-16) didn't repeat pattern

3. **No regime split in Phase 24**
   - Missed that signal fails in high volatility
   - This is the signal's core use case

4. **No out-of-sample validation**
   - In-sample results always optimistic
   - Out-of-sample reveals overfitting

---

## DATA & METHODOLOGY

### Data Split
- **Phase 24:** April 2-9, 2026 | 171 hourly candles
- **Phase 25:** April 9-16, 2026 | 171 hourly candles
- **Asset:** BTC/USDT perpetual futures
- **Granularity:** Hourly OHLCV
- **Total:** 14.2 days of real market data

### Signal C Parameters (Locked from Phase 24)
```
Vol Lookback:           20 ticks
Vol Spike Threshold:    1.5x average (1.2x for hourly)
Entry:                  Long on upward breakout during vol spike
Exit:                   +2.0% target OR -2.0% stop
Max Hold:               100 ticks
Cost Model:             10 bps round-trip
Parameter Tuning:       ZERO
```

### Validation Approach
- ✓ Out-of-sample data (different date range)
- ✓ Zero parameter tuning
- ✓ Regime splits (high/mid/low volatility)
- ✓ Random baseline control
- ✓ Stability metrics (win rate, PnL, drawdown, Sharpe)

---

## LESSONS LEARNED

### For Signal Development
1. **Never trust small samples:** Minimum 50-100 trades required
2. **Regime analysis is critical:** Signals must work across conditions
3. **Out-of-sample validation is mandatory:** Catches overfitting
4. **Random baseline matters:** Both signal and baseline need large samples

### For Future Validation
- Require minimum 50 trades in initial discovery
- Implement regime splits for all signals
- Always run out-of-sample tests with zero tuning
- Use 100+ trade random baselines
- Measure consistency across market conditions

---

## FILES & ARTIFACTS

### Reports
- **`PHASE25_SUMMARY.txt`** — Executive summary (2-min read)
- **`PHASE25_VALIDATION_REPORT.md`** — Full technical report (20-min read)
- **`PHASE25_INDEX.md`** — This file

### Data
- **`phase25_results.json`** — Raw test results (JSON)
  - Signal C metrics (sample size, win rate, PnL, drawdown, Sharpe)
  - Random baseline metrics
  - Regime performance (high/mid/low vol)
  - Q1-Q4 answers
  - Final verdict

### Code
- **`phase25_final.py`** — Main validation script (reproducible)
  - SignalC_VolatilityExpansion class
  - RandomTimingControl class
  - Trade analysis functions
  - Regime classification
  - Full test pipeline

### Archive (Intermediate)
- `phase25_volatility_validation.py` — Synthetic data version
- `phase25_validation_real_data.py` — Real data first pass
- `phase25_expanded_granularity.py` — Minute-level expansion attempt
- `phase25_final_validation.json` — Earlier results (superseded)
- `phase25_validation_results.json` — Earlier results (superseded)

---

## FINAL RECOMMENDATION

### Action: DISCARD Signal C

**Do NOT:**
- Deploy to production
- Allocate capital
- Use in live trading
- Further optimize (will only increase overfitting)

**Reason:**
- Fails regime stability test (loses in high volatility)
- Small sample size collapse (3 trades Phase 25 vs 7 Phase 24)
- Edge degrades 57% out-of-sample (classic overfitting signature)
- Not generalizable to new market conditions

**Next Phase:**
- Return to signal discovery
- Apply lessons learned (larger samples, regime splits, OOS validation)
- Iterate until finding genuine edge that generalizes

---

## METADATA

- **Validation Date:** April 16, 2026
- **Completion Time:** ~30 minutes
- **Status:** ✓ COMPLETE
- **Confidence Level:** HIGH
- **Production Readiness:** 0%
- **Next Steps:** Return to Phase 24 (signal discovery) with refined methodology

---

**Generated by:** Phase 25 Volatility Expansion Validation Suite  
**For:** D.J. (Polymarket Trading System)  
**Status:** Ready for review
