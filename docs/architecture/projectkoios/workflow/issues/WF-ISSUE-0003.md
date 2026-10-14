# WF-ISSUE-0003 — Durable local process-supervisor ownership

- **Kind:** architecture
- **Status:** OPEN
- **Workflow-local scope:** restart-safe local external-job execution
- **Authoritative owner:** Workflow deployment architecture, coordinated with provider owners

## Problem or question

Which component durably owns start-key deduplication, generation-safe process identity, process-group lifetime, observation, and reconciliation across worker or service restart?

## Current evidence

A bare PID or synchronous `subprocess.run` cannot distinguish PID reuse, lost acknowledgement, or orphaned process trees. Simulations providers currently lack a uniform durable start ledger. The candidate protocol requires a ledger entry before launch acknowledgement.

## Consequence

The platform cannot safely claim at-most-once launch, authoritative reconciliation, or restart without duplicate effects.

## Alternatives and recommendation

Alternatives are a generic durable local supervisor, a provider-owned supervisor/ledger under a generic worker host, or an operating-system service adapter. Provider-owned ledgers are currently recommended because the provider understands native job identity, but common invariants should remain in Workflow SDK bases.

## Resolution gate

Fault-injection proves crash-before-launch, crash-after-launch-before-ack, duplicate start, PID reuse, cancellation, worker restart, and authoritative `never_started` reconciliation.

## Affected architecture

Worker, lifecycle provider, dispatch outbox, occurrence reconciliation, and Laptop deployment.
