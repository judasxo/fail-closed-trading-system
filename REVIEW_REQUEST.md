# Public Release Review Request

Review this as a sanitized portfolio repository, not as a trading strategy or executable broker client.

Please verify:

1. The README’s quantitative claims match `evidence/outcomes.json`.
2. The repository contains no credentials, private filesystem paths, raw prices, account identifiers, or order identifiers.
3. The demo is credential-free, network-free, deterministic, and incapable of broker mutation.
4. Each synthetic scenario models the stated control correctly: intent before entry, no retry, direct proof after rejection, manual reconciliation after ambiguity, heartbeat-gap failure, and rejection of a deliberate control-bypass attempt.
5. The sabotage regression substitutes a runner that ignores intent and proves the invariant assertion fails against it.
6. Limitations are prominent enough to prevent paper execution from being mistaken for profitability or live readiness.
7. The architecture and interview guide are understandable without access to the private project.

Run:

```text
python demo.py --scenario all
python -m unittest discover -s tests -v
```

No authenticated request, installation, or external dependency is required or authorized.
