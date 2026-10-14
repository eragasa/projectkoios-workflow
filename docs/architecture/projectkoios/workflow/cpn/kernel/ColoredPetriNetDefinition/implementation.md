# `ColoredPetriNetDefinition` implementation

## Responsibility

Construct through the composer or strict deserializer, then validate closed references, identity uniqueness, color compatibility, expression typing, capacities, variable binding, and ordering policy. Reject subclasses and noncanonical collection order.

The compiler retains the exact serialized definition in `WorkflowExecutionPlan`. Definitions are immutable; corrections produce a new version and digest.
