# Security Model

This public release is intentionally inert.

- It contains no credentials or credential-loading code.
- It contains no broker hostnames or HTTP client.
- It contains no order-submission implementation.
- It contains no account, order, or position identifiers.
- It retains no raw price or size series.
- Its demo is a pure local state machine using fixed synthetic events.

## Reporting a problem

Do not include credentials, account identifiers, or private broker responses in a public issue. Describe the affected file and behavior using synthetic values.

## Private-system controls represented by the demo

The private project uses local hidden credential entry, paper-only endpoint isolation, externally retained execution fingerprints, intent-before-mutation, persistent mutation budgets, no retry after ambiguous mutation, and final clean-account reconciliation. Those controls are described here but the order-capable implementation is deliberately excluded.
