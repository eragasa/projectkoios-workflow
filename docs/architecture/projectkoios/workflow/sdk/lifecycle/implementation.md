# `projectkoios.workflow.sdk.lifecycle` implementation

> **Status: provisional architecture candidate.**

## Responsibility

Provide request/result records and ABC accessors for all seven actionizers. `ExternalLifecycleProviderBase` may enforce correlation, digest-bound start keys, closed outcome tags, evidence limits, and redaction, but cannot provide a false durable-start guarantee.

A standardized lifecycle fragment is under evaluation with candidate colors for prepared, authority pending/granted, dispatch intent, running, ambiguous, reconciliation required, cancellation requested/cancelling, collecting, and terminal evidence. Candidate guarded transitions cover prepare/stage outcomes, grants, dispatch intent, launch acknowledgement or ambiguity, observation, reconciliation, cancellation, collection, retry policy, and success commit. These names and decomposition are not yet accepted contracts.

The occurrence and dispatch-intent/outbox records plus canonical request digest must be durable before `start`. Provider observations carry occurrence, attempt, request digest, generation-safe handle, and monotonic observation revision. Stale observations may remain evidence but cannot regress the marking.

Provider descriptors advertise deduplication, authoritative reconciliation, cancellation, and evidence capabilities. The service rejects incompatible guarantees during linking rather than discovering limitations during launch. Ambiguity never enables a fresh launch transition.
