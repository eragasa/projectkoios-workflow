# `ColoredPetriNetMarking`

## Responsibility

`ColoredPetriNetMarking` is the authoritative workflow state for one net revision. It maps every place to a bounded multiset of typed token occurrences and has an exact content identity.

Operational claims, leases, and attempts surround a marking but do not silently alter it. Only an admitted pure firing or explicit engine-owned ingress operation produces a successor marking.
