# `AbstractWorkflow`

## Responsibility

`AbstractWorkflow` is the nominal external owner of one workflow source definition. A subclass declares a stable identity and immutable composition using SDK fragment, connection, action, and target records.

Its final definition property constructs a generic `WorkflowDefinition`; subclasses do not define bespoke serialized workflow schemas. The class performs no discovery, persistence, scheduling, enablement, firing, or effect execution.
