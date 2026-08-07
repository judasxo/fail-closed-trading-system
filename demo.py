#!/usr/bin/env python3
"""Run credential-free demonstrations of the fail-closed control logic."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))

from failclosed_demo.core import (  # noqa: E402
    Event,
    SCENARIOS,
    evaluate_heartbeat_run,
    run_order_scenario,
)


def attempt_control_bypass() -> dict[str, object]:
    """Attempt entry without intent and report whether the guard rejected it."""
    try:
        run_order_scenario((Event.PREFLIGHT_READY, Event.ENTRY_ACCEPTED))
    except ValueError as exc:
        return {
            "sabotage_detected": True,
            "terminal_state": "CONTROL_BYPASS_REJECTED",
            "reason": str(exc),
        }
    return {
        "sabotage_detected": False,
        "terminal_state": "UNSAFE_CONTROL_BYPASS_ACCEPTED",
        "reason": "intent-before-entry invariant did not fire",
    }


def _run(name: str) -> dict[str, object]:
    if name == "sleep_gap":
        return evaluate_heartbeat_run(
            timestamps_seconds=(0.0, 60.0, 120.0, 10956.0, 11016.0),
            maximum_gap_seconds=90.0,
        ).as_dict()
    if name == "control_bypass_attempt":
        return attempt_control_bypass()
    return run_order_scenario(SCENARIOS[name]).as_dict()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--scenario",
        choices=(*SCENARIOS, "sleep_gap", "control_bypass_attempt", "all"),
        default="all",
    )
    args = parser.parse_args()
    names = [*SCENARIOS, "sleep_gap", "control_bypass_attempt"] if args.scenario == "all" else [args.scenario]
    print(json.dumps({name: _run(name) for name in names}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
