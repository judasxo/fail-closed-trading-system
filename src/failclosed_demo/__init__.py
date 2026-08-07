"""Credential-free examples of fail-closed trading-system controls."""

from .core import SCENARIOS, HeartbeatResult, ScenarioResult, evaluate_heartbeat_run, run_order_scenario

__all__ = [
    "SCENARIOS",
    "HeartbeatResult",
    "ScenarioResult",
    "evaluate_heartbeat_run",
    "run_order_scenario",
]
