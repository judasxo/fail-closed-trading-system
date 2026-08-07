# Fail-Closed Trading Research and Paper Operations

Most trading projects showcase the strategy that survived. This project showcases the controls that prevented weak strategies, defective data, and ambiguous execution states from being presented as success.

It combines:

- falsifiable, pre-registered market research;
- strict dataset-admission and selection accounting;
- paper-only equity and cryptocurrency execution paths;
- fail-closed reconciliation and no-retry controls; and
- reproducible operational reliability testing.

It does **not** claim a profitable strategy, live-money readiness, or long-term unattended reliability.

## Results

| Test | Outcome |
|---|---|
| Turn-of-month persistence | Primary claim failed: −2.62 bp per cycle; one-sided lower bound −23.90 bp. |
| Prior-session direction | Both required gates failed: −5.28 bp after cost; lower bound −7.01 bp. |
| Public-vendor data admission | Rejected despite 99.94% cent-level agreement because two rows had impossible OHLC geometry and one close differed by $0.20. |
| Equity paper canary | One $1 SPY round trip completed and reconciled cleanly. |
| Crypto automated canary | One $10 BTC/USD round trip completed and reconciled cleanly. |
| Reliability V1 | Failed: the host slept, creating a three-hour heartbeat gap. |
| Reliability V2 | Passed all nine unchanged thresholds over a genuine 24-hour window. |
| Crypto cost floor | Median 59.75 bp; p95 63.63 bp before slippage. |

The turn-of-month study contains the clearest example of why the primary estimand matters. Its strategy-versus-cash quantity was +23.44 bp with a +3.93 bp lower bound—a result that could easily have been marketed as a win. The pre-registered question was whether turn-of-month days outperformed other eligible days, and that claim failed. The project kept the failure.

## Try the synthetic demo

No credentials, broker account, network connection, or third-party packages are required.

```powershell
python demo.py --scenario all
python -m unittest discover -s tests -v
```

The demo replays four operational situations:

1. a clean paper-style round trip;
2. a definitive entry rejection with direct proof that no order exists;
3. an ambiguous failure after intent, requiring manual reconciliation; and
4. a reliability run rejected because of a large heartbeat gap; and
5. a deliberate attempt to bypass intent-before-entry, rejected by the control.

It does not contact a broker or place an order. It exists to make the safety logic understandable and testable.

## Design principles

- **Intent before mutation:** the audit record exists before any simulated order action.
- **No retry after ambiguity:** an uncertain mutation halts for reconciliation.
- **Direct evidence over inference:** a rejection is considered clean only after order absence and account cleanliness are proven.
- **Failures remain failures:** instrumentation may improve, but acceptance thresholds do not change after a failed run.
- **Research and execution are separate:** strategy-research modules cannot import order-capable modules.
- **Selection is counted:** pre-trial development screens are not treated as information-free.
- **Precision before evaluation:** a candidate must be capable of detecting the smallest economically relevant effect before it receives a trial.

## Repository map

```text
demo.py                       Synthetic command-line replay
src/failclosed_demo/          Pure state machine and reliability evaluator
tests/                        Offline behavioral and release-safety tests
evidence/outcomes.json        Sanitized quantitative evidence with source hashes
docs/ARCHITECTURE.md          Research and operations boundaries
docs/INTERVIEW_GUIDE.md       Concise project explanation and technical Q&A
docs/LIMITATIONS.md           Claims the project deliberately does not make
SECURITY.md                   Public-release security model
```

## Why this is portfolio-worthy

The system repeatedly accepted outcomes that slowed the project down:

- it killed two hypotheses instead of tuning them;
- refused an attractive subgroup rescue and showed it was underpowered;
- rejected the only usable source in a final data-provider exception;
- recorded an unauthorized development screen as a governance failure;
- preserved a failed 24-hour run instead of counting 1,440 observations as success; and
- classified real order rejections without retrying through uncertainty.

The point is not that failure is virtuous. The point is that a system becomes trustworthy when failure cannot be quietly relabeled as success.

The regression suite also includes an adversarial test: it substitutes a deliberately sabotaged runner that ignores intent-before-entry and proves the invariant assertion fails against that implementation. This demonstrates that the test constrains the behavior it names.

## Evidence

The public [evidence summary](evidence/outcomes.json) contains selected metrics and SHA-256 digests of the private canonical artifacts from which they were derived. It contains no credentials, account identifiers, raw prices, order identifiers, or private filesystem paths.

## Current status

The research search is closed until its recorded review date. The paper operational system is complete for its bounded purpose. The original charter’s live-money deliverable was not completed and this public release does not present paper execution as a substitute.
