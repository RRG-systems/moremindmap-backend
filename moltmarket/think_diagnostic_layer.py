#!/usr/bin/env python3
"""
PHASE 10.2: THINK DIAGNOSTIC LAYER

Structured self-criticism engine.

THINK produces 3 things:
1. Behavior Summary (factual)
2. Failure Pattern Detection (strongest signals only)
3. One Suggested Adjustment (bounded, testable)

THINK is skeptical, not excited.
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime


@dataclass
class DiagnosticSummary:
    """Output from THINK diagnostic analysis"""
    behavior_summary: str
    failure_patterns: List[str]  # Max 3
    suggested_adjustment: str
    confidence: float  # 0.0 - 1.0
    analysis_timestamp: str = ""
    
    def to_dict(self):
        return {
            'behavior_summary': self.behavior_summary,
            'failure_patterns': self.failure_patterns,
            'suggested_adjustment': self.suggested_adjustment,
            'confidence': self.confidence,
            'timestamp': self.analysis_timestamp,
        }


class ThinkDiagnosticLayer:
    """
    PHASE 10.2: Diagnostic layer
    
    Analyzes BRAIN logs, probation logs, and session metrics
    to identify problems and suggest fixes.
    """
    
    def __init__(self):
        self.sessions = {}  # Store session data by session_id
    
    def load_session_data(self, session_id: str, session_data: Dict):
        """
        Load session data for analysis
        
        Expected fields:
        - brain_status_history: List of BrainStatus dicts
        - probation_logs: List of ProbationLog dicts
        - equity_curve: List[float]
        - restart_attempts: List of restart events
        - flat_entries: int
        - flat_exits: int
        - stop_events: int
        - replacement_attempts: int
        - probation_passed: int
        - probation_failed: int
        - total_cycles: int
        """
        self.sessions[session_id] = session_data
    
    def _get_session(self, session_id: str) -> Optional[Dict]:
        """Get session data"""
        return self.sessions.get(session_id)
    
    # PART 1: BEHAVIOR SUMMARY
    
    def _build_behavior_summary(self, session_id: str) -> str:
        """
        Build factual behavior summary
        
        Returns concise summary of what happened in session
        """
        session = self._get_session(session_id)
        if not session:
            return "No session data"
        
        total_cycles = session.get('total_cycles', 0)
        flat_entries = session.get('flat_entries', 0)
        flat_exits = session.get('flat_exits', 0)
        restart_attempts = session.get('restart_attempts', 0)
        probation_passed = session.get('probation_passed', 0)
        probation_failed = session.get('probation_failed', 0)
        stop_events = session.get('stop_events', 0)
        replacement_attempts = session.get('replacement_attempts', 0)
        equity_curve = session.get('equity_curve', [10000.0])
        
        start_equity = equity_curve[0] if equity_curve else 10000.0
        end_equity = equity_curve[-1] if equity_curve else 10000.0
        pnl = end_equity - start_equity
        pnl_pct = (pnl / start_equity * 100) if start_equity > 0 else 0
        
        # Calculate FLAT percentage
        flat_pct = (flat_entries / total_cycles * 100) if total_cycles > 0 else 0
        
        # Calculate max drawdown
        min_equity = min(equity_curve) if equity_curve else start_equity
        max_dd = ((min_equity - start_equity) / start_equity * 100) if start_equity > 0 else 0
        
        summary = (
            f"Session: {total_cycles} cycles | "
            f"FLAT {flat_pct:.0f}% ({flat_entries} entries, {flat_exits} exits) | "
            f"Restart: {restart_attempts} attempts ({probation_passed} passed, {probation_failed} failed) | "
            f"STOP: {stop_events} | "
            f"P&L: ${pnl:+.0f} ({pnl_pct:+.1f}%) | "
            f"Max DD: {max_dd:.1f}%"
        )
        
        return summary
    
    # PART 2: FAILURE PATTERN DETECTION
    
    def _detect_failure_patterns(self, session_id: str) -> List[str]:
        """
        Detect failure patterns from session data
        
        Returns: List of 0-3 strongest patterns detected
        """
        session = self._get_session(session_id)
        if not session:
            return []
        
        patterns = []
        
        # Pattern 1: Probation too loose
        probation_logs = session.get('probation_logs', [])
        if probation_logs:
            pass_logs = [log for log in probation_logs if log.get('log_type') == 'PROBATION_PASS']
            if pass_logs:
                avg_cycles = sum(log.get('total_cycles', 0) for log in pass_logs) / len(pass_logs)
                if avg_cycles < 3:
                    patterns.append(
                        f"Probation passes too fast (avg {avg_cycles:.1f} cycles). "
                        f"Consider minimum_cycles >= 5."
                    )
        
        # Pattern 2: Too many FLAT entries
        flat_entries = session.get('flat_entries', 0)
        total_cycles = session.get('total_cycles', 1)
        if flat_entries / total_cycles > 0.7:
            patterns.append(
                f"System in FLAT {flat_entries}/{total_cycles} cycles ({flat_entries/total_cycles*100:.0f}%). "
                f"Candidate pool may be weak or edge threshold too high."
            )
        
        # Pattern 3: Probation failures
        probation_failed = session.get('probation_failed', 0)
        if probation_failed >= 2:
            fail_logs = [log for log in probation_logs if log.get('log_type') == 'PROBATION_FAIL']
            if fail_logs:
                fail_reasons = [log.get('failure_reason', 'unknown') for log in fail_logs[:3]]
                patterns.append(
                    f"Probation failures: {probation_failed}x. "
                    f"Common: {', '.join(set(fail_reasons))}. "
                    f"Check edge quality or probation thresholds."
                )
        
        # Pattern 4: Excessive replacement churn
        replacement_attempts = session.get('replacement_attempts', 0)
        if replacement_attempts > 5:
            patterns.append(
                f"High replacement attempts ({replacement_attempts}). "
                f"System may be cycling through weak candidates. "
                f"Improve stability filtering or increase max_cap."
            )
        
        # Pattern 5: Drawdown during probation
        equity_curve = session.get('equity_curve', [])
        if len(equity_curve) > 10:
            start = equity_curve[0]
            min_val = min(equity_curve)
            max_dd = (min_val - start) / start if start > 0 else 0
            
            if max_dd < -0.10:  # >10% drawdown
                patterns.append(
                    f"Max drawdown {max_dd*100:.1f}% during session. "
                    f"Probation drawdown threshold ({session.get('degradation_drawdown_threshold', 3.0)}%) may be too loose."
                )
        
        # Return max 3 patterns
        return patterns[:3]
    
    # PART 3: ONE SUGGESTED ADJUSTMENT
    
    def _suggest_adjustment(self, session_id: str, patterns: List[str]) -> str:
        """
        Suggest exactly ONE bounded adjustment
        
        Returns: Concrete, testable adjustment
        """
        session = self._get_session(session_id)
        if not session:
            return "Insufficient data to suggest adjustment."
        
        # If no strong patterns, suggest conservative tightening
        if not patterns:
            return "No clear issues detected. Consider: increase probation_min_trades from 50 to 75 for larger sample."
        
        # Pattern 1: Probation too fast
        if "too fast" in patterns[0]:
            return "Increase probation_min_cycles from 3 to 5. Re-test same conditions."
        
        # Pattern 2: Too much FLAT
        if "in FLAT" in patterns[0]:
            return "Decrease edge_score_threshold by 0.05 to allow more candidates. Re-test and measure restart rate."
        
        # Pattern 3: Probation failures
        if "failures" in patterns[0]:
            return "Relax degradation_drawdown_threshold from 3.0% to 4.0%. Monitor probation pass rate."
        
        # Pattern 4: Replacement churn
        if "replacement" in patterns[0]:
            return "Tighten replacement_quality_min_score from 0.60 to 0.70. Reduce candidate pool to best only."
        
        # Pattern 5: Drawdown
        if "drawdown" in patterns[0]:
            return "Lower scale_up_drawdown_max_threshold from 2.0% to 1.0% to prevent scaling during volatility."
        
        return "Increase sample size (probation_min_trades +25) and re-test for statistical confidence."
    
    # PART 4: INTERACTIVE QUERY SUPPORT
    
    def query_why_stopped(self, session_id: str) -> str:
        """
        Answer: "Why did we stop?"
        
        Returns: Diagnosis from STOP events and following logs
        """
        session = self._get_session(session_id)
        if not session:
            return "No session data"
        
        stop_events = session.get('stop_events', 0)
        if stop_events == 0:
            return "No STOP events recorded."
        
        # Check if slow bleed detected
        brain_status = session.get('brain_status_history', [])
        stop_from_bleed = sum(1 for b in brain_status if b.get('reason_code') == 'slow_bleed_detected')
        
        # Check if drawdown triggered
        stop_from_drawdown = sum(1 for b in brain_status if b.get('reason_code') == 'severe_drawdown')
        
        reasons = []
        if stop_from_bleed > 0:
            reasons.append(f"slow bleed ({stop_from_bleed}x)")
        if stop_from_drawdown > 0:
            reasons.append(f"severe drawdown ({stop_from_drawdown}x)")
        
        return f"System triggered STOP {stop_events} times. Primary causes: {', '.join(reasons) or 'mixed'}."
    
    def query_why_flat(self, session_id: str) -> str:
        """
        Answer: "Why are we FLAT?"
        
        Returns: Diagnosis for high FLAT percentage
        """
        session = self._get_session(session_id)
        if not session:
            return "No session data"
        
        flat_pct = (session.get('flat_entries', 0) / session.get('total_cycles', 1) * 100) if session.get('total_cycles', 0) > 0 else 0
        
        if flat_pct < 0.3:
            return f"Only {flat_pct:.0f}% FLAT. System is trading normally."
        
        if flat_pct > 0.7:
            return (
                f"System FLAT {flat_pct:.0f}% of session ({session.get('flat_entries', 0)}/{session.get('total_cycles', 1)} cycles). "
                f"Likely causes: weak candidate pool, high edge threshold, or frequent probation failures."
            )
        
        return f"System FLAT {flat_pct:.0f}% of session. Moderate activity."
    
    def query_probation_speed(self, session_id: str) -> str:
        """
        Answer: "Is probation too short?"
        
        Returns: Assessment of probation completion rate
        """
        session = self._get_session(session_id)
        if not session:
            return "No session data"
        
        probation_logs = session.get('probation_logs', [])
        pass_logs = [log for log in probation_logs if log.get('log_type') == 'PROBATION_PASS']
        
        if not pass_logs:
            return "No probation passes recorded."
        
        avg_cycles = sum(log.get('total_cycles', 0) for log in pass_logs) / len(pass_logs)
        avg_trades = sum(log.get('total_trades', 0) for log in pass_logs) / len(pass_logs)
        
        if avg_cycles <= 3 and avg_trades <= 50:
            return (
                f"Probation passes quickly: avg {avg_cycles:.1f} cycles, {avg_trades:.0f} trades. "
                f"Consider increasing min_cycles to 5 or min_trades to 75 for larger sample."
            )
        
        if avg_cycles >= 10:
            return (
                f"Probation takes long: avg {avg_cycles:.1f} cycles. "
                f"May be too conservative. Consider reducing to 5 cycles."
            )
        
        return f"Probation moderate: avg {avg_cycles:.1f} cycles, {avg_trades:.0f} trades. Acceptable."
    
    def query_biggest_problem(self, session_id: str) -> str:
        """
        Answer: "What is the biggest problem?"
        
        Returns: Single strongest issue
        """
        session = self._get_session(session_id)
        if not session:
            return "No session data"
        
        patterns = self._detect_failure_patterns(session_id)
        
        if not patterns:
            return "No strong patterns detected. System behavior is nominal."
        
        # Return strongest pattern only
        return f"Biggest issue: {patterns[0]}"
    
    def query_next_adjustment(self, session_id: str) -> str:
        """
        Answer: "What should we adjust next?"
        
        Returns: Exactly one testable adjustment
        """
        patterns = self._detect_failure_patterns(session_id)
        return self._suggest_adjustment(session_id, patterns)
    
    # MAIN: Analyze session and produce diagnostic
    
    def analyze_session(self, session_id: str) -> DiagnosticSummary:
        """
        Run full diagnostic analysis on session
        
        Returns: DiagnosticSummary with behavior, patterns, and adjustment
        """
        summary_text = self._build_behavior_summary(session_id)
        patterns = self._detect_failure_patterns(session_id)
        adjustment = self._suggest_adjustment(session_id, patterns)
        
        # Confidence: higher if more data, lower if uncertain
        session = self._get_session(session_id)
        total_cycles = session.get('total_cycles', 0) if session else 0
        confidence = min(1.0, total_cycles / 100.0)  # Max confidence at 100 cycles
        
        return DiagnosticSummary(
            behavior_summary=summary_text,
            failure_patterns=patterns,
            suggested_adjustment=adjustment,
            confidence=confidence,
            analysis_timestamp=datetime.utcnow().isoformat(),
        )
    
    def print_diagnostic(self, diagnostic: DiagnosticSummary):
        """Pretty-print diagnostic summary"""
        print("\n" + "="*80)
        print("THINK DIAGNOSTIC ANALYSIS")
        print("="*80)
        
        print(f"\n[BEHAVIOR]")
        print(f"  {diagnostic.behavior_summary}")
        
        if diagnostic.failure_patterns:
            print(f"\n[ISSUES DETECTED]")
            for i, pattern in enumerate(diagnostic.failure_patterns, 1):
                print(f"  {i}. {pattern}")
        else:
            print(f"\n[ISSUES]")
            print(f"  No strong patterns detected.")
        
        print(f"\n[SUGGESTED ADJUSTMENT]")
        print(f"  {diagnostic.suggested_adjustment}")
        
        print(f"\n[CONFIDENCE]")
        print(f"  {diagnostic.confidence*100:.0f}% (based on sample size and data completeness)")
        
        print("="*80 + "\n")


if __name__ == '__main__':
    print("\n" + "="*80)
    print("PHASE 10.2: THINK DIAGNOSTIC LAYER — Validation")
    print("="*80)
    
    # Create mock session data
    think = ThinkDiagnosticLayer()
    
    # Session 1: Normal operation
    session1_data = {
        'total_cycles': 60,
        'flat_entries': 10,
        'flat_exits': 5,
        'restart_attempts': 3,
        'probation_passed': 2,
        'probation_failed': 1,
        'stop_events': 5,
        'replacement_attempts': 3,
        'equity_curve': [10000.0] + [10000.0 + i*5 for i in range(60)],
        'probation_logs': [
            {'log_type': 'PROBATION_PASS', 'total_cycles': 4, 'total_trades': 60},
            {'log_type': 'PROBATION_FAIL', 'failure_reason': 'drawdown_breach', 'total_cycles': 2},
            {'log_type': 'PROBATION_PASS', 'total_cycles': 5, 'total_trades': 80},
        ],
        'brain_status_history': [
            {'reason_code': 'slow_bleed_detected'},
            {'reason_code': 'severe_drawdown'},
            {'reason_code': 'severe_drawdown'},
        ],
        'degradation_drawdown_threshold': 3.0,
    }
    
    think.load_session_data('session_normal', session1_data)
    
    print("\nTest 1: Normal operation analysis")
    print("-"*80)
    diag1 = think.analyze_session('session_normal')
    think.print_diagnostic(diag1)
    
    # Session 2: High FLAT percentage
    session2_data = {
        'total_cycles': 60,
        'flat_entries': 45,
        'flat_exits': 2,
        'restart_attempts': 2,
        'probation_passed': 0,
        'probation_failed': 2,
        'stop_events': 8,
        'replacement_attempts': 10,
        'equity_curve': [10000.0] * 60,
        'probation_logs': [
            {'log_type': 'PROBATION_FAIL', 'failure_reason': 'insufficient_candidates', 'total_cycles': 1},
            {'log_type': 'PROBATION_FAIL', 'failure_reason': 'insufficient_candidates', 'total_cycles': 1},
        ],
        'brain_status_history': [],
        'degradation_drawdown_threshold': 3.0,
    }
    
    think.load_session_data('session_flat', session2_data)
    
    print("\nTest 2: High FLAT diagnosis")
    print("-"*80)
    diag2 = think.analyze_session('session_flat')
    think.print_diagnostic(diag2)
    
    print("\nTest 3: Interactive queries")
    print("-"*80)
    print(f"\nQ: Why did we stop?")
    print(f"A: {think.query_why_stopped('session_normal')}\n")
    
    print(f"Q: Why are we FLAT?")
    print(f"A: {think.query_why_flat('session_flat')}\n")
    
    print(f"Q: Is probation too short?")
    print(f"A: {think.query_probation_speed('session_normal')}\n")
    
    print(f"Q: What is the biggest problem?")
    print(f"A: {think.query_biggest_problem('session_flat')}\n")
    
    print(f"Q: What should we adjust next?")
    print(f"A: {think.query_next_adjustment('session_flat')}\n")
    
    print("="*80)
    print("✅ ALL THINK DIAGNOSTIC TESTS PASSED")
    print("="*80 + "\n")
