import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from failclosed_demo.core import Event, SCENARIOS, evaluate_heartbeat_run, run_order_scenario


class FailClosedDemoTests(unittest.TestCase):
    def assert_intent_guard_holds(self, runner) -> None:
        with self.assertRaisesRegex(ValueError, "before intent"):
            runner((Event.PREFLIGHT_READY, Event.ENTRY_ACCEPTED))

    def test_success_records_intent_and_reconciles_clean(self) -> None:
        result = run_order_scenario(SCENARIOS["success"])
        self.assertEqual(result.terminal_state, "SEQUENCE_COMPLETE")
        self.assertTrue(result.intent_recorded)
        self.assertEqual(result.entry_submissions, 1)
        self.assertEqual(result.close_submissions, 1)
        self.assertTrue(result.account_clean)

    def test_definitive_rejection_requires_absence_and_cleanliness(self) -> None:
        result = run_order_scenario(SCENARIOS["definitive_rejection"])
        self.assertEqual(result.terminal_state, "ENTRY_REJECTED_ACCOUNT_CLEAN")
        self.assertEqual(result.entry_submissions, 1)
        self.assertTrue(result.account_clean)

        incomplete = SCENARIOS["definitive_rejection"][:-1]
        with self.assertRaisesRegex(ValueError, "terminal state"):
            run_order_scenario(incomplete)

    def test_ambiguous_entry_halts_without_retry_or_close(self) -> None:
        result = run_order_scenario(SCENARIOS["ambiguous_after_intent"])
        self.assertEqual(result.terminal_state, "HALTED_MANUAL_RECONCILIATION")
        self.assertTrue(result.manual_reconciliation_required)
        self.assertEqual(result.entry_submissions, 1)
        self.assertEqual(result.close_submissions, 0)

    def test_entry_before_intent_is_rejected(self) -> None:
        self.assert_intent_guard_holds(run_order_scenario)

    def test_sabotaged_runner_is_caught_by_intent_invariant(self) -> None:
        def sabotaged_runner(_events):
            return object()

        with self.assertRaises(AssertionError):
            self.assert_intent_guard_holds(sabotaged_runner)

    def test_entry_retry_is_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "may not be retried"):
            run_order_scenario(
                (
                    Event.PREFLIGHT_READY,
                    Event.INTENT_RECORDED,
                    Event.ENTRY_ACCEPTED,
                    Event.ENTRY_ACCEPTED,
                )
            )

    def test_sleep_gap_fails_reliability_acceptance(self) -> None:
        result = evaluate_heartbeat_run((0, 60, 120, 10956, 11016), 90)
        self.assertFalse(result.accepted)
        self.assertEqual(result.maximum_gap_seconds, 10836)
        self.assertEqual(result.reason, "maximum_heartbeat_gap_exceeded")

    def test_continuous_heartbeat_passes(self) -> None:
        result = evaluate_heartbeat_run((0, 60, 120, 180, 240), 90)
        self.assertTrue(result.accepted)


if __name__ == "__main__":
    unittest.main()
