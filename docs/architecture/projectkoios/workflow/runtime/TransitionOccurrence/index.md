# `TransitionOccurrence`

> **Status: provisional architecture candidate.**

## Responsibility

`TransitionOccurrence` is the durable identity of one selected and reserved transition binding at one exact enabling marking. Repeated firing in a CPN loop creates a new occurrence. Operational retries create new attempts under the same occurrence.

The occurrence binds definition digest, net instance, transition, ordered binding, enabling marking revision, exact bound-token evidence, reservation, and outcome evidence. Its public worker context additionally binds attempt identity/ordinal and optional parent-net correlation.
