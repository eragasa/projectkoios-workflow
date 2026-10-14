# `WorkflowExecutionPlan`

## Responsibility

`WorkflowExecutionPlan` is the immutable, durable, replayable declaration of one compiled workflow. It contains the exact definition closure, canonical flat CPN IR, transition/action mappings, nested targets, and compiler/composition evidence.

It contains no live adapter, provider, effect, authority, repository, run, or process-local handle. Deployment binding is deliberately separate.
