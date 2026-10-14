# `TaskDefinition` implementation

## Responsibility

Adapt the historical execution-kind invariant while using target route names appropriate to isolated workers and external lifecycle providers. A task definition admits exactly one route and must reject route-specific fields belonging to another route.

Tests cover route ambiguity, missing schemas, nested-target misuse, action identity drift, deterministic ordering, and mapping closure.
