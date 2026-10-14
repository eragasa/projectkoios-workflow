# `projectkoios.workflow.service` implementation

> **Status: provisional architecture candidate.** Service/process boundaries
> remain open pending deployment and crash evidence.

## Responsibility

One candidate is a persistent single local control-plane service with transactional command handling; another separates scheduler and API processes over the same authoritative store. In either case, command actionizers validate expected revisions and idempotency keys, while query actionizers return bounded privacy-reduced projections.

Before `start`, one Workflow transaction must retain the occurrence/reservation state, dispatch-intent token or equivalent record, outbox item, and canonical request digest. Provider callbacks must bind occurrence, attempt, request digest, generation-safe handle, and observation revision. Guards reject marking regression while retaining stale observations as evidence.

Drain stops new selections and claims while observation/reconciliation continues for active effects. Restart rebuilds projections and resumes observation without relaunching uncertain work. Health and readiness have distinct results.
