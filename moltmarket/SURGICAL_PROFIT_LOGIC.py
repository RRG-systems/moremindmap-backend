"""
SURGICAL PROFIT DIAGNOSIS LOGIC

When we're losing money, diagnose ruthlessly. No excuses.
Obsessively good analysis — every observation logged.
"""

def get_surgical_profit_analysis(shadow_pnl, paper_pnl, win_rate, total_trades, trades=None):
    """
    Return ruthless profit diagnosis.
    
    If losing: UNACCEPTABLE. Root cause. Fix it.
    If barely profitable: NOT GOOD ENOUGH. Tighten.
    If profitable: KEEP PUSHING. Scale ruthlessly.
    """
    
    msg = "**Profit Engine — Surgical Diagnosis:**\n\n"
    
    if total_trades < 20:
        return "Sample size too small. Can't diagnose yet. Need minimum 20-30 trades for signal."
    
    # LOSING MONEY — UNACCEPTABLE
    if shadow_pnl < 0:
        msg += f"🛑 **UNACCEPTABLE: We're down ${abs(shadow_pnl):.2f}. This is a failure state.**\n\n"
        msg += "**Root cause analysis (what's actually broken):**\n\n"
        
        # Direction problem?
        if win_rate < 0.48:
            msg += f"1. **DIRECTION WRONG** (win rate: {win_rate*100:.1f}%)\n"
            msg += "   This is the core problem. We're picking the wrong side more than 50% of the time.\n"
            msg += "   This is not execution. This is signal failure.\n\n"
            msg += "   **Root causes to investigate:**\n"
            msg += "   - Entry signal is inverted or lagged\n"
            msg += "   - Confirmation rules too loose (accepting false breakouts)\n"
            msg += "   - Market regime changed (what worked in trending market fails in chop)\n\n"
            msg += "   **Mutations to try IMMEDIATELY:**\n"
            msg += "   - Invert entry logic. Test if inverse works better.\n"
            msg += "   - Add 1-2 bar delay to entry. Maybe we're too early.\n"
            msg += "   - Tighten confirmation from 2 bars to 3-4 bars. Reject weak signals.\n"
            msg += "   - Test opposite market regime (mean reversion if currently trend-following).\n\n"
        
        # Execution bleed?
        bleed = abs(paper_pnl - shadow_pnl)
        if bleed > 50:
            msg += f"2. **EXECUTION BLEED** (${bleed:.2f} difference)\n"
            msg += "   Even if direction were right, we're losing this much to slippage/costs.\n\n"
            msg += "   **Fix immediately:**\n"
            msg += "   - Reduce position size 30%. Current size is too aggressive for market depth.\n"
            msg += "   - Use limit orders instead of market. Accept worse fills for better prices.\n"
            msg += "   - Widen stop loss from current to next support/resistance. Avoid noise.\n\n"
        
        msg += f"3. **FINAL VERDICT: This strategy doesn't work. Period.**\n"
        msg += "   - Win rate below 50% means we're wrong on direction.\n"
        msg += "   - No amount of position sizing fixes a wrong signal.\n"
        msg += "   - This is a mutation failure. Respawn Nursery completely.\n\n"
        msg += "   **Action (non-negotiable):**\n"
        msg += "   - STOP current Arena strategy. Move to FLAT.\n"
        msg += "   - Respawn 20 babies with different mutation categories (not tweaks).\n"
        msg += "   - Test: opposite direction logic, different entry signals, different timeframes.\n"
        msg += "   - Don't try to fix this baby. It's broken at the foundation.\n"
    
    # BARELY PROFITABLE — UNACCEPTABLE
    elif 0 < shadow_pnl < 50:
        msg += f"⚠️  **BARELY PROFITABLE: ${shadow_pnl:.2f} on {total_trades} trades.**\n"
        msg += "**This is not good enough.** Average PnL per trade is tiny. We're noisy.\n\n"
        msg += "**Why this is a problem:**\n"
        msg += f"- Per-trade average: ${shadow_pnl/total_trades:.2f}\n"
        msg += "- This is below execution costs on most days.\n"
        msg += "- One bad week of market conditions and we're back to negative.\n"
        msg += "- This is not an edge. This is luck within noise.\n\n"
        msg += "**Surgical fixes:**\n"
        msg += "1. **Tighten entry/exit by 20-30%.** We're probably right on direction but sloppy on timing.\n"
        msg += "2. **Only trade when conviction is high.** Skip low-confidence setups.\n"
        msg += "3. **Promote best Nursery baby immediately.** If any baby outperforms, use it.\n"
        msg += "4. **If no baby outperforms, respawn with tighter parameters.** Current mutations too loose.\n\n"
        msg += "**Target:** Get to $100+ per cycle. If you can't in 50 trades, it's not an edge.\n"
    
    # PROFITABLE — STILL PUSH
    else:
        msg += f"✓ **PROFITABLE: ${shadow_pnl:.2f}. ({win_rate*100:.0f}% win rate).**\n"
        msg += "Edge is real. Now scale it ruthlessly.\n\n"
        msg += "**What to check:**\n"
        msg += "1. **Is Nursery learning?** Best baby vs Arena?\n"
        msg += "   - If any baby beats Arena by >$50: Promote immediately.\n"
        msg += "   - If no baby beats Arena: Respawn with tighter mutations (not looser).\n\n"
        msg += "2. **Market condition dependency:**\n"
        msg += "   - Does edge work in trending? In choppy? In high volatility?\n"
        msg += "   - If only in one regime: BRAIN needs regime detection. Adjust size per regime.\n\n"
        msg += "3. **Scaling:** Can we double position size without degrading win rate?\n"
        msg += "   - Test 1.5x position size for 10 trades. Monitor win rate.\n"
        msg += "   - If win rate stays >55%: Increase to 1.5x permanently.\n"
        msg += "   - If win rate drops: Stop. Current size is optimal for market depth.\n\n"
        msg += "4. **Lock in gains:** Use tighter stops. Let winners run less.\n"
        msg += "   - Current target might be too greedy for this market.\n"
        msg += "   - 2-3 wins at smaller target > 1 huge win + 2 stopouts.\n"
    
    return msg
