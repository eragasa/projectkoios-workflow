# `projectkoios.workflow.compilation.definitions` architecture

## Responsibility

The definitions module owns frozen generic snapshots produced from external
Task source owners. It erases live Python ownership while retaining exact Task
identity, specialization, contracts, composition, and compiler inputs.

`TaskDefinition` is the parent-visible definition root. An atomic variant names
one pure or effectful execution route. `WorkflowDefinition` is the composite
Task variant and retains ordered Task instances plus explicit child input/export
contracts. Definitions are compiler inputs, not markings, runs, deployment
bindings, handlers, or providers.
