# `projectkoios.workflow` architecture

> **Status: provisional architecture candidate.** Responsibilities and names
> below remain subject to review; they authorize no implementation or migration.

## Responsibility

`projectkoios.workflow` owns the generic CPN workflow platform: SDK contracts, compilation, immutable definition and deployment artifacts, validation, markings, enablement, deterministic selection, token reservation, pure firing, durable occurrences and attempts, provider coordination, replay, provenance, control-plane services, and read-only visualization.

It does not own domain request semantics, scientific acceptance, calculator formats, extraction correctness, reference authority, credentials, or publication decisions. Those remain with external owners implementing the SDK.

The current operator-selected candidate uses CPN as the sole executable process formalism. Reusable behaviors such as fan-out, approval, timers, external effects, retry, reconciliation, and cancellation are fragment templates compiled into one flat validated net—not parallel step or DAG abstractions.

## Open architecture questions

Physical distribution boundaries, authority issuance, durable process supervision, operational-companion-net composition, nested-net correlation, cancellation propagation, terminal success layers, storage technology, service-process separation, and worker dispatch direction remain unresolved. The child documents present testable candidates without closing those decisions.
