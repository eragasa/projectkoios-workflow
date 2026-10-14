# `AbstractTask`

## Responsibility

`AbstractTask` is a source-language owner for one action route that will be mapped to CPN transition behavior. It supplies a stable identity, exactly one declared route kind, and exact request/result or nested-target contracts.

It is not a durable runtime task and does not own attempts. Runtime semantic identities are the net instance, marking, transition, selected binding, occurrence, and attempt.
