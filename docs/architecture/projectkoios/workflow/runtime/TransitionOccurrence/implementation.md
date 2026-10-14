# `TransitionOccurrence` implementation

## Responsibility

Use a content-bound identity derived from definition, net instance, transition, binding digest, enabling marking revision, and selection evidence. Store attempts separately with monotonic ordinals and exact idempotency keys.

Ambiguous effects retain the reservation and original start key until reconciliation. Failed or cancelled attempts do not create fabricated firing records. UI task status is derived from occurrence and attempt projections.
