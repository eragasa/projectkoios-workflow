# `OccurrenceContext`

> **Status: provisional architecture candidate.** The exact public name and
> representation are not accepted contracts.

## Responsibility

`OccurrenceContext` identifies one attempt to realize one logical occurrence of one enabled CPN binding. The current candidate binds definition digest, net-instance identity, transition identity, enabling marking revision, exact bound-token evidence, binding digest, occurrence identity, attempt identity and ordinal, and optional parent-net correlation.

The same transition enabled again after a loop receives another occurrence identity. A permitted retry receives another attempt under the existing occurrence.
