# WF-ISSUE-0005 — Cancellation propagation policy

- **Kind:** architecture
- **Status:** NARROWED
- **Workflow-local scope:** occurrence, net-instance, and child correlation
- **Authoritative owner:** Workflow architecture with grant-policy input

## Problem or question

What default and configurable rules govern cancellation propagation across attempts, external jobs, child net instances, joins, and parent terminal outcomes?

## Current evidence

The candidate invariant is token-driven cancellation that remains nonterminal until provider-confirmed. A cancel request has its own idempotency key, authority, actor/reason, and observation lifecycle. Parent/child propagation is explicit CPN composition rather than hidden recursive killing.

## Consequence

Unspecified propagation can either leave unauthorized work running or incorrectly classify completed/ambiguous effects as cancelled.

## Alternatives and recommendation

Alternatives include no automatic propagation, request-only propagation to declared children, or policy-specific escalation. The recommendation is explicit definition-owned request propagation with no implied termination and success-before-confirmed-cancel race preservation.

## Resolution gate

Accepted semantics cover unsupported cancellation, already terminal, accepted but running, ambiguous cancel, process-tree escalation, child joins, and restart replay.

## Affected architecture

Lifecycle fragments, runtime, nested correlation, authority grants, and application status projections.
