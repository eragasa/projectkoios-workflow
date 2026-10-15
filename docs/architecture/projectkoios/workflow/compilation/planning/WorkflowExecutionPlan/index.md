# `WorkflowExecutionPlan`

## Responsibility

`WorkflowExecutionPlan` is the immutable, durable, replayable declaration of
one compiled workflow. It contains the exact definition closure, canonical flat
CPN IR, transition/action mappings, nested targets, and compiler/composition
evidence.

It contains no live adapter, provider, effect, authority, repository, run, or
process-local handle. Deployment binding is deliberately separate.

## Current bounded candidate

`ExperimentalWorkflowPureActionExecutionPlan` closes only the currently
implemented semantics for one pure external action: the exact selected-binding
representation-profile identity and the exact content-identified output-mapping
descriptor. The mapping descriptor transitively closes the SDK transition
binding and firer descriptor.

This record is an embeddable implementation candidate, not the complete
`WorkflowExecutionPlan`. It makes no conformance claim for canonical flat CPN
IR, initial marking, input-source mapping, children, compiler evidence, terminal
delivery, or the proposed full CPN-bindings contract set.
