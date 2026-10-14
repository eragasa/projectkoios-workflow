# `ColoredPetriNetFragmentTemplate`

## Responsibility

`ColoredPetriNetFragmentTemplate` is the abstract reusable source of a bounded CPN control pattern. It owns template identity, base-template identity, inheritance evidence, declared extension points, parameter schema, and deterministic fragment instantiation.

It does not validate a complete workflow, resolve global priority, connect fragments, or execute a marking. Those responsibilities belong to the composer and kernel.
