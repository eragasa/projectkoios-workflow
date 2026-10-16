# `projectkoios.workflow.compilation.planning` architecture

## Responsibility

Planning compiles one complete Workflow-definition closure into a durable
`WorkflowExecutionPlan`. It composes fragments, resolves namespaces and
priorities, validates Task ports and contracts, flattens the current Workflow to
canonical CPN IR, and records exact atomic and workflow-backed Task mappings.

Atomic Task descriptors constrain typed ports, effect class, authority,
idempotency, and evidence. Workflow-backed Task descriptors name a separately
compiled child plan plus explicit input/export and terminal-delivery contracts.
Neither form lets the compiler infer scientific topology or provider behavior.

Planning performs no provider selection, live binding, run creation, Task
invocation, effect execution, signature-derived topology, or reflective
auto-wiring.
