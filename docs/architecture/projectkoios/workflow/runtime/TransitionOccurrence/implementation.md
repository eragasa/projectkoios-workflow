# `TransitionOccurrence` implementation

## Responsibility

Use a content-bound identity derived from exact plan, net instance, transition,
binding digest, predecessor revision, selection evidence, and Task-instance
mapping. Store Task invocation, attempts, effect observations, and child-run
correlations as separate records with exact identities.

Ambiguous effects retain the reservation and start key until reconciliation.
Workflow-backed Tasks retain child-creation intent and never infer terminal
success from child disappearance. Failed, cancelled, stale, or unadmitted child
outcomes do not create fabricated firing records.

UI work status is a derived projection over Task invocation, occurrence, attempt,
and child/effect evidence; it is never the authoritative Task identity.
