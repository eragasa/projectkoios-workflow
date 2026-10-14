# `projectkoios.workflow.sdk.lifecycle` architecture

> **Status: provisional architecture candidate.** The operation split and
> lifecycle-subnet representation remain under review.

## Responsibility

The lifecycle module defines provider operations for external effects: prepare, stage, start, observe, reconcile, cancel, and collect. Each operation has a frozen request, a `DataObjectActionizer`, and a closed result.

The lifecycle separates pre-effect validation, first filesystem effect, sole process/job launch, read-only observation, ambiguity reconciliation, protected cancellation, and terminal evidence collection. Capability is distinct from authorization. The provider reports mechanical outcomes and evidence; later action-specific and domain transitions own normalization and scientific acceptance.
