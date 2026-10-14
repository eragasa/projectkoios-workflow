# WF-ISSUE-0017 — Idempotency scope across occurrence and attempt

- **Kind:** contract
- **Status:** OPEN
- **Workflow-local scope:** action invocation, staging, start, retry, and reconciliation keys
- **Authoritative owner:** Workflow runtime and provider protocol architecture

## Problem or question

Which idempotency identities are occurrence-scoped, attempt-scoped, request-content-scoped, or provider-native, and how do they change across retry without permitting duplicate external effects?

## Current evidence

One occurrence represents one logical firing of one enabled binding; a retry creates another attempt under that occurrence. Providers require same start key plus same digest to replay the original receipt and same key plus different digest to conflict. Ambiguous outcomes must reconcile the original key. Owner actions may also have content-level request identities independent of operational attempt identity.

## Consequence

One undifferentiated key either prevents legitimate retries, allows duplicate launches, or conflates owner-level exact replay with provider start deduplication. Changed configuration or authority could be hidden under an old key.

## Alternatives and recommendation

Use layered candidate identities: an occurrence/action request identity binds definition, action, selected inputs, and logical result; each attempt has a distinct attempt identity; staging has an attempt/workspace key; start has an attempt-scoped start key bound to canonical prepared request and grant digests; reconciliation and cancellation reuse the relevant original start/job identity. A new attempt never reuses a possibly entered start key.

## Resolution gate

Accepted derivations and conflict rules cover pure duplicate invocation, pre-effect retry, effectful terminal retry, ambiguous reconciliation, changed digest, changed grant, changed provider/environment, stage replay, cancel replay, child creation, and same-store owner idempotency. Tests prove exact replay returns retained evidence while collisions fail closed.

## Affected architecture

Occurrence context, lifecycle SPI, owner action descriptors, persistence uniqueness, provider launch ledger, child correlation, and `WF-ISSUE-0012`.
