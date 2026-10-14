# `TaskDefinition`

## Responsibility

`TaskDefinition` is the immutable source-level description of one action route owned by an external `AbstractTask`. It binds task identity, one route kind, and exact action or nested-target contract references.

It is a compiler mapping input, not the semantic identity of runtime execution. Occurrence and attempt records identify runtime activity.
