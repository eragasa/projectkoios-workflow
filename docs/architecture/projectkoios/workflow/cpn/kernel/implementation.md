# `projectkoios.workflow.cpn.kernel` implementation

## Responsibility

Keep kernel operations free of I/O, clocks, registries, callbacks, and mutable global state. Expression evaluation uses a closed bounded AST and rejects type or evaluation defects. External outputs cannot participate in pre-effect guards.

Concurrency is coordinated outside the pure kernel through marking revisions and token reservations, followed by serializable/CAS revalidation. Inhibitor arcs require protection against concurrent token insertion.
