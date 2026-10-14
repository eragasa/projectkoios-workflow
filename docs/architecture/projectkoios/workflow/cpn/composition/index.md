# `projectkoios.workflow.cpn.composition` architecture

## Responsibility

The composition module combines immutable instantiated fragments through typed port connections and produces one validated flat `ColoredPetriNetDefinition`. It owns deterministic namespacing, connection validation, global priority resolution, and composition evidence.

Composition is compile-time reuse. It is not hierarchical execution and does not create runtime fragment instances.
