# `projectkoios.workflow.runtime` architecture

> **Status: provisional architecture candidate.** Runtime record names and the
> reservation/lifecycle decomposition remain under review.

## Responsibility

The runtime owns durable net instances around the pure CPN kernel: marking revisions, enabled-binding projections, token reservations, transition occurrences, attempts, claims, leases, timers, signals, approvals, external lifecycle correlation, cancellation, reconciliation, checkpoints, and replay.

It does not own workflow source compilation, provider discovery, domain result semantics, or pure kernel rules. A UI task is a projection over an occurrence and is never the primary semantic identity. Operation-scoped keys derive from occurrence and attempt identities rather than task or node names.
