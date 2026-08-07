"""Pure state machines extracted from the project's operational design principles."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from typing import Iterable


class Event(str, Enum):
    PREFLIGHT_READY = "PREFLIGHT_READY"
    INTENT_RECORDED = "INTENT_RECORDED"
    ENTRY_ACCEPTED = "ENTRY_ACCEPTED"
    ENTRY_FILLED = "ENTRY_FILLED"
    CLOSE_ACCEPTED = "CLOSE_ACCEPTED"
    RECONCILED_CLEAN = "RECONCILED_CLEAN"
    ENTRY_REJECTED_DEFINITIVE = "ENTRY_REJECTED_DEFINITIVE"
    ORDER_ABSENCE_PROVED = "ORDER_ABSENCE_PROVED"
    ACCOUNT_CLEAN_PROVED = "ACCOUNT_CLEAN_PROVED"
    ENTRY_AMBIGUOUS = "ENTRY_AMBIGUOUS"


@dataclass(frozen=True)
class ScenarioResult:
    terminal_state: str
    intent_recorded: bool
    entry_submissions: int
    close_submissions: int
    account_clean: bool | None
    manual_reconciliation_required: bool
    audit_events: tuple[str, ...]

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class HeartbeatResult:
    accepted: bool
    observations: int
    maximum_gap_seconds: float
    threshold_seconds: float
    reason: str

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


SCENARIOS: dict[str, tuple[Event, ...]] = {
    "success": (
        Event.PREFLIGHT_READY,
        Event.INTENT_RECORDED,
        Event.ENTRY_ACCEPTED,
        Event.ENTRY_FILLED,
        Event.CLOSE_ACCEPTED,
        Event.RECONCILED_CLEAN,
    ),
    "definitive_rejection": (
        Event.PREFLIGHT_READY,
        Event.INTENT_RECORDED,
        Event.ENTRY_REJECTED_DEFINITIVE,
        Event.ORDER_ABSENCE_PROVED,
        Event.ACCOUNT_CLEAN_PROVED,
    ),
    "ambiguous_after_intent": (
        Event.PREFLIGHT_READY,
        Event.INTENT_RECORDED,
        Event.ENTRY_AMBIGUOUS,
    ),
}


def run_order_scenario(events: Iterable[Event]) -> ScenarioResult:
    audit: list[str] = []
    ready = False
    intent = False
    entry_submissions = 0
    close_submissions = 0
    entry_filled = False
    rejection_seen = False
    absence_proved = False

    for raw_event in events:
        event = Event(raw_event)
        audit.append(event.value)

        if event is Event.PREFLIGHT_READY:
            if audit != [Event.PREFLIGHT_READY.value]:
                raise ValueError("Preflight must be the first event")
            ready = True
        elif event is Event.INTENT_RECORDED:
            if not ready or intent:
                raise ValueError("Intent requires one successful preflight")
            intent = True
        elif event is Event.ENTRY_ACCEPTED:
            if not intent:
                raise ValueError("Entry cannot occur before intent")
            entry_submissions += 1
            if entry_submissions != 1:
                raise ValueError("Entry mutation may not be retried")
        elif event is Event.ENTRY_FILLED:
            if entry_submissions != 1:
                raise ValueError("Fill requires one accepted entry")
            entry_filled = True
        elif event is Event.CLOSE_ACCEPTED:
            if not intent or not entry_filled:
                raise ValueError("Close requires recorded intent and a filled entry")
            close_submissions += 1
            if close_submissions != 1:
                raise ValueError("Close mutation may not be retried")
        elif event is Event.RECONCILED_CLEAN:
            if close_submissions != 1:
                raise ValueError("Clean reconciliation requires one close submission")
            return ScenarioResult(
                "SEQUENCE_COMPLETE",
                intent,
                entry_submissions,
                close_submissions,
                True,
                False,
                tuple(audit),
            )
        elif event is Event.ENTRY_REJECTED_DEFINITIVE:
            if not intent:
                raise ValueError("A rejection cannot precede intent")
            entry_submissions += 1
            if entry_submissions != 1:
                raise ValueError("Rejected entry may not be retried")
            rejection_seen = True
        elif event is Event.ORDER_ABSENCE_PROVED:
            if not rejection_seen:
                raise ValueError("Order absence must follow a definitive rejection")
            absence_proved = True
        elif event is Event.ACCOUNT_CLEAN_PROVED:
            if not absence_proved:
                raise ValueError("Clean rejection requires direct proof of order absence")
            return ScenarioResult(
                "ENTRY_REJECTED_ACCOUNT_CLEAN",
                intent,
                entry_submissions,
                close_submissions,
                True,
                False,
                tuple(audit),
            )
        elif event is Event.ENTRY_AMBIGUOUS:
            if not intent:
                raise ValueError("Ambiguity cannot precede intent")
            entry_submissions += 1
            if entry_submissions != 1:
                raise ValueError("Ambiguous entry may not be retried")
            return ScenarioResult(
                "HALTED_MANUAL_RECONCILIATION",
                intent,
                entry_submissions,
                close_submissions,
                None,
                True,
                tuple(audit),
            )

    raise ValueError("Scenario ended without an allowed terminal state")


def evaluate_heartbeat_run(
    timestamps_seconds: Iterable[float],
    maximum_gap_seconds: float,
) -> HeartbeatResult:
    timestamps = tuple(float(value) for value in timestamps_seconds)
    if len(timestamps) < 2:
        raise ValueError("At least two heartbeats are required")
    if maximum_gap_seconds <= 0:
        raise ValueError("Maximum gap must be positive")
    if any(later <= earlier for earlier, later in zip(timestamps, timestamps[1:])):
        raise ValueError("Heartbeat timestamps must be strictly increasing")
    maximum_gap = max(later - earlier for earlier, later in zip(timestamps, timestamps[1:]))
    accepted = maximum_gap <= maximum_gap_seconds
    return HeartbeatResult(
        accepted=accepted,
        observations=len(timestamps),
        maximum_gap_seconds=maximum_gap,
        threshold_seconds=maximum_gap_seconds,
        reason="all_thresholds_pass" if accepted else "maximum_heartbeat_gap_exceeded",
    )
