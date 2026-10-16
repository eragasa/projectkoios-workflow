# `TaskDefinition` implementation

## Responsibility

Implement a closed immutable definition family rather than an extensible runtime
record hierarchy. Construction and decoding require exact variants and reject
unknown subclasses.

An atomic variant admits exactly one route and rejects fields owned by another
route or by Workflow composition. A Workflow variant admits composition and
child contracts and rejects atomic execution descriptors. Owner-specific Task
configuration remains behind opaque owner identities and deployment bindings;
it does not widen the generic definition schema.

Tests cover route ambiguity, definition-kind substitution, missing schemas,
workflow-cycle misuse, action identity drift, deterministic ordering, mapping
closure, and separation from runtime identities.
