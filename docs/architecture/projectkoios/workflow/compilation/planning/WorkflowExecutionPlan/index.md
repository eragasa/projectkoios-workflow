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
descriptor. `ExperimentalWorkflowPureActionInputPlan` extends that unchanged
base record with one ordered input-source mapping per SDK input role. The
mapping descriptors transitively close source kind, source profile, and mapping
version without retaining payloads or live repositories.

`ExperimentalWorkflowPureActionCpnPlan` adds exact bounded canonical flat-CPN
definition bytes, representation profile, digest, and candidate CPN execution
profile. The reservation and firing candidates require its exact identity and
byte-equal supplied definition.

These records are embeddable implementation candidates, not the complete
`WorkflowExecutionPlan`. They make no conformance claim for canonical decode,
initial marking, complete CPN profile closure, durable source authority,
children, compiler evidence, terminal delivery, or the proposed full
CPN-bindings contract set.
