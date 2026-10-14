# `ColoredPetriNetFragmentTemplate` implementation

## Responsibility

Define a minimal ABC plus `ValidatedFragmentTemplateBase`. The base computes canonical identity, verifies the inheritance chain, and checks use of declared extension points. External subclasses supply declarative records only.

Tests cover inherited behavior, semantic-delta identity, deterministic instantiation, base mutation, port weakening, invalid namespace, parameter bounds, and reuse of one template across distinct workflows. No template may embed a Python guard callable or retain a mutable adapter.
