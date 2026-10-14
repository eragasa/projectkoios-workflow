# `OccurrenceContext` schematic

> **Status: provisional architecture candidate.**

## Responsibility

```text
OccurrenceContext
├── definition_digest
├── net_instance_id
├── transition_id
├── enabling_marking_revision
├── bound_token_ids or reservation digest
├── binding_digest
├── occurrence_id
├── attempt_id
├── attempt_ordinal
└── parent_net_instance_id, when required
```

Operation-scoped idempotency, dispatch, observation, reconciliation, and cancellation keys derive from this context rather than from display task or node names.
