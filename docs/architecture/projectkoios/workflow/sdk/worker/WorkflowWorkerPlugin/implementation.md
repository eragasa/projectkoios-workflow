# `WorkflowWorkerPlugin` implementation

## Responsibility

Use a narrow ABC with no service client, marking, scheduler, or persistence methods. The worker host supplies occurrence requests and captures results through SDK records.

Conformance rejects missing or extra implementations, descriptor disagreement, mutable component collections, duplicate action bindings, incompatible lifecycle versions, and initialization that performs external effects.
