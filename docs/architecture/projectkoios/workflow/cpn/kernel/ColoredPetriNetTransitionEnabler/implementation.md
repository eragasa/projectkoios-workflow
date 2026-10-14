# `ColoredPetriNetTransitionEnabler` implementation

## Responsibility

Keep enumeration pure, bounded, and deterministic. Guard evaluation failures are closed enablement failures rather than false or exceptions. Inhibitor arcs are nonbinding absence tests; read arcs bind without consuming.

Conformance covers repeated anonymous tokens, identified tokens, multiple variable assignments, guard composition/type failures, capacities, deduplication, and caller-order independence.
