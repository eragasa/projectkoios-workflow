# `AbstractWorkflow` implementation

## Responsibility

Implement `AbstractWorkflow` as a nominal subclass of the future Task source
ABC. Provide abstract identity and composition declarations plus a
non-overridable definition constructor that validates exact immutable Task
instances, child references, ports, and export contracts.

The constructor rejects live Tasks, handlers, providers, callables, repositories,
mutable collections, direct self-targets, and indirect definition cycles. A
workflow-backed Task reference identifies a separately compiled definition; it
does not serialize the child graph into the parent definition.

Conformance must cover substitution in a parent Task position, stable canonical
definition construction, owner mutation independence, subclass misuse,
parent/child identity separation, and inability to use child success without an
admitted terminal delivery. Runtime behavior remains outside the source ABC.
