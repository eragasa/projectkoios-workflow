# `ColoredPetriNetTransitionEnabler`

## Responsibility

`ColoredPetriNetTransitionEnabler` computes the complete deterministic set of enabled transition bindings for one exact definition and marking. It respects token multiplicity, consume/read/inhibit modes, guards, capacities, and definition-owned variable order.

It does not select a binding, reserve tokens, invoke an action, or change the marking.
